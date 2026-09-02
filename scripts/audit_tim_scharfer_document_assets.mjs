import { mkdir, writeFile } from "node:fs/promises";
import { dirname, resolve } from "node:path";
import { chromium } from "../../radlight/node_modules/playwright/index.mjs";

const CDP_URL = "http://127.0.0.1:9222";
function argumentValue(name, fallback = "") {
  const index = process.argv.indexOf(name);
  return index === -1 ? fallback : process.argv[index + 1] || fallback;
}
const OUTPUT = resolve(argumentValue("--output", "exports/tim/remediation/scharfer-document-assets-audit-2026-09-01.json"));

const PRODUCTS = [
  [2345680, "SCH-18-12"], [2345681, "SCH-18-24"],
  [2345683, "SCH-20-12"], [2345682, "SCH-20-24"],
  [2345684, "SCH-30-12"], [2345685, "SCH-30-24"],
  [2345687, "SCH-45-12"], [2345686, "SCH-45-24"],
  [2345688, "SCH-60-12"], [2345689, "SCH-60-24"],
  [2345691, "SCH-100-12"], [2345690, "SCH-100-24"],
  [2345692, "SCH-150-12"], [2345693, "SCH-150-24"],
  [2345697, "SCH-200-12"], [2345694, "SCH-200-24"],
  [2345696, "SCH-300-12"], [2345695, "SCH-300-24"],
  [7774290, "SCH-400-12"], [7774293, "SCH-400-24"],
].map(([id, model]) => ({ id, model }));

const browser = await chromium.connectOverCDP(CDP_URL);
const context = browser.contexts()[0];
if (!context) throw new Error("Brak aktywnego kontekstu Chrome.");

let page = null;
let frame = null;
for (const candidate of context.pages()) {
  for (const candidateFrame of candidate.frames().filter((item) => item.url().includes("/pimcore/admin/"))) {
    const authenticated = await candidateFrame.evaluate(() => Boolean(window.Ext)
      && Boolean(window.pimcore?.settings?.csrfToken)
      && Number(window.pimcore?.currentuser?.id || window.pimcore?.globalmanager?.get?.("user")?.id) > 0).catch(() => false);
    if (authenticated) {
      page = candidate;
      frame = candidateFrame;
      break;
    }
  }
  if (frame) break;
}
if (!page || !frame) throw new Error("Brak zalogowanej ramki PIMCORE.");

const blockedRequests = [];
const routeHandler = async (route) => {
  const request = route.request();
  if (["GET", "HEAD", "OPTIONS"].includes(request.method().toUpperCase())) return route.continue();
  blockedRequests.push({ method: request.method(), url: request.url() });
  return route.abort("blockedbyclient");
};
await page.route("**/*", routeHandler);

async function readObject(id) {
  const response = await frame.evaluate(async ({ objectId, nonce }) => {
    const request = await fetch(`/pimcore/admin/object/get?id=${objectId}&_=${nonce}`, {
      credentials: "same-origin",
      headers: { Accept: "application/json", "Cache-Control": "no-cache" },
    });
    let payload = null;
    try { payload = await request.json(); } catch {}
    return { status: request.status, payload };
  }, { objectId: id, nonce: Date.now() });
  if (response.status !== 200 || !response.payload) throw new Error(`object_read_failed:${id}:${response.status}`);
  return response.payload;
}

async function auditAsset(assetId) {
  return frame.evaluate(async ({ id, nonce }) => {
    const metadataRequest = await fetch(`/pimcore/admin/asset/get-data-by-id?id=${id}&_=${nonce}`, {
      credentials: "same-origin",
      headers: { Accept: "application/json", "Cache-Control": "no-cache" },
    });
    let metadata = null;
    try { metadata = await metadataRequest.json(); } catch {}
    const downloadRequest = await fetch(`/pimcore/admin/asset/download?id=${id}&_=${nonce}`, {
      credentials: "same-origin",
      headers: { "Cache-Control": "no-cache" },
    });
    const result = {
      id,
      metadataStatus: metadataRequest.status,
      type: String(metadata?.type || ""),
      path: `${String(metadata?.path || "").replace(/\/$/, "")}/${String(metadata?.filename || "")}`,
      downloadStatus: downloadRequest.status,
      contentType: String(downloadRequest.headers.get("content-type") || ""),
      contentLength: String(downloadRequest.headers.get("content-length") || ""),
    };
    try { await downloadRequest.body?.cancel(); } catch {}
    return result;
  }, { id: Number(assetId), nonce: Date.now() });
}

const results = [];
const assetCache = new Map();
for (const product of PRODUCTS) {
  const object = await readObject(product.id);
  const row = {
    ...product,
    liveModel: String(object.data?.manufacturerIndex || ""),
    ean: String(object.data?.ean || ""),
    price: object.data?.netCatalogPrice ?? null,
    published: Boolean(object.general?.published),
    relations: {},
  };
  for (const field of ["certifications", "dataSheet", "instructions"]) {
    const relations = Array.isArray(object.data?.[field]) ? object.data[field] : [];
    row.relations[field] = [];
    for (const relation of relations) {
      const assetId = Number(relation?.id || 0);
      if (!assetId) continue;
      if (!assetCache.has(assetId)) assetCache.set(assetId, await auditAsset(assetId));
      row.relations[field].push({ relation: { id: assetId, path: relation.path || "" }, audit: assetCache.get(assetId) });
    }
  }
  results.push(row);
  console.log(`${product.model}: CE ${row.relations.certifications.map((item) => item.audit.downloadStatus).join(",") || "brak"}; karta ${row.relations.dataSheet.map((item) => item.audit.downloadStatus).join(",") || "brak"}`);
}

const allAssets = [...assetCache.values()];
const report = {
  generatedAt: new Date().toISOString(),
  mode: "read-only",
  products: results,
  uniqueAssets: allAssets.length,
  downloadableAssets: allAssets.filter((asset) => asset.downloadStatus === 200 && asset.contentType.includes("pdf")).length,
  unavailableAssets: allAssets.filter((asset) => asset.downloadStatus !== 200 || !asset.contentType.includes("pdf")).length,
  blockedRequests,
};

await mkdir(dirname(OUTPUT), { recursive: true });
await writeFile(OUTPUT, `${JSON.stringify(report, null, 2)}\n`, "utf8");
await page.unroute("**/*", routeHandler);
console.log(JSON.stringify({ output: OUTPUT, uniqueAssets: report.uniqueAssets, downloadableAssets: report.downloadableAssets, unavailableAssets: report.unavailableAssets, blockedRequests }, null, 2));
process.exit(0);
