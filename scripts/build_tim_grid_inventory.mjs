import { mkdir, readFile, writeFile } from "node:fs/promises";
import { dirname, resolve } from "node:path";

function argumentValue(name, fallback = "") {
  const index = process.argv.indexOf(name);
  return index === -1 ? fallback : process.argv[index + 1] || fallback;
}

const treePath = resolve(argumentValue("--tree", "/tmp/tim-live-main-catalog-complete.json"));
const inputPaths = argumentValue("--inputs", [
  "/tmp/tim-pimcore-grid-prescot.json",
  "/tmp/tim-pimcore-grid-klus.json",
  "/tmp/tim-pimcore-grid-milight.json",
  "/tmp/tim-pimcore-grid-scharfer.json",
].join(",")).split(",").map((value) => resolve(value.trim())).filter(Boolean);
const outputPath = resolve(argumentValue("--output", "/tmp/tim-pimcore-grid-inventory.json"));

const [tree, ...grids] = await Promise.all([
  readFile(treePath, "utf8").then(JSON.parse),
  ...inputPaths.map((path) => readFile(path, "utf8").then(JSON.parse)),
]);
const mainIds = new Set((tree?.pimcoreTree?.nodes || []).map((node) => Number(node.id)).filter(Boolean));
const supplierMainPrefix = "/Produkty/Katalog główny/PRESCOT SPÓŁKA Z-00060865/";
const byId = new Map();

for (const grid of grids) {
  for (const record of grid?.pimcoreGrid?.records || []) {
    const id = Number(record.id);
    if (!String(record.fullpath || "").startsWith(supplierMainPrefix)) continue;
    const stock = Math.max(0, ...(record.stockLevel || []).map((entry) => Number(entry.stockTotalQuantityMz) || 0));
    byId.set(id, {
      id,
      httpStatus: 200,
      general: {
        key: record.filename || "",
        fullpath: record.fullpath || "",
        published: Boolean(record.published),
        locked: Boolean(record.locked),
        versionCount: null,
      },
      ean: String(record.ean || "").trim(),
      manufacturerIndex: String(record.manufacturerIndex || "").trim(),
      timIndex: String(record.timIndex || "").trim(),
      timName: String(record.timName || "").trim(),
      manufacturerMfgid: String(record.manufacturerMfgid || "").trim(),
      manufacturer: String(record.manufacturer || "").trim(),
      state: record.state?.value || record.state || "",
      status: record.status?.value || record.status || "",
      stock,
      productAvailableForSale: record.productAvailableForSale?.value || record.productAvailableForSale || "",
      descriptionHtml: String(record.productDescriptions?.data?.longMarketingDescription || ""),
    });
  }
}

const products = [...byId.values()].sort((left, right) => left.id - right.id);
const report = {
  generatedAt: new Date().toISOString(),
  sourceTree: treePath,
  sourceGrids: inputPaths,
  readOnly: true,
  counts: {
    mainTreeProducts: mainIds.size,
    matchedMainCards: products.length,
    active: products.filter((item) => item.state === "active").length,
    activePositive: products.filter((item) => item.state === "active" && item.stock > 0).length,
    uniqueEans: new Set(products.map((item) => item.ean).filter(Boolean)).size,
  },
  products,
};

await mkdir(dirname(outputPath), { recursive: true });
await writeFile(outputPath, `${JSON.stringify(report, null, 2)}\n`, "utf8");
console.log(JSON.stringify(report.counts, null, 2));
