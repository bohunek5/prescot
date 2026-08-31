import { mkdir, readFile, writeFile } from "node:fs/promises";
import { dirname, resolve } from "node:path";

function argumentValue(name, fallback = "") {
  const index = process.argv.indexOf(name);
  return index === -1 ? fallback : process.argv[index + 1] || fallback;
}

const beforePath = resolve(argumentValue("--before", "exports/tim/remediation/full-description-queue-v3.json"));
const afterPath = resolve(argumentValue("--after", "exports/tim/remediation/full-description-queue-v4.json"));
const outputPath = resolve(argumentValue("--output", "exports/tim/remediation/description-delta-queue.json"));
const [before, after] = await Promise.all([
  readFile(beforePath, "utf8").then(JSON.parse),
  readFile(afterPath, "utf8").then(JSON.parse),
]);
const beforeById = new Map(Object.values(before.stages || {}).flat().filter((row) => row.pimcoreId).map((row) => [Number(row.pimcoreId), row]));
const stages = { activePositiveNeedsUpdate: [], activeZeroNeedsUpdate: [] };
for (const stage of Object.keys(stages)) {
  for (const row of after?.stages?.[stage] || []) {
    const prior = beforeById.get(Number(row.pimcoreId));
    if (!prior || String(prior.descriptionHtml || "") === String(row.descriptionHtml || "")) continue;
    stages[stage].push(row);
  }
}
const document = {
  generatedAt: new Date().toISOString(),
  sourceBefore: beforePath,
  sourceAfter: afterPath,
  policy: "Only mapped active cards whose final conservative TIM description differs from the previously applied queue.",
  counts: Object.fromEntries(Object.entries(stages).map(([name, rows]) => [name, rows.length])),
  stages,
};
await mkdir(dirname(outputPath), { recursive: true });
await writeFile(outputPath, `${JSON.stringify(document, null, 2)}\n`, "utf8");
console.log(JSON.stringify(document.counts));
console.log(outputPath);
