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
assert.equal(await page.locator(".description-preview > section").count(), 1);
assert.match(await page.locator(".description-preview").innerText(), /S-shape/i);
assert.match(await page.locator(".parameter-label").innerText(), /^atrybuty$/i);
await page.screenshot({ path: "/tmp/prescot-s-shape-wapro.png", fullPage: true });

await page.locator('[data-platform="shoper"]').click();
await page.locator(".product-trigger").click();
assert.equal(await page.locator(".description-preview > section").count(), 4);
assert.match(await page.locator(".description-preview").innerText(), /3000K/i);
assert.match(await page.locator(".description-preview").innerText(), /1000\s*lm\/m/i);
assert.equal(await page.locator(".parameter-section").count(), 0);
await page.screenshot({ path: "/tmp/prescot-s-shape.png", fullPage: true });

await page.locator('[data-platform="tim"]').click();
await page.locator(".product-trigger").click();
assert.equal(await page.locator(".description-preview > section").count(), 1);
const sShapeTimText = await page.locator(".description-preview").innerText();
assert.match(sShapeTimText, /Do czego służy i gdzie użyć:\s*Taśma LED Premium S-Shape/i);
assert.match(sShapeTimText, /Wskazówki przy instalacji modelu:\s*EF018-050-6-WW/i);
assert.doesNotMatch(sShapeTimText, /Opis dla TIM\.pl|Dane techniczne|Indeks handlowy|Producent\s*:|EAN\s*:/i);
assert.equal(await page.locator(".parameter-section").count(), 0);
await page.screenshot({ path: "/tmp/prescot-s-shape-tim.png", fullPage: true });

await page.locator("#search-input").fill("5905475368349");
await page.waitForTimeout(260);
await page.locator(".product-trigger").click();
const wcobTimText = await page.locator(".description-preview").innerText();
assert.match(await page.locator(".product-trigger").innerText(), /Taś000753/i);
assert.match(wcobTimText, /Wskazówki przy instalacji modelu:\s*Taś000753/i);
assert.doesNotMatch(wcobTimText, /24WCOB320WW5IP62/i);
assert.doesNotMatch(wcobTimText, /Opis dla TIM\.pl|Dane techniczne|Indeks handlowy|Producent\s*:|EAN\s*:|kod producenta|kod produktu|numer katalogowy/i);
assert.equal(await page.locator(".parameter-section").count(), 0);

await page.locator("#search-input").fill("5901885261386");
await page.waitForTimeout(260);
await page.locator(".product-trigger").click();
const economicBlueTimText = await page.locator(".description-preview").innerText();
assert.match(economicBlueTimText, /podświetlenia ekspozycyjne i oznaczenia w kolorze niebieskim/i);
assert.match(economicBlueTimText, /Dziel taśmę wyłącznie w oznaczonych miejscach/i);
assert.match(economicBlueTimText, /Do czego służy i gdzie użyć:\s*Taśma Economic IP63 12V 60led niebieska SMD2835 \(5\)/i);
assert.match(economicBlueTimText, /Wskazówki przy instalacji modelu:\s*EH007-050-8-B/i);
assert.doesNotMatch(economicBlueTimText, /5901885261386|Opis dla TIM\.pl|Dane techniczne|Indeks handlowy|Producent\s*:|EAN\s*:/i);
assert.equal(await page.locator(".description-preview h2").count(), 1);
assert.equal(await page.locator(".description-preview h3").count(), 1);
await page.screenshot({ path: "/tmp/prescot-economic-blue-tim.png", fullPage: true });

assert.deepEqual(consoleErrors, []);
console.log("UI: 4 platformy, 6 rodzin, WAPRO domyślne.");
console.log("EAN: wyszukiwanie zwraca dokładnie jeden aktywny produkt.");
console.log("S-Shape: WAPRO klasyczny; Shoper 4 pomarańczowe sekcje bez dodatkowych atrybutów; TIM czysty użytkowy HTML.");
console.log("TIM: nazwa artykułu w nagłówku zastosowania i indeks handlowy w nagłówku porad; bez tabeli danych.");
console.log("EH007: zastosowanie niebieskiej taśmy i porady montażowe z indeksem handlowym.");
console.log("Konsola przeglądarki: 0 błędów.");

await browser.close();
