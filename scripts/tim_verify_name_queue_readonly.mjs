import { mkdir, readFile, writeFile } from "node:fs/promises";
import { dirname, resolve } from "node:path";
import { chromium } from "../../radlight/node_modules/playwright/index.mjs";

function argumentValue(name, fallback = "") {
  const index = process.argv.indexOf(name);
  return index === -1 ? fallback : process.argv[index + 1] || fallback;
}

function stockValue(stockLevel) {
  if (!Array.isArray(stockLevel)) return 0;
  return Math.max(0, ...stockLevel.map((row) => Number(row?.stockTotalQuantityMz) || 0));
}

const profileDir = argumentValue("--profile-dir");
const queuePath = resolve(argumentValue("--queue", "exports/tim/remediation/active-cover-name-queue.json"));
const stageName = argumentValue("--stage", "activePositive");
const outputPath = resolve(argumentValue("--output", "/tmp/tim-name-queue-live-verification.json"));
const concurrency = Math.max(1, Math.min(16, Number(argumentValue("--concurrency", "8")) || 8));
const startIndex = Math.max(0, Number(argumentValue("--start-index", "0")) || 0);
const limit = Math.max(1, Number(argumentValue("--limit", "1000000")) || 1_000_000);
const allowZeroStock = process.argv.includes("--allow-zero-stock");
if (!profileDir) throw new Error("Podaj --profile-dir z kopią zalogowanego profilu Chrome.");
if (stageName === "activeZero" && !allowZeroStock) throw new Error("Etap activeZero wymaga --allow-zero-stock.");
if (allowZeroStock && stageName !== "activeZero") throw new Error("--allow-zero-stock jest dozwolone wyłącznie dla etapu activeZero.");

const queueDocument = JSON.parse(await readFile(queuePath, "utf8"));
const fullQueue = queueDocument?.stages?.[stageName];
if (!Array.isArray(fullQueue)) throw new Error(`Nie znaleziono etapu ${stageName}.`);
const queue = fullQueue.slice(startIndex, startIndex + limit);

const context = await chromium.launchPersistentContext(profileDir, {
  headless: true,
  executablePath: "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
  args: ["--profile-directory=Default"],
  serviceWorkers: "block",
  timeout: 45_000,
});

let readSequence = 0;
async function readObject(objectId) {
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
      if (response.status() < 500) return { status: response.status(), object };
      lastError = `http_${response.status()}`;
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
      timIndex: String(expected.timIndex || ""),
      beforeName: String(expected.beforeName || ""),
      expectedName: String(expected.afterName || ""),
      status: "failed",
    };
    try {
      const read = await readObject(objectId);
      const object = read.object || {};
      const data = object.data || {};
      row.httpStatus = read.status;
      row.currentName = String(data.timName || "");
      row.treeKey = String(object.general?.key || "");
      row.liveState = data.state ?? null;
      row.published = object.general?.published === true;
      row.locked = object.general?.locked === true;
      row.liveStock = stockValue(data.stockLevel);
      row.identityMatches = read.status === 200
        && Number(object.general?.id) === objectId
        && String(data.ean || "") === row.ean
        && String(data.manufacturerIndex || "") === row.manufacturerCode
        && String(data.timIndex || "") === row.timIndex;
      row.nameMatches = row.currentName === row.expectedName;
      row.stockMatchesStage = allowZeroStock ? row.liveStock === 0 : row.liveStock > 0;
      row.activePublishedInStockStage = data.state === "active" && row.published && row.stockMatchesStage;
      row.status = row.identityMatches && row.nameMatches && row.activePublishedInStockStage ? "verified" : "mismatch";
      if (!row.identityMatches) row.reason = "identity_mismatch";
      else if (!row.activePublishedInStockStage) row.reason = "not_active_published_in_expected_stock_stage";
      else if (!row.nameMatches) row.reason = "name_mismatch";
    } catch (error) {
      row.reason = error.message;
    }
    results[index] = row;
  }
}

try {
  await Promise.all(Array.from({ length: concurrency }, () => worker()));
} finally {
  await context.close();
}

const report = {
  generatedAt: new Date().toISOString(),
  mode: "read_only_get_verification",
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
