import { mkdir, readFile, writeFile } from "node:fs/promises";
import { resolve } from "node:path";

function argumentValue(name, fallback = "") {
  const index = process.argv.indexOf(name);
  return index === -1 ? fallback : process.argv[index + 1] || fallback;
}

function normalize(value) {
  return String(value || "")
    .normalize("NFKD")
    .replace(/[\u0300-\u036f]/g, "")
    .replace(/[^a-z0-9]+/gi, " ")
    .trim()
    .toLowerCase();
}

function decodeXml(value) {
  return String(value ?? "")
    .replace(/^<!\[CDATA\[|\]\]>$/g, "")
    .replaceAll("&lt;", "<")
    .replaceAll("&gt;", ">")
    .replaceAll("&quot;", '"')
    .replaceAll("&apos;", "'")
    .replaceAll("&amp;", "&")
    .trim();
}

function xmlAttribute(value, name) {
  const match = String(value || "").match(new RegExp(`\\b${name}="([^"]*)"`, "i"));
  return decodeXml(match?.[1] || "");
}

function parseTimFeed(input) {
  return [...String(input || "").matchAll(/<o\b([^>]*)>([\s\S]*?)<\/o>/gi)].map((match) => {
    const attributes = {};
    for (const attribute of match[2].matchAll(/<a\s+name="([^"]+)"[^>]*>([\s\S]*?)<\/a>/gi)) {
      attributes[decodeXml(attribute[1])] = decodeXml(attribute[2]);
    }
    return {
      ean: String(attributes.EAN || "").trim(),
      price: xmlAttribute(match[1], "price"),
      stock: xmlAttribute(match[1], "stock"),
      unit: String(attributes.Jednostka || "").trim(),
      producer: String(attributes.Producent || "").trim(),
      manufacturerCode: String(attributes["Kod producenta"] || attributes.Kod_producenta || "").trim(),
    };
  });
}

function csvCell(value) {
  return `"${String(value ?? "").replaceAll('"', '""')}"`;
}

function buildTimName(product) {
  const code = String(product.manufacturerCode || product.tradeIndex || "").trim();
  const name = String(product.name || "").trim();
  if (!code || normalize(name).endsWith(normalize(code))) return name.slice(0, 128);
  const prefixLength = Math.max(0, 128 - code.length - 1);
  return `${name.slice(0, prefixLength).trim()} ${code}`.trim();
}

const manifestPath = resolve(argumentValue("--manifest", "exports/tim/tim-manifest.json"));
const catalogPath = resolve(argumentValue("--catalog", "data/catalog.json"));
const sourceAuditPath = resolve(argumentValue("--source-audit", "exports/tim/source-audit/tim-source-audit.json"));
const bufferAuditPath = resolve(argumentValue("--buffer-audit"));
const activeAuditPath = resolve(argumentValue("--active-audit"));
const activeObjectAuditPath = argumentValue("--active-object-audit") ? resolve(argumentValue("--active-object-audit")) : "";
const bufferObjectAuditPath = argumentValue("--buffer-object-audit") ? resolve(argumentValue("--buffer-object-audit")) : "";
const timFeedPath = argumentValue("--tim-feed") ? resolve(argumentValue("--tim-feed")) : "";
const outputDir = resolve(argumentValue("--output-dir", "exports/tim/pilots"));
if (!bufferAuditPath) throw new Error("Podaj --buffer-audit z pełnym odczytem bufora PIMCORE.");
if (!activeAuditPath) throw new Error("Podaj --active-audit z pełnym odczytem katalogu głównego PIMCORE.");

const [manifest, catalog, sourceAudit, bufferAudit, activeAudit, activeObjectAudit, bufferObjectAudit, timFeedText] = await Promise.all([
  readFile(manifestPath, "utf8").then(JSON.parse),
  readFile(catalogPath, "utf8").then(JSON.parse),
  readFile(sourceAuditPath, "utf8").then(JSON.parse),
  readFile(bufferAuditPath, "utf8").then(JSON.parse),
  readFile(activeAuditPath, "utf8").then(JSON.parse),
  activeObjectAuditPath ? readFile(activeObjectAuditPath, "utf8").then(JSON.parse) : Promise.resolve({ pimcoreObjects: [] }),
  bufferObjectAuditPath ? readFile(bufferObjectAuditPath, "utf8").then(JSON.parse) : Promise.resolve({ pimcoreObjects: [] }),
  timFeedPath ? readFile(timFeedPath, "utf8") : Promise.resolve(""),
]);

const timFeedOffers = parseTimFeed(timFeedText);
if (timFeedPath && !timFeedOffers.length) throw new Error("Podany --tim-feed nie zawiera ofert Ceneo.");
const timFeedGroups = new Map();
for (const offer of timFeedOffers) {
  if (!offer.ean) continue;
  timFeedGroups.set(offer.ean, [...(timFeedGroups.get(offer.ean) || []), offer]);
}
const timFeedByEan = new Map([...timFeedGroups]
  .filter(([, offers]) => offers.length === 1)
  .map(([ean, offers]) => [ean, offers[0]]));

const bufferPayload = JSON.parse(bufferAudit.pimcoreGet?.body || "{}");
const bufferNodes = bufferPayload.nodes || [];
const activeKeys = new Set(sourceAudit.reconciliation.matches.map((item) => item.productKey));
const activeNodes = activeAudit.pimcoreTree?.nodes || [];
if (!activeNodes.length || activeAudit.pimcoreTree?.failedPages?.length) {
  throw new Error("Pełny odczyt katalogu aktywnego PIMCORE jest pusty albo niekompletny.");
}
const activeNames = new Set(activeNodes.map((item) => normalize(item.key)));
const activeNodesByName = new Map();
for (const node of activeNodes) {
  const key = normalize(node.key);
  activeNodesByName.set(key, [...(activeNodesByName.get(key) || []), node]);
}
const bufferNames = new Set(bufferNodes.map((item) => normalize(item.key)));
const bufferNodesByName = new Map();
for (const node of bufferNodes) {
  const key = normalize(node.key);
  bufferNodesByName.set(key, [...(bufferNodesByName.get(key) || []), node]);
}
const liveBufferByEan = new Map((bufferObjectAudit.pimcoreObjects || [])
  .filter((item) => item?.data?.ean)
  .map((item) => [String(item.data.ean), item]));
const catalogByKey = new Map(catalog.products.map((product) => [product.key, product]));
const sourceMatchByKey = new Map(sourceAudit.reconciliation.matches.map((item) => [item.productKey, item]));
const liveObjectByEan = new Map((activeObjectAudit.pimcoreObjects || [])
  .filter((item) => item?.data?.ean)
  .map((item) => [String(item.data.ean), item]));

function isActive(product) {
  return activeKeys.has(product.productKey)
    || activeNames.has(normalize(product.name))
    || activeNames.has(normalize(buildTimName(product)));
}

const ready = manifest.products.filter((product) => product.status === "ready");
const activeReady = ready.filter(isActive);
const bufferReady = ready.filter((product) => bufferNames.has(normalize(product.name)));
const bufferDescriptionCandidates = bufferReady.map((product) => {
  const matches = bufferNodesByName.get(normalize(product.name)) || [];
  const liveObject = liveBufferByEan.get(String(product.ean || ""));
  const uniqueNode = liveObject || (matches.length === 1 ? matches[0] : null);
  return uniqueNode ? {
    ...product,
    pimcoreId: Number(uniqueNode.id || 0),
    currentTimName: uniqueNode.key || product.name,
    timIndex: "",
    liveVerified: false,
    matchMethod: "buffer_exact_name",
  } : null;
}).filter(Boolean);
const newCandidates = ready
  .filter((product) => !isActive(product))
  .filter((product) => !bufferNames.has(normalize(product.name)))
  .map((product) => {
    const catalogProduct = catalogByKey.get(product.productKey) || {};
    const images = [catalogProduct.image, ...(catalogProduct.images || [])].filter(Boolean);
    return {
      ...product,
      timName: buildTimName(product),
      images: [...new Set(images)],
      sourceStockNumber: Number(String(product.stock).replace(",", ".")) || 0,
    };
  })
  .filter((product) => product.images.length > 0)
  .sort((left, right) => right.sourceStockNumber - left.sourceStockNumber || left.name.localeCompare(right.name, "pl"));

function activeDescriptionRecord(product) {
  const sourceMatch = sourceMatchByKey.get(product.productKey);
  const liveObject = liveObjectByEan.get(String(product.ean || ""));
  const nameMatches = activeNodesByName.get(normalize(product.name))
    || activeNodesByName.get(normalize(buildTimName(product)))
    || [];
  const uniqueNameMatch = nameMatches.length === 1 ? nameMatches[0] : null;
  const pimcoreId = Number(liveObject?.id || sourceMatch?.pimcoreId || uniqueNameMatch?.id || 0);
  return {
    ...product,
    pimcoreId,
    timIndex: liveObject?.data?.timIndex || sourceMatch?.timIndex || "",
    currentTimName: liveObject?.data?.timName || uniqueNameMatch?.key || product.name,
    liveVerified: Boolean(liveObject?.data?.ean === product.ean && liveObject?.data?.state === "active"),
    matchMethod: liveObject ? "live_ean" : sourceMatch ? `source_${sourceMatch.method}` : uniqueNameMatch ? "live_exact_name" : "",
  };
}

const activeDescriptionMapped = activeReady
  .map(activeDescriptionRecord)
  .filter((product) => product.pimcoreId > 0 && product.descriptionHtml);
const activeDescriptionById = new Map();
for (const product of activeDescriptionMapped) {
  activeDescriptionById.set(product.pimcoreId, [...(activeDescriptionById.get(product.pimcoreId) || []), product]);
}
const activeDescriptionCollisions = [...activeDescriptionById.entries()]
  .filter(([, products]) => products.length > 1)
  .map(([pimcoreId, products]) => ({
    pimcoreId,
    products: products.map(({ productKey, ean, name, manufacturerCode, matchMethod }) => ({
      productKey, ean, name, manufacturerCode, matchMethod,
    })),
  }));
const conflictingPimcoreIds = new Set(activeDescriptionCollisions.map((item) => item.pimcoreId));
const activeDescriptionCandidates = activeDescriptionMapped
  .filter((product) => !conflictingPimcoreIds.has(product.pimcoreId));
const preferredDescriptionKey = "ean:5903684853625";
const preferredDescriptionPilot = activeDescriptionCandidates.find((product) => product.productKey === preferredDescriptionKey)
  || activeDescriptionCandidates.find((product) => product.liveVerified)
  || activeDescriptionCandidates[0];
const activeDescriptionSorted = [
  preferredDescriptionPilot,
  ...activeDescriptionCandidates.filter((product) => product.productKey !== preferredDescriptionPilot.productKey),
];
const activeDescriptionStages = {
  pilot1: activeDescriptionSorted.slice(0, 1),
  pilot10: activeDescriptionSorted.slice(0, 10),
  pilot500: activeDescriptionSorted.slice(0, 500),
  pilotAll: activeDescriptionSorted,
};

const preferredPilotKey = "ean:5903684853625";
const preferredPilot = newCandidates.find((product) => product.productKey === preferredPilotKey) || newCandidates[0];
const sameCategoryCandidates = newCandidates.filter((product) => (
  product.producer === preferredPilot.producer && product.category === preferredPilot.category
));
const sameProducerCandidates = newCandidates.filter((product) => product.producer === preferredPilot.producer);
const stage10 = [...new Map([
  preferredPilot,
  ...sameCategoryCandidates,
  ...sameProducerCandidates,
].map((product) => [product.productKey, product])).values()].slice(0, 10);
const stage500 = [preferredPilot, ...newCandidates.filter((product) => product.productKey !== preferredPilot.productKey)].slice(0, 500);

const liveKnownDefaults = new Map([
  [preferredPilotKey, {
    manufacturerTim: "PRESCOT",
    manufacturerMfgid: "00060865",
    unitTim: "szt.",
    vat: "23",
    sizeCategory: "A",
    b24CrmId: "451",
    b24Path: "Oprawy oświetleniowe/Osprzęt do opraw oświetleniowych/Wyposażenie dodatkowe do taśm i węży LED",
  }],
]);

function commercialRow(product) {
  const known = liveKnownDefaults.get(product.productKey) || {};
  const timFeed = timFeedByEan.get(String(product.ean || "")) || {};
  const unitTim = known.unitTim || timFeed.unit || "";
  const timNetPrice = timFeed.price || "";
  const requiredMissing = [];
  if (!known.manufacturerTim) requiredMissing.push("manufacturer_tim");
  if (!known.manufacturerMfgid) requiredMissing.push("manufacturer_mfgid");
  if (!unitTim) requiredMissing.push("unit_tim");
  if (!known.sizeCategory) requiredMissing.push("size_category");
  if (!known.b24CrmId) requiredMissing.push("b24_crm_id");
  requiredMissing.push("shipping_time");
  if (!(Number(timNetPrice) > 0)) requiredMissing.push("tim_net_price");
  return {
    product_key: product.productKey,
    ean: product.ean,
    manufacturer_code: product.manufacturerCode,
    producer_source: product.producer,
    manufacturer_tim: known.manufacturerTim || "",
    manufacturer_mfgid: known.manufacturerMfgid || "",
    name_tim: product.timName,
    category_source: product.category,
    b24_crm_id: known.b24CrmId || "",
    b24_path: known.b24Path || "",
    unit_tim: unitTim,
    vat: known.vat || "23",
    size_category: known.sizeCategory || "",
    shipping_time: "",
    tim_net_price: timNetPrice,
    tim_feed_price: timFeed.price || "",
    tim_feed_stock_reference: timFeed.stock || "",
    wapro_price_reference_only: product.price,
    wapro_stock_reference: product.stock,
    main_image: product.images[0] || "",
    additional_images: product.images.slice(1).join(" | "),
    description_status: "ready",
    required_missing: requiredMissing.join(" | "),
  };
}

const columns = [
  "product_key", "ean", "manufacturer_code", "producer_source", "manufacturer_tim", "manufacturer_mfgid",
  "name_tim", "category_source", "b24_crm_id", "b24_path", "unit_tim", "vat", "size_category",
  "shipping_time", "tim_net_price", "wapro_price_reference_only", "wapro_stock_reference", "main_image",
  "additional_images", "description_status", "required_missing", "tim_feed_price", "tim_feed_stock_reference",
];

function asCsv(products) {
  const rows = products.map(commercialRow);
  return `\uFEFF${columns.map(csvCell).join(";")}\r\n${rows.map((row) => columns.map((column) => csvCell(row[column])).join(";")).join("\r\n")}\r\n`;
}

function activeDescriptionCsv(products) {
  const activeColumns = [
    "pimcore_id", "tim_index", "product_key", "ean", "manufacturer_code", "current_tim_name",
    "match_method", "live_verified", "description_html_new",
  ];
  const rows = products.map((product) => ({
    pimcore_id: product.pimcoreId,
    tim_index: product.timIndex,
    product_key: product.productKey,
    ean: product.ean,
    manufacturer_code: product.manufacturerCode,
    current_tim_name: product.currentTimName,
    match_method: product.matchMethod,
    live_verified: product.liveVerified ? "TAK" : "NIE",
    description_html_new: product.descriptionHtml,
  }));
  return `\uFEFF${activeColumns.map(csvCell).join(";")}\r\n${rows.map((row) => activeColumns.map((column) => csvCell(row[column])).join(";")).join("\r\n")}\r\n`;
}

await mkdir(outputDir, { recursive: true });
await Promise.all([
  writeFile(resolve(outputDir, "pilot-1-commercial.csv"), asCsv([preferredPilot]), "utf8"),
  writeFile(resolve(outputDir, "pilot-10-commercial.csv"), asCsv(stage10), "utf8"),
  writeFile(resolve(outputDir, "pilot-500-commercial.csv"), asCsv(stage500), "utf8"),
  writeFile(resolve(outputDir, "active-description-pilot-1.csv"), activeDescriptionCsv(activeDescriptionStages.pilot1), "utf8"),
  writeFile(resolve(outputDir, "active-description-pilot-10.csv"), activeDescriptionCsv(activeDescriptionStages.pilot10), "utf8"),
  writeFile(resolve(outputDir, "active-description-pilot-500.csv"), activeDescriptionCsv(activeDescriptionStages.pilot500), "utf8"),
  writeFile(resolve(outputDir, "active-description-pilot.json"), `${JSON.stringify({
    generatedAt: new Date().toISOString(),
    source: { manifestPath, sourceAuditPath, activeAuditPath, activeObjectAuditPath },
    counts: {
      candidates: activeDescriptionCandidates.length,
      liveVerified: activeDescriptionCandidates.filter((item) => item.liveVerified).length,
      ambiguousRecordsExcluded: activeDescriptionCollisions.reduce((total, item) => total + item.products.length, 0),
      ambiguousPimcoreIds: activeDescriptionCollisions.length,
    },
    collisions: activeDescriptionCollisions,
    stages: activeDescriptionStages,
  }, null, 2)}\n`, "utf8"),
  writeFile(resolve(outputDir, "buffer-description-pilot.json"), `${JSON.stringify({
    generatedAt: new Date().toISOString(),
    source: { manifestPath, bufferAuditPath, bufferObjectAuditPath },
    counts: {
      candidates: bufferDescriptionCandidates.length,
      unmatchedOrAmbiguous: bufferReady.length - bufferDescriptionCandidates.length,
    },
    stages: {
      pilot1: bufferDescriptionCandidates.slice(0, 1),
      pilot10: bufferDescriptionCandidates.slice(0, 10),
      pilotAll: bufferDescriptionCandidates,
    },
  }, null, 2)}\n`, "utf8"),
  writeFile(resolve(outputDir, "pilot-content.json"), `${JSON.stringify({
    generatedAt: new Date().toISOString(),
    source: { manifestPath, sourceAuditPath, bufferAuditPath, activeAuditPath, timFeedPath },
    counts: {
      ready: ready.length,
      activeReady: activeReady.length,
      bufferReady: bufferReady.length,
      newCandidatesWithImages: newCandidates.length,
      liveBuffer: bufferPayload.total || bufferNodes.length,
      liveActive: activeNodes.length,
      timFeedOffers: timFeedOffers.length,
      newCandidatesMatchedTimFeed: newCandidates.filter((item) => timFeedByEan.has(String(item.ean || ""))).length,
    },
    stages: { pilot1: [preferredPilot], pilot10: stage10, pilot500: stage500 },
  }, null, 2)}\n`, "utf8"),
]);

console.log(`Gotowe opisy na aktywnych kartach: ${activeReady.length}`);
console.log(`Aktywne karty z jednoznacznym ID do aktualizacji: ${activeDescriptionCandidates.length}`);
console.log(`Niejednoznaczne dopasowania wykluczone: ${activeDescriptionCollisions.reduce((total, item) => total + item.products.length, 0)} rekordy / ${activeDescriptionCollisions.length} ID PIMCORE`);
console.log(`Pilot opisu: PIMCORE ${preferredDescriptionPilot.pimcoreId} — ${preferredDescriptionPilot.name}`);
console.log(`Gotowe opisy w buforze: ${bufferReady.length}`);
console.log(`Nowi kandydaci z obrazami: ${newCandidates.length}`);
console.log(`Pilot 1: ${preferredPilot.productKey} — ${preferredPilot.name}`);
console.log(`Partie: 1 / ${stage10.length} / ${stage500.length}`);
console.log(`Braki blokujące pilot 1: ${commercialRow(preferredPilot).required_missing}.`);
console.log(`Katalog: ${outputDir}`);
