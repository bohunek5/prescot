#!/usr/bin/env node

import { mkdir, readFile, rm, writeFile } from "node:fs/promises";
import { dirname, resolve } from "node:path";
import { renderTimDescription, validateTimDescription } from "./tim_description_quality.mjs";
import {
  TIM_SCOPE_CONFIG,
  groupCounts,
  numericValue,
  timScopeDecision,
} from "./tim_scope.mjs";

function argumentValue(name, fallback = "") {
  const index = process.argv.indexOf(name);
  return index >= 0 ? process.argv[index + 1] || fallback : fallback;
}

function csvCell(value) {
  return `"${String(value ?? "").replaceAll('"', '""').replace(/[\r\n]+/g, " ")}"`;
}

function csv(rows) {
  const headers = [
    "status",
    "product_key",
    "ean",
    "indeks_handlowy",
    "kod_producenta",
    "producent",
    "nazwa",
    "kategoria",
    "cena_zrodlowa_wapro_xml",
    "stan_zrodlowy_wapro_xml",
    "eprel_pdf_zweryfikowany",
    "opis_html_tim",
    "blokady",
    "ostrzezenia",
  ];
  const lines = [headers.map(csvCell).join(";")];
  for (const row of rows) {
    lines.push([
      row.status,
      row.productKey,
      row.ean,
      row.tradeIndex,
      row.manufacturerCode,
      row.producer,
      row.name,
      row.category,
      row.price,
      row.stock,
      row.verifiedEprelUrl,
      row.descriptionHtml,
      row.hardBlocks.join(" | "),
      row.reviewFlags.join(" | "),
    ].map(csvCell).join(";"));
  }
  return `\uFEFF${lines.join("\r\n")}\r\n`;
}

function editMap(payload) {
  const map = new Map();
  for (const edit of payload?.edits || []) {
    if (edit?.platform !== "tim" || !edit.productKey || !edit.description) continue;
    map.set(edit.productKey, String(edit.description));
  }
  return map;
}

function reasonCounts(entries, field) {
  return groupCounts(entries.flatMap((entry) => entry[field].map((reason) => ({ reason }))), (item) => item.reason);
}

function timNameWarnings(product) {
  const name = String(product.name || "").trim();
  const manufacturerCode = String(product.manufacturerCode || "").trim();
  const warnings = [];
  if (name.length > 128) warnings.push("tim_name_over_128");
  if (/[®∞&α]/u.test(name)) warnings.push("tim_name_forbidden_special_character");
  if (name && name === name.toLocaleUpperCase("pl") && /[A-ZĄĆĘŁŃÓŚŹŻ]{5}/u.test(name)) warnings.push("tim_name_all_uppercase");
  if (manufacturerCode && !name.toLocaleLowerCase("pl").endsWith(manufacturerCode.toLocaleLowerCase("pl"))) warnings.push("tim_name_missing_manufacturer_code_at_end");
  return warnings;
}

function markdownReport(report) {
  const lines = [
    "# TIM — raport kontrolny eksportu",
    "",
    `Wygenerowano: ${report.generatedAt}`,
    "",
    "## Wynik",
    "",
    `- Zakres TIM: ${report.scopeProducts.toLocaleString("pl-PL")} produktów.`,
    `- Opisy gotowe do mapowania w aktualnym szablonie TIM: ${report.statusCounts.ready.toLocaleString("pl-PL")}.`,
    `- Do ręcznej decyzji lub researchu: ${report.statusCounts.review.toLocaleString("pl-PL")}.`,
    `- Zablokowane: ${report.statusCounts.blocked.toLocaleString("pl-PL")}.`,
    `- Poza zakresem: ${report.statusCounts.out_of_scope.toLocaleString("pl-PL")}.`,
    "",
    "Stan `ready` oznacza gotową treść opisu, a nie gotowy oficjalny import. Stan `review` nie trafia do pliku z gotową treścią. Stan zerowy jest ostrzeżeniem, a brak lub duplikat EAN, cena niedodatnia i wadliwy opis są blokadą.",
    "",
    "## Blokada automatycznego wgrywania",
    "",
    "Ten katalog nie jest szablonem MarketTIM i nie może zostać przesłany bez mapowania. Przed importem trzeba potwierdzić cenę B2B netto, jednostkę fakturowania, producenta z listy TIM, kategorię B24, gabaryt, VAT i czas wysyłki. Multimedia i ETIM obsługuje się osobno.",
    "",
    "## Zakres producentów",
    "",
    ...Object.entries(report.byProducer).map(([name, count]) => `- ${name}: ${count.toLocaleString("pl-PL")}`),
    "",
    "## Blokady",
    "",
    ...(Object.keys(report.hardBlockCounts).length
      ? Object.entries(report.hardBlockCounts).map(([name, count]) => `- ${name}: ${count.toLocaleString("pl-PL")}`)
      : ["- Brak blokad."]),
    "",
    "## Ostrzeżenia wymagające decyzji",
    "",
    ...(Object.keys(report.reviewFlagCounts).length
      ? Object.entries(report.reviewFlagCounts).map(([name, count]) => `- ${name}: ${count.toLocaleString("pl-PL")}`)
      : ["- Brak ostrzeżeń."]),
    "",
    "## EPREL",
    "",
    ...Object.entries(report.eprelStatusCounts).map(([name, count]) => `- ${name}: ${count.toLocaleString("pl-PL")}`),
    "",
    "Do kolumny z kartą EPREL trafiają wyłącznie produkty ze statusem `verified_exact_model`. Niedopasowania i warianty nie są eksportowane jako poprawne powiązania.",
    "",
    "## Nazwy wymagające dostosowania do szablonu TIM",
    "",
    ...Object.entries(report.nameWarningCounts).map(([name, count]) => `- ${name}: ${count.toLocaleString("pl-PL")}`),
    "",
    "## Pliki",
    "",
    "- `tim-content-ready.csv` — opisy bez blokad i ostrzeżeń; plik pomocniczy, nie szablon importu.",
    "- `tim-content-review.csv` — rekordy wymagające decyzji lub uzupełnienia źródeł.",
    "- `tim-content-blocked.csv` — rekordy, których nie wolno użyć.",
    "- `tim-content-all.csv` — pełny zakres wraz ze statusem.",
    "- `tim-manifest.json` — audytowalny manifest z opisem i powodami decyzji.",
    "",
  ];
  return `${lines.join("\n")}\n`;
}

const outputDir = resolve(argumentValue("--output-dir", "exports/tim"));
const statusOutput = resolve(argumentValue("--status-output", "data/tim-status.json"));
const editsPath = argumentValue("--edits");

const [catalog, generated, researchQueue, resolutions, eprelCandidates] = await Promise.all([
  readFile(new URL("../data/catalog.json", import.meta.url), "utf8").then(JSON.parse),
  readFile(new URL("../data/seo-descriptions.json", import.meta.url), "utf8").then(JSON.parse),
  readFile(new URL("../data/source-research-queue.json", import.meta.url), "utf8").then(JSON.parse),
  readFile(new URL("../data/source-resolutions.json", import.meta.url), "utf8").then(JSON.parse),
  readFile(new URL("../data/eprel-candidates.json", import.meta.url), "utf8")
    .then((value) => JSON.parse(value))
    .catch(() => ({ meta: { status: "not_available" }, products: {} })),
]);
const edits = editsPath ? editMap(JSON.parse(await readFile(resolve(editsPath), "utf8"))) : new Map();
const unresolvedResearch = new Set(researchQueue.products
  .filter((item) => resolutions.products?.[item.key]?.status !== "verified")
  .map((item) => item.key));

const eanCounts = new Map();
for (const product of catalog.products) {
  if (!product.ean) continue;
  eanCounts.set(product.ean, (eanCounts.get(product.ean) || 0) + 1);
}

const entries = [];
const statusProducts = {};
for (const product of catalog.products) {
  const scope = timScopeDecision(product);
  if (!scope.included) {
    statusProducts[product.key] = {
      status: "out_of_scope",
      inclusionReasons: scope.inclusionReasons,
      exclusionReasons: scope.exclusionReasons,
      hardBlocks: [],
      reviewFlags: [],
    };
    continue;
  }

  const descriptionHtml = renderTimDescription(product, generated.products?.[product.key], edits.get(product.key) || "");
  const descriptionErrors = validateTimDescription(product, descriptionHtml);
  const hardBlocks = [];
  const reviewFlags = [];
  const information = [];
  const eprel = eprelCandidates.products?.[product.key] || null;
  const nameWarnings = timNameWarnings(product);

  if (!/^\d{13}$/.test(product.ean || "")) hardBlocks.push("missing_or_invalid_ean");
  if (product.ean && (eanCounts.get(product.ean) || 0) > 1) hardBlocks.push("duplicate_ean");
  if (numericValue(product.price) <= 0) hardBlocks.push("nonpositive_price");
  if (descriptionErrors.length) hardBlocks.push(...descriptionErrors.map((error) => `invalid_tim_description:${error}`));
  if (numericValue(product.stock) <= 0) reviewFlags.push("zero_stock");
  if (unresolvedResearch.has(product.key)) reviewFlags.push("source_research_pending");
  if (!String(product.sourceDescription || "").trim()) reviewFlags.push("source_description_empty");
  if (eprel?.status === "review_variant_model") reviewFlags.push("eprel_variant_requires_evidence");
  if (eprel?.status === "blocked_model_mismatch") reviewFlags.push("eprel_candidate_model_mismatch");
  if (eprel?.status === "blocked_missing_official_pdf") reviewFlags.push("eprel_official_pdf_missing");
  if (eprel?.status === "verified_exact_model") information.push("eprel_exact_model_verified");
  if (edits.has(product.key)) information.push("browser_edit_applied");

  const status = hardBlocks.length ? "blocked" : reviewFlags.length ? "review" : "ready";
  const entry = {
    status,
    productKey: product.key,
    ean: product.ean,
    tradeIndex: product.code,
    manufacturerCode: product.manufacturerCode,
    producer: product.producer,
    name: product.name,
    category: product.category,
    categoryRoot: product.categoryRoot,
    price: product.price,
    stock: product.stock,
    verifiedEprelUrl: eprel?.status === "verified_exact_model" ? eprel.productInformationSheetPl : "",
    eprelStatus: eprel?.status || "not_assigned",
    productUrl: product.url,
    descriptionHtml,
    hardBlocks,
    reviewFlags: [...new Set(reviewFlags)],
    information,
    nameWarnings,
    scopeReasons: scope.inclusionReasons,
  };
  entries.push(entry);
  statusProducts[product.key] = {
    status,
    hardBlocks: entry.hardBlocks,
    reviewFlags: entry.reviewFlags,
    information,
    nameWarnings,
    eprelStatus: entry.eprelStatus,
    verifiedEprelUrl: entry.verifiedEprelUrl,
    inclusionReasons: scope.inclusionReasons,
    exclusionReasons: [],
  };
}

const ready = entries.filter((entry) => entry.status === "ready");
const review = entries.filter((entry) => entry.status === "review");
const blocked = entries.filter((entry) => entry.status === "blocked");
const statusCounts = {
  ready: ready.length,
  review: review.length,
  blocked: blocked.length,
  out_of_scope: catalog.products.length - entries.length,
};
const report = {
  generatedAt: new Date().toISOString(),
  catalogGeneratedAt: catalog.meta.generatedAt,
  descriptionUpdatedAt: generated.meta.updatedAt,
  scopeVersion: TIM_SCOPE_CONFIG.version,
  allActiveProducts: catalog.products.length,
  scopeProducts: entries.length,
  statusCounts,
  descriptionsInReadyPackage: ready.length,
  officialImportReady: false,
  editsApplied: edits.size,
  byProducer: groupCounts(entries, (entry) => entry.producer),
  byCategoryRoot: groupCounts(entries, (entry) => entry.categoryRoot),
  profiles: {
    all: entries.filter((entry) => entry.categoryRoot === "Profile do taśm LED").length,
    aluminium: entries.filter((entry) => entry.category.includes("aluminiowe")).length,
    pcv: entries.filter((entry) => entry.category.includes("PCV")).length,
  },
  hardBlockCounts: reasonCounts(blocked, "hardBlocks"),
  reviewFlagCounts: reasonCounts(review, "reviewFlags"),
  nameWarningCounts: reasonCounts(entries, "nameWarnings"),
  eprelStatusCounts: groupCounts(entries, (entry) => entry.eprelStatus),
  eprelSourceStatus: eprelCandidates.meta?.status || "not_available",
};
const manifest = {
  meta: report,
  scope: TIM_SCOPE_CONFIG,
  products: entries,
};
const timStatus = {
  meta: {
    generatedAt: report.generatedAt,
    scopeVersion: TIM_SCOPE_CONFIG.version,
    counts: statusCounts,
  },
  products: statusProducts,
};

await mkdir(outputDir, { recursive: true });
await mkdir(dirname(statusOutput), { recursive: true });
await Promise.all(["tim-ready.csv", "tim-review.csv", "tim-blocked.csv", "tim-all.csv"].map((file) => rm(resolve(outputDir, file), { force: true })));
await Promise.all([
  writeFile(resolve(outputDir, "tim-content-ready.csv"), csv(ready), "utf8"),
  writeFile(resolve(outputDir, "tim-content-review.csv"), csv(review), "utf8"),
  writeFile(resolve(outputDir, "tim-content-blocked.csv"), csv(blocked), "utf8"),
  writeFile(resolve(outputDir, "tim-content-all.csv"), csv(entries), "utf8"),
  writeFile(resolve(outputDir, "tim-manifest.json"), `${JSON.stringify(manifest, null, 2)}\n`, "utf8"),
  writeFile(resolve(outputDir, "tim-report.json"), `${JSON.stringify(report, null, 2)}\n`, "utf8"),
  writeFile(resolve(outputDir, "TIM-RAPORT.md"), markdownReport(report), "utf8"),
  writeFile(resolve(outputDir, "NIE-WGRYWAC-BEZ-MAPOWANIA.txt"), "STOP: pliki CSV w tym katalogu są pakietem treści i kontroli, a nie oficjalnym szablonem MarketTIM. Nie wgrywaj ich bez potwierdzenia ceny B2B, jednostki, producenta, kategorii B24, VAT, gabarytu i czasu wysyłki. Multimedia oraz ETIM wymagają osobnych importów.\n", "utf8"),
  writeFile(statusOutput, `${JSON.stringify(timStatus)}\n`, "utf8"),
]);

console.log(`Zakres TIM: ${entries.length}`);
console.log(`Gotowe: ${ready.length}; do weryfikacji: ${review.length}; zablokowane: ${blocked.length}; poza zakresem: ${statusCounts.out_of_scope}`);
console.log(`Pakiet: ${outputDir}`);
console.log(`Status panelu: ${statusOutput}`);
