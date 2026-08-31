import { mkdir, readFile, writeFile } from "node:fs/promises";
import { dirname, resolve } from "node:path";

function argumentValue(name, fallback = "") {
  const index = process.argv.indexOf(name);
  return index === -1 ? fallback : process.argv[index + 1] || fallback;
}

const manifestPath = resolve(argumentValue("--manifest", "exports/tim/tim-manifest.json"));
const baseQueuePath = resolve(argumentValue("--base-queue", "exports/tim/remediation/full-description-queue-v3.json"));
const searchPath = resolve(argumentValue("--search", "/tmp/tim-live-fulltext-missing417.json"));
const bufferTreePath = resolve(argumentValue("--buffer-tree", "/tmp/tim-live-buffer-prescot-complete.json"));
const outputPath = resolve(argumentValue("--output", "exports/tim/remediation/supplemental-description-queue.json"));

const [manifest, baseQueue, searchAudit, bufferAudit] = await Promise.all([
  readFile(manifestPath, "utf8").then(JSON.parse),
  readFile(baseQueuePath, "utf8").then(JSON.parse),
  readFile(searchPath, "utf8").then(JSON.parse),
  readFile(bufferTreePath, "utf8").then(JSON.parse),
]);
let bufferPayload = {};
try { bufferPayload = JSON.parse(bufferAudit?.pimcoreGet?.body || "{}"); } catch {}
const bufferIds = new Set((bufferPayload.nodes || []).map((row) => Number(row.id)).filter(Boolean));

const manifestByEan = new Map((manifest.products || []).filter((row) => row.ean).map((row) => [String(row.ean), row]));
const sourceRows = baseQueue?.stages?.missingInMainCatalog;
if (!Array.isArray(sourceRows)) throw new Error("Brak etapu missingInMainCatalog w kolejce bazowej.");
const sourceByEan = new Map(sourceRows.filter((row) => row.ean).map((row) => [String(row.ean), row]));
const alreadyMappedIds = new Set([
  ...(baseQueue?.stages?.activePositiveNeedsUpdate || []),
  ...(baseQueue?.stages?.activePositiveCurrent || []),
  ...(baseQueue?.stages?.activeZeroNeedsUpdate || []),
  ...(baseQueue?.stages?.activeZeroCurrent || []),
].map((row) => Number(row.pimcoreId)).filter(Boolean));

const stages = {
  activePositiveNeedsUpdate: [],
  activeZeroNeedsUpdate: [],
  bufferNewNeedsUpdate: [],
  bufferApprovalNeedsUpdate: [],
  manufacturerCodeAlias: [],
  inactiveDiscontinued: [],
  ambiguousExactEan: [],
  missingInTimSearch: [],
  invalidSource: [],
};
const searches = new Map((searchAudit.pimcoreSearch || []).map((row) => [String(row.term), row]));

for (const [ean, source] of sourceByEan) {
  const product = manifestByEan.get(ean);
  if (!product?.descriptionHtml || !product.manufacturerCode) {
    stages.invalidSource.push({ ean, productKey: source.productKey, reason: "current_manifest_missing_description_or_manufacturer_code" });
    continue;
  }
  const search = searches.get(ean);
  if (!search || Number(search.status) !== 200) {
    stages.invalidSource.push({ ...product, reason: "search_missing_or_failed" });
    continue;
  }
  const exactHits = (search.records || []).filter((record) => String(record.ean || "") === ean);
  if (exactHits.length === 0) {
    stages.missingInTimSearch.push({ ...product, reason: "no_exact_ean_in_fulltext_search" });
    continue;
  }
  if (exactHits.length !== 1) {
    stages.ambiguousExactEan.push({ ...product, reason: "multiple_exact_ean_hits", hits: exactHits });
    continue;
  }
  const card = exactHits[0];
  const record = {
    ...product,
    pimcoreId: Number(card.id),
    timIndex: String(card.timIndex || ""),
    currentTimName: String(card.timName || ""),
    liveState: String(card.state || ""),
    liveStatus: String(card.status || ""),
    liveStock: Number(card.stock) || 0,
    liveManufacturerCode: String(card.manufacturerIndex || ""),
    liveLocked: Boolean(card.locked),
    matchMethod: "fulltext_search_single_exact_ean",
  };
  if (alreadyMappedIds.has(record.pimcoreId)) {
    stages.ambiguousExactEan.push({ ...record, reason: "object_already_present_in_base_queue" });
    continue;
  }
  if (record.liveManufacturerCode !== String(product.manufacturerCode)) {
    stages.manufacturerCodeAlias.push({ ...record, reason: "manufacturer_code_mismatch" });
    continue;
  }
  if (bufferIds.has(record.pimcoreId) && card.published === true && record.liveState === "new") {
    stages.bufferNewNeedsUpdate.push({ ...record, reason: "exact_card_in_supplier_buffer" });
    continue;
  }
  if (bufferIds.has(record.pimcoreId) && card.published === true && record.liveState === "new_for_approval") {
    stages.bufferApprovalNeedsUpdate.push({ ...record, reason: "exact_card_in_supplier_buffer_approval_state" });
    continue;
  }
  if (card.published !== true || record.liveState !== "active") {
    stages.inactiveDiscontinued.push({ ...record, reason: "not_published_active_or_supplier_buffer" });
    continue;
  }
  stages[record.liveStock > 0 ? "activePositiveNeedsUpdate" : "activeZeroNeedsUpdate"].push(record);
}

stages.activePositiveNeedsUpdate.sort((left, right) => right.liveStock - left.liveStock);
stages.activeZeroNeedsUpdate.sort((left, right) => left.ean.localeCompare(right.ean));
stages.bufferNewNeedsUpdate.sort((left, right) => left.ean.localeCompare(right.ean));
stages.bufferApprovalNeedsUpdate.sort((left, right) => left.ean.localeCompare(right.ean));
const document = {
  generatedAt: new Date().toISOString(),
  sourceManifest: manifestPath,
  sourceBaseQueue: baseQueuePath,
  sourceSearchAudit: searchPath,
  sourceBufferTree: bufferTreePath,
  policy: "Supplement only one full-text hit with exact EAN, exact manufacturer trade index, published active state, and an object ID absent from the base queue.",
  counts: Object.fromEntries(Object.entries(stages).map(([name, rows]) => [name, rows.length])),
  stages,
};

await mkdir(dirname(outputPath), { recursive: true });
await writeFile(outputPath, `${JSON.stringify(document, null, 2)}\n`, "utf8");
console.log(JSON.stringify(document.counts, null, 2));
console.log(outputPath);
