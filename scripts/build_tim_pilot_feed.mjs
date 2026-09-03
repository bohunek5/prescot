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

const priorityNameOverrides = new Map([
  ["5905475368011", "Sterownik LED MONO 12A touch RF komplet z pilotem czarnym 12-24V Prescot"],
  ["5905475368004", "Sterownik LED CCT 12A touch RF komplet z pilotem czarnym 12-24V Prescot"],
  ["5905475368028", "Sterownik LED RGB 12A touch RF komplet z pilotem czarnym 12-24V Prescot"],
  ["5905475368042", "Sterownik LED RGBW 12A touch RF komplet z pilotem czarnym 12-24V Prescot"],
  ["5905475368035", "Sterownik LED RGBCCT 12A touch RF komplet z pilotem czarnym 12-24V Prescot"],
]);

const priorityCurrentPerChannelOverrides = new Map([
  ["5905475368011", "12A"],
  ["5905475368004", "6A"],
  ["5905475368028", "4A"],
  ["5905475368042", "3A"],
  ["5905475368035", "2,4A"],
]);

const priorityDescriptionOverrides = new Map([
  ["5905475368011", `<h2>Sterownik LED MONO 12A z pilotem RF PR-MONO-12A</h2>
<p>Zestaw do sterowania jednobarwnym oświetleniem LED. Obejmuje odbiornik oraz czarny pilot dotykowy RF.</p>
<h3>Zastosowanie i parametry</h3>
<ul><li>Sterowanie i ściemnianie jednobarwnych taśm LED</li><li>Napięcie wejściowe i wyjściowe: 12 V lub 24 V DC</li><li>Jeden kanał; maksymalnie 12 A</li><li>Stopień ochrony: IP20</li></ul>
<h3>Dobór i montaż</h3>
<p>Dobierz zasilacz i taśmę LED o zgodnym napięciu. Nie przekraczaj dopuszczalnego prądu sterownika. Przed podłączeniem wyłącz zasilanie i sprawdź polaryzację oraz schemat w instrukcji.</p>`],
  ["5905475368004", `<h2>Sterownik LED CCT 12A z pilotem RF PR-CCT-12A</h2>
<p>Zestaw do sterowania taśmami LED CCT ze zmianą temperatury barwowej. Obejmuje odbiornik oraz czarny pilot dotykowy RF.</p>
<h3>Zastosowanie i parametry</h3>
<ul><li>Sterowanie jasnością i temperaturą barwową zgodnej taśmy CCT</li><li>Napięcie wejściowe i wyjściowe: 12 V lub 24 V DC</li><li>Dwa kanały; maksymalnie 12 A łącznie i 6 A na kanał</li><li>Stopień ochrony: IP20</li></ul>
<h3>Dobór i montaż</h3>
<p>Dobierz zasilacz i taśmę CCT o zgodnym napięciu oraz układzie przewodów. Nie przekraczaj dopuszczalnego prądu sterownika. Przed podłączeniem wyłącz zasilanie i sprawdź schemat w instrukcji.</p>`],
  ["5905475368028", `<h2>Sterownik LED RGB 12A z pilotem RF PR-RGB-12A</h2>
<p>Zestaw do sterowania wielokolorową taśmą LED RGB. Obejmuje trzykanałowy odbiornik oraz czarny pilot dotykowy RF 2,4 GHz.</p>
<h3>Parametry</h3>
<ul><li>Napięcie wejściowe i wyjściowe: 12 V lub 24 V DC</li><li>Trzy kanały; maksymalnie 12 A łącznie i 4 A na kanał</li><li>Zakres ściemniania: 0–100%</li><li>Zasięg sterowania: do 30 m</li><li>Stopień ochrony: IP20</li></ul>
<h3>Dobór i montaż</h3>
<p>Dobierz zasilacz i taśmę RGB o zgodnym napięciu. Nie przekraczaj obciążenia całkowitego ani obciążenia pojedynczego kanału. Przed podłączeniem wyłącz zasilanie i sprawdź przewody zgodnie z instrukcją.</p>`],
  ["5905475368042", `<h2>Sterownik LED RGBW 12A z pilotem RF PR-RGBW-12A</h2>
<p>Zestaw do sterowania taśmą LED RGBW z oddzielnym kanałem światła białego. Obejmuje czterokanałowy odbiornik oraz czarny pilot dotykowy RF 2,4 GHz.</p>
<h3>Parametry</h3>
<ul><li>Napięcie wejściowe i wyjściowe: 12 V lub 24 V DC</li><li>Cztery kanały; maksymalnie 12 A łącznie i 3 A na kanał</li><li>Zakres ściemniania: 0–100%</li><li>Zasięg sterowania: do 30 m</li><li>Stopień ochrony: IP20</li></ul>
<h3>Dobór i montaż</h3>
<p>Dobierz zasilacz i taśmę RGBW o zgodnym napięciu. Nie przekraczaj obciążenia całkowitego ani obciążenia pojedynczego kanału. Przed podłączeniem wyłącz zasilanie i sprawdź przewody zgodnie z instrukcją.</p>`],
  ["5905475368035", `<h2>Sterownik LED RGBCCT 12A z pilotem RF PR-RGBCCT-12A</h2>
<p>Zestaw do sterowania wielokolorową taśmą LED RGBCCT ze zmianą temperatury barwowej. Obejmuje pięciokanałowy odbiornik oraz czarny pilot dotykowy RF 2,4 GHz.</p>
<h3>Parametry</h3>
<ul><li>Napięcie wejściowe i wyjściowe: 12 V lub 24 V DC</li><li>Pięć kanałów; maksymalnie 12 A łącznie i 2,4 A na kanał</li><li>Zakres ściemniania: 0–100%</li><li>Zasięg sterowania: do 30 m</li><li>Stopień ochrony: IP20</li></ul>
<h3>Dobór i montaż</h3>
<p>Dobierz zasilacz i taśmę RGBCCT o zgodnym napięciu. Nie przekraczaj obciążenia całkowitego ani obciążenia pojedynczego kanału. Przed podłączeniem wyłącz zasilanie i sprawdź przewody zgodnie z instrukcją.</p>`],
]);

const rmDescriptionOverrides = new Map([
  ["5905475368301", `<h2>Rozdzielacz mocy LED Mono 1/9 RM-MONO-19</h2>
<p>Rozdzielacz przeznaczony do uporządkowanego rozprowadzenia zasilania na kilka odcinków jednokolorowej taśmy LED. Jedno wejście i dziewięć wyjść ułatwiają wykonanie większych instalacji, między innymi w zabudowie meblowej, profilach, witrynach i oświetleniu schodów.</p>
<h3>Dobór i zastosowanie</h3>
<p>Model pracuje w instalacjach DC 5–48 V i obsługuje prąd całkowity do 25 A, maksymalnie 10 A na pojedynczą gałąź. Przed montażem należy zsumować obciążenie wszystkich podłączonych odcinków i dobrać odpowiedni zasilacz oraz przekrój przewodów.</p>
<h3>Bezpieczeństwo montażu</h3>
<p>Podłączenie należy wykonać przy wyłączonym zasilaniu, zachowując właściwą polaryzację. Nie wolno przekraczać dopuszczalnego prądu rozdzielacza ani poszczególnych wyjść.</p>`],
  ["5905475368318", `<h2>Rozdzielacz mocy LED CCT 1/6 RM-CCT-16</h2>
<p>Rozdzielacz do instalacji z taśmami LED CCT, w których regulowana jest temperatura barwowa światła. Jedno wejście i sześć wyjść pozwalają rozprowadzić zasilanie i sygnał do kilku odcinków z jednego sterownika.</p>
<h3>Dobór i zastosowanie</h3>
<p>Model pracuje w instalacjach DC 5–48 V i obsługuje prąd całkowity do 25 A, maksymalnie 10 A na pojedynczą gałąź. Należy dobrać zgodną taśmę CCT, sterownik, zasilacz oraz przewody odpowiednie do łącznego obciążenia.</p>
<h3>Bezpieczeństwo montażu</h3>
<p>Podłączenie należy wykonać przy wyłączonym zasilaniu, zgodnie z oznaczeniem kanałów i polaryzacją. Nie wolno przekraczać dopuszczalnego prądu rozdzielacza ani poszczególnych wyjść.</p>`],
  ["5905475368325", `<h2>Rozdzielacz mocy LED RGB 1/4 RM-RGB-14</h2>
<p>Rozdzielacz przeznaczony do taśm LED RGB. Jedno wejście i cztery wyjścia pozwalają rozprowadzić kanały R, G i B oraz wspólny przewód do kilku odcinków taśmy bez wykonywania przypadkowych połączeń.</p>
<h3>Dobór i zastosowanie</h3>
<p>Model pracuje w instalacjach DC 5–48 V i obsługuje prąd całkowity do 25 A, maksymalnie 10 A na pojedynczą gałąź. Należy dobrać zgodną taśmę RGB, sterownik, zasilacz oraz przekroje przewodów do łącznego obciążenia.</p>
<h3>Bezpieczeństwo montażu</h3>
<p>Podłączenie należy wykonać przy wyłączonym zasilaniu, zachowując kolejność kanałów i właściwą polaryzację. Nie wolno przekraczać dopuszczalnego prądu rozdzielacza ani poszczególnych wyjść.</p>`],
  ["5905475368332", `<h2>Rozdzielacz mocy LED RGBW 1/3 RM-RGBW-13</h2>
<p>Rozdzielacz do instalacji z taśmami LED RGBW, wyposażonymi w kanały kolorowe i osobny kanał światła białego. Jedno wejście i trzy wyjścia ułatwiają czytelne podłączenie kilku odcinków do wspólnego sterownika.</p>
<h3>Dobór i zastosowanie</h3>
<p>Model pracuje w instalacjach DC 5–48 V i obsługuje prąd całkowity do 25 A, maksymalnie 10 A na pojedynczą gałąź. Należy dobrać zgodną taśmę RGBW, sterownik, zasilacz oraz przewody odpowiednie do łącznego obciążenia.</p>
<h3>Bezpieczeństwo montażu</h3>
<p>Podłączenie należy wykonać przy wyłączonym zasilaniu, zgodnie z oznaczeniem kanałów i polaryzacją. Nie wolno przekraczać dopuszczalnego prądu rozdzielacza ani poszczególnych wyjść.</p>`],
  ["5905475368387", `<h2>Rozdzielacz mocy LED RGBCW 1/3 RM-RGBCW-13</h2>
<p>Rozdzielacz przeznaczony do instalacji LED RGBCW, łączących kanały RGB z dwoma kanałami bieli. Jedno wejście i trzy wyjścia pozwalają uporządkować przewody i rozprowadzić sygnał do kilku odcinków taśmy.</p>
<h3>Dobór i zastosowanie</h3>
<p>Model pracuje w instalacjach DC 5–48 V i obsługuje prąd całkowity do 25 A, maksymalnie 10 A na pojedynczą gałąź. Należy dobrać zgodną taśmę RGBCW, sterownik, zasilacz oraz przewody odpowiednie do łącznego obciążenia.</p>
<h3>Bezpieczeństwo montażu</h3>
<p>Podłączenie należy wykonać przy wyłączonym zasilaniu, zgodnie z oznaczeniem kanałów i polaryzacją. Nie wolno przekraczać dopuszczalnego prądu rozdzielacza ani poszczególnych wyjść.</p>`],
]);

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
  const sourcePriceNumber = Number(sourcePrice);
  const price = sourcePriceNumber.toFixed(2);
  const stock = text(sourceOffer.match(/\bstock="([^"]+)"/)?.[1]);
  const category = extractCdata(sourceOffer, /<cat><!\[CDATA\[([\s\S]*?)\]\]><\/cat>/);
  const producer = attribute(sourceOffer, "Producent");
  const manufacturerCode = attribute(sourceOffer, "Kod producenta");
  const unit = attribute(sourceOffer, "Jednostka");
  const sourceName = extractCdata(sourceOffer, /<name><!\[CDATA\[([\s\S]*?)\]\]><\/name>/);
  const mainImage = decodeXml(text(sourceOffer.match(/<main url="([^"]+)"\s*\/>/)?.[1]));
  const normalizedBaseName = text(priorityNameOverrides.get(ean) || product.name || sourceName).replace(/\s+/g, " ").replace(/\bwyc\.?\b/gi, "").replace(/\s+/g, " ").trim();
  const name = new RegExp(`${manufacturerCode.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")}$`, "i").test(normalizedBaseName)
    ? normalizedBaseName
    : `${normalizedBaseName} ${manufacturerCode}`;
  const description = text(priorityDescriptionOverrides.get(ean) || rmDescriptionOverrides.get(ean) || product.descriptionHtml).replace(/^<section>/i, "").replace(/<\/section>$/i, "");
  for (const idMatch of sourceOffer.matchAll(/Producent odpowiedzialny"><!\[CDATA\[(producer_\d+)\]\]>/g)) referencedProducerIds.add(idMatch[1]);
  for (const idMatch of sourceOffer.matchAll(/Podmiot odpowiedzialny"><!\[CDATA\[(responsible_\d+)\]\]>/g)) referencedPersonIds.add(idMatch[1]);

  if (!validEan13(ean)) errors.push(`${ean}: nieprawidłowa suma kontrolna EAN`);
  if (!(Number(price) > 0)) errors.push(`${ean}: cena TIM nie jest dodatnia`);
  if (!Number.isFinite(sourcePriceNumber) || Number(price) !== sourcePriceNumber) errors.push(`${ean}: cena po przygotowaniu nie jest dokładnie równa cenie netto z prescot.xml`);
  if (!(Number(stock) > 0)) errors.push(`${ean}: stan TIM nie jest dodatni`);
  if (!unit) errors.push(`${ean}: brak jednostki w aktualnym prescot.xml`);
  if (!mainImage) errors.push(`${ean}: brak zdjęcia głównego`);
  if (!description) errors.push(`${ean}: brak opisu TIM`);
  if (/\b\d{13}\b/.test(description)) errors.push(`${ean}: opis zawiera EAN`);
  if (/\b(?:PRE|STR|ZAS)\d+\b/i.test(description)) errors.push(`${ean}: opis zawiera wewnętrzny indeks katalogowy`);
  if (!description.includes(manufacturerCode)) errors.push(`${ean}: opis nie zawiera indeksu handlowego producenta`);
  if (!manufacturerCode) errors.push(`${ean}: brak kodu producenta`);
  if (name.length > 128) errors.push(`${ean}: nazwa ma ${name.length} znaków`);
  if (/kaja|light\s*prestige/i.test(`${producer} ${name} ${category}`)) errors.push(`${ean}: produkt spoza zakresu`);

  let updatedOffer = sourceOffer.replace(/\bprice="[^"]+"/, `price="${price}"`);
  updatedOffer = updatedOffer.replace(/<name><!\[CDATA\[[\s\S]*?\]\]><\/name>/, `<name>${cdata(name)}</name>`);
  updatedOffer = updatedOffer.replace(/<desc><!\[CDATA\[[\s\S]*?\]\]><\/desc>/, `<desc>${cdata(description)}</desc>`);
  const currentPerChannel = priorityCurrentPerChannelOverrides.get(ean);
  if (currentPerChannel) {
    updatedOffer = updatedOffer.replace(
      /(<a name="Prąd na 1 kanał"><!\[CDATA\[)[\s\S]*?(\]\]><\/a>)/,
      `$1${currentPerChannel}$2`,
    );
  }
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
