import { mkdir, readFile, writeFile } from "node:fs/promises";
import { dirname, resolve } from "node:path";

function argumentValue(name, fallback = "") {
  const index = process.argv.indexOf(name);
  return index === -1 ? fallback : process.argv[index + 1] || fallback;
}

function text(value) {
  return String(value ?? "").replace(/^\uFEFF/, "").trim();
}

function parseDelimited(input, delimiter = ";") {
  const rows = [];
  let row = [];
  let cell = "";
  let quoted = false;
  const value = String(input).replace(/^\uFEFF/, "");
  for (let index = 0; index < value.length; index += 1) {
    const char = value[index];
    if (char === '"') {
      if (quoted && value[index + 1] === '"') {
        cell += '"';
        index += 1;
      } else {
        quoted = !quoted;
      }
    } else if (!quoted && char === delimiter) {
      row.push(cell);
      cell = "";
    } else if (!quoted && (char === "\n" || char === "\r")) {
      if (char === "\r" && value[index + 1] === "\n") index += 1;
      row.push(cell);
      if (row.some(Boolean)) rows.push(row);
      row = [];
      cell = "";
    } else {
      cell += char;
    }
  }
  if (cell || row.length) {
    row.push(cell);
    if (row.some(Boolean)) rows.push(row);
  }
  const headers = (rows.shift() || []).map(text);
  return rows.map((cells) => Object.fromEntries(headers.map((header, index) => [header, cells[index] ?? ""])));
}

function escapeAttribute(value) {
  return text(value)
    .replaceAll("&", "&amp;")
    .replaceAll('"', "&quot;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;");
}

function cdata(value) {
  return `<![CDATA[${String(value ?? "").replaceAll("]]>", "]]]]><![CDATA[>")}]]>`;
}

function validEan13(value) {
  const ean = text(value);
  if (!/^\d{13}$/.test(ean)) return false;
  const sum = [...ean.slice(0, 12)].reduce((total, digit, index) => total + Number(digit) * (index % 2 ? 3 : 1), 0);
  return (10 - (sum % 10)) % 10 === Number(ean[12]);
}

const contentPath = resolve(argumentValue("--content", "exports/tim/pilots/pilot-content.json"));
const commercialPath = resolve(argumentValue("--commercial"));
const stage = argumentValue("--stage", "pilot1");
const outputPath = resolve(argumentValue("--output", `exports/tim/pilots/${stage}.xml`));
if (!commercialPath) throw new Error("Podaj --commercial z uzupełnionymi danymi handlowymi.");

const [content, commercialText] = await Promise.all([
  readFile(contentPath, "utf8").then(JSON.parse),
  readFile(commercialPath, "utf8"),
]);
const products = content.stages[stage];
if (!Array.isArray(products) || !products.length) throw new Error(`Nieznany lub pusty etap ${stage}.`);
const commercialRows = parseDelimited(commercialText);
const commercialByKey = new Map(commercialRows.map((row) => [text(row.product_key), row]));

const requiredColumns = [
  "ean", "manufacturer_code", "manufacturer_tim", "manufacturer_mfgid", "name_tim", "category_source",
  "b24_crm_id", "unit_tim", "vat", "size_category", "shipping_time", "tim_net_price", "main_image",
];
const errors = [];
const offers = [];

for (const product of products) {
  const row = commercialByKey.get(product.productKey);
  if (!row) {
    errors.push(`${product.productKey}: brak w pliku handlowym`);
    continue;
  }
  for (const column of requiredColumns) {
    if (!text(row[column])) errors.push(`${product.productKey}: brak ${column}`);
  }
  if (!validEan13(row.ean)) errors.push(`${product.productKey}: nieprawidłowy EAN ${row.ean}`);
  if (!(Number(row.tim_net_price) > 0)) errors.push(`${product.productKey}: cena netto TIM musi być dodatnia`);
  if (text(row.name_tim).length > 128) errors.push(`${product.productKey}: nazwa TIM przekracza 128 znaków`);
  if (/kaja|light\s*prestige/i.test(`${row.producer_source} ${row.manufacturer_tim} ${row.name_tim} ${row.category_source}`)) {
    errors.push(`${product.productKey}: producent poza zakresem`);
  }
  if (!product.descriptionHtml || !product.images?.length) errors.push(`${product.productKey}: brak opisu lub zdjęcia`);
  const additionalImages = text(row.additional_images).split("|").map(text).filter(Boolean);
  const imageXml = [text(row.main_image), ...additionalImages]
    .map((url, index) => index === 0 ? `<main url="${escapeAttribute(url)}" />` : `<i url="${escapeAttribute(url)}" />`)
    .join("");
  const attributes = [
    ["Producent", row.manufacturer_tim],
    ["Kod producenta", row.manufacturer_code],
    ["EAN", row.ean],
    ["Jednostka", row.unit_tim],
    ["VAT", row.vat],
    ["Gabaryt", row.size_category],
    ["Czas wysyłki", row.shipping_time],
    ["Kategoria B24", row.b24_crm_id],
  ];
  if (product.verifiedEprelUrl) attributes.push(["Karta EPREL PDF", product.verifiedEprelUrl]);
  offers.push(
    `  <o id="${escapeAttribute(product.productKey.replace(/^ean:/, ""))}" url="${escapeAttribute(product.productUrl)}" price="${escapeAttribute(row.tim_net_price)}" avail="1" stock="${escapeAttribute(product.stock)}">\n`
    + `    <cat>${cdata(row.category_source)}</cat>\n`
    + `    <name>${cdata(row.name_tim)}</name>\n`
    + `    <imgs>${imageXml}</imgs>\n`
    + `    <desc>${cdata(product.descriptionHtml)}</desc>\n`
    + `    <attrs>${attributes.map(([name, value]) => `<a name="${escapeAttribute(name)}">${cdata(value)}</a>`).join("")}</attrs>\n`
    + "  </o>",
  );
}

if (errors.length) {
  console.error(`Paczka ${stage} zatrzymana (${errors.length} problemów):`);
  for (const error of errors.slice(0, 80)) console.error(`- ${error}`);
  process.exitCode = 1;
} else {
  const xml = `<?xml version="1.0" encoding="utf-8"?>\n<offers xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="1">\n${offers.join("\n")}\n</offers>\n`;
  await mkdir(dirname(outputPath), { recursive: true });
  await writeFile(outputPath, xml, "utf8");
  console.log(`Gotowa paczka Ceneo TIM: ${offers.length} produktów — ${outputPath}`);
}
