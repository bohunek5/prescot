import { writeFile } from "node:fs/promises";
import { resolve } from "node:path";
import { chromium } from "../../radlight/node_modules/playwright/index.mjs";

function argumentValue(name, fallback = "") {
  const index = process.argv.indexOf(name);
  return index === -1 ? fallback : process.argv[index + 1] || fallback;
}

const profileDir = argumentValue("--profile-dir");
const configurationId = argumentValue("--configuration-id");
const outputPath = resolve(argumentValue("--output", "/tmp/tim-schedule-pilot-validation.json"));
if (!profileDir || !configurationId) throw new Error("Podaj --profile-dir i --configuration-id.");
if (!process.argv.includes("--apply")) throw new Error("Uruchomienie walidacji wymaga --apply.");

const configApi = `https://dostawca.tim.pl/api/product_import_configurations/${configurationId}`;
const scheduleApi = `${configApi}/schedule`;
const verificationUrl = `https://dostawca.tim.pl/produkty/import-produktow/dodawanie-schematu/ceneo/${configurationId}/weryfikacja`;
const allowedWrites = [];
const blockedWrites = [];
let authorization = "";
const expectedBody = JSON.stringify({ headers: { Accept: "application/json" } });

const context = await chromium.launchPersistentContext(profileDir, {
  headless: true,
  executablePath: "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
  args: ["--profile-directory=Default"],
  serviceWorkers: "block",
});
await context.route("**/*", async (route) => {
  const request = route.request();
  const method = request.method().toUpperCase();
  const url = request.url();
  if (["GET", "HEAD", "OPTIONS"].includes(method)) return route.continue();
  if (method === "POST" && url === scheduleApi && request.postData() === expectedBody && allowedWrites.length === 0) {
    allowedWrites.push({ method, url });
    return route.continue();
  }
  if (!/sentry\.tim\.pl|google-analytics\.com|cdn-cgi\/rum|www\.tim\.pl\/rb_/.test(url)) {
    blockedWrites.push({ method, url, reason: "not_allowlisted" });
  }
  return route.abort("blockedbyclient");
});
const page = context.pages()[0] || await context.newPage();
page.on("request", (request) => {
  if (request.url() === configApi) authorization = request.headers()["x-authorization"] || authorization;
});
await page.goto(verificationUrl, { waitUntil: "domcontentloaded", timeout: 45_000 });
for (let attempt = 0; !authorization && attempt < 20; attempt += 1) await page.waitForTimeout(250);
if (!authorization) throw new Error("Nie znaleziono nagłówka autoryzacji aktywnej sesji.");
const response = await page.evaluate(async ({ url, auth }) => {
  const result = await fetch(url, {
    method: "POST",
    headers: { "X-Authorization": auth, "Content-Type": "application/json" },
    body: JSON.stringify({ headers: { Accept: "application/json" } }),
  });
  return { status: result.status, body: (await result.text()).slice(0, 100_000) };
}, { url: scheduleApi, auth: authorization });
await page.waitForTimeout(2_500);
const report = {
  generatedAt: new Date().toISOString(),
  configurationId,
  verificationUrl,
  allowedWrites,
  blockedWrites,
  response,
  finalUrl: page.url(),
  bodyText: (await page.locator("body").innerText().catch(() => "")).slice(0, 30_000),
};
await writeFile(outputPath, `${JSON.stringify(report, null, 2)}\n`, "utf8");
await context.close();
console.log(JSON.stringify({ allowedWrites: allowedWrites.length, responseStatus: response.status }, null, 2));
if (allowedWrites.length !== 1 || response.status >= 400) process.exitCode = 1;
