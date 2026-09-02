#!/usr/bin/env node

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

function same(a, b) {
  return JSON.stringify(a) === JSON.stringify(b);
}

function price(value) {
  return Number(value?.value ?? value);
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

function stableGeneral(general) {
  const keys = ["id", "parentId", "type", "key", "classId", "published", "className", "fullpath"];
  return Object.fromEntries(keys.map((key) => [key, clone(general?.[key])]));
}

function protectedData(data) {
  const copy = clone(data || {});
  delete copy.dataSheet;
  delete copy.assortmentType;
  delete copy.countAttachments;
  delete copy.dataSheetAdded;
  return copy;
}

const apply = process.argv.includes("--apply");
const start = Math.max(0, Number(argumentValue("--start", "0")) || 0);
const limit = Math.max(1, Number(argumentValue("--limit", "3")) || 3);
const maxCards = Math.max(0, Number(argumentValue("--max-cards", "0")) || 0);
if (apply && maxCards < 1) throw new Error("Tryb --apply wymaga dodatniego --max-cards.");
const outputPath = resolve(argumentValue("--output", "exports/tim/remediation/buffer-incorrect-datasheets-removal.json"));
const source = JSON.parse(await readFile(resolve("exports/tim/remediation/buffer-strip-catalog-ce-queue-2026-09-01.json"), "utf8"));
const models = new Set(["48EC480-050-8-NW", "48EC480-050-8-NW50", "E009-050-8-W6K100"]);
const queue = source.items
  .filter((item) => models.has(item.model))
  .map((item) => ({ ...item, expectedPath: `/Import multimediow/24248/${item.model}_karta_katalogowa.pdf` }))
  .slice(start, start + limit);

const report = { generatedAt: new Date().toISOString(), apply, start, limit, maxCards, written: 0, results: [], fatalError: "" };
const persist = () => writeFile(outputPath, `${JSON.stringify(report, null, 2)}\n`, "utf8");

const browser = await chromium.connectOverCDP("http://127.0.0.1:9222");
const context = browser.contexts()[0];
let page = null;
let frame = null;
for (const candidate of context.pages()) {
  for (const candidateFrame of candidate.frames().filter((item) => item.url().includes("/pimcore/admin/"))) {
    const ok = await candidateFrame.evaluate(() => Boolean(window.Ext)
      && Boolean(window.pimcore?.settings?.csrfToken)
      && Number(window.pimcore?.currentuser?.id) > 0).catch(() => false);
    if (ok) { page = candidate; frame = candidateFrame; break; }
  }
  if (frame) break;
}
if (!page || !frame) throw new Error("Brak zalogowanej ramki PIMCORE.");

async function readObject(id) {
  for (let attempt = 0; attempt < 8; attempt += 1) {
    const result = await frame.evaluate(async (objectId) => {
      const response = await fetch(`/pimcore/admin/object/get?id=${objectId}&_=${Date.now()}`, {
        credentials: "same-origin",
        headers: { Accept: "application/json", "Cache-Control": "no-cache" },
      });
      let payload = null;
      try { payload = await response.json(); } catch {}
      return { status: response.status, payload };
    }, id);
    if (result.status === 200 && result.payload) return result.payload;
    await page.waitForTimeout(750);
  }
  throw new Error(`object_read_failed:${id}`);
}

async function releaseOwnLock(id) {
  return frame.evaluate(async (objectId) => {
    const probe = await fetch(`/pimcore/admin/object/get?id=${objectId}&_=${Date.now()}`, {
      credentials: "same-origin",
      headers: { Accept: "application/json", "Cache-Control": "no-cache" },
    });
    const payload = await probe.json();
    const currentUserId = Number(window.pimcore?.currentuser?.id);
    if (!payload?.editlock) return { released: false, reason: "no_lock" };
    if (Number(payload.editlock.userId) !== currentUserId) return { released: false, reason: "foreign_lock" };
    const response = await new Promise((resolveRequest) => window.Ext.Ajax.request({
      url: "/pimcore/admin/element/unlock-element",
      method: "PUT",
      headers: { "X-Pimcore-CSRF-Token": window.pimcore.settings.csrfToken },
      params: { id: objectId, type: "object" },
      callback: (_options, success, result) => resolveRequest({ success, status: result?.status || 0 }),
    }));
    if (!response.success || response.status !== 200) throw new Error(`own_lock_release_failed:http_${response.status}`);
    return { released: true, reason: "own_lock" };
  }, id);
}

for (const product of queue) {
  if (apply && report.written >= maxCards) break;
  const result = { id: product.id, ean: product.ean, model: product.model, status: "failed" };
  try {
    const before = await readObject(product.id);
    const data = before.data || {};
    const relation = data.dataSheet;
    if (Number(before.general?.id) !== Number(product.id)
      || String(data.ean || "") !== String(product.ean)
      || String(data.manufacturerIndex || "") !== product.model
      || String(data.state || "") !== "new"
      || String(data.status || "") !== "new"
      || before.general?.published !== true
      || Math.abs(price(data.listPrice) - Number(product.xmlPrice)) > 0.0001
      || !Array.isArray(relation)
      || relation.length !== 1
      || String(relation[0]?.path || "") !== product.expectedPath) throw new Error("identity_price_state_or_expected_relation_guard_failed");
    if (before.general?.locked) throw new Error("live_object_locked");
    if (!apply) {
      result.status = "verified_ready_dry_run";
      result.expectedRemoval = product.expectedPath;
      report.results.push(result);
      await persist();
      continue;
    }
    const beforeProtected = protectedData(data);
    const beforeGeneral = stableGeneral(before.general);
    const beforeWorkflow = clone(before.workflowManagement);
    const beforeVersion = Number(before.general.versionCount);
    const saveData = { dataSheet: null, netCatalogPrice: clone(data.netCatalogPrice) };
    const response = await frame.evaluate(async ({ id, dataValue, generalValue }) => new Promise((resolveRequest) => {
      window.Ext.Ajax.request({
        url: "/pimcore/admin/object/save?task=undefined",
        method: "PUT",
        headers: { "X-Pimcore-CSRF-Token": window.pimcore.settings.csrfToken },
        params: { id, data: JSON.stringify(dataValue), general: JSON.stringify(generalValue), dirtyFields: JSON.stringify(["dataSheet"]) },
        callback: (_options, success, reply) => resolveRequest({ success, status: reply?.status || 0, body: String(reply?.responseText || "").slice(0, 100_000) }),
      });
    }), { id: product.id, dataValue: saveData, generalValue: saveGeneral(before.general) });
    let after = null;
    for (let attempt = 0; attempt < 8; attempt += 1) {
      after = await readObject(product.id);
      if (after.data?.dataSheet == null || (Array.isArray(after.data.dataSheet) && after.data.dataSheet.length === 0)) break;
      await page.waitForTimeout(750);
    }
    if (!(after.data?.dataSheet == null || (Array.isArray(after.data.dataSheet) && after.data.dataSheet.length === 0))) {
      throw new Error(`datasheet_removal_not_applied:http_${response.status}`);
    }
    if (!same(protectedData(after.data), beforeProtected)) throw new Error("protected_data_changed");
    if (!same(stableGeneral(after.general), beforeGeneral)) throw new Error("stable_general_changed");
    if (!same(after.workflowManagement, beforeWorkflow)) throw new Error("workflow_changed");
    const delta = Number(after.general.versionCount) - beforeVersion;
    if (![0, 1].includes(delta)) throw new Error(`unexpected_version_delta:${delta}`);
    result.status = "removed_incorrect_relation";
    result.httpStatus = response.status;
    result.removedRelation = product.expectedPath;
    result.assetRetained = true;
    result.protectedDataUnchanged = true;
    result.workflowUnchanged = true;
    result.lockRelease = await releaseOwnLock(product.id);
    report.written += 1;
    report.results.push(result);
    await persist();
    console.log(JSON.stringify({ id: product.id, model: product.model, status: result.status }));
  } catch (error) {
    result.lockRelease = await releaseOwnLock(product.id).catch((releaseError) => ({ released: false, reason: releaseError.message }));
    result.reason = error.message;
    report.results.push(result);
    report.fatalError = `${product.model}: ${error.message}`;
    await persist();
    break;
  }
}

await persist();
console.log(JSON.stringify({ checked: report.results.length, written: report.written, fatalError: report.fatalError }));
if (report.fatalError) process.exitCode = 1;
process.exit(process.exitCode || 0);
