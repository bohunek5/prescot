#!/usr/bin/env node

import { readFile, writeFile } from "node:fs/promises";
import { resolve } from "node:path";
import { chromium } from "../../radlight/node_modules/playwright/index.mjs";

const inventoryPath = "/private/tmp/tim-pimcore-grid-inventory.json";
const catalogPath = resolve("data/catalog.json");
const verificationPath = resolve("exports/tim/remediation/final-session-stability-verify-2026-09-01.json");
function argumentValue(name, fallback = "") {
  const index = process.argv.indexOf(name);
  return index === -1 ? fallback : process.argv[index + 1] || fallback;
}
const outputPath = resolve(argumentValue("--output", "exports/tim/remediation/active-brand-offer-live-readonly-2026-09-01.json"));
const [inventory, catalog, verification] = await Promise.all([
  readFile(inventoryPath, "utf8").then(JSON.parse),
  readFile(catalogPath, "utf8").then(JSON.parse),
  readFile(verificationPath, "utf8").then(JSON.parse),
]);

const catalogByEan = new Map(catalog.products.filter((item) => item.ean).map((item) => [String(item.ean), item]));
const catalogByModel = new Map();
for (const item of catalog.products) {
  if (!item.manufacturerCode) continue;
  const key = String(item.manufacturerCode);
  if (!catalogByModel.has(key)) catalogByModel.set(key, []);
  catalogByModel.get(key).push(item);
}

function catalogProduct(item) {
  const exact = catalogByEan.get(String(item.ean || ""));
  if (exact) return exact;
  const matches = catalogByModel.get(String(item.manufacturerIndex || item.model || "")) || [];
  return matches.length === 1 ? matches[0] : null;
}

function brand(item) {
  const product = catalogProduct(item);
  const producer = String(product?.producer || "");
  const identity = `${producer} ${item.manufacturerIndex || item.model || ""} ${item.timName || ""}`;
  if (/SCHARFER|\bSCH-/iu.test(identity)) return "Scharfer";
  if (/KLUŚ|KLUS/iu.test(producer)) return "KLUŚ";
  if (/PRESCOT/iu.test(producer)) return "Prescot";
  if (!product) {
    const manufacturer = String(item.manufacturer || "");
    if (/KLUŚ|KLUS/iu.test(manufacturer)) return "KLUŚ";
    if (/PRESCOT/iu.test(manufacturer)) return "Prescot";
  }
  return "";
}

const seeds = new Map();
for (const item of inventory.products) {
  const itemBrand = brand(item);
  if (item.state !== "active" || !itemBrand) continue;
  seeds.set(Number(item.id), { id: Number(item.id), brand: itemBrand });
}
for (const result of verification.results) {
  if (result.liveState !== "active") continue;
  seeds.set(Number(result.id), { id: Number(result.id), brand: "Prescot" });
}
const brandFilter = argumentValue("--brand", "");
const queue = [...seeds.values()]
  .filter((item) => !brandFilter || item.brand === brandFilter)
  .sort((left, right) => left.id - right.id);

const browser = await chromium.connectOverCDP("http://127.0.0.1:9222");
const context = browser.contexts()[0];
async function findAuthenticatedFrame() {
  for (const candidatePage of context.pages()) {
    for (const candidateFrame of candidatePage.frames().filter((item) => item.url() === "https://dostawca.tim.pl/pimcore/admin/")) {
      const active = await candidateFrame.evaluate(() => Number(window.pimcore?.currentuser?.id) > 0
        && window.pimcore?.currentuser?.active === true).catch(() => false);
      if (active) return candidateFrame;
    }
  }
  return null;
}
let frame = await findAuthenticatedFrame();
if (!frame) throw new Error("Brak aktywnej, zalogowanej ramki PIMCORE.");
const currentUserId = await frame.evaluate(() => Number(window.pimcore.currentuser.id));

const rows = [];
const concurrency = Math.max(1, Number(argumentValue("--concurrency", "80")) || 80);
for (let start = 0; start < queue.length; start += concurrency) {
  const batch = queue.slice(start, start + concurrency);
  const evaluateBatch = (targetFrame) => targetFrame.evaluate(async ({ items, currentUserId }) => Promise.all(items.map(async (seed) => {
    const unlockOwnReadLock = async () => fetch("/pimcore/admin/element/unlock-element", {
      method: "PUT",
      credentials: "same-origin",
      headers: {
        "X-Pimcore-CSRF-Token": window.pimcore.settings.csrfToken,
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
      },
      body: new URLSearchParams({ id: String(seed.id), type: "object" }),
    });
    try {
      let response = await fetch(`/pimcore/admin/object/get?id=${seed.id}&_=${Date.now()}-${seed.id}`, {
        credentials: "same-origin",
        cache: "no-store",
        headers: { Accept: "application/json", "Cache-Control": "no-cache" },
      });
      let object = await response.json();
      if (object?.editlock) {
        if (Number(object.editlock.userId) !== currentUserId) {
          return {
            id: seed.id,
            expectedBrand: seed.brand,
            httpStatus: response.status,
            error: "foreign_lock_skipped",
            lockUserId: Number(object.editlock.userId),
          };
        }
        await unlockOwnReadLock();
        response = await fetch(`/pimcore/admin/object/get?id=${seed.id}&_=${Date.now()}-${seed.id}-retry`, {
          credentials: "same-origin",
          cache: "no-store",
          headers: { Accept: "application/json", "Cache-Control": "no-cache" },
        });
        object = await response.json();
      }
      if (object?.editlock || !object?.general) {
        return { id: seed.id, expectedBrand: seed.brand, httpStatus: response.status, error: "object_read_unavailable" };
      }
      const data = object?.data || {};
      const stockLevel = Array.isArray(data.stockLevel) ? data.stockLevel : [];
      const row = {
        id: seed.id,
        expectedBrand: seed.brand,
        httpStatus: response.status,
        published: object?.general?.published === true,
        locked: object?.general?.locked === true,
        ean: String(data.ean || "").trim(),
        model: String(data.manufacturerIndex || "").trim(),
        timIndex: String(data.timIndex || "").trim(),
        timName: String(data.timName || "").trim(),
        manufacturer: String(data.manufacturer || ""),
        state: data.state?.value || data.state || "",
        status: data.status?.value || data.status || "",
        stock: Math.max(0, ...stockLevel.map((entry) => Number(entry.stockTotalQuantityMz) || 0)),
        listPrice: data.listPrice ?? null,
        mainPhoto: String(data.mainPhoto || ""),
        descriptionHtml: String(data.productDescriptions?.data?.longMarketingDescription || ""),
        dataSheet: Array.isArray(data.dataSheet) ? data.dataSheet.length : 0,
        certifications: Array.isArray(data.certifications) ? data.certifications.length : 0,
        instructions: Array.isArray(data.instructions) ? data.instructions.length : 0,
        energyClassLabels: Array.isArray(data.energyClassLabels) ? data.energyClassLabels.length : 0,
        energyTechnicalCards: Array.isArray(data.energyTechnicalCards) ? data.energyTechnicalCards.length : 0,
      };
      const unlockResponse = await unlockOwnReadLock();
      if (unlockResponse.status !== 200) row.lockCleanupError = `unlock_http_${unlockResponse.status}`;
      return row;
    } catch (error) {
      return { id: seed.id, expectedBrand: seed.brand, httpStatus: 0, error: error.message };
    }
  })), { items: batch, currentUserId });
  let result = null;
  let lastError = null;
  for (let attempt = 0; attempt < 4 && !result; attempt += 1) {
    try {
      frame = await findAuthenticatedFrame();
      if (!frame) throw new Error("authenticated_frame_temporarily_unavailable");
      result = await evaluateBatch(frame);
    } catch (error) {
      lastError = error;
      const retryable = /Execution context was destroyed|navigation|temporarily_unavailable/i.test(String(error?.message || error));
      if (!retryable || attempt === 3) throw error;
      await new Promise((done) => setTimeout(done, 750));
    }
  }
  if (!result) throw lastError || new Error("batch_read_failed");
  rows.push(...result);
  if (rows.length % 200 < concurrency || rows.length === queue.length) console.log(`Odczytano ${rows.length}/${queue.length}`);
}

function counts(items) {
  const live = items.filter((item) => item.httpStatus === 200 && item.state === "active" && item.published);
  return {
    requested: items.length,
    read: items.filter((item) => item.httpStatus === 200).length,
    activePublished: live.length,
    activePositive: live.filter((item) => item.stock > 0).length,
    missingEan: live.filter((item) => !item.ean).length,
    missingModel: live.filter((item) => !item.model).length,
    missingPhoto: live.filter((item) => !item.mainPhoto).length,
    missingDescription: live.filter((item) => !item.descriptionHtml).length,
    descriptionHasEan: live.filter((item) => /\b\d{13}\b/u.test(item.descriptionHtml)).length,
    descriptionMissingModel: live.filter((item) => item.model && !item.descriptionHtml.includes(item.model)).length,
    missingDataSheet: live.filter((item) => !item.dataSheet).length,
    missingCertifications: live.filter((item) => !item.certifications).length,
    missingInstructions: live.filter((item) => !item.instructions).length,
    locked: live.filter((item) => item.locked).length,
  };
}

const report = {
  generatedAt: new Date().toISOString(),
  readOnly: true,
  releasesOwnReadLocks: true,
  seedInventory: inventoryPath,
  sourceCatalog: catalogPath,
  counts: Object.fromEntries(["Prescot", "Scharfer", "KLUŚ"].map((name) => [name, counts(rows.filter((item) => item.expectedBrand === name))])),
  failed: rows.filter((item) => item.httpStatus !== 200),
  products: rows,
};
await writeFile(outputPath, `${JSON.stringify(report, null, 2)}\n`, "utf8");
console.log(JSON.stringify({ outputPath, counts: report.counts, failed: report.failed.length }, null, 2));
process.exit(0);
