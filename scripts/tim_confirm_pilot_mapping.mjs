import { writeFile } from "node:fs/promises";
import { resolve } from "node:path";
import { chromium } from "../../radlight/node_modules/playwright/index.mjs";

function argumentValue(name, fallback = "") {
  const index = process.argv.indexOf(name);
  return index === -1 ? fallback : process.argv[index + 1] || fallback;
}

const profileDir = argumentValue("--profile-dir");
const configurationId = argumentValue("--configuration-id");
const step = argumentValue("--step");
const buttonName = argumentValue("--button");
const endpoint = argumentValue("--endpoint");
const bodyMode = argumentValue("--body-mode", "empty-object");
const expectedCurrentStatus = argumentValue("--expected-current-status");
const expectedNextStatus = argumentValue("--expected-next-status");
const outputPath = resolve(argumentValue("--output", "/tmp/tim-confirm-pilot-mapping.json"));
if (![profileDir, configurationId, step, buttonName, endpoint, expectedCurrentStatus, expectedNextStatus].every(Boolean)) {
  throw new Error("Brakuje wymaganych argumentów potwierdzenia mapowania.");
}
if (!process.argv.includes("--apply")) throw new Error("Potwierdzenie mapowania wymaga --apply.");

const pageUrl = `https://dostawca.tim.pl/produkty/import-produktow/dodawanie-schematu/ceneo/${configurationId}/${step}`;
const configApi = `https://dostawca.tim.pl/api/product_import_configurations/${configurationId}`;
const writeApi = `${configApi}/${endpoint}`;
const expectedBody = bodyMode === "transition"
  ? JSON.stringify({ headers: { Accept: "application/json" } })
  : "{}";
const allowedWrites = [];
const blockedWrites = [];
const apiResponses = [];
let currentStatus = "";
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
  if (method === "POST" && url === writeApi && request.postData() === expectedBody && currentStatus === expectedCurrentStatus && allowedWrites.length === 0) {
    allowedWrites.push({ method, url, body: expectedBody, guardedCurrentStatus: currentStatus });
    return route.continue();
  }
  if (!/sentry\.tim\.pl|google-analytics\.com|cdn-cgi\/rum|www\.tim\.pl\/rb_/.test(url)) {
    blockedWrites.push({ method, url, body: request.postData(), reason: "not_allowlisted_or_guard_failed" });
  }
  return route.abort("blockedbyclient");
});
const page = context.pages()[0] || await context.newPage();
page.setDefaultTimeout(10_000);
page.on("response", async (response) => {
  if (response.url() === configApi || response.url() === writeApi) {
    const body = (await response.text().catch(() => "")).slice(0, 100_000);
    apiResponses.push({ url: response.url(), status: response.status(), body });
    if (response.url() === configApi) {
      try { currentStatus = JSON.parse(body).status || currentStatus; } catch {}
    }
  }
});
await page.goto(pageUrl, { waitUntil: "domcontentloaded", timeout: 45_000 });
for (let attempt = 0; !currentStatus && attempt < 20; attempt += 1) await page.waitForTimeout(250);
if (currentStatus !== expectedCurrentStatus) throw new Error(`Nieprawidłowy status przed zapisem: ${currentStatus || "brak"}.`);
await page.getByRole("button", { name: new RegExp(buttonName, "i") }).click();
await page.waitForTimeout(2_500);
let nextStatus = "";
for (const response of [...apiResponses].reverse()) {
  try {
    const status = JSON.parse(response.body).status;
    if (status) { nextStatus = status; break; }
  } catch {}
}
const report = {
  generatedAt: new Date().toISOString(), configurationId, pageUrl, expectedCurrentStatus, expectedNextStatus,
  currentStatus, nextStatus, allowedWrites, blockedWrites, apiResponses, finalUrl: page.url(),
  bodyText: (await page.locator("body").innerText().catch(() => "")).slice(0, 30_000),
};
await writeFile(outputPath, `${JSON.stringify(report, null, 2)}\n`, "utf8");
await context.close();
console.log(JSON.stringify({ currentStatus, nextStatus, allowedWrites: allowedWrites.length }, null, 2));
if (allowedWrites.length !== 1 || nextStatus !== expectedNextStatus) process.exitCode = 1;
