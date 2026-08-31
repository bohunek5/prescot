import { createHash } from "node:crypto";
import { mkdir, readFile, writeFile } from "node:fs/promises";
import { dirname, resolve } from "node:path";
import { chromium } from "../../radlight/node_modules/playwright/index.mjs";

function argumentValue(name, fallback = "") {
  const index = process.argv.indexOf(name);
  return index === -1 ? fallback : process.argv[index + 1] || fallback;
}

function normalizedDescription(html) {
  return String(html || "")
    .replace(/^<section>\s*/i, "")
    .replace(/\s*<\/section>$/i, "")
    .replace(/&quot;|&#0*34;|&#x0*22;/gi, '"')
    .replace(/&apos;|&#0*39;|&#x0*27;/gi, "'")
    .trim();
}

function digest(value) {
  return createHash("sha256").update(String(value || "")).digest("hex");
}

function stockValue(stockLevel) {
  if (!Array.isArray(stockLevel)) return 0;
  return Math.max(0, ...stockLevel.map((row) => Number(row?.stockTotalQuantityMz) || 0));
}

function priceValue(...values) {
  for (const value of values) {
    const candidate = value && typeof value === "object" ? value.value : value;
    if (candidate !== null && candidate !== undefined && candidate !== "") return candidate;
  }
  return null;
}

const profileDir = argumentValue("--profile-dir");
const cdpUrl = argumentValue("--cdp-url");
const queuePath = resolve(argumentValue("--queue", "exports/tim/remediation/full-description-queue-v2.json"));
const stageName = argumentValue("--stage", "activePositiveNeedsUpdate");
const outputPath = resolve(argumentValue("--output", "/tmp/tim-description-queue-live-verification.json"));
const concurrency = Math.max(1, Math.min(16, Number(argumentValue("--concurrency", "8")) || 8));
const startIndex = Math.max(0, Number(argumentValue("--start-index", "0")) || 0);
const limit = Math.max(1, Number(argumentValue("--limit", "1000000")) || 1_000_000);
const allowZeroStock = process.argv.includes("--allow-zero-stock");
const expectedBufferState = stageName === "bufferNewNeedsUpdate"
  ? "new"
  : stageName === "bufferApprovalNeedsUpdate"
    ? "new_for_approval"
    : "";
if (!profileDir && !cdpUrl) throw new Error("Podaj --profile-dir albo --cdp-url z zalogowaną sesją Chrome.");
if (stageName === "activeZeroNeedsUpdate" && !allowZeroStock) throw new Error("Etap activeZeroNeedsUpdate wymaga --allow-zero-stock.");
if (allowZeroStock && stageName !== "activeZeroNeedsUpdate") throw new Error("--allow-zero-stock jest dozwolone wyłącznie dla etapu activeZeroNeedsUpdate.");

const queueDocument = JSON.parse(await readFile(queuePath, "utf8"));
const fullQueue = queueDocument?.stages?.[stageName];
if (!Array.isArray(fullQueue)) throw new Error(`Nie znaleziono etapu ${stageName}.`);
const queue = fullQueue.slice(startIndex, startIndex + limit);

let browser = null;
let context = null;
let page = null;
let pimcoreFrame = null;
if (cdpUrl) {
  browser = await chromium.connectOverCDP(cdpUrl);
  context = browser.contexts()[0];
  page = context.pages().find((candidate) => candidate.frames().some((frame) => frame.url() === "https://dostawca.tim.pl/pimcore/admin/"));
  pimcoreFrame = page?.frames().find((frame) => frame.url() === "https://dostawca.tim.pl/pimcore/admin/") || null;
  if (!pimcoreFrame) throw new Error("Nie znaleziono zalogowanej ramki PIMCORE w sesji CDP.");
} else {
  context = await chromium.launchPersistentContext(profileDir, {
    headless: true,
    executablePath: "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    args: ["--profile-directory=Default"],
    serviceWorkers: "block",
    timeout: 45_000,
  });
  const sessionPostAllowlist = new Set([
    "https://dostawca.tim.pl/pimcore/api/authenticate-user-by-token",
    "https://dostawca.tim.pl/pimcore/api/verify-session",
  ]);
  await context.route("**/*", async (route) => {
    const method = route.request().method().toUpperCase();
    const url = route.request().url();
    if (["GET", "HEAD", "OPTIONS"].includes(method)) return route.continue();
    if (method === "POST" && sessionPostAllowlist.has(url)) return route.continue();
    return route.abort("blockedbyclient");
  });
  page = context.pages()[0] || await context.newPage();
  await page.goto("https://dostawca.tim.pl/pimcore/", { waitUntil: "domcontentloaded", timeout: 45_000 });
  pimcoreFrame = page.frames().find((frame) => frame.url().includes("/pimcore/admin/"));
  for (let attempt = 0; !pimcoreFrame && attempt < 15; attempt += 1) {
    await page.waitForTimeout(1_000);
    pimcoreFrame = page.frames().find((frame) => frame.url().includes("/pimcore/admin/"));
  }
  if (!pimcoreFrame) throw new Error("Nie znaleziono zalogowanej ramki PIMCORE.");
  await page.waitForTimeout(5_000);
}

let readSequence = 0;
async function readObject(objectId) {
  let lastError = "read_timeout";
  for (let attempt = 1; attempt <= 3; attempt += 1) {
    try {
      readSequence += 1;
      const url = `https://dostawca.tim.pl/pimcore/admin/object/get?id=${objectId}&_=${Date.now()}-${readSequence}`;
      if (cdpUrl) {
        const result = await pimcoreFrame.evaluate(async (target) => {
          const response = await fetch(target, { method: "GET", credentials: "same-origin", cache: "no-store" });
          let object = null;
          try { object = JSON.parse(await response.text()); } catch {}
          return { status: response.status, object };
        }, url);
        if (result.status < 500) return result;
        lastError = `http_${result.status}`;
      } else {
        const response = await context.request.get(url, {
          timeout: 30_000,
          headers: { "Cache-Control": "no-cache", Pragma: "no-cache" },
        });
        let object = null;
        try { object = await response.json(); } catch {}
        if (response.status() < 500) return { status: response.status(), object };
        lastError = `http_${response.status()}`;
      }
    } catch (error) {
      lastError = String(error?.name || error?.message || error);
    }
    if (attempt < 3) await new Promise((resolveWait) => setTimeout(resolveWait, attempt * 700));
  }
  throw new Error(`read_failed_after_retries:${lastError}`);
}

const results = new Array(queue.length);
let nextIndex = 0;
async function worker() {
  while (true) {
    const index = nextIndex;
    nextIndex += 1;
    if (index >= queue.length) return;
    const expected = queue[index];
    const objectId = Number(expected.pimcoreId);
    const row = {
      index: startIndex + index,
      objectId,
      ean: String(expected.ean || ""),
      manufacturerCode: String(expected.manufacturerCode || ""),
      name: String(expected.name || ""),
      status: "failed",
    };
    try {
      const read = await readObject(objectId);
      const object = read.object || {};
      const data = object.data || {};
      const current = normalizedDescription(data.productDescriptions?.data?.longMarketingDescription);
      const target = normalizedDescription(expected.descriptionHtml);
      row.httpStatus = read.status;
      row.timIndex = data.timIndex ?? null;
      row.liveState = data.state ?? null;
      row.liveStatus = data.status ?? null;
      row.published = object.general?.published === true;
      row.locked = object.general?.locked === true;
      row.versionCount = object.general?.versionCount ?? null;
      row.liveStock = stockValue(data.stockLevel);
      row.livePrice = priceValue(data.netCatalogPrice, data.prize);
      row.liveVatRate = priceValue(data.vatRate);
      row.liveMeasureUnit = data.measureUnit ?? null;
      row.productAvailableForSale = data.productAvailableForSale ?? null;
      row.currentHash = digest(current);
      row.expectedHash = digest(target);
      row.descriptionLength = current.length;
      row.identityMatches = read.status === 200
        && Number(object.general?.id) === objectId
        && String(data.ean || "") === row.ean
        && String(data.manufacturerIndex || "") === row.manufacturerCode;
      row.descriptionMatches = current === target;
      row.stockMatchesStage = expectedBufferState ? true : allowZeroStock ? row.liveStock === 0 : row.liveStock > 0;
      row.statePathAndPublished = expectedBufferState
        ? data.state === expectedBufferState
          && row.published
          && String(object.general?.fullpath || "").startsWith("/Produkty/Bufor/PRESCOT SPÓŁKA Z-00060865/")
        : data.state === "active" && row.published;
      row.status = row.identityMatches && row.descriptionMatches && row.statePathAndPublished ? "verified" : "mismatch";
      if (!row.identityMatches) row.reason = "identity_mismatch";
      else if (!row.statePathAndPublished) row.reason = expectedBufferState ? "not_expected_buffer_state_or_path" : "not_active_or_not_published";
      else if (!row.descriptionMatches) row.reason = "description_mismatch";
      else if (!expectedBufferState && !row.stockMatchesStage) row.warning = "live_stock_changed_since_queue_snapshot";
    } catch (error) {
      row.reason = error.message;
    }
    results[index] = row;
  }
}

try {
  await Promise.all(Array.from({ length: concurrency }, () => worker()));
} finally {
  if (cdpUrl) await browser.close();
  else await context.close();
}

const report = {
  generatedAt: new Date().toISOString(),
  mode: "read_only_get_verification",
  transport: cdpUrl ? "existing_chrome_cdp" : "isolated_profile",
  queuePath,
  stageName,
  startIndex,
  limit,
  concurrency,
  allowZeroStock,
  counts: {
    total: results.length,
    verified: results.filter((row) => row.status === "verified").length,
    mismatch: results.filter((row) => row.status === "mismatch").length,
    failed: results.filter((row) => row.status === "failed").length,
    locked: results.filter((row) => row.locked).length,
  },
  results,
};
await mkdir(dirname(outputPath), { recursive: true });
await writeFile(outputPath, `${JSON.stringify(report, null, 2)}\n`, "utf8");
console.log(JSON.stringify(report.counts));
console.log(outputPath);
if (report.counts.mismatch || report.counts.failed) process.exitCode = 1;
