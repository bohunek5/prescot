import { readFile, writeFile } from "node:fs/promises";
import { resolve } from "node:path";
import { chromium } from "../../radlight/node_modules/playwright/index.mjs";

const apply = process.argv.includes("--apply");
const outputIndex = process.argv.indexOf("--output");
const output = resolve(outputIndex >= 0 ? process.argv[outputIndex + 1] : "exports/tim/remediation/buffer-ip67-nw-energy-class-repair.json");
const objectId = 15907505;
const fichePath = resolve("tmp/pdfs/eprel-buffer-priority-family/24EC320NW50IP67_Fiche_2724835_PL.pdf");
const activationQueuePath = resolve("exports/tim/remediation/buffer-ip67-priority3-activation-queue-2026-09-01.json");
const expected = {
  ean: "5905475368172",
  model: "24EC320NW50IP67",
  timIndex: "P000-00000-25196",
  eprelModel: "24EC320NW1IP67",
  eprelId: "2724835",
  beforeClass: "F",
  correctClass: "G",
  listPrice: 450,
  labelPath: "/Import multimediow/24248/24EC320NW50IP67_EPREL_2724835_etykieta.jpg",
  ficheRelationPath: "/Import multimediow/24248/24EC320NW50IP67_EPREL_2724835_karta_informacyjna.pdf",
};

const clone = (value) => value == null ? value : JSON.parse(JSON.stringify(value));
const same = (a, b) => JSON.stringify(a) === JSON.stringify(b);
const relationPath = (value) => Array.isArray(value) && value.length === 1 ? String(value[0]?.path || "") : "";
const money = (value) => Number(value && typeof value === "object" ? value.value : value);
const normalizedWithoutEnergyClass = (data) => {
  const copy = clone(data || {});
  delete copy.energyClass;
  for (const stock of copy.stockLevel || []) {
    delete stock.modificationDate;
    delete stock.updatedAt;
  }
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

const ficheBytes = await readFile(fichePath);
if (ficheBytes.subarray(0, 4).toString("ascii") !== "%PDF") throw new Error("Oficjalna karta EPREL nie jest plikiem PDF.");
const activationQueue = JSON.parse(await readFile(activationQueuePath, "utf8"));
const activationEvidence = activationQueue.items?.find((item) => Number(item.id) === objectId);
if (!activationEvidence
  || activationEvidence.ean !== expected.ean
  || activationEvidence.model !== expected.model
  || Number(activationEvidence.price) !== expected.listPrice
  || Number(activationEvidence.xmlStock) <= 0
  || activationEvidence.eprelId !== expected.eprelId
  || activationEvidence.eprelModel !== expected.eprelModel) {
  throw new Error("Brak spójnego dowodu XML/EPREL z kolejki aktywacyjnej.");
}

const report = { generatedAt: new Date().toISOString(), apply, objectId, expected, evidence: { fichePath, pdfSignature: true, activationQueuePath, xmlStock: activationEvidence.xmlStock }, status: "pending", save: null };
const persist = () => writeFile(output, `${JSON.stringify(report, null, 2)}\n`, "utf8");

const browser = await chromium.connectOverCDP("http://127.0.0.1:9222");
const context = browser.contexts()[0];
const page = context.pages().find((item) => item.url() === "https://dostawca.tim.pl/pimcore/admin/");
if (!page) throw new Error("Brak bezpośredniej, zalogowanej karty PIMCORE.");
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
const liveStock = Math.max(0, ...(data.stockLevel || []).map((entry) => Number(entry.stockTotalQuantityMz) || 0));
const guards = {
  id: Number(before.general?.id) === objectId,
  ean: String(data.ean || "") === expected.ean,
  model: String(data.manufacturerIndex || "") === expected.model,
  timIndex: String(data.timIndex || "") === expected.timIndex,
  state: String(data.state || "") === "active",
  status: String(data.status || "") === "active",
  published: before.general?.published === true,
  unlocked: !before.general?.locked,
  price: money(data.listPrice) === expected.listPrice,
  xmlPositiveStockEvidence: Number(activationEvidence.xmlStock) > 0,
  label: relationPath(data.energyClassLabels) === expected.labelPath,
  fiche: relationPath(data.energyTechnicalCards) === expected.ficheRelationPath,
};
report.guards = guards;
if (!Object.values(guards).every(Boolean)) {
  report.status = "guard_failed";
  report.live = {
    id: before.general?.id,
    ean: data.ean,
    model: data.manufacturerIndex,
    timIndex: data.timIndex,
    state: data.state,
    status: data.status,
    published: before.general?.published,
    locked: before.general?.locked,
    price: data.listPrice,
    liveStock,
    labelPath: relationPath(data.energyClassLabels),
    fichePath: relationPath(data.energyTechnicalCards),
  };
  await persist();
  throw new Error("Karta nie spełnia warunków bezpiecznej korekty klasy EPREL.");
}
if (![expected.beforeClass, expected.correctClass].includes(String(data.energyClass || ""))) {
  throw new Error(`Nieoczekiwana bieżąca klasa: ${String(data.energyClass || "<pusta>")}`);
}
report.before = {
  versionCount: before.general.versionCount,
  energyClass: data.energyClass,
  state: data.state,
  status: data.status,
  timIndex: data.timIndex,
  listPrice: data.listPrice,
  liveStock,
  labelPath: relationPath(data.energyClassLabels),
  fichePath: relationPath(data.energyTechnicalCards),
};
if (String(data.energyClass) === expected.correctClass) {
  report.status = "already_correct";
  await persist();
  console.log(JSON.stringify({ status: report.status, objectId }));
  process.exit(0);
}
if (!apply) {
  report.status = "verified_ready_dry_run";
  await persist();
  console.log(JSON.stringify({ status: report.status, objectId, beforeClass: data.energyClass, correctClass: expected.correctClass }));
  process.exit(0);
}

const save = await page.evaluate(async ({ id, dataValue, generalValue, dirtyFieldsValue }) => {
  const body = new URLSearchParams({
    id: String(id),
    data: JSON.stringify(dataValue),
    general: JSON.stringify(generalValue),
    dirtyFields: JSON.stringify(dirtyFieldsValue),
  });
  const response = await fetch("/pimcore/admin/object/save?task=undefined", {
    method: "PUT",
    credentials: "same-origin",
    headers: {
      "X-Pimcore-CSRF-Token": window.pimcore.settings.csrfToken,
      "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    },
    body,
  });
  return {
    success: response.ok,
    status: response.status,
    body: String(await response.text()).slice(0, 20_000),
  };
}, {
  id: objectId,
  dataValue: { energyClass: expected.correctClass },
  generalValue: saveGeneral(before.general),
  dirtyFieldsValue: ["energyClass"],
});
report.save = save;

let after = null;
for (let attempt = 0; attempt < 8; attempt += 1) {
  after = await readObject();
  if (String(after.data?.energyClass || "") === expected.correctClass) break;
  await page.waitForTimeout(750);
}
if (save.status !== 200 || save.success !== true) throw new Error(`Korekta klasy HTTP ${save.status}`);
if (String(after.data?.energyClass || "") !== expected.correctClass) throw new Error("Klasa energetyczna nie została poprawiona.");
if (!same(normalizedWithoutEnergyClass(after.data), normalizedWithoutEnergyClass(before.data))) throw new Error("Po korekcie zmieniły się inne dane produktu.");
if (!same(stableGeneral(after.general), stableGeneral(before.general))) throw new Error("Po korekcie zmieniły się dane ogólne.");
if (!same(after.workflowManagement, before.workflowManagement)) throw new Error("Po korekcie zmienił się workflow.");
report.after = {
  versionCount: after.general.versionCount,
  energyClass: after.data.energyClass,
  state: after.data.state,
  status: after.data.status,
  timIndex: after.data.timIndex,
  listPrice: after.data.listPrice,
  labelPath: relationPath(after.data.energyClassLabels),
  fichePath: relationPath(after.data.energyTechnicalCards),
};
report.status = "repaired_and_verified";
await persist();
console.log(JSON.stringify({ status: report.status, objectId, beforeClass: data.energyClass, afterClass: after.data.energyClass }));
process.exit(0);
