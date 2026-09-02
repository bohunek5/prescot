#!/usr/bin/env node

import { readFile, writeFile } from "node:fs/promises";
import { resolve } from "node:path";

const sourcePath = resolve("exports/tim/remediation/buffer-strip-catalog-ce-queue-2026-09-01.json");
const outputPath = resolve("exports/tim/remediation/buffer-strip-activation-queue-2026-09-01.json");
const source = JSON.parse(await readFile(sourcePath, "utf8"));
const completeModels = new Set([
  "12EC480WW275",
  "24EC320WW1IP67",
  "24EC320NW1IP67",
  "24EC320W1IP67",
  "ES009-025-4-W20K",
  "ES009-050-4-W20K",
]);

const items = source.items
  .filter((item) => completeModels.has(item.model))
  .map((item) => ({
    id: Number(item.id),
    ean: String(item.ean),
    model: String(item.model),
    price: Number(item.xmlPrice),
    xmlStock: Number(item.xmlStock),
    requiredRelations: [
      "dataSheet",
      "certifications",
      "energyClassLabels",
      "energyTechnicalCards",
    ],
  }));

if (items.length !== completeModels.size) throw new Error(`Niepełna kolejka aktywacji: ${items.length}/${completeModels.size}`);
await writeFile(outputPath, `${JSON.stringify({ generatedAt: new Date().toISOString(), source: sourcePath, items }, null, 2)}\n`, "utf8");
console.log(JSON.stringify({ output: outputPath, items: items.length }, null, 2));
