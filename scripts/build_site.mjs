#!/usr/bin/env node

import { copyFile, mkdir, readFile, rm, writeFile } from "node:fs/promises";
import { dirname, resolve } from "node:path";

const root = resolve(new URL("..", import.meta.url).pathname);
const output = resolve(process.argv[2] || "dist");
const files = [
  "index.html",
  "styles.css",
  "app.js",
  "description-engine.js",
  "prescot_logo.svg",
  "ikona wapro.png",
  "ikona tim.jpg",
  "ikona allegro.png",
  "ikona_shoper.svg",
  "data/catalog.json",
  "data/seo-descriptions.json",
  "data/quality-report.json",
  "data/tim-status.json",
];

await rm(output, { recursive: true, force: true });
for (const file of files) {
  const target = resolve(output, file);
  await mkdir(dirname(target), { recursive: true });
  await copyFile(resolve(root, file), target);
}

const sourceOverrides = JSON.parse(await readFile(resolve(root, "data/manual-overrides.json"), "utf8"));
const products = {};
const descriptionIds = new Set();
for (const [productKey, assignment] of Object.entries(sourceOverrides.products || {})) {
  const filtered = {};
  const shoperId = assignment.wapro || "";
  const shoperHtml = sourceOverrides.descriptions?.[shoperId] || "";
  if (shoperId && shoperHtml && !shoperHtml.includes('class="blog-grid"')) {
    filtered.wapro = shoperId;
    descriptionIds.add(shoperId);
  }
  const allegroId = assignment.allegro || "";
  if (allegroId && allegroId !== assignment.wapro && sourceOverrides.descriptions?.[allegroId]) {
    filtered.allegro = allegroId;
    descriptionIds.add(allegroId);
  }
  if (Object.keys(filtered).length) products[productKey] = filtered;
}
const overrides = {
  meta: {
    ...sourceOverrides.meta,
    deploymentFilteredAt: new Date().toISOString(),
    note: "Publiczny plik zawiera wyłącznie ręczne opisy faktycznie używane przez panel.",
  },
  products,
  descriptions: Object.fromEntries([...descriptionIds].map((id) => [id, sourceOverrides.descriptions[id]])),
};
await writeFile(resolve(output, "data/manual-overrides.json"), `${JSON.stringify(overrides)}\n`, "utf8");
await writeFile(resolve(output, ".nojekyll"), "", "utf8");

console.log(`Build strony: ${output}`);
console.log(`Pliki publiczne: ${files.length + 2}; ręczne opisy: ${descriptionIds.size}.`);
