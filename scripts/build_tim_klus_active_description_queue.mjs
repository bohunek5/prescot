import { mkdir, readFile, writeFile } from "node:fs/promises";
import { dirname, resolve } from "node:path";

const snapshotPath = resolve(process.argv[2]
  || "exports/tim/remediation/active-brand-offer-live-readonly-post-scharfer-2026-09-01.json");
const outputPath = resolve(process.argv[3]
  || "exports/tim/remediation/klus-active-description-queue-2026-09-01.json");
const snapshot = JSON.parse(await readFile(snapshotPath, "utf8"));

const escapeHtml = (value) => String(value || "")
  .replaceAll("&", "&amp;")
  .replaceAll("<", "&lt;")
  .replaceAll(">", "&gt;")
  .replaceAll('"', "&quot;")
  .replaceAll("'", "&#39;");

function clean(html) {
  return String(html || "")
    .replace(/<p[^>]*>[\s\u00a0]*(?:<strong>)?[\s\u00a0]*Więcej[\s\u00a0]+informacji[\s\u00a0]+o[\s\u00a0]+produkcie:[\s\S]*?<\/p>/giu, "")
    .replace(/(?:<br\s*\/?>(?:\s|&nbsp;)*){1,3}Więcej informacji o produkcie:\s*(?:&nbsp;|\u00a0|<br\s*\/?>)*/giu, "")
    .replace(/Więcej informacji o produkcie:\s*(?:&nbsp;|\u00a0|<br\s*\/?>)*/giu, "")
    .trim();
}

function description(item) {
  const existing = clean(item.descriptionHtml);
  const body = existing || "<p>Produkt marki KLUŚ. Szczegółowe parametry oraz kompatybilność z elementami systemu podaje karta produktu producenta.</p>";
  return `<h2>${escapeHtml(item.timName)}</h2>\n<p><strong>Indeks handlowy:</strong> ${escapeHtml(item.model)}</p>\n${body}`;
}

const stages = { activePositiveNeedsUpdate: [], activeZeroNeedsUpdate: [] };
const rejected = [];
for (const item of snapshot.products || []) {
  if (item.expectedBrand !== "KLUŚ" || item.state !== "active" || item.published !== true) continue;
  if (String(item.descriptionHtml || "").includes(String(item.model || ""))) continue;
  if (!item.ean || !item.model || !item.timName) {
    rejected.push({ id: item.id, ean: item.ean, model: item.model, timName: item.timName, reason: "missing_identity" });
    continue;
  }
  const record = {
    pimcoreId: Number(item.id),
    ean: String(item.ean),
    manufacturerCode: String(item.model),
    name: String(item.timName),
    descriptionHtml: description(item),
  };
  if (/\b\d{13}\b/u.test(record.descriptionHtml)) throw new Error(`EAN w opisie ${item.id}`);
  if (/\bPRE-\d+/iu.test(record.descriptionHtml)) throw new Error(`Indeks wewnętrzny w opisie ${item.id}`);
  const stage = Number(item.stock || 0) > 0 ? "activePositiveNeedsUpdate" : "activeZeroNeedsUpdate";
  stages[stage].push(record);
}

const report = {
  generatedAt: new Date().toISOString(),
  sourceSnapshot: snapshotPath,
  rules: [
    "preserve factual existing description",
    "add exact KLUŚ trade model",
    "never add EAN or PRE internal index",
    "separate positive-stock and zero-stock active products",
  ],
  counts: {
    activePositiveNeedsUpdate: stages.activePositiveNeedsUpdate.length,
    activeZeroNeedsUpdate: stages.activeZeroNeedsUpdate.length,
    rejected: rejected.length,
  },
  stages,
  rejected,
};
await mkdir(dirname(outputPath), { recursive: true });
await writeFile(outputPath, `${JSON.stringify(report, null, 2)}\n`, "utf8");
console.log(JSON.stringify({ outputPath, counts: report.counts }, null, 2));
