import assert from "node:assert/strict";
import { chromium } from "../../radlight/node_modules/playwright/index.mjs";

const browser = await chromium.launch({
  headless: true,
  executablePath: "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
});
const page = await browser.newPage({ viewport: { width: 1888, height: 1333 }, deviceScaleFactor: 1 });
const consoleErrors = [];
page.on("console", (message) => {
  if (message.type() === "error") consoleErrors.push(message.text());
});
page.on("pageerror", (error) => consoleErrors.push(error.message));

await page.goto("http://127.0.0.1:8765/", { waitUntil: "networkidle" });
await page.locator("#app").waitFor({ state: "visible" });

assert.match(await page.locator("#cloud-state").innerText(), /3[\s.]?410 aktywnych produktów/);
assert.equal(await page.locator(".main-tab-btn").count(), 4);
assert.equal(await page.locator(".family-tab").count(), 6);
assert.equal(await page.locator('[data-platform="wapro"]').getAttribute("aria-pressed"), "true");
await page.screenshot({ path: "/tmp/prescot-panel.png", fullPage: false });

async function searchAndOpen(ean) {
  const search = page.locator("#search-input");
  await search.fill(ean);
  await page.waitForTimeout(260);
  assert.equal(await page.locator(".product-accordion").count(), 1, `EAN ${ean} powinien wskazać jeden produkt`);
  await page.locator(".product-trigger").click();
  await page.locator(".product-body").waitFor({ state: "visible" });
}

await searchAndOpen("5901885264851");
assert.equal(await page.locator(".description-preview > section").count(), 4);
assert.match(await page.locator(".description-preview").innerText(), /S-shape/i);
assert.match(await page.locator(".description-preview").innerText(), /3000K/i);
assert.match(await page.locator(".description-preview").innerText(), /1000\s*lm\/m/i);
await page.screenshot({ path: "/tmp/prescot-s-shape.png", fullPage: true });

await page.locator('[data-platform="shoper"]').click();
await page.locator(".product-trigger").click();
assert.equal(await page.locator(".description-preview > section").count(), 1);
assert.match(await page.locator(".description-preview").innerText(), /Najważniejsze cechy|Premium S-shape/i);

await page.locator('[data-platform="tim"]').click();
await page.locator(".product-trigger").click();
assert.ok(await page.locator(".description-preview > section").count() >= 4);
assert.match(await page.locator(".description-preview").innerText(), /Parametry|dane do doboru/i);

assert.deepEqual(consoleErrors, []);
console.log("UI: 4 platformy, 6 rodzin, WAPRO domyślne.");
console.log("EAN: wyszukiwanie zwraca dokładnie jeden aktywny produkt.");
console.log("S-Shape: WAPRO 4 sekcje; Shoper układ prosty; TIM układ techniczny.");
console.log("Konsola przeglądarki: 0 błędów.");

await browser.close();
