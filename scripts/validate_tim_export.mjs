#!/usr/bin/env node

import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import { resolve } from "node:path";
import { selectTimScope } from "./tim_scope.mjs";
import { validateTimDescription } from "./tim_description_quality.mjs";

function argumentValue(name, fallback) {
  const index = process.argv.indexOf(name);
  return index >= 0 ? process.argv[index + 1] || fallback : fallback;
}

const outputDir = resolve(argumentValue("--output-dir", "exports/tim"));
const [catalog, manifest] = await Promise.all([
  readFile(new URL("../data/catalog.json", import.meta.url), "utf8").then(JSON.parse),
  readFile(resolve(outputDir, "tim-manifest.json"), "utf8").then(JSON.parse),
]);

const expectedScope = selectTimScope(catalog.products);
assert.equal(manifest.products.length, expectedScope.length, "Manifest nie obejmuje dokładnego zakresu TIM.");
assert.equal(new Set(manifest.products.map((entry) => entry.productKey)).size, manifest.products.length, "Manifest powtarza produkty.");

const productByKey = new Map(catalog.products.map((product) => [product.key, product]));
const usableEans = new Set();
for (const entry of manifest.products) {
  const product = productByKey.get(entry.productKey);
  assert.ok(product, `Nieznany produkt w manifeście: ${entry.productKey}`);
  assert.ok(["ready", "review", "blocked"].includes(entry.status), `Nieznany status: ${entry.status}`);
  if (entry.status === "ready") {
    assert.equal(entry.hardBlocks.length, 0, `${entry.productKey}: gotowy produkt ma blokadę.`);
    assert.equal(entry.reviewFlags.length, 0, `${entry.productKey}: gotowy produkt ma ostrzeżenie.`);
  }
  if (entry.status === "review") {
    assert.equal(entry.hardBlocks.length, 0, `${entry.productKey}: produkt review ma blokadę.`);
    assert.ok(entry.reviewFlags.length, `${entry.productKey}: produkt review nie ma powodu.`);
  }
  if (entry.status === "blocked") assert.ok(entry.hardBlocks.length, `${entry.productKey}: blokada bez powodu.`);

  const descriptionErrors = validateTimDescription(product, entry.descriptionHtml);
  const descriptionBlock = entry.hardBlocks.some((reason) => reason.startsWith("invalid_tim_description:"));
  assert.equal(Boolean(descriptionErrors.length), descriptionBlock, `${entry.productKey}: niespójny status jakości opisu.`);

  if (entry.status !== "blocked") {
    assert.match(entry.ean, /^\d{13}$/, `${entry.productKey}: rekord do użycia nie ma poprawnego EAN.`);
    assert.ok(!usableEans.has(entry.ean), `${entry.productKey}: powtórzony EAN poza blokadą.`);
    usableEans.add(entry.ean);
  }
  if (entry.verifiedEprelUrl) {
    assert.ok(
      ["verified_exact_model", "verified_packaging_variant"].includes(entry.eprelStatus),
      `${entry.productKey}: link EPREL bez dokładnej zgodności lub zatwierdzonego wariantu długościowego.`,
    );
    assert.match(entry.verifiedEprelUrl, /^https:\/\/eprel\.ec\.europa\.eu\/fiches\/lightsources\/Fiche_\d+_PL\.pdf$/i);
  }
}

const counts = Object.fromEntries(["ready", "review", "blocked"].map((status) => [
  status,
  manifest.products.filter((entry) => entry.status === status).length,
]));
assert.deepEqual(counts, {
  ready: manifest.meta.statusCounts.ready,
  review: manifest.meta.statusCounts.review,
  blocked: manifest.meta.statusCounts.blocked,
});
assert.equal(counts.ready + counts.review + counts.blocked, expectedScope.length);
assert.equal(manifest.meta.profiles.all, 911);
assert.equal(manifest.meta.profiles.aluminium, 758);
assert.equal(manifest.meta.profiles.pcv, 153);
assert.equal(manifest.meta.officialImportReady, false, "Pakiet treści nie może udawać oficjalnego importu MarketTIM.");

console.log(`Manifest TIM: ${manifest.products.length} produktów.`);
console.log(`Gotowe: ${counts.ready}; do weryfikacji: ${counts.review}; zablokowane: ${counts.blocked}.`);
console.log("Zakres, EAN-y, statusy i opisy TIM są spójne.");
