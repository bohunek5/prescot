import { readFile, writeFile } from "node:fs/promises";
import { resolve } from "node:path";
import { chromium } from "../../radlight/node_modules/playwright/index.mjs";

const TIM_ORIGIN = "https://dostawca.tim.pl";
const CDP_URL = "http://127.0.0.1:9222";
const QUEUE_IDS = [
  1290827,
  1290830,
  1290835,
  1290840,
  1290844,
  1292237,
  1292238,
  1292239,
  1292240,
  1292242,
];
const TAPE_QUEUE_IDS = [
  1781497,
  1781499,
  2417226,
  2488879,
  10625103,
  10625106,
  10626236,
  10626239,
];

function argumentValue(name, fallback = "") {
  const index = process.argv.indexOf(name);
  return index === -1 ? fallback : process.argv[index + 1] || fallback;
}

function clone(value) {
  return value == null ? value : JSON.parse(JSON.stringify(value));
}

function same(a, b) {
  return JSON.stringify(a) === JSON.stringify(b);
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

function saveGeneral(general) {
  const keys = [
    "objectFromVersion", "id", "creationDate", "userOwner", "published", "className", "fullpath", "php",
    "allowInheritance", "allowVariants", "showVariants", "showAppLoggerTab", "showFieldLookup",
    "linkGeneratorReference", "userModification", "versionDate", "versionCount", "iconCls", "icon", "cls",
    "qtipCfg", "text",
  ];
  return Object.fromEntries(keys.map((key) => [key, general?.[key] ?? null]));
}

function stableGeneral(general) {
  const keys = ["id", "parentId", "type", "key", "classId", "published", "className", "fullpath"];
  return Object.fromEntries(keys.map((key) => [key, clone(general?.[key])]));
}

function stockSnapshot(stockLevel) {
  return (Array.isArray(stockLevel) ? stockLevel : []).map((row) => ({
    id: Number(row?.id),
    published: row?.published,
    stockFreeQuantity: row?.stockFreeQuantity,
    stockTotalQuantity: row?.stockTotalQuantity,
    stockTotal55WDQuantity: row?.stockTotal55WDQuantity,
    stockTotalQuantityMz: row?.stockTotalQuantityMz,
  }));
}

function positiveStock(stockLevel) {
  return stockSnapshot(stockLevel).some((row) => Number(row.stockTotalQuantityMz || 0) > 0
    || Number(row.stockFreeQuantity || 0) > 0
    || Number(row.stockTotalQuantity || 0) > 0);
}

function protectedSnapshot(object) {
  const data = object?.data || {};
  return {
    general: stableGeneral(object?.general),
    workflowManagement: clone(object?.workflowManagement),
    ean: data.ean,
    manufacturerIndex: data.manufacturerIndex,
    supplierIndex: data.supplierIndex,
    timIndex: data.timIndex,
    timName: data.timName,
    state: data.state,
    status: data.status,
    listPrice: clone(data.listPrice),
    netCatalogPrice: clone(data.netCatalogPrice),
    stockLevel: stockSnapshot(data.stockLevel),
    productDescriptions: clone(data.productDescriptions),
    certifications: clone(data.certifications),
    instructions: clone(data.instructions),
    dataSheet: clone(data.dataSheet),
    mainPhoto: clone(data.mainPhoto),
    energyClass: clone(data.energyClass),
    energyClassLabels: clone(data.energyClassLabels),
    energyTechnicalCards: clone(data.energyTechnicalCards),
  };
}

function normalize(value) {
  return String(value ?? "").trim().replace(/,/g, ".");
}

function numberWithUnit(value, unit) {
  const match = normalize(value).match(new RegExp(`^(\\d+(?:\\.\\d+)?)\\s*${unit}(?:\\s*DC)?$`, "i"));
  return match ? match[1] : "";
}

function dimensions(value) {
  const match = normalize(value).match(/^(\d+(?:\.\d+)?)\s*x\s*(\d+(?:\.\d+)?)\s*x\s*(\d+(?:\.\d+)?)\s*mm$/i);
  return match ? { length: match[1], width: match[2], height: match[3] } : null;
}

function attribute(attributes, wanted) {
  const entry = Object.entries(attributes || {}).find(([key]) => key.toLocaleLowerCase("pl-PL") === wanted.toLocaleLowerCase("pl-PL"));
  return entry?.[1] ?? "";
}

function createEtimUpdate(object, product) {
  const etimField = findField(object?.layout, "etimTim");
  const groups = Object.entries(etimField?.activeGroupDefinitions || {});
  if (groups.length !== 1) throw new Error(`expected_one_active_etim_group:${groups.length}`);
  const [groupId, group] = groups[0];
  if (String(group.name || "") !== "EC002710") throw new Error(`unexpected_etim_class:${group.name || "none"}`);
  const definitions = (group.keys || []).map((entry) => ({
    keyId: String(entry.id),
    title: String(entry.definition?.title || "").trim(),
    type: String(entry.definition?.fieldtype || ""),
    options: entry.definition?.options || [],
  }));
  const byTitle = new Map(definitions.map((definition) => [definition.title, definition]));
  const size = dimensions(attribute(product.attributes, "Wymiar"));
  const voltage = numberWithUnit(attribute(product.attributes, "Napięcie Wyjściowe"), "V");
  const power = numberWithUnit(attribute(product.attributes, "Moc"), "W");
  const ipLabel = String(attribute(product.attributes, "Klasa szczelności")).trim().toUpperCase();
  if (!size || !voltage || !power || !/^IP\d{2}$/i.test(ipLabel)) throw new Error("incomplete_exact_source_attributes");
  const ipDefinition = byTitle.get("Stopień ochrony (IP)");
  const ipOption = ipDefinition?.options.find((option) => String(option.key).trim().toUpperCase() === ipLabel);
  if (!ipOption) throw new Error(`ip_option_not_found:${ipLabel}`);
  const proposed = [
    ["Szerokość [mm]", size.width],
    ["Wysokość [mm]", size.height],
    ["Napięcie wyjściowe [V]", voltage],
    ["Długość [mm]", size.length],
    ["Moc wyjściowa od/do [W]", power],
    ["Stopień ochrony (IP)", ipOption.value],
  ];
  for (const [title] of proposed) if (!byTitle.has(title)) throw new Error(`etim_definition_missing:${title}`);

  const current = clone(object.data?.etimTim || {});
  const currentDefault = current?.data && !Array.isArray(current.data) && current.data.default && !Array.isArray(current.data.default)
    ? clone(current.data.default) : {};
  const currentMetaDefault = current?.metaData && !Array.isArray(current.metaData) && current.metaData.default && !Array.isArray(current.metaData.default)
    ? clone(current.metaData.default) : {};
  const groupValues = currentDefault[groupId] && !Array.isArray(currentDefault[groupId]) ? clone(currentDefault[groupId]) : {};
  const groupMeta = currentMetaDefault[groupId] && !Array.isArray(currentMetaDefault[groupId]) ? clone(currentMetaDefault[groupId]) : {};
  const added = [];
  for (const [title, value] of proposed) {
    const definition = byTitle.get(title);
    const existing = groupValues[definition.keyId];
    if (existing !== null && existing !== undefined && existing !== "" && existing !== 0) continue;
    groupValues[definition.keyId] = value;
    groupMeta[definition.keyId] = { inherited: false, objectid: Number(object.general.id) };
    added.push({ keyId: Number(definition.keyId), title, type: definition.type, value });
  }
  const filledCount = Object.values(groupValues).filter((value) => value !== null && value !== undefined && value !== "" && value !== 0).length;
  if (filledCount < 4 || added.length < 1) throw new Error(`insufficient_safe_etim_values:${filledCount}`);
  const activeGroups = current?.activeGroups && !Array.isArray(current.activeGroups) ? clone(current.activeGroups) : {};
  activeGroups[groupId] = true;
  const groupCollectionMapping = current?.groupCollectionMapping && !Array.isArray(current.groupCollectionMapping)
    ? clone(current.groupCollectionMapping) : {};
  if (!(groupId in groupCollectionMapping)) groupCollectionMapping[groupId] = null;
  return {
    groupId: Number(groupId),
    value: {
      data: { default: { ...currentDefault, [groupId]: groupValues } },
      metaData: { default: { ...currentMetaDefault, [groupId]: groupMeta } },
      inherited: false,
      activeGroups,
      groupCollectionMapping,
    },
    added,
    filledCount,
  };
}

function exactNumber(value, unitPattern) {
  const match = normalize(value).match(new RegExp(`^(\\d+(?:\\.\\d+)?)\\s*${unitPattern}$`, "i"));
  return match ? match[1] : "";
}

function createTapeEtimUpdate(object, product) {
  const etimField = findField(object?.layout, "etimTim");
  const groups = Object.entries(etimField?.activeGroupDefinitions || {});
  if (groups.length !== 1) throw new Error(`expected_one_active_etim_group:${groups.length}`);
  const [groupId, group] = groups[0];
  if (String(group.name || "") !== "EC002706") throw new Error(`unexpected_etim_class:${group.name || "none"}`);
  const definitions = (group.keys || []).map((entry) => ({
    keyId: String(entry.id),
    title: String(entry.definition?.title || "").trim(),
    type: String(entry.definition?.fieldtype || ""),
    options: entry.definition?.options || [],
  }));
  const byTitle = new Map(definitions.map((definition) => [definition.title, definition]));
  const option = (title, label) => {
    const definition = byTitle.get(title);
    const match = definition?.options.find((item) => String(item.key).trim().toLocaleLowerCase("pl-PL") === String(label).trim().toLocaleLowerCase("pl-PL"));
    if (!match) throw new Error(`etim_option_not_found:${title}:${label}`);
    return match.value;
  };
  const width = exactNumber(attribute(product.attributes, "Szerokość taśmy"), "mm");
  const luminousFlux = exactNumber(attribute(product.attributes, "Jasność"), "lm(?:/m)?");
  const voltage = exactNumber(attribute(product.attributes, "Napięcie wejściowe"), "V(?:\\s*DC)?");
  const power = exactNumber(attribute(product.attributes, "Moc"), "W/m");
  const segment = exactNumber(attribute(product.attributes, "Moduł cięcia"), "mm");
  const ledCount = exactNumber(attribute(product.attributes, "Ilość diod"), "(?:/m)?");
  const angle = exactNumber(attribute(product.attributes, "Kąt świecenia"), "°");
  const rollMetres = exactNumber(attribute(product.attributes, "Rolka"), "m");
  const temperature = String(product.name || "").match(/\b(\d{4})\s*K\b/i)?.[1] || "";
  const soldByMetre = String(attribute(product.attributes, "Taśma na metry")).trim().toLocaleLowerCase("pl-PL") === "tak";
  const length = rollMetres ? String(soldByMetre ? 1000 : Number(rollMetres) * 1000) : "";
  const lightText = `${attribute(product.attributes, "Barwa światła")} ${product.name || ""}`.toLocaleLowerCase("pl-PL");
  const lightLabel = lightText.includes("ciepł") ? "Ciepła"
    : lightText.includes("neutral") ? "Neutralna"
      : lightText.includes("zimn") ? "Zimna"
        : Number(temperature) <= 3500 ? "Ciepła"
          : Number(temperature) <= 5000 ? "Neutralna"
            : Number(temperature) > 5000 ? "Zimna" : "";
  if (![width, luminousFlux, voltage, power, segment, ledCount, angle, length, temperature, lightLabel].every(Boolean)) {
    throw new Error("incomplete_exact_tape_source_attributes");
  }
  const proposed = [
    ["Szerokość [mm]", width],
    ["Model", option("Model", "Taśma")],
    ["Strumień świetlny [lm]", luminousFlux],
    ["Temperatura barwowa [K]", temperature],
    ["Kąt rozsyłu światła [°]", angle],
    ["Rodzaj napięcia", option("Rodzaj napięcia", "DC")],
    ["Napięcie lampy [V]", voltage],
    ["Typ lampy", option("Typ lampy", "LED")],
    ["Długość [mm]", length],
    ["Moc lampy na metr [W]", power],
    ["Długość pojedynczego segmentu [mm]", segment],
    ["Ilość diod LED na metr", ledCount],
    ["Barwa światła", option("Barwa światła", lightLabel)],
  ];
  for (const [title] of proposed) if (!byTitle.has(title)) throw new Error(`etim_definition_missing:${title}`);

  const current = clone(object.data?.etimTim || {});
  const currentDefault = current?.data && !Array.isArray(current.data) && current.data.default && !Array.isArray(current.data.default)
    ? clone(current.data.default) : {};
  const currentMetaDefault = current?.metaData && !Array.isArray(current.metaData) && current.metaData.default && !Array.isArray(current.metaData.default)
    ? clone(current.metaData.default) : {};
  const groupValues = currentDefault[groupId] && !Array.isArray(currentDefault[groupId]) ? clone(currentDefault[groupId]) : {};
  const groupMeta = currentMetaDefault[groupId] && !Array.isArray(currentMetaDefault[groupId]) ? clone(currentMetaDefault[groupId]) : {};
  const added = [];
  for (const [title, value] of proposed) {
    const definition = byTitle.get(title);
    const existing = groupValues[definition.keyId];
    if (existing !== null && existing !== undefined && existing !== "" && existing !== 0) continue;
    groupValues[definition.keyId] = value;
    groupMeta[definition.keyId] = { inherited: false, objectid: Number(object.general.id) };
    added.push({ keyId: Number(definition.keyId), title, type: definition.type, value });
  }
  const filledCount = Object.values(groupValues).filter((value) => value !== null && value !== undefined && value !== "" && value !== 0).length;
  if (filledCount < 10 || added.length < 1) throw new Error(`insufficient_safe_etim_values:${filledCount}`);
  const activeGroups = current?.activeGroups && !Array.isArray(current.activeGroups) ? clone(current.activeGroups) : {};
  activeGroups[groupId] = true;
  const groupCollectionMapping = current?.groupCollectionMapping && !Array.isArray(current.groupCollectionMapping)
    ? clone(current.groupCollectionMapping) : {};
  if (!(groupId in groupCollectionMapping)) groupCollectionMapping[groupId] = null;
  return {
    groupId: Number(groupId),
    value: {
      data: { default: { ...currentDefault, [groupId]: groupValues } },
      metaData: { default: { ...currentMetaDefault, [groupId]: groupMeta } },
      inherited: false,
      activeGroups,
      groupCollectionMapping,
    },
    added,
    filledCount,
  };
}

const apply = process.argv.includes("--apply");
const family = argumentValue("--family", "power");
if (!["power", "tapes"].includes(family)) throw new Error(`Nieobsługiwana rodzina: ${family}`);
const start = Math.max(0, Number(argumentValue("--start", "0")) || 0);
const limit = Math.max(1, Number(argumentValue("--limit", "1")) || 1);
const maxCards = Math.max(0, Number(argumentValue("--max-cards", "0")) || 0);
const outputPath = resolve(argumentValue("--output", `exports/tim/remediation/basic-etim-${family}-live.json`));
if (apply && maxCards < 1) throw new Error("Tryb --apply wymaga dodatniego --max-cards.");

const catalogDocument = JSON.parse(await readFile(resolve("data/catalog.json"), "utf8"));
const catalog = Array.isArray(catalogDocument) ? catalogDocument : catalogDocument.products || [];
const byIdentity = new Map();
for (const product of catalog) {
  const key = `${String(product.ean || "").trim()}|${String(product.manufacturerCode || "").trim()}`;
  if (!byIdentity.has(key)) byIdentity.set(key, []);
  byIdentity.get(key).push(product);
}
const familyQueue = family === "tapes" ? TAPE_QUEUE_IDS : QUEUE_IDS;
const queue = familyQueue.slice(start, start + limit);
const report = {
  generatedAt: new Date().toISOString(),
  apply,
  family,
  start,
  limit,
  maxCards,
  queue,
  results: [],
};
const persist = () => writeFile(outputPath, `${JSON.stringify(report, null, 2)}\n`, "utf8");

const browser = await chromium.connectOverCDP(CDP_URL);
const context = browser.contexts()[0];
let page = null;
let frame = null;
for (const candidate of context.pages()) {
  const candidateFrame = candidate.frames().find((item) => item.url() === `${TIM_ORIGIN}/pimcore/admin/`);
  if (candidateFrame) {
    const authenticated = await candidateFrame.evaluate(() => Boolean(window.Ext)
      && Boolean(window.pimcore?.settings?.csrfToken)
      && Number(window.pimcore?.currentuser?.id) > 0
      && window.pimcore?.currentuser?.active === true).catch(() => false);
    if (authenticated) {
      page = candidate;
      frame = candidateFrame;
      break;
    }
  }
}
if (!page || !frame) throw new Error("Brak uwierzytelnionej ramki PIMCORE.");

async function readObject(id) {
  for (let attempt = 0; attempt < 8; attempt += 1) {
    const result = await frame.evaluate(async ({ objectId, token }) => {
      const response = await fetch(`/pimcore/admin/object/get?id=${objectId}&_=${token}`, {
        credentials: "same-origin",
        cache: "no-store",
        headers: { Accept: "application/json", "Cache-Control": "no-cache" },
      });
      let payload = null;
      try { payload = await response.json(); } catch {}
      return { status: response.status, payload };
    }, { objectId: id, token: `${Date.now()}-${attempt}` });
    if (result.status === 200 && result.payload) return result.payload;
    await page.waitForTimeout(500);
  }
  throw new Error(`object_read_failed:${id}`);
}

let written = 0;
for (const id of queue) {
  if (apply && written >= maxCards) break;
  const result = { id, status: "failed" };
  try {
    const before = await readObject(id);
    const data = before.data || {};
    result.ean = String(data.ean || "");
    result.model = String(data.manufacturerIndex || "");
    result.timName = String(data.timName || "");
    const exact = byIdentity.get(`${result.ean}|${result.model}`) || [];
    const expectedCategory = family === "tapes" ? "Taśmy LED" : "Zasilacze LED";
    if (exact.length !== 1 || exact[0].categoryRoot !== expectedCategory) throw new Error(`catalog_identity_not_unique:${exact.length}`);
    if (Number(before.general?.id) !== id
      || before.general?.published !== true
      || before.general?.locked === true
      || String(data.state || "") !== "active"
      || String(data.status || "") !== "active"
      || !positiveStock(data.stockLevel)) throw new Error("live_identity_state_or_stock_guard_failed");
    const update = family === "tapes" ? createTapeEtimUpdate(before, exact[0]) : createEtimUpdate(before, exact[0]);
    result.added = update.added;
    result.filledAfter = update.filledCount;
    result.beforeVersion = Number(before.general.versionCount);
    result.protectedBefore = protectedSnapshot(before);
    if (!apply) {
      result.status = "verified_ready_dry_run";
      report.results.push(result);
      await persist();
      continue;
    }
    const saveData = { etimTim: update.value };
    const save = await frame.evaluate(async ({ objectId, dataValue, generalValue }) => {
      const body = new URLSearchParams({
        id: String(objectId),
        data: JSON.stringify(dataValue),
        general: JSON.stringify(generalValue),
        dirtyFields: JSON.stringify(["etimTim"]),
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
      return { status: response.status, ok: response.ok, body: String(await response.text()).slice(0, 20_000) };
    }, { objectId: id, dataValue: saveData, generalValue: saveGeneral(before.general) });
    result.saveStatus = save.status;
    result.saveBody = save.body;
    if (!save.ok || save.status !== 200) throw new Error(`save_failed:http_${save.status}`);
    let after = null;
    let valuesApplied = false;
    for (let attempt = 0; attempt < 8; attempt += 1) {
      after = await readObject(id);
      const values = after.data?.etimTim?.data?.default?.[String(update.groupId)] || {};
      valuesApplied = update.added.every((entry) => same(values[String(entry.keyId)], entry.value));
      if (valuesApplied) break;
      await page.waitForTimeout(500);
    }
    if (!valuesApplied) throw new Error("etim_values_not_applied");
    const protectedAfter = protectedSnapshot(after);
    if (!same(result.protectedBefore, protectedAfter)) {
      result.protectedAfter = protectedAfter;
      throw new Error("protected_fields_changed");
    }
    const versionDelta = Number(after.general?.versionCount) - result.beforeVersion;
    if (![0, 1].includes(versionDelta)) throw new Error(`unexpected_version_delta:${versionDelta}`);
    result.status = "saved_verified";
    result.afterVersion = Number(after.general?.versionCount);
    result.progressAfter = Number(after.data?.etimByTimComplementProgress || 0);
    result.protectedFieldsUnchanged = true;
    delete result.protectedBefore;
    written += 1;
  } catch (error) {
    result.reason = String(error?.message || error);
    report.results.push(result);
    await persist();
    break;
  }
  report.results.push(result);
  await persist();
  console.log(JSON.stringify({ id: result.id, model: result.model, status: result.status, added: result.added?.length, progressAfter: result.progressAfter }));
}

report.completedAt = new Date().toISOString();
report.summary = {
  selected: queue.length,
  ready: report.results.filter((item) => item.status === "verified_ready_dry_run").length,
  saved: report.results.filter((item) => item.status === "saved_verified").length,
  failed: report.results.filter((item) => item.status === "failed").length,
};
await persist();
await browser.close();
console.log(JSON.stringify({ output: outputPath, ...report.summary }, null, 2));
