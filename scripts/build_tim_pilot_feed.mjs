import { mkdir, readFile, writeFile } from "node:fs/promises";
import { dirname, resolve } from "node:path";

function argumentValue(name, fallback = "") {
  const index = process.argv.indexOf(name);
  return index === -1 ? fallback : process.argv[index + 1] || fallback;
}

function text(value) {
  return String(value ?? "").replace(/^\uFEFF/, "").trim();
}

function decodeXml(value) {
  return text(value)
    .replaceAll("&amp;", "&")
    .replaceAll("&quot;", '"')
    .replaceAll("&apos;", "'")
    .replaceAll("&lt;", "<")
    .replaceAll("&gt;", ">");
}

function cdata(value) {
  return `<![CDATA[${String(value ?? "").replaceAll("]]>", "]]]]><![CDATA[>")}]]>`;
}

function extractCdata(block, pattern) {
  return text(block.match(pattern)?.[1] || "");
}

function attribute(block, name) {
  const escaped = name.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  return extractCdata(block, new RegExp(`<a name="${escaped}"><!\\[CDATA\\[([\\s\\S]*?)\\]\\]><\\/a>`));
}

function validEan13(value) {
  const ean = text(value);
  if (!/^\d{13}$/.test(ean)) return false;
  const sum = [...ean.slice(0, 12)].reduce((total, digit, index) => total + Number(digit) * (index % 2 ? 3 : 1), 0);
  return (10 - (sum % 10)) % 10 === Number(ean[12]);
}

const defaultTargets = [
  "5905475368394",
  "5905475368400",
  "5905475368424",
  "5999863091001",
  "5999863091070",
  "5905475368363",
  "5905475368417",
  "5999863091063",
  "5999863091049",
  "5905475368349",
];
const targets = argumentValue("--targets")
  ? argumentValue("--targets").split(",").map(text).filter(Boolean)
  : defaultTargets;

const sourcePath = resolve(argumentValue("--source", "/tmp/prescot.xml"));
const manifestPath = resolve(argumentValue("--manifest", "exports/tim/tim-manifest.json"));
const outputPath = resolve(argumentValue("--output", "tim-import/pilot-10.xml"));
const auditPath = resolve(argumentValue("--audit", "exports/tim/pilots/new-products-pilot-10-audit.json"));

const [sourceRaw, manifestDocument] = await Promise.all([
  readFile(sourcePath, "utf8"),
  readFile(manifestPath, "utf8").then(JSON.parse),
]);
const source = sourceRaw.replace(/^\uFEFF/, "");
const manifestByEan = new Map((manifestDocument.products || []).map((product) => [String(product.ean), product]));
const offerByEan = new Map();
for (const match of source.matchAll(/^  <o id="[\s\S]*?^  <\/o>/gm)) {
  const block = match[0];
  const ean = attribute(block, "EAN");
  if (ean) offerByEan.set(ean, block);
}

const errors = [];
const auditProducts = [];
const offers = [];
const referencedProducerIds = new Set();
const referencedPersonIds = new Set();
for (const ean of targets) {
  const sourceOffer = offerByEan.get(ean)?.replace(/\r\n?/g, "\n");
  const product = manifestByEan.get(ean);
  if (!sourceOffer) {
    errors.push(`${ean}: brak dokładnej oferty w aktualnym prescot.xml`);
    continue;
  }
  if (!product) {
    errors.push(`${ean}: brak opisu TIM w manifeście`);
    continue;
  }
  const id = text(sourceOffer.match(/^  <o id="([^"]+)"/)?.[1]);
  const sourcePrice = text(sourceOffer.match(/\bprice="([^"]+)"/)?.[1]);
  const price = Number(sourcePrice).toFixed(2);
  const stock = text(sourceOffer.match(/\bstock="([^"]+)"/)?.[1]);
  const category = extractCdata(sourceOffer, /<cat><!\[CDATA\[([\s\S]*?)\]\]><\/cat>/);
  const producer = attribute(sourceOffer, "Producent");
  const manufacturerCode = attribute(sourceOffer, "Kod producenta");
  const unit = attribute(sourceOffer, "Jednostka");
  const sourceName = extractCdata(sourceOffer, /<name><!\[CDATA\[([\s\S]*?)\]\]><\/name>/);
  const mainImage = decodeXml(text(sourceOffer.match(/<main url="([^"]+)"\s*\/>/)?.[1]));
  const normalizedBaseName = text(product.name || sourceName).replace(/\s+/g, " ").replace(/\bwyc\.?\b/gi, "").replace(/\s+/g, " ").trim();
  const name = new RegExp(`${manufacturerCode.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")}$`, "i").test(normalizedBaseName)
    ? normalizedBaseName
    : `${normalizedBaseName} ${manufacturerCode}`;
  const description = text(product.descriptionHtml).replace(/^<section>/i, "").replace(/<\/section>$/i, "");
  for (const idMatch of sourceOffer.matchAll(/Producent odpowiedzialny"><!\[CDATA\[(producer_\d+)\]\]>/g)) referencedProducerIds.add(idMatch[1]);
  for (const idMatch of sourceOffer.matchAll(/Podmiot odpowiedzialny"><!\[CDATA\[(responsible_\d+)\]\]>/g)) referencedPersonIds.add(idMatch[1]);

  if (!validEan13(ean)) errors.push(`${ean}: nieprawidłowa suma kontrolna EAN`);
  if (!(Number(price) > 0)) errors.push(`${ean}: cena TIM nie jest dodatnia`);
  if (!(Number(stock) > 0)) errors.push(`${ean}: stan TIM nie jest dodatni`);
  if (!unit) errors.push(`${ean}: brak jednostki w aktualnym prescot.xml`);
  if (!mainImage) errors.push(`${ean}: brak zdjęcia głównego`);
  if (!description) errors.push(`${ean}: brak opisu TIM`);
  if (!manufacturerCode) errors.push(`${ean}: brak kodu producenta`);
  if (name.length > 128) errors.push(`${ean}: nazwa ma ${name.length} znaków`);
  if (/kaja|light\s*prestige/i.test(`${producer} ${name} ${category}`)) errors.push(`${ean}: produkt spoza zakresu`);

  let updatedOffer = sourceOffer.replace(/\bprice="[^"]+"/, `price="${price}"`);
  updatedOffer = updatedOffer.replace(/<name><!\[CDATA\[[\s\S]*?\]\]><\/name>/, `<name>${cdata(name)}</name>`);
  updatedOffer = updatedOffer.replace(/<desc><!\[CDATA\[[\s\S]*?\]\]><\/desc>/, `<desc>${cdata(description)}</desc>`);
  offers.push(updatedOffer);
  auditProducts.push({
    order: auditProducts.length + 1,
    sourceId: id,
    ean,
    manufacturerCode,
    producer,
    name,
    category,
    priceTimNet: price,
    priceTimNetSource: sourcePrice,
    stock,
    unit,
    mainImage,
    descriptionLength: description.length,
  });
}

const metadataBlocks = (containerName, ids) => {
  if (!ids.size) return "";
  const sourceContainer = source.match(new RegExp(`<${containerName}>[\\s\\S]*?<\\/${containerName}>`))?.[0] || "";
  const blocks = [];
  for (const id of ids) {
    const block = sourceContainer.match(new RegExp(`    <p id="${id}">[\\s\\S]*?    <\\/p>`))?.[0];
    if (!block) errors.push(`${id}: brak definicji w ${containerName}`);
    else blocks.push(block);
  }
  return blocks.length ? `  <${containerName}>\n${blocks.join("\n")}\n  </${containerName}>\n` : "";
};

if (offers.length !== targets.length) errors.push(`paczka ma ${offers.length} ofert zamiast ${targets.length}`);
if (new Set(auditProducts.map((product) => product.ean)).size !== targets.length) errors.push("EAN-y w paczce nie są unikatowe");
const audit = {
  generatedAt: new Date().toISOString(),
  source: sourcePath,
  output: outputPath,
  rules: {
    exactEanMissInLivePimcore: true,
    positiveTimFeedPriceAndStock: true,
    descriptionsFromTimManifest: true,
    excludedBrands: ["Kaja", "Light Prestige"],
  },
  counts: { requested: targets.length, built: offers.length, errors: errors.length },
  errors,
  products: auditProducts,
};
await mkdir(dirname(auditPath), { recursive: true });
await writeFile(auditPath, `${JSON.stringify(audit, null, 2)}\n`, "utf8");
if (errors.length) {
  console.error(errors.join("\n"));
  process.exitCode = 1;
} else {
  const xml = `<?xml version="1.0" encoding="UTF-8"?>\n<offers xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="1">\n`
    + metadataBlocks("responsibleProducers", referencedProducerIds)
    + metadataBlocks("responsiblePersons", referencedPersonIds)
    + `${offers.join("\n")}\n</offers>\n`;
  await mkdir(dirname(outputPath), { recursive: true });
  await writeFile(outputPath, xml, "utf8");
  console.log(`Gotowy kontrolowany pilot TIM: ${offers.length} produktów — ${outputPath}`);
}
