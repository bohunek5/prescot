import { chromium } from "../../radlight/node_modules/playwright/index.mjs";

const CDP_URL = "http://127.0.0.1:9222";
const OBJECT_ID = 15907539;
const capturePopulated = process.argv.includes("--capture-populated");
const TEST_DOCUMENTS = {
  certifications: { id: 19067751, path: "/Import multimediow/24248/CE_Prescot_zasilacze_PR-MADXX-1224.pdf" },
  instructions: { id: 19067752, path: "/Import multimediow/24248/Instrukcja_PR-MADXX-1224.pdf" },
  dataSheet: { id: 19067753, path: "/Import multimediow/24248/PR-MAD36-1224_karta_katalogowa.pdf" },
};

const browser = await chromium.connectOverCDP(CDP_URL);
const context = browser.contexts()[0];
let page = null;
let frame = null;

for (const candidate of context.pages()) {
  for (const candidateFrame of candidate.frames().filter((item) => item.url().includes("/pimcore/admin/"))) {
    const authenticated = await candidateFrame.evaluate(() => {
      try {
        return typeof window.pimcore?.globalmanager?.get?.("user")?.isAllowed === "function";
      } catch {
        return false;
      }
    }).catch(() => false);
    if (authenticated) {
      page = candidate;
      frame = candidateFrame;
      break;
    }
  }
  if (frame) break;
}

if (!page || !frame) throw new Error("Brak uwierzytelnionej ramki PIMCORE.");

let capturedSave = null;
const blockedRequests = [];
const routeHandler = async (route) => {
  const request = route.request();
  const url = new URL(request.url());
  if (request.method() === "PUT" && new URL(request.url()).pathname === "/pimcore/admin/object/save") {
    const params = new URLSearchParams(request.postData() || "");
    capturedSave = {
      url: request.url(),
      keys: [...params.keys()],
      data: JSON.parse(params.get("data") || "null"),
      dirtyFields: JSON.parse(params.get("dirtyFields") || "null"),
      general: JSON.parse(params.get("general") || "null"),
      csrfHeaderPresent: Boolean(request.headers()["x-pimcore-csrf-token"]),
    };
    return route.abort("blockedbyclient");
  }
  if (request.method() === "POST" && url.pathname === `/admin/workflow/actions/${OBJECT_ID}`) return route.continue();
  if (!["GET", "HEAD", "OPTIONS"].includes(request.method())) {
    blockedRequests.push({ method: request.method(), url: request.url() });
    return route.abort("blockedbyclient");
  }
  return route.continue();
};

await page.route("**/*", routeHandler);

await frame.evaluate((id) => {
  const key = `object_${id}`;
  const existing = window.pimcore?.globalmanager?.get?.(key);
  if (existing?.edit?.dataFields?.certifications) return;
  try { existing?.tab?.close?.(); } catch {}
  try { window.pimcore?.globalmanager?.remove?.(key); } catch {}
  window.pimcore.helpers.openObject(id, "object");
}, OBJECT_ID);
await frame.waitForFunction((id) => Boolean(window.pimcore?.globalmanager?.get?.(`object_${id}`)), OBJECT_ID, { timeout: 20_000 });
await frame.waitForFunction((id) => Boolean(window.pimcore?.globalmanager?.get?.(`object_${id}`)?.edit?.dataFields?.certifications), OBJECT_ID, { timeout: 20_000 }).catch(() => {});
await page.waitForTimeout(1_500);

const output = await frame.evaluate((id) => {
  const object = window.pimcore.globalmanager.get(`object_${id}`);
  const panels = window.Ext.ComponentQuery.query("panel").filter((component) => [
    "Podstawowe", "Multimedia/Załączniki", "Cechy | Wersja ETIM", "Dane PIM",
  ].includes(component.title));
  const multimedia = panels.find((component) => component.title === "Multimedia/Załączniki");
  if (multimedia?.ownerCt?.setActiveTab) multimedia.ownerCt.setActiveTab(multimedia);
  const fields = object?.edit?.dataFields || {};
  const describe = (field) => field ? {
    className: field.$className || field.self?.getName?.() || field.constructor?.name || null,
    keys: Object.keys(field).sort(),
    hasGetValue: typeof field.getValue === "function",
    hasSetValue: typeof field.setValue === "function",
    value: typeof field.getValue === "function" ? field.getValue() : undefined,
    componentId: field.id || field.getId?.() || null,
    rendered: field.rendered ?? null,
    xtype: field.xtype || field.getXType?.() || null,
  } : null;
  return {
    url: location.href,
    objectKeys: Object.keys(object || {}).sort(),
    editKeys: Object.keys(object?.edit || {}).sort(),
    dataFieldKeys: Object.keys(fields).sort(),
    panels: panels.map((component) => ({
      id: component.id,
      title: component.title,
      active: component.ownerCt?.getActiveTab?.() === component,
      rendered: component.rendered,
    })),
    fields: {
      certifications: describe(fields.certifications),
      instructions: describe(fields.instructions),
      dataSheet: describe(fields.dataSheet),
    },
  };
}, OBJECT_ID);

await page.waitForTimeout(1_200);
const refreshed = await frame.evaluate((id) => {
  const object = window.pimcore.globalmanager.get(`object_${id}`);
  const fields = object?.edit?.dataFields || {};
  const describe = (field) => field ? {
    className: field.$className || field.self?.getName?.() || field.constructor?.name || null,
    keys: Object.keys(field).sort(),
    hasGetValue: typeof field.getValue === "function",
    hasSetValue: typeof field.setValue === "function",
    value: typeof field.getValue === "function" ? field.getValue() : undefined,
    componentId: field.id || field.getId?.() || null,
    xtype: field.xtype || field.getXType?.() || null,
    store: field.store?.getRange?.().map((record) => record.data) || null,
    component: field.component ? {
      id: field.component.id || null,
      xtype: field.component.xtype || field.component.getXType?.() || null,
      keys: Object.keys(field.component).sort(),
    } : null,
    storeModelFields: field.store?.model?.getFields?.().map((item) => ({
      name: item.name,
      type: item.type,
      defaultValue: item.defaultValue,
    })) || null,
    ownMethodNames: Object.getOwnPropertyNames(Object.getPrototypeOf(field) || {}).sort(),
    inheritedMethodNames: Object.getOwnPropertyNames(Object.getPrototypeOf(Object.getPrototypeOf(field) || {}) || {}).sort(),
    getValueSource: typeof field.getValue === "function" ? String(field.getValue).slice(0, 8_000) : null,
  } : null;
  return {
    dataFieldKeys: Object.keys(fields).sort(),
    fields: {
      certifications: describe(fields.certifications),
      instructions: describe(fields.instructions),
      dataSheet: describe(fields.dataSheet),
    },
  };
}, OBJECT_ID);

let populatedValues = null;
if (capturePopulated) {
  populatedValues = await frame.evaluate(({ id, documents }) => {
    const object = window.pimcore.globalmanager.get(`object_${id}`);
    for (const [name, asset] of Object.entries(documents)) {
      const field = object.edit.dataFields[name];
      field.store.removeAll();
      field.store.add({
        id: asset.id,
        path: asset.path,
        type: "asset",
        subtype: "document",
        expirationdate: null,
        rowId: `${asset.id}$$1$$asset`,
      });
      if (typeof field.dataChanged === "function") field.dataChanged();
    }
    object.dirty = true;
    const values = Object.fromEntries(Object.entries(documents).map(([name]) => [name, object.edit.dataFields[name].getValue()]));
    const button = object.toolbarButtons?.save;
    if (typeof button?.handler !== "function") throw new Error("Brak natywnego handlera zapisu.");
    button.handler(button);
    return values;
  }, { id: OBJECT_ID, documents: TEST_DOCUMENTS });
  await page.waitForTimeout(1_500);
}

console.log(JSON.stringify({ output, refreshed, populatedValues, capturedSave, blockedRequests }, null, 2));

await frame.evaluate((id) => {
  const object = window.pimcore?.globalmanager?.get?.(`object_${id}`);
  try {
    for (const name of ["certifications", "instructions", "dataSheet"]) object?.edit?.dataFields?.[name]?.store?.removeAll?.();
    object.dirty = false;
    object._allowDirtyClose = true;
  } catch {}
  try { object?.tab?.close?.(); } catch {}
}, OBJECT_ID).catch(() => {});
await page.waitForTimeout(500);
await page.unroute("**/*", routeHandler);
process.exit(0);
