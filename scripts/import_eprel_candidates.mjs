#!/usr/bin/env node

import { readFile, writeFile } from "node:fs/promises";
import { resolve } from "node:path";

function argumentValue(name, fallback = "") {
  const index = process.argv.indexOf(name);
  return index >= 0 ? process.argv[index + 1] || fallback : fallback;
}

function decodeXml(value) {
  return String(value ?? "")
    .replaceAll("&lt;", "<")
    .replaceAll("&gt;", ">")
    .replaceAll("&quot;", '"')
    .replaceAll("&apos;", "'")
    .replaceAll("&amp;", "&");
}

function normalize(value) {
  return String(value ?? "").replace(/\s+/g, " ").trim().toLocaleLowerCase("pl");
}

function masterAssignments(xml) {
  const assignments = [];
  for (const match of String(xml).matchAll(/<o\b[^>]*>([\s\S]*?)<\/o>/gi)) {
    const attributes = Object.fromEntries(
      [...match[1].matchAll(/<a\s+name="([^"]+)"[^>]*>([\s\S]*?)<\/a>/gi)]
        .map((item) => [decodeXml(item[1]), decodeXml(item[2]).trim()]),
    );
    if (!attributes.Kod_produktu || !attributes.Karta_EPREL_PDF) continue;
    assignments.push({
      manufacturerCode: attributes.Kod_produktu,
      url: attributes.Karta_EPREL_PDF,
    });
  }
  return assignments;
}

function eprelId(url) {
  return String(url).match(/(?:Fiche_|lightsources\/)(\d+)/i)?.[1] || "";
}

const masterPath = resolve(argumentValue("--master-xml"));
if (!argumentValue("--master-xml")) throw new Error("Podaj --master-xml.");
const catalogPath = resolve(argumentValue("--catalog", "data/catalog.json"));
const outputPath = resolve(argumentValue("--output", "data/eprel-candidates.json"));
const [xml, catalog] = await Promise.all([
  readFile(masterPath, "utf8"),
  readFile(catalogPath, "utf8").then((value) => JSON.parse(value)),
]);

const assignments = masterAssignments(xml);
const byCode = new Map();
for (const assignment of assignments) {
  const key = normalize(assignment.manufacturerCode);
  const values = byCode.get(key) || new Set();
  values.add(assignment.url);
  byCode.set(key, values);
}

const products = {};
const conflicts = [];
for (const product of catalog.products) {
  const urls = [...(byCode.get(normalize(product.manufacturerCode)) || [])];
  if (urls.length > 1) {
    conflicts.push({ productKey: product.key, manufacturerCode: product.manufacturerCode, urls });
    continue;
  }
  if (urls.length !== 1) continue;
  products[product.key] = {
    status: "candidate",
    eprelId: eprelId(urls[0]),
    productInformationSheetPl: urls[0],
    matchedBy: "manufacturer_code",
    source: "tim-master-xml",
  };
}

const matchedCodes = new Set(Object.keys(products).map((key) => normalize(catalog.products.find((product) => product.key === key)?.manufacturerCode)));
const unmatchedAssignments = [...byCode.entries()]
  .filter(([code]) => !matchedCodes.has(code))
  .map(([code, urls]) => ({ manufacturerCode: code, urls: [...urls] }));
const output = {
  meta: {
    generatedAt: new Date().toISOString(),
    status: "candidate_only_not_verified",
    sourceFile: masterPath.split("/").at(-1),
    assignmentsInSource: assignments.length,
    uniqueSourceCodes: byCode.size,
    matchedProducts: Object.keys(products).length,
    uniqueLinks: new Set(Object.values(products).map((item) => item.productInformationSheetPl)).size,
    conflicts: conflicts.length,
    unmatchedSourceCodes: unmatchedAssignments.length,
    note: "Powiązania wymagają potwierdzenia modelu w oficjalnej karcie EPREL przed importem do TIM.",
  },
  products,
  conflicts,
  unmatchedAssignments,
};

await writeFile(outputPath, `${JSON.stringify(output, null, 2)}\n`, "utf8");
console.log(`EPREL: ${output.meta.matchedProducts} kandydatów dla aktywnego katalogu, ${output.meta.uniqueLinks} unikatowych kart.`);
console.log(`Konflikty: ${output.meta.conflicts}; niedopasowane kody źródłowe: ${output.meta.unmatchedSourceCodes}.`);
console.log(`Plik: ${outputPath}`);
