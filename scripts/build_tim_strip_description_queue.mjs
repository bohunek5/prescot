#!/usr/bin/env node

import { readFile, writeFile } from "node:fs/promises";
import { resolve } from "node:path";
import { generateDescription, plainTextFromHtml } from "../description-engine.js";
import { validateTimDescription } from "./tim_description_quality.mjs";

const documentQueuePath = resolve("exports/tim/remediation/buffer-strip-catalog-ce-queue-2026-09-01.json");
const catalogPath = resolve("data/catalog.json");
const outputPath = resolve("exports/tim/remediation/buffer-strip-description-queue-2026-09-01.json");

const documentQueue = JSON.parse(await readFile(documentQueuePath, "utf8"));
const catalog = JSON.parse(await readFile(catalogPath, "utf8"));
const byEan = new Map(catalog.products.map((product) => [String(product.ean || ""), product]));

const items = documentQueue.items.map((source) => {
  const product = byEan.get(String(source.ean));
  if (!product) throw new Error(`Brak produktu w katalogu opisów dla EAN ${source.ean}.`);
  if (String(product.manufacturerCode || "") !== String(source.model)) {
    throw new Error(`Niezgodny indeks handlowy dla EAN ${source.ean}: ${product.manufacturerCode} != ${source.model}`);
  }
  const descriptionHtml = generateDescription(product, "tim");
  const errors = validateTimDescription(product, descriptionHtml);
  const text = plainTextFromHtml(descriptionHtml);
  if (errors.length) throw new Error(`${source.model}: ${errors.join(",")}`);
  if (text.includes(String(source.ean))) throw new Error(`${source.model}: EAN w opisie.`);
  if (product.code && String(product.code) !== String(product.manufacturerCode) && text.includes(String(product.code))) {
    throw new Error(`${source.model}: wewnętrzny indeks katalogowy w opisie.`);
  }
  return {
    pimcoreId: Number(source.id),
    ean: String(source.ean),
    manufacturerCode: String(source.model),
    name: String(product.name),
    descriptionHtml,
  };
});

const output = {
  generatedAt: new Date().toISOString(),
  sourceCatalog: catalogPath,
  sourceDocuments: documentQueuePath,
  stages: { bufferNewNeedsUpdate: items },
};
await writeFile(outputPath, `${JSON.stringify(output, null, 2)}\n`, "utf8");
console.log(JSON.stringify({ output: outputPath, items: items.length }, null, 2));
