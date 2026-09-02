import { createHash } from "node:crypto";
import { mkdir, readFile, writeFile } from "node:fs/promises";
import { basename, resolve } from "node:path";

const mapPath = resolve(process.argv[2]
  || "exports/tim/remediation/klus-official-document-map-2026-09-01.json");
const outputDir = resolve(process.argv[3] || "tmp/pdfs/klus-official");
const outputPath = resolve(process.argv[4]
  || "exports/tim/remediation/klus-official-document-downloads-2026-09-01.json");

const map = JSON.parse(await readFile(mapPath, "utf8"));
const wantedTypes = new Set(["dataSheet", "instruction", "certification"]);
const urlRows = new Map();
for (const record of map.records) {
  if (!record.best?.exactModelInPage) continue;
  for (const document of record.best.documents || []) {
    if (!wantedTypes.has(document.type) || urlRows.has(document.url)) continue;
    const hash = createHash("sha256").update(document.url).digest("hex").slice(0, 12);
    const sourceBase = decodeURIComponent(basename(new URL(document.url).pathname))
      .replace(/[^A-Za-z0-9._-]+/g, "_")
      .replace(/\.pdf$/i, "")
      .slice(0, 64);
    const filename = `KLUS_${hash}_${sourceBase || document.type}.pdf`;
    urlRows.set(document.url, {
      url: document.url,
      type: document.type,
      label: document.label,
      filename,
      source: resolve(outputDir, filename),
    });
  }
}

await mkdir(outputDir, { recursive: true });
const downloads = [];
const rows = [...urlRows.values()];
for (let start = 0; start < rows.length; start += 6) {
  const batch = rows.slice(start, start + 6);
  downloads.push(...await Promise.all(batch.map(async (row) => {
    try {
      const response = await fetch(row.url, {
        redirect: "follow",
        headers: { "User-Agent": "Mozilla/5.0" },
      });
      const bytes = Buffer.from(await response.arrayBuffer());
      const contentType = String(response.headers.get("content-type") || "");
      const isPdf = bytes.subarray(0, 4).toString("ascii") === "%PDF";
      if (response.status !== 200 || !isPdf || bytes.length < 1_000) {
        return { ...row, http: response.status, contentType, bytes: bytes.length, ok: false };
      }
      await writeFile(row.source, bytes);
      return {
        ...row,
        http: response.status,
        contentType,
        bytes: bytes.length,
        sha256: createHash("sha256").update(bytes).digest("hex"),
        ok: true,
      };
    } catch (error) {
      return { ...row, http: 0, bytes: 0, ok: false, error: String(error?.message || error) };
    }
  })));
  console.log(`Dokumenty KLUŚ: pobrano ${Math.min(start + batch.length, rows.length)}/${rows.length}`);
}

const report = {
  generatedAt: new Date().toISOString(),
  sourceMap: mapPath,
  officialOnly: true,
  counts: {
    requested: downloads.length,
    downloaded: downloads.filter((row) => row.ok).length,
    failed: downloads.filter((row) => !row.ok).length,
    dataSheet: downloads.filter((row) => row.ok && row.type === "dataSheet").length,
    instruction: downloads.filter((row) => row.ok && row.type === "instruction").length,
    certification: downloads.filter((row) => row.ok && row.type === "certification").length,
  },
  downloads,
};
await writeFile(outputPath, `${JSON.stringify(report, null, 2)}\n`, "utf8");
console.log(JSON.stringify(report.counts, null, 2));
console.log(`Raport: ${outputPath}`);
