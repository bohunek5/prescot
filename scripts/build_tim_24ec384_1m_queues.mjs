#!/usr/bin/env node

import { readFile, writeFile } from "node:fs/promises";
import { resolve } from "node:path";
import { generateDescription, plainTextFromHtml } from "../description-engine.js";
import { validateTimDescription } from "./tim_description_quality.mjs";

const expected = [
  { id: 10649251, ean: "5905475367052", model: "24EC384-042-8-WWL1", price: 8, stock: 106, card: "24EC384-042-8-WWL1.pdf" },
  { id: 10648939, ean: "5905475367083", model: "24EC384-042-8-NWL1", price: 8, stock: 84, card: "24EC384-042-8-XX1L.pdf" },
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
  if (!text.includes(item.model) || !text.includes("Długość rolki: 1m") || text.includes(item.ean) || text.includes(product.code)) {
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
await writeFile(resolve("exports/tim/remediation/24ec384-1m-documents-queue-2026-09-01.json"), `${JSON.stringify(documents, null, 2)}\n`);
await writeFile(resolve("exports/tim/remediation/24ec384-1m-description-queue-2026-09-01.json"), `${JSON.stringify(descriptions, null, 2)}\n`);
console.log(JSON.stringify({ items: expected.length, models: expected.map((item) => item.model) }));
