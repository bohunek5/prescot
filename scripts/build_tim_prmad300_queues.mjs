#!/usr/bin/env node

import { readFile, writeFile } from "node:fs/promises";
import { resolve } from "node:path";
import { generateDescription, plainTextFromHtml } from "../description-engine.js";
import { validateTimDescription } from "./tim_description_quality.mjs";

const catalog = JSON.parse(await readFile(resolve("data/catalog.json"), "utf8"));
const product = catalog.products.find((item) => String(item.ean || "") === "5905475368127");
if (!product || product.manufacturerCode !== "PR-MAD300-1224") throw new Error("Brak dokładnego PR-MAD300-1224 w katalogu opisów.");

const descriptionHtml = generateDescription(product, "tim");
const text = plainTextFromHtml(descriptionHtml);
const errors = validateTimDescription(product, descriptionHtml);
if (errors.length) throw new Error(errors.join(","));
if (!text.includes("PR-MAD300-1224") || !text.includes("12V/24V") || !text.includes("25A/12.5A")) {
  throw new Error("Opis nie zawiera dokładnych parametrów wariantu 300 W.");
}
if (text.includes(product.ean) || text.includes(product.code)) throw new Error("Opis zawiera EAN albo wewnętrzny indeks katalogowy.");

const root = "/Users/karolbohdanowicz/Desktop/_PRESCOT/_2026";
const documents = {
  generatedAt: new Date().toISOString(),
  items: [{
    id: 15907533,
    ean: "5905475368127",
    model: "PR-MAD300-1224",
    timListPrice: 55,
    xmlPrice: 55,
    xmlStock: 157,
    documents: {
      certifications: {
        source: `${root}/TIM.PL/TIM - karty ce/Zasilacze LED/CE Prescot zasilacze PR-MADXX-1224.pdf`,
        filename: "CE_Prescot_zasilacze_PR-MADXX-1224.pdf",
      },
      instructions: {
        source: `${root}/Zasilacze 1224/Instrukcja PR-MADXX-1224.pdf`,
        filename: "Instrukcja_PR-MADXX-1224.pdf",
      },
      dataSheet: {
        source: `${root}/TIM.PL/TIM - karty ce/Karty katalogowe/Zasilacze LED/PR-MAD-AUTODETEKCJA/PR-MAD300-1224.pdf`,
        filename: "PR-MAD300-1224_karta_katalogowa.pdf",
      },
    },
  }],
};
const descriptions = {
  generatedAt: new Date().toISOString(),
  sourceCatalog: resolve("data/catalog.json"),
  stages: {
    bufferNewNeedsUpdate: [{
      pimcoreId: 15907533,
      ean: "5905475368127",
      manufacturerCode: "PR-MAD300-1224",
      name: product.name,
      descriptionHtml,
    }],
  },
};
const activation = {
  generatedAt: new Date().toISOString(),
  items: [{
    id: 15907533,
    ean: "5905475368127",
    model: "PR-MAD300-1224",
    price: 55,
    xmlStock: 157,
    requiredRelations: ["dataSheet", "certifications", "instructions"],
  }],
};

await writeFile(resolve("exports/tim/remediation/pr-mad300-documents-queue-2026-09-01.json"), `${JSON.stringify(documents, null, 2)}\n`);
await writeFile(resolve("exports/tim/remediation/pr-mad300-description-queue-2026-09-01.json"), `${JSON.stringify(descriptions, null, 2)}\n`);
await writeFile(resolve("exports/tim/remediation/pr-mad300-activation-queue-2026-09-01.json"), `${JSON.stringify(activation, null, 2)}\n`);
console.log(JSON.stringify({ model: product.manufacturerCode, descriptionChars: descriptionHtml.length, queues: 3 }));
