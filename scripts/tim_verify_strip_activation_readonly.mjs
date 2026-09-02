import { readFile, writeFile } from "node:fs/promises";
import { resolve } from "node:path";
import { chromium } from "../../radlight/node_modules/playwright/index.mjs";

const pick = (name, fallback = "") => {
  const index = process.argv.indexOf(name);
  return index < 0 ? fallback : process.argv[index + 1] || fallback;
};

const queuePath = resolve(pick("--queue", "exports/tim/remediation/buffer-strip-activation-queue-2026-09-01.json"));
const outputPath = resolve(pick("--output", "exports/tim/remediation/buffer-strip-activation-postverify-2026-09-01.json"));
const queue = JSON.parse(await readFile(queuePath, "utf8"));
if (!Array.isArray(queue?.items)) throw new Error("Kolejka nie zawiera tablicy items.");

const expectedStates = new Map([
  [15907490, "active"],
  [15907487, "active"],
  [15907484, "active"],
  [15907511, "new_for_approval"],
  [15907522, "new_for_approval"],
  [15907514, "new_for_approval"],
]);

const relationCount = (value) => Array.isArray(value) ? value.length : 0;
const priceValue = (value) => Number(value && typeof value === "object" ? value.value : value);
const browser = await chromium.connectOverCDP("http://127.0.0.1:9222");
const context = browser.contexts()[0];
const page = context?.pages().find((candidate) => candidate.frames().some((frame) => frame.url().includes("/pimcore/admin/")));
const frame = page?.frames().find((candidate) => candidate.url().includes("/pimcore/admin/"));
if (!frame) throw new Error("Brak zalogowanej ramki PIMCORE w Chrome.");

const report = {
  generatedAt: new Date().toISOString(),
  mode: "read_only_live_postverification",
  queuePath,
  counts: {},
  results: [],
};

for (const expected of queue.items) {
  const response = await frame.evaluate(async (id) => {
    const reply = await fetch(`/pimcore/admin/object/get?id=${id}&_=${Date.now()}`, {
      credentials: "same-origin",
      cache: "no-store",
      headers: { Accept: "application/json", "Cache-Control": "no-cache" },
    });
    let payload = null;
    try { payload = JSON.parse(await reply.text()); } catch {}
    return { status: reply.status, payload };
  }, expected.id);
  const object = response.payload || {};
  const data = object.data || {};
  const description = String(data.productDescriptions?.data?.longMarketingDescription || "");
  const expectedState = expectedStates.get(expected.id);
  const checks = {
    http: response.status === 200,
    objectId: Number(object.general?.id) === expected.id,
    ean: String(data.ean || "") === expected.ean,
    model: String(data.manufacturerIndex || "") === expected.model,
    price: priceValue(data.listPrice) === expected.price,
    state: String(data.state || "") === expectedState,
    published: object.general?.published === true,
    unlocked: !object.editlock && object.general?.locked !== true,
    descriptionModel: description.includes(expected.model),
    descriptionNoEan: !/\b\d{13}\b/.test(description),
    timIndex: expectedState === "active" ? Boolean(String(data.timIndex || "").trim()) : true,
    dataSheet: relationCount(data.dataSheet) === 1,
    certifications: relationCount(data.certifications) === 1,
    energyClass: Boolean(String(data.energyClass || "").trim()),
    energyClassLabels: relationCount(data.energyClassLabels) === 1,
    energyTechnicalCards: relationCount(data.energyTechnicalCards) === 1,
  };
  report.results.push({
    id: expected.id,
    ean: expected.ean,
    model: expected.model,
    xmlStock: expected.xmlStock,
    expectedPrice: expected.price,
    livePrice: priceValue(data.listPrice),
    expectedState,
    liveState: data.state ?? null,
    liveStatus: data.status ?? null,
    timIndex: data.timIndex ?? null,
    fullpath: object.general?.fullpath ?? null,
    checks,
    status: Object.values(checks).every(Boolean) ? "verified" : "mismatch",
  });
}

report.counts = {
  total: report.results.length,
  verified: report.results.filter((row) => row.status === "verified").length,
  mismatch: report.results.filter((row) => row.status === "mismatch").length,
  active: report.results.filter((row) => row.liveState === "active").length,
  awaitingTimApproval: report.results.filter((row) => row.liveState === "new_for_approval").length,
  locked: report.results.filter((row) => !row.checks.unlocked).length,
};

await writeFile(outputPath, `${JSON.stringify(report, null, 2)}\n`, "utf8");
console.log(JSON.stringify({ outputPath, counts: report.counts }));
process.exit(report.counts.mismatch ? 1 : 0);
