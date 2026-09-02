#!/usr/bin/env node

import { readFile, writeFile } from "node:fs/promises";
import { resolve } from "node:path";
import { generateDescription, plainTextFromHtml } from "../description-engine.js";
import { validateTimDescription } from "./tim_description_quality.mjs";

const expected = [
  { id: 15907493, ean: "5905475367922", model: "12EC480WW2750", price: 225, stock: 19, card: "12EC480XX.pdf", length: "50m" },
  { id: 10047256, ean: "5905475361593", model: "E003-025-8-W100", price: 13, stock: 5, card: "E003-025-8-XX100.pdf", length: "100m" },
];
const catalog = JSON.parse(await readFile(resolve("data/catalog.json"), "utf8"));
const byEan = new Map(catalog.products.map((item) => [String(item.ean || ""), item]));
const descriptionItems = expected.map((item) => {
  const original = byEan.get(item.ean);
  if (!original || original.manufacturerCode !== item.model) throw new Error(`Brak dokładnego ${item.model} w katalogu opisów.`);
  const product = item.model === "E003-025-8-W100"
    ? { ...original, name: original.name.replace(/\(100\)/u, "100m") }
    : original;
  const descriptionHtml = generateDescription(product, "tim");
  const text = plainTextFromHtml(descriptionHtml);
  const errors = validateTimDescription(product, descriptionHtml);
  if (errors.length) throw new Error(`${item.model}: ${errors.join(",")}`);
  if (!text.includes(item.model) || !text.includes(`Długość rolki: ${item.length}`) || text.includes(item.ean) || text.includes(original.code)) {
    throw new Error(`${item.model}: błędna tożsamość albo długość w opisie.`);
  }
  return { pimcoreId: item.id, ean: item.ean, manufacturerCode: item.model, name: product.name, descriptionHtml };
});

const root = "/Users/karolbohdanowicz/Desktop/_PRESCOT/_2026/TIM.PL/TIM - karty ce";
const documents = {
  generatedAt: new Date().toISOString(),
  items: expected.map((item) => ({
    id: item.id,
    ean: item.ean,
    model: item.model,
    timListPrice: item.price,
    xmlPrice: item.price,
    xmlStock: item.stock,
    documents: {
      certifications: {
        source: `${root}/Taśmy LED/Prescot Taśmy led Premium CE 2026.pdf`,
        filename: "CE_Prescot_Tasmy_LED_Premium_2026.pdf",
      },
      dataSheet: {
        source: `${root}/Karty katalogowe/Taśmy LED/PREMIUM/${item.card}`,
        filename: `${item.model}_karta_katalogowa.pdf`,
      },
    },
  })),
};
const descriptions = {
  generatedAt: new Date().toISOString(),
  sourceCatalog: resolve("data/catalog.json"),
  stages: { bufferNewNeedsUpdate: descriptionItems },
};
await writeFile(resolve("exports/tim/remediation/exact-ean-tape-documents-queue-2026-09-01.json"), `${JSON.stringify(documents, null, 2)}\n`);
await writeFile(resolve("exports/tim/remediation/exact-ean-tape-description-queue-2026-09-01.json"), `${JSON.stringify(descriptions, null, 2)}\n`);
console.log(JSON.stringify({ items: expected.length, models: expected.map((item) => item.model) }));
