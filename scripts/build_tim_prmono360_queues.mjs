#!/usr/bin/env node

import { readFile, writeFile } from "node:fs/promises";
import { resolve } from "node:path";
import { generateDescription, plainTextFromHtml } from "../description-engine.js";
import { validateTimDescription } from "./tim_description_quality.mjs";

const catalog = JSON.parse(await readFile(resolve("data/catalog.json"), "utf8"));
const product = catalog.products.find((item) => String(item.ean || "") === "5904162806294");
if (!product || product.manufacturerCode !== "PR-MONO-360-WALL-P") throw new Error("Brak dokładnego PR-MONO-360-WALL-P w katalogu opisów.");

const descriptionHtml = generateDescription(product, "tim");
const text = plainTextFromHtml(descriptionHtml);
const errors = validateTimDescription(product, descriptionHtml);
if (errors.length) throw new Error(errors.join(","));
if (!text.includes("PR-MONO-360-WALL-P") || !text.includes("12-24V") || !text.includes("1x30A")) {
  throw new Error("Opis nie zawiera dokładnych parametrów sterownika.");
}
if (text.includes(product.ean) || text.includes(product.code)) throw new Error("Opis zawiera EAN albo wewnętrzny indeks katalogowy.");

const docsRoot = "/Users/karolbohdanowicz/Desktop/_PRESCOT/_2026/TIM.PL/TIM - karty ce";
const documents = {
  generatedAt: new Date().toISOString(),
  sourceProductUrl: "https://prescot.com.pl/pl/p/Sterownik-LED-Mono-1x30A-potencjometr-12-24V-Prescot/19233",
  items: [{
    id: 15907499,
    ean: "5904162806294",
    model: "PR-MONO-360-WALL-P",
    timListPrice: 37,
    xmlPrice: 37,
    xmlStock: 8,
    documents: {
      certifications: {
        source: `${docsRoot}/Sterowniki LED/Prescot Sterowniki CE.pdf`,
        filename: "CE_Prescot_Sterowniki_2026.pdf",
      },
      dataSheet: {
        source: resolve("tmp/pdfs/priorities/Dimmer-Hookup-Prescot-LED.pdf"),
        filename: "PR-MONO-360-WALL-P_Dimmer-Hookup_karta.pdf",
      },
    },
  }],
};
const descriptions = {
  generatedAt: new Date().toISOString(),
  sourceCatalog: resolve("data/catalog.json"),
  stages: {
    bufferNewNeedsUpdate: [{
      pimcoreId: 15907499,
      ean: "5904162806294",
      manufacturerCode: "PR-MONO-360-WALL-P",
      name: product.name,
      descriptionHtml,
    }],
  },
};
const activation = {
  generatedAt: new Date().toISOString(),
  items: [{
    id: 15907499,
    ean: "5904162806294",
    model: "PR-MONO-360-WALL-P",
    price: 37,
    xmlStock: 8,
    requiredRelations: ["dataSheet", "certifications"],
  }],
};

await writeFile(resolve("exports/tim/remediation/pr-mono-360-documents-queue-2026-09-01.json"), `${JSON.stringify(documents, null, 2)}\n`);
await writeFile(resolve("exports/tim/remediation/pr-mono-360-description-queue-2026-09-01.json"), `${JSON.stringify(descriptions, null, 2)}\n`);
await writeFile(resolve("exports/tim/remediation/pr-mono-360-activation-queue-2026-09-01.json"), `${JSON.stringify(activation, null, 2)}\n`);
console.log(JSON.stringify({ model: product.manufacturerCode, descriptionChars: descriptionHtml.length, queues: 3 }));
