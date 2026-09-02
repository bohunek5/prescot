import { writeFile } from "node:fs/promises";
import { resolve } from "node:path";
import { chromium } from "../../radlight/node_modules/playwright/index.mjs";

const apply = process.argv.includes("--apply");
const outputIndex = process.argv.indexOf("--output");
const output = resolve(outputIndex >= 0 ? process.argv[outputIndex + 1] : "exports/tim/remediation/pr-mad36-price-restore.json");
const objectId = 15907539;
const expected = {
  ean: "5905475368073",
  model: "PR-MAD36-1224",
  listPrice: { value: 23.5, unit: "1" },
  netCatalogPriceBeforePilot: { value: 19.11, unit: "1" },
  documents: {
    certifications: 19067751,
    instructions: 19067752,
    dataSheet: 19067753,
  },
};

const clone = (value) => value == null ? value : JSON.parse(JSON.stringify(value));
const same = (a, b) => JSON.stringify(a) === JSON.stringify(b);
const withoutNetPrice = (data) => {
  const copy = clone(data || {});
  delete copy.netCatalogPrice;
  return copy;
};
const saveGeneral = (general) => Object.fromEntries([
  "objectFromVersion", "id", "creationDate", "userOwner", "published", "className", "fullpath", "php",
  "allowInheritance", "allowVariants", "showVariants", "showAppLoggerTab", "showFieldLookup",
  "linkGeneratorReference", "userModification", "versionDate", "versionCount", "iconCls", "icon", "cls",
  "qtipCfg", "text",
].map((key) => [key, general?.[key] ?? null]));
const stableGeneral = (general) => Object.fromEntries([
  "id", "parentId", "type", "key", "classId", "published", "className", "fullpath",
].map((key) => [key, clone(general?.[key])]));
const documentId = (value) => Array.isArray(value) && value.length === 1 ? Number(value[0]?.id) : 0;

const report = { generatedAt: new Date().toISOString(), apply, objectId, expected, status: "pending", save: null };
const persist = () => writeFile(output, `${JSON.stringify(report, null, 2)}\n`, "utf8");

const browser = await chromium.connectOverCDP("http://127.0.0.1:9222");
const context = browser.contexts()[0];
const page = context.pages().find((item) => item.url() === "https://dostawca.tim.pl/pimcore/admin/");
if (!page) throw new Error("Brak bezpośredniej karty PIMCORE.");
await page.reload({ waitUntil: "domcontentloaded" });
await page.waitForTimeout(2_000);
const ready = await page.evaluate(() => Boolean(window.Ext)
  && Boolean(window.pimcore?.settings?.csrfToken)
  && Number(window.pimcore?.currentuser?.id) > 0
  && window.pimcore?.currentuser?.active === true);
if (!ready) throw new Error("Sesja PIMCORE nie jest gotowa.");

async function readObject() {
  const response = await context.request.get(`https://dostawca.tim.pl/pimcore/admin/object/get?id=${objectId}&_=${Date.now()}`, {
    headers: { Accept: "application/json", "Cache-Control": "no-cache" },
  });
  if (response.status() !== 200) throw new Error(`Odczyt karty HTTP ${response.status()}`);
  return response.json();
}

const before = await readObject();
const data = before.data || {};
if (Number(before.general?.id) !== objectId
  || String(data.ean || "") !== expected.ean
  || String(data.manufacturerIndex || "") !== expected.model
  || String(data.state || "") !== "new"
  || String(data.status || "") !== "new"
  || before.general?.published !== true
  || before.general?.locked
  || !same(data.listPrice, expected.listPrice)
  || data.netCatalogPrice?.value !== null
  || documentId(data.certifications) !== expected.documents.certifications
  || documentId(data.instructions) !== expected.documents.instructions
  || documentId(data.dataSheet) !== expected.documents.dataSheet) {
  throw new Error("Karta nie spełnia warunków bezpiecznego przywrócenia ceny.");
}
report.before = {
  versionCount: before.general.versionCount,
  listPrice: data.listPrice,
  netCatalogPrice: data.netCatalogPrice,
  state: data.state,
  status: data.status,
};
if (!apply) {
  report.status = "verified_dry_run";
  await persist();
  console.log(JSON.stringify({ status: report.status, objectId }));
  process.exit(0);
}

const save = await page.evaluate(async ({ id, dataValue, generalValue, dirtyFieldsValue }) => new Promise((resolveRequest) => {
  window.Ext.Ajax.request({
    url: "/pimcore/admin/object/save?task=undefined",
    method: "PUT",
    headers: { "X-Pimcore-CSRF-Token": window.pimcore.settings.csrfToken },
    params: { id, data: JSON.stringify(dataValue), general: JSON.stringify(generalValue), dirtyFields: JSON.stringify(dirtyFieldsValue) },
    callback: (_options, success, response) => resolveRequest({
      success,
      status: response?.status || 0,
      body: String(response?.responseText || "").slice(0, 20_000),
    }),
  });
}), {
  id: objectId,
  dataValue: { netCatalogPrice: expected.netCatalogPriceBeforePilot },
  generalValue: saveGeneral(before.general),
  dirtyFieldsValue: ["netCatalogPrice"],
});
report.save = save;

let after = null;
for (let attempt = 0; attempt < 8; attempt += 1) {
  after = await readObject();
  if (same(after.data?.netCatalogPrice, expected.netCatalogPriceBeforePilot)) break;
  await page.waitForTimeout(750);
}
if (save.status !== 200 || save.success !== true) throw new Error(`Przywrócenie ceny HTTP ${save.status}`);
if (!same(after.data?.netCatalogPrice, expected.netCatalogPriceBeforePilot)) throw new Error("Cena katalogowa nie została przywrócona.");
if (!same(withoutNetPrice(after.data), withoutNetPrice(before.data))) throw new Error("Po przywróceniu ceny zmieniły się inne dane.");
if (!same(stableGeneral(after.general), stableGeneral(before.general))) throw new Error("Po przywróceniu ceny zmieniły się dane ogólne.");
if (!same(after.workflowManagement, before.workflowManagement)) throw new Error("Po przywróceniu ceny zmienił się workflow.");
report.after = {
  versionCount: after.general.versionCount,
  listPrice: after.data.listPrice,
  netCatalogPrice: after.data.netCatalogPrice,
  state: after.data.state,
  status: after.data.status,
};
report.status = "restored_and_verified";
await persist();
console.log(JSON.stringify({ status: report.status, objectId, before: report.before, after: report.after }));
process.exit(0);
