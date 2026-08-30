import { mkdir, readFile, writeFile } from "node:fs/promises";
import { dirname, resolve } from "node:path";
import { chromium } from "../../radlight/node_modules/playwright/index.mjs";

function argumentValue(name, fallback = "") {
  const index = process.argv.indexOf(name);
  return index === -1 ? fallback : process.argv[index + 1] || fallback;
}

const profileDir = argumentValue("--profile-dir");
const treePath = resolve(argumentValue("--tree", "/tmp/tim-live-main-catalog-complete.json"));
const outputPath = resolve(argumentValue("--output", "/tmp/tim-pimcore-inventory-snapshot.json"));
const concurrency = Math.min(80, Math.max(1, Number(argumentValue("--concurrency", "8")) || 8));
const directFetch = process.argv.includes("--direct-fetch");

if (!profileDir) throw new Error("Podaj --profile-dir.");

const treeDocument = JSON.parse(await readFile(treePath, "utf8"));
const ids = [...new Set((treeDocument?.pimcoreTree?.nodes || [])
  .filter((node) => node?.className === "product" && Number(node.id) > 0)
  .map((node) => Number(node.id)))];
if (!ids.length) throw new Error(`Brak kart produktów w ${treePath}.`);

const context = await chromium.launchPersistentContext(profileDir, {
  headless: true,
  executablePath: "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
  args: ["--profile-directory=Default"],
  serviceWorkers: "block",
});

const blockedWrites = [];
await context.route("**/*", async (route) => {
  const method = route.request().method().toUpperCase();
  if (["GET", "HEAD", "OPTIONS"].includes(method)) return route.continue();
  const url = route.request().url();
  if (method === "POST" && [
    "https://dostawca.tim.pl/pimcore/api/authenticate-user-by-token",
    "https://dostawca.tim.pl/pimcore/api/verify-session",
  ].includes(url)) return route.continue();
  if (!/cdn-cgi\/rum|liveupdate\.pimcore\.org\/update-check/.test(url)) blockedWrites.push({ method, url });
  return route.abort("blockedbyclient");
});

const page = context.pages()[0] || await context.newPage();
await page.goto("https://dostawca.tim.pl/pimcore/", { waitUntil: "domcontentloaded", timeout: 45_000 });
let frame = page.frames().find((item) => item.url().includes("/pimcore/admin/"));
for (let attempt = 0; !frame && attempt < 15; attempt += 1) {
  await page.waitForTimeout(1_000);
  frame = page.frames().find((item) => item.url().includes("/pimcore/admin/"));
}
if (!frame) throw new Error("Nie znaleziono ramki PIMCORE.");
await page.waitForTimeout(3_000);

const browserCookies = await context.cookies(["https://dostawca.tim.pl/"]);
const cookieHeader = browserCookies.map((cookie) => `${cookie.name}=${cookie.value}`).join("; ");
const userAgent = await page.evaluate(() => navigator.userAgent);

function summarizeObject(id, responseStatus, payload, error = "") {
  if (error) return { id, httpStatus: responseStatus, error };
  const data = payload?.data || {};
  const stock = Math.max(0, ...(data.stockLevel || []).map((entry) => Number(entry.stockTotalQuantityMz) || 0));
  return {
    id,
    httpStatus: responseStatus,
    general: {
      key: payload?.general?.key || "",
      fullpath: payload?.general?.fullpath || "",
      published: Boolean(payload?.general?.published),
      locked: Boolean(payload?.general?.locked),
      versionCount: payload?.general?.versionCount ?? null,
    },
    ean: String(data.ean || "").trim(),
    manufacturerIndex: String(data.manufacturerIndex || "").trim(),
    timIndex: String(data.timIndex || "").trim(),
    timName: String(data.timName || "").trim(),
    state: data.state?.value || data.state || "",
    status: data.status?.value || data.status || "",
    stock,
    productAvailableForSale: data.productAvailableForSale?.value || data.productAvailableForSale || "",
    descriptionHtml: String(data.productDescriptions?.data?.longMarketingDescription || ""),
  };
}

async function fetchDirect(id) {
  try {
    const response = await fetch(`https://dostawca.tim.pl/pimcore/admin/object/get?id=${id}`, {
      headers: {
        Accept: "application/json, text/plain, */*",
        Cookie: cookieHeader,
        Referer: "https://dostawca.tim.pl/pimcore/admin/",
        "User-Agent": userAgent,
      },
    });
    let payload = null;
    try { payload = await response.json(); } catch {}
    return summarizeObject(id, response.status, payload);
  } catch (error) {
    return summarizeObject(id, 0, null, error.message);
  }
}

const products = [];
for (let start = 0; start < ids.length; start += concurrency) {
  const batch = ids.slice(start, start + concurrency);
  const result = directFetch
    ? await Promise.all(batch.map(fetchDirect))
    : await frame.evaluate(async (objectIds) => Promise.all(objectIds.map(async (id) => {
    try {
      const response = await fetch(`/pimcore/admin/object/get?id=${id}`, { credentials: "same-origin" });
      let payload = null;
      try { payload = await response.json(); } catch {}
      const data = payload?.data || {};
      const stock = Math.max(0, ...(data.stockLevel || []).map((entry) => Number(entry.stockTotalQuantityMz) || 0));
      return {
        id,
        httpStatus: response.status,
        general: {
          key: payload?.general?.key || "",
          fullpath: payload?.general?.fullpath || "",
          published: Boolean(payload?.general?.published),
          locked: Boolean(payload?.general?.locked),
          versionCount: payload?.general?.versionCount ?? null,
        },
        ean: String(data.ean || "").trim(),
        manufacturerIndex: String(data.manufacturerIndex || "").trim(),
        timIndex: String(data.timIndex || "").trim(),
        timName: String(data.timName || "").trim(),
        state: data.state?.value || data.state || "",
        status: data.status?.value || data.status || "",
        stock,
        productAvailableForSale: data.productAvailableForSale?.value || data.productAvailableForSale || "",
        descriptionHtml: String(data.productDescriptions?.data?.longMarketingDescription || ""),
      };
    } catch (error) {
      return { id, httpStatus: 0, error: error.message };
    }
    })), batch);
  products.push(...result);
  if (products.length % 200 < concurrency || products.length === ids.length) {
    console.log(`Odczytano ${products.length}/${ids.length}`);
  }
}

const report = {
  generatedAt: new Date().toISOString(),
  sourceTree: treePath,
  readOnly: true,
  counts: {
    requested: ids.length,
    read: products.filter((item) => item.httpStatus === 200).length,
    failed: products.filter((item) => item.httpStatus !== 200).length,
    active: products.filter((item) => item.state === "active").length,
    activePositive: products.filter((item) => item.state === "active" && item.stock > 0).length,
  },
  blockedWrites,
  products,
};

await mkdir(dirname(outputPath), { recursive: true });
await writeFile(outputPath, `${JSON.stringify(report, null, 2)}\n`, "utf8");
await context.close();
console.log(JSON.stringify(report.counts));
console.log(`Raport: ${outputPath}`);
