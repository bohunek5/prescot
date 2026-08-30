import { readFile, writeFile } from "node:fs/promises";
import { resolve } from "node:path";
import { chromium } from "../../radlight/node_modules/playwright/index.mjs";

function argumentValue(name, fallback = "") {
  const index = process.argv.indexOf(name);
  return index === -1 ? fallback : process.argv[index + 1] || fallback;
}

function clone(value) {
  return value == null ? value : JSON.parse(JSON.stringify(value));
}

function protectedSnapshot(object) {
  const data = object?.data || {};
  const stockLevel = clone(data.stockLevel || []);
  for (const stock of stockLevel) {
    delete stock.modificationDate;
    delete stock.updatedAt;
  }
  return {
    ean: clone(data.ean),
    manufacturer: clone(data.manufacturer),
    manufacturerIndex: clone(data.manufacturerIndex),
    suppliersProductId: clone(data.suppliersProductId),
    timIndex: clone(data.timIndex),
    listPrice: clone(data.listPrice),
    netCatalogPrice: clone(data.netCatalogPrice),
    stockLevel,
    measureUnit: clone(data.measureUnit),
    availability: clone(data.availability),
    status: clone(data.status),
    state: clone(data.state),
    sale: clone(data.sale),
    productAvailableForSale: clone(data.productAvailableForSale),
    mainPhoto: clone(data.mainPhoto),
    assignedCategory24: clone(data.assignedCategory24),
    productDescriptions: clone(data.productDescriptions),
  };
}

function saveGeneral(general) {
  const keys = [
    "objectFromVersion", "id", "creationDate", "userOwner", "published", "className", "fullpath", "php",
    "allowInheritance", "allowVariants", "showVariants", "showAppLoggerTab", "showFieldLookup",
    "linkGeneratorReference", "userModification", "versionDate", "versionCount", "iconCls", "icon", "cls",
    "qtipCfg", "text",
  ];
  return Object.fromEntries(keys.map((key) => [key, general?.[key] ?? null]));
}

const profileDir = argumentValue("--profile-dir");
const queuePath = resolve(argumentValue("--queue", "exports/tim/remediation/active-positive-wyc-name-queue.json"));
const stage = argumentValue("--stage", "pilot1");
const outputPath = resolve(argumentValue("--output", "/tmp/tim-pimcore-name-cleanup.json"));
const startIndex = Math.max(0, Number(argumentValue("--start-index", "0")) || 0);
const limit = Math.max(1, Number(argumentValue("--limit", "10")) || 10);
const maxWrites = Math.max(0, Number(argumentValue("--max-writes", "0")) || 0);
const applySave = process.argv.includes("--apply");
if (!profileDir) throw new Error("Podaj --profile-dir.");
if (applySave && maxWrites < 1) throw new Error("Tryb --apply wymaga dodatniego --max-writes.");
const queueDocument = JSON.parse(await readFile(queuePath, "utf8"));
const fullQueue = queueDocument?.stages?.[stage];
if (!Array.isArray(fullQueue)) throw new Error(`Brak etapu ${stage}.`);
const queue = fullQueue.slice(startIndex, startIndex + limit);
const results = [];
const allowedWrites = [];
const blockedWrites = [];
let currentGuard = null;
let writes = 0;
let fatalError = "";
const report = () => ({
  generatedAt: new Date().toISOString(), stage, startIndex, limit, maxWrites, applySave, queueLength: queue.length,
  writes,
  counts: {
    checked: results.length,
    saved: results.filter((item) => ["saved", "saved_with_validation"].includes(item.status)).length,
    alreadyCurrent: results.filter((item) => item.status === "already_current").length,
    locked: results.filter((item) => item.status === "locked").length,
    skipped: results.filter((item) => item.status === "skipped").length,
    failed: results.filter((item) => item.status === "failed").length,
  },
  fatalError, results, allowedWrites, blockedWrites,
});
const persist = () => writeFile(outputPath, `${JSON.stringify(report(), null, 2)}\n`, "utf8");

const context = await chromium.launchPersistentContext(profileDir, {
  headless: true,
  executablePath: "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
  args: ["--profile-directory=Default"],
  serviceWorkers: "block",
});
await context.route("**/*", async (route) => {
  const request = route.request();
  const method = request.method().toUpperCase();
  const url = request.url();
  if (["GET", "HEAD", "OPTIONS"].includes(method)) return route.continue();
  if (applySave && method === "PUT" && currentGuard && url === "https://dostawca.tim.pl/pimcore/admin/object/save?task=undefined") {
    try {
      const params = new URLSearchParams(request.postData() || "");
      const data = JSON.parse(params.get("data") || "null");
      const general = JSON.parse(params.get("general") || "null");
      const dirtyFields = JSON.parse(params.get("dirtyFields") || "null");
      const valid = [...params.keys()].sort().join(",") === "data,dirtyFields,general,id"
        && params.get("id") === String(currentGuard.objectId)
        && Number(general?.id) === currentGuard.objectId
        && Number(general?.versionCount) === currentGuard.versionCount
        && JSON.stringify(Object.keys(data || {})) === JSON.stringify(["timName"])
        && data.timName === currentGuard.expectedName
        && JSON.stringify(dirtyFields) === JSON.stringify(["timName"]);
      if (!valid) throw new Error("save_guard_failed");
      allowedWrites.push({ objectId: currentGuard.objectId, method, url, dirtyFields, expectedName: currentGuard.expectedName });
      return route.continue();
    } catch (error) {
      blockedWrites.push({ objectId: currentGuard?.objectId || 0, method, url, reason: error.message });
      return route.abort("blockedbyclient");
    }
  }
  if (!/cdn-cgi\/rum|liveupdate\.pimcore\.org\/update-check/.test(url)) {
    blockedWrites.push({ objectId: currentGuard?.objectId || 0, method, url, reason: "not_allowlisted" });
  }
  return route.abort("blockedbyclient");
});

const page = context.pages()[0] || await context.newPage();
await page.goto("https://dostawca.tim.pl/pimcore/", { waitUntil: "domcontentloaded", timeout: 45_000 });
let frame = page.frames().find((item) => item.url().includes("/pimcore/admin/"));
for (let attempt = 0; !frame && attempt < 15; attempt += 1) {
  await page.waitForTimeout(1_000);
  frame = page.frames().find((item) => item.url().includes("/pimcore/admin/"));
}
if (!frame) throw new Error("Nie znaleziono ramki PIMCORE.");
await page.waitForTimeout(3_000);
const readObject = async (objectId) => frame.evaluate(async (id) => {
  const response = await fetch(`/pimcore/admin/object/get?id=${id}`, { credentials: "same-origin" });
  let object = null;
  try { object = await response.json(); } catch {}
  return { status: response.status, object };
}, objectId);

for (let offset = 0; offset < queue.length; offset += 1) {
  if (applySave && writes >= maxWrites) break;
  const product = queue[offset];
  const objectId = Number(product.pimcoreId);
  const item = { index: startIndex + offset, objectId, timIndex: product.timIndex, beforeName: product.beforeName, afterName: product.afterName, status: "failed" };
  currentGuard = null;
  try {
    const beforeRead = await readObject(objectId);
    const beforeObject = beforeRead.object;
    const data = beforeObject?.data || {};
    const liveStock = Math.max(0, ...(data.stockLevel || []).map((entry) => Number(entry.stockTotalQuantityMz) || 0));
    const stableIdentityMatches = beforeRead.status === 200
      && Number(beforeObject?.general?.id) === objectId
      && String(data.timIndex || "") === String(product.timIndex)
      && String(data.manufacturerIndex || "") === String(product.manufacturerCode)
      && String(data.ean || "") === String(product.ean || "")
      && data.state === "active"
      && liveStock > 0
      && beforeObject?.general?.published === true;
    if (stableIdentityMatches && String(data.timName || "") === String(product.afterName)) {
      item.status = "already_current";
      results.push(item);
      await persist();
      continue;
    }
    const identityMatches = beforeRead.status === 200
      && Number(beforeObject?.general?.id) === objectId
      && String(data.timIndex || "") === String(product.timIndex)
      && String(data.manufacturerIndex || "") === String(product.manufacturerCode)
      && String(data.ean || "") === String(product.ean || "")
      && String(data.timName || "") === String(product.beforeName)
      && data.state === "active"
      && liveStock > 0
      && beforeObject?.general?.published === true;
    if (!identityMatches) {
      item.status = "skipped";
      item.reason = "live_identity_name_state_or_stock_mismatch";
      results.push(item);
      await persist();
      continue;
    }
    if (beforeObject.general.locked) {
      item.status = "locked";
      item.reason = "live_object_locked";
      results.push(item);
      await persist();
      continue;
    }
    if (!applySave) {
      item.status = "skipped";
      item.reason = "verified_ready_dry_run";
      results.push(item);
      await persist();
      continue;
    }
    const beforeProtected = protectedSnapshot(beforeObject);
    const beforeWorkflow = clone(beforeObject.workflowManagement);
    const beforeVersion = Number(beforeObject.general.versionCount);
    currentGuard = { objectId, expectedName: product.afterName, versionCount: beforeVersion };
    const saveResponse = await frame.evaluate(async ({ id, expectedName, general }) => new Promise((resolveRequest) => {
      window.Ext.Ajax.request({
        url: "/pimcore/admin/object/save?task=undefined",
        method: "PUT",
        headers: { "X-Pimcore-CSRF-Token": window.pimcore.settings.csrfToken },
        params: {
          id,
          data: JSON.stringify({ timName: expectedName }),
          general: JSON.stringify(general),
          dirtyFields: JSON.stringify(["timName"]),
        },
        callback: (_options, success, response) => resolveRequest({ success, status: response?.status || 0, body: String(response?.responseText || "").slice(0, 100_000) }),
      });
    }), { id: objectId, expectedName: product.afterName, general: saveGeneral(beforeObject.general) });
    let savePayload = null;
    try { savePayload = JSON.parse(saveResponse.body); } catch {}
    const accepted = saveResponse.status === 200 && saveResponse.success === true && savePayload?.success === true;
    item.saveResponseStatus = saveResponse.status;
    let afterObject = null;
    let applied = false;
    for (let attempt = 0; attempt < 4; attempt += 1) {
      afterObject = (await readObject(objectId)).object;
      applied = String(afterObject?.data?.timName || "") === String(product.afterName);
      if (applied) break;
      await page.waitForTimeout(700);
    }
    if (!applied && saveResponse.status === 422) {
      item.status = "skipped";
      item.reason = "server_validation_422_no_name_change";
      item.validationResponse = saveResponse.body;
      results.push(item);
      currentGuard = null;
      await persist();
      continue;
    }
    if (!applied) throw new Error(`save_failed_http_${saveResponse.status}`);
    const protectedUnchanged = JSON.stringify(protectedSnapshot(afterObject)) === JSON.stringify(beforeProtected);
    const workflowUnchanged = JSON.stringify(afterObject.workflowManagement) === JSON.stringify(beforeWorkflow);
    const identityUnchanged = ["id", "className", "published"].every((key) => JSON.stringify(afterObject.general[key]) === JSON.stringify(beforeObject.general[key]));
    const beforeDirectory = String(beforeObject.general.fullpath || "").replace(/\/[^/]*$/, "");
    const expectedFullpath = `${beforeDirectory}/${product.afterName}`;
    const automaticTreeRenameCorrect = afterObject.general.key === product.afterName && afterObject.general.fullpath === expectedFullpath;
    const versionDelta = Number(afterObject.general.versionCount) - beforeVersion;
    if (!protectedUnchanged || !workflowUnchanged || !identityUnchanged || !automaticTreeRenameCorrect || ![0, 1].includes(versionDelta)) throw new Error("post_save_verification_failed");
    item.status = accepted ? "saved" : "saved_with_validation";
    item.httpStatus = saveResponse.status;
    delete item.saveResponseStatus;
    item.beforeVersionCount = beforeVersion;
    item.afterVersionCount = afterObject.general.versionCount;
    item.protectedFieldsUnchanged = protectedUnchanged;
    item.workflowUnchanged = workflowUnchanged;
    item.identityUnchanged = identityUnchanged;
    item.automaticTreeRenameCorrect = automaticTreeRenameCorrect;
    writes += 1;
    results.push(item);
    currentGuard = null;
    await persist();
    console.log(JSON.stringify({ objectId, status: item.status, beforeName: item.beforeName, afterName: item.afterName }));
  } catch (error) {
    item.status = "failed";
    item.reason = error.message;
    results.push(item);
    fatalError = `Karta ${objectId}: ${error.message}`;
    currentGuard = null;
    await persist();
    break;
  }
}
await persist();
await context.close();
console.log(`Zapisane nazwy: ${writes}; sprawdzone: ${results.length}; błąd krytyczny: ${fatalError || "brak"}.`);
if (fatalError) process.exitCode = 1;
