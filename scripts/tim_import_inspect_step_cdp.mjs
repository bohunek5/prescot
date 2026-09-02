import { writeFile } from "node:fs/promises";
import { resolve } from "node:path";
import { chromium } from "../../radlight/node_modules/playwright/index.mjs";

function argumentValue(name, fallback = "") {
  const index = process.argv.indexOf(name);
  return index === -1 ? fallback : process.argv[index + 1] || fallback;
}

const cdpUrl = argumentValue("--cdp-url", "http://127.0.0.1:9222");
const configurationId = argumentValue("--configuration-id");
const step = argumentValue("--step");
const outputPath = resolve(argumentValue("--output", "/tmp/tim-import-inspect-step-cdp.json"));
if (!configurationId || !step) throw new Error("Podaj --configuration-id i --step.");

const pageUrl = `https://dostawca.tim.pl/produkty/import-produktow/dodawanie-schematu/ceneo/${configurationId}/${step}`;
const report = {
  generatedAt: new Date().toISOString(), readOnly: true, configurationId, step, pageUrl,
  responses: [], blockedWrites: [], finalUrl: "", bodyText: "", buttons: [], fatalError: "",
};
let page;
try {
  const browser = await chromium.connectOverCDP(cdpUrl);
  const context = browser.contexts()[0];
  if (!context) throw new Error("Brak aktywnego kontekstu Chrome.");
  page = await context.newPage();
  await page.route("**/*", async (route) => {
    const request = route.request();
    if (["GET", "HEAD", "OPTIONS"].includes(request.method().toUpperCase())) return route.continue();
    report.blockedWrites.push({ method: request.method(), url: request.url(), body: request.postData() });
    return route.abort("blockedbyclient");
  });
  page.on("response", async (response) => {
    const url = response.url();
    if (!url.includes("/api/") || (!url.includes(configurationId) && !/categories|manufacturers|units/i.test(url))) return;
    report.responses.push({
      method: response.request().method(), url, status: response.status(),
      body: (await response.text().catch(() => "")).slice(0, 200_000),
    });
  });
  await page.goto(pageUrl, { waitUntil: "domcontentloaded", timeout: 45_000 });
  await page.waitForTimeout(4_000);
  report.finalUrl = page.url();
  report.bodyText = (await page.locator("body").innerText().catch(() => "")).slice(0, 50_000);
  report.buttons = await page.getByRole("button").allTextContents().catch(() => []);
} catch (error) {
  report.fatalError = error instanceof Error ? error.message : String(error);
} finally {
  await writeFile(outputPath, `${JSON.stringify(report, null, 2)}\n`, "utf8");
  await page?.close().catch(() => {});
}
console.log(JSON.stringify({ responses: report.responses.length, blockedWrites: report.blockedWrites.length, buttons: report.buttons, fatalError: report.fatalError }, null, 2));
if (report.fatalError) process.exitCode = 1;
process.exit(process.exitCode || 0);
