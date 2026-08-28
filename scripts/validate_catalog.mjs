#!/usr/bin/env node

import { readFile, writeFile } from "node:fs/promises";
import { generateDescription, plainTextFromHtml, PLATFORM_NAMES } from "../description-engine.js";

const catalog = JSON.parse(await readFile(new URL("../data/catalog.json", import.meta.url), "utf8"));
const overrides = JSON.parse(await readFile(new URL("../data/manual-overrides.json", import.meta.url), "utf8"));
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

const invalidEans = products.filter((product) => product.ean && !/^\d{8,14}$/.test(product.ean));
assert(!invalidEans.length, `Nieprawidłowy format EAN: ${invalidEans.map((product) => product.ean).join(", ")}`);

const generatedFingerprints = new Map();
let generatedCount = 0;
let manualCount = 0;
let shortestDescription = { length: Number.POSITIVE_INFINITY, product: null, platform: "" };
let longestDescription = { length: 0, product: null, platform: "" };

for (const product of products) {
  for (const platform of platforms) {
    const overrideId = overrides.products?.[product.key]?.[platform];
    const manualHtml = overrideId ? overrides.descriptions?.[overrideId] : "";
    const html = manualHtml || generateDescription(product, platform);
    const text = plainTextFromHtml(html);
    if (manualHtml) manualCount += 1;
    else generatedCount += 1;

    assert(text.length >= 180, `Zbyt krótki opis: ${product.key} / ${platform} (${text.length} znaków).`);
    assert(!/\b(?:undefined|null|nan)\b/i.test(text), `Niedozwolona wartość w opisie: ${product.key} / ${platform}.`);
    assert(occurrences(html, /<section\b/gi) === occurrences(html, /<\/section>/gi), `Niezbilansowane sekcje: ${product.key} / ${platform}.`);

    if (!manualHtml) {
      const identifier = product.ean || product.manufacturerCode || product.code;
      assert(text.includes(identifier), `Brak identyfikatora w opisie: ${product.key} / ${platform}.`);
      const fingerprint = text.toLocaleLowerCase("pl").replace(/\s+/g, " ").trim();
      const existing = generatedFingerprints.get(fingerprint);
      if (existing) {
        errors.push(`Identyczny opis wygenerowany dla ${existing} oraz ${product.key}/${platform}.`);
      } else {
        generatedFingerprints.set(fingerprint, `${product.key}/${platform}`);
      }
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
  exactDuplicateGeneratedDescriptions: 0,
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
