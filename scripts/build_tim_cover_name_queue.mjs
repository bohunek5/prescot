import { mkdir, readFile, writeFile } from "node:fs/promises";
import { dirname, resolve } from "node:path";

function argumentValue(name, fallback = "") {
  const index = process.argv.indexOf(name);
  return index === -1 ? fallback : process.argv[index + 1] || fallback;
}

const inventoryPath = resolve(argumentValue("--inventory", "/private/tmp/tim-pimcore-grid-inventory.json"));
const outputPath = resolve(argumentValue("--output", "exports/tim/remediation/active-cover-name-queue.json"));
const inventory = JSON.parse(await readFile(inventoryPath, "utf8"));
const products = Array.isArray(inventory.products) ? inventory.products : [];
const suffix = /\s*\(\s*bez osłony\s*\)\s*$/iu;
const allNames = new Map();
for (const product of products) {
  const key = String(product.timName || "").trim().toLocaleLowerCase("pl");
  if (!key) continue;
  if (!allNames.has(key)) allNames.set(key, []);
  allNames.get(key).push(Number(product.id));
}

const candidates = products
  .filter((product) => product.state === "active"
    && product.general?.published === true
    && /^osłona\b/iu.test(String(product.timName || ""))
    && suffix.test(String(product.timName || "")))
  .map((product) => {
    const beforeName = String(product.timName || "").trim();
    const afterName = beforeName.replace(suffix, "").trim();
    const collisions = (allNames.get(afterName.toLocaleLowerCase("pl")) || []).filter((id) => id !== Number(product.id));
    return {
      pimcoreId: Number(product.id),
      timIndex: String(product.timIndex || ""),
      ean: String(product.ean || ""),
      manufacturerCode: String(product.manufacturerIndex || ""),
      stock: Number(product.stock) || 0,
      beforeName,
      afterName,
      liveLocked: product.general?.locked === true,
      collisions,
    };
  });

const targetCounts = new Map();
for (const item of candidates) {
  const key = item.afterName.toLocaleLowerCase("pl");
  targetCounts.set(key, (targetCounts.get(key) || 0) + 1);
}

const blocked = [];
const eligible = [];
for (const item of candidates) {
  const reasons = [];
  if (!item.pimcoreId || !item.timIndex || !item.ean || !item.manufacturerCode) reasons.push("missing_identity");
  if (!item.afterName || item.afterName === item.beforeName) reasons.push("invalid_target_name");
  if (item.collisions.length) reasons.push("target_name_already_exists");
  if ((targetCounts.get(item.afterName.toLocaleLowerCase("pl")) || 0) > 1) reasons.push("duplicate_target_in_queue");
  if (item.liveLocked) reasons.push("locked_in_inventory_snapshot");
  if (reasons.length) blocked.push({ ...item, reasons });
  else eligible.push(item);
}

eligible.sort((left, right) => right.stock - left.stock || left.beforeName.localeCompare(right.beforeName, "pl"));
const activePositive = eligible.filter((item) => item.stock > 0);
const activeZero = eligible.filter((item) => item.stock <= 0);
const document = {
  generatedAt: new Date().toISOString(),
  sourceInventory: inventoryPath,
  policy: "Only active, published names beginning with Osłona and ending with (bez osłony) are eligible. Profile names are not changed. Existing or duplicate target names are blocked.",
  counts: {
    candidates: candidates.length,
    activePositive: activePositive.length,
    activeZero: activeZero.length,
    blocked: blocked.length,
  },
  stages: {
    pilot1: activePositive.slice(0, 1),
    pilot10: activePositive.slice(0, 10),
    activePositive,
    activeZero,
    blocked,
  },
};

await mkdir(dirname(outputPath), { recursive: true });
await writeFile(outputPath, `${JSON.stringify(document, null, 2)}\n`, "utf8");
console.log(JSON.stringify(document.counts));
