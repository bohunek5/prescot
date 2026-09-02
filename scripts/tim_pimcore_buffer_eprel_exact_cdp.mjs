import { readFile, writeFile } from "node:fs/promises";
import { resolve } from "node:path";
import { chromium } from "../../radlight/node_modules/playwright/index.mjs";

const CDP_URL = "http://127.0.0.1:9222";
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

function criticalData(data, ignoreActiveDynamics = false) {
  const keys = [
    "ean", "manufacturerIndex", "suppliersProductId", "timIndex", "timName", "listPrice", "netCatalogPrice",
    "vatRate", "availability", "measureUnit", "state", "status", "sale", "productAvailableForSale", "mainPhoto",
    "manufacturer", "manufacturerMfgid", "manufacturerName", "assignedCategory24", "category", "categoryB24",
    "productDescriptions", "dataSheet", "certifications", "instructions", "stockLevel",
  ];
  const result = Object.fromEntries(keys.map((key) => [key, clone(data?.[key])]));
  if (ignoreActiveDynamics) {
    // TIM asynchronously enriches active cards after activation. These values
    // are never sent by this script, so their concurrent updates are safe.
    delete result.mainPhoto;
    delete result.stockLevel;
    delete result.packagingLevels;
    delete result.lastUpdateScoringDate;
  }
  return result;
}

function relation(asset, subtype) {
  return [{
    id: Number(asset.id),
    path: String(asset.path),
    type: "asset",
    subtype,
    expirationdate: null,
    rowId: `${Number(asset.id)}$$1$$asset`,
  }];
}

function relationMatches(value, asset, subtype) {
  return Array.isArray(value)
    && value.length === 1
    && Number(value[0]?.id) === Number(asset.id)
    && String(value[0]?.path || "") === String(asset.path)
    && String(value[0]?.subtype || "") === subtype;
}

function emptyRelation(value) {
  return value == null || (Array.isArray(value) && value.length === 0);
}

const apply = process.argv.includes("--apply");
const replaceInvalidLegacyEnergy = process.argv.includes("--replace-invalid-legacy-energy");
const legacyEnergyAllowlist = {
  9567950: {
    energyClass: "E | Nowe oznaczenie",
    label: { id: 17858176, path: "/PIM-MEDIA/Products/GLOWNA/0001/000/21/006/52/0001-00021-00652.jpg" },
    fiche: { id: 17858177, path: "/PIM-MEDIA/Products/GLOWNA/0001/000/21/006/52/0001-00021-00652.pdf" },
  },
  10047335: {
    energyClass: "E | Nowe oznaczenie",
    label: { id: 17646305, path: "/PIM-MEDIA/Products/GLOWNA/0001/000/21/704/83/0001-00021-70483.jpg" },
    fiche: { id: 17646306, path: "/PIM-MEDIA/Products/GLOWNA/0001/000/21/704/83/0001-00021-70483.pdf" },
  },
};
const startIndex = Math.max(0, Number(argumentValue("--start-index", "0")) || 0);
const limit = Math.max(1, Number(argumentValue("--limit", "1")) || 1);
const maxCards = Math.max(0, Number(argumentValue("--max-cards", "0")) || 0);
const allowedStates = argumentValue("--allowed-states", "new").split(",").map((value) => value.trim()).filter(Boolean);
if (apply && maxCards < 1) throw new Error("Tryb --apply wymaga dodatniego --max-cards.");
const queuePath = resolve(argumentValue("--queue", "exports/tim/remediation/buffer-eprel-exact-queue-2026-08-31.json"));
const outputPath = resolve(argumentValue("--output", "exports/tim/remediation/buffer-eprel-exact-cdp-live.json"));
const queueDocument = JSON.parse(await readFile(queuePath, "utf8"));
if (!Array.isArray(queueDocument?.items)) throw new Error("Brak tablicy items w kolejce.");
const queue = queueDocument.items.slice(startIndex, startIndex + limit);
const duplicateEvidencePaths = argumentValue("--duplicate-evidence", "")
  .split(",")
  .map((value) => value.trim())
  .filter(Boolean)
  .map((value) => resolve(value));
const duplicateEvidence = await Promise.all(duplicateEvidencePaths.map(async (path) => ({
  path,
  document: JSON.parse(await readFile(path, "utf8")),
})));

const report = {
  generatedAt: new Date().toISOString(),
  apply,
  queuePath,
  startIndex,
  limit,
  maxCards,
  allowedStates,
  duplicateEvidencePaths,
  checked: 0,
  written: 0,
  uploadedAssets: [],
  reusedAssets: [],
  observedWrites: [],
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
      && Number(window.pimcore?.currentuser?.id) > 0
      && window.pimcore?.currentuser?.active === true).catch(() => false);
    if (authenticated) {
      page = candidate;
      frame = candidateFrame;
      break;
    }
  }
  if (frame) break;
}
if (!page || !frame) throw new Error("Brak istniejącej uwierzytelnionej ramki PIMCORE.");

const observeWrite = (request) => {
  const method = request.method().toUpperCase();
  if (["GET", "HEAD", "OPTIONS"].includes(method)) return;
  const url = new URL(request.url());
  report.observedWrites.push({ method, path: url.pathname, query: url.search });
};
page.on("request", observeWrite);

async function getJson(path) {
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

async function readObject(id) {
  for (let attempt = 0; attempt < 8; attempt += 1) {
    const result = await getJson(`/admin/object/get?id=${id}&_=${Date.now()}-${attempt}`);
    if (result.status === 200 && result.payload) return result.payload;
    await page.waitForTimeout(750);
  }
  throw new Error(`object_read_failed:${id}`);
}

async function verifyWritableSession(objectId, classId) {
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
  if (response.status !== 200 || response.success !== true) {
    throw new Error(`pimcore_writable_session_unavailable:http_${response.status}`);
  }
}

async function findExactModelDuplicates(model, objectId) {
  return frame.evaluate(async ({ term, currentId }) => {
    const fields = ["id", "manufacturerIndex", "timIndex", "timName", "status", "state"];
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
    const response = await new Promise((resolveRequest) => {
      window.Ext.Ajax.request({
        url: "/pimcore/admin/bundle/advanced-object-search/admin/grid-proxy?classId=3&xaction=read",
        method: "POST",
        headers: { "X-Pimcore-CSRF-Token": window.pimcore.settings.csrfToken },
        params: {
          class: "product",
          language: "pl",
          filter: JSON.stringify(filter),
          page: 1,
          start: 0,
          limit: 100,
          "fields[]": fields,
        },
        callback: (_options, success, result) => resolveRequest({
          success,
          status: result?.status || 0,
          body: String(result?.responseText || "").slice(0, 200_000),
        }),
      });
    });
    let payload = null;
    try { payload = JSON.parse(response.body); } catch {}
    if (!response.success || response.status !== 200 || !payload?.success) {
      throw new Error(`duplicate_search_failed:http_${response.status}`);
    }
    return (payload.data || [])
      .filter((record) => Number(record.id || record.o_id) !== Number(currentId)
        && String(record.manufacturerIndex || "") === String(term))
      .map((record) => ({
        id: Number(record.id || record.o_id),
        timIndex: String(record.timIndex || ""),
        timName: String(record.timName || record.key || ""),
        status: String(record.status?.value || record.status || ""),
        state: String(record.state?.value || record.state || ""),
      }));
  }, { term: model, currentId: objectId });
}

function verifyUniqueModelFromEvidence(model, objectId, ean) {
  const duplicates = [];
  for (const source of duplicateEvidence) {
    if (Array.isArray(source.document?.items)) {
      const rows = source.document.items;
      const current = rows.filter((record) => Number(record.id) === Number(objectId)
        && String(record.model || record.manufacturerIndex || "") === String(model));
      if (current.length !== 1 || String(current[0].ean || "") !== String(ean)) {
        throw new Error(`duplicate_evidence_identity_failed:${source.path}`);
      }
      duplicates.push(...rows
        .filter((record) => Number(record.id) !== Number(objectId)
          && String(record.model || record.manufacturerIndex || "") === String(model))
        .map((record) => ({
          id: Number(record.id),
          timIndex: String(record.timIndex || ""),
          timName: String(record.timName || record.name || ""),
          status: String(record.status?.value || record.status || ""),
          state: String(record.state?.value || record.state || ""),
          evidence: source.path,
        })));
      duplicates.push(...(Array.isArray(current[0].activeDuplicates) ? current[0].activeDuplicates : [])
        .map((id) => ({ id: Number(id), evidence: source.path, source: "activeDuplicates" })));
      continue;
    }
    const products = Array.isArray(source.document?.products) ? source.document.products : [];
    const exact = products.filter((record) => String(record.manufacturerIndex || record.model || "") === String(model));
    const current = exact.filter((record) => Number(record.id) === Number(objectId));
    if (current.length !== 1 || String(current[0].ean || "") !== String(ean)) {
      throw new Error(`duplicate_evidence_identity_failed:${source.path}`);
    }
    duplicates.push(...exact
      .filter((record) => Number(record.id) !== Number(objectId))
      .map((record) => ({
        id: Number(record.id),
        timIndex: String(record.timIndex || ""),
        timName: String(record.timName || ""),
        status: String(record.status?.value || record.status || ""),
        state: String(record.state?.value || record.state || ""),
        evidence: source.path,
      })));
  }
  return duplicates;
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
        callback: (_options, success, result) => resolveRequest({ success, status: result?.status || 0 }),
      });
    });
    if (!response.success || response.status !== 200) throw new Error(`own_lock_release_failed:http_${response.status}`);
    return { released: true, reason: "own_lock" };
  }, id);
}

async function listAssets() {
  const result = await getJson(`/admin/asset/tree-get-children-by-id?node=${ASSET_PARENT_ID}&limit=1000&start=0&view=MULTIMEDIA_IMPORT&_=${Date.now()}`);
  if (result.status !== 200 || !Array.isArray(result.payload?.nodes)) throw new Error("asset_tree_read_failed");
  return result.payload.nodes;
}

async function verifyAsset(id, expectedPath, expectedType) {
  const result = await getJson(`/admin/asset/get-data-by-id?id=${Number(id)}&_=${Date.now()}`);
  const livePath = `${String(result.payload?.path || "").replace(/\/$/, "")}/${String(result.payload?.filename || "")}`;
  if (result.status !== 200
    || livePath !== expectedPath
    || String(result.payload?.type || "") !== expectedType) throw new Error(`asset_verification_failed:${id}`);
  return { id: Number(id), path: expectedPath, type: expectedType };
}

async function findOrUpload({ objectId, source, filename, assetType, mimeType }) {
  const expectedPath = `${ASSET_PARENT}/${filename}`;
  const exact = (await listAssets()).filter((node) => String(node.key || "") === filename && String(node.path || "") === expectedPath);
  if (exact.length > 1) throw new Error(`duplicate_exact_asset:${filename}`);
  if (exact.length === 1) {
    const asset = await verifyAsset(exact[0].id, expectedPath, assetType);
    report.reusedAssets.push({ objectId, source, ...asset });
    await persist();
    return asset;
  }
  if (!apply) return { id: 0, path: expectedPath, type: assetType, pendingUpload: true };
  const bytes = await readFile(source);
  if (assetType === "image" && mimeType === "image/png"
    && !bytes.subarray(0, 8).equals(Buffer.from([137, 80, 78, 71, 13, 10, 26, 10]))) {
    throw new Error(`source_is_not_png:${filename}`);
  }
  if (assetType === "image" && mimeType === "image/jpeg"
    && !bytes.subarray(0, 2).equals(Buffer.from([255, 216]))) {
    throw new Error(`source_is_not_jpeg:${filename}`);
  }
  if (assetType === "document" && bytes.subarray(0, 4).toString("ascii") !== "%PDF") {
    throw new Error(`source_is_not_pdf:${filename}`);
  }
  const result = await frame.evaluate(async ({ parentPath, filenameValue, assetTypeValue, mimeTypeValue, bytesBase64 }) => {
    const binary = atob(bytesBase64);
    const bytesArray = new Uint8Array(binary.length);
    for (let index = 0; index < binary.length; index += 1) bytesArray[index] = binary.charCodeAt(index);
    const body = new FormData();
    body.append("Filedata", new File([bytesArray], filenameValue, { type: mimeTypeValue }));
    body.append("filename", filenameValue);
    body.append("csrfToken", window.pimcore.settings.csrfToken);
    const response = await fetch(`/pimcore/admin/asset/add-asset?parentPath=${encodeURIComponent(parentPath)}&uploadAssetType=${encodeURIComponent(assetTypeValue)}`, {
      method: "POST",
      credentials: "same-origin",
      body,
    });
    let payload = null;
    try { payload = await response.json(); } catch {}
    return { status: response.status, payload };
  }, {
    parentPath: ASSET_PARENT,
    filenameValue: filename,
    assetTypeValue: assetType,
    mimeTypeValue: mimeType,
    bytesBase64: bytes.toString("base64"),
  });
  const id = Number(result.payload?.asset?.id);
  if (result.status !== 200 || result.payload?.success !== true || !Number.isFinite(id)) {
    throw new Error(`asset_upload_failed:${filename}:http_${result.status}`);
  }
  const asset = await verifyAsset(id, expectedPath, assetType);
  report.uploadedAssets.push({ objectId, source, ...asset });
  await persist();
  return asset;
}

for (let offset = 0; offset < queue.length; offset += 1) {
  if (apply && report.written >= maxCards) break;
  const product = queue[offset];
  const objectId = Number(product.pimcoreId);
  const item = { index: startIndex + offset, objectId, ean: product.ean, model: product.manufacturerCode, eprelId: product.eprelId, status: "failed" };
  try {
    report.checked += 1;
    const before = await readObject(objectId);
    const data = before.data || {};
    const description = String(data.productDescriptions?.data?.longMarketingDescription || "");
    const timPrice = numericPrice(data.listPrice);
    const liveState = String(data.state || "");
    const photoPath = String(data.mainPhoto || "");
    if (Number(before.general?.id) !== objectId
      || String(data.ean || "") !== String(product.ean)
      || String(data.manufacturerIndex || "") !== String(product.manufacturerCode)
      || before.general?.published !== true
      || !allowedStates.includes(liveState)
      || !(["new", "active"].includes(liveState) && String(data.status || "") === liveState)
      || (liveState === "active" && !String(data.timIndex || "").trim())
      || Number(product.xmlStock) <= 0
      || !Number.isFinite(Number(product.xmlPrice))
      || Math.abs(timPrice - Number(product.timListPrice)) > 0.0001
      || Math.abs(timPrice - Number(product.xmlPrice)) > 0.0001
      || !(photoPath.startsWith("/Produkty/PRESCOT SPÓŁKA Z-00060865/") || photoPath.startsWith("/PIM-MEDIA/Products/GLOWNA/"))
      || !description.includes(String(product.manufacturerCode))
      || /\b\d{13}\b/.test(description)) throw new Error("identity_price_description_or_state_guard_failed");
    if (before.general?.locked) throw new Error("live_object_locked");
    const legacy = legacyEnergyAllowlist[objectId];
    const legacyMatches = Boolean(replaceInvalidLegacyEnergy && legacy)
      && String(data.energyClass || "") === legacy.energyClass
      && Array.isArray(data.energyClassLabels) && data.energyClassLabels.length === 1
      && Number(data.energyClassLabels[0]?.id) === legacy.label.id
      && String(data.energyClassLabels[0]?.path || "") === legacy.label.path
      && Array.isArray(data.energyTechnicalCards) && data.energyTechnicalCards.length === 1
      && Number(data.energyTechnicalCards[0]?.id) === legacy.fiche.id
      && String(data.energyTechnicalCards[0]?.path || "") === legacy.fiche.path;
    if (replaceInvalidLegacyEnergy && !legacyMatches) throw new Error("legacy_energy_allowlist_guard_failed");
    if (!replaceInvalidLegacyEnergy) {
      if (!emptyRelation(data.energyClassLabels)) throw new Error("nonempty_energy_label_requires_review");
      if (!emptyRelation(data.energyTechnicalCards)) throw new Error("nonempty_energy_card_requires_review");
      if (String(data.energyClass || "") && String(data.energyClass) !== String(product.energyClass)) {
        throw new Error("conflicting_energy_class_requires_review");
      }
    }

    const duplicates = duplicateEvidence.length
      ? verifyUniqueModelFromEvidence(product.manufacturerCode, objectId, product.ean)
      : await findExactModelDuplicates(product.manufacturerCode, objectId);
    if (duplicates.length) {
      item.status = "duplicate_existing_product";
      item.duplicates = duplicates;
      report.results.push(item);
      await persist();
      continue;
    }

    const labelFilename = `${product.manufacturerCode}_EPREL_${product.eprelId}_etykieta.jpg`;
    const labelSource = String(product.labelFile).replace(/\.png$/i, "_tim.jpg");
    const ficheFilename = `${product.manufacturerCode}_EPREL_${product.eprelId}_karta_informacyjna.pdf`;
    if (!apply) {
      item.status = "verified_ready_dry_run";
      item.timPrice = timPrice;
      item.xmlPrice = Number(product.xmlPrice);
      item.xmlStock = Number(product.xmlStock);
      item.documents = { labelFilename, ficheFilename };
      report.results.push(item);
      await persist();
      continue;
    }

    await verifyWritableSession(objectId, before.general.classId);
    const label = await findOrUpload({
      objectId,
      source: labelSource,
      filename: labelFilename,
      assetType: "image",
      mimeType: "image/jpeg",
    });
    const fiche = await findOrUpload({
      objectId,
      source: product.productInformationSheet,
      filename: ficheFilename,
      assetType: "document",
      mimeType: "application/pdf",
    });

    const ignoreActiveDynamics = liveState === "active";
    const beforeCritical = criticalData(data, ignoreActiveDynamics);
    const beforeGeneral = stableGeneral(before.general);
    const beforeWorkflow = clone(before.workflowManagement);
    const beforeVersion = Number(before.general.versionCount);
    const saveData = {
      energyClass: String(product.energyClass),
      energyClassLabels: relation(label, "image"),
      energyTechnicalCards: relation(fiche, "document"),
      netCatalogPrice: clone(data.netCatalogPrice),
    };
    const dirtyFields = ["energyClass", "energyClassLabels", "energyTechnicalCards"];
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
      return {
        success: response.ok,
        status: response.status,
        body: String(await response.text()).slice(0, 100_000),
      };
    }, { id: objectId, dataValue: saveData, generalValue: saveGeneral(before.general), dirtyFieldsValue: dirtyFields });
    item.saveResponse = { status: save.status, success: save.success, body: save.body };

    let after = null;
    let applied = false;
    for (let attempt = 0; attempt < 8; attempt += 1) {
      after = await readObject(objectId);
      applied = String(after.data?.energyClass || "") === String(product.energyClass)
        && relationMatches(after.data?.energyClassLabels, label, "image")
        && relationMatches(after.data?.energyTechnicalCards, fiche, "document");
      if (applied) break;
      await page.waitForTimeout(750);
    }
    if (!applied) throw new Error(`object_save_not_applied:http_${save.status}`);
    if (!same(criticalData(after.data, ignoreActiveDynamics), beforeCritical)) throw new Error("protected_critical_data_changed");
    if (!same(stableGeneral(after.general), beforeGeneral)) throw new Error("stable_general_changed");
    if (!same(after.workflowManagement, beforeWorkflow)) throw new Error("workflow_changed");
    const versionDelta = Number(after.general.versionCount) - beforeVersion;
    if (![0, 1].includes(versionDelta)) throw new Error(`unexpected_version_delta:${versionDelta}`);

    item.status = "saved";
    item.httpStatus = save.status;
    item.beforeVersion = beforeVersion;
    item.afterVersion = Number(after.general.versionCount);
    item.dirtyFields = dirtyFields;
    item.documents = { label: label.path, fiche: fiche.path };
    item.protectedCriticalDataUnchanged = true;
    item.workflowUnchanged = true;
    item.lockRelease = await releaseOwnLock(objectId);
    report.written += 1;
    report.results.push(item);
    await persist();
    console.log(JSON.stringify({ objectId, model: product.manufacturerCode, status: item.status, documents: item.documents }));
  } catch (error) {
    item.lockRelease = await releaseOwnLock(objectId).catch((releaseError) => ({ released: false, reason: releaseError.message }));
    item.status = "failed";
    item.reason = error.message;
    report.results.push(item);
    report.fatalError = `${product.manufacturerCode}: ${error.message}`;
    await persist();
    break;
  }
}

page.off("request", observeWrite);
await persist();
console.log(JSON.stringify({ checked: report.checked, written: report.written, uploaded: report.uploadedAssets.length, reused: report.reusedAssets.length, fatalError: report.fatalError }));
if (report.fatalError) process.exitCode = 1;
process.exit(process.exitCode || 0);
