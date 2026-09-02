import { readFile, writeFile } from "node:fs/promises";
import { resolve } from "node:path";
import { chromium } from "../../radlight/node_modules/playwright/index.mjs";

const CDP_URL = "http://127.0.0.1:9222";
const apply = process.argv.includes("--apply");
const pick = (name, fallback = "") => {
  const index = process.argv.indexOf(name);
  return index < 0 ? fallback : process.argv[index + 1] || fallback;
};
const start = Math.max(0, Number(pick("--start", "0")) || 0);
const limit = Math.max(1, Number(pick("--limit", "1")) || 1);
const maxCards = Math.max(0, Number(pick("--max-cards", "0")) || 0);
const queuePath = pick("--queue", "");
if (apply && maxCards < 1) throw new Error("Tryb --apply wymaga dodatniego --max-cards.");

const defaultProducts = [
  { id: 15907539, ean: "5905475368073", model: "PR-MAD36-1224", price: 23.5 },
  { id: 15907542, ean: "5905475368080", model: "PR-MAD60-1224", price: 30 },
  { id: 15907545, ean: "5905475368097", model: "PR-MAD100-1224", price: 39 },
  { id: 15907551, ean: "5905475368103", model: "PR-MAD150-1224", price: 44 },
  { id: 15907554, ean: "5905475368110", model: "PR-MAD200-1224", price: 50 },
];
const queueDocument = queuePath ? JSON.parse(await readFile(resolve(queuePath), "utf8")) : null;
const sourceProducts = queuePath ? queueDocument?.items : defaultProducts;
if (!Array.isArray(sourceProducts)) throw new Error("Brak tablicy items w kolejce aktywacji.");
const products = sourceProducts.slice(start, start + limit);

const output = resolve(pick("--output", "exports/tim/remediation/pr-mad-submit-for-acceptance.json"));
const report = { generatedAt: new Date().toISOString(), apply, queuePath: queuePath ? resolve(queuePath) : "", start, limit, maxCards, results: [], fatalError: "" };
const persist = () => writeFile(output, `${JSON.stringify(report, null, 2)}\n`, "utf8");

const browser = await chromium.connectOverCDP(CDP_URL);
const context = browser.contexts()[0];
const page = context?.pages().find((candidate) => candidate.url().includes("/pimcore/admin/"));
if (!page) throw new Error("Brak zalogowanej karty PIMCORE.");
await page.reload({ waitUntil: "domcontentloaded" });
await page.waitForTimeout(2_000);
if (!await page.evaluate(() => Boolean(window.Ext)
  && Boolean(window.pimcore?.settings?.csrfToken)
  && Number(window.pimcore?.currentuser?.id) > 0
  && window.pimcore?.currentuser?.active === true)) throw new Error("Sesja PIMCORE nie jest aktywna.");

async function rawObject(id) {
  return page.evaluate(async (objectId) => {
    const response = await fetch(`/pimcore/admin/object/get?id=${objectId}&_=${Date.now()}`, {
      credentials: "same-origin",
      headers: { Accept: "application/json", "Cache-Control": "no-cache" },
    });
    return response.json();
  }, id);
}

async function releaseOwnLock(id, payload) {
  if (!payload?.editlock) return false;
  const own = await page.evaluate((userId) => Number(window.pimcore?.currentuser?.id) === Number(userId), payload.editlock.userId);
  if (!own) throw new Error(`foreign_lock:${id}`);
  const result = await page.evaluate(async (objectId) => new Promise((resolveRequest) => {
    window.Ext.Ajax.request({
      url: "/pimcore/admin/element/unlock-element",
      method: "PUT",
      headers: { "X-Pimcore-CSRF-Token": window.pimcore.settings.csrfToken },
      params: { id: objectId, type: "object" },
      callback: (_options, success, response) => resolveRequest({ success, status: response?.status || 0 }),
    });
  }), id);
  if (!result.success || result.status !== 200) throw new Error(`own_lock_release_failed:${id}:http_${result.status}`);
  return true;
}

async function readObject(id) {
  let payload = await rawObject(id);
  if (payload?.editlock) {
    await releaseOwnLock(id, payload);
    payload = await rawObject(id);
  }
  if (Number(payload?.general?.id) !== id || !payload?.data) throw new Error(`object_read_failed:${id}`);
  return payload;
}

async function actions(id, classId) {
  const result = await page.evaluate(async ({ objectId, objectClassId }) => {
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
    return { success: response.ok, status: response.status, payload };
  }, { objectId: id, objectClassId: classId });
  if (!result.success || result.status !== 200) throw new Error(`workflow_actions_failed:${id}:http_${result.status}`);
  return result.payload;
}

const critical = (object) => {
  const data = object.data || {};
  return {
    ean: data.ean,
    manufacturerIndex: data.manufacturerIndex,
    productName: data.productName,
    name: data.name,
    timName: data.timName,
    listPrice: data.listPrice,
    netCatalogPrice: data.netCatalogPrice,
    mainPhoto: data.mainPhoto,
    description: data.productDescriptions,
    dataSheet: data.dataSheet,
    certifications: data.certifications,
    instructions: data.instructions,
    energyClass: data.energyClass,
    energyClassLabels: data.energyClassLabels,
    energyTechnicalCards: data.energyTechnicalCards,
  };
};
const same = (a, b) => JSON.stringify(a) === JSON.stringify(b);

let submitted = 0;
for (const product of products) {
  if (apply && submitted >= maxCards) break;
  const result = { ...product, status: "failed" };
  try {
    const before = await readObject(product.id);
    const data = before.data;
    const description = String(data.productDescriptions?.data?.longMarketingDescription || "");
    const requiredRelations = product.requiredRelations || ["certifications", "instructions", "dataSheet"];
    if (String(data.ean || "") !== product.ean
      || String(data.manufacturerIndex || "") !== product.model
      || Number(data.listPrice?.value) !== product.price
      || (product.xmlStock != null && Number(product.xmlStock) <= 0)
      || String(data.state || "") !== "new"
      || String(data.status || "") !== "new"
      || before.general?.published !== true
      || before.general?.locked === true
      || !description.includes(product.model)
      || /\b\d{13}\b/.test(description)
      || !requiredRelations.every((field) => Array.isArray(data[field]) && data[field].length === 1)) {
      throw new Error("pre_submission_guard_failed");
    }
    const workflow = await actions(product.id, before.general.classId);
    const transition = workflow?.workflowManagement?.workflows
      ?.flatMap((item) => item.allowedTransitions || [])
      ?.find((item) => item.name === "send_for_acceptance");
    if (!transition || transition.label !== "Wyślij do akceptacji") throw new Error("send_for_acceptance_not_available");
    await releaseOwnLock(product.id, await rawObject(product.id));
    if (!apply) {
      result.status = "verified_ready_dry_run";
      result.transition = transition.name;
      report.results.push(result);
      await persist();
      continue;
    }

    const beforeCritical = critical(before);
    const response = await page.evaluate(async ({ objectId }) => {
      const body = new URLSearchParams({
        ctype: "object",
        cid: String(objectId),
        workflowName: "state",
        transition: "send_for_acceptance",
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
      return { success: reply.ok, status: reply.status, body: String(await reply.text()).slice(0, 30_000) };
    }, { objectId: product.id });
    result.response = response;
    if (!response.success || response.status !== 200) throw new Error(`transition_failed:http_${response.status}`);
    let responsePayload = null;
    try { responsePayload = JSON.parse(response.body); } catch {}
    if (responsePayload?.success !== true) throw new Error(`transition_rejected:${responsePayload?.message || "unknown"}`);
    await page.waitForTimeout(800);
    const after = await readObject(product.id);
    if (!same(critical(after), beforeCritical)) throw new Error("critical_data_changed_after_transition");
    const afterState = String(after.data?.state || "");
    if (afterState === "active" && !String(after.data?.timIndex || "").trim()) {
      throw new Error("tim_index_not_assigned_to_active_product");
    }
    if (!["active", "new_for_approval"].includes(afterState)) {
      throw new Error(`unexpected_state_after_transition:${afterState}`);
    }
    const afterWorkflow = await actions(product.id, after.general.classId);
    const stillNew = afterWorkflow?.workflowManagement?.workflows
      ?.flatMap((item) => item.allowedTransitions || [])
      ?.some((item) => item.name === "send_for_acceptance");
    await releaseOwnLock(product.id, await rawObject(product.id));
    if (stillNew || String(after.data?.state || "") === "new") throw new Error("transition_not_applied");
    result.status = afterState === "active" ? "activated" : "submitted_for_acceptance";
    result.beforeState = data.state;
    result.afterState = after.data.state;
    result.afterStatus = after.data.status;
    result.criticalDataUnchanged = true;
    submitted += 1;
    report.results.push(result);
    await persist();
    console.log(JSON.stringify(result));
  } catch (error) {
    result.reason = error.message;
    report.results.push(result);
    report.fatalError = `${product.model}: ${error.message}`;
    await releaseOwnLock(product.id, await rawObject(product.id)).catch(() => {});
    await persist();
    break;
  }
}

await persist();
console.log(JSON.stringify({ submitted, fatalError: report.fatalError }));
if (report.fatalError) process.exitCode = 1;
process.exit(process.exitCode || 0);
