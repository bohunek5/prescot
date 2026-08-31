import { mkdir, readFile, writeFile } from "node:fs/promises";
import { dirname, resolve } from "node:path";

function argumentValue(name, fallback = "") {
  const index = process.argv.indexOf(name);
  return index === -1 ? fallback : process.argv[index + 1] || fallback;
}

const coverPath = resolve(argumentValue("--cover", "exports/tim/remediation/active-cover-name-queue.json"));
const wycPath = resolve(argumentValue("--wyc", "exports/tim/remediation/active-positive-wyc-name-queue.json"));
const outputPath = resolve(argumentValue("--output", "exports/tim/remediation/final-name-queue.json"));
const [cover, wyc] = await Promise.all([
  readFile(coverPath, "utf8").then(JSON.parse),
  readFile(wycPath, "utf8").then(JSON.parse),
]);

const positive = new Map();
for (const row of wyc?.stages?.all || []) positive.set(Number(row.pimcoreId), { ...row, cleanupKinds: ["wyc"] });
for (const row of cover?.stages?.activePositive || []) {
  const prior = positive.get(Number(row.pimcoreId));
  positive.set(Number(row.pimcoreId), {
    ...row,
    cleanupKinds: prior ? ["wyc", "osłona_bez_osłony"] : ["osłona_bez_osłony"],
  });
}
const zero = new Map((cover?.stages?.activeZero || []).map((row) => [Number(row.pimcoreId), {
  ...row,
  cleanupKinds: ["osłona_bez_osłony"],
}]));

const stages = {
  activePositive: [...positive.values()].sort((left, right) => Number(right.stock) - Number(left.stock)),
  activeZero: [...zero.values()].sort((left, right) => String(left.ean).localeCompare(String(right.ean))),
};
const document = {
  generatedAt: new Date().toISOString(),
  policy: "Final expected TIM names after composing the standalone wyc cleanup and the cover-only contradiction cleanup.",
  counts: Object.fromEntries(Object.entries(stages).map(([name, rows]) => [name, rows.length])),
  stages,
};
await mkdir(dirname(outputPath), { recursive: true });
await writeFile(outputPath, `${JSON.stringify(document, null, 2)}\n`, "utf8");
console.log(JSON.stringify(document.counts));
console.log(outputPath);
