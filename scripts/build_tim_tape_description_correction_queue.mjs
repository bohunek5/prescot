import { mkdir, readFile, writeFile } from "node:fs/promises";
import { dirname, resolve } from "node:path";

const sourcePath = resolve(process.argv[2]
  || "exports/tim/remediation/prescot-tape-natural-description-queue-v9-2026-09-02.json");
const outputPath = resolve(process.argv[3]
  || "exports/tim/remediation/prescot-tape-natural-description-corrections-2026-09-02.json");

const source = JSON.parse(await readFile(sourcePath, "utf8"));
const products = source?.stages?.activePositiveNeedsUpdate || [];

const corrections = new Map([
  [10047385, [
    ["Profil aluminiowy należy dobrać do taśmy o szerokości 8mm.",
      "Profil aluminiowy należy dobrać do taśmy o szerokości 10mm."],
  ]],
  [8659736, [
    ["Do taśmy należy dobrać zasilacz 12V DC", "Do taśmy należy dobrać zasilacz 24V DC"],
  ]],
  [10047335, [
    ["Do taśmy należy dobrać zasilacz 12V DC", "Do taśmy należy dobrać zasilacz 24V DC"],
  ]],
  // Ten wariant był ostatnią pozycją Premium 5Y poza wcześniejszym postverify.
  [10047461, []],
]);

const selected = [];
for (const [pimcoreId, replacements] of corrections) {
  const product = products.find((item) => Number(item.pimcoreId) === pimcoreId);
  if (!product) throw new Error(`Brak produktu PIMCORE ${pimcoreId} w kolejce źródłowej.`);
  let descriptionHtml = String(product.descriptionHtml || "");
  for (const [before, after] of replacements) {
    const occurrences = descriptionHtml.split(before).length - 1;
    if (occurrences !== 1) throw new Error(`${pimcoreId}: oczekiwano jednego fragmentu do korekty, jest ${occurrences}.`);
    descriptionHtml = descriptionHtml.replace(before, after);
  }

  const nameVoltage = String(product.name || "").match(/\b(12|24|36|48)\s*V\b/iu)?.[1] || "";
  const descriptionVoltage = descriptionHtml.match(/zasilacz\s+(12|24|36|48)\s*V\b/iu)?.[1] || "";
  const nameWidth = String(product.name || "").match(/\b(\d+(?:[.,]\d+)?)\s*mm\b/iu)?.[1] || "";
  const descriptionWidth = descriptionHtml.match(/szerokości\s+(\d+(?:[.,]\d+)?)\s*mm\b/iu)?.[1] || "";
  if (nameVoltage && descriptionVoltage && nameVoltage !== descriptionVoltage) {
    throw new Error(`${pimcoreId}: sprzeczne napięcie ${nameVoltage}V/${descriptionVoltage}V.`);
  }
  if (nameWidth && descriptionWidth && nameWidth !== descriptionWidth) {
    throw new Error(`${pimcoreId}: sprzeczna szerokość ${nameWidth}mm/${descriptionWidth}mm.`);
  }
  if ((descriptionHtml.match(/<h2>/giu) || []).length !== 1 || (descriptionHtml.match(/<h3>/giu) || []).length !== 2) {
    throw new Error(`${pimcoreId}: nieprawidłowa liczba nagłówków.`);
  }
  if (!descriptionHtml.includes("<h3>Barwa światła i zastosowanie</h3>")
      || !descriptionHtml.includes("<h3>Dobór i bezpieczeństwo</h3>")) {
    throw new Error(`${pimcoreId}: brak wymaganego układu opisu.`);
  }
  if (/\b\d{13}\b/u.test(descriptionHtml)
      || /\b(?:PRE[-_ ]?\d+|TAŚ\d+|PRO\d+|KAT\d+)\b/iu.test(descriptionHtml)
      || /\bEconomic\b/iu.test(descriptionHtml)) {
    throw new Error(`${pimcoreId}: opis zawiera niedozwolony identyfikator lub nazwę serii.`);
  }
  selected.push({ ...product, descriptionHtml, correctionApplied: replacements.length > 0 });
}

const output = {
  generatedAt: new Date().toISOString(),
  sourceQueue: sourcePath,
  rules: [
    "only exact active positive-stock PIMCORE cards from the validated v9 queue",
    "correct source conflicts using the product name and trade index evidence",
    "three concise TIM blocks; no EAN or internal Prescot index",
    "only productDescriptions may be written",
  ],
  counts: { activePositiveNeedsUpdate: selected.length },
  stages: {
    activePositiveNeedsUpdate: selected,
    activePositiveCurrent: [],
    activeZeroNeedsUpdate: [],
    activeZeroCurrent: [],
  },
};

await mkdir(dirname(outputPath), { recursive: true });
await writeFile(outputPath, `${JSON.stringify(output, null, 2)}\n`, "utf8");
console.log(JSON.stringify({ outputPath, count: selected.length, ids: selected.map((item) => item.pimcoreId) }, null, 2));
