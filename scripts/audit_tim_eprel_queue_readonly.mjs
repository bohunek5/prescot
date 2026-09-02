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
const outputPath = resolve(argumentValue("--output", "exports/tim/remediation/eprel-queue-postverify.json"));
const start = Math.max(0, Number(argumentValue("--start", "0")) || 0);
const limit = Math.max(1, Number(argumentValue("--limit", "100000")) || 100000);
const expectedStateOverride = argumentValue("--expected-state-override", "");
if (expectedStateOverride && !["new", "new_for_approval", "active"].includes(expectedStateOverride)) {
  throw new Error("Niedozwolony --expected-state-override.");
}
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

const products = [];
for (const expected of queue.items.slice(start, start + limit)) {
  const live = await frame.evaluate(async (item) => {
    const response = await fetch(`/pimcore/admin/object/get?id=${item.pimcoreId}&_=${Date.now()}`, {
      credentials: "same-origin",
      headers: { "Cache-Control": "no-cache" },
    });
    const object = await response.json();
    const data = object.data || {};
    const downloads = {};
    for (const field of ["energyClassLabels", "energyTechnicalCards"]) {
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
      energyClass: String(data.energyClass || ""),
      descriptionHasModel: description.includes(item.manufacturerCode),
      descriptionHasEan: /\b\d{13}\b/u.test(description),
      downloads,
    };
  }, expected);
  const labelFilename = `${expected.manufacturerCode}_EPREL_${expected.eprelId}_etykieta.jpg`;
  const ficheFilename = `${expected.manufacturerCode}_EPREL_${expected.eprelId}_karta_informacyjna.pdf`;
  const label = live.downloads.energyClassLabels;
  const fiche = live.downloads.energyTechnicalCards;
  const documentsOk = label.length === 1
    && fiche.length === 1
    && label[0].path.endsWith(`/${labelFilename}`)
    && fiche[0].path.endsWith(`/${ficheFilename}`)
    && label[0].status === 200
    && fiche[0].status === 200
    && label[0].contentType.includes("image/jpeg")
    && fiche[0].contentType.includes("pdf");
  const expectedState = expectedStateOverride || String(expected.state || expected.expectedState || "active");
  const expectedStatus = expectedState === "active" ? "active" : "new";
  const verified = live.httpStatus === 200
    && live.id === Number(expected.pimcoreId)
    && live.ean === String(expected.ean)
    && live.model === String(expected.manufacturerCode)
    && Math.abs(numeric(live.price) - Number(expected.timListPrice)) < 0.0001
    && Math.abs(numeric(live.price) - Number(expected.xmlPrice)) < 0.0001
    && live.state === expectedState
    && live.status === expectedStatus
    && live.published
    && !live.locked
    && live.energyClass === String(expected.energyClass)
    && live.descriptionHasModel
    && !live.descriptionHasEan
    && documentsOk;
  products.push({ expected, live, documentsOk, verified });
  console.log(`${expected.manufacturerCode}: ${verified ? "OK" : "BŁĄD"}`);
}

const report = {
  generatedAt: new Date().toISOString(),
  readOnly: true,
  queuePath,
  start,
  limit,
  counts: {
    total: products.length,
    verified: products.filter((item) => item.verified).length,
    failed: products.filter((item) => !item.verified).length,
    downloadableRelations: products.flatMap((item) => Object.values(item.live.downloads).flat()).filter((asset) => asset.status === 200).length,
  },
  blockedWrites,
  products,
};
await mkdir(dirname(outputPath), { recursive: true });
await writeFile(outputPath, `${JSON.stringify(report, null, 2)}\n`, "utf8");
await page.unroute("**/*", routeHandler);
console.log(JSON.stringify({ output: outputPath, counts: report.counts, blockedWrites: blockedWrites.length }, null, 2));
if (report.counts.failed || blockedWrites.length) process.exitCode = 1;
process.exit(process.exitCode || 0);
