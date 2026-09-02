import { readFile, writeFile } from "node:fs/promises";
import { basename, resolve } from "node:path";
import { chromium } from "../../radlight/node_modules/playwright/index.mjs";

const CDP_URL = "http://127.0.0.1:9222";
const TIM_ORIGIN = "https://dostawca.tim.pl";
const ASSET_PARENT = "/Import multimediow/24248";
const ASSET_PARENT_ID = 1658124;
const CARD_ROOT = resolve("output/pdf/scharfer-new-ean-2026-09-01");

const PRODUCTS = [
  { id: 2345680, model: "SCH-18-12", oldEan: "5905475360008", newEan: "5999863091001", supplierId: "9437", timIndex: "0001-00016-83853", price: 20, stock: 661 },
  { id: 2345681, model: "SCH-18-24", oldEan: "5905475360015", newEan: "5999863091018", supplierId: "9438", timIndex: "0001-00016-83854", price: 20, stock: 189 },
  { id: 2345683, model: "SCH-20-12", oldEan: "5905475360039", newEan: "5999863091025", supplierId: "9440", timIndex: "0001-00016-83856", price: 26.5, stock: 278 },
  { id: 2345682, model: "SCH-20-24", oldEan: "5905475360022", newEan: "5999863091032", supplierId: "9439", timIndex: "0001-00016-83855", price: 26.5, stock: 164 },
  { id: 2345684, model: "SCH-30-12", oldEan: "5905475360046", newEan: "5999863091049", supplierId: "9441", timIndex: "0001-00016-83857", price: 27.1, stock: 477 },
  { id: 2345685, model: "SCH-30-24", oldEan: "5905475360053", newEan: "5999863091063", supplierId: "9442", timIndex: "0001-00016-83858", price: 27.1, stock: 424 },
  { id: 2345687, model: "SCH-45-12", oldEan: "5905475360077", newEan: "5999863091056", supplierId: "9444", timIndex: "0001-00016-83860", price: 32.5, stock: 401 },
  { id: 2345686, model: "SCH-45-24", oldEan: "5905475360060", newEan: "5999863091070", supplierId: "9443", timIndex: "0001-00016-83859", price: 32.5, stock: 551 },
  { id: 2345688, model: "SCH-60-12", oldEan: "5905475360084", newEan: "5999863091087", supplierId: "9445", timIndex: "0001-00016-83861", price: 36, stock: 363 },
  { id: 2345689, model: "SCH-60-24", oldEan: "5905475360091", newEan: "5999863091094", supplierId: "9446", timIndex: "0001-00016-83862", price: 36, stock: 203 },
  { id: 2345691, model: "SCH-100-12", oldEan: "5905475360114", newEan: "5999863091100", supplierId: "9448", timIndex: "0001-00016-83864", price: 62, stock: 313 },
  { id: 2345690, model: "SCH-100-24", oldEan: "5905475360107", newEan: "5999863091117", supplierId: "9447", timIndex: "0001-00016-83863", price: 62, stock: 261 },
  { id: 2345692, model: "SCH-150-12", oldEan: "5905475360121", newEan: "5999863091124", supplierId: "9449", timIndex: "0001-00016-83865", price: 105, stock: 166 },
  { id: 2345693, model: "SCH-150-24", oldEan: "5905475360138", newEan: "5999863091131", supplierId: "9450", timIndex: "0001-00016-83866", price: 105, stock: 56 },
  { id: 2345697, model: "SCH-200-12", oldEan: "5905475360145", newEan: "5999863091148", supplierId: "9462", timIndex: "0001-00016-83870", price: 120, stock: 35 },
  { id: 2345694, model: "SCH-200-24", oldEan: "5905475360152", newEan: "5999863091155", supplierId: "9451", timIndex: "0001-00016-83867", price: 120, stock: 175 },
  { id: 2345696, model: "SCH-300-12", oldEan: "5905475360176", newEan: "5999863091162", supplierId: "9453", timIndex: "0001-00016-83869", price: 177, stock: 115 },
  { id: 2345695, model: "SCH-300-24", oldEan: "5905475360169", newEan: "5999863091179", supplierId: "9452", timIndex: "0001-00016-83868", price: 177, stock: 158 },
  { id: 7774290, model: "SCH-400-12", oldEan: "5905475364433", newEan: "5999863091186", supplierId: "13122", timIndex: "0001-00019-96768", price: 260, stock: 16 },
  { id: 7774293, model: "SCH-400-24", oldEan: "5905475364440", newEan: "5999863091193", supplierId: "13123", timIndex: "0001-00019-96769", price: 260, stock: 29 },
];

function argumentValue(name, fallback = "") {
  const index = process.argv.indexOf(name);
  return index === -1 ? fallback : process.argv[index + 1] || fallback;
}

function clone(value) {
  return value == null ? value : JSON.parse(JSON.stringify(value));
}

function same(a, b) {
  return JSON.stringify(a) === JSON.stringify(b);
}

function numericPrice(value) {
  if (value && typeof value === "object" && "value" in value) return Number(value.value);
  return Number(value);
}

function powerFromModel(model) {
  return model.split("-")[1];
}

function stableGeneral(general) {
  const keys = ["id", "parentId", "type", "key", "classId", "published", "className", "fullpath"];
  return Object.fromEntries(keys.map((key) => [key, clone(general?.[key])]));
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

function relation(asset) {
  return [{
    id: Number(asset.id),
    path: String(asset.path),
    type: "asset",
    subtype: "document",
    expirationdate: null,
    rowId: `${Number(asset.id)}$$1$$asset`,
  }];
}

function relationHasAsset(value, asset) {
  return Array.isArray(value)
    && value.length === 1
    && Number(value[0]?.id) === Number(asset.id)
    && String(value[0]?.type || "asset") === "asset";
}

function protectedData(data) {
  const copy = clone(data || {});
  for (const key of [
    "ean", "dataSheet", "assortmentType", "countAttachments", "dataSheetAdded", "stockLevel",
    "packagingLevels", "lastUpdateScoringDate",
  ]) delete copy[key];
  return copy;
}

const apply = process.argv.includes("--apply");
const start = Math.max(0, Number(argumentValue("--start", "0")) || 0);
const limit = Math.max(1, Number(argumentValue("--limit", "1")) || 1);
const maxCards = Math.max(0, Number(argumentValue("--max-cards", "0")) || 0);
const outputPath = resolve(argumentValue("--output", "exports/tim/remediation/scharfer-ean-datasheet-live.json"));
if (apply && maxCards < 1) throw new Error("Tryb --apply wymaga --max-cards większego od zera.");

const queue = PRODUCTS.slice(start, start + limit).map((product) => ({
  ...product,
  card: resolve(CARD_ROOT, `SCH-${powerFromModel(product.model)}PL-nowe-EAN.pdf`),
  cardFilename: `Scharfer_SCH-${powerFromModel(product.model)}_karta_techniczna_PL_EAN_2026-09.pdf`,
}));

const report = {
  generatedAt: new Date().toISOString(),
  apply,
  start,
  limit,
  maxCards,
  queue: queue.map(({ card, ...item }) => ({ ...item, card })),
  uploadedAssets: [],
  reusedAssets: [],
  allowedWrites: [],
  blockedWrites: [],
  results: [],
  fatalError: "",
};
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
      && (typeof window.pimcore?.globalmanager?.get?.("user")?.isAllowed === "function"
        || Number(window.pimcore?.currentuser?.id) > 0)).catch(() => false);
    if (authenticated) {
      page = candidate;
      frame = candidateFrame;
      break;
    }
  }
  if (frame) break;
}
if (!page || !frame) throw new Error("Brak zalogowanej ramki PIMCORE.");

async function readObject(id) {
  for (let attempt = 0; attempt < 8; attempt += 1) {
    const response = await frame.evaluate(async ({ objectId, nonce }) => {
      const request = await fetch(`/pimcore/admin/object/get?id=${objectId}&_=${nonce}`, {
        credentials: "same-origin",
        headers: { Accept: "application/json", "Cache-Control": "no-cache" },
      });
      let payload = null;
      try { payload = await request.json(); } catch {}
      return { status: request.status, payload };
    }, { objectId: id, nonce: `${Date.now()}-${attempt}` });
    if (response.status === 200 && response.payload) return response.payload;
    await page.waitForTimeout(750);
  }
  throw new Error(`object_read_failed:${id}`);
}

async function searchPublishedEan(ean) {
  return frame.evaluate(async (term) => {
    const fields = ["id", "ean", "manufacturerIndex", "timIndex"];
    const filter = {
      classId: 3,
      conditions: {
        fulltextSearchTerm: term,
        filters: [{
          fieldname: "o_published",
          fieldLabel: "opublikowano",
          filterEntryData: true,
          operator: "must",
          ignoreInheritance: "",
        }],
      },
    };
    const result = await new Promise((resolveRequest) => window.Ext.Ajax.request({
      url: "/admin/bundle/advanced-object-search/admin/grid-proxy?classId=3&xaction=read",
      method: "POST",
      headers: { "X-Pimcore-CSRF-Token": window.pimcore.settings.csrfToken },
      timeout: 20_000,
      params: {
        class: "product",
        language: "pl",
        filter: JSON.stringify(filter),
        page: 1,
        start: 0,
        limit: 100,
        "fields[]": fields,
      },
      callback: (_options, success, response) => resolveRequest({
        success,
        status: response?.status || 0,
        body: String(response?.responseText || ""),
      }),
    }));
    let payload = null;
    try { payload = JSON.parse(result.body); } catch {}
    return {
      status: result.status,
      records: (payload?.data || []).map((record) => ({
        id: Number(record.id || record.o_id),
        ean: String(record.ean || ""),
        manufacturerIndex: String(record.manufacturerIndex || ""),
        timIndex: String(record.timIndex || ""),
      })),
    };
  }, ean);
}

async function listAssets() {
  const response = await frame.evaluate(async ({ node, nonce }) => {
    const request = await fetch(`/pimcore/admin/asset/tree-get-children-by-id?node=${node}&limit=1000&start=0&view=MULTIMEDIA_IMPORT&_=${nonce}`, {
      credentials: "same-origin",
      headers: { Accept: "application/json", "Cache-Control": "no-cache" },
    });
    let payload = null;
    try { payload = await request.json(); } catch {}
    return { status: request.status, payload };
  }, { node: ASSET_PARENT_ID, nonce: Date.now() });
  if (response.status !== 200 || !Array.isArray(response.payload?.nodes)) throw new Error("asset_tree_read_failed");
  return response.payload.nodes;
}

async function verifyAsset(id, expectedPath = "") {
  const response = await frame.evaluate(async ({ assetId, nonce }) => {
    const request = await fetch(`/pimcore/admin/asset/get-data-by-id?id=${assetId}&_=${nonce}`, {
      credentials: "same-origin",
      headers: { Accept: "application/json", "Cache-Control": "no-cache" },
    });
    let payload = null;
    try { payload = await request.json(); } catch {}
    return { status: request.status, payload };
  }, { assetId: id, nonce: Date.now() });
  const currentPath = `${String(response.payload?.path || "").replace(/\/$/, "")}/${String(response.payload?.filename || "")}`;
  if (response.status !== 200
    || String(response.payload?.type || "") !== "document"
    || (expectedPath && currentPath !== expectedPath)) throw new Error(`asset_verification_failed:${id}`);
  return { id: Number(id), path: currentPath, type: "document" };
}

let currentGuard = null;
let written = 0;
const routeHandler = async (route) => {
  const request = route.request();
  const method = request.method().toUpperCase();
  if (["GET", "HEAD", "OPTIONS"].includes(method)) return route.continue();
  const url = new URL(request.url());

  if (method === "POST"
    && url.origin === TIM_ORIGIN
    && url.pathname === "/admin/bundle/advanced-object-search/admin/grid-proxy"
    && url.search === "?classId=3&xaction=read") {
    report.allowedWrites.push({ kind: "read_only_ean_uniqueness_search", objectId: currentGuard?.objectId || 0 });
    return route.continue();
  }

  if (apply && method === "POST" && currentGuard?.kind === "asset") {
    try {
      if (url.origin !== TIM_ORIGIN || url.pathname !== "/pimcore/admin/asset/add-asset") throw new Error("asset_url_not_allowlisted");
      if (url.searchParams.get("parentPath") !== ASSET_PARENT
        || url.searchParams.get("uploadAssetType") !== "document"
        || [...url.searchParams.keys()].sort().join(",") !== "parentPath,uploadAssetType") throw new Error("asset_query_guard_failed");
      const contentType = String(request.headers()["content-type"] || "");
      const body = request.postDataBuffer();
      const bodyText = body?.toString("latin1") || "";
      if (!body || !contentType.startsWith("multipart/form-data; boundary=")
        || !bodyText.includes(`name="Filedata"; filename="${currentGuard.filename}"`)
        || !bodyText.includes(`name="filename"\r\n\r\n${currentGuard.filename}`)
        || !bodyText.includes('name="csrfToken"')
        || body.indexOf(currentGuard.bytes) < 0) throw new Error("asset_payload_guard_failed");
      report.allowedWrites.push({ kind: "asset_upload", objectId: currentGuard.objectId, filename: currentGuard.filename });
      return route.continue();
    } catch (error) {
      report.blockedWrites.push({ method, url: request.url(), reason: error.message });
      return route.abort("blockedbyclient");
    }
  }

  if (apply && method === "PUT" && currentGuard?.kind === "object") {
    try {
      if (url.origin !== TIM_ORIGIN || url.pathname !== "/pimcore/admin/object/save" || url.search !== "?task=undefined") throw new Error("object_url_not_allowlisted");
      const params = new URLSearchParams(request.postData() || "");
      const data = JSON.parse(params.get("data") || "null");
      const general = JSON.parse(params.get("general") || "null");
      const dirtyFields = JSON.parse(params.get("dirtyFields") || "null");
      if ([...params.keys()].sort().join(",") !== "data,dirtyFields,general,id"
        || params.get("id") !== String(currentGuard.objectId)
        || Number(general?.id) !== currentGuard.objectId
        || Number(general?.versionCount) !== currentGuard.versionCount
        || !same(data, currentGuard.data)
        || !same(dirtyFields, ["ean", "dataSheet"])) throw new Error("object_payload_guard_failed");
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

async function findOrUpload(product) {
  const expectedPath = `${ASSET_PARENT}/${product.cardFilename}`;
  const exact = (await listAssets()).filter((node) => String(node.key || "") === product.cardFilename && String(node.path || "") === expectedPath);
  if (exact.length > 1) throw new Error(`duplicate_exact_asset:${product.cardFilename}`);
  if (exact.length === 1) {
    const asset = await verifyAsset(exact[0].id, expectedPath);
    report.reusedAssets.push({ objectId: product.id, source: product.card, ...asset });
    await persist();
    return asset;
  }
  if (!apply) return { id: 0, path: expectedPath, type: "document", pendingUpload: true };
  const bytes = await readFile(product.card);
  if (bytes.subarray(0, 4).toString("ascii") !== "%PDF") throw new Error(`source_is_not_pdf:${basename(product.card)}`);
  currentGuard = { kind: "asset", objectId: product.id, filename: product.cardFilename, bytes };
  const response = await frame.evaluate(async ({ parentPath, filename, bytesBase64 }) => {
    const binary = atob(bytesBase64);
    const fileBytes = new Uint8Array(binary.length);
    for (let index = 0; index < binary.length; index += 1) fileBytes[index] = binary.charCodeAt(index);
    const body = new FormData();
    body.append("Filedata", new File([fileBytes], filename, { type: "application/pdf" }));
    body.append("filename", filename);
    body.append("csrfToken", window.pimcore.settings.csrfToken);
    const request = await fetch(`/pimcore/admin/asset/add-asset?parentPath=${encodeURIComponent(parentPath)}&uploadAssetType=document`, {
      method: "POST",
      credentials: "same-origin",
      body,
    });
    let payload = null;
    try { payload = await request.json(); } catch {}
    return { status: request.status, payload };
  }, { parentPath: ASSET_PARENT, filename: product.cardFilename, bytesBase64: bytes.toString("base64") });
  currentGuard = null;
  const id = Number(response.payload?.asset?.id);
  if (response.status !== 200 || response.payload?.success !== true || !Number.isFinite(id)) throw new Error(`asset_upload_failed:${product.cardFilename}:http_${response.status}`);
  const asset = await verifyAsset(id, expectedPath);
  report.uploadedAssets.push({ objectId: product.id, source: product.card, ...asset });
  await persist();
  return asset;
}

for (const product of queue) {
  if (apply && written >= maxCards) break;
  const result = { id: product.id, model: product.model, oldEan: product.oldEan, newEan: product.newEan, status: "failed" };
  currentGuard = { kind: "read", objectId: product.id };
  try {
    const before = await readObject(product.id);
    const data = before.data || {};
    const unique = await searchPublishedEan(product.newEan);
    if (unique.status !== 200 || unique.records.some((record) => record.id !== product.id)) throw new Error("new_ean_already_exists_or_search_failed");
    if (Number(before.general?.id) !== product.id
      || before.general?.published !== true
      || before.general?.locked === true
      || String(data.ean || "") !== product.oldEan
      || String(data.manufacturerIndex || "") !== product.model
      || String(data.suppliersProductId || "") !== product.supplierId
      || String(data.timIndex || "") !== product.timIndex
      || String(data.state?.value || data.state || "") !== "active"
      || String(data.status?.value || data.status || "") !== "active"
      || Math.abs(numericPrice(data.listPrice) - product.price) > 0.0001
      || product.stock <= 0
      || !String(data.mainPhoto || "").startsWith("/PIM-MEDIA/Products/GLOWNA/")
      || !Array.isArray(data.certifications) || data.certifications.length !== 1
      || !Array.isArray(data.dataSheet) || data.dataSheet.length !== 1
      || /\b\d{13}\b/.test(String(data.productDescriptions?.data?.longMarketingDescription || ""))) {
      throw new Error("live_identity_price_documents_or_state_guard_failed");
    }
    const cardBytes = await readFile(product.card);
    if (cardBytes.subarray(0, 4).toString("ascii") !== "%PDF") throw new Error("corrected_card_is_not_pdf");
    if (!apply) {
      result.status = "verified_ready_dry_run";
      result.currentDataSheet = clone(data.dataSheet);
      result.currentCertification = clone(data.certifications);
      result.card = product.card;
      result.cardFilename = product.cardFilename;
      report.results.push(result);
      await persist();
      continue;
    }

    const asset = await findOrUpload(product);
    const beforeProtected = protectedData(data);
    const beforeGeneral = stableGeneral(before.general);
    const beforeWorkflow = clone(before.workflowManagement);
    const beforeVersion = Number(before.general.versionCount);
    const beforeCertification = clone(data.certifications);
    const beforePrice = numericPrice(data.listPrice);
    const saveData = {
      ean: product.newEan,
      dataSheet: relation(asset),
      netCatalogPrice: clone(data.netCatalogPrice),
    };
    const dirtyFields = ["ean", "dataSheet"];
    currentGuard = { kind: "object", objectId: product.id, versionCount: beforeVersion, data: saveData };
    const save = await frame.evaluate(async ({ id, dataValue, generalValue, dirtyFieldsValue }) => new Promise((resolveRequest) => {
      window.Ext.Ajax.request({
        url: "/pimcore/admin/object/save?task=undefined",
        method: "PUT",
        headers: { "X-Pimcore-CSRF-Token": window.pimcore.settings.csrfToken },
        params: {
          id,
          data: JSON.stringify(dataValue),
          general: JSON.stringify(generalValue),
          dirtyFields: JSON.stringify(dirtyFieldsValue),
        },
        callback: (_options, success, response) => resolveRequest({
          success,
          status: response?.status || 0,
          body: String(response?.responseText || "").slice(0, 100_000),
        }),
      });
    }), { id: product.id, dataValue: saveData, generalValue: saveGeneral(before.general), dirtyFieldsValue: dirtyFields });
    currentGuard = null;
    result.saveResponseStatus = save.status;
    result.saveResponseBody = save.body;
    await persist();

    let after = null;
    let applied = false;
    for (let attempt = 0; attempt < 10; attempt += 1) {
      after = await readObject(product.id);
      applied = String(after.data?.ean || "") === product.newEan && relationHasAsset(after.data?.dataSheet, asset);
      if (applied) break;
      await page.waitForTimeout(900);
    }
    if (!applied) throw new Error(`object_save_not_applied:http_${save.status}`);
    const protectedBefore = beforeProtected;
    const protectedAfter = protectedData(after.data);
    if (!same(protectedAfter, protectedBefore)) {
      const changedKeys = [...new Set([...Object.keys(protectedBefore), ...Object.keys(protectedAfter)])]
        .filter((key) => !same(protectedBefore[key], protectedAfter[key]));
      result.protectedChanges = changedKeys;
      throw new Error(`protected_data_changed:${changedKeys.join(",")}`);
    }
    if (!same(stableGeneral(after.general), beforeGeneral)) throw new Error("stable_general_changed");
    if (!same(after.workflowManagement, beforeWorkflow)) throw new Error("workflow_changed");
    if (!same(after.data?.certifications, beforeCertification)) throw new Error("certification_changed");
    if (Math.abs(numericPrice(after.data?.listPrice) - beforePrice) > 0.0001) throw new Error("price_changed");
    if (String(after.data?.manufacturerIndex || "") !== product.model
      || String(after.data?.suppliersProductId || "") !== product.supplierId
      || String(after.data?.timIndex || "") !== product.timIndex
      || String(after.data?.timName || "") !== String(data.timName || "")
      || String(after.data?.state?.value || after.data?.state || "") !== "active"
      || String(after.data?.status?.value || after.data?.status || "") !== "active") throw new Error("protected_identity_or_state_changed");

    result.status = "saved";
    result.httpStatus = save.status;
    result.saveAccepted = save.status === 200 && save.success === true;
    result.beforeVersion = beforeVersion;
    result.afterVersion = Number(after.general.versionCount);
    result.beforePrice = beforePrice;
    result.afterPrice = numericPrice(after.data.listPrice);
    result.beforeDataSheet = clone(data.dataSheet);
    result.afterDataSheet = clone(after.data.dataSheet);
    result.certificationUnchanged = true;
    result.protectedDataUnchanged = true;
    result.workflowUnchanged = true;
    written += 1;
    report.results.push(result);
    await persist();
    console.log(JSON.stringify({ id: product.id, model: product.model, status: result.status, ean: product.newEan, price: result.afterPrice }));
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
console.log(JSON.stringify({ written, uploaded: report.uploadedAssets.length, reused: report.reusedAssets.length, fatalError: report.fatalError }));
if (report.fatalError) process.exitCode = 1;
process.exit(process.exitCode || 0);
