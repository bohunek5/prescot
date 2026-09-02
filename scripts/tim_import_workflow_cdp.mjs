import { writeFile } from "node:fs/promises";
import { resolve } from "node:path";
import { chromium } from "../../radlight/node_modules/playwright/index.mjs";

function argumentValue(name, fallback = "") {
  const index = process.argv.indexOf(name);
  return index === -1 ? fallback : process.argv[index + 1] || fallback;
}

const cdpUrl = argumentValue("--cdp-url", "http://127.0.0.1:9222");
const configurationId = argumentValue("--configuration-id");
const action = argumentValue("--action", "get");
const expectedCurrentStatus = argumentValue("--expected-current-status");
const expectedNextStatus = argumentValue("--expected-next-status");
const timeoutMs = Math.max(1_000, Number(argumentValue("--timeout-ms", "90000")) || 90_000);
const outputPath = resolve(argumentValue("--output", "/tmp/tim-import-workflow-cdp.json"));
const apply = process.argv.includes("--apply");

if (!configurationId) throw new Error("Podaj --configuration-id.");
const writeActions = {
  schedule: { endpoint: "schedule", body: { headers: { Accept: "application/json" } } },
  accept_mapped_categories: { endpoint: "accept_mapped_categories", body: {} },
  confirm_categories: { endpoint: "confirm_categories", body: {} },
  accept_mapped_manufacturers: { endpoint: "accept_mapped_manufacturers", body: {} },
  confirm_manufacturers: { endpoint: "confirm_manufacturers", body: {} },
  accept_mapped_units: { endpoint: "accept_mapped_units", body: {} },
  confirm_units: { endpoint: "confirm_units", body: {} },
  confirm: { endpoint: "confirm", body: { headers: { Accept: "application/json" } } },
};
if (action !== "get" && !writeActions[action]) throw new Error(`Nieobsługiwana akcja: ${action}.`);
if (action !== "get" && !apply) throw new Error(`Akcja ${action} wymaga --apply.`);
if (action !== "get" && !expectedCurrentStatus) throw new Error("Dla zapisu podaj --expected-current-status.");

const configApi = `https://dostawca.tim.pl/api/product_import_configurations/${configurationId}`;
const pageUrl = `https://dostawca.tim.pl/produkty/import-produktow/dodawanie-schematu/ceneo/${configurationId}/weryfikacja`;
const report = {
  generatedAt: new Date().toISOString(),
  action,
  apply,
  configurationId,
  pageUrl,
  authObserved: false,
  before: null,
  write: null,
  polls: [],
  after: null,
  finalUrl: "",
  bodyText: "",
  fatalError: "",
};
const persist = () => writeFile(outputPath, `${JSON.stringify(report, null, 2)}\n`, "utf8");

let page;
try {
  const browser = await chromium.connectOverCDP(cdpUrl);
  const context = browser.contexts()[0];
  if (!context) throw new Error("Brak aktywnego kontekstu Chrome.");
  page = await context.newPage();
  let authorization = "";
  page.on("request", (request) => {
    if (request.url().startsWith("https://dostawca.tim.pl/api/")) {
      authorization = request.headers()["x-authorization"] || authorization;
    }
  });
  await page.goto(pageUrl, { waitUntil: "domcontentloaded", timeout: 45_000 });
  for (let attempt = 0; !authorization && attempt < 40; attempt += 1) await page.waitForTimeout(250);
  if (!authorization) throw new Error("Nie znaleziono autoryzacji aktywnej sesji TIM.");
  report.authObserved = true;

  const api = async (url, method = "GET", body = undefined) => page.evaluate(async ({ url, method, body, auth }) => {
    const response = await fetch(url, {
      method,
      headers: {
        Accept: "application/json",
        ...(body === undefined ? {} : { "Content-Type": "application/json" }),
        "X-Authorization": auth,
      },
      ...(body === undefined ? {} : { body: JSON.stringify(body) }),
    });
    const text = (await response.text()).slice(0, 100_000);
    let json = null;
    try { json = JSON.parse(text); } catch {}
    return { status: response.status, text, json };
  }, { url, method, body, auth: authorization });

  report.before = await api(configApi);
  if (report.before.status >= 400) throw new Error(`Odczyt schematu zwrócił HTTP ${report.before.status}.`);
  const currentStatus = report.before.json?.status || "";

  if (action !== "get") {
    if (currentStatus !== expectedCurrentStatus) {
      throw new Error(`Oczekiwano statusu ${expectedCurrentStatus}, jest ${currentStatus || "brak"}.`);
    }
    const writeAction = writeActions[action];
    report.write = await api(`${configApi}/${writeAction.endpoint}`, "POST", writeAction.body);
    if (report.write.status >= 400) throw new Error(`Akcja ${action} zwróciła HTTP ${report.write.status}.`);

    const started = Date.now();
    while (Date.now() - started < timeoutMs) {
      await page.waitForTimeout(1_500);
      const poll = await api(configApi);
      report.polls.push({ at: new Date().toISOString(), status: poll.status, configurationStatus: poll.json?.status || "" });
      report.after = poll;
      const next = poll.json?.status || "";
      if (expectedNextStatus ? next === expectedNextStatus : next !== currentStatus) break;
    }
  } else {
    report.after = report.before;
  }

  report.finalUrl = page.url();
  report.bodyText = (await page.locator("body").innerText().catch(() => "")).slice(0, 30_000);
  if (expectedNextStatus && report.after?.json?.status !== expectedNextStatus) {
    throw new Error(`Nie osiągnięto statusu ${expectedNextStatus}; jest ${report.after?.json?.status || "brak"}.`);
  }
} catch (error) {
  report.fatalError = error instanceof Error ? error.message : String(error);
} finally {
  await persist();
  await page?.close().catch(() => {});
}

console.log(JSON.stringify({
  action: report.action,
  beforeStatus: report.before?.json?.status || "",
  writeStatus: report.write?.status || 0,
  afterStatus: report.after?.json?.status || "",
  polls: report.polls.length,
  fatalError: report.fatalError,
}, null, 2));
if (report.fatalError) process.exitCode = 1;
process.exit(process.exitCode || 0);
