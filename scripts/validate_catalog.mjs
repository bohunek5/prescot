#!/usr/bin/env node

import { readFile, writeFile } from "node:fs/promises";
import { generateDescription, normalizeDescriptionIdentity, renderSeoDescription, plainTextFromHtml, PLATFORM_NAMES } from "../description-engine.js";

const catalog = JSON.parse(await readFile(new URL("../data/catalog.json", import.meta.url), "utf8"));
const overrides = JSON.parse(await readFile(new URL("../data/manual-overrides.json", import.meta.url), "utf8"));
const generated = JSON.parse(await readFile(new URL("../data/seo-descriptions.json", import.meta.url), "utf8"));
const errors = [];
const warnings = [];
const platforms = Object.keys(PLATFORM_NAMES);

function assert(condition, message) {
  if (!condition) errors.push(message);
}

function occurrences(value, pattern) {
  return (value.match(pattern) || []).length;
}

const products = catalog.products;
assert(products.length === catalog.meta.activeProducts, "Liczba produktów nie zgadza się z metadanymi.");
assert(new Set(products.map((product) => product.key)).size === products.length, "Klucze produktów nie są unikalne.");
assert(new Set(products.map((product) => product.id)).size === products.length, "ID produktów nie są unikalne.");
assert(products.every((product) => product.code), "Co najmniej jeden aktywny produkt nie ma kodu produktu.");
assert(Object.keys(generated.products || {}).length === products.length, "Plik SEO nie obejmuje wszystkich aktywnych produktów.");
assert(products.every((product) => generated.products?.[product.key]?.editorial), "Co najmniej jeden produkt nie ma opisu SEO po audycie.");

const invalidEans = products.filter((product) => product.ean && !/^\d{8,14}$/.test(product.ean));
assert(!invalidEans.length, `Nieprawidłowy format EAN: ${invalidEans.map((product) => product.ean).join(", ")}`);

const descriptionFingerprints = new Map();
let generatedCount = 0;
let manualCount = 0;
let shortestDescription = { length: Number.POSITIVE_INFINITY, product: null, platform: "" };
let longestDescription = { length: 0, product: null, platform: "" };
let sharedTimPurposeDescriptions = 0;

for (const product of products) {
  for (const platform of platforms) {
    const assignment = overrides.products?.[product.key];
    let overrideId = platform === "shoper" ? assignment?.wapro : assignment?.[platform];
    overrideId ||= "";
    if (platform === "shoper" && overrideId && overrides.descriptions?.[overrideId]?.includes('class="blog-grid"')) overrideId = "";
    if (["wapro", "tim"].includes(platform)) overrideId = "";
    if (platform === "allegro" && overrideId === assignment?.wapro) overrideId = "";
    const manualHtml = overrideId ? overrides.descriptions?.[overrideId] : "";
    const savedSeo = generated.products?.[product.key];
    const html = normalizeDescriptionIdentity(
      product,
      manualHtml || (savedSeo ? renderSeoDescription(product, savedSeo, platform) : generateDescription(product, platform)),
      { ensureTradeIndex: platform !== "tim" },
    );
    const text = plainTextFromHtml(html);
    if (manualHtml) manualCount += 1;
    else generatedCount += 1;

    assert(text.length >= 180, `Zbyt krótki opis: ${product.key} / ${platform} (${text.length} znaków).`);
    assert(!/\b(?:undefined|null|nan)\b/i.test(text), `Niedozwolona wartość w opisie: ${product.key} / ${platform}.`);
    assert(!/\b(?:kod produktu|kod producenta|numer katalogowy|nr katalogowy)\b/i.test(text), `Niedozwolona nazwa identyfikatora: ${product.key} / ${platform}.`);
    if (platform !== "tim") assert(new RegExp(`indeks handlowy\\s*:?\\s*${product.code.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")}`, "i").test(text), `Brak indeksu handlowego: ${product.key} / ${platform}.`);
    assert(occurrences(html, /<section\b/gi) === occurrences(html, /<\/section>/gi), `Niezbilansowane sekcje: ${product.key} / ${platform}.`);
    if (platform === "shoper") {
      assert(occurrences(html, /<section\b/gi) >= 3, `Shoper nie ma pomarańczowego układu sekcji: ${product.key}.`);
      assert(/#(?:e94b25|f04923)/i.test(html), `Shoper nie ma pomarańczowego motywu: ${product.key}.`);
    }
    if (["wapro", "tim"].includes(platform)) {
      assert(occurrences(html, /<section\b/gi) === 1, `${platform.toUpperCase()} nie ma klasycznego układu jednej sekcji: ${product.key}.`);
      assert(!/\sstyle=/i.test(html), `${platform.toUpperCase()} zawiera zbędne style prezentacyjne: ${product.key}.`);
    }
    if (platform === "tim" && product.categoryRoot === "Taśmy LED") {
      assert(/Do czego służy i gdzie użyć tej taśmy LED/i.test(text), `TIM nie ma zastosowań taśmy dla instalatora: ${product.key}.`);
    }
    if (platform === "tim") {
      assert(!/Opis dla TIM\.pl|Dane techniczne|Indeks handlowy|Producent\s*:|EAN\s*:|Dane służą do porównania wariantu/i.test(text), `TIM powtarza dane karty produktu: ${product.key}.`);
      assert(!/\b(?:napięcie|moc(?: wyjściowa)?|prąd|wymiar(?:y)?|klasa szczelności|kod(?: produktu| producenta| elementu| modułu)?|model)\s*:/i.test(text), `TIM zawiera blok parametrów zamiast porady: ${product.key}.`);
      assert(!product.ean || !text.includes(product.ean), `TIM powtarza EAN: ${product.key}.`);
      if (product.code.length >= 5) assert(!text.toLocaleLowerCase("pl").includes(product.code.toLocaleLowerCase("pl")), `TIM powtarza indeks handlowy bez etykiety: ${product.key}.`);
      assert(/Wskazówki dla instalatora/i.test(text), `TIM nie ma porad dla instalatora: ${product.key}.`);
      assert(occurrences(html, /<h2\b/gi) === 1 && occurrences(html, /<h3\b/gi) === 1, `TIM ma więcej niż dwa bloki treści: ${product.key}.`);
      const timLists = [...html.matchAll(/<ul>(.*?)<\/ul>/gis)].map((match) => occurrences(match[1], /<li\b/gi));
      assert(timLists.length === 2 && timLists[0] >= 2, `TIM nie ma dwóch konkretnych zastosowań: ${product.key}.`);
      assert(timLists[1] >= 3, `TIM nie ma co najmniej trzech porad montażowych: ${product.key}.`);
    }

    const fingerprint = text.toLocaleLowerCase("pl").replace(/\s+/g, " ").trim();
    const existing = descriptionFingerprints.get(fingerprint);
    if (existing) {
      if (platform === "tim" && existing.platform === "tim") {
        // Różne warianty handlowe mogą mieć identyczne zastosowanie i zalecenia
        // montażowe. TIM celowo nie dostaje sztucznych synonimów ani identyfikatorów.
        sharedTimPurposeDescriptions += 1;
      } else {
        errors.push(`Identyczny opis dla ${existing.label} oraz ${product.key}/${platform}.`);
      }
    } else {
      descriptionFingerprints.set(fingerprint, { label: `${product.key}/${platform}`, platform });
    }

    if (!manualHtml) {
      const identifier = product.ean || product.code;
      if (platform !== "tim") assert(text.includes(identifier), `Brak identyfikatora w opisie: ${product.key} / ${platform}.`);
      const name = product.name.toLocaleLowerCase("pl");
      if ((name.includes("bez led") || name.includes("bez źródła")) && /zawiera źródło światła|ze źródłem światła/i.test(text)) {
        errors.push(`Sprzeczność „bez LED” w opisie ${product.key}/${platform}.`);
      }
      if (name.includes("bez zasilacza") && /zasilacz (?:jest |w )?komplecie|zawiera zasilacz/i.test(text)) {
        errors.push(`Sprzeczność „bez zasilacza” w opisie ${product.key}/${platform}.`);
      }
    }

    if (text.length < shortestDescription.length) shortestDescription = { length: text.length, product: product.key, platform };
    if (text.length > longestDescription.length) longestDescription = { length: text.length, product: product.key, platform };
  }
}

const assignedOverrideIds = new Set(
  Object.values(overrides.products || {}).flatMap((assignment) => Object.values(assignment)),
);
const orphanOverrides = Object.keys(overrides.descriptions || {}).filter((id) => !assignedOverrideIds.has(id));
if (orphanOverrides.length) warnings.push(`${orphanOverrides.length} ręcznych opisów nie ma przypisania do aktywnego produktu.`);

const report = {
  checkedAt: new Date().toISOString(),
  activeProducts: products.length,
  platforms: platforms.length,
  totalDescriptions: products.length * platforms.length,
  generatedDescriptions: generatedCount,
  manualDescriptions: manualCount,
  exactDuplicateDescriptions: sharedTimPurposeDescriptions,
  exactDuplicateGeneratedDescriptions: sharedTimPurposeDescriptions,
  sharedTimPurposeDescriptions,
  productsWithEan: products.filter((product) => product.ean).length,
  productsWithoutEan: products.filter((product) => !product.ean).length,
  shortestDescription,
  longestDescription,
  warnings,
  errors,
};

if (process.argv.includes("--write")) {
  await writeFile(new URL("../data/quality-report.json", import.meta.url), JSON.stringify(report, null, 2) + "\n", "utf8");
}

console.log(`Produkty: ${report.activeProducts}`);
console.log(`Opisy sprawdzone: ${report.totalDescriptions}`);
console.log(`Ręczne: ${report.manualDescriptions}; wygenerowane: ${report.generatedDescriptions}`);
console.log(`Najkrótszy opis: ${shortestDescription.length} znaków (${shortestDescription.product}/${shortestDescription.platform})`);
console.log(`Najdłuższy opis: ${longestDescription.length} znaków (${longestDescription.product}/${longestDescription.platform})`);
if (warnings.length) warnings.forEach((warning) => console.warn(`OSTRZEŻENIE: ${warning}`));
if (errors.length) {
  errors.slice(0, 40).forEach((error) => console.error(`BŁĄD: ${error}`));
  if (errors.length > 40) console.error(`…oraz ${errors.length - 40} kolejnych błędów.`);
  process.exitCode = 1;
} else {
  console.log("Walidacja zakończona bez błędów.");
}
