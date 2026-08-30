import { mkdir, readFile, writeFile } from "node:fs/promises";
import { dirname, resolve } from "node:path";

function argumentValue(name, fallback = "") {
  const index = process.argv.indexOf(name);
  return index === -1 ? fallback : process.argv[index + 1] || fallback;
}

function cleanName(value) {
  return String(value || "")
    .replace(/^wyc\.?\s*/iu, "")
    .replace(/\s+wyc\.?(?=\s|$)/giu, "")
    .trim();
}

const inputPath = resolve(argumentValue("--input", "/tmp/tim-live-wyc-objects.json"));
const outputPath = resolve(argumentValue("--output", "exports/tim/remediation/active-positive-wyc-name-queue.json"));
const source = JSON.parse(await readFile(inputPath, "utf8"));
const queue = [];
const excluded = [];
for (const item of source.pimcoreObjects || []) {
  const data = item.data || {};
  const state = data.state?.value || data.state || "";
  const stock = Math.max(0, ...(data.stockLevel || []).map((entry) => Number(entry.stockTotalQuantityMz) || 0));
  const beforeName = String(data.timName || "");
  const afterName = cleanName(beforeName);
  const record = {
    pimcoreId: Number(item.id),
    timIndex: String(data.timIndex || ""),
    ean: String(data.ean || ""),
    manufacturerCode: String(data.manufacturerIndex || ""),
    beforeName,
    afterName,
    stock,
    state,
    published: Boolean(item.general?.published),
    locked: Boolean(item.general?.locked),
    versionCount: item.general?.versionCount ?? null,
  };
  const eligible = item.status === 200
    && state === "active"
    && stock > 0
    && item.general?.published === true
    && beforeName !== afterName
    && Boolean(record.timIndex);
  (eligible ? queue : excluded).push({ ...record, reason: eligible ? "eligible" : "not_active_positive_published_or_no_name_change" });
}
queue.sort((left, right) => right.stock - left.stock || left.pimcoreId - right.pimcoreId);
const document = {
  generatedAt: new Date().toISOString(),
  source: inputPath,
  policy: "Remove only the standalone token wyc or wyc. from timName on published active cards with positive live stock.",
  counts: { inspected: (source.pimcoreObjects || []).length, eligible: queue.length, excluded: excluded.length },
  stages: { pilot1: queue.slice(0, 1), pilot10: queue.slice(0, 10), all: queue },
  excluded,
};
await mkdir(dirname(outputPath), { recursive: true });
await writeFile(outputPath, `${JSON.stringify(document, null, 2)}\n`, "utf8");
console.log(JSON.stringify(document.counts, null, 2));
