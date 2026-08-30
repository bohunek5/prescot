import { mkdir, readFile, writeFile } from "node:fs/promises";
import { dirname, resolve } from "node:path";

function argumentValue(name, fallback = "") {
  const index = process.argv.indexOf(name);
  return index === -1 ? fallback : process.argv[index + 1] || fallback;
}

const queuePath = resolve(argumentValue("--queue", "/tmp/tim-pilots-all/active-description-pilot.json"));
const searchPath = resolve(argumentValue("--search", "/tmp/tim-live-fulltext-skipped39.json"));
const outputPath = resolve(argumentValue("--output", "exports/tim/remediation/description-remediation.json"));

const [queueDocument, searchDocument] = await Promise.all([
  readFile(queuePath, "utf8").then(JSON.parse),
  readFile(searchPath, "utf8").then(JSON.parse),
]);

const products = queueDocument?.stages?.pilotAll || [];
const productByEan = new Map(products.map((product) => [String(product.ean), product]));
const buckets = {
  exactActivePositive: [],
  exactActiveZero: [],
  exactBuffer: [],
  codeAliasActive: [],
  identityConflict: [],
  noExactEanHit: [],
};

for (const search of searchDocument.pimcoreSearch || []) {
  const product = productByEan.get(String(search.term));
  if (!product) continue;
  const exactEanRecords = (search.records || []).filter((record) => String(record.ean) === String(product.ean));
  if (!exactEanRecords.length) {
    buckets.noExactEanHit.push({ ...product, reason: "no_published_exact_ean_hit" });
    continue;
  }
  if (exactEanRecords.length !== 1) {
    buckets.identityConflict.push({ ...product, reason: "multiple_published_exact_ean_hits", hits: exactEanRecords });
    continue;
  }
  const hit = exactEanRecords[0];
  const remapped = {
    ...product,
    pimcoreId: Number(hit.id),
    timIndex: hit.timIndex || "",
    currentTimName: hit.timName || "",
    liveStock: hit.stock,
    liveState: hit.state,
    liveStatus: hit.status,
    liveManufacturerCode: hit.manufacturerIndex || "",
    previousPimcoreId: Number(product.pimcoreId) || null,
    matchMethod: "published_exact_ean",
  };
  if (String(hit.manufacturerIndex) !== String(product.manufacturerCode)) {
    const sourceWords = String(product.name || "").toLocaleLowerCase("pl").split(/[^\p{L}\p{N}]+/u).filter((word) => word.length >= 4);
    const liveName = String(hit.timName || "").toLocaleLowerCase("pl");
    const overlap = sourceWords.filter((word) => liveName.includes(word));
    const severeConflict = overlap.length < Math.min(2, sourceWords.length);
    (severeConflict ? buckets.identityConflict : buckets.codeAliasActive).push({
      ...remapped,
      reason: severeConflict ? "ean_collision_name_and_code_conflict" : "manufacturer_code_alias_requires_review",
      nameWordOverlap: overlap,
    });
    continue;
  }
  if (hit.state === "active" && Number(hit.stock) > 0) buckets.exactActivePositive.push(remapped);
  else if (hit.state === "active") buckets.exactActiveZero.push(remapped);
  else buckets.exactBuffer.push(remapped);
}

const document = {
  generatedAt: new Date().toISOString(),
  sourceQueue: queuePath,
  sourceSearch: searchPath,
  policy: "Automatic queue only when one published card has exact EAN, exact manufacturer code, active state and positive live stock.",
  counts: Object.fromEntries(Object.entries(buckets).map(([key, value]) => [key, value.length])),
  stages: {
    exactActivePositive: buckets.exactActivePositive,
    exactActivePositivePilot1: buckets.exactActivePositive.slice(0, 1),
    exactActivePositivePilot10: buckets.exactActivePositive.slice(0, 10),
    ...buckets,
  },
};

await mkdir(dirname(outputPath), { recursive: true });
await writeFile(outputPath, `${JSON.stringify(document, null, 2)}\n`, "utf8");
console.log(JSON.stringify(document.counts, null, 2));
