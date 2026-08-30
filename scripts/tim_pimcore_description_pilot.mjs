import { readFile, writeFile } from "node:fs/promises";
import { resolve } from "node:path";
import { chromium } from "../../radlight/node_modules/playwright/index.mjs";

function argumentValue(name, fallback = "") {
  const index = process.argv.indexOf(name);
  return index === -1 ? fallback : process.argv[index + 1] || fallback;
}

const profileDir = argumentValue("--profile-dir");
const objectId = Number(argumentValue("--object-id"));
const openActionsMenu = process.argv.includes("--open-actions-menu");
const dryRunSave = process.argv.includes("--dry-run-save");
const applySave = process.argv.includes("--apply");
const pilotJsonPath = resolve(argumentValue("--pilot-json", "exports/tim/pilots/active-description-pilot.json"));
const pilotStage = argumentValue("--pilot-stage", "pilot1");
const targetTab = argumentValue("--tab", "Dane PIM");
const outputPath = resolve(argumentValue("--output", "/tmp/tim-pimcore-description-inspect.json"));
const screenshotPath = resolve(argumentValue("--screenshot", "/tmp/tim-pimcore-description-inspect.png"));
if (!profileDir) throw new Error("Podaj --profile-dir z izolowaną kopią profilu Chrome.");
if (!Number.isFinite(objectId) || objectId <= 0) throw new Error("Podaj prawidłowe --object-id.");
if (dryRunSave && applySave) throw new Error("Wybierz tylko jeden tryb: --dry-run-save albo --apply.");

let pilot = null;
if (dryRunSave || applySave) {
  const pilotDocument = JSON.parse(await readFile(pilotJsonPath, "utf8"));
  const stage = pilotDocument?.stages?.[pilotStage];
  if (!Array.isArray(stage)) throw new Error(`Nie ma etapu ${pilotStage} w kolejce pilota.`);
  pilot = stage.find((item) => Number(item.pimcoreId) === objectId);
  if (!pilot || !pilot.descriptionHtml || !pilot.ean) {
    throw new Error(`Etap ${pilotStage} nie zawiera kompletnego rekordu karty ${objectId}.`);
  }
}

const allowedPosts = [];
const allowedWrites = [];
const blockedPosts = [];
let expectedSaveHtml = "";
const context = await chromium.launchPersistentContext(profileDir, {
  headless: true,
  executablePath: "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
  args: ["--profile-directory=Default"],
  viewport: { width: 1800, height: 1200 },
  serviceWorkers: "block",
});

await context.route("**/*", async (route) => {
  const request = route.request();
  const method = request.method().toUpperCase();
  const url = request.url();
  if (["GET", "HEAD", "OPTIONS"].includes(method)) return route.continue();
  if (method === "POST" && new RegExp(`^https://dostawca\\.tim\\.pl/admin/workflow/actions/${objectId}$`).test(url)) {
    allowedPosts.push({ method, url });
    return route.continue();
  }
  if (applySave && method === "PUT" && url === "https://dostawca.tim.pl/pimcore/admin/object/save?task=undefined") {
    const params = new URLSearchParams(request.postData() || "");
    const data = JSON.parse(params.get("data") || "null");
    const general = JSON.parse(params.get("general") || "null");
    const dirtyFields = JSON.parse(params.get("dirtyFields") || "null");
    const dataKeys = data && typeof data === "object" ? Object.keys(data) : [];
    const descriptionData = data?.productDescriptions?.data;
    const descriptionKeys = descriptionData && typeof descriptionData === "object" ? Object.keys(descriptionData) : [];
    const valid = params.get("id") === String(objectId)
      && Number(general?.id) === objectId
      && JSON.stringify(dataKeys) === JSON.stringify(["productDescriptions"])
      && data?.productDescriptions?.type === "productDescriptions"
      && JSON.stringify(descriptionKeys) === JSON.stringify(["longMarketingDescription"])
      && descriptionData.longMarketingDescription === expectedSaveHtml
      && JSON.stringify(dirtyFields) === JSON.stringify(["productDescriptions"]);
    if (!valid) {
      blockedPosts.push({ method, url, postData: String(request.postData() || "").slice(0, 100_000), reason: "save_guard_failed" });
      return route.abort("blockedbyclient");
    }
    allowedWrites.push({
      method,
      url,
      objectId,
      dirtyFields,
      dataKeys,
      descriptionKeys,
      descriptionLength: expectedSaveHtml.length,
    });
    return route.continue();
  }
  blockedPosts.push({ method, url, postData: String(request.postData() || "").slice(0, 100_000) });
  return route.abort("blockedbyclient");
});

const page = context.pages()[0] || await context.newPage();
await page.goto("https://dostawca.tim.pl/pimcore/", { waitUntil: "domcontentloaded", timeout: 45_000 });
let frame = page.frames().find((item) => item.url().includes("/pimcore/admin/"));
for (let attempt = 0; !frame && attempt < 15; attempt += 1) {
  await page.waitForTimeout(1_000);
  frame = page.frames().find((item) => item.url().includes("/pimcore/admin/"));
}
if (!frame) throw new Error("Nie znaleziono ramki PIMCORE.");
await page.waitForTimeout(7_000);
await frame.evaluate((id) => window.pimcore.helpers.openObject(id, "object"), objectId);
await page.waitForTimeout(7_000);

const lockedDialog = /Inna osoba używa tego elementu/i.test(await frame.locator("body").innerText().catch(() => ""));
if (lockedDialog) throw new Error("Karta jest używana przez inną osobę; nie wymuszono otwarcia.");

const readCriticalSnapshot = async () => frame.evaluate(async (id) => {
  const response = await fetch(`/pimcore/admin/object/get?id=${id}`, { credentials: "same-origin" });
  if (!response.ok) throw new Error(`Nie udało się odczytać karty ${id}: HTTP ${response.status}`);
  const object = await response.json();
  const data = object.data || {};
  const pick = (value) => value == null ? value : JSON.parse(JSON.stringify(value));
  return {
    general: {
      id: object.general?.id,
      key: object.general?.key,
      className: object.general?.className,
      fullpath: object.general?.fullpath,
      published: object.general?.published,
      locked: object.general?.locked,
      modificationDate: object.general?.modificationDate,
      versionDate: object.general?.versionDate,
      versionCount: object.general?.versionCount,
      userModification: object.general?.userModification,
    },
    fields: {
      timIndex: pick(data.timIndex),
      timName: pick(data.timName),
      supplier: pick(data.supplier),
      manufacturer: pick(data.manufacturer),
      manufacturerIndex: pick(data.manufacturerIndex),
      ean: pick(data.ean),
      listPrice: pick(data.listPrice),
      netCatalogPrice: pick(data.netCatalogPrice),
      stockLevel: pick(data.stockLevel),
      measureUnit: pick(data.measureUnit),
      availability: pick(data.availability),
      status: pick(data.status),
      state: pick(data.state),
      sale: pick(data.sale),
      productAvailableForSale: pick(data.productAvailableForSale),
      mainPhoto: pick(data.mainPhoto),
      assignedCategory24: pick(data.assignedCategory24),
    },
    descriptionBlock: pick(data.productDescriptions),
    workflowManagement: pick(object.workflowManagement),
  };
}, objectId);

const beforeSnapshot = (dryRunSave || applySave) ? await readCriticalSnapshot() : null;
if (beforeSnapshot) {
  const liveEan = String(beforeSnapshot.fields?.ean ?? "");
  const liveManufacturerIndex = String(beforeSnapshot.fields?.manufacturerIndex ?? "");
  const liveState = String(beforeSnapshot.fields?.state ?? "");
  if (liveEan !== String(pilot.ean)
    || liveManufacturerIndex !== String(pilot.manufacturerCode)
    || liveState !== "active"
    || beforeSnapshot.general?.published !== true) {
    throw new Error(`Karta ${objectId} nie przeszła kontroli EAN, kodu producenta, aktywnego stanu i publikacji.`);
  }
}

if (openActionsMenu) {
  const actionsButton = frame.getByText("Akcje", { exact: true }).last();
  if (await actionsButton.isVisible().catch(() => false)) {
    await actionsButton.click();
    await page.waitForTimeout(1_000);
  }
}

const pimTab = frame.getByText(targetTab, { exact: true }).last();
if (await pimTab.isVisible().catch(() => false)) {
  await pimTab.click();
  await page.waitForTimeout(3_000);
}

const domFields = await frame.locator("textarea, input, [contenteditable='true'], iframe").evaluateAll((nodes) => nodes.map((node) => ({
  tag: node.tagName,
  id: node.id || "",
  name: node.getAttribute("name") || "",
  type: node.getAttribute("type") || "",
  title: node.getAttribute("title") || "",
  ariaLabel: node.getAttribute("aria-label") || "",
  dataRef: node.getAttribute("data-ref") || "",
  className: node.className || "",
  value: "value" in node ? String(node.value || "").slice(0, 2_000) : String(node.textContent || "").slice(0, 2_000),
})).filter((item) => /opis|desc|marketing|productdescription/i.test(`${item.id} ${item.name} ${item.title} ${item.ariaLabel} ${item.className} ${item.value}`)));

const extFields = await frame.evaluate(() => {
  const ext = window.Ext;
  if (!ext?.ComponentQuery) return [];
  return ext.ComponentQuery.query("*").map((component) => {
    const label = component.fieldLabel || component.title || component.text || "";
    const name = component.name || component.dataIndex || component.itemId || "";
    const id = component.id || "";
    const xtype = component.xtype || component.getXType?.() || "";
    const combined = `${label} ${name} ${id} ${xtype}`;
    if (!/opis|desc|marketing|productdescription/i.test(combined)) return null;
    let value = "";
    try {
      const current = component.getValue?.();
      value = typeof current === "string" ? current.slice(0, 5_000) : JSON.stringify(current ?? "").slice(0, 5_000);
    } catch {}
    return { label, name, id, xtype, value, disabled: Boolean(component.disabled), readOnly: Boolean(component.readOnly) };
  }).filter(Boolean);
});

const workflowComponents = await frame.evaluate(() => {
  const ext = window.Ext;
  if (!ext?.ComponentQuery) return [];
  return ext.ComponentQuery.query("*").map((component) => {
    const text = component.text || component.fieldLabel || component.title || component.tooltip || "";
    if (!/zmień|wnioskuj|akcje|zapisz/i.test(String(text))) return null;
    let handler = "";
    try { handler = String(component.handler || "").slice(0, 5_000); } catch {}
    return {
      text: String(text),
      id: component.id || "",
      itemId: component.itemId || "",
      xtype: component.xtype || component.getXType?.() || "",
      disabled: Boolean(component.disabled),
      hidden: Boolean(component.hidden),
      handler,
    };
  }).filter(Boolean);
});

const objectEditorInspection = await frame.evaluate((id) => {
  const gm = window.pimcore?.globalmanager;
  const candidates = [`object_${id}`, `object_${id}_object`, `object_${id}_product`];
  const summarize = (value, depth = 0) => {
    if (value == null) return value;
    if (typeof value !== "object" && typeof value !== "function") return String(value).slice(0, 2_000);
    const keys = Object.keys(value).slice(0, 300);
    const summary = {
      constructor: String(value?.constructor?.name || ""),
      keys,
      prototypeNames: Object.getOwnPropertyNames(Object.getPrototypeOf(value) || {}).slice(0, 300),
    };
    if (depth < 1) {
      for (const key of keys.filter((item) => /data|edit|layout|field|object|panel|tab/i.test(item)).slice(0, 40)) {
        try { summary[key] = summarize(value[key], depth + 1); } catch {}
      }
    }
    return summary;
  };
  const found = {};
  for (const key of candidates) {
    try {
      const value = gm?.get?.(key);
      if (value) found[key] = summarize(value);
    } catch {}
  }
  const wysiwygClass = window.pimcore?.object?.tags?.wysiwyg;
  return {
    globalManager: summarize(gm),
    found,
    wysiwygClassType: typeof wysiwygClass,
    wysiwygPrototypeKeys: wysiwygClass?.prototype ? Object.getOwnPropertyNames(wysiwygClass.prototype) : [],
    wysiwygMethods: wysiwygClass?.prototype ? Object.fromEntries(Object.getOwnPropertyNames(wysiwygClass.prototype).filter((key) => typeof wysiwygClass.prototype[key] === "function").map((key) => [key, String(wysiwygClass.prototype[key]).slice(0, 10_000)])) : {},
  };
}, objectId);

const objectScopedInspection = await frame.evaluate((id) => {
  const object = window.pimcore?.globalmanager?.get?.(`object_${id}`);
  const itemSummary = (component) => ({
    id: component?.id || "",
    title: String(component?.title || component?.text || ""),
    xtype: component?.xtype || component?.getXType?.() || "",
    hidden: Boolean(component?.hidden),
    disabled: Boolean(component?.disabled),
  });
  const fieldRecords = [];
  const seen = new WeakSet();
  const walk = (value, path, depth) => {
    if (!value || typeof value !== "object" || seen.has(value) || depth > 6) return;
    seen.add(value);
    let name = "";
    let currentValue = "";
    try { name = String(value.getName?.() || value.fieldConfig?.name || ""); } catch {}
    try { currentValue = String(value.getValue?.() || "").slice(0, 5_000); } catch {}
    if (/productDescriptions|longMarketingDescription|opis/i.test(`${path} ${name} ${value.fieldConfig?.title || ""}`)) {
      fieldRecords.push({
        path,
        constructor: String(value.constructor?.name || ""),
        keys: Object.keys(value).slice(0, 200),
        prototypeNames: Object.getOwnPropertyNames(Object.getPrototypeOf(value) || {}).slice(0, 200),
        name,
        editableDivId: value.editableDivId || "",
        title: String(value.fieldConfig?.title || ""),
        currentValue,
      });
    }
    for (const [key, child] of Object.entries(value)) {
      if (child && typeof child === "object" && !/component|layout|toolbar|object|store|owner/i.test(key)) {
        walk(child, path ? `${path}.${key}` : key, depth + 1);
      }
    }
  };
  walk(object?.edit?.dataFields, "dataFields", 0);
  return {
    dataFieldTopKeys: Object.keys(object?.edit?.dataFields || {}),
    fieldRecords,
    toolbarButtonKeys: Object.keys(object?.toolbarButtons || {}),
    toolbarButtons: Object.entries(object?.toolbarButtons || {}).map(([key, value]) => ({ key, ...itemSummary(value) })),
    tabPanelItems: (object?.tabPanel?.items?.items || []).map(itemSummary),
    mainTab: itemSummary(object?.tab),
  };
}, objectId);

const descriptionPanel = await frame.evaluate(() => {
  const ext = window.Ext;
  if (!ext?.ComponentQuery) return null;
  const panel = ext.ComponentQuery.query("*").find((component) => component.title === "Opis marketingowy długi");
  if (!panel) return null;
  const serialize = (component) => {
    let value = "";
    try {
      const current = component.getValue?.();
      value = typeof current === "string" ? current.slice(0, 10_000) : JSON.stringify(current ?? "").slice(0, 10_000);
    } catch {}
    return {
      id: String(component.id || ""),
      itemId: String(component.itemId || ""),
      name: String(component.name || ""),
      title: String(component.title || ""),
      fieldLabel: String(component.fieldLabel || ""),
      xtype: String(component.xtype || component.getXType?.() || ""),
      value,
      disabled: Boolean(component.disabled),
      readOnly: Boolean(component.readOnly),
    };
  };
  const descendants = panel.query?.("*") || [];
  const root = panel.el?.dom || null;
  const dom = root ? [...root.querySelectorAll("textarea, input, [contenteditable='true'], iframe")].map((node) => ({
    tag: node.tagName,
    id: node.id || "",
    name: node.getAttribute("name") || "",
    className: String(node.className || ""),
    src: node.getAttribute("src") || "",
    value: "value" in node ? String(node.value || "").slice(0, 10_000) : String(node.textContent || "").slice(0, 10_000),
  })) : [];
  return {
    panel: serialize(panel),
    descendants: descendants.map(serialize),
    dom,
    html: String(root?.innerHTML || "").slice(0, 30_000),
    quill: (() => {
      const editor = root?.querySelector(".ql-editor[contenteditable='true']") || null;
      const container = editor?.parentElement || null;
      let instance = null;
      try { instance = window.Quill?.find?.(container) || container?.__quill || window.Quill?.find?.(editor) || null; } catch {}
      return {
        globalType: typeof window.Quill,
        findType: typeof window.Quill?.find,
        editorFound: Boolean(editor),
        containerId: container?.id || "",
        containerKeys: container ? Object.keys(container).filter((key) => /quill/i.test(key)) : [],
        instanceFound: Boolean(instance),
        instanceConstructor: String(instance?.constructor?.name || ""),
        clipboardType: typeof instance?.clipboard?.dangerouslyPasteHTML,
        moduleClipboardType: typeof instance?.getModule?.("clipboard")?.dangerouslyPasteHTML,
        currentHtml: String(editor?.innerHTML || "").slice(0, 20_000),
      };
    })(),
  };
});

let dryRunResult = null;
if (dryRunSave || applySave) {
  dryRunResult = await frame.evaluate(({ expectedId, html }) => {
    const ext = window.Ext;
    const panel = ext?.ComponentQuery?.query("*")?.find((component) => component.title === "Opis marketingowy długi");
    const root = panel?.el?.dom || null;
    const editor = root?.querySelector(".ql-editor[contenteditable='true']") || null;
    if (!editor) throw new Error("Nie znaleziono edytora długiego opisu.");
    const container = editor.parentElement;
    let quill = null;
    try { quill = window.Quill?.find?.(container) || container?.__quill || window.Quill?.find?.(editor) || null; } catch {}
    const beforeHtml = editor.innerHTML;
    const clipboard = quill?.clipboard || quill?.getModule?.("clipboard") || null;
    if (clipboard?.dangerouslyPasteHTML) {
      clipboard.dangerouslyPasteHTML(html, "user");
    } else {
      editor.innerHTML = html;
      editor.dispatchEvent(new InputEvent("input", { bubbles: true, inputType: "insertText" }));
      editor.dispatchEvent(new Event("change", { bubbles: true }));
    }
    const semanticHtml = String(quill?.getSemanticHTML?.() || editor.innerHTML);
    document.dispatchEvent(new CustomEvent(window.pimcore.events.changeWysiwyg, {
      detail: { e: { target: container }, data: semanticHtml },
    }));
    return {
      expectedId,
      beforeHtml,
      afterHtml: editor.innerHTML,
      usedQuill: Boolean(quill),
      quillText: String(quill?.getText?.() || "").slice(0, 20_000),
      quillSemanticHtml: semanticHtml.slice(0, 50_000),
      quillContents: quill?.getContents?.() || null,
    };
  }, { expectedId: objectId, html: pilot.descriptionHtml });
  expectedSaveHtml = dryRunResult.quillSemanticHtml;
  await page.waitForTimeout(1_000);
  const saveButtonId = await frame.evaluate(() => {
    const button = window.Ext?.ComponentQuery?.query("splitbutton")?.find((component) => component.text === "Zapisz" && !component.hidden);
    return button?.id || "";
  });
  if (!saveButtonId) throw new Error("Nie znaleziono komponentu Zapisz.");
  dryRunResult.saveButtonId = saveButtonId;
  const saveResponsePromise = applySave
    ? page.waitForResponse((response) => response.request().method() === "PUT" && response.url() === "https://dostawca.tim.pl/pimcore/admin/object/save?task=undefined", { timeout: 30_000 })
    : null;
  await frame.locator(`#${saveButtonId}`).click();
  let saveResponse = null;
  if (saveResponsePromise) {
    const response = await saveResponsePromise;
    saveResponse = {
      status: response.status(),
      ok: response.ok(),
      contentType: response.headers()["content-type"] || "",
      body: String(await response.text().catch(() => "")).slice(0, 100_000),
    };
  }
  await page.waitForTimeout(4_000);
  dryRunResult.blockedPostsAfterSave = blockedPosts.slice();
  dryRunResult.saveResponse = saveResponse;
}

const afterSnapshot = applySave ? await readCriticalSnapshot() : null;
const verification = applySave ? {
  descriptionMatches: afterSnapshot?.descriptionBlock?.data?.longMarketingDescription === expectedSaveHtml,
  protectedFieldsUnchanged: JSON.stringify(afterSnapshot?.fields) === JSON.stringify(beforeSnapshot?.fields),
  identityUnchanged: ["id", "key", "className", "fullpath", "published"].every((key) => JSON.stringify(afterSnapshot?.general?.[key]) === JSON.stringify(beforeSnapshot?.general?.[key])),
  workflowUnchanged: JSON.stringify(afterSnapshot?.workflowManagement) === JSON.stringify(beforeSnapshot?.workflowManagement),
  beforeVersionCount: beforeSnapshot?.general?.versionCount,
  afterVersionCount: afterSnapshot?.general?.versionCount,
} : null;

const bodyText = await frame.locator("body").innerText().catch(() => "");
await page.screenshot({ path: screenshotPath, fullPage: true }).catch(() => {});
const report = {
  generatedAt: new Date().toISOString(),
  objectId,
  finalUrl: page.url(),
  lockedDialog,
  allowedPosts,
  allowedWrites,
  blockedPosts,
  bodyText: bodyText.slice(0, 100_000),
  domFields,
  extFields,
  workflowComponents,
  objectEditorInspection,
  objectScopedInspection,
  descriptionPanel,
  dryRunSave,
  applySave,
  pilotStage,
  pilotIdentity: pilot ? {
    ean: pilot.ean,
    manufacturerCode: pilot.manufacturerCode,
    name: pilot.name,
    timIndex: pilot.timIndex,
  } : null,
  dryRunResult,
  beforeSnapshot,
  afterSnapshot,
  verification,
  screenshotPath,
};
await writeFile(outputPath, `${JSON.stringify(report, null, 2)}\n`, "utf8");
await context.close();
console.log(`PIMCORE ${objectId}: pola DOM ${domFields.length}; komponenty Ext ${extFields.length}; blokada cudzej sesji: ${lockedDialog ? "tak" : "nie"}.`);
console.log(`Raport: ${outputPath}`);
