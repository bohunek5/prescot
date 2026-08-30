#!/usr/bin/env node

import { mkdir, readFile, writeFile } from "node:fs/promises";
import { dirname, resolve } from "node:path";

function argumentValue(name, fallback = "") {
  const index = process.argv.indexOf(name);
  return index >= 0 ? process.argv[index + 1] || fallback : fallback;
}

const inputPath = resolve(argumentValue("--input", "data/eprel-candidates.json"));
const downloadDir = resolve(argumentValue("--download-dir", "/tmp/pdfs/prescot-eprel"));
const reportPath = resolve(argumentValue("--report", "exports/tim/source-audit/eprel-link-check.json"));
const input = JSON.parse(await readFile(inputPath, "utf8"));
const links = [...new Map(Object.values(input.products)
  .map((item) => [item.productInformationSheetPl, item.eprelId])).entries()];

await mkdir(downloadDir, { recursive: true });
await mkdir(dirname(reportPath), { recursive: true });

async function download([url, id]) {
  try {
    const response = await fetch(url, { redirect: "follow", signal: AbortSignal.timeout(30_000) });
    const contentType = response.headers.get("content-type") || "";
    const bytes = new Uint8Array(await response.arrayBuffer());
    const isPdf = response.ok && (contentType.includes("application/pdf") || String.fromCharCode(...bytes.slice(0, 4)) === "%PDF");
    const path = resolve(downloadDir, `${id || "unknown"}.pdf`);
    if (isPdf) await writeFile(path, bytes);
    return { url, eprelId: id, ok: isPdf, httpStatus: response.status, contentType, bytes: bytes.length, path: isPdf ? path : "" };
  } catch (error) {
    return { url, eprelId: id, ok: false, error: error.message };
  }
}

const results = [];
for (let index = 0; index < links.length; index += 4) {
  results.push(...await Promise.all(links.slice(index, index + 4).map(download)));
}
const report = {
  generatedAt: new Date().toISOString(),
  checked: results.length,
  availablePdf: results.filter((item) => item.ok).length,
  failed: results.filter((item) => !item.ok).length,
  results,
  note: "Dostępność PDF nie potwierdza jeszcze zgodności modelu produktu.",
};
await writeFile(reportPath, `${JSON.stringify(report, null, 2)}\n`, "utf8");
console.log(`EPREL PDF: ${report.availablePdf}/${report.checked} dostępnych; błędy: ${report.failed}.`);
console.log(`Raport: ${reportPath}`);
if (report.failed) process.exitCode = 2;
