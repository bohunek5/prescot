import { readFile, writeFile } from "node:fs/promises";
import { resolve } from "node:path";
import { chromium } from "../../radlight/node_modules/playwright/index.mjs";

function argumentValue(name, fallback = "") {
  const index = process.argv.indexOf(name);
  return index === -1 ? fallback : process.argv[index + 1] || fallback;
}

function canonicalDescription(html) {
  return String(html || "").trim().replace(/^<section>\s*/i, "").replace(/\s*<\/section>$/i, "").trim();
}

function normalizedStoredDescription(html) {
  return String(html || "")
    .replace(/&quot;|&#0*34;|&#x0*22;/gi, '"')
    .replace(/&apos;|&#0*39;|&#x0*27;/gi, "'")
    .trim();
}

function descriptionsEqual(left, right) {
  return normalizedStoredDescription(left) === normalizedStoredDescription(right);
}

function comparableFields(fields) {
  const copy = JSON.parse(JSON.stringify(fields || {}));
  for (const stock of copy.stockLevel || []) {
    delete stock.modificationDate;
    delete stock.updatedAt;
  }
  return copy;
}

function snapshot(object) {
  const data = object?.data || {};
  const pick = (value) => value == null ? value : JSON.parse(JSON.stringify(value));
  return {
    general: {
      id: object?.general?.id,
      key: object?.general?.key,
      className: object?.general?.className,
      fullpath: object?.general?.fullpath,
      published: object?.general?.published,
      locked: object?.general?.locked,
      versionCount: object?.general?.versionCount,
    },
    fields: {
      timIndex: pick(data.timIndex),
      timName: pick(data.timName),
      supplier: pick(data.supplier),
      manufacturer: pick(data.manufacturer),
      manufacturerIndex: pick(data.manufacturerIndex),
      ean: pick(data.ean),
      listPrice: pick(data.listPrice),
      netCatalogPrice: pick(data.netCatalogPrice),
      stockLevel: pick(data.stockLevel),
      measureUnit: pick(data.measureUnit),
      availability: pick(data.availability),
      status: pick(data.status),
      state: pick(data.state),
      sale: pick(data.sale),
      productAvailableForSale: pick(data.productAvailableForSale),
      mainPhoto: pick(data.mainPhoto),
      assignedCategory24: pick(data.assignedCategory24),
    },
    description: String(data.productDescriptions?.data?.longMarketingDescription || ""),
    workflowManagement: pick(object?.workflowManagement),
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
const pilotJsonPath = resolve(argumentValue("--pilot-json", "exports/tim/pilots/active-description-pilot.json"));
const pilotStage = argumentValue("--pilot-stage", "pilot500");
const outputPath = resolve(argumentValue("--output", "/tmp/tim-pimcore-description-api-batch.json"));
const startIndex = Math.max(0, Number(argumentValue("--start-index", "0")) || 0);
const limit = Math.max(1, Number(argumentValue("--limit", "500")) || 500);
const maxWrites = Math.max(0, Number(argumentValue("--max-writes", "0")) || 0);
const allowedStates = argumentValue("--allowed-states", "active").split(",").map((value) => value.trim()).filter(Boolean);
const applySave = process.argv.includes("--apply");
if (!profileDir) throw new Error("Podaj --profile-dir z izolowaną kopią profilu Chrome.");
if (applySave && maxWrites < 1) throw new Error("Tryb --apply wymaga dodatniego --max-writes.");

const pilotDocument = JSON.parse(await readFile(pilotJsonPath, "utf8"));
const fullStage = pilotDocument?.stages?.[pilotStage];
if (!Array.isArray(fullStage)) throw new Error(`Nie ma etapu ${pilotStage}.`);
const queue = fullStage.slice(startIndex, startIndex + limit);
const results = [];
const allowedWrites = [];
const blockedWrites = [];
let currentGuard = null;
let writes = 0;
let fatalError = "";

const report = () => ({
  generatedAt: new Date().toISOString(),
  mode: "pimcore_ext_ajax_exact_field_save",
  pilotStage,
  startIndex,
  limit,
  maxWrites,
  applySave,
  allowedStates,
  queueLength: queue.length,
  writes,
  counts: {
    checked: results.length,
    saved: results.filter((item) => item.status === "saved" || item.status === "saved_with_validation").length,
    savedWithValidation: results.filter((item) => item.status === "saved_with_validation").length,
    alreadyCurrent: results.filter((item) => item.status === "already_current").length,
    locked: results.filter((item) => item.status === "locked").length,
    skipped: results.filter((item) => item.status === "skipped").length,
    failed: results.filter((item) => item.status === "failed").length,
  },
  fatalError,
  results,
  allowedWrites,
  blockedWrites,
});
const persist = async () => writeFile(outputPath, `${JSON.stringify(report(), null, 2)}\n`, "utf8");

console.log(`Uruchamianie sesji PIMCORE dla ${queue.length} pozycji od indeksu ${startIndex}...`);
const context = await chromium.launchPersistentContext(profileDir, {
  headless: true,
  executablePath: "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
  args: ["--profile-directory=Default"],
  viewport: { width: 1600, height: 1100 },
  serviceWorkers: "block",
  timeout: 45_000,
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
      const descriptionData = data?.productDescriptions?.data;
      const valid = [...params.keys()].sort().join(",") === "data,dirtyFields,general,id"
        && params.get("id") === String(currentGuard.objectId)
        && Number(general?.id) === currentGuard.objectId
        && Number(general?.versionCount) === currentGuard.versionCount
        && JSON.stringify(Object.keys(data || {})) === JSON.stringify(["productDescriptions"])
        && data?.productDescriptions?.type === "productDescriptions"
        && JSON.stringify(Object.keys(descriptionData || {})) === JSON.stringify(["longMarketingDescription"])
        && descriptionData?.longMarketingDescription === currentGuard.expectedHtml
        && JSON.stringify(dirtyFields) === JSON.stringify(["productDescriptions"]);
      if (!valid) throw new Error("save_guard_failed");
      allowedWrites.push({
        objectId: currentGuard.objectId,
        versionCount: currentGuard.versionCount,
        method,
        url,
        dirtyFields,
        descriptionLength: currentGuard.expectedHtml.length,
      });
      return route.continue();
    } catch (error) {
      blockedWrites.push({ objectId: currentGuard?.objectId || 0, method, url, reason: error.message });
      return route.abort("blockedbyclient");
    }
  }
  if (!["POST"].includes(method) || !/cdn-cgi\/rum|liveupdate\.pimcore\.org\/update-check/.test(url)) {
    blockedWrites.push({ objectId: currentGuard?.objectId || 0, method, url, reason: "not_allowlisted" });
  }
  return route.abort("blockedbyclient");
});

const page = context.pages()[0] || await context.newPage();
console.log("Otwieranie PIMCORE...");
await page.goto("https://dostawca.tim.pl/pimcore/", { waitUntil: "domcontentloaded", timeout: 45_000 });
console.log("PIMCORE otwarty; sprawdzanie sesji...");
let frame = page.frames().find((item) => item.url().includes("/pimcore/admin/"));
for (let attempt = 0; !frame && attempt < 15; attempt += 1) {
  await page.waitForTimeout(1_000);
  frame = page.frames().find((item) => item.url().includes("/pimcore/admin/"));
}
if (!frame) throw new Error("Nie znaleziono ramki PIMCORE.");
await page.waitForTimeout(4_000);

let readSequence = 0;
const readObject = async (objectId) => {
  let lastError = "read_timeout";
  for (let attempt = 1; attempt <= 3; attempt += 1) {
    try {
      readSequence += 1;
      const response = await context.request.get(`https://dostawca.tim.pl/pimcore/admin/object/get?id=${objectId}&_=${Date.now()}-${readSequence}`, {
        timeout: 30_000,
        headers: { "Cache-Control": "no-cache", Pragma: "no-cache" },
      });
      let object = null;
      try { object = await response.json(); } catch {}
      return { status: response.status(), object, error: null };
    } catch (error) {
      lastError = String(error?.name || error?.message || error);
    }
    if (attempt < 3) await page.waitForTimeout(3_000);
  }
  throw new Error(`read_failed_after_retries:${lastError}`);
};

for (let offset = 0; offset < queue.length; offset += 1) {
  if (applySave && writes >= maxWrites) break;
  const product = queue[offset];
  const index = startIndex + offset;
  const objectId = Number(product.pimcoreId);
  const item = {
    index,
    objectId,
    ean: product.ean,
    manufacturerCode: product.manufacturerCode,
    name: product.name,
    status: "failed",
  };
  currentGuard = null;
  try {
    if (!objectId || !product.descriptionHtml || !product.ean || !product.manufacturerCode) {
      item.status = "skipped";
      item.reason = "incomplete_queue_record";
      results.push(item);
      await persist();
      continue;
    }
    const beforeRead = await readObject(objectId);
    const beforeObject = beforeRead.object;
    const before = snapshot(beforeObject);
    item.beforeVersionCount = before.general.versionCount;
    item.timIndex = before.fields.timIndex;
    const identityMatches = beforeRead.status === 200
      && Number(before.general.id) === objectId
      && String(before.fields.ean || "") === String(product.ean)
      && String(before.fields.manufacturerIndex || "") === String(product.manufacturerCode)
      && allowedStates.includes(String(before.fields.state || ""))
      && before.general.published === true;
    if (!identityMatches) {
      item.status = "skipped";
      item.reason = "live_identity_or_state_mismatch";
      results.push(item);
      await persist();
      continue;
    }
    const expectedHtml = canonicalDescription(product.descriptionHtml);
    if (descriptionsEqual(before.description, expectedHtml)) {
      item.status = "already_current";
      results.push(item);
      await persist();
      continue;
    }
    if (before.general.locked) {
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

    const general = saveGeneral(beforeObject.general);
    const data = {
      productDescriptions: {
        type: "productDescriptions",
        data: { longMarketingDescription: expectedHtml },
      },
    };
    currentGuard = { objectId, expectedHtml, versionCount: Number(before.general.versionCount) };
    const saveResponse = await frame.evaluate(async ({ id, dataPayload, generalPayload }) => new Promise((resolveRequest) => {
      window.Ext.Ajax.request({
        url: "/pimcore/admin/object/save?task=undefined",
        method: "PUT",
        timeout: 45_000,
        headers: { "X-Pimcore-CSRF-Token": window.pimcore.settings.csrfToken },
        params: {
          id,
          data: JSON.stringify(dataPayload),
          general: JSON.stringify(generalPayload),
          dirtyFields: JSON.stringify(["productDescriptions"]),
        },
        callback: (_options, success, response) => resolveRequest({
          success,
          status: response?.status || 0,
          body: String(response?.responseText || "").slice(0, 100_000),
        }),
      });
    }), { id: objectId, dataPayload: data, generalPayload: general });
    item.saveResponseStatus = saveResponse.status;
    item.saveResponseBody = saveResponse.body;
    let savePayload = null;
    try { savePayload = JSON.parse(saveResponse.body); } catch {}
    const responseAccepted = saveResponse.status === 200 && saveResponse.success === true && savePayload?.success === true;
    let afterRead = null;
    let after = null;
    let protectedFieldsUnchanged = false;
    let identityUnchanged = false;
    let workflowUnchanged = false;
    let versionDelta = Number.NaN;
    let descriptionApplied = false;
    let verificationAttempts = 0;
    for (let attempt = 1; attempt <= 6; attempt += 1) {
      verificationAttempts = attempt;
      afterRead = await readObject(objectId);
      after = snapshot(afterRead.object);
      protectedFieldsUnchanged = JSON.stringify(comparableFields(after.fields)) === JSON.stringify(comparableFields(before.fields));
      identityUnchanged = ["id", "key", "className", "fullpath", "published"]
        .every((key) => JSON.stringify(after.general[key]) === JSON.stringify(before.general[key]));
      workflowUnchanged = JSON.stringify(after.workflowManagement) === JSON.stringify(before.workflowManagement);
      versionDelta = Number(after.general.versionCount) - Number(before.general.versionCount);
      descriptionApplied = afterRead.status === 200 && descriptionsEqual(after.description, expectedHtml);
      const versionIsExpected = responseAccepted ? versionDelta === 1 : [0, 1].includes(versionDelta);
      if (descriptionApplied && protectedFieldsUnchanged && identityUnchanged && workflowUnchanged && versionIsExpected) break;
      if (attempt < 6) await page.waitForTimeout(attempt * 700);
    }
    item.verificationAttempts = verificationAttempts;
    if (!descriptionApplied) {
      if (saveResponse.status === 422) {
        item.status = "skipped";
        item.reason = "server_validation_422_no_description_change";
        results.push(item);
        currentGuard = null;
        await persist();
        continue;
      }
      throw new Error(`save_failed_http_${saveResponse.status}`);
    }
    if (!protectedFieldsUnchanged || !identityUnchanged || !workflowUnchanged
      || (responseAccepted ? versionDelta !== 1 : ![0, 1].includes(versionDelta))) {
      throw new Error("post_save_verification_failed");
    }
    item.status = responseAccepted ? "saved" : "saved_with_validation";
    if (!responseAccepted) item.validationResponse = saveResponse.body;
    item.httpStatus = saveResponse.status;
    delete item.saveResponseStatus;
    delete item.saveResponseBody;
    item.afterVersionCount = after.general.versionCount;
    item.descriptionLength = expectedHtml.length;
    item.protectedFieldsUnchanged = protectedFieldsUnchanged;
    item.identityUnchanged = identityUnchanged;
    item.workflowUnchanged = workflowUnchanged;
    if (verificationAttempts === 1) delete item.verificationAttempts;
    writes += 1;
    results.push(item);
    currentGuard = null;
    await persist();
    console.log(JSON.stringify({ index, objectId, status: item.status, versions: [item.beforeVersionCount, item.afterVersionCount] }));
    await page.waitForTimeout(150);
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
console.log(`Zapisane: ${writes}; sprawdzone: ${results.length}; błąd krytyczny: ${fatalError || "brak"}.`);
console.log(`Raport: ${outputPath}`);
if (fatalError) process.exitCode = 1;
