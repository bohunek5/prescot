import { readFile, writeFile } from "node:fs/promises";
import { resolve } from "node:path";
import { chromium } from "../../radlight/node_modules/playwright/index.mjs";

function argumentValue(name, fallback = "") {
  const index = process.argv.indexOf(name);
  return index === -1 ? fallback : process.argv[index + 1] || fallback;
}

function canonicalDescription(html) {
  return String(html || "").trim().replace(/^<section>/i, "").replace(/<\/section>$/i, "");
}

function comparableFields(fields) {
  const copy = JSON.parse(JSON.stringify(fields || {}));
  for (const stock of copy.stockLevel || []) {
    delete stock.modificationDate;
    delete stock.updatedAt;
  }
  return copy;
}

const profileDir = argumentValue("--profile-dir");
const pilotJsonPath = resolve(argumentValue("--pilot-json", "exports/tim/pilots/active-description-pilot.json"));
const pilotStage = argumentValue("--pilot-stage", "pilot500");
const outputPath = resolve(argumentValue("--output", "/tmp/tim-pimcore-description-batch.json"));
const screenshotPath = resolve(argumentValue("--screenshot", "/tmp/tim-pimcore-description-batch.png"));
const startIndex = Math.max(0, Number(argumentValue("--start-index", "0")) || 0);
const limit = Math.max(1, Number(argumentValue("--limit", "500")) || 500);
const maxWrites = Math.max(0, Number(argumentValue("--max-writes", "0")) || 0);
const applySave = process.argv.includes("--apply");
if (!profileDir) throw new Error("Podaj --profile-dir z izolowaną kopią profilu Chrome.");
if (applySave && maxWrites < 1) throw new Error("Tryb --apply wymaga dodatniego --max-writes.");

const pilotDocument = JSON.parse(await readFile(pilotJsonPath, "utf8"));
const fullStage = pilotDocument?.stages?.[pilotStage];
if (!Array.isArray(fullStage)) throw new Error(`Nie ma etapu ${pilotStage}.`);
const queue = fullStage.slice(startIndex, startIndex + limit);
const results = [];
const allowedWrites = [];
const allowedUnlocks = [];
const blockedWrites = [];
let currentGuard = null;
let writes = 0;
let fatalError = "";

const report = () => ({
  generatedAt: new Date().toISOString(),
  pilotStage,
  startIndex,
  limit,
  maxWrites,
  applySave,
  queueLength: queue.length,
  writes,
  counts: {
    checked: results.length,
    saved: results.filter((item) => item.status === "saved").length,
    alreadyCurrent: results.filter((item) => item.status === "already_current").length,
    locked: results.filter((item) => item.status === "locked").length,
    skipped: results.filter((item) => item.status === "skipped").length,
    failed: results.filter((item) => item.status === "failed").length,
  },
  fatalError,
  results,
  allowedWrites,
  allowedUnlocks,
  blockedWrites,
  screenshotPath,
});

const persist = async () => writeFile(outputPath, `${JSON.stringify(report(), null, 2)}\n`, "utf8");

const context = await chromium.launchPersistentContext(profileDir, {
  headless: true,
  executablePath: "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
  args: ["--profile-directory=Default"],
  viewport: { width: 1800, height: 1200 },
  serviceWorkers: "block",
});

await context.route("**/*", async (route) => {
  const request = route.request();
  const method = request.method().toUpperCase();
  const url = request.url();
  if (["GET", "HEAD", "OPTIONS"].includes(method)) return route.continue();
  if (method === "POST" && currentGuard && url === `https://dostawca.tim.pl/admin/workflow/actions/${currentGuard.objectId}`) {
    return route.continue();
  }
  if (method === "PUT" && currentGuard?.allowUnlock === true && url === "https://dostawca.tim.pl/pimcore/admin/element/unlock-element") {
    const params = new URLSearchParams(request.postData() || "");
    const valid = params.get("id") === String(currentGuard.objectId)
      && params.get("type") === "object"
      && [...params.keys()].sort().join(",") === "id,type";
    if (valid) {
      allowedUnlocks.push({ objectId: currentGuard.objectId, method, url });
      return route.continue();
    }
    blockedWrites.push({ objectId: currentGuard.objectId, method, url, reason: "unlock_guard_failed", postData: String(request.postData() || "").slice(0, 20_000) });
    return route.abort("blockedbyclient");
  }
  if (applySave && method === "PUT" && currentGuard && url === "https://dostawca.tim.pl/pimcore/admin/object/save?task=undefined") {
    try {
      const params = new URLSearchParams(request.postData() || "");
      const data = JSON.parse(params.get("data") || "null");
      const general = JSON.parse(params.get("general") || "null");
      const dirtyFields = JSON.parse(params.get("dirtyFields") || "null");
      const descriptionData = data?.productDescriptions?.data;
      const valid = params.get("id") === String(currentGuard.objectId)
        && Number(general?.id) === currentGuard.objectId
        && JSON.stringify(Object.keys(data || {})) === JSON.stringify(["productDescriptions"])
        && data?.productDescriptions?.type === "productDescriptions"
        && JSON.stringify(Object.keys(descriptionData || {})) === JSON.stringify(["longMarketingDescription"])
        && descriptionData?.longMarketingDescription === currentGuard.expectedHtml
        && JSON.stringify(dirtyFields) === JSON.stringify(["productDescriptions"]);
      if (!valid) throw new Error("save_guard_failed");
      allowedWrites.push({
        objectId: currentGuard.objectId,
        method,
        url,
        dirtyFields,
        descriptionLength: currentGuard.expectedHtml.length,
      });
      return route.continue();
    } catch (error) {
      blockedWrites.push({ objectId: currentGuard?.objectId || 0, method, url, reason: error.message, postData: String(request.postData() || "").slice(0, 20_000) });
      return route.abort("blockedbyclient");
    }
  }
  if (!["POST"].includes(method) || !/cdn-cgi\/rum|liveupdate\.pimcore\.org\/update-check/.test(url)) {
    blockedWrites.push({ objectId: currentGuard?.objectId || 0, method, url, reason: "not_allowlisted", postData: String(request.postData() || "").slice(0, 20_000) });
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
await page.waitForTimeout(5_000);

const readSnapshot = async (objectId) => frame.evaluate(async (id) => {
  const response = await fetch(`/pimcore/admin/object/get?id=${id}`, { credentials: "same-origin" });
  let object = null;
  try { object = await response.json(); } catch {}
  const data = object?.data || {};
  const pick = (value) => value == null ? value : JSON.parse(JSON.stringify(value));
  return {
    httpStatus: response.status,
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
}, objectId);

const closeObject = async (objectId) => frame.evaluate((id) => {
  const key = `object_${id}`;
  const object = window.pimcore?.globalmanager?.get?.(key);
  try { object?.tab?.close?.(); } catch {}
}, objectId).catch(() => {});

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
    const before = await readSnapshot(objectId);
    item.beforeVersionCount = before.general.versionCount;
    item.timIndex = before.fields.timIndex;
    const identityMatches = before.httpStatus === 200
      && Number(before.general.id) === objectId
      && String(before.fields.ean || "") === String(product.ean)
      && String(before.fields.manufacturerIndex || "") === String(product.manufacturerCode)
      && String(before.fields.state || "") === "active"
      && before.general.published === true;
    if (!identityMatches) {
      item.status = "skipped";
      item.reason = "live_identity_or_state_mismatch";
      results.push(item);
      await persist();
      continue;
    }
    const expectedCanonical = canonicalDescription(product.descriptionHtml);
    if (before.description === expectedCanonical) {
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

    currentGuard = { objectId, expectedHtml: expectedCanonical, allowUnlock: false };
    await frame.evaluate((id) => window.pimcore.helpers.openObject(id, "object"), objectId);
    await frame.waitForFunction((id) => Boolean(window.pimcore?.globalmanager?.get?.(`object_${id}`)), objectId, { timeout: 20_000 });
    await page.waitForTimeout(1_500);
    const lockDialog = frame.locator(".x-message-box").filter({ hasText: /Inna osoba używa tego elementu/i }).last();
    if (await lockDialog.isVisible().catch(() => false)) {
      const noButton = lockDialog.getByText("Nie", { exact: true }).last();
      if (await noButton.isVisible().catch(() => false)) await noButton.click();
      item.status = "locked";
      item.reason = "foreign_session_dialog";
      results.push(item);
      await closeObject(objectId);
      await persist();
      continue;
    }
    currentGuard.allowUnlock = true;

    const mediaTab = frame.locator(`#object_${objectId}`).getByText("Multimedia/Załączniki", { exact: true }).last();
    await mediaTab.click({ timeout: 15_000 });
    await frame.waitForFunction((id) => {
      const object = window.pimcore?.globalmanager?.get?.(`object_${id}`);
      const field = object?.edit?.dataFields?.productDescriptions?.currentElements?.productDescriptions?.fields?.longMarketingDescription;
      return Boolean(field?.editableDivId && document.getElementById(field.editableDivId)?.querySelector?.(".ql-editor[contenteditable='true']"));
    }, objectId, { timeout: 20_000 });
    const editResult = await frame.evaluate(({ id, html }) => {
      const object = window.pimcore?.globalmanager?.get?.(`object_${id}`);
      const field = object?.edit?.dataFields?.productDescriptions?.currentElements?.productDescriptions?.fields?.longMarketingDescription;
      const container = field?.editableDivId ? document.getElementById(field.editableDivId) : null;
      const editor = container?.querySelector(".ql-editor[contenteditable='true']") || null;
      if (!editor) throw new Error(`Nie znaleziono edytora opisu dla ${id}.`);
      const quill = window.Quill?.find?.(container) || container?.__quill || window.Quill?.find?.(editor) || null;
      const clipboard = quill?.clipboard || quill?.getModule?.("clipboard") || null;
      if (!clipboard?.dangerouslyPasteHTML) throw new Error(`Brak edytora Quill dla ${id}.`);
      clipboard.dangerouslyPasteHTML(html, "user");
      const semanticHtml = String(quill.getSemanticHTML?.() || editor.innerHTML);
      document.dispatchEvent(new CustomEvent(window.pimcore.events.changeWysiwyg, {
        detail: { e: { target: container }, data: semanticHtml },
      }));
      return { semanticHtml, textLength: String(quill.getText?.() || "").trim().length };
    }, { id: objectId, html: product.descriptionHtml });
    if (editResult.semanticHtml !== expectedCanonical || editResult.textLength < 100) {
      throw new Error("quill_output_mismatch");
    }

    const scopedSaveButtonId = await frame.evaluate((id) => {
      const object = window.pimcore?.globalmanager?.get?.(`object_${id}`);
      const button = object?.toolbarButtons?.save;
      return button?.text === "Zapisz" && !button.hidden ? button.id : "";
    }, objectId);
    if (!scopedSaveButtonId) throw new Error("save_button_missing");
    const saveResponsePromise = page.waitForResponse((response) => response.request().method() === "PUT"
      && response.url() === "https://dostawca.tim.pl/pimcore/admin/object/save?task=undefined", { timeout: 30_000 });
    await frame.locator(`#${scopedSaveButtonId}`).click();
    const saveResponse = await saveResponsePromise;
    const saveBody = await saveResponse.text().catch(() => "");
    let savePayload = null;
    try { savePayload = JSON.parse(saveBody); } catch {}
    if (!saveResponse.ok() || savePayload?.success !== true) throw new Error(`save_failed_http_${saveResponse.status()}`);
    await page.waitForTimeout(600);

    const after = await readSnapshot(objectId);
    const protectedFieldsUnchanged = JSON.stringify(comparableFields(after.fields)) === JSON.stringify(comparableFields(before.fields));
    const identityUnchanged = ["id", "key", "className", "fullpath", "published"]
      .every((key) => JSON.stringify(after.general[key]) === JSON.stringify(before.general[key]));
    const workflowUnchanged = JSON.stringify(after.workflowManagement) === JSON.stringify(before.workflowManagement);
    if (after.description !== expectedCanonical || !protectedFieldsUnchanged || !identityUnchanged || !workflowUnchanged) {
      throw new Error("post_save_verification_failed");
    }
    item.status = "saved";
    item.httpStatus = saveResponse.status();
    item.afterVersionCount = after.general.versionCount;
    item.descriptionLength = expectedCanonical.length;
    item.protectedFieldsUnchanged = protectedFieldsUnchanged;
    item.identityUnchanged = identityUnchanged;
    item.workflowUnchanged = workflowUnchanged;
    writes += 1;
    results.push(item);
    await closeObject(objectId);
    await frame.waitForFunction((id) => !window.pimcore?.globalmanager?.exists?.(`object_${id}`), objectId, { timeout: 10_000 }).catch(() => {});
    await page.waitForTimeout(700);
    currentGuard = null;
    await persist();
    console.log(JSON.stringify({ index, objectId, status: item.status, versions: [item.beforeVersionCount, item.afterVersionCount] }));
  } catch (error) {
    item.status = "failed";
    item.reason = error.message;
    results.push(item);
    fatalError = `Karta ${objectId}: ${error.message}`;
    await closeObject(objectId);
    currentGuard = null;
    await persist();
    break;
  }
}

await page.screenshot({ path: screenshotPath, fullPage: true }).catch(() => {});
await persist();
await context.close();
console.log(`Zapisane: ${writes}; sprawdzone: ${results.length}; błąd krytyczny: ${fatalError || "brak"}.`);
console.log(`Raport: ${outputPath}`);
if (fatalError) process.exitCode = 1;
