import { readFile, stat, writeFile } from "node:fs/promises";
import { createHash } from "node:crypto";
import { resolve } from "node:path";

const sourcePath = resolve(process.argv[2] || "exports/tim/remediation/klus-active-next-documents-readonly-2026-09-02.json");
const outputPath = resolve(process.argv[3] || "exports/tim/remediation/klus-active-next-documents-fuzzy80to99-write-queue-2026-09-02.json");
const source = JSON.parse(await readFile(sourcePath, "utf8"));

if (!Array.isArray(source.fuzzy80to99)) throw new Error("Brak tablicy fuzzy80to99.");

const items = [];
const rejected = [];
for (const product of source.fuzzy80to99) {
  if (!Number.isInteger(Number(product.pimcoreId))) throw new Error("Nieprawidłowy PIMCORE ID.");
  if (!String(product.model || "").trim() || /^PRE[-_]/i.test(String(product.model))) throw new Error(`Nieprawidłowy model: ${product.model}`);
  if (product.state !== "active" || Number(product.stock) <= 0) throw new Error(`Produkt poza aktywnym dodatnim zakresem: ${product.model}`);
  if (Number(product.confidence) < 80 || Number(product.confidence) >= 100) throw new Error(`Pewność poza 80–99: ${product.model}`);
  if (!String(product.officialProductUrl || "").startsWith("https://klusdesign.eu/")) throw new Error(`Nieoficjalny URL: ${product.model}`);
  if (!Array.isArray(product.conflicts)) throw new Error(`Nieprawidłowy format konfliktów: ${product.model}`);
  if (product.conflicts.length) {
    rejected.push({
      id: Number(product.pimcoreId),
      ean: String(product.ean || ""),
      model: String(product.model || ""),
      confidence: Number(product.confidence),
      conflicts: product.conflicts,
      decision: "manual_review_no_write",
    });
    continue;
  }
  if (!/^\d{13}$/.test(String(product.ean || ""))) throw new Error(`Nieprawidłowy EAN: ${product.model}`);
  if (!Array.isArray(product.targetFields) || !product.targetFields.length) throw new Error(`Brak pól docelowych: ${product.model}`);

  const documents = {};
  for (const field of product.targetFields) {
    if (!["dataSheet", "certifications"].includes(field)) throw new Error(`Niedozwolone pole ${field}: ${product.model}`);
    const document = product.documents?.[field];
    if (!document || Number(document.confidence) < 80) throw new Error(`Brak bezpiecznego dokumentu ${field}: ${product.model}`);
    if (!String(document.officialUrl || "").startsWith("https://klusdesign.eu/")) throw new Error(`Nieoficjalny dokument ${field}: ${product.model}`);
    const localFile = resolve(String(document.localFile || ""));
    const fileStat = await stat(localFile);
    if (!fileStat.isFile() || fileStat.size !== Number(document.bytes)) throw new Error(`Niezgodny plik lokalny ${field}: ${product.model}`);
    const bytes = await readFile(localFile);
    if (bytes.subarray(0, 4).toString("ascii") !== "%PDF") throw new Error(`Plik nie jest PDF ${field}: ${product.model}`);
    const sha256 = createHash("sha256").update(bytes).digest("hex");
    if (sha256 !== document.sha256) throw new Error(`Niezgodny SHA-256 ${field}: ${product.model}`);
    documents[field] = { source: localFile, filename: document.filename };
  }

  items.push({
    id: Number(product.pimcoreId),
    ean: String(product.ean),
    model: String(product.model),
    state: "active",
    timName: String(product.name || ""),
    xmlStock: Number(product.stock),
    confidence: Number(product.confidence),
    confidenceReason: String(product.confidenceReason || ""),
    officialProductUrl: String(product.officialProductUrl),
    documents,
  });
}

const seen = new Set();
for (const item of items) {
  if (seen.has(item.id)) throw new Error(`Duplikat PIMCORE ID: ${item.id}`);
  seen.add(item.id);
}

const counts = {
  items: items.length,
  dataSheet: items.filter((item) => item.documents.dataSheet).length,
  certifications: items.filter((item) => item.documents.certifications).length,
  rejected: rejected.length,
  confidence: Object.fromEntries(
    [...new Set(items.map((item) => item.confidence))]
      .sort((a, b) => b - a)
      .map((confidence) => [confidence, items.filter((item) => item.confidence === confidence).length]),
  ),
};

const output = {
  generatedAt: new Date().toISOString(),
  source: sourcePath,
  selection: "KLUŚ fuzzy 80–99%, active, positive stock, official product page and verified local PDFs",
  safeguards: [
    "exact live PIMCORE id/EAN/manufacturerIndex required by writer",
    "only empty document fields may be written",
    "price, stock, name, identifiers, status and workflow are protected",
    "local PDF size and SHA-256 verified before queue creation",
  ],
  counts,
  items,
  rejected,
};

await writeFile(outputPath, `${JSON.stringify(output, null, 2)}\n`, "utf8");
console.log(JSON.stringify({ output: outputPath, counts }, null, 2));
