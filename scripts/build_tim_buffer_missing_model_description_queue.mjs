#!/usr/bin/env node

import { writeFile } from "node:fs/promises";
import { resolve } from "node:path";
import { generateDescription, plainTextFromHtml } from "../description-engine.js";
import { validateTimDescription } from "./tim_description_quality.mjs";

const source = [
  {
    pimcoreId: 10047458,
    ean: "5901854562247",
    manufacturerCode: "36W/865BL",
    name: "Świetlówka liniowa T8 36W/865 Bellight",
    category: "Świetlówki",
    categoryRoot: "Świetlówki",
  },
  {
    pimcoreId: 10651076,
    ean: "5905475366994",
    manufacturerCode: "24D160-9-4080-1010",
    name: "Taśma Delux 24V 160led 4000K 420/840/1480lm SMD2835 PL7Y 3in1 10m",
    category: "Taśmy LED",
    categoryRoot: "Taśmy LED",
  },
  {
    pimcoreId: 10651109,
    ean: "5905475367007",
    manufacturerCode: "24D160-9-4080-101",
    name: "Taśma Delux 24V 160led 4000K 420/840/1480lm SMD2835 PL7Y 3in1 1m",
    category: "Taśmy LED",
    categoryRoot: "Taśmy LED",
  },
];

const items = source.map((product) => {
  const descriptionHtml = generateDescription({ ...product, code: "", attributes: {} }, "tim");
  const text = plainTextFromHtml(descriptionHtml);
  const errors = validateTimDescription(product, descriptionHtml);
  if (errors.length) throw new Error(`${product.manufacturerCode}: ${errors.join(",")}`);
  if (!text.includes(product.manufacturerCode) || text.includes(product.ean)) {
    throw new Error(`${product.manufacturerCode}: błędna publiczna tożsamość opisu.`);
  }
  return { ...product, descriptionHtml };
});

const outputPath = resolve("exports/tim/remediation/buffer-missing-model-description-queue-2026-09-01.json");
const output = {
  generatedAt: new Date().toISOString(),
  policy: "Exact live PIM ID, EAN and trade index; only description is eligible. No internal code or EAN in copy.",
  stages: { bufferNewNeedsUpdate: items },
};
await writeFile(outputPath, `${JSON.stringify(output, null, 2)}\n`, "utf8");
console.log(JSON.stringify({ output: outputPath, items: items.length }, null, 2));
