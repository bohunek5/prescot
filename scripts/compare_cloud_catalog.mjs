#!/usr/bin/env node

import { mkdir, readFile, writeFile } from "node:fs/promises";
import { dirname, resolve } from "node:path";

function argumentValue(name, fallback = "") {
  const index = process.argv.indexOf(name);
  return index >= 0 ? process.argv[index + 1] || fallback : fallback;
}

const currentPath = resolve(argumentValue("--current", "data/catalog.json"));
const freshPath = resolve(argumentValue("--fresh"));
if (!argumentValue("--fresh")) throw new Error("Podaj --fresh z katalogiem zbudowanym ze świeżego XML.");
const reportPath = resolve(argumentValue("--report", "/tmp/prescot-cloud-audit.json"));
const [current, fresh] = await Promise.all([
  readFile(currentPath, "utf8").then((value) => JSON.parse(value)),
  readFile(freshPath, "utf8").then((value) => JSON.parse(value)),
]);

const fields = ["name", "category", "categoryRoot", "producer", "code", "manufacturerCode", "ean", "url", "price", "stock", "image", "images", "attributes", "sourceDescription"];
const currentByKey = new Map(current.products.map((product) => [product.key, product]));
const freshByKey = new Map(fresh.products.map((product) => [product.key, product]));
const added = fresh.products.filter((product) => !currentByKey.has(product.key)).map((product) => product.key);
const removed = current.products.filter((product) => !freshByKey.has(product.key)).map((product) => product.key);
const changed = [];
const changedFieldCounts = {};
for (const [key, product] of currentByKey) {
  const next = freshByKey.get(key);
  if (!next) continue;
  const changedFields = fields.filter((field) => JSON.stringify(product[field]) !== JSON.stringify(next[field]));
  if (!changedFields.length) continue;
  changed.push({ key, changedFields });
  for (const field of changedFields) changedFieldCounts[field] = (changedFieldCounts[field] || 0) + 1;
}
const report = {
  checkedAt: new Date().toISOString(),
  currentGeneratedAt: current.meta.generatedAt,
  freshGeneratedAt: fresh.meta.generatedAt,
  currentProducts: current.products.length,
  freshProducts: fresh.products.length,
  added,
  removed,
  changed,
  changedFieldCounts,
  drift: added.length > 0 || removed.length > 0 || changed.length > 0,
};
await mkdir(dirname(reportPath), { recursive: true });
await writeFile(reportPath, `${JSON.stringify(report, null, 2)}\n`, "utf8");
console.log(`Chmura: ${fresh.products.length} aktywnych; dodane ${added.length}; usunięte ${removed.length}; zmienione ${changed.length}.`);
console.log(`Raport: ${reportPath}`);
if (report.drift) process.exitCode = 2;
