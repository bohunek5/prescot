import { mkdir, readFile, writeFile } from "node:fs/promises";
import { dirname, resolve } from "node:path";

function argumentValue(name, fallback = "") {
  const index = process.argv.indexOf(name);
  return index === -1 ? fallback : process.argv[index + 1] || fallback;
}

const inputPath = resolve(argumentValue("--input"));
const outputPath = resolve(argumentValue("--output", "data/tim-commercial-catalog.json"));
if (!argumentValue("--input")) throw new Error("Podaj --input z katalogiem zbudowanym z prescot.xml.");
const catalog = JSON.parse(await readFile(inputPath, "utf8"));
if (!String(catalog?.meta?.source || "").includes("prescot.xml")) {
  throw new Error("Źródło migawki handlowej nie jest prescot.xml.");
}
const products = (catalog.products || []).map((product) => ({
  key: product.key,
  ean: product.ean,
  code: product.code,
  price: product.price,
  stock: product.stock,
  measureUnit: product.attributes?.Jednostka || "",
}));
const document = {
  meta: {
    generatedAt: catalog.meta.generatedAt,
    source: catalog.meta.source,
    allOffers: catalog.meta.allOffers,
    activeProducts: catalog.meta.activeProducts,
    purpose: "TIM price, stock and unit only; never description content",
  },
  products,
};
await mkdir(dirname(outputPath), { recursive: true });
await writeFile(outputPath, `${JSON.stringify(document, null, 2)}\n`, "utf8");
console.log(JSON.stringify({ outputPath, products: products.length, source: document.meta.source }));
