import { readFile, writeFile } from "node:fs/promises";
import { basename, resolve } from "node:path";
import { chromium } from "../../radlight/node_modules/playwright/index.mjs";

const CDP_URL = "http://127.0.0.1:9222";
const TIM_ORIGIN = "https://dostawca.tim.pl";
const ASSET_PARENT = "/Import multimediow/24248";
const ASSET_PARENT_ID = 1658124;

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

function withoutDocumentFields(data, ignoreActiveDynamics = false) {
  const copy = clone(data || {});
  delete copy.certifications;
  delete copy.instructions;
  delete copy.dataSheet;
  // These fields are recalculated by TIM/Pimcore when document relations change.
  delete copy.assortmentType;
  delete copy.countAttachments;
  delete copy.dataSheetAdded;
  delete copy.certificationAdded;
  if (ignoreActiveDynamics) {
    // TIM asynchronously creates/moves active-product media, warehouse levels,
    // packaging levels and scoring timestamps. These fields are never present
    // in this script's tightly guarded save payload.
    delete copy.mainPhoto;
    delete copy.stockLevel;
    delete copy.packagingLevels;
    delete copy.lastUpdateScoringDate;
  }
  return copy;
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

function relation(asset, field) {
  const row = {
    id: Number(asset.id),
    path: String(asset.path),
    type: "asset",
    subtype: "document",
    expirationdate: null,
    rowId: `${Number(asset.id)}$$1$$asset`,
  };
  return [row];
}

function relationMatches(value, asset) {
  return Array.isArray(value)
    && value.length === 1
    && Number(value[0]?.id) === Number(asset.id)
    && String(value[0]?.path || "") === String(asset.path);
}

function relationEmpty(value) {
  return value == null || (Array.isArray(value) && value.length === 0);
}

const apply = process.argv.includes("--apply");
const nativeRequests = process.argv.includes("--native-requests");
const directSave = process.argv.includes("--direct-save");
const limit = Math.max(1, Number(argumentValue("--limit", "1")) || 1);
const start = Math.max(0, Number(argumentValue("--start", "0")) || 0);
const maxCards = Math.max(0, Number(argumentValue("--max-cards", "0")) || 0);
const allowedStates = argumentValue("--allowed-states", "new").split(",").map((value) => value.trim()).filter(Boolean);
const outputPath = resolve(argumentValue("--output", "exports/tim/remediation/pr-mad-priority-documents-live.json"));
const queuePath = argumentValue("--queue", "");
if (apply && maxCards < 1) throw new Error("Tryb --apply wymaga dodatniego --max-cards.");

const sourceRoot = "/Users/karolbohdanowicz/Desktop/_PRESCOT/_2026/TIM.PL/TIM - karty ce";
const defaultQueue = [
  { id: 15907539, ean: "5905475368073", model: "PR-MAD36-1224", sheet: `${sourceRoot}/Karty katalogowe/Zasilacze LED/PR-MAD-AUTODETEKCJA/PR-MAD36-1224.pdf` },
  { id: 15907542, ean: "5905475368080", model: "PR-MAD60-1224", sheet: `${sourceRoot}/Karty katalogowe/Zasilacze LED/PR-MAD-AUTODETEKCJA/PR-MAD60-1224.pdf` },
  { id: 15907545, ean: "5905475368097", model: "PR-MAD100-1224", sheet: `${sourceRoot}/Karty katalogowe/Zasilacze LED/PR-MAD-AUTODETEKCJA/PR-MAD100-1224.pdf` },
  { id: 15907551, ean: "5905475368103", model: "PR-MAD150-1224", sheet: `${sourceRoot}/Karty katalogowe/Zasilacze LED/PR-MAD-AUTODETEKCJA/PR-MAD150-1224.pdf` },
  { id: 15907554, ean: "5905475368110", model: "PR-MAD200-1224", sheet: `${sourceRoot}/Karty katalogowe/Zasilacze LED/PR-MAD-AUTODETEKCJA/PR-MAD200-1224.pdf` },
];

const commonFiles = {
  certifications: {
    source: `${sourceRoot}/Zasilacze LED/CE Prescot zasilacze PR-MADXX-1224.pdf`,
    filename: "CE_Prescot_zasilacze_PR-MADXX-1224.pdf",
  },
  instructions: {
    source: resolve("tmp/pdfs/priorities/Instrukcja-PR-MADXX-1224.pdf"),
    filename: "Instrukcja_PR-MADXX-1224.pdf",
  },
};
const queueDocument = queuePath ? JSON.parse(await readFile(resolve(queuePath), "utf8")) : null;
const sourceQueue = queuePath ? queueDocument?.items : defaultQueue;
if (!Array.isArray(sourceQueue)) throw new Error("Brak tablicy items w kolejce dokumentów.");
const queue = sourceQueue.slice(start, start + limit);

const report = {
  generatedAt: new Date().toISOString(),
  apply,
  nativeRequests,
  directSave,
  queuePath: queuePath ? resolve(queuePath) : "",
  start,
  limit,
  maxCards,
  allowedStates,
  queue: queue.map(({ id, ean, model }) => ({ id, ean, model })),
  uploadedAssets: [],
  reusedAssets: [],
  allowedWrites: [],
  blockedWrites: [],
  observedNativeWrites: [],
  results: [],
  fatalError: "",
};
const persist = () => writeFile(outputPath, `${JSON.stringify(report, null, 2)}\n`, "utf8");

let currentGuard = null;
let written = 0;
const browser = await chromium.connectOverCDP(CDP_URL);
const context = browser.contexts()[0];
if (!context) throw new Error("Brak aktywnego kontekstu Chrome.");
let page = null;
let frame = null;
for (const candidate of context.pages()) {
  for (const candidateFrame of candidate.frames().filter((item) => item.url().includes("/pimcore/admin/"))) {
    const authenticated = await candidateFrame.evaluate(() => {
      let user = null;
      try { user = window.pimcore?.globalmanager?.get?.("user"); } catch {}
      const currentUser = window.pimcore?.currentuser;
      return Boolean(window.Ext)
        && Boolean(window.pimcore?.settings?.csrfToken)
        && (typeof user?.isAllowed === "function"
          || (Number(currentUser?.id) > 0 && currentUser?.active === true));
    }).catch(() => false);
    if (authenticated) {
      page = candidate;
      frame = candidateFrame;
      break;
    }
  }
  if (frame) break;
}
if (!page || !frame) throw new Error("Brak istniejącej uwierzytelnionej ramki PIMCORE.");

if (apply && nativeRequests && page.url().includes("/pimcore/admin/")) {
  await page.reload({ waitUntil: "domcontentloaded" });
  await page.waitForTimeout(2_000);
  frame = page.mainFrame();
  const refreshed = await frame.evaluate(() => Boolean(window.Ext)
    && Boolean(window.pimcore?.settings?.csrfToken)
    && Number(window.pimcore?.currentuser?.id) > 0
    && window.pimcore?.currentuser?.active === true).catch(() => false);
  if (!refreshed) throw new Error("Nie udało się odświeżyć uwierzytelnionej sesji PIMCORE.");
}

const routeHandler = async (route) => {
  const request = route.request();
  const method = request.method().toUpperCase();
  if (["GET", "HEAD", "OPTIONS"].includes(method)) return route.continue();
  const url = new URL(request.url());

  if (method === "POST" && currentGuard?.objectId
    && url.origin === TIM_ORIGIN
    && url.pathname === `/pimcore/admin/workflow/actions/${currentGuard.objectId}`) {
    const params = new URLSearchParams(request.postData() || "");
    if (params.get("ctype") === "object"
      && params.get("cid") === String(currentGuard.objectId)
      && params.get("classId") === String(currentGuard.classId)
      && [...params.keys()].sort().join(",") === "cid,classId,ctype"
      && Boolean(request.headers()["x-pimcore-csrf-token"])) {
      report.allowedWrites.push({ kind: "workflow_actions_read", objectId: currentGuard.objectId });
      return route.continue();
    }
    report.blockedWrites.push({ method, url: request.url(), reason: "workflow_actions_guard_failed" });
    return route.abort("blockedbyclient");
  }

  if (method === "PUT" && currentGuard?.allowUnlock === true
    && url.origin === TIM_ORIGIN
    && url.pathname === "/pimcore/admin/element/unlock-element") {
    const params = new URLSearchParams(request.postData() || "");
    if (params.get("id") === String(currentGuard.objectId)
      && params.get("type") === "object"
      && [...params.keys()].sort().join(",") === "id,type") {
      report.allowedWrites.push({ kind: "release_own_lock", objectId: currentGuard.objectId });
      return route.continue();
    }
    report.blockedWrites.push({ method, url: request.url(), reason: "unlock_guard_failed" });
    return route.abort("blockedbyclient");
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
      report.allowedWrites.push({ kind: "asset", objectId: currentGuard.objectId, filename: currentGuard.filename });
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
        || !same(dirtyFields, currentGuard.dirtyFields)) throw new Error("object_payload_guard_failed");
      report.allowedWrites.push({ kind: "object", objectId: currentGuard.objectId, dirtyFields });
      return route.continue();
    } catch (error) {
      report.blockedWrites.push({ method, url: request.url(), reason: error.message });
      return route.abort("blockedbyclient");
    }
  }

  report.blockedWrites.push({ method, url: request.url(), reason: "not_allowlisted" });
  return route.abort("blockedbyclient");
};
const nativeRequestObserver = (request) => {
  const method = request.method().toUpperCase();
  if (["GET", "HEAD", "OPTIONS"].includes(method)) return;
  const url = new URL(request.url());
  report.observedNativeWrites.push({ method, path: url.pathname, query: url.search });
};
if (nativeRequests) page.on("request", nativeRequestObserver);
else await page.route("**/*", routeHandler);

async function getJson(path) {
  if (nativeRequests) {
    return frame.evaluate(async (requestPath) => {
      const response = await fetch(`/pimcore${requestPath}`, {
        credentials: "same-origin",
        headers: { Accept: "application/json", "Cache-Control": "no-cache" },
      });
      let payload = null;
      try { payload = await response.json(); } catch {}
      return { status: response.status, payload };
    }, path);
  }
  const response = await context.request.get(`${TIM_ORIGIN}/pimcore${path}`, { headers: { Accept: "application/json", "Cache-Control": "no-cache" } });
  let payload = null;
  try { payload = await response.json(); } catch {}
  return { status: response.status(), payload };
}

async function readObject(id) {
  for (let attempt = 0; attempt < 8; attempt += 1) {
    const result = await getJson(`/admin/object/get?id=${id}&_=${Date.now()}-${attempt}`);
    if (result.status === 200 && result.payload) return result.payload;
    await page.waitForTimeout(750);
  }
  throw new Error(`object_read_failed:${id}`);
}

async function verifyWritableSession(objectId, classId) {
  currentGuard = { kind: "csrf_preflight", objectId, classId, allowUnlock: false };
  const response = await frame.evaluate(async ({ id, classIdValue }) => {
    const body = new URLSearchParams({ ctype: "object", cid: String(id), classId: String(classIdValue) });
    const result = await fetch(`/pimcore/admin/workflow/actions/${id}`, {
      method: "POST",
      credentials: "same-origin",
      headers: {
        "X-Pimcore-CSRF-Token": window.pimcore.settings.csrfToken,
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
      },
      body,
    });
    return { success: result.ok, status: result.status, body: String(await result.text()).slice(0, 20_000) };
  }, { id: objectId, classIdValue: classId });
  currentGuard = null;
  if (response.status !== 200 || response.success !== true) {
    throw new Error(`pimcore_writable_session_unavailable:http_${response.status}`);
  }
}

async function closeObject(id) {
  await frame.evaluate((objectId) => {
    const object = window.pimcore?.globalmanager?.get?.(`object_${objectId}`);
    try { object?.tab?.close?.(); } catch {}
  }, id).catch(() => {});
  await page.waitForTimeout(300);
}

async function releaseOwnLock(id) {
  return frame.evaluate(async (objectId) => {
    const probe = await fetch(`/pimcore/admin/object/get?id=${objectId}&_=${Date.now()}`, {
      credentials: "same-origin",
      headers: { Accept: "application/json", "Cache-Control": "no-cache" },
    });
    let payload = null;
    try { payload = await probe.json(); } catch {}
    const currentUserId = Number(window.pimcore?.currentuser?.id);
    if (!payload?.editlock) return { released: false, reason: "no_lock" };
    if (Number(payload.editlock.userId) !== currentUserId) return { released: false, reason: "foreign_lock" };
    const response = await new Promise((resolveRequest) => {
      window.Ext.Ajax.request({
        url: "/pimcore/admin/element/unlock-element",
        method: "PUT",
        headers: { "X-Pimcore-CSRF-Token": window.pimcore.settings.csrfToken },
        params: { id: objectId, type: "object" },
        callback: (_options, success, result) => resolveRequest({
          success,
          status: result?.status || 0,
          body: String(result?.responseText || "").slice(0, 2_000),
        }),
      });
    });
    if (!response.success || response.status !== 200) throw new Error(`own_lock_release_failed:http_${response.status}`);
    return { released: true, reason: "own_lock", status: response.status };
  }, id);
}

let assetTreeCache = null;
async function listAssets(force = false) {
  if (!force && Array.isArray(assetTreeCache)) return assetTreeCache;
  const limit = 500;
  const first = await getJson(`/admin/asset/tree-get-children-by-id?node=${ASSET_PARENT_ID}&limit=${limit}&start=0&view=MULTIMEDIA_IMPORT&_=${Date.now()}`);
  if (first.status !== 200 || !Array.isArray(first.payload?.nodes)) throw new Error("asset_tree_read_failed");
  const nodes = [...first.payload.nodes];
  const total = Math.max(nodes.length, Number(first.payload?.total) || 0);
  for (let start = nodes.length; start < total; start += limit) {
    const page = await getJson(`/admin/asset/tree-get-children-by-id?node=${ASSET_PARENT_ID}&limit=${limit}&start=${start}&view=MULTIMEDIA_IMPORT&_=${Date.now()}-${start}`);
    if (page.status !== 200 || !Array.isArray(page.payload?.nodes)) throw new Error(`asset_tree_page_read_failed:${start}`);
    nodes.push(...page.payload.nodes);
  }
  assetTreeCache = nodes;
  return assetTreeCache;
}

async function verifyAsset(id, expectedPath, force = false) {
  const matches = (await listAssets(force)).filter((node) => Number(node.id) === Number(id));
  if (matches.length !== 1
    || String(matches[0].path || "") !== expectedPath
    || String(matches[0].type || "") !== "document") throw new Error(`asset_verification_failed:${id}`);
  return { id: Number(id), path: expectedPath, type: "document" };
}

async function findOrUpload({ objectId, source, filename }) {
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
  const result = await frame.evaluate(async ({ parentPath, filenameValue, bytesBase64 }) => {
    const binary = atob(bytesBase64);
    const bytesArray = new Uint8Array(binary.length);
    for (let index = 0; index < binary.length; index += 1) bytesArray[index] = binary.charCodeAt(index);
    const body = new FormData();
    body.append("Filedata", new File([bytesArray], filenameValue, { type: "application/pdf" }));
    body.append("filename", filenameValue);
    body.append("csrfToken", window.pimcore.settings.csrfToken);
    const response = await fetch(`/pimcore/admin/asset/add-asset?parentPath=${encodeURIComponent(parentPath)}&uploadAssetType=document`, { method: "POST", credentials: "same-origin", body });
    let payload = null;
    try { payload = await response.json(); } catch {}
    return { status: response.status, payload };
  }, { parentPath: ASSET_PARENT, filenameValue: filename, bytesBase64: bytes.toString("base64") });
  currentGuard = null;
  const id = Number(result.payload?.asset?.id);
  if (result.status !== 200 || result.payload?.success !== true || !Number.isFinite(id)) throw new Error(`asset_upload_failed:${filename}:http_${result.status}`);
  assetTreeCache = null;
  const asset = await verifyAsset(id, expectedPath, true);
  report.uploadedAssets.push({ objectId, source, ...asset });
  await persist();
  return asset;
}

for (const product of queue) {
  if (apply && written >= maxCards) break;
  const result = { id: product.id, ean: product.ean, model: product.model, status: "failed" };
  currentGuard = null;
  try {
    const before = await readObject(product.id);
    const data = before.data || {};
    const description = String(data.productDescriptions?.data?.longMarketingDescription || "");
    const requireDescriptionModel = product.requireDescriptionModel !== false;
    const timPrice = numericPrice(data.listPrice);
    const liveState = String(data.state || "");
    const photoPath = String(data.mainPhoto || "");
    if (Number(before.general?.id) !== product.id
      || String(data.ean || "") !== product.ean
      || String(data.manufacturerIndex || "") !== product.model
      || before.general?.published !== true
      || !allowedStates.includes(liveState)
      || !["new", "new_for_approval", "active"].includes(liveState)
      || String(data.status || "") !== (liveState === "active" ? "active" : "new")
      || (liveState === "active" && !String(data.timIndex || "").trim())
      || (product.xmlStock != null && Number(product.xmlStock) <= 0)
      || (product.timListPrice != null && Math.abs(timPrice - Number(product.timListPrice)) > 0.0001)
      || (product.xmlPrice != null && Math.abs(timPrice - Number(product.xmlPrice)) > 0.0001)
      || !(photoPath.startsWith("/Produkty/PRESCOT SPÓŁKA Z-00060865/") || photoPath.startsWith("/PIM-MEDIA/Products/GLOWNA/"))
      || (requireDescriptionModel && !description.includes(product.model))
      || /\b\d{13}\b/.test(description)) throw new Error("identity_description_or_state_guard_failed");
    if (before.general?.locked) {
      result.status = "locked";
      result.reason = "live_object_locked";
      report.results.push(result);
      await persist();
      continue;
    }
    const specs = product.documents || {
      certifications: commonFiles.certifications,
      instructions: commonFiles.instructions,
      dataSheet: { source: product.sheet, filename: `${product.model}_karta_katalogowa.pdf` },
    };
    const fields = Object.keys(specs);
    if (!fields.length || fields.some((field) => !["certifications", "instructions", "dataSheet"].includes(field))) {
      throw new Error("invalid_document_fields");
    }
    for (const field of fields) {
      if (!relationEmpty(data[field])) throw new Error(`nonempty_${field}_requires_review`);
    }
    if (!apply) {
      result.status = "verified_ready_dry_run";
      result.documents = Object.fromEntries(Object.entries(specs).map(([field, spec]) => [field, spec.filename]));
      currentGuard = { kind: "dry_read_cleanup", objectId: product.id, classId: before.general.classId, allowUnlock: true };
      result.lockRelease = await releaseOwnLock(product.id);
      currentGuard = null;
      report.results.push(result);
      await persist();
      continue;
    }

    await verifyWritableSession(product.id, before.general.classId);

    const assets = {};
    for (const [field, spec] of Object.entries(specs)) assets[field] = await findOrUpload({ objectId: product.id, ...spec });
    const saveData = {
      ...Object.fromEntries(Object.entries(assets).map(([field, asset]) => [field, relation(asset, field)])),
      netCatalogPrice: clone(data.netCatalogPrice),
    };
    const dirtyFields = fields;
    const ignoreActiveDynamics = liveState === "active";
    const beforeData = withoutDocumentFields(data, ignoreActiveDynamics);
    const beforeGeneral = stableGeneral(before.general);
    const beforeWorkflow = clone(before.workflowManagement);
    const beforeVersion = Number(before.general.versionCount);
    if (!directSave) {
      currentGuard = { kind: "open", objectId: product.id, classId: before.general.classId, allowUnlock: false };
      await frame.evaluate((id) => window.pimcore.helpers.openObject(id, "object"), product.id);
      await frame.waitForFunction((id) => Boolean(window.pimcore?.globalmanager?.get?.(`object_${id}`)), product.id, { timeout: 20_000 });
      await page.waitForTimeout(1_200);
      const lockDialog = frame.locator(".x-message-box").filter({ hasText: /Inna osoba używa tego elementu/i }).last();
      if (await lockDialog.isVisible().catch(() => false)) {
        const noButton = lockDialog.getByText("Nie", { exact: true }).last();
        if (await noButton.isVisible().catch(() => false)) await noButton.click();
        await closeObject(product.id);
        throw new Error("foreign_session_lock_dialog");
      }
    }
    currentGuard = { kind: "object", objectId: product.id, classId: before.general.classId, versionCount: beforeVersion, data: saveData, dirtyFields, allowUnlock: true };
    const save = await frame.evaluate(async ({ id, dataValue, generalValue, dirtyFieldsValue }) => {
      const body = new URLSearchParams({
        id: String(id),
        data: JSON.stringify(dataValue),
        general: JSON.stringify(generalValue),
        dirtyFields: JSON.stringify(dirtyFieldsValue),
      });
      const response = await fetch("/pimcore/admin/object/save?task=undefined", {
        method: "PUT",
        credentials: "same-origin",
        headers: {
          "X-Pimcore-CSRF-Token": window.pimcore.settings.csrfToken,
          "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        },
        body,
      });
      return { success: response.ok, status: response.status, body: String(await response.text()).slice(0, 100_000) };
    }, { id: product.id, dataValue: saveData, generalValue: saveGeneral(before.general), dirtyFieldsValue: dirtyFields });
    result.saveResponseStatus = save.status;
    result.saveResponseBody = save.body;
    let after = null;
    let applied = false;
    for (let attempt = 0; attempt < 8; attempt += 1) {
      after = await readObject(product.id);
      applied = Object.entries(assets).every(([field, asset]) => relationMatches(after.data?.[field], asset));
      if (applied) break;
      await page.waitForTimeout(750);
    }
    if (!applied) throw new Error(`object_save_not_applied:http_${save.status}`);
    if (!same(withoutDocumentFields(after.data, ignoreActiveDynamics), beforeData)) {
      const afterData = withoutDocumentFields(after.data, ignoreActiveDynamics);
      const changedKeys = [...new Set([...Object.keys(beforeData), ...Object.keys(afterData)])]
        .filter((key) => !same(beforeData[key], afterData[key]));
      result.protectedChanges = Object.fromEntries(changedKeys.map((key) => [key, {
        before: clone(beforeData[key]),
        after: clone(afterData[key]),
      }]));
      throw new Error(`protected_data_changed:${changedKeys.join(",")}`);
    }
    if (!same(stableGeneral(after.general), beforeGeneral)) throw new Error("stable_general_changed");
    if (!same(after.workflowManagement, beforeWorkflow)) throw new Error("workflow_changed");
    const versionDelta = Number(after.general.versionCount) - beforeVersion;
    if (![0, 1].includes(versionDelta)) throw new Error(`unexpected_version_delta:${versionDelta}`);
    result.status = "saved";
    result.httpStatus = save.status;
    result.beforeVersion = beforeVersion;
    result.afterVersion = Number(after.general.versionCount);
    result.dirtyFields = dirtyFields;
    result.documents = Object.fromEntries(Object.entries(assets).map(([field, asset]) => [field, asset.path]));
    result.protectedDataUnchanged = true;
    result.workflowUnchanged = true;
    if (!directSave) await closeObject(product.id);
    else result.lockRelease = await releaseOwnLock(product.id);
    currentGuard = null;
    written += 1;
    report.results.push(result);
    await persist();
    console.log(JSON.stringify({ id: product.id, model: product.model, status: result.status, documents: result.documents }));
  } catch (error) {
    await closeObject(product.id);
    if (directSave) result.lockRelease = await releaseOwnLock(product.id).catch((releaseError) => ({ released: false, reason: releaseError.message }));
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
if (nativeRequests) page.off("request", nativeRequestObserver);
else await page.unroute("**/*", routeHandler);
console.log(JSON.stringify({ written, uploaded: report.uploadedAssets.length, reused: report.reusedAssets.length, fatalError: report.fatalError }));
if (report.fatalError) process.exitCode = 1;
process.exit(process.exitCode || 0);
