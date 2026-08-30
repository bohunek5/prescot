import { readFile, writeFile } from "node:fs/promises";
import { resolve } from "node:path";
import { chromium } from "../../radlight/node_modules/playwright/index.mjs";

function argumentValue(name, fallback = "") {
  const index = process.argv.indexOf(name);
  return index === -1 ? fallback : process.argv[index + 1] || fallback;
}

const profileDir = argumentValue("--profile-dir");
const auditPath = resolve(argumentValue("--audit", "exports/tim/pilots/new-products-pilot-10-audit.json"));
const outputPath = resolve(argumentValue("--output", "/tmp/tim-create-pilot-import.json"));
const importName = argumentValue("--name", "PRESCOT - PILOT 10 KONTROLOWANY 30.08.2026");
const sourceUrl = argumentValue("--source-url", "https://raw.githubusercontent.com/bohunek5/prescot/main/tim-import/pilot-10.xml");
const applyCreate = process.argv.includes("--apply");
if (!profileDir) throw new Error("Podaj --profile-dir.");
if (!applyCreate) throw new Error("Utworzenie schematu wymaga flagi --apply.");

const audit = JSON.parse(await readFile(auditPath, "utf8"));
if (audit?.counts?.built !== 10 || audit?.counts?.errors !== 0) throw new Error("Pilot lokalny nie ma dokładnie 10 poprawnych rekordów.");
const publicResponse = await fetch(sourceUrl, { redirect: "follow" });
const publicXml = await publicResponse.text();
const publicOfferCount = [...publicXml.matchAll(/^  <o id="/gm)].length;
if (!publicResponse.ok || publicOfferCount !== 10) throw new Error(`Publiczny XML nie przeszedł kontroli: HTTP ${publicResponse.status}, ofert ${publicOfferCount}.`);

const expectedPayload = {
  name: importName,
  type: "PRODUCT",
  isPeriodical: "false",
  url: sourceUrl,
};
const allowedWrites = [];
const blockedWrites = [];
const responses = [];
let fatalError = "";
const context = await chromium.launchPersistentContext(profileDir, {
  headless: true,
  executablePath: "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
  args: ["--profile-directory=Default"],
  viewport: { width: 1600, height: 1100 },
  serviceWorkers: "block",
});

await context.route("**/*", async (route) => {
  const request = route.request();
  const method = request.method().toUpperCase();
  const url = request.url();
  if (["GET", "HEAD", "OPTIONS"].includes(method)) return route.continue();
  if (method === "POST" && url === "https://dostawca.tim.pl/api/product_import_configurations/uri") {
    let payload = null;
    try { payload = JSON.parse(request.postData() || "null"); } catch {}
    const valid = JSON.stringify(payload) === JSON.stringify(expectedPayload) && allowedWrites.length === 0;
    if (valid) {
      allowedWrites.push({ method, url, payload });
      return route.continue();
    }
    blockedWrites.push({ method, url, reason: "create_guard_failed", payload });
    return route.abort("blockedbyclient");
  }
  if (!/sentry\.tim\.pl|google-analytics\.com|cdn-cgi\/rum|www\.tim\.pl\/rb_/.test(url)) {
    blockedWrites.push({ method, url, reason: "not_allowlisted" });
  }
  return route.abort("blockedbyclient");
});

const page = context.pages()[0] || await context.newPage();
page.setDefaultTimeout(10_000);
page.on("response", async (response) => {
  if (response.url() === "https://dostawca.tim.pl/api/product_import_configurations/uri") {
    responses.push({ status: response.status(), body: (await response.text().catch(() => "")).slice(0, 100_000) });
  }
});

try {
  await page.goto("https://dostawca.tim.pl/produkty/import-produktow/dodawanie-schematu/ceneo/nowy/konfiguracja", {
    waitUntil: "domcontentloaded",
    timeout: 45_000,
  });
  await page.waitForTimeout(1_800);
  await page.locator("#importName").fill(importName);
  await page.getByText("Podaj adres URL pliku", { exact: true }).click();
  await page.locator("#link").fill(sourceUrl);
  await page.getByText("Import pojedynczy produktów, cen i danych technicznych", { exact: true }).click();
  await page.getByRole("button", { name: /KONTYNUUJ/i }).click();
  await page.waitForTimeout(4_000);
} catch (error) {
  fatalError = error.message;
}

const bodyText = await page.locator("body").innerText().catch(() => "");
const report = {
  generatedAt: new Date().toISOString(),
  sourceUrl,
  publicHttpStatus: publicResponse.status,
  publicOfferCount,
  expectedPayload,
  allowedWrites,
  blockedWrites,
  responses,
  finalUrl: page.url(),
  bodyText: bodyText.slice(0, 30_000),
  fatalError,
};
await writeFile(outputPath, `${JSON.stringify(report, null, 2)}\n`, "utf8");
await context.close();
console.log(JSON.stringify({
  allowedWrites: allowedWrites.length,
  responseStatus: responses[0]?.status || 0,
  finalUrl: report.finalUrl,
  fatalError,
}, null, 2));
if (fatalError || allowedWrites.length !== 1 || responses[0]?.status >= 400) process.exitCode = 1;
