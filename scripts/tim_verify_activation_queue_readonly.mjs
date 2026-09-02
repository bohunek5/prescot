import { readFile, writeFile } from "node:fs/promises";
import { resolve } from "node:path";
import { chromium } from "../../radlight/node_modules/playwright/index.mjs";

const pick = (name, fallback = "") => {
  const index = process.argv.indexOf(name);
  return index < 0 ? fallback : process.argv[index + 1] || fallback;
};
const queuePath = resolve(pick("--queue", "exports/tim/remediation/final-active-verification-queue-2026-09-01.json"));
const outputPath = resolve(pick("--output", "exports/tim/remediation/final-active-live-postverify-2026-09-01.json"));
const queue = JSON.parse(await readFile(queuePath, "utf8"));
if (!Array.isArray(queue?.items)) throw new Error("Kolejka nie zawiera tablicy items.");

const relationCount = (value) => Array.isArray(value) ? value.length : 0;
const priceValue = (value) => Number(value && typeof value === "object" ? value.value : value);
const browser = await chromium.connectOverCDP("http://127.0.0.1:9222");
const context = browser.contexts()[0];
const frame = context?.pages().flatMap((page) => page.frames()).find((candidate) => candidate.url().includes("/pimcore/admin/"));
if (!frame) throw new Error("Brak zalogowanej ramki PIMCORE w Chrome.");

const results = [];
for (const expected of queue.items) {
  const response = await frame.evaluate(async (id) => {
    const reply = await fetch(`/pimcore/admin/object/get?id=${id}&_=${Date.now()}`, {
      credentials: "same-origin", cache: "no-store", headers: { Accept: "application/json", "Cache-Control": "no-cache" },
    });
    let payload = null;
    try { payload = JSON.parse(await reply.text()); } catch {}
    return { status: reply.status, payload };
  }, expected.id);
  const object = response.payload || {};
  const data = object.data || {};
  const description = String(data.productDescriptions?.data?.longMarketingDescription || "");
  const relationChecks = Object.fromEntries((expected.requiredRelations || []).map((field) => [field, relationCount(data[field]) === 1]));
  const checks = {
    http: response.status === 200,
    identity: Number(object.general?.id) === expected.id && String(data.ean || "") === expected.ean && String(data.manufacturerIndex || "") === expected.model,
    price: priceValue(data.listPrice) === expected.price,
    state: String(data.state || "") === expected.expectedState,
    published: object.general?.published === true,
    unlocked: !object.editlock && object.general?.locked !== true,
    description: description.includes(expected.model) && !/\b\d{13}\b/.test(description),
    timIndex: expected.expectedState === "active" ? Boolean(String(data.timIndex || "").trim()) : true,
    ...relationChecks,
  };
  results.push({
    ...expected,
    liveState: data.state ?? null,
    liveStatus: data.status ?? null,
    timIndex: data.timIndex ?? null,
    livePrice: priceValue(data.listPrice),
    fullpath: object.general?.fullpath ?? null,
    checks,
    status: Object.values(checks).every(Boolean) ? "verified" : "mismatch",
  });
}

const report = {
  generatedAt: new Date().toISOString(),
  mode: "read_only_live_postverification",
  queuePath,
  counts: {
    total: results.length,
    verified: results.filter((row) => row.status === "verified").length,
    mismatch: results.filter((row) => row.status === "mismatch").length,
    active: results.filter((row) => row.liveState === "active").length,
    awaitingTimApproval: results.filter((row) => row.liveState === "new_for_approval").length,
    locked: results.filter((row) => !row.checks.unlocked).length,
  },
  results,
};
await writeFile(outputPath, `${JSON.stringify(report, null, 2)}\n`, "utf8");
console.log(JSON.stringify({ outputPath, counts: report.counts }));
process.exit(report.counts.mismatch ? 1 : 0);
