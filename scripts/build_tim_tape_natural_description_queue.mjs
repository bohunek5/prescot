import { mkdir, readFile, writeFile } from "node:fs/promises";
import { dirname, resolve } from "node:path";

import { generateDescription, timDescriptionName, timTradeIndex } from "../description-engine.js";
import { validateTimDescription } from "./tim_description_quality.mjs";

const snapshotPath = resolve(process.argv[2]
  || "exports/tim/remediation/active-brand-offer-live-readonly-post-scharfer-2026-09-01.json");
const catalogPath = resolve(process.argv[3] || "data/catalog.json");
const outputPath = resolve(process.argv[4]
  || "exports/tim/remediation/prescot-tape-natural-description-queue-2026-09-02.json");

const [snapshot, catalogDocument] = await Promise.all([
  readFile(snapshotPath, "utf8").then(JSON.parse),
  readFile(catalogPath, "utf8").then(JSON.parse),
]);

const canonical = (html) => String(html || "")
  .trim()
  .replace(/^<section>\s*/iu, "")
  .replace(/\s*<\/section>$/iu, "")
  .trim();

const normalizedStored = (html) => String(html || "")
  .replace(/&quot;|&#0*34;|&#x0*22;/giu, '"')
  .replace(/&apos;|&#0*39;|&#x0*27;/giu, "'")
  .trim();

function tapeSeries(product) {
  const name = String(product?.name || "");
  const source = String(product?.sourceDescription || "");
  const code = String(product?.manufacturerCode || "");
  const warranty = String(product?.attributes?.Gwarancja || "");
  if (/\bDelux\b|\bPL7Y\b/iu.test(name) || /\b84\s*miesi/iu.test(warranty)) return "Delux7Y";
  if (/\bEconomic\b/iu.test(name) || /\bEconomic\b/iu.test(source) || /^EH/iu.test(code)) return "Standard2Y";
  if (/\bPremium\b/iu.test(name)) {
    const stated = Number(
      name.match(/\b(?:PL)?(\d)Y\b/iu)?.[1]
      || name.match(/\b(\d+)\s+(?:lat|lata)\s+gwarancji\b/iu)?.[1]
      || 0,
    );
    if (stated === 5) return "Premium5Y";
    if (stated === 3 || (!stated && /EC/iu.test(code))) return "Premium3Y";
    if (/\b60\s*miesi/iu.test(warranty)) return "Premium5Y";
    if (/\b36\s*miesi/iu.test(warranty)) return "Premium3Y";
  }
  return "Other";
}

const seriesPriority = new Map([
  ["Delux7Y", 0],
  ["Premium5Y", 1],
  ["Premium3Y", 2],
]);

const byEan = new Map();
for (const product of catalogDocument.products || []) {
  if (product.categoryRoot !== "Taśmy LED") continue;
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
  const matches = byEan.get(ean) || [];
  if (!ean || !model || matches.length !== 1) continue;
  const product = matches[0];
  const series = tapeSeries(product);
  if (!seriesPriority.has(series)) continue;
  const tradeIndex = timTradeIndex(product);
  if (!tradeIndex || tradeIndex !== model) {
    rejected.push({ id: live.id, ean, model, series, reason: "catalog_trade_index_mismatch" });
    continue;
  }

  const fullDescription = generateDescription(product, "tim");
  const descriptionHtml = canonical(fullDescription);
  const errors = validateTimDescription(product, fullDescription);
  const attributes = product.attributes || {};
  const saysPolish = /wyprodukowana w Polsce/iu.test(descriptionHtml);
  const sourcePolish = String(attributes["Polska produkcja"] || "").toLocaleLowerCase("pl") === "tak";
  const hasGenericFallback = /Charakter światła oraz miejsce zastosowania należy dopasować/iu.test(descriptionHtml);
  const expectedSeriesWarranty = series === "Premium5Y" ? 5 : series === "Premium3Y" ? 3 : 0;
  const hasExpectedSeriesWarranty = !expectedSeriesWarranty
    || new RegExp(`${expectedSeriesWarranty}-letnią gwarancją`, "iu").test(descriptionHtml);
  const forbidden = /\b\d{13}\b|\b(?:PRE[-_ ]?\d+|TAŚ\d+|PRO\d+|KAT\d+|WYP[-_][\p{L}\p{N}_.-]*)\b|Opis dotyczy produktu|Parametry produktu|Indeks handlowy\s*:|Wariant ma moc|\bEconomic\b/iu.test(descriptionHtml);
  if (errors.length || forbidden || saysPolish !== sourcePolish || hasGenericFallback || !hasExpectedSeriesWarranty) {
    rejected.push({
      id: live.id,
      ean,
      model,
      series,
      reason: "description_quality_guard_failed",
      errors,
      forbidden,
      saysPolish,
      sourcePolish,
      hasGenericFallback,
      expectedSeriesWarranty,
      hasExpectedSeriesWarranty,
    });
    continue;
  }

  const record = {
    pimcoreId: Number(live.id),
    ean,
    manufacturerCode: tradeIndex,
    name: timDescriptionName(product),
    descriptionHtml,
    sourceProductKey: product.key,
    sourceUrl: product.url,
    series,
    liveStock: Number(live.stock || 0),
    timIndex: String(live.timIndex || ""),
  };
  const current = normalizedStored(live.descriptionHtml) === normalizedStored(descriptionHtml);
  const stockGroup = record.liveStock > 0 ? "activePositive" : "activeZero";
  stages[`${stockGroup}${current ? "Current" : "NeedsUpdate"}`].push(record);
}

for (const values of Object.values(stages)) values.sort((left, right) => {
  const seriesDelta = seriesPriority.get(left.series) - seriesPriority.get(right.series);
  if (seriesDelta) return seriesDelta;
  return right.liveStock - left.liveStock || left.ean.localeCompare(right.ean);
});

const allAccepted = Object.values(stages).flat();
const report = {
  generatedAt: new Date().toISOString(),
  sourceSnapshot: snapshotPath,
  sourceCatalog: catalogPath,
  writeOrder: ["Delux7Y", "Premium5Y", "Premium3Y"],
  rules: [
    "only active published Prescot LED tapes",
    "exact unique EAN and exact live model equals manufacturer trade index",
    "three natural copy blocks without a parameter list",
    "no EAN, internal index, generic boilerplate or Economic label",
    "Polish production only when the source attribute equals Tak",
    "Premium 5Y and Premium 3Y must state the matching commercial warranty",
    "positive stock before zero stock",
    "never change name, price, EAN, stock or identifiers",
  ],
  counts: {
    ...Object.fromEntries(Object.entries(stages).map(([key, value]) => [key, value.length])),
    bySeries: Object.fromEntries([...seriesPriority.keys()].map((series) => [
      series,
      allAccepted.filter((item) => item.series === series).length,
    ])),
    rejected: rejected.length,
  },
  stages,
  rejected,
};

await mkdir(dirname(outputPath), { recursive: true });
await writeFile(outputPath, `${JSON.stringify(report, null, 2)}\n`, "utf8");
console.log(JSON.stringify({ outputPath, counts: report.counts }, null, 2));
