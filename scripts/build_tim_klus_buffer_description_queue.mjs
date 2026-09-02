import { mkdir, readFile, writeFile } from "node:fs/promises";
import { dirname, resolve } from "node:path";

const snapshotPath = resolve(process.argv[2]
  || "exports/tim/remediation/buffer-current-live-readonly-after-activations-2026-09-01.json");
const outputPath = resolve(process.argv[3]
  || "exports/tim/remediation/klus-buffer-description-queue-2026-09-01.json");

const snapshot = JSON.parse(await readFile(snapshotPath, "utf8"));

const escapeHtml = (value) => String(value || "")
  .replaceAll("&", "&amp;")
  .replaceAll("<", "&lt;")
  .replaceAll(">", "&gt;")
  .replaceAll('"', "&quot;")
  .replaceAll("'", "&#39;");

function cleanedExistingDescription(html) {
  return String(html || "")
    .replace(/(?:<br\s*\/?>(?:\s|&nbsp;)*){1,3}Więcej informacji o produkcie:\s*(?:&nbsp;|\u00a0|<br\s*\/?>)*/giu, "")
    .replace(/Więcej informacji o produkcie:\s*(?:&nbsp;|\u00a0|<br\s*\/?>)*/giu, "")
    .trim();
}

function buildDescription(item) {
  const name = escapeHtml(item.timName);
  const model = escapeHtml(item.model);
  const existing = cleanedExistingDescription(item.descriptionHtml);
  const factualBody = existing || `<p>Produkt marki KLUŚ. Szczegółowe parametry i zgodność z elementami systemu podaje karta produktu producenta.</p>`;
  return `<h2>${name}</h2>\n<p><strong>Indeks handlowy:</strong> ${model}</p>\n${factualBody}`;
}

const stages = {
  bufferNewNeedsUpdate: [],
  bufferApprovalNeedsUpdate: [],
  klusBufferActiveNeedsUpdate: [],
};

for (const item of snapshot.items) {
  if (!/KLUŚ|KLUS/iu.test(`${item.manufacturerName || ""} ${item.manufacturerPath || ""}`)) continue;
  if (!item.ean || !item.model || !item.timName || String(item.descriptionHtml || "").includes(item.model)) continue;
  const record = {
    pimcoreId: Number(item.id),
    ean: String(item.ean),
    manufacturerCode: String(item.model),
    name: String(item.timName),
    descriptionHtml: buildDescription(item),
    liveState: String(item.state || ""),
  };
  if (/\b\d{13}\b/.test(record.descriptionHtml)) throw new Error(`EAN w opisie ${item.id}`);
  if (/\bPRE-\d+/i.test(record.descriptionHtml)) throw new Error(`Indeks wewnętrzny w opisie ${item.id}`);
  if (item.state === "new") stages.bufferNewNeedsUpdate.push(record);
  else if (item.state === "new_for_approval") stages.bufferApprovalNeedsUpdate.push(record);
  else if (item.state === "active") stages.klusBufferActiveNeedsUpdate.push(record);
}

const report = {
  generatedAt: new Date().toISOString(),
  sourceSnapshot: snapshotPath,
  rules: [
    "zachowaj merytoryczną treść istniejącego opisu",
    "dodaj nazwę i indeks handlowy KLUŚ",
    "usuń pustą frazę 'Więcej informacji o produkcie:'",
    "nigdy nie dodawaj EAN ani indeksu wewnętrznego PRE",
  ],
  counts: Object.fromEntries(Object.entries(stages).map(([key, rows]) => [key, rows.length])),
  stages,
};

await mkdir(dirname(outputPath), { recursive: true });
await writeFile(outputPath, `${JSON.stringify(report, null, 2)}\n`, "utf8");
console.log(JSON.stringify({ outputPath, counts: report.counts }, null, 2));
