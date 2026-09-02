#!/usr/bin/env node

import { readFile, writeFile } from "node:fs/promises";
import { resolve } from "node:path";

import { chromium } from "../../radlight/node_modules/playwright/index.mjs";

function argumentValue(name, fallback = "") {
  const index = process.argv.indexOf(name);
  return index === -1 ? fallback : process.argv[index + 1] || fallback;
}

const queuePath = resolve(argumentValue("--queue", "exports/tim/remediation/noncore-withdrawal-queue-2026-09-02.json"));
const outputPath = resolve(argumentValue("--output", "/tmp/tim-withdraw-noncore-products.json"));
const start = Math.max(0, Number(argumentValue("--start", "0")) || 0);
const limit = Math.max(1, Number(argumentValue("--limit", "100")) || 100);
const maxWrites = Math.max(0, Number(argumentValue("--max-writes", "0")) || 0);
const apply = process.argv.includes("--apply");
if (apply && maxWrites < 1) throw new Error("Tryb --apply wymaga --max-writes > 0.");

const document = JSON.parse(await readFile(queuePath, "utf8"));
const queue = (document.items || []).slice(start, start + limit);
const results = [];
let writes = 0;
let fatalError = "";

const report = () => ({
  generatedAt: new Date().toISOString(),
  queuePath,
  apply,
  start,
  limit,
  writes,
  counts: {
    checked: results.length,
    ready: results.filter((item) => item.status === "verified_ready_dry_run").length,
    requested: results.filter((item) => item.status === "withdrawal_requested").length,
    alreadyRequested: results.filter((item) => item.status === "already_requested_or_withdrawn").length,
    serverRejected: results.filter((item) => item.status === "server_rejected_no_change").length,
    skipped: results.filter((item) => item.status === "skipped").length,
    failed: results.filter((item) => item.status === "failed").length,
  },
  fatalError,
  results,
});
const persist = () => writeFile(outputPath, `${JSON.stringify(report(), null, 2)}\n`, "utf8");

const browser = await chromium.connectOverCDP("http://127.0.0.1:9222");
const context = browser.contexts()[0];
const page = context.pages().find((candidate) => candidate.frames().some((frame) => frame.url() === "https://dostawca.tim.pl/pimcore/admin/"));
let frame = page?.frames().find((candidate) => candidate.url() === "https://dostawca.tim.pl/pimcore/admin/");
if (!frame) throw new Error("Brak aktywnej, zalogowanej ramki PIMCORE.");
if (apply && page.url().includes("/pimcore/admin/")) {
  await page.reload({ waitUntil: "domcontentloaded" });
  await page.waitForTimeout(2_000);
  frame = page.mainFrame();
}
const authenticated = await frame.evaluate(() => Number(window.pimcore?.currentuser?.id) > 0
  && window.pimcore?.currentuser?.active === true
  && Boolean(window.pimcore?.settings?.csrfToken));
if (!authenticated) throw new Error("Sesja PIMCORE nie jest aktywna.");

const rawObject = async (id) => frame.evaluate(async (objectId) => {
  const response = await fetch(`/pimcore/admin/object/get?id=${objectId}&_=${Date.now()}-${objectId}`, {
    credentials: "same-origin",
    cache: "no-store",
    headers: { Accept: "application/json", "Cache-Control": "no-cache" },
  });
  let object = null;
  try { object = await response.json(); } catch {}
  return { status: response.status, object };
}, id);

const workflowActions = async (id, classId) => frame.evaluate(async ({ objectId, objectClassId }) => {
  const body = new URLSearchParams({ ctype: "object", cid: String(objectId), classId: String(objectClassId) });
  const response = await fetch(`/pimcore/admin/workflow/actions/${objectId}`, {
    method: "POST",
    credentials: "same-origin",
    headers: {
      "X-Pimcore-CSRF-Token": window.pimcore.settings.csrfToken,
      "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    },
    body,
  });
  let payload = null;
  try { payload = await response.json(); } catch {}
  return { status: response.status, payload };
}, { objectId: id, objectClassId: classId });

function relationCount(value) {
  return Array.isArray(value) ? value.length : 0;
}

function stockValue(value) {
  return Array.isArray(value) ? Math.max(0, ...value.map((row) => Number(row?.stockTotalQuantityMz) || 0)) : 0;
}

function cleanStock(value) {
  return (Array.isArray(value) ? value : []).map((row) => ({
    id: row?.id,
    stockFreeQuantity: row?.stockFreeQuantity,
    stockTotalQuantity: row?.stockTotalQuantity,
    stockTotal55WDQuantity: row?.stockTotal55WDQuantity,
    stockTotalQuantityMz: row?.stockTotalQuantityMz,
  }));
}

function critical(object) {
  const data = object?.data || {};
  return {
    general: {
      id: object?.general?.id,
      key: object?.general?.key,
      className: object?.general?.className,
      published: object?.general?.published,
    },
    data: {
      ean: data.ean,
      manufacturerIndex: data.manufacturerIndex,
      timIndex: data.timIndex,
      timName: data.timName,
      manufacturer: data.manufacturer,
      listPrice: data.listPrice,
      netCatalogPrice: data.netCatalogPrice,
      stockLevel: cleanStock(data.stockLevel),
      productDescriptions: data.productDescriptions,
      mainPhoto: data.mainPhoto,
      dataSheet: data.dataSheet,
      certifications: data.certifications,
      instructions: data.instructions,
      energyClass: data.energyClass,
      energyClassLabels: data.energyClassLabels,
      energyTechnicalCards: data.energyTechnicalCards,
    },
  };
}

function same(left, right) {
  return JSON.stringify(left) === JSON.stringify(right);
}

function transitions(actions) {
  return (actions?.payload?.workflowManagement?.workflows || [])
    .flatMap((workflow) => (workflow.allowedTransitions || []).map((transition) => ({
      workflow: workflow.name,
      name: transition.name,
      label: String(transition.label || "").trim(),
    })));
}

for (let offset = 0; offset < queue.length; offset += 1) {
  if (apply && writes >= maxWrites) break;
  const expected = queue[offset];
  const result = {
    index: start + offset,
    pimcoreId: Number(expected.pimcoreId),
    ean: expected.ean,
    manufacturerCode: expected.manufacturerCode,
    timName: expected.timName,
    brand: expected.brand,
    rule: expected.rule,
    status: "failed",
  };
  try {
    const beforeRead = await rawObject(result.pimcoreId);
    const before = beforeRead.object;
    const data = before?.data || {};
    result.beforeState = String(data.state?.value || data.state || "");
    result.beforeStatus = String(data.status?.value || data.status || "");
    result.liveStock = stockValue(data.stockLevel);
    result.dataSheetCount = relationCount(data.dataSheet);
    result.certificationsCount = relationCount(data.certifications);
    const exactIdentity = beforeRead.status === 200
      && Number(before?.general?.id) === result.pimcoreId
      && before?.general?.published === true
      && before?.general?.locked !== true
      && String(data.ean || "") === String(expected.ean)
      && String(data.manufacturerIndex || "") === String(expected.manufacturerCode)
      && String(data.timName || "") === String(expected.timName);
    const brandMatches = expected.brand === "Kaja"
      ? /\bKAJA\b/iu.test(String(data.timName || ""))
      : expected.brand === "GTV"
        ? /\bGTV\b/iu.test(String(data.timName || ""))
        : expected.brand === "Cree Lamp"
          ? /^CREE LAMP\s*-/iu.test(String(data.timName || ""))
          : expected.brand === "Britop"
            ? /^BRITOP\s*-/iu.test(String(data.timName || ""))
            : expected.brand === "Karlik LOGO"
              ? /^LOGO\b/iu.test(String(data.timName || "")) && /^LWP-/iu.test(String(data.manufacturerIndex || ""))
              : false;
    const ruleMatches = expected.rule === "remove_regardless"
      ? expected.brand === "Kaja"
      : expected.rule === "low_stock_no_documents"
        ? result.liveStock < 10 && result.dataSheetCount === 0 && result.certificationsCount === 0
        : false;
    if (!exactIdentity || !brandMatches || !ruleMatches) {
      result.status = "skipped";
      result.reason = "live_identity_brand_or_policy_mismatch";
      results.push(result);
      await persist();
      continue;
    }
    const beforeActions = await workflowActions(result.pimcoreId, before.general?.classId);
    const available = transitions(beforeActions);
    result.availableTransitions = available;
    const withdrawal = available.find((item) => item.workflow === "state" && item.name === "application_for_withdrawal");
    if (!withdrawal) {
      result.status = "already_requested_or_withdrawn";
      results.push(result);
      await persist();
      continue;
    }
    if (!apply) {
      result.status = "verified_ready_dry_run";
      results.push(result);
      await persist();
      continue;
    }
    const beforeCritical = critical(before);
    const beforePath = String(before?.general?.fullpath || "");
    const response = await frame.evaluate(async ({ objectId }) => {
      const body = new URLSearchParams({
        ctype: "object",
        cid: String(objectId),
        workflowName: "state",
        transition: "application_for_withdrawal",
      });
      const reply = await fetch("/pimcore/admin/workflow/submit-workflow-transition", {
        method: "POST",
        credentials: "same-origin",
        headers: {
          "X-Pimcore-CSRF-Token": window.pimcore.settings.csrfToken,
          "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        },
        body,
      });
      return { status: reply.status, ok: reply.ok, body: String(await reply.text()).slice(0, 30_000) };
    }, { objectId: result.pimcoreId });
    result.transitionResponse = response;
    let responsePayload = null;
    try { responsePayload = JSON.parse(response.body); } catch {}
    if (!response.ok || response.status !== 200 || responsePayload?.success !== true) {
      const rejectedRead = await rawObject(result.pimcoreId);
      if (!same(critical(rejectedRead.object), beforeCritical)) {
        throw new Error(`withdrawal_rejected_but_product_data_changed:http_${response.status}`);
      }
      result.status = "server_rejected_no_change";
      result.reason = String(responsePayload?.message || `http_${response.status}`);
      result.protectedProductDataUnchanged = true;
      results.push(result);
      await persist();
      continue;
    }
    await page.waitForTimeout(1_000);
    const afterRead = await rawObject(result.pimcoreId);
    const after = afterRead.object;
    if (!same(critical(after), beforeCritical)) throw new Error("protected_product_data_changed_after_withdrawal_request");
    const afterPath = String(after?.general?.fullpath || "");
    const expectedArchivePath = beforePath.replace("/Produkty/Katalog główny/", "/Produkty/Archiwum/");
    if (beforePath === expectedArchivePath || afterPath !== expectedArchivePath) {
      throw new Error("unexpected_archive_path_after_withdrawal_request");
    }
    const afterActions = await workflowActions(result.pimcoreId, after.general?.classId);
    const afterAvailable = transitions(afterActions);
    if (afterAvailable.some((item) => item.workflow === "state" && item.name === "application_for_withdrawal")) {
      throw new Error("withdrawal_transition_still_available_after_request");
    }
    result.afterState = String(after?.data?.state?.value || after?.data?.state || "");
    result.afterStatus = String(after?.data?.status?.value || after?.data?.status || "");
    result.beforePath = beforePath;
    result.afterPath = afterPath;
    result.afterProductAvailableForSale = String(after?.data?.productAvailableForSale?.value || after?.data?.productAvailableForSale || "");
    if (result.afterState !== "discontinued" || result.afterStatus !== "discontinued"
      || result.afterProductAvailableForSale !== "nie") {
      throw new Error("unexpected_state_after_withdrawal_request");
    }
    result.afterAvailableTransitions = afterAvailable;
    result.protectedProductDataUnchanged = true;
    result.status = "withdrawal_requested";
    writes += 1;
    results.push(result);
    await persist();
    console.log(JSON.stringify({ id: result.pimcoreId, model: result.manufacturerCode, status: result.status, state: result.afterState }));
  } catch (error) {
    result.status = "failed";
    result.reason = error.message;
    results.push(result);
    fatalError = `${result.manufacturerCode}: ${error.message}`;
    await persist();
    break;
  }
}

await persist();
console.log(JSON.stringify({ outputPath, counts: report().counts, fatalError }, null, 2));
process.exit(fatalError ? 1 : 0);
