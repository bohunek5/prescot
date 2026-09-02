import { mkdir, writeFile } from "node:fs/promises";
import { dirname, resolve } from "node:path";
import { chromium } from "../../radlight/node_modules/playwright/index.mjs";

const OUTPUT = resolve("exports/tim/remediation/prescot-active-exact-tapes-postverify-2026-09-01.json");
const PRODUCTS = [
  { id: 2398815, model: "12D018-010-10-NWH50", ean: "5905475361050", price: 10, eprelId: "1068744" },
  { id: 2398816, model: "12D018-010-10-NWL50", ean: "5905475361067", price: 10, eprelId: "1069314" },
  { id: 2398818, model: "12D018-010-10-WWL50", ean: "5905475361081", price: 10, eprelId: "1395324" },
  { id: 2398820, model: "12D018-010-10-WL50", ean: "5905475361104", price: 10, eprelId: "1396524" },
  { id: 2667162, model: "24D013-050-10-WW50", ean: "5905475361623", price: 13, eprelId: "1347725" },
];
function numeric(value) { return Number(value && typeof value === "object" && "value" in value ? value.value : value); }

const browser = await chromium.connectOverCDP("http://127.0.0.1:9222");
const context = browser.contexts()[0];
let page = null;
let frame = null;
for (const candidate of context.pages()) {
  for (const candidateFrame of candidate.frames().filter((item) => item.url().includes("/pimcore/admin/"))) {
    if (await candidateFrame.evaluate(() => Number(window.pimcore?.currentuser?.id) > 0).catch(() => false)) {
      page = candidate; frame = candidateFrame; break;
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

const results = [];
for (const product of PRODUCTS) {
  const row = await frame.evaluate(async (expected) => {
    const response = await fetch(`/pimcore/admin/object/get?id=${expected.id}&_=${Date.now()}`, { credentials: "same-origin", headers: { "Cache-Control": "no-cache" } });
    const object = await response.json();
    const data = object.data || {};
    const fields = ["certifications", "dataSheet", "energyClassLabels", "energyTechnicalCards"];
    const downloads = {};
    for (const field of fields) {
      downloads[field] = [];
      for (const relation of (Array.isArray(data[field]) ? data[field] : [])) {
        const request = await fetch(`/pimcore/admin/asset/download?id=${relation.id}&_=${Date.now()}`, { credentials: "same-origin", headers: { "Cache-Control": "no-cache" } });
        downloads[field].push({ id: Number(relation.id), status: request.status, contentType: String(request.headers.get("content-type") || "") });
        try { await request.body?.cancel(); } catch {}
      }
    }
    return {
      id: Number(object.general?.id), model: String(data.manufacturerIndex || ""), ean: String(data.ean || ""), timIndex: String(data.timIndex || ""),
      price: data.listPrice, state: String(data.state?.value || data.state || ""), status: String(data.status?.value || data.status || ""),
      published: Boolean(object.general?.published), locked: Boolean(object.general?.locked), energyClass: String(data.energyClass || ""),
      descriptionHasModel: String(data.productDescriptions?.data?.longMarketingDescription || "").includes(expected.model),
      descriptionHasEan: /\b\d{13}\b/u.test(String(data.productDescriptions?.data?.longMarketingDescription || "")),
      downloads,
    };
  }, product);
  const allDownloads = Object.values(row.downloads).flat();
  const ok = row.id === product.id && row.model === product.model && row.ean === product.ean
    && Math.abs(numeric(row.price) - product.price) < 0.0001 && row.state === "active" && row.status === "active"
    && row.published && !row.locked && row.energyClass === "F" && row.descriptionHasModel && !row.descriptionHasEan
    && allDownloads.length === 4 && allDownloads.every((asset) => asset.status === 200
      && (asset.contentType.includes("pdf") || asset.contentType.includes("image/jpeg")));
  results.push({ ...product, live: row, verified: ok });
  console.log(`${product.model}: ${ok ? "OK" : "BŁĄD"}; ${allDownloads.map((asset) => asset.status).join("/")}`);
}

const report = {
  generatedAt: new Date().toISOString(), readOnly: true, products: results,
  counts: { total: results.length, verified: results.filter((item) => item.verified).length, failed: results.filter((item) => !item.verified).length },
  blockedWrites,
};
await mkdir(dirname(OUTPUT), { recursive: true });
await writeFile(OUTPUT, `${JSON.stringify(report, null, 2)}\n`, "utf8");
await page.unroute("**/*", routeHandler);
console.log(JSON.stringify({ output: OUTPUT, counts: report.counts, blockedWrites: blockedWrites.length }, null, 2));
if (report.counts.failed || blockedWrites.length) process.exitCode = 1;
process.exit(process.exitCode || 0);
