#!/usr/bin/env node

import { mkdir, readFile, stat, writeFile } from "node:fs/promises";
import { basename, resolve } from "node:path";
import { selectTimScope } from "./tim_scope.mjs";

function argumentValue(name, fallback = "") {
  const index = process.argv.indexOf(name);
  return index >= 0 ? process.argv[index + 1] || fallback : fallback;
}

function requiredArgument(name) {
  const value = argumentValue(name);
  if (!value) throw new Error(`Brak wymaganego argumentu ${name}.`);
  return resolve(value);
}

function decodeXml(value) {
  return String(value ?? "")
    .replaceAll("&lt;", "<")
    .replaceAll("&gt;", ">")
    .replaceAll("&quot;", '"')
    .replaceAll("&apos;", "'")
    .replaceAll("&amp;", "&");
}

function text(value) {
  return String(value ?? "").replace(/^\uFEFF/, "").replace(/\s+/g, " ").trim();
}

function normalized(value) {
  return text(value).toLocaleLowerCase("pl");
}

function countBy(values, selector) {
  const counts = new Map();
  for (const value of values) {
    const key = text(selector(value)) || "(brak)";
    counts.set(key, (counts.get(key) || 0) + 1);
  }
  return Object.fromEntries([...counts.entries()].sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0], "pl")));
}

function parseDelimited(input, delimiter = ";") {
  const rows = [];
  let row = [];
  let cell = "";
  let quoted = false;
  const value = String(input).replace(/^\uFEFF/, "");
  for (let index = 0; index < value.length; index += 1) {
    const char = value[index];
    if (char === '"') {
      if (quoted && value[index + 1] === '"') {
        cell += '"';
        index += 1;
      } else {
        quoted = !quoted;
      }
    } else if (!quoted && char === delimiter) {
      row.push(cell);
      cell = "";
    } else if (!quoted && (char === "\n" || char === "\r")) {
      if (char === "\r" && value[index + 1] === "\n") index += 1;
      row.push(cell);
      if (row.some((item) => item !== "")) rows.push(row);
      row = [];
      cell = "";
    } else {
      cell += char;
    }
  }
  if (cell || row.length) {
    row.push(cell);
    if (row.some((item) => item !== "")) rows.push(row);
  }
  if (!rows.length) return [];
  const headers = rows[0].map(text);
  return rows.slice(1).map((cells) => Object.fromEntries(headers.map((header, index) => [header, cells[index] ?? ""])));
}

function xmlTag(block, tag) {
  return decodeXml(block.match(new RegExp(`<${tag}(?:\\s[^>]*)?>([\\s\\S]*?)<\\/${tag}>`, "i"))?.[1] || "");
}

function xmlAttribute(openingTag, name) {
  return decodeXml(openingTag.match(new RegExp(`\\b${name}="([^"]*)"`, "i"))?.[1] || "");
}

function parseMasterXml(input) {
  return [...String(input).matchAll(/<o\b([^>]*)>([\s\S]*?)<\/o>/gi)].map((match) => {
    const attributes = {};
    for (const attribute of match[2].matchAll(/<a\s+name="([^"]+)"[^>]*>([\s\S]*?)<\/a>/gi)) {
      attributes[decodeXml(attribute[1])] = decodeXml(attribute[2]);
    }
    return {
      id: xmlAttribute(match[1], "id"),
      price: xmlAttribute(match[1], "price"),
      stock: xmlAttribute(match[1], "stock"),
      name: text(xmlTag(match[2], "name")),
      category: text(xmlTag(match[2], "cat")),
      description: xmlTag(match[2], "desc"),
      imageCount: [...match[2].matchAll(/<(?:main|i)\s+url="/gi)].length,
      attributes,
    };
  });
}

function usableEan(value) {
  const ean = text(value);
  return /^\d{8,14}$/.test(ean) ? ean : "";
}

function deniedText(value) {
  return /\bkaja\b|light\s*prestige|^light(?:\s|$)/iu.test(text(value));
}

function uniqueIndex(values, selector) {
  const index = new Map();
  for (const value of values) {
    const key = normalized(selector(value));
    if (!key) continue;
    const items = index.get(key) || [];
    items.push(value);
    index.set(key, items);
  }
  return index;
}

function reconcile(catalog, panelRows) {
  const target = selectTimScope(catalog.products);
  const byEan = uniqueIndex(panelRows, (row) => usableEan(row["Kod kreskowy"]));
  const byManufacturerCode = uniqueIndex(panelRows, (row) => row["Indeks producenta"]);
  let matchedByEan = 0;
  let matchedByManufacturerCode = 0;
  const ambiguous = [];
  const missing = [];
  const matches = [];

  for (const product of target) {
    const eanMatches = usableEan(product.ean) ? byEan.get(normalized(product.ean)) || [] : [];
    const codeMatches = byManufacturerCode.get(normalized(product.manufacturerCode)) || [];
    let match = null;
    let method = "";
    if (eanMatches.length === 1) {
      [match] = eanMatches;
      method = "ean";
      matchedByEan += 1;
    } else if (!eanMatches.length && codeMatches.length === 1) {
      [match] = codeMatches;
      method = "manufacturer_code";
      matchedByManufacturerCode += 1;
    } else if (eanMatches.length > 1 || codeMatches.length > 1) {
      ambiguous.push({ productKey: product.key, ean: product.ean, manufacturerCode: product.manufacturerCode, eanMatches: eanMatches.length, codeMatches: codeMatches.length });
    } else {
      missing.push({ productKey: product.key, ean: product.ean, manufacturerCode: product.manufacturerCode, producer: product.producer, name: product.name });
    }
    if (match) matches.push({
      productKey: product.key,
      method,
      timIndex: text(match["Indeks TIM"]),
      pimcoreId: text(match.id),
      visible: text(match["Widoczny na tim.pl"]),
    });
  }
  return {
    targetProducts: target.length,
    matched: matches.length,
    matchedByEan,
    matchedByManufacturerCode,
    ambiguous: ambiguous.length,
    missing: missing.length,
    matches,
    ambiguousProducts: ambiguous,
    missingProducts: missing,
  };
}

function markdown(report) {
  const errorLines = Object.entries(report.lastImport.errorsByReason).slice(0, 12)
    .map(([reason, count]) => `- ${reason}: ${count.toLocaleString("pl-PL")}`);
  return `# TIM - audyt źródeł i ostatnich importów

Wygenerowano: ${report.generatedAt}

## Decyzja operacyjna

**STOP: pliku \`${report.masterXml.file}\` nie wolno ponownie uruchamiać ani traktować jako poprawnego importu.** Zawiera wartości zastępcze w polu EAN, produkty spoza ustalonego zakresu oraz opisy niezgodne z aktualnymi regułami jakości.

## Aktualny eksport katalogu TIM/PIMCORE

- Rekordy aktywne: ${report.panel.activeRows.toLocaleString("pl-PL")}.
- Widoczne na TIM.pl: ${report.panel.visibleRows.toLocaleString("pl-PL")}.
- Produkty Light Prestige/Kaja wykryte w aktywnym eksporcie: ${report.panel.deniedRows.toLocaleString("pl-PL")}.
- Produkty z docelowego zakresu Prescot dopasowane do eksportu: ${report.reconciliation.matched.toLocaleString("pl-PL")} z ${report.reconciliation.targetProducts.toLocaleString("pl-PL")}.
- Docelowe produkty bez jednoznacznego dopasowania w eksporcie: ${report.reconciliation.missing.toLocaleString("pl-PL")}.

## Ostatni raport importu

- Wiersze: ${report.lastImport.rows.toLocaleString("pl-PL")}.
- Błędy: ${report.lastImport.errorRows.toLocaleString("pl-PL")}.
- Zaimportowane: ${report.lastImport.importedRows.toLocaleString("pl-PL")}.
- Wyedytowane: ${report.lastImport.editedRows.toLocaleString("pl-PL")}.

Najczęstsze przyczyny:

${errorLines.join("\n")}

## Kontrola master XML

- Oferty: ${report.masterXml.offers.toLocaleString("pl-PL")}.
- Nieprawidłowe EAN: ${report.masterXml.invalidEan.toLocaleString("pl-PL")} (w tym \`MA\`: ${report.masterXml.eanMa.toLocaleString("pl-PL")}).
- Produkty Light Prestige/Kaja: ${report.masterXml.deniedRows.toLocaleString("pl-PL")}.
- Bez zdjęcia w pliku: ${report.masterXml.withoutImages.toLocaleString("pl-PL")}.
- Opisy ze stylem inline: ${report.masterXml.inlineStyleDescriptions.toLocaleString("pl-PL")}.
- Opisy powtarzające EAN: ${report.masterXml.eanRepeatedInDescription.toLocaleString("pl-PL")}.
- Powiązania EPREL: ${report.masterXml.eprelAssignments.toLocaleString("pl-PL")} (${report.masterXml.uniqueEprelLinks.toLocaleString("pl-PL")} unikatowych linków).

## Zasada dalszej pracy

Plik z WAPRO jest źródłem nazwy, stanu i ceny źródłowej, ale cena z tego XML nie jest automatycznie ceną netto dla TIM. Opisy są przygotowywane oddzielnie. Oficjalny import TIM wymaga aktualnego szablonu, mapowania producenta, jednostki i kategorii B24; multimedia oraz ETIM są obsługiwane osobnymi procesami.
`;
}

const panelPath = requiredArgument("--panel-export");
const importPath = requiredArgument("--import-report");
const masterPath = requiredArgument("--master-xml");
const outputDir = resolve(argumentValue("--output-dir", "exports/tim/source-audit"));
const catalogPath = resolve(argumentValue("--catalog", "data/catalog.json"));

const [panelText, importText, masterText, catalog, panelStat, importStat, masterStat] = await Promise.all([
  readFile(panelPath, "utf8"),
  readFile(importPath, "utf8"),
  readFile(masterPath, "utf8"),
  readFile(catalogPath, "utf8").then((value) => JSON.parse(value)),
  stat(panelPath),
  stat(importPath),
  stat(masterPath),
]);

const panelRows = parseDelimited(panelText);
const importRows = parseDelimited(importText);
const masterOffers = parseMasterXml(masterText);
const deniedPanel = panelRows.filter((row) => deniedText(`${row.Producent} ${row["Nazwa TIM"]}`));
const deniedMaster = masterOffers.filter((offer) => deniedText(`${offer.attributes.Producent} ${offer.name} ${offer.category}`));
const importStatuses = countBy(importRows, (row) => row.Status);
const numericMasterEans = masterOffers.map((offer) => usableEan(offer.attributes.EAN)).filter(Boolean);
const eanCounts = countBy(numericMasterEans, (ean) => ean);
const duplicateNumericEans = Object.fromEntries(Object.entries(eanCounts).filter(([, count]) => count > 1));
const reconciliation = reconcile(catalog, panelRows);

const report = {
  generatedAt: new Date().toISOString(),
  sources: {
    panelExport: { file: basename(panelPath), modifiedAt: panelStat.mtime.toISOString() },
    importReport: { file: basename(importPath), modifiedAt: importStat.mtime.toISOString() },
    masterXml: { file: basename(masterPath), modifiedAt: masterStat.mtime.toISOString() },
    catalog: { file: basename(catalogPath), generatedAt: catalog.meta.generatedAt, source: catalog.meta.source },
  },
  panel: {
    rows: panelRows.length,
    activeRows: panelRows.filter((row) => text(row.Status) === "Aktywny").length,
    visibleRows: panelRows.filter((row) => text(row["Widoczny na tim.pl"]).toUpperCase() === "TRUE").length,
    deniedRows: deniedPanel.length,
    producers: countBy(panelRows, (row) => row.Producent),
    deniedProducts: deniedPanel.map((row) => ({ timIndex: text(row["Indeks TIM"]), manufacturerCode: text(row["Indeks producenta"]), producer: text(row.Producent), name: text(row["Nazwa TIM"]), visible: text(row["Widoczny na tim.pl"]) })),
  },
  lastImport: {
    rows: importRows.length,
    errorRows: Number(importStatuses["Błąd"] || 0),
    importedRows: Number(importStatuses.Zaimportowany || 0),
    editedRows: Number(importStatuses.Wyedytowany || 0),
    statuses: importStatuses,
    errorsByReason: countBy(importRows.filter((row) => row.Status === "Błąd"), (row) => row.Informacje),
  },
  masterXml: {
    file: basename(masterPath),
    offers: masterOffers.length,
    invalidEan: masterOffers.filter((offer) => !usableEan(offer.attributes.EAN)).length,
    eanMa: masterOffers.filter((offer) => text(offer.attributes.EAN).toUpperCase() === "MA").length,
    duplicateNumericEans,
    deniedRows: deniedMaster.length,
    deniedProducts: deniedMaster.map((offer) => ({ id: offer.id, code: text(offer.attributes.Kod_produktu), producer: text(offer.attributes.Producent), name: offer.name })),
    withoutImages: masterOffers.filter((offer) => offer.imageCount === 0).length,
    inlineStyleDescriptions: masterOffers.filter((offer) => /\sstyle=/i.test(offer.description)).length,
    eanRepeatedInDescription: masterOffers.filter((offer) => /\bEAN\s*:/i.test(offer.description)).length,
    eprelAssignments: masterOffers.filter((offer) => text(offer.attributes.Karta_EPREL_PDF)).length,
    uniqueEprelLinks: new Set(masterOffers.map((offer) => text(offer.attributes.Karta_EPREL_PDF)).filter(Boolean)).size,
    producers: countBy(masterOffers, (offer) => offer.attributes.Producent),
  },
  reconciliation,
  hardStop: masterOffers.some((offer) => !usableEan(offer.attributes.EAN)) || deniedMaster.length > 0 || Number(importStatuses["Błąd"] || 0) > 0,
};

await mkdir(outputDir, { recursive: true });
await Promise.all([
  writeFile(resolve(outputDir, "tim-source-audit.json"), `${JSON.stringify(report, null, 2)}\n`, "utf8"),
  writeFile(resolve(outputDir, "TIM-ZRODLA-RAPORT.md"), markdown(report), "utf8"),
]);

console.log(`Panel: ${report.panel.activeRows} aktywnych, ${report.panel.visibleRows} widocznych, ${report.panel.deniedRows} poza zakresem.`);
console.log(`Ostatni import: ${report.lastImport.errorRows} błędów / ${report.lastImport.rows} wierszy.`);
console.log(`Master XML: ${report.masterXml.offers} ofert, ${report.masterXml.invalidEan} wadliwych EAN, ${report.masterXml.deniedRows} poza zakresem.`);
console.log(`Dopasowanie katalogu docelowego do panelu: ${reconciliation.matched}/${reconciliation.targetProducts}.`);
console.log(`Raport: ${outputDir}`);

if (process.argv.includes("--strict") && report.hardStop) process.exitCode = 2;
