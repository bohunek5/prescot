import { mkdir, writeFile } from "node:fs/promises";
import { dirname, resolve } from "node:path";

const outputPath = resolve(process.argv[2] || "exports/tim/remediation/pr-mad-natural-description-queue-2026-09-02.json");

const products = [
  { pimcoreId: 15907539, ean: "5905475368073", manufacturerCode: "PR-MAD36-1224", watts: 36 },
  { pimcoreId: 15907542, ean: "5905475368080", manufacturerCode: "PR-MAD60-1224", watts: 60 },
  { pimcoreId: 15907545, ean: "5905475368097", manufacturerCode: "PR-MAD100-1224", watts: 100 },
  { pimcoreId: 15907551, ean: "5905475368103", manufacturerCode: "PR-MAD150-1224", watts: 150 },
  { pimcoreId: 15907554, ean: "5905475368110", manufacturerCode: "PR-MAD200-1224", watts: 200 },
];

function description(product) {
  return `<section>
<h2>Zasilacz LED ${product.watts} W z auto-detekcją 12/24 V ${product.manufacturerCode}</h2>
<p>Wnętrzowy zasilacz impulsowy Prescot do taśm i modułów LED. Funkcja Auto-Identify rozpoznaje odbiornik 12 lub 24 V DC i ustawia właściwe napięcie wyjściowe. Model ma aluminiową, półzalewaną obudowę oraz stopień ochrony IP20.</p>
<h3>Zastosowanie</h3>
<p>Zasilacz jest przeznaczony do instalacji LED w suchych wnętrzach, między innymi w zabudowach meblowych, wnękach i sufitach podwieszanych. Obudowa wymaga swobodnego przepływu powietrza.</p>
<h3>Dobór i bezpieczeństwo</h3>
<p>Łączna moc odbiorników nie powinna przekraczać 80% mocy zasilacza. Wokół obudowy należy zachować co najmniej 50 mm wolnej przestrzeni. Przed montażem trzeba wyłączyć zasilanie i sprawdzić polaryzację wyjścia. Zasilacz ma zabezpieczenia OVP, OLP, OTP i SCP oraz 36-miesięczną gwarancję.</p>
</section>`;
}

const forbidden = ["Co to jest", "EAN", "GTIN", "50% mniej", "cicha praca", "bezawaryjn", "PRE-"];
const items = products.map((product) => {
  const descriptionHtml = description(product);
  const errors = forbidden.filter((value) => descriptionHtml.toLocaleLowerCase("pl").includes(value.toLocaleLowerCase("pl")));
  if (!descriptionHtml.includes(product.manufacturerCode)) errors.push("missing_trade_model");
  if (descriptionHtml.includes(product.ean)) errors.push("ean_in_description");
  if (errors.length) throw new Error(`${product.manufacturerCode}: ${errors.join(", ")}`);
  return {
    ...product,
    name: `Zasilacz modułowy LED ${product.watts}W-Auto 12V/24V Prescot ${product.manufacturerCode}`,
    descriptionHtml,
    evidence: "Karta katalogowa producenta PR-MAD, strony 1-2: Auto-Identify 12/24 V, IP20, obudowa półzalewana, OVP/OLP/OTP/SCP, zapas 20%, wentylacja 50 mm, gwarancja 36 miesięcy.",
  };
});

const queue = {
  generatedAt: new Date().toISOString(),
  scope: "description_only",
  protectedFields: ["price", "stock", "name", "ean", "identifiers", "documents", "workflow", "status"],
  stages: { activePositiveNeedsUpdate: items },
};

await mkdir(dirname(outputPath), { recursive: true });
await writeFile(outputPath, `${JSON.stringify(queue, null, 2)}\n`, "utf8");
console.log(JSON.stringify({ outputPath, items: items.length, descriptionLengths: items.map((item) => item.descriptionHtml.length) }));
