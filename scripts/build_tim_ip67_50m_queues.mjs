#!/usr/bin/env node

import { readFile, writeFile } from "node:fs/promises";
import { resolve } from "node:path";
import { generateDescription, plainTextFromHtml } from "../description-engine.js";
import { validateTimDescription } from "./tim_description_quality.mjs";

const expected = [
  { id: 15907502, ean: "5905475368165", model: "24EC320WW50IP67", price: 450, stock: 14 },
  { id: 15907505, ean: "5905475368172", model: "24EC320NW50IP67", price: 450, stock: 200 },
  { id: 15907508, ean: "5905475368189", model: "24EC320W50IP67", price: 450, stock: 3 },
];
const catalog = JSON.parse(await readFile(resolve("data/catalog.json"), "utf8"));
const byEan = new Map(catalog.products.map((item) => [String(item.ean || ""), item]));
const descriptionItems = expected.map((item) => {
  const product = byEan.get(item.ean);
  if (!product || product.manufacturerCode !== item.model) throw new Error(`Brak dokładnego ${item.model} w katalogu opisów.`);
  const descriptionHtml = generateDescription(product, "tim");
  const text = plainTextFromHtml(descriptionHtml);
  const errors = validateTimDescription(product, descriptionHtml);
  if (errors.length) throw new Error(`${item.model}: ${errors.join(",")}`);
  if (!text.includes(item.model) || !text.includes("Długość rolki: 50m") || text.includes(item.ean) || text.includes(product.code)) {
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
        source: `${root}/Karty katalogowe/Taśmy LED/PREMIUM/24EC320XXIP67.pdf`,
        filename: "24EC320XXIP67_karta_katalogowa.pdf",
      },
    },
  })),
};
const descriptions = {
  generatedAt: new Date().toISOString(),
  sourceCatalog: resolve("data/catalog.json"),
  stages: { bufferNewNeedsUpdate: descriptionItems },
};
await writeFile(resolve("exports/tim/remediation/ip67-50m-documents-queue-2026-09-01.json"), `${JSON.stringify(documents, null, 2)}\n`);
await writeFile(resolve("exports/tim/remediation/ip67-50m-description-queue-2026-09-01.json"), `${JSON.stringify(descriptions, null, 2)}\n`);
console.log(JSON.stringify({ items: expected.length, models: expected.map((item) => item.model) }));
