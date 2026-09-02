import { mkdir, readFile, writeFile } from "node:fs/promises";
import { createHash } from "node:crypto";
import { dirname, resolve } from "node:path";

import { generateDescription, timDescriptionName, timTradeIndex } from "../description-engine.js";

const snapshotPath = resolve(process.argv[2]
  || "exports/tim/remediation/active-brand-offer-live-readonly-post-scharfer-2026-09-01.json");
const catalogPath = resolve(process.argv[3] || "data/catalog.json");
const outputPath = resolve(process.argv[4]
  || "exports/tim/remediation/prescot-active-description-queue-2026-09-01.json");

const [snapshot, catalogDocument] = await Promise.all([
  readFile(snapshotPath, "utf8").then(JSON.parse),
  readFile(catalogPath, "utf8").then(JSON.parse),
]);

const canonicalDescription = (html) => String(html || "")
  .trim()
  .replace(/^<section>\s*/iu, "")
  .replace(/\s*<\/section>$/iu, "")
  .trim();

const normalizedStoredDescription = (html) => String(html || "")
  .replace(/&quot;|&#0*34;|&#x0*22;/giu, '"')
  .replace(/&apos;|&#0*39;|&#x0*27;/giu, "'")
  .trim();

const isUserExcludedBrand = (product) => /\bKAJA\b|LIGHT\s*PRESTIGE/iu.test([
  product?.name,
  product?.producer,
  product?.category,
  product?.url,
].filter(Boolean).join(" "));

const byEan = new Map();
for (const product of catalogDocument.products || []) {
  const ean = String(product.ean || "").trim();
  if (!ean) continue;
  if (!byEan.has(ean)) byEan.set(ean, []);
  byEan.get(ean).push(product);
}

const stages = {
  activePositiveNeedsUpdate: [],
  activePositiveCurrent: [],
  activeZeroNeedsUpdate: [],
  activeZeroCurrent: [],
};
const rejected = [];

for (const live of snapshot.products || []) {
  if (live.expectedBrand !== "Prescot" || live.state !== "active" || live.published !== true) continue;
  const ean = String(live.ean || "").trim();
  const model = String(live.model || "").trim();
  if (!ean || !model) {
    rejected.push({ id: live.id, ean, model, timName: live.timName, reason: "missing_live_identity" });
    continue;
  }
  const matches = byEan.get(ean) || [];
  if (matches.length !== 1) {
    rejected.push({ id: live.id, ean, model, timName: live.timName, reason: matches.length ? "ambiguous_catalog_ean" : "missing_catalog_ean" });
    continue;
  }
  const product = matches[0];
  if (isUserExcludedBrand(product)) {
    rejected.push({ id: live.id, ean, model, timName: live.timName, reason: "excluded_brand_user_scope" });
    continue;
  }
  const tradeIndex = timTradeIndex(product);
  if (!tradeIndex || tradeIndex !== model) {
    rejected.push({
      id: live.id,
      ean,
      model,
      catalogTradeIndex: tradeIndex,
      timName: live.timName,
      reason: "catalog_trade_index_mismatch",
    });
    continue;
  }
  const descriptionHtml = canonicalDescription(generateDescription(product, "tim"));
  if (!descriptionHtml || !descriptionHtml.includes(`Indeks handlowy: ${tradeIndex}`)) {
    throw new Error(`Brak indeksu handlowego w opisie ${live.id}/${tradeIndex}`);
  }
  if (/\b\d{13}\b/u.test(descriptionHtml)) throw new Error(`EAN w opisie ${live.id}/${tradeIndex}`);
  if (/\b(?:PRE[-_ ]?\d+|TAŚ\d+|PRO\d+|KAT\d+|WYP[-_][\p{L}\p{N}_.-]*)\b/iu.test(descriptionHtml)) {
    throw new Error(`Wewnętrzny indeks w opisie ${live.id}/${tradeIndex}`);
  }
  const record = {
    pimcoreId: Number(live.id),
    ean,
    manufacturerCode: tradeIndex,
    name: timDescriptionName(product),
    descriptionHtml,
    sourceProductKey: product.key,
    liveStock: Number(live.stock || 0),
    timIndex: String(live.timIndex || ""),
  };
  const current = normalizedStoredDescription(live.descriptionHtml) === normalizedStoredDescription(descriptionHtml);
  const prefix = Number(live.stock || 0) > 0 ? "activePositive" : "activeZero";
  stages[`${prefix}${current ? "Current" : "NeedsUpdate"}`].push(record);
}

stages.activePositiveNeedsUpdate.sort((left, right) => right.liveStock - left.liveStock || left.ean.localeCompare(right.ean));
stages.activeZeroNeedsUpdate.sort((left, right) => left.ean.localeCompare(right.ean));

const report = {
  generatedAt: new Date().toISOString(),
  sourceSnapshot: snapshotPath,
  sourceCatalog: catalogPath,
  sourceCatalogSha256: createHash("sha256").update(await readFile(catalogPath)).digest("hex"),
  rules: [
    "only active published Prescot cards",
    "exact unique EAN in the local Prescot catalog",
    "exact live model equals catalog trade index",
    "exclude KAJA and Light Prestige from automated TIM description work",
    "TIM description generated from the current /prescot engine",
    "never add EAN, PRE or other internal catalog index",
    "never change name, price, EAN, stock or identifiers",
    "separate positive-stock and zero-stock products",
  ],
  counts: {
    ...Object.fromEntries(Object.entries(stages).map(([key, value]) => [key, value.length])),
    rejected: rejected.length,
  },
  stages,
  rejected,
};

await mkdir(dirname(outputPath), { recursive: true });
await writeFile(outputPath, `${JSON.stringify(report, null, 2)}\n`, "utf8");
console.log(JSON.stringify({ outputPath, counts: report.counts }, null, 2));
