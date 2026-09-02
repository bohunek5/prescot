import { createHash } from "node:crypto";
import { readFile, writeFile } from "node:fs/promises";
import { resolve } from "node:path";
import { chromium } from "../../radlight/node_modules/playwright/index.mjs";

function argumentValue(name, fallback = "") {
  const index = process.argv.indexOf(name);
  return index === -1 ? fallback : process.argv[index + 1] || fallback;
}

const cdpUrl = argumentValue("--cdp-url", "http://127.0.0.1:9222");
const auditPath = resolve(argumentValue("--audit"));
const outputPath = resolve(argumentValue("--output", "/tmp/tim-create-controlled-import-cdp.json"));
const importName = argumentValue("--name");
const sourceUrl = argumentValue("--source-url");
const expectedCount = Number(argumentValue("--expected-count", "0"));
const apply = process.argv.includes("--apply");

if (!auditPath || !importName || !sourceUrl || !Number.isInteger(expectedCount) || expectedCount < 1) {
  throw new Error("Podaj --audit, --name, --source-url i dodatnie --expected-count.");
}
if (!apply) throw new Error("Utworzenie schematu wymaga flagi --apply.");

const audit = JSON.parse(await readFile(auditPath, "utf8"));
if (Number(audit?.counts?.built) !== expectedCount || Number(audit?.counts?.errors) !== 0) {
  throw new Error(`Audyt lokalny nie ma ${expectedCount} poprawnych rekordów.`);
}

const publicResponse = await fetch(sourceUrl, { redirect: "follow", cache: "no-store" });
const publicXml = await publicResponse.text();
const publicOfferCount = [...publicXml.matchAll(/<o\s+id=/g)].length;
if (!publicResponse.ok || publicOfferCount !== expectedCount) {
  throw new Error(`Publiczny XML nie przeszedł kontroli: HTTP ${publicResponse.status}, ofert ${publicOfferCount}.`);
}

const expectedPayload = {
  name: importName,
  type: "PRODUCT",
  isPeriodical: "false",
  url: sourceUrl,
};
const report = {
  generatedAt: new Date().toISOString(),
  apply,
  cdpUrl,
  sourceUrl,
  publicHttpStatus: publicResponse.status,
  publicOfferCount,
  publicSha256: createHash("sha256").update(publicXml).digest("hex"),
  auditPath,
  expectedPayload,
  authObserved: false,
  response: null,
  finalUrl: "",
  bodyText: "",
  fatalError: "",
};
const persist = () => writeFile(outputPath, `${JSON.stringify(report, null, 2)}\n`, "utf8");

let browser;
let page;
try {
  browser = await chromium.connectOverCDP(cdpUrl);
  const context = browser.contexts()[0];
  if (!context) throw new Error("Brak aktywnego kontekstu Chrome.");
  page = await context.newPage();
  let authorization = "";
  page.on("request", (request) => {
    if (request.url().startsWith("https://dostawca.tim.pl/api/")) {
      authorization = request.headers()["x-authorization"] || authorization;
    }
  });
  await page.goto("https://dostawca.tim.pl/produkty/import-produktow", {
    waitUntil: "domcontentloaded",
    timeout: 45_000,
  });
  for (let attempt = 0; !authorization && attempt < 40; attempt += 1) {
    await page.waitForTimeout(250);
  }
  if (!authorization) throw new Error("Nie znaleziono autoryzacji aktywnej sesji TIM.");
  report.authObserved = true;

  report.response = await page.evaluate(async ({ payload, auth }) => {
    const response = await fetch("https://dostawca.tim.pl/api/product_import_configurations/uri", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-Authorization": auth,
      },
      body: JSON.stringify(payload),
    });
    return { status: response.status, body: (await response.text()).slice(0, 100_000) };
  }, { payload: expectedPayload, auth: authorization });

  report.finalUrl = page.url();
  report.bodyText = (await page.locator("body").innerText().catch(() => "")).slice(0, 30_000);
  if (report.response.status >= 400) {
    throw new Error(`TIM zwrócił HTTP ${report.response.status} przy tworzeniu schematu.`);
  }
} catch (error) {
  report.fatalError = error instanceof Error ? error.message : String(error);
} finally {
  await persist();
  await page?.close().catch(() => {});
}

console.log(JSON.stringify({
  publicOfferCount: report.publicOfferCount,
  authObserved: report.authObserved,
  responseStatus: report.response?.status || 0,
  responseBody: report.response?.body || "",
  fatalError: report.fatalError,
}, null, 2));
if (report.fatalError || report.response?.status >= 400 || !report.response) process.exitCode = 1;
process.exit(process.exitCode || 0);
