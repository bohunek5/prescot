import { mkdir, readFile, writeFile } from "node:fs/promises";
import { dirname, resolve } from "node:path";

function argumentValue(name, fallback = "") {
  const index = process.argv.indexOf(name);
  return index === -1 ? fallback : process.argv[index + 1] || fallback;
}

function canonicalDescription(html) {
  return String(html || "").trim().replace(/^<section>\s*/i, "").replace(/\s*<\/section>$/i, "").trim();
}

function normalizedStoredDescription(html) {
  return String(html || "")
    .replace(/&quot;|&#0*34;|&#x0*22;/gi, '"')
    .replace(/&apos;|&#0*39;|&#x0*27;/gi, "'")
    .trim();
}

function descriptionsEqual(left, right) {
  return normalizedStoredDescription(left) === normalizedStoredDescription(right);
}

const manifestPath = resolve(argumentValue("--manifest", "exports/tim/tim-manifest.json"));
const inventoryPath = resolve(argumentValue("--inventory", "/tmp/tim-pimcore-inventory-snapshot.json"));
const outputPath = resolve(argumentValue("--output", "exports/tim/remediation/full-description-queue.json"));

const [manifest, inventory] = await Promise.all([
  readFile(manifestPath, "utf8").then(JSON.parse),
  readFile(inventoryPath, "utf8").then(JSON.parse),
]);

const byEan = new Map();
for (const card of inventory.products || []) {
  if (!card.ean || card.httpStatus !== 200 || !card.general?.published) continue;
  if (!byEan.has(card.ean)) byEan.set(card.ean, []);
  byEan.get(card.ean).push(card);
}

const stages = {
  activePositiveNeedsUpdate: [],
  activePositiveCurrent: [],
  activeZeroNeedsUpdate: [],
  activeZeroCurrent: [],
  exactInactive: [],
  manufacturerCodeAlias: [],
  identityConflict: [],
  missingInMainCatalog: [],
  invalidSource: [],
};

for (const product of manifest.products || []) {
  if (product.status === "out_of_scope") continue;
  const expectedHtml = canonicalDescription(product.descriptionHtml);
  if (!/^\d{8,14}$/.test(String(product.ean || "")) || !product.manufacturerCode || !expectedHtml) {
    stages.invalidSource.push({ productKey: product.productKey, ean: product.ean, reason: "missing_ean_code_or_description" });
    continue;
  }
  const hits = byEan.get(String(product.ean)) || [];
  if (!hits.length) {
    stages.missingInMainCatalog.push({ ...product, reason: "no_published_exact_ean_in_main_catalog" });
    continue;
  }
  if (hits.length !== 1) {
    stages.identityConflict.push({ ...product, reason: "multiple_published_exact_ean_hits", hits });
    continue;
  }
  const card = hits[0];
  const record = {
    ...product,
    pimcoreId: card.id,
    timIndex: card.timIndex,
    currentTimName: card.timName,
    liveState: card.state,
    liveStatus: card.status,
    liveStock: card.stock,
    liveManufacturerCode: card.manufacturerIndex,
    liveLocked: card.general.locked,
    liveVersionCount: card.general.versionCount,
    matchMethod: "published_main_catalog_exact_ean",
  };
  if (String(card.manufacturerIndex) !== String(product.manufacturerCode)) {
    stages.manufacturerCodeAlias.push({ ...record, reason: "manufacturer_code_mismatch" });
    continue;
  }
  if (card.state !== "active") {
    stages.exactInactive.push(record);
    continue;
  }
  const current = descriptionsEqual(card.descriptionHtml, expectedHtml);
  if (card.stock > 0) stages[current ? "activePositiveCurrent" : "activePositiveNeedsUpdate"].push(record);
  else stages[current ? "activeZeroCurrent" : "activeZeroNeedsUpdate"].push(record);
}

stages.activePositiveNeedsUpdate.sort((left, right) => Number(right.liveStock) - Number(left.liveStock));
stages.activeZeroNeedsUpdate.sort((left, right) => String(left.ean).localeCompare(String(right.ean)));

const document = {
  generatedAt: new Date().toISOString(),
  sourceManifest: manifestPath,
  sourceInventory: inventoryPath,
  policy: "Only one published main-catalog card with exact EAN, exact manufacturer code and active state is eligible. Positive stock is processed first.",
  counts: Object.fromEntries(Object.entries(stages).map(([key, value]) => [key, value.length])),
  stages,
};

await mkdir(dirname(outputPath), { recursive: true });
await writeFile(outputPath, `${JSON.stringify(document, null, 2)}\n`, "utf8");
console.log(JSON.stringify(document.counts, null, 2));
