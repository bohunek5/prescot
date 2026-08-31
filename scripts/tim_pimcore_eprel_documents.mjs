import { readFile, writeFile } from "node:fs/promises";
import { basename, dirname, extname, resolve } from "node:path";
import { chromium } from "../../radlight/node_modules/playwright/index.mjs";

function argumentValue(name, fallback = "") {
  const index = process.argv.indexOf(name);
  return index === -1 ? fallback : process.argv[index + 1] || fallback;
}

function clone(value) {
  return value == null ? value : JSON.parse(JSON.stringify(value));
}

function protectedDataSnapshot(data) {
  const stockLevel = clone(data?.stockLevel || []);
  for (const stock of stockLevel) {
    delete stock.modificationDate;
    delete stock.updatedAt;
  }
  const keys = [
    "ean", "manufacturer", "manufacturerMfgid", "manufacturerName", "manufacturerIndex", "suppliersProductId",
    "timIndex", "timName", "listPrice", "netCatalogPrice", "prize", "vatRate", "availability", "measureUnit",
    "status", "state", "sale", "productAvailableForSale", "mainPhoto", "assignedCategory24", "category", "categoryB24",
    "productDescriptions", "dataSheet", "instructions",
  ];
  return { ...Object.fromEntries(keys.map((key) => [key, clone(data?.[key])])), stockLevel };
}

function stableGeneralSnapshot(general) {
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

function relation(asset, subtype) {
  return [{
    id: Number(asset.id),
    path: String(asset.path),
    type: "asset",
    subtype,
    rowId: `${Number(asset.id)}$$1$$asset`,
  }];
}

function same(valueA, valueB) {
  return JSON.stringify(valueA) === JSON.stringify(valueB);
}

function isEmptyRelation(value) {
  return value == null || (Array.isArray(value) && value.length === 0);
}

function relationHasPath(value, path) {
  return Array.isArray(value) && value.length === 1 && String(value[0]?.path || "") === path;
}

function relationMatchesFilename(value, filename, productMediaPath) {
  if (!Array.isArray(value) || value.length !== 1) return false;
  const path = String(value[0]?.path || "");
  return path === `${assetParentPath}/${filename}` || path === `${productMediaPath}/${filename}`;
}

const profileDir = argumentValue("--profile-dir");
const queuePath = resolve(argumentValue("--queue", "exports/tim/remediation/eprel-exact-documents-queue.json"));
const outputPath = resolve(argumentValue("--output", "/tmp/tim-eprel-documents.json"));
const startIndex = Math.max(0, Number(argumentValue("--start-index", "0")) || 0);
const limit = Math.max(1, Number(argumentValue("--limit", "1")) || 1);
const maxCards = Math.max(0, Number(argumentValue("--max-cards", "0")) || 0);
const assetParentPath = argumentValue("--asset-parent", "/Import multimediow/24248");
const applySave = process.argv.includes("--apply");
if (!profileDir) throw new Error("Podaj --profile-dir.");
if (applySave && maxCards < 1) throw new Error("Tryb --apply wymaga dodatniego --max-cards.");
if (assetParentPath !== "/Import multimediow/24248") throw new Error("Niedozwolony katalog docelowy assetów.");

const queueDocument = JSON.parse(await readFile(queuePath, "utf8"));
const fullQueue = queueDocument?.items;
if (!Array.isArray(fullQueue)) throw new Error("Brak tablicy items w kolejce.");
const queue = fullQueue.slice(startIndex, startIndex + limit);
const results = [];
const allowedWrites = [];
const blockedWrites = [];
const uploadedAssets = [];
const reusedAssets = [];
let currentGuard = null;
let cardsWritten = 0;
let fatalError = "";
const report = () => ({
  generatedAt: new Date().toISOString(),
  queuePath,
  startIndex,
  limit,
  maxCards,
  assetParentPath,
  applySave,
  queueLength: queue.length,
  cardsWritten,
  counts: {
    checked: results.length,
    saved: results.filter((item) => ["saved", "saved_with_validation"].includes(item.status)).length,
    alreadyCurrent: results.filter((item) => item.status === "already_current").length,
    locked: results.filter((item) => item.status === "locked").length,
    skipped: results.filter((item) => item.status === "skipped").length,
    failed: results.filter((item) => item.status === "failed").length,
    assetsUploaded: uploadedAssets.length,
    assetsReused: reusedAssets.length,
  },
  fatalError,
  results,
  uploadedAssets,
  reusedAssets,
  allowedWrites,
  blockedWrites,
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
  const requestUrl = new URL(request.url());
  if (["GET", "HEAD", "OPTIONS"].includes(method)) return route.continue();

  if (applySave && method === "POST" && currentGuard?.kind === "asset") {
    try {
      if (requestUrl.origin !== "https://dostawca.tim.pl" || requestUrl.pathname !== "/pimcore/admin/asset/add-asset") {
        throw new Error("asset_url_not_allowlisted");
      }
      if (requestUrl.searchParams.get("parentPath") !== currentGuard.parentPath
        || requestUrl.searchParams.get("uploadAssetType") !== currentGuard.assetType
        || [...requestUrl.searchParams.keys()].sort().join(",") !== "parentPath,uploadAssetType") {
        throw new Error("asset_parent_path_guard_failed");
      }
      const contentType = String(request.headers()["content-type"] || "");
      const body = request.postDataBuffer();
      const bodyText = body?.toString("latin1") || "";
      const dispositionCount = (bodyText.match(/Content-Disposition: form-data;/g) || []).length;
      if (!contentType.startsWith("multipart/form-data; boundary=")
        || !body
        || dispositionCount !== 3
        || !bodyText.includes(`name="Filedata"; filename="${currentGuard.filename}"`)
        || !bodyText.includes(`name="filename"\r\n\r\n${currentGuard.filename}`)
        || !bodyText.includes("name=\"csrfToken\"")
        || body.indexOf(currentGuard.bytes) < 0) {
        throw new Error("asset_payload_guard_failed");
      }
      allowedWrites.push({
        objectId: currentGuard.objectId,
        method,
        path: requestUrl.pathname,
        parentPath: currentGuard.parentPath,
        filename: currentGuard.filename,
        assetType: currentGuard.assetType,
      });
      return route.continue();
    } catch (error) {
      blockedWrites.push({ objectId: currentGuard?.objectId || 0, method, url: request.url(), reason: error.message });
      return route.abort("blockedbyclient");
    }
  }

  if (applySave && method === "PUT" && currentGuard?.kind === "object") {
    try {
      if (requestUrl.origin !== "https://dostawca.tim.pl"
        || requestUrl.pathname !== "/pimcore/admin/object/save"
        || requestUrl.search !== "?task=undefined") {
        throw new Error("object_url_not_allowlisted");
      }
      const params = new URLSearchParams(request.postData() || "");
      const data = JSON.parse(params.get("data") || "null");
      const general = JSON.parse(params.get("general") || "null");
      const dirtyFields = JSON.parse(params.get("dirtyFields") || "null");
      if ([...params.keys()].sort().join(",") !== "data,dirtyFields,general,id"
        || params.get("id") !== String(currentGuard.objectId)
        || Number(general?.id) !== currentGuard.objectId
        || Number(general?.versionCount) !== currentGuard.versionCount
        || !same(data, currentGuard.data)
        || !same(dirtyFields, currentGuard.dirtyFields)) {
        throw new Error("object_save_guard_failed");
      }
      allowedWrites.push({ objectId: currentGuard.objectId, method, path: requestUrl.pathname, dirtyFields });
      return route.continue();
    } catch (error) {
      blockedWrites.push({ objectId: currentGuard?.objectId || 0, method, url: request.url(), reason: error.message });
      return route.abort("blockedbyclient");
    }
  }

  if (!/cdn-cgi\/rum|liveupdate\.pimcore\.org\/update-check/.test(request.url())) {
    blockedWrites.push({ objectId: currentGuard?.objectId || 0, method, url: request.url(), reason: "not_allowlisted" });
  }
  return route.abort("blockedbyclient");
});

const page = context.pages()[0] || await context.newPage();
await page.goto("https://dostawca.tim.pl/pimcore/", { waitUntil: "domcontentloaded", timeout: 45_000 });
await page.waitForTimeout(3_000);
const frame = page.frames().find((item) => item.url().includes("/pimcore/admin/"));
if (!frame) throw new Error("Nie znaleziono ramki PIMCORE.");

let readSequence = 0;
async function readObject(objectId) {
  for (let attempt = 0; attempt < 30; attempt += 1) {
    readSequence += 1;
    const response = await context.request.get(`https://dostawca.tim.pl/pimcore/admin/object/get?id=${objectId}&_=${Date.now()}-${readSequence}`, {
      headers: { Accept: "application/json", "Cache-Control": "no-cache" },
    });
    let object = null;
    try { object = await response.json(); } catch {}
    if (response.status() === 200 && object) return { status: 200, object };
    if (response.status() < 500) return { status: response.status(), object };
    await page.waitForTimeout(800 * (attempt + 1));
  }
  return { status: 599, object: null };
}

async function uploadAsset({ objectId, parentPath, sourcePath, filename, assetType, mimeType }) {
  const bytes = await readFile(sourcePath);
  const bytesBase64 = bytes.toString("base64");
  currentGuard = { kind: "asset", objectId, parentPath, filename, assetType, bytes };
  const response = await frame.evaluate(async ({ parentPathValue, filenameValue, assetTypeValue, mimeTypeValue, bytesBase64Value }) => {
    const binary = atob(bytesBase64Value);
    const fileBytes = new Uint8Array(binary.length);
    for (let index = 0; index < binary.length; index += 1) fileBytes[index] = binary.charCodeAt(index);
    const body = new FormData();
    body.append("Filedata", new File([fileBytes], filenameValue, { type: mimeTypeValue }));
    body.append("filename", filenameValue);
    body.append("csrfToken", window.pimcore.settings.csrfToken);
    const request = await fetch(`/pimcore/admin/asset/add-asset?parentPath=${encodeURIComponent(parentPathValue)}&uploadAssetType=${encodeURIComponent(assetTypeValue)}`, {
      method: "POST",
      credentials: "same-origin",
      body,
    });
    let payload = null;
    try { payload = await request.json(); } catch {}
    return { status: request.status, payload };
  }, { parentPathValue: parentPath, filenameValue: filename, assetTypeValue: assetType, mimeTypeValue: mimeType, bytesBase64Value: bytesBase64 });
  currentGuard = null;
  if (response.status !== 200 || response.payload?.success !== true || !response.payload?.asset) {
    const detail = String(response.payload?.message || response.payload?.error || "unknown_error").replace(/\s+/g, " ").slice(0, 500);
    throw new Error(`asset_upload_failed_http_${response.status}:${detail}`);
  }
  const asset = response.payload.asset;
  const expectedPath = `${parentPath}/${filename}`;
  const assetId = Number(asset.id);
  if (!Number.isFinite(assetId)) throw new Error("asset_upload_missing_id");
  let verifiedAsset = null;
  for (let attempt = 0; attempt < 5; attempt += 1) {
    const read = await context.request.get(`https://dostawca.tim.pl/pimcore/admin/asset/get-data-by-id?id=${assetId}&_=${Date.now()}-${attempt}`, {
      headers: { Accept: "application/json", "Cache-Control": "no-cache" },
    });
    try { verifiedAsset = await read.json(); } catch {}
    const currentPath = `${String(verifiedAsset?.path || "").replace(/\/$/, "")}/${String(verifiedAsset?.filename || "")}`;
    if (read.status() === 200 && currentPath === expectedPath && String(verifiedAsset?.type || "") === assetType) break;
    verifiedAsset = null;
    await page.waitForTimeout(1_000);
  }
  if (!verifiedAsset) {
    throw new Error(`asset_upload_verification_failed:${String(asset.path)}`);
  }
  const entry = { objectId, sourcePath, id: assetId, path: expectedPath, type: assetType };
  uploadedAssets.push(entry);
  await persist();
  return entry;
}

async function findOwnedAsset(objectId, filename, assetType) {
  const response = await context.request.get("https://dostawca.tim.pl/pimcore/admin/asset/tree-get-children-by-id?node=1658124&limit=500&start=0&view=MULTIMEDIA_IMPORT", {
    headers: { Accept: "application/json", "Cache-Control": "no-cache" },
  });
  let payload = null;
  try { payload = await response.json(); } catch {}
  if (response.status() !== 200 || !Array.isArray(payload?.nodes)) throw new Error("owned_asset_tree_read_failed");
  const expectedPath = `${assetParentPath}/${filename}`;
  const exact = payload.nodes.filter((node) => String(node.key || "") === filename && String(node.path || "") === expectedPath);
  if (exact.length > 1) throw new Error(`duplicate_exact_owned_asset:${filename}`);
  if (exact.length === 0) return null;
  if (String(exact[0].type || "") !== assetType || !Number.isFinite(Number(exact[0].id))) {
    throw new Error(`conflicting_exact_owned_asset:${filename}`);
  }
  const entry = { objectId, id: Number(exact[0].id), path: expectedPath, type: assetType };
  reusedAssets.push(entry);
  await persist();
  return entry;
}

async function verifyKnownAsset(objectId, expected, assetType) {
  const assetId = Number(expected?.id);
  const expectedPath = String(expected?.path || "");
  if (!Number.isFinite(assetId) || !expectedPath.startsWith(`${assetParentPath}/`)) throw new Error("known_asset_identity_guard_failed");
  const response = await context.request.get(`https://dostawca.tim.pl/pimcore/admin/asset/get-data-by-id?id=${assetId}&_=${Date.now()}`, {
    headers: { Accept: "application/json", "Cache-Control": "no-cache" },
  });
  let payload = null;
  try { payload = await response.json(); } catch {}
  const currentPath = `${String(payload?.path || "").replace(/\/$/, "")}/${String(payload?.filename || "")}`;
  if (response.status() !== 200 || currentPath !== expectedPath || String(payload?.type || "") !== assetType) {
    throw new Error("known_asset_live_verification_failed");
  }
  const entry = { objectId, id: assetId, path: expectedPath, type: assetType };
  reusedAssets.push(entry);
  await persist();
  return entry;
}

for (let offset = 0; offset < queue.length; offset += 1) {
  if (applySave && cardsWritten >= maxCards) break;
  const product = queue[offset];
  const objectId = Number(product.pimcoreId);
  const item = {
    index: startIndex + offset,
    objectId,
    ean: product.ean,
    manufacturerCode: product.manufacturerCode,
    timIndex: product.timIndex,
    eprelId: product.eprelId,
    status: "failed",
  };
  currentGuard = null;
  try {
    const labelBytes = await readFile(product.labelFile);
    const pdfBytes = await readFile(product.productInformationSheet);
    if (!labelBytes.subarray(0, 8).equals(Buffer.from([137, 80, 78, 71, 13, 10, 26, 10]))) throw new Error("label_is_not_png");
    if (pdfBytes.subarray(0, 4).toString("ascii") !== "%PDF") throw new Error("sheet_is_not_pdf");
    if (basename(product.productInformationSheet) !== `Fiche_${product.eprelId}_PL.pdf`) throw new Error("eprel_file_id_mismatch");

    const beforeRead = await readObject(objectId);
    const beforeObject = beforeRead.object;
    const data = beforeObject?.data || {};
    const liveStock = Math.max(0, ...(data.stockLevel || []).map((entry) => Number(entry.stockTotalQuantityMz) || 0));
    const identityMatches = beforeRead.status === 200
      && Number(beforeObject?.general?.id) === objectId
      && String(data.timIndex || "") === String(product.timIndex)
      && String(data.manufacturerIndex || "") === String(product.manufacturerCode)
      && String(data.ean || "") === String(product.ean)
      && data.state === "active"
      && liveStock > 0
      && beforeObject?.general?.published === true;
    if (!identityMatches) {
      item.status = "skipped";
      item.reason = "live_identity_state_or_stock_mismatch";
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
    const productMediaPath = dirname(String(data.mainPhoto || ""));
    if (!productMediaPath.startsWith("/PIM-MEDIA/Products/GLOWNA/") || !String(data.mainPhoto || "").endsWith(`/${product.timIndex}_1_pr.jpg`)) {
      item.status = "skipped";
      item.reason = "main_photo_path_guard_failed";
      results.push(item);
      await persist();
      continue;
    }
    if (String(data.energyClass || "") && String(data.energyClass) !== product.energyClass) {
      item.status = "skipped";
      item.reason = "nonempty_conflicting_energy_class";
      results.push(item);
      await persist();
      continue;
    }
    const labelUploadPath = product.labelUploadFile || product.labelFile;
    const labelUploadBytes = await readFile(labelUploadPath);
    const labelUploadExtension = extname(labelUploadPath).toLocaleLowerCase("en");
    const labelUploadMime = labelUploadExtension === ".jpg" || labelUploadExtension === ".jpeg" ? "image/jpeg" : "image/png";
    const labelUploadSignatureValid = labelUploadMime === "image/jpeg"
      ? labelUploadBytes.subarray(0, 2).equals(Buffer.from([255, 216]))
      : labelUploadBytes.subarray(0, 8).equals(Buffer.from([137, 80, 78, 71, 13, 10, 26, 10]));
    if (!labelUploadSignatureValid) throw new Error("label_upload_file_signature_mismatch");
    const assetStem = product.assetStem || product.manufacturerCode;
    const labelFilename = product.existingLabelAsset
      ? basename(product.existingLabelAsset.path)
      : `${assetStem}_etykieta_energetyczna${labelUploadExtension === ".jpeg" ? ".jpg" : labelUploadExtension}`;
    const sheetFilename = `${assetStem}_karta_informacyjna_produktu.pdf`;
    const labelPath = `${assetParentPath}/${labelFilename}`;
    const sheetPath = `${assetParentPath}/${sheetFilename}`;
    if (product.addLabel && !isEmptyRelation(data.energyClassLabels) && !relationMatchesFilename(data.energyClassLabels, labelFilename, productMediaPath)) {
      item.status = "skipped";
      item.reason = "nonempty_energy_label_requires_review";
      results.push(item);
      await persist();
      continue;
    }
    if (!product.addLabel && isEmptyRelation(data.energyClassLabels)) {
      item.status = "skipped";
      item.reason = "expected_existing_energy_label_missing";
      results.push(item);
      await persist();
      continue;
    }

    const labelAlreadyCurrent = !product.addLabel || relationMatchesFilename(data.energyClassLabels, labelFilename, productMediaPath);
    const sheetAlreadyCurrent = relationMatchesFilename(data.energyTechnicalCards, sheetFilename, productMediaPath);
    const classAlreadyCurrent = String(data.energyClass || "") === product.energyClass;
    if (labelAlreadyCurrent && sheetAlreadyCurrent && classAlreadyCurrent) {
      item.status = "already_current";
      results.push(item);
      await persist();
      continue;
    }
    if (!isEmptyRelation(data.energyTechnicalCards) && !sheetAlreadyCurrent) {
      item.status = "skipped";
      item.reason = "nonempty_energy_technical_card_requires_review";
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

    const beforeData = protectedDataSnapshot(data);
    const beforeGeneral = stableGeneralSnapshot(beforeObject.general);
    const beforeWorkflow = clone(beforeObject.workflowManagement);
    const beforeVersion = Number(beforeObject.general.versionCount);
    let labelAsset = null;
    if (product.addLabel && !labelAlreadyCurrent) {
      labelAsset = product.existingLabelAsset
        ? await verifyKnownAsset(objectId, product.existingLabelAsset, "image")
        : await findOwnedAsset(objectId, labelFilename, "image") || await uploadAsset({
        objectId,
        parentPath: assetParentPath,
        sourcePath: labelUploadPath,
        filename: labelFilename,
        assetType: "image",
        mimeType: labelUploadMime,
      });
    }
    let sheetAsset = null;
    if (!sheetAlreadyCurrent) {
      sheetAsset = await findOwnedAsset(objectId, sheetFilename, "document") || await uploadAsset({
        objectId,
        parentPath: assetParentPath,
        sourcePath: product.productInformationSheet,
        filename: sheetFilename,
        assetType: "document",
        mimeType: "application/pdf",
      });
    }

    const saveData = {};
    const dirtyFields = [];
    if (!classAlreadyCurrent) {
      saveData.energyClass = product.energyClass;
      dirtyFields.push("energyClass");
    }
    if (product.addLabel && !labelAlreadyCurrent) {
      saveData.energyClassLabels = relation(labelAsset, "image");
      dirtyFields.push("energyClassLabels");
    }
    if (!sheetAlreadyCurrent) {
      saveData.energyTechnicalCards = relation(sheetAsset, "document");
      dirtyFields.push("energyTechnicalCards");
    }
    if (dirtyFields.length === 0) throw new Error("no_dirty_fields_after_upload");
    currentGuard = { kind: "object", objectId, versionCount: beforeVersion, data: saveData, dirtyFields };
    const saveResponse = await frame.evaluate(async ({ id, dataValue, generalValue, dirtyFieldsValue }) => new Promise((resolveRequest) => {
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
    }), { id: objectId, dataValue: saveData, generalValue: saveGeneral(beforeObject.general), dirtyFieldsValue: dirtyFields });
    currentGuard = null;
    let savePayload = null;
    try { savePayload = JSON.parse(saveResponse.body); } catch {}
    const accepted = saveResponse.status === 200 && saveResponse.success === true && savePayload?.success === true;

    let afterObject = null;
    let applied = false;
    for (let attempt = 0; attempt < 6; attempt += 1) {
      afterObject = (await readObject(objectId)).object;
      const afterData = afterObject?.data || {};
      applied = String(afterData.energyClass || "") === product.energyClass
        && (!product.addLabel || relationMatchesFilename(afterData.energyClassLabels, labelFilename, productMediaPath))
        && relationMatchesFilename(afterData.energyTechnicalCards, sheetFilename, productMediaPath);
      if (applied) break;
      await page.waitForTimeout(800);
    }
    if (!applied) throw new Error(`object_save_failed_http_${saveResponse.status}`);

    const protectedDataUnchanged = same(protectedDataSnapshot(afterObject.data), beforeData);
    const generalUnchanged = same(stableGeneralSnapshot(afterObject.general), beforeGeneral);
    const workflowUnchanged = same(afterObject.workflowManagement, beforeWorkflow);
    const versionDelta = Number(afterObject.general.versionCount) - beforeVersion;
    if (!protectedDataUnchanged || !generalUnchanged || !workflowUnchanged || ![0, 1].includes(versionDelta)) {
      throw new Error("post_save_verification_failed");
    }
    item.status = accepted ? "saved" : "saved_with_validation";
    item.httpStatus = saveResponse.status;
    item.validationResponse = accepted ? "" : saveResponse.body;
    item.beforeVersionCount = beforeVersion;
    item.afterVersionCount = Number(afterObject.general.versionCount);
    item.dirtyFields = dirtyFields;
    item.energyClass = product.energyClass;
    item.energyClassLabel = String(afterObject.data.energyClassLabels?.[0]?.path || "");
    item.energyTechnicalCard = String(afterObject.data.energyTechnicalCards?.[0]?.path || "");
    item.protectedDataUnchanged = true;
    item.generalUnchanged = true;
    item.workflowUnchanged = true;
    cardsWritten += 1;
    results.push(item);
    await persist();
    console.log(JSON.stringify({ objectId, status: item.status, dirtyFields }));
  } catch (error) {
    currentGuard = null;
    item.status = "failed";
    item.reason = error.message;
    results.push(item);
    fatalError = `Karta ${objectId}: ${error.message}`;
    await persist();
    break;
  }
}

await persist();
await context.close();
console.log(`Zapisane karty: ${cardsWritten}; przesłane assety: ${uploadedAssets.length}; błą̨d krytyczny: ${fatalError || "brak"}.`);
if (fatalError) process.exitCode = 1;
