import { readFile, writeFile } from "node:fs/promises";
import { resolve } from "node:path";
import { chromium } from "../../radlight/node_modules/playwright/index.mjs";

function arg(name, fallback = "") {
  const index = process.argv.indexOf(name);
  return index === -1 ? fallback : process.argv[index + 1] || fallback;
}

function stock(product) {
  return Number(product?.stock || 0);
}

function findField(node, name) {
  if (!node || typeof node !== "object") return null;
  if (node.name === name) return node;
  for (const child of node.children || []) {
    const found = findField(child, name);
    if (found) return found;
  }
  return null;
}

function isFilled(value) {
  return value !== null && value !== undefined && value !== "" && value !== 0;
}

function printable(definition, value) {
  if (!definition) return value;
  const option = (definition.options || []).find((item) => String(item.value) === String(value));
  return option?.key || value;
}

const auditPath = resolve(arg(
  "--audit",
  "exports/tim/remediation/active-brand-offer-prescot-live-after-cards-descriptions-ce-2026-09-02.json",
));
const outputPath = resolve(arg(
  "--output",
  "exports/tim/remediation/active-positive-etim-readonly-2026-09-02.json",
));
const cdpUrl = arg("--cdp-url", "http://127.0.0.1:9222");
const start = Math.max(0, Number(arg("--start", "0")) || 0);
const limit = Math.max(1, Number(arg("--limit", "99999")) || 99999);
const batchSize = Math.max(1, Math.min(20, Number(arg("--batch-size", "10")) || 10));

const source = JSON.parse(await readFile(auditPath, "utf8"));
const queue = (source.products || [])
  .filter((product) => product.httpStatus === 200
    && product.published === true
    && product.state === "active"
    && stock(product) > 0)
  .slice(start, start + limit);

const browser = await chromium.connectOverCDP(cdpUrl);
const context = browser.contexts()[0];
const page = context.pages().find((candidate) => candidate.frames()
  .some((frame) => frame.url() === "https://dostawca.tim.pl/pimcore/admin/"));
const frame = page?.frames().find((candidate) => candidate.url() === "https://dostawca.tim.pl/pimcore/admin/");
if (!frame) throw new Error("Brak aktywnej, zalogowanej ramki PIMCORE.");

const results = [];
for (let batchStart = 0; batchStart < queue.length; batchStart += batchSize) {
  const batch = queue.slice(batchStart, batchStart + batchSize);
  const responses = await frame.evaluate(async (ids) => Promise.all(ids.map(async (objectId) => {
    try {
      const request = await fetch(`/pimcore/admin/object/get?id=${objectId}&_=${Date.now()}-${objectId}`, {
        method: "GET",
        credentials: "same-origin",
        cache: "no-store",
      });
      let object = null;
      try { object = JSON.parse(await request.text()); } catch {}
      return { id: objectId, status: request.status, object };
    } catch (error) {
      return { id: objectId, status: 0, object: null, error: String(error?.message || error) };
    }
  })), batch.map((product) => Number(product.id)));
  const responseById = new Map(responses.map((response) => [Number(response.id), response]));
  for (let relativeIndex = 0; relativeIndex < batch.length; relativeIndex += 1) {
    const index = batchStart + relativeIndex;
    const sourceProduct = batch[relativeIndex];
    const id = Number(sourceProduct.id);
  const result = {
    index: start + index,
    id,
    ean: sourceProduct.ean,
    model: sourceProduct.model,
    timName: sourceProduct.timName,
    stock: sourceProduct.stock,
    status: "failed",
  };
  try {
    const response = responseById.get(id) || { status: 0, object: null };
    const object = response.object;
    const data = object?.data || {};
    const etimField = findField(object?.layout, "etimTim");
    const activeGroups = Object.entries(etimField?.activeGroupDefinitions || {});
    const valuesByGroup = data.etimTim?.data?.default || {};
    const groups = activeGroups.map(([groupId, group]) => {
      const values = valuesByGroup[groupId] || {};
      const definitions = new Map((group.keys || []).map((item) => [String(item.id), item]));
      const filled = Object.entries(values)
        .filter(([, value]) => isFilled(value))
        .map(([keyId, value]) => {
          const entry = definitions.get(String(keyId));
          return {
            keyId: Number(keyId),
            code: entry?.name || "",
            title: entry?.definition?.title || "",
            type: entry?.definition?.fieldtype || "",
            value,
            displayValue: printable(entry?.definition, value),
          };
        });
      return {
        groupId: Number(groupId),
        code: group.name,
        title: group.description,
        availableKeys: (group.keys || []).length,
        filledCount: filled.length,
        filled,
        definitions: (group.keys || []).map((entry) => ({
          keyId: Number(entry.id),
          code: entry.name,
          title: entry.definition?.title || "",
          type: entry.definition?.fieldtype || "",
          options: entry.definition?.options || [],
        })),
      };
    });
    result.status = response.status === 200 ? "ok" : `http_${response.status}`;
    result.liveIdentity = {
      id: object?.general?.id,
      published: object?.general?.published,
      locked: object?.general?.locked,
      state: data.state,
      ean: data.ean,
      model: data.manufacturerIndex,
      timName: data.timName,
      versionCount: object?.general?.versionCount,
    };
    result.etimClass = data.etimClass;
    result.progress = Number(data.etimByTimComplementProgress || 0);
    result.groups = groups;
    result.filledCount = groups.reduce((sum, group) => sum + group.filledCount, 0);
  } catch (error) {
    result.error = String(error?.message || error);
  }
  results.push(result);
  }
  const completed = Math.min(batchStart + batch.length, queue.length);
  process.stdout.write(`ETIM odczyt ${completed}/${queue.length}\n`);
  await writeFile(outputPath, `${JSON.stringify({ generatedAt: new Date().toISOString(), readOnly: true, source: auditPath, start, limit, batchSize, results }, null, 2)}\n`, "utf8");
}

await browser.close();
const report = {
  generatedAt: new Date().toISOString(),
  readOnly: true,
  source: auditPath,
  start,
  limit,
  batchSize,
  counts: {
    requested: queue.length,
    read: results.filter((item) => item.status === "ok").length,
    failed: results.filter((item) => item.status !== "ok").length,
    belowFour: results.filter((item) => item.status === "ok" && item.filledCount < 4).length,
    zero: results.filter((item) => item.status === "ok" && item.filledCount === 0).length,
  },
  results,
};
await writeFile(outputPath, `${JSON.stringify(report, null, 2)}\n`, "utf8");
console.log(JSON.stringify({ output: outputPath, ...report.counts }, null, 2));
