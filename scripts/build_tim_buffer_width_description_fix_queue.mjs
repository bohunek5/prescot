#!/usr/bin/env node

import { readFile, writeFile } from "node:fs/promises";
import { resolve } from "node:path";
import { generateDescription, plainTextFromHtml } from "../description-engine.js";
import { validateTimDescription } from "./tim_description_quality.mjs";

const snapshotPath = resolve("exports/tim/remediation/buffer-current-live-final-2026-09-01.json");
const catalogPath = resolve("data/catalog.json");
const outputPath = resolve("exports/tim/remediation/buffer-width-description-fix-queue-2026-09-01.json");
const [snapshot, catalog] = await Promise.all([
  readFile(snapshotPath, "utf8").then(JSON.parse),
  readFile(catalogPath, "utf8").then(JSON.parse),
]);
const byEan = new Map(catalog.products.map((product) => [String(product.ean || ""), product]));
const stages = { bufferNewNeedsUpdate: [], bufferApprovalNeedsUpdate: [] };

for (const item of snapshot.items) {
  const oldHtml = String(item.descriptionHtml || "");
  if (!/<li>Długość:\s*\d+(?:[.,]\d+)?mm<\/li>/iu.test(oldHtml)) continue;
  if (!item.ean || !item.model || !["new", "new_for_approval"].includes(String(item.state || ""))) {
    throw new Error(`Niepełna tożsamość albo niedozwolony stan PIM ${item.id}.`);
  }
  const product = byEan.get(String(item.ean));
  if (!product || String(product.manufacturerCode || "") !== String(item.model)) {
    throw new Error(`Brak dokładnego EAN + indeks handlowy w katalogu dla PIM ${item.id}.`);
  }
  const descriptionHtml = generateDescription(product, "tim");
  const text = plainTextFromHtml(descriptionHtml);
  const errors = validateTimDescription(product, descriptionHtml);
  if (errors.length) throw new Error(`${item.model}: ${errors.join(",")}`);
  if (/Długość:\s*\d+(?:[.,]\d+)?mm/iu.test(text)) throw new Error(`${item.model}: nadal błędna długość w mm.`);
  if (text.includes(String(item.ean))) throw new Error(`${item.model}: EAN w opisie.`);
  if (!text.includes(String(item.model))) throw new Error(`${item.model}: brak indeksu handlowego.`);
  if (product.code && String(product.code) !== String(product.manufacturerCode) && text.includes(String(product.code))) {
    throw new Error(`${item.model}: wewnętrzny indeks katalogowy w opisie.`);
  }
  const record = {
    pimcoreId: Number(item.id),
    ean: String(item.ean),
    manufacturerCode: String(item.model),
    name: String(product.name),
    descriptionHtml,
  };
  stages[item.state === "new" ? "bufferNewNeedsUpdate" : "bufferApprovalNeedsUpdate"].push(record);
}

const output = {
  generatedAt: new Date().toISOString(),
  policy: "Only buffer descriptions containing the proven width-as-length defect; exact EAN and trade index required. Description is the only target field.",
  sourceSnapshot: snapshotPath,
  sourceCatalog: catalogPath,
  counts: Object.fromEntries(Object.entries(stages).map(([key, value]) => [key, value.length])),
  stages,
};
await writeFile(outputPath, `${JSON.stringify(output, null, 2)}\n`, "utf8");
console.log(JSON.stringify({ output: outputPath, counts: output.counts }, null, 2));
