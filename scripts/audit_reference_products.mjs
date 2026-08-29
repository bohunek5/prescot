import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import { generateDescription, renderSeoDescription, plainTextFromHtml } from "../description-engine.js";

const catalog = JSON.parse(await readFile(new URL("../data/catalog.json", import.meta.url), "utf8"));
const overrides = JSON.parse(await readFile(new URL("../data/manual-overrides.json", import.meta.url), "utf8"));
const generated = JSON.parse(await readFile(new URL("../data/seo-descriptions.json", import.meta.url), "utf8"));
const platforms = ["wapro", "tim", "allegro", "shoper"];

function countSections(html) {
  return (html.match(/<section\b/gi) || []).length;
}

function resolve(product, platform) {
  const assignment = overrides.products?.[product.key];
  let id = platform === "shoper" ? assignment?.wapro : assignment?.[platform];
  id ||= "";
  if (platform === "shoper" && id && overrides.descriptions?.[id]?.includes('class="blog-grid"')) id = "";
  if (["wapro", "tim"].includes(platform)) id = "";
  if (platform === "allegro" && id === assignment?.wapro) id = "";
  return (id && overrides.descriptions?.[id]) || renderSeoDescription(product, generated.products?.[product.key], platform) || generateDescription(product, platform);
}

const references = [
  ["5901885264851", "S-Shape", ["S-Shape", "3000K", "1000 lm/m", "Praktyczne poradniki"]],
  ["5905475367663", "COB 48V", ["48V", "4000K", "800lm/m", "Praktyczne poradniki"]],
  ["5905475368349", "WCOB", ["WCOB", "3000K", "IP62", "Parametry i montaż"]],
  ["5999863091193", "Scharfer", ["SCH-400-24", "400W", "24V", "Praktyczne poradniki"]],
  ["5905475368073", "PR-MAD", ["PR-MAD36-1224", "36W", "12V/24V", "Praktyczne poradniki"]],
  ["5905475368004", "Sterownik touch 12A", ["PR-CCT-12A", "CCT", "12A", "Praktyczne poradniki"]],
  ["5905475363603", "Złączka FC8", ["bezlutowa", "8mm", "ZŁĄCZKA", "PORADNIKI"]],
];

for (const [ean, label, markers] of references) {
  const product = catalog.products.find((item) => item.ean === ean);
  assert.ok(product, `${label}: brak aktywnego produktu o EAN ${ean}`);
  const descriptions = Object.fromEntries(platforms.map((platform) => [platform, resolve(product, platform)]));
  const fingerprints = new Set(platforms.map((platform) => plainTextFromHtml(descriptions[platform]).toLocaleLowerCase("pl")));
  assert.equal(fingerprints.size, 4, `${label}: kanały nie są unikatowe`);
  assert.ok(countSections(descriptions.shoper) >= 4, `${label}: Shoper nie ma rodzinnego układu kart`);
  assert.equal(countSections(descriptions.wapro), 1, `${label}: WAPRO nie zachował klasycznego układu`);
  assert.equal(countSections(descriptions.tim), 1, `${label}: TIM nie ma czystego układu technicznego`);
  const shoperText = plainTextFromHtml(descriptions.shoper);
  for (const marker of markers) assert.ok(shoperText.toLocaleLowerCase("pl").includes(marker.toLocaleLowerCase("pl")), `${label}: brak „${marker}” w Shoperze`);
  assert.ok(!descriptions.shoper.includes('class="blog-grid"'), `${label}: wykryto drugi, doklejony blog`);
  assert.ok(!/\sstyle=/i.test(descriptions.wapro), `${label}: WAPRO zawiera style prezentacyjne`);
  assert.ok(!/\sstyle=/i.test(descriptions.tim), `${label}: TIM zawiera style prezentacyjne`);
  console.log(`${label}: Shoper ${countSections(descriptions.shoper)} karty; WAPRO ${countSections(descriptions.wapro)} sekcja; TIM ${countSections(descriptions.tim)} sekcja; 4 unikatowe kanały.`);
}

const sShape = catalog.products.find((item) => item.ean === "5901885264851");
const sShapeText = plainTextFromHtml(resolve(sShape, "shoper"));
assert.match(sShapeText, /1000\s*lm\/m/i);
assert.doesNotMatch(sShapeText, /900\s*lm\/m/i);

const wcob = catalog.products.find((item) => item.ean === "5905475368349");
const wcobSections = resolve(wcob, "shoper").match(/<section\b[\s\S]*?<\/section>/gi) || [];
assert.ok(wcobSections.length >= 4);
assert.doesNotMatch(plainTextFromHtml(wcobSections[2]), /3000\s*K/i, "WCOB: trzecia karta powtarza barwę");

assert.equal(Object.keys(generated.products || {}).length, catalog.meta.activeProducts);
assert.equal(Object.keys(generated.failures || {}).length, 0);
console.log(`Pokrycie: ${catalog.meta.activeProducts} aktywnych produktów, 0 odrzuconych generatora.`);
