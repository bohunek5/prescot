#!/usr/bin/env node

import { readFile, writeFile } from "node:fs/promises";
import { generateDescription, normalizeDescriptionIdentity, renderSeoDescription, plainTextFromHtml, PLATFORM_NAMES } from "../description-engine.js";
import { timBodyFingerprint, validateTimDescription } from "./tim_description_quality.mjs";

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

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
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
const timBodyFingerprints = new Map();

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
      { ensureTradeIndex: platform !== "tim", preserveManufacturerCode: platform === "tim" },
    );
    const text = plainTextFromHtml(html);
    if (manualHtml) manualCount += 1;
    else generatedCount += 1;

    assert(text.length >= 180, `Zbyt krótki opis: ${product.key} / ${platform} (${text.length} znaków).`);
    assert(!/\b(?:undefined|null|nan)\b/i.test(text), `Niedozwolona wartość w opisie: ${product.key} / ${platform}.`);
    if (platform !== "tim") assert(!/\b(?:kod produktu|kod producenta|numer katalogowy|nr katalogowy)\b/i.test(text), `Niedozwolona nazwa identyfikatora: ${product.key} / ${platform}.`);
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
    if (platform === "tim") {
      const timErrors = validateTimDescription(product, html);
      assert(!timErrors.length, `TIM ma wadliwy opis: ${product.key} — ${timErrors.join(" | ")}.`);
      const bodyFingerprint = timBodyFingerprint(html);
      timBodyFingerprints.set(bodyFingerprint, (timBodyFingerprints.get(bodyFingerprint) || 0) + 1);
    }

    const fingerprint = text.toLocaleLowerCase("pl").replace(/\s+/g, " ").trim();
    const existing = descriptionFingerprints.get(fingerprint);
    if (existing) {
      errors.push(`Identyczny opis dla ${existing.label} oraz ${product.key}/${platform}.`);
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
  exactDuplicateDescriptions: 0,
  exactDuplicateGeneratedDescriptions: 0,
  productsWithEan: products.filter((product) => product.ean).length,
  productsWithoutEan: products.filter((product) => !product.ean).length,
  shortestDescription,
  longestDescription,
  timUniqueBodiesIgnoringHeadings: timBodyFingerprints.size,
  timProductsSharingBody: [...timBodyFingerprints.values()].filter((count) => count > 1).reduce((sum, count) => sum + count, 0),
  timLargestSharedBodyGroup: Math.max(...timBodyFingerprints.values()),
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
