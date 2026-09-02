import { mkdir, readFile, writeFile } from "node:fs/promises";
import { dirname, resolve } from "node:path";
import { chromium } from "../../radlight/node_modules/playwright/index.mjs";

const CDP_URL = "http://127.0.0.1:9222";
const TIM_ORIGIN = "https://dostawca.tim.pl";
const QUEUE_PATH = resolve("exports/tim/remediation/scharfer-description-queue-2026-09-01.json");

function argumentValue(name, fallback = "") {
  const index = process.argv.indexOf(name);
  return index === -1 ? fallback : process.argv[index + 1] || fallback;
}
function clone(value) { return value == null ? value : JSON.parse(JSON.stringify(value)); }
function same(a, b) { return JSON.stringify(a) === JSON.stringify(b); }
function numericPrice(value) { return Number(value && typeof value === "object" && "value" in value ? value.value : value); }
function canonicalDescription(html) { return String(html || "").trim().replace(/^<section>\s*/i, "").replace(/\s*<\/section>$/i, "").trim(); }
function normalizedDescription(html) {
  return String(html || "").replace(/&quot;|&#0*34;|&#x0*22;/gi, '"').replace(/&apos;|&#0*39;|&#x0*27;/gi, "'").trim();
}
function descriptionsEqual(a, b) { return normalizedDescription(a) === normalizedDescription(b); }
function saveGeneral(general) {
  const keys = ["objectFromVersion", "id", "creationDate", "userOwner", "published", "className", "fullpath", "php", "allowInheritance", "allowVariants", "showVariants", "showAppLoggerTab", "showFieldLookup", "linkGeneratorReference", "userModification", "versionDate", "versionCount", "iconCls", "icon", "cls", "qtipCfg", "text"];
  return Object.fromEntries(keys.map((key) => [key, general?.[key] ?? null]));
}
function stableGeneral(general) {
  const keys = ["id", "parentId", "type", "key", "classId", "published", "className", "fullpath"];
  return Object.fromEntries(keys.map((key) => [key, clone(general?.[key])]));
}
function protectedData(data) {
  const copy = clone(data || {});
  for (const key of ["productDescriptions", "stockLevel", "packagingLevels", "lastUpdateScoringDate"]) delete copy[key];
  return copy;
}

const apply = process.argv.includes("--apply");
const start = Math.max(0, Number(argumentValue("--start", "0")) || 0);
const limit = Math.max(1, Number(argumentValue("--limit", "1")) || 1);
const maxCards = Math.max(0, Number(argumentValue("--max-cards", "0")) || 0);
const outputPath = resolve(argumentValue("--output", "exports/tim/remediation/scharfer-description-refresh.json"));
if (apply && maxCards < 1) throw new Error("Tryb --apply wymaga --max-cards większego od zera.");
const source = JSON.parse(await readFile(QUEUE_PATH, "utf8"));
const allItems = source?.stages?.scharferNeedsUpdate;
if (!Array.isArray(allItems) || allItems.length !== 20) throw new Error("Kolejka nie zawiera 20 pozycji Scharfer.");
const queue = allItems.slice(start, start + limit);

const report = {
  generatedAt: new Date().toISOString(), apply, start, limit, maxCards, queuePath: QUEUE_PATH,
  scope: "productDescriptions only; price, EAN, name, stock, documents, status and workflow protected",
  allowedWrites: [], blockedWrites: [], results: [], fatalError: "",
};
await mkdir(dirname(outputPath), { recursive: true });
const persist = () => writeFile(outputPath, `${JSON.stringify(report, null, 2)}\n`, "utf8");

const browser = await chromium.connectOverCDP(CDP_URL);
const context = browser.contexts()[0];
if (!context) throw new Error("Brak aktywnego kontekstu Chrome.");
let page = null;
let frame = null;
for (const candidate of context.pages()) {
  for (const candidateFrame of candidate.frames().filter((item) => item.url().includes("/pimcore/admin/"))) {
    const authenticated = await candidateFrame.evaluate(() => Boolean(window.Ext)
      && Boolean(window.pimcore?.settings?.csrfToken)
      && Number(window.pimcore?.currentuser?.id || window.pimcore?.globalmanager?.get?.("user")?.id) > 0).catch(() => false);
    if (authenticated) { page = candidate; frame = candidateFrame; break; }
  }
  if (frame) break;
}
if (!page || !frame) throw new Error("Brak zalogowanej ramki PIMCORE.");

let currentGuard = null;
let written = 0;
const routeHandler = async (route) => {
  const request = route.request();
  const method = request.method().toUpperCase();
  if (["GET", "HEAD", "OPTIONS"].includes(method)) return route.continue();
  const url = new URL(request.url());
  if (apply && method === "PUT" && currentGuard?.kind === "object" && url.origin === TIM_ORIGIN && url.pathname === "/pimcore/admin/object/save" && url.search === "?task=undefined") {
    try {
      const params = new URLSearchParams(request.postData() || "");
      const data = JSON.parse(params.get("data") || "null");
      const general = JSON.parse(params.get("general") || "null");
      const dirtyFields = JSON.parse(params.get("dirtyFields") || "null");
      const descriptionData = data?.productDescriptions?.data;
      if ([...params.keys()].sort().join(",") !== "data,dirtyFields,general,id"
        || params.get("id") !== String(currentGuard.objectId)
        || Number(general?.id) !== currentGuard.objectId
        || Number(general?.versionCount) !== currentGuard.versionCount
        || JSON.stringify(Object.keys(data || {})) !== JSON.stringify(["productDescriptions", "netCatalogPrice"])
        || data.productDescriptions?.type !== "productDescriptions"
        || JSON.stringify(Object.keys(descriptionData || {})) !== JSON.stringify(["longMarketingDescription"])
        || descriptionData.longMarketingDescription !== currentGuard.expectedHtml
        || !same(data.netCatalogPrice, currentGuard.netCatalogPrice)
        || !same(dirtyFields, ["productDescriptions"])) throw new Error("object_payload_guard_failed");
      report.allowedWrites.push({ kind: "object_save", objectId: currentGuard.objectId, dirtyFields, descriptionLength: currentGuard.expectedHtml.length });
      return route.continue();
    } catch (error) {
      report.blockedWrites.push({ method, url: request.url(), reason: error.message });
      return route.abort("blockedbyclient");
    }
  }
  report.blockedWrites.push({ method, url: request.url(), reason: "not_allowlisted" });
  return route.abort("blockedbyclient");
};
await page.route("**/*", routeHandler);

async function readObject(id) {
  for (let attempt = 0; attempt < 8; attempt += 1) {
    const response = await frame.evaluate(async ({ objectId, nonce }) => {
      const request = await fetch(`/pimcore/admin/object/get?id=${objectId}&_=${nonce}`, { credentials: "same-origin", headers: { Accept: "application/json", "Cache-Control": "no-cache" } });
      let payload = null;
      try { payload = await request.json(); } catch {}
      return { status: request.status, payload };
    }, { objectId: id, nonce: `${Date.now()}-${attempt}` });
    if (response.status === 200 && response.payload) return response.payload;
    await page.waitForTimeout(500);
  }
  throw new Error(`object_read_failed:${id}`);
}

for (const product of queue) {
  if (apply && written >= maxCards) break;
  const result = { id: Number(product.pimcoreId), model: product.manufacturerCode, ean: product.ean, status: "failed" };
  try {
    const expectedHtml = canonicalDescription(product.descriptionHtml);
    if (!expectedHtml.includes(product.manufacturerCode) || /\b\d{13}\b/u.test(expectedHtml) || /\bPRE[-_ ]?\d/iu.test(expectedHtml)) throw new Error("description_content_guard_failed");
    const before = await readObject(result.id);
    const data = before.data || {};
    const beforeIdentity = {
      model: String(data.manufacturerIndex || ""), ean: String(data.ean || ""), suppliersProductId: String(data.suppliersProductId || ""), timIndex: String(data.timIndex || ""),
      name: String(data.timName || before.general?.key || ""), price: numericPrice(data.listPrice), state: String(data.state?.value || data.state || ""), status: String(data.status?.value || data.status || ""), published: Boolean(before.general?.published),
    };
    if (Number(before.general?.id) !== result.id || beforeIdentity.model !== product.manufacturerCode || beforeIdentity.ean !== product.ean || Math.abs(beforeIdentity.price - Number(product.timListPrice)) > 0.0001 || beforeIdentity.state !== "active" || beforeIdentity.status !== "active" || !beforeIdentity.published || before.general?.locked) throw new Error(`identity_state_or_price_guard_failed:${JSON.stringify(beforeIdentity)}`);
    const currentHtml = String(data.productDescriptions?.data?.longMarketingDescription || "");
    result.before = { identity: beforeIdentity, version: Number(before.general?.versionCount), descriptionLength: currentHtml.length };
    if (descriptionsEqual(currentHtml, expectedHtml)) {
      result.status = "already_current";
      report.results.push(result);
      await persist();
      continue;
    }
    if (!apply) {
      result.status = "verified_ready_dry_run";
      result.targetLength = expectedHtml.length;
      report.results.push(result);
      await persist();
      console.log(JSON.stringify({ id: result.id, model: result.model, status: result.status }));
      continue;
    }
    const beforeProtected = protectedData(data);
    const beforeGeneral = stableGeneral(before.general);
    const beforeWorkflow = clone(before.workflowManagement);
    const beforeVersion = Number(before.general.versionCount);
    const netCatalogPrice = clone(data.netCatalogPrice);
    const saveData = { productDescriptions: { type: "productDescriptions", data: { longMarketingDescription: expectedHtml } }, netCatalogPrice };
    currentGuard = { kind: "object", objectId: result.id, versionCount: beforeVersion, expectedHtml, netCatalogPrice };
    const save = await frame.evaluate(async ({ id, dataValue, generalValue }) => new Promise((resolveRequest) => window.Ext.Ajax.request({
      url: "/pimcore/admin/object/save?task=undefined", method: "PUT", headers: { "X-Pimcore-CSRF-Token": window.pimcore.settings.csrfToken },
      params: { id, data: JSON.stringify(dataValue), general: JSON.stringify(generalValue), dirtyFields: JSON.stringify(["productDescriptions"]) },
      callback: (_options, success, response) => resolveRequest({ success, status: response?.status || 0, body: String(response?.responseText || "").slice(0, 100_000) }),
    })), { id: result.id, dataValue: saveData, generalValue: saveGeneral(before.general) });
    currentGuard = null;
    result.saveResponse = save;
    let after = null;
    for (let attempt = 0; attempt < 8; attempt += 1) {
      after = await readObject(result.id);
      if (descriptionsEqual(after.data?.productDescriptions?.data?.longMarketingDescription, expectedHtml)) break;
      await page.waitForTimeout(600);
    }
    if (save.status !== 200 || save.success !== true || !descriptionsEqual(after?.data?.productDescriptions?.data?.longMarketingDescription, expectedHtml)) throw new Error(`object_save_not_applied:http_${save.status}`);
    if (!same(protectedData(after.data), beforeProtected)) {
      const afterProtected = protectedData(after.data);
      const changed = [...new Set([...Object.keys(beforeProtected), ...Object.keys(afterProtected)])].filter((key) => !same(beforeProtected[key], afterProtected[key]));
      result.protectedChanges = Object.fromEntries(changed.map((key) => [key, { before: beforeProtected[key], after: afterProtected[key] }]));
      throw new Error(`protected_data_changed:${changed.join(",")}`);
    }
    if (!same(stableGeneral(after.general), beforeGeneral)) throw new Error("stable_general_changed");
    if (!same(after.workflowManagement, beforeWorkflow)) throw new Error("workflow_changed");
    const afterIdentity = {
      model: String(after.data?.manufacturerIndex || ""), ean: String(after.data?.ean || ""), suppliersProductId: String(after.data?.suppliersProductId || ""), timIndex: String(after.data?.timIndex || ""),
      name: String(after.data?.timName || after.general?.key || ""), price: numericPrice(after.data?.listPrice), state: String(after.data?.state?.value || after.data?.state || ""), status: String(after.data?.status?.value || after.data?.status || ""), published: Boolean(after.general?.published),
    };
    if (!same(afterIdentity, beforeIdentity)) throw new Error(`post_save_identity_changed:${JSON.stringify({ beforeIdentity, afterIdentity })}`);
    result.status = "saved_and_verified";
    result.after = { identity: afterIdentity, version: Number(after.general?.versionCount), descriptionLength: expectedHtml.length, workflowUnchanged: true };
    written += 1;
    report.results.push(result);
    await persist();
    console.log(JSON.stringify({ id: result.id, model: result.model, status: result.status, version: result.after.version }));
  } catch (error) {
    currentGuard = null;
    result.status = "failed";
    result.reason = error.message;
    report.results.push(result);
    report.fatalError = `${result.model}: ${error.message}`;
    await persist();
    break;
  }
}

await persist();
await page.unroute("**/*", routeHandler);
console.log(JSON.stringify({ output: outputPath, written, blockedWrites: report.blockedWrites.length, fatalError: report.fatalError }, null, 2));
if (report.fatalError) process.exitCode = 1;
process.exit(process.exitCode || 0);
