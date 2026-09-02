import { mkdir, readFile, writeFile } from "node:fs/promises";
import { basename, dirname, resolve } from "node:path";
import { chromium } from "../../radlight/node_modules/playwright/index.mjs";

const CDP_URL = "http://127.0.0.1:9222";
const TIM_ORIGIN = "https://dostawca.tim.pl";
const ASSET_PARENT = "/Import multimediow/24248";
const ASSET_PARENT_ID = 1658124;
const CARD_ROOT = resolve("output/pdf/scharfer-tim-current-ean-2026-09-01");
const CE_SOURCE = "/Users/karolbohdanowicz/Desktop/_PRESCOT/_2026/TIM.PL/TIM - karty ce/Zasilacze LED/CE - SCHARFER- PL.pdf";
const CE_FILENAME = "CE_Scharfer_zasilacze_LED_PL_2026-09.pdf";

const PRODUCTS = [
  { id: 2345680, model: "SCH-18-12", ean: "5905475360008", supplierId: "9437", timIndex: "0001-00016-83853", price: 20 },
  { id: 2345681, model: "SCH-18-24", ean: "5905475360015", supplierId: "9438", timIndex: "0001-00016-83854", price: 20 },
  { id: 2345683, model: "SCH-20-12", ean: "5905475360039", supplierId: "9440", timIndex: "0001-00016-83856", price: 26.5 },
  { id: 2345682, model: "SCH-20-24", ean: "5905475360022", supplierId: "9439", timIndex: "0001-00016-83855", price: 26.5 },
  { id: 2345684, model: "SCH-30-12", ean: "5905475360046", supplierId: "9441", timIndex: "0001-00016-83857", price: 27.1 },
  { id: 2345685, model: "SCH-30-24", ean: "5905475360053", supplierId: "9442", timIndex: "0001-00016-83858", price: 27.1 },
  { id: 2345687, model: "SCH-45-12", ean: "5905475360077", supplierId: "9444", timIndex: "0001-00016-83860", price: 32.5 },
  { id: 2345686, model: "SCH-45-24", ean: "5905475360060", supplierId: "9443", timIndex: "0001-00016-83859", price: 32.5 },
  { id: 2345688, model: "SCH-60-12", ean: "5905475360084", supplierId: "9445", timIndex: "0001-00016-83861", price: 36 },
  { id: 2345689, model: "SCH-60-24", ean: "5905475360091", supplierId: "9446", timIndex: "0001-00016-83862", price: 36 },
  { id: 2345691, model: "SCH-100-12", ean: "5905475360114", supplierId: "9448", timIndex: "0001-00016-83864", price: 62 },
  { id: 2345690, model: "SCH-100-24", ean: "5905475360107", supplierId: "9447", timIndex: "0001-00016-83863", price: 62 },
  { id: 2345692, model: "SCH-150-12", ean: "5905475360121", supplierId: "9449", timIndex: "0001-00016-83865", price: 105 },
  { id: 2345693, model: "SCH-150-24", ean: "5905475360138", supplierId: "9450", timIndex: "0001-00016-83866", price: 105 },
  { id: 2345697, model: "SCH-200-12", ean: "5905475360145", supplierId: "9462", timIndex: "0001-00016-83870", price: 120 },
  { id: 2345694, model: "SCH-200-24", ean: "5905475360152", supplierId: "9451", timIndex: "0001-00016-83867", price: 120 },
  { id: 2345696, model: "SCH-300-12", ean: "5905475360176", supplierId: "9453", timIndex: "0001-00016-83869", price: 177 },
  { id: 2345695, model: "SCH-300-24", ean: "5905475360169", supplierId: "9452", timIndex: "0001-00016-83868", price: 177 },
  { id: 7774290, model: "SCH-400-12", ean: "5905475364433", supplierId: "13122", timIndex: "0001-00019-96768", price: 260 },
  { id: 7774293, model: "SCH-400-24", ean: "5905475364440", supplierId: "13123", timIndex: "0001-00019-96769", price: 260 },
];

function argumentValue(name, fallback = "") {
  const index = process.argv.indexOf(name);
  return index === -1 ? fallback : process.argv[index + 1] || fallback;
}
function clone(value) { return value == null ? value : JSON.parse(JSON.stringify(value)); }
function same(a, b) { return JSON.stringify(a) === JSON.stringify(b); }
function numericPrice(value) { return Number(value && typeof value === "object" && "value" in value ? value.value : value); }
function power(model) { return model.split("-")[1]; }
function relation(asset) {
  return [{ id: Number(asset.id), path: String(asset.path), type: "asset", subtype: "document", expirationdate: null, rowId: `${Number(asset.id)}$$1$$asset` }];
}
function relationAssetId(value) { return Array.isArray(value) && value.length === 1 ? Number(value[0]?.id || 0) : 0; }
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
  for (const field of ["certifications", "dataSheet", "countAttachments", "certificationAdded", "dataSheetAdded", "assortmentType", "stockLevel", "packagingLevels", "lastUpdateScoringDate"]) delete copy[field];
  return copy;
}

const apply = process.argv.includes("--apply");
const start = Math.max(0, Number(argumentValue("--start", "0")) || 0);
const limit = Math.max(1, Number(argumentValue("--limit", "1")) || 1);
const maxCards = Math.max(0, Number(argumentValue("--max-cards", "0")) || 0);
const outputPath = resolve(argumentValue("--output", "exports/tim/remediation/scharfer-document-refresh.json"));
if (apply && maxCards < 1) throw new Error("Tryb --apply wymaga --max-cards większego od zera.");
const queue = PRODUCTS.slice(start, start + limit);

const report = {
  generatedAt: new Date().toISOString(), apply, start, limit, maxCards,
  scope: "certifications and dataSheet only; prices, EAN, names, stock, status and workflow protected",
  queue, uploadedAssets: [], reusedAssets: [], allowedWrites: [], blockedWrites: [], results: [], fatalError: "",
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
  if (method === "POST" && currentGuard?.kind === "preflight" && url.origin === TIM_ORIGIN && url.pathname === `/admin/workflow/actions/${currentGuard.objectId}`) {
    const params = new URLSearchParams(request.postData() || "");
    if (params.get("ctype") === "object" && params.get("cid") === String(currentGuard.objectId) && params.get("classId") === String(currentGuard.classId) && [...params.keys()].sort().join(",") === "cid,classId,ctype") {
      report.allowedWrites.push({ kind: "workflow_actions_read", objectId: currentGuard.objectId });
      return route.continue();
    }
  }
  if (apply && method === "POST" && currentGuard?.kind === "asset" && url.origin === TIM_ORIGIN && url.pathname === "/pimcore/admin/asset/add-asset") {
    try {
      if (url.searchParams.get("parentPath") !== ASSET_PARENT || url.searchParams.get("uploadAssetType") !== "document" || [...url.searchParams.keys()].sort().join(",") !== "parentPath,uploadAssetType") throw new Error("asset_query_guard_failed");
      const body = request.postDataBuffer();
      const contentType = String(request.headers()["content-type"] || "");
      const text = body?.toString("latin1") || "";
      if (!body || !contentType.startsWith("multipart/form-data; boundary=") || !text.includes(`filename="${currentGuard.filename}"`) || !text.includes('name="csrfToken"') || body.indexOf(currentGuard.bytes) < 0) throw new Error("asset_payload_guard_failed");
      report.allowedWrites.push({ kind: "asset_upload", objectId: currentGuard.objectId, filename: currentGuard.filename });
      return route.continue();
    } catch (error) {
      report.blockedWrites.push({ method, url: request.url(), reason: error.message });
      return route.abort("blockedbyclient");
    }
  }
  if (apply && method === "PUT" && currentGuard?.kind === "object" && url.origin === TIM_ORIGIN && url.pathname === "/pimcore/admin/object/save" && url.search === "?task=undefined") {
    try {
      const params = new URLSearchParams(request.postData() || "");
      const data = JSON.parse(params.get("data") || "null");
      const general = JSON.parse(params.get("general") || "null");
      const dirtyFields = JSON.parse(params.get("dirtyFields") || "null");
      if ([...params.keys()].sort().join(",") !== "data,dirtyFields,general,id" || params.get("id") !== String(currentGuard.objectId) || Number(general?.id) !== currentGuard.objectId || Number(general?.versionCount) !== currentGuard.versionCount || !same(data, currentGuard.data) || !same(dirtyFields, ["certifications", "dataSheet"])) throw new Error("object_payload_guard_failed");
      report.allowedWrites.push({ kind: "object_save", objectId: currentGuard.objectId, dirtyFields });
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
async function assetDownloadAudit(id) {
  return frame.evaluate(async ({ assetId, nonce }) => {
    const request = await fetch(`/pimcore/admin/asset/download?id=${assetId}&_=${nonce}`, { credentials: "same-origin", headers: { "Cache-Control": "no-cache" } });
    const result = { status: request.status, contentType: String(request.headers.get("content-type") || "") };
    try { await request.body?.cancel(); } catch {}
    return result;
  }, { assetId: Number(id), nonce: Date.now() });
}
async function listAssets() {
  const response = await frame.evaluate(async ({ node, nonce }) => {
    const request = await fetch(`/pimcore/admin/asset/tree-get-children-by-id?node=${node}&limit=1000&start=0&view=MULTIMEDIA_IMPORT&_=${nonce}`, { credentials: "same-origin", headers: { Accept: "application/json", "Cache-Control": "no-cache" } });
    let payload = null;
    try { payload = await request.json(); } catch {}
    return { status: request.status, payload };
  }, { node: ASSET_PARENT_ID, nonce: Date.now() });
  if (response.status !== 200 || !Array.isArray(response.payload?.nodes)) throw new Error("asset_tree_read_failed");
  return response.payload.nodes;
}
async function verifyAsset(id, expectedPath) {
  const exact = (await listAssets()).filter((node) => Number(node.id) === Number(id));
  if (exact.length !== 1 || String(exact[0].path || "") !== expectedPath || String(exact[0].type || "") !== "document") throw new Error(`asset_verification_failed:${id}`);
  const download = await assetDownloadAudit(id);
  if (download.status !== 200 || !download.contentType.includes("pdf")) throw new Error(`asset_not_downloadable:${id}:http_${download.status}`);
  return { id: Number(id), path: expectedPath, type: "document", download };
}
async function findOrUpload(objectId, source, filename) {
  const expectedPath = `${ASSET_PARENT}/${filename}`;
  const exact = (await listAssets()).filter((node) => String(node.key || "") === filename && String(node.path || "") === expectedPath);
  if (exact.length > 1) throw new Error(`duplicate_exact_asset:${filename}`);
  if (exact.length === 1) {
    const asset = await verifyAsset(exact[0].id, expectedPath);
    report.reusedAssets.push({ objectId, source, ...asset });
    await persist();
    return asset;
  }
  if (!apply) return { id: 0, path: expectedPath, type: "document", pendingUpload: true };
  const bytes = await readFile(source);
  if (bytes.subarray(0, 4).toString("ascii") !== "%PDF") throw new Error(`source_is_not_pdf:${basename(source)}`);
  currentGuard = { kind: "asset", objectId, filename, bytes };
  const response = await frame.evaluate(async ({ parentPath, filenameValue, bytesBase64 }) => {
    const binary = atob(bytesBase64);
    const bytes = new Uint8Array(binary.length);
    for (let index = 0; index < binary.length; index += 1) bytes[index] = binary.charCodeAt(index);
    const body = new FormData();
    body.append("Filedata", new File([bytes], filenameValue, { type: "application/pdf" }));
    body.append("filename", filenameValue);
    body.append("csrfToken", window.pimcore.settings.csrfToken);
    const request = await fetch(`/pimcore/admin/asset/add-asset?parentPath=${encodeURIComponent(parentPath)}&uploadAssetType=document`, { method: "POST", credentials: "same-origin", body });
    let payload = null;
    try { payload = await request.json(); } catch {}
    return { status: request.status, payload };
  }, { parentPath: ASSET_PARENT, filenameValue: filename, bytesBase64: bytes.toString("base64") });
  currentGuard = null;
  const id = Number(response.payload?.asset?.id || 0);
  if (response.status !== 200 || response.payload?.success !== true || !id) throw new Error(`asset_upload_failed:${filename}:http_${response.status}`);
  const asset = await verifyAsset(id, expectedPath);
  report.uploadedAssets.push({ objectId, source, ...asset });
  await persist();
  return asset;
}
async function verifyWritableSession(objectId, classId) {
  currentGuard = { kind: "preflight", objectId, classId };
  const response = await frame.evaluate(async ({ id, classIdValue }) => new Promise((resolveRequest) => window.Ext.Ajax.request({
    url: `/admin/workflow/actions/${id}`, method: "POST", headers: { "X-Pimcore-CSRF-Token": window.pimcore.settings.csrfToken }, params: { ctype: "object", cid: id, classId: classIdValue },
    callback: (_options, success, result) => resolveRequest({ success, status: result?.status || 0 }),
  })), { id: objectId, classIdValue: classId });
  currentGuard = null;
  if (!response.success || response.status !== 200) throw new Error(`pimcore_writable_session_unavailable:http_${response.status}`);
}

for (const product of queue) {
  if (apply && written >= maxCards) break;
  const result = { id: product.id, model: product.model, ean: product.ean, status: "failed" };
  try {
    const before = await readObject(product.id);
    const data = before.data || {};
    const identity = {
      id: Number(before.general?.id), model: String(data.manufacturerIndex || ""), ean: String(data.ean || ""), supplierId: String(data.suppliersProductId || ""), timIndex: String(data.timIndex || ""),
      price: numericPrice(data.listPrice), name: String(data.name || data.productName || before.general?.key || ""), state: String(data.state || ""), status: String(data.status || ""), published: Boolean(before.general?.published),
    };
    if (identity.id !== product.id || identity.model !== product.model || identity.ean !== product.ean || identity.supplierId !== product.supplierId || identity.timIndex !== product.timIndex || Math.abs(identity.price - product.price) > 0.0001 || identity.state !== "active" || identity.status !== "active" || !identity.published || before.general?.locked) throw new Error(`identity_state_or_price_guard_failed:${JSON.stringify(identity)}`);
    const oldCeId = relationAssetId(data.certifications);
    const oldSheetId = relationAssetId(data.dataSheet);
    if (!oldCeId || !oldSheetId) throw new Error("expected_single_existing_documents_missing");
    const [oldCeAudit, oldSheetAudit] = await Promise.all([assetDownloadAudit(oldCeId), assetDownloadAudit(oldSheetId)]);
    if (oldCeAudit.status === 200 || oldSheetAudit.status === 200) throw new Error("existing_document_is_downloadable_review_required");
    const cardFilename = `Scharfer_SCH-${power(product.model)}_karta_techniczna_PL_EAN_TIM_2026-09.pdf`;
    const cardSource = resolve(CARD_ROOT, `SCH-${power(product.model)}PL-EAN-TIM.pdf`);
    result.before = { identity, version: Number(before.general?.versionCount), oldCeId, oldSheetId, oldCeAudit, oldSheetAudit };
    result.documents = { certifications: { source: CE_SOURCE, filename: CE_FILENAME }, dataSheet: { source: cardSource, filename: cardFilename } };
    if (!apply) {
      result.status = "verified_ready_dry_run";
      report.results.push(result);
      await persist();
      console.log(JSON.stringify({ id: product.id, model: product.model, status: result.status }));
      continue;
    }
    await verifyWritableSession(product.id, before.general.classId);
    const ceAsset = await findOrUpload(product.id, CE_SOURCE, CE_FILENAME);
    const sheetAsset = await findOrUpload(product.id, cardSource, cardFilename);
    const saveData = { certifications: relation(ceAsset), dataSheet: relation(sheetAsset), netCatalogPrice: clone(data.netCatalogPrice) };
    const beforeProtected = protectedData(data);
    const beforeGeneral = stableGeneral(before.general);
    const beforeWorkflow = clone(before.workflowManagement);
    const beforeVersion = Number(before.general.versionCount);
    currentGuard = { kind: "object", objectId: product.id, versionCount: beforeVersion, data: saveData };
    const save = await frame.evaluate(async ({ id, dataValue, generalValue }) => new Promise((resolveRequest) => window.Ext.Ajax.request({
      url: "/pimcore/admin/object/save?task=undefined", method: "PUT", headers: { "X-Pimcore-CSRF-Token": window.pimcore.settings.csrfToken },
      params: { id, data: JSON.stringify(dataValue), general: JSON.stringify(generalValue), dirtyFields: JSON.stringify(["certifications", "dataSheet"]) },
      callback: (_options, success, response) => resolveRequest({ success, status: response?.status || 0, body: String(response?.responseText || "").slice(0, 100_000) }),
    })), { id: product.id, dataValue: saveData, generalValue: saveGeneral(before.general) });
    currentGuard = null;
    result.saveResponse = save;
    let after = null;
    for (let attempt = 0; attempt < 8; attempt += 1) {
      after = await readObject(product.id);
      if (relationAssetId(after.data?.certifications) === ceAsset.id && relationAssetId(after.data?.dataSheet) === sheetAsset.id) break;
      await page.waitForTimeout(600);
    }
    if (save.status !== 200 || save.success !== true || relationAssetId(after?.data?.certifications) !== ceAsset.id || relationAssetId(after?.data?.dataSheet) !== sheetAsset.id) throw new Error(`object_save_not_applied:http_${save.status}`);
    if (!same(protectedData(after.data), beforeProtected)) {
      const afterProtected = protectedData(after.data);
      const changed = [...new Set([...Object.keys(beforeProtected), ...Object.keys(afterProtected)])].filter((key) => !same(beforeProtected[key], afterProtected[key]));
      result.protectedChanges = Object.fromEntries(changed.map((key) => [key, { before: beforeProtected[key], after: afterProtected[key] }]));
      throw new Error(`protected_data_changed:${changed.join(",")}`);
    }
    if (!same(stableGeneral(after.general), beforeGeneral)) throw new Error("stable_general_changed");
    if (!same(after.workflowManagement, beforeWorkflow)) throw new Error("workflow_changed");
    const [ceDownload, sheetDownload] = await Promise.all([assetDownloadAudit(ceAsset.id), assetDownloadAudit(sheetAsset.id)]);
    if (ceDownload.status !== 200 || !ceDownload.contentType.includes("pdf") || sheetDownload.status !== 200 || !sheetDownload.contentType.includes("pdf")) throw new Error("post_save_documents_not_downloadable");
    const afterIdentity = { model: String(after.data?.manufacturerIndex || ""), ean: String(after.data?.ean || ""), supplierId: String(after.data?.suppliersProductId || ""), timIndex: String(after.data?.timIndex || ""), price: numericPrice(after.data?.listPrice), name: String(after.data?.name || after.data?.productName || after.general?.key || ""), state: String(after.data?.state || ""), status: String(after.data?.status || ""), published: Boolean(after.general?.published) };
    if (!same(afterIdentity, { ...identity, id: undefined })) {
      const expectedIdentity = clone(identity); delete expectedIdentity.id;
      if (!same(afterIdentity, expectedIdentity)) throw new Error(`post_save_identity_changed:${JSON.stringify({ identity, afterIdentity })}`);
    }
    result.status = "saved_and_verified";
    result.after = { identity: afterIdentity, version: Number(after.general?.versionCount), ceAsset, sheetAsset, ceDownload, sheetDownload, workflowUnchanged: true };
    written += 1;
    report.results.push(result);
    await persist();
    console.log(JSON.stringify({ id: product.id, model: product.model, status: result.status, version: result.after.version }));
  } catch (error) {
    currentGuard = null;
    result.status = "failed";
    result.reason = error.message;
    report.results.push(result);
    report.fatalError = `${product.model}: ${error.message}`;
    await persist();
    break;
  }
}

await persist();
await page.unroute("**/*", routeHandler);
console.log(JSON.stringify({ output: outputPath, written, uploaded: report.uploadedAssets.length, reused: report.reusedAssets.length, blockedWrites: report.blockedWrites.length, fatalError: report.fatalError }, null, 2));
if (report.fatalError) process.exitCode = 1;
process.exit(process.exitCode || 0);
