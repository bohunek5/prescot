import { mkdir, readFile, writeFile } from "node:fs/promises";
import { dirname, resolve } from "node:path";
import { chromium } from "../../radlight/node_modules/playwright/index.mjs";

function argumentValue(name, fallback = "") {
  const index = process.argv.indexOf(name);
  return index === -1 ? fallback : process.argv[index + 1] || fallback;
}
function numeric(value) {
  return Number(value && typeof value === "object" && "value" in value ? value.value : value);
}

const queuePath = resolve(argumentValue("--queue"));
const outputPath = resolve(argumentValue("--output", "exports/tim/remediation/document-queue-postverify.json"));
const start = Math.max(0, Number(argumentValue("--start", "0")) || 0);
const limit = Math.max(1, Number(argumentValue("--limit", "100000")) || 100000);
const concurrency = Math.max(1, Math.min(20, Number(argumentValue("--concurrency", "1")) || 1));
const ignoreDescriptionModel = process.argv.includes("--ignore-description-model");
if (!argumentValue("--queue")) throw new Error("Podaj --queue.");
const queue = JSON.parse(await readFile(queuePath, "utf8"));
if (!Array.isArray(queue?.items)) throw new Error("Brak tablicy items w kolejce.");

const browser = await chromium.connectOverCDP("http://127.0.0.1:9222");
const context = browser.contexts()[0];
let page = null;
let frame = null;
for (const candidate of context.pages()) {
  for (const candidateFrame of candidate.frames().filter((item) => item.url().includes("/pimcore/admin/"))) {
    if (await candidateFrame.evaluate(() => Number(window.pimcore?.currentuser?.id) > 0).catch(() => false)) {
      page = candidate;
      frame = candidateFrame;
      break;
    }
  }
  if (frame) break;
}
if (!page || !frame) throw new Error("Brak zalogowanej ramki PIMCORE.");

const blockedWrites = [];
const routeHandler = async (route) => {
  const request = route.request();
  if (["GET", "HEAD", "OPTIONS"].includes(request.method().toUpperCase())) return route.continue();
  blockedWrites.push({ method: request.method(), url: request.url() });
  return route.abort("blockedbyclient");
};
await page.route("**/*", routeHandler);

async function verifyExpected(expected) {
  const expectedFields = Object.keys(expected.documents || {});
  const live = await frame.evaluate(async ({ item, fields }) => {
    const response = await fetch(`/pimcore/admin/object/get?id=${item.id}&_=${Date.now()}`, {
      credentials: "same-origin",
      headers: { "Cache-Control": "no-cache" },
    });
    const object = await response.json();
    const data = object.data || {};
    const downloads = {};
    for (const field of fields) {
      downloads[field] = [];
      for (const relation of (Array.isArray(data[field]) ? data[field] : [])) {
        const assetResponse = await fetch(`/pimcore/admin/asset/download?id=${relation.id}&_=${Date.now()}`, {
          credentials: "same-origin",
          headers: { "Cache-Control": "no-cache" },
        });
        downloads[field].push({
          id: Number(relation.id),
          path: String(relation.path || ""),
          status: assetResponse.status,
          contentType: String(assetResponse.headers.get("content-type") || ""),
        });
        try { await assetResponse.body?.cancel(); } catch {}
      }
    }
    const description = String(data.productDescriptions?.data?.longMarketingDescription || "");
    return {
      httpStatus: response.status,
      id: Number(object.general?.id),
      published: Boolean(object.general?.published),
      locked: Boolean(object.general?.locked),
      ean: String(data.ean || ""),
      model: String(data.manufacturerIndex || ""),
      timIndex: String(data.timIndex || ""),
      timName: String(data.timName || ""),
      price: data.listPrice,
      state: String(data.state?.value || data.state || ""),
      status: String(data.status?.value || data.status || ""),
      descriptionHasModel: description.includes(item.model),
      descriptionHasEan: /\b\d{13}\b/u.test(description),
      downloads,
    };
  }, { item: expected, fields: expectedFields });
  const expectedPaths = Object.fromEntries(Object.entries(expected.documents || {}).map(([field, spec]) => [field, `/Import multimediow/24248/${spec.filename}`]));
  const documentsOk = expectedFields.every((field) => Array.isArray(live.downloads[field])
    && live.downloads[field].length === 1
    && live.downloads[field][0].path === expectedPaths[field]
    && live.downloads[field][0].status === 200
    && live.downloads[field][0].contentType.includes("pdf"));
  const expectedState = String(expected.state || expected.expectedState || "active");
  const expectedStatus = expectedState === "active" ? "active" : "new";
  const timPriceOk = expected.timListPrice == null
    || Math.abs(numeric(live.price) - Number(expected.timListPrice)) < 0.0001;
  const xmlPriceOk = expected.xmlPrice == null
    || Math.abs(numeric(live.price) - Number(expected.xmlPrice)) < 0.0001;
  const verified = live.httpStatus === 200
    && live.id === Number(expected.id)
    && live.ean === String(expected.ean)
    && live.model === String(expected.model)
    && timPriceOk
    && xmlPriceOk
    && live.state === expectedState
    && live.status === expectedStatus
    && live.published
    && !live.locked
    && (ignoreDescriptionModel || live.descriptionHasModel)
    && !live.descriptionHasEan
    && documentsOk;
  return {
    id: expected.id,
    ean: expected.ean,
    model: expected.model,
    expectedPrice: expected.timListPrice,
    expectedState,
    expectedDocuments: expectedPaths,
    live,
    documentsOk,
    verified,
  };
}

const results = [];
const selected = queue.items.slice(start, start + limit);
for (let offset = 0; offset < selected.length; offset += concurrency) {
  const batch = await Promise.all(selected.slice(offset, offset + concurrency).map(verifyExpected));
  results.push(...batch);
  for (const result of batch) console.log(`${result.model}: ${result.verified ? "OK" : "BŁĄD"}`);
}

const report = {
  generatedAt: new Date().toISOString(),
  readOnly: true,
  queuePath,
  start,
  limit,
  concurrency,
  ignoreDescriptionModel,
  counts: {
    total: results.length,
    verified: results.filter((item) => item.verified).length,
    failed: results.filter((item) => !item.verified).length,
    downloadableRelations: results.flatMap((item) => Object.values(item.live.downloads).flat()).filter((asset) => asset.status === 200).length,
  },
  blockedWrites,
  products: results,
};
await mkdir(dirname(outputPath), { recursive: true });
await writeFile(outputPath, `${JSON.stringify(report, null, 2)}\n`, "utf8");
await page.unroute("**/*", routeHandler);
console.log(JSON.stringify({ output: outputPath, counts: report.counts, blockedWrites: blockedWrites.length }, null, 2));
if (report.counts.failed || blockedWrites.length) process.exitCode = 1;
process.exit(process.exitCode || 0);
