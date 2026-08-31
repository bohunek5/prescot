import { readFile, writeFile } from "node:fs/promises";
import { resolve } from "node:path";
import { chromium } from "../../radlight/node_modules/playwright/index.mjs";

function argumentValue(name, fallback = "") {
  const index = process.argv.indexOf(name);
  return index === -1 ? fallback : process.argv[index + 1] || fallback;
}

const profileDir = argumentValue("--profile-dir");
if (!profileDir) throw new Error("Podaj --profile-dir z izolowaną kopią profilu Chrome.");

const outputPath = resolve(argumentValue("--output", "/tmp/tim-live-readonly-audit.json"));
const screenshotPath = resolve(argumentValue("--screenshot", "/tmp/tim-live-readonly-audit.png"));
const targetUrl = argumentValue("--url", "https://dostawca.tim.pl/");
const pimcoreGetPath = argumentValue("--pimcore-get", "");
const pageGetPath = argumentValue("--page-get", "");
const captureResourcePattern = argumentValue("--capture-resource-pattern", "");
const pimcoreIntrospect = process.argv.includes("--pimcore-introspect");
const pimcoreFulltextSearch = argumentValue("--pimcore-fulltext-search", "");
const pimcoreFulltextSearchFile = argumentValue("--pimcore-fulltext-search-file", "");
const pimcoreFulltextSearchStage = argumentValue("--pimcore-fulltext-search-stage", "");
let pimcoreFulltextTerms = pimcoreFulltextSearch.split(",").map((value) => value.trim()).filter(Boolean);
if (pimcoreFulltextSearchFile) {
  const document = JSON.parse(await readFile(resolve(pimcoreFulltextSearchFile), "utf8"));
  const source = pimcoreFulltextSearchStage ? document?.stages?.[pimcoreFulltextSearchStage] : document;
  if (pimcoreFulltextSearchStage && !Array.isArray(source)) {
    throw new Error(`Nie znaleziono etapu ${pimcoreFulltextSearchStage} w pliku wyszukiwania.`);
  }
  const discovered = [];
  const visit = (value) => {
    if (!value || typeof value !== "object") return;
    if (typeof value.ean === "string" && value.ean.trim()) discovered.push(value.ean.trim());
    if (Array.isArray(value)) value.forEach(visit);
    else Object.values(value).forEach(visit);
  };
  visit(source);
  pimcoreFulltextTerms.push(...discovered);
}
pimcoreFulltextTerms = [...new Set(pimcoreFulltextTerms)];
const pimcoreOpenId = argumentValue("--pimcore-open-id", "");
const confirmPimcoreOpen = process.argv.includes("--confirm-pimcore-open");
const allowPimcoreWorkflowLookup = process.argv.includes("--allow-pimcore-workflow-lookup");
const pimcoreObjectIds = argumentValue("--pimcore-object-ids", "")
  .split(",")
  .map((value) => Number(value.trim()))
  .filter((value) => Number.isFinite(value) && value > 0);
const pimcoreTreeNode = Number(argumentValue("--pimcore-tree-node", ""));
const pimcoreTreeView = argumentValue("--pimcore-tree-view", "");
const pimcoreTreePageSize = Math.min(500, Math.max(30, Number(argumentValue("--pimcore-tree-page-size", "250")) || 250));
const pimcoreGridParentId = Number(argumentValue("--pimcore-grid-parent-id", ""));
const pimcoreGridPageSize = Math.min(500, Math.max(10, Number(argumentValue("--pimcore-grid-page-size", "250")) || 250));
const pimcoreGridManufacturerMfgid = argumentValue("--pimcore-grid-manufacturer-mfgid", "00060865");
const pimcoreGridMaxPages = Math.max(0, Number(argumentValue("--pimcore-grid-max-pages", "0")) || 0);

const blockedRequests = [];
const allowedSessionRequests = [];
const networkRequests = [];
const failedResponses = [];
const sessionPostAllowlist = new Set([
  "https://dostawca.tim.pl/pimcore/api/authenticate-user-by-token",
  "https://dostawca.tim.pl/pimcore/api/verify-session",
]);
const context = await chromium.launchPersistentContext(profileDir, {
  headless: true,
  executablePath: "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
  args: ["--profile-directory=Default"],
  viewport: { width: 1600, height: 1100 },
  serviceWorkers: "block",
});

await context.route("**/*", async (route) => {
  const method = route.request().method().toUpperCase();
  const url = route.request().url();
  if (["GET", "HEAD", "OPTIONS"].includes(method)) {
    await route.continue();
    return;
  }
  if (method === "POST" && sessionPostAllowlist.has(url)) {
    allowedSessionRequests.push({ method, url });
    await route.continue();
    return;
  }
  if (method === "POST" && allowPimcoreWorkflowLookup && /^https:\/\/dostawca\.tim\.pl\/admin\/workflow\/actions\/\d+$/.test(url)) {
    allowedSessionRequests.push({ method, url });
    await route.continue();
    return;
  }
  if (method === "POST" && (pimcoreFulltextTerms.length || (Number.isFinite(pimcoreGridParentId) && pimcoreGridParentId > 0))) {
    const pathname = new URL(url).pathname;
    if ([
      "/admin/bundle/advanced-object-search/admin/grid-proxy",
      "/pimcore/admin/bundle/advanced-object-search/admin/grid-proxy",
    ].includes(pathname)) {
      allowedSessionRequests.push({ method, url, purpose: "read_only_fulltext_search" });
      await route.continue();
      return;
    }
  }
  blockedRequests.push({ method, url });
  await route.abort("blockedbyclient");
});

const page = context.pages()[0] || await context.newPage();
const consoleErrors = [];
const apiResponses = [];
const capturedResources = [];
const apiResponsePromises = [];
page.on("request", (request) => {
  if (["document", "fetch", "xhr"].includes(request.resourceType())) {
    networkRequests.push({ method: request.method(), type: request.resourceType(), url: request.url() });
  }
});
page.on("response", (response) => {
  if (response.status() >= 400) {
    failedResponses.push({ status: response.status(), url: response.url() });
  }
  if (response.request().method() === "GET" && response.url().includes("/api/product_import")) {
    apiResponsePromises.push(response.text().then((body) => {
      apiResponses.push({
        status: response.status(),
        url: response.url(),
        body: body.slice(0, 2_000_000),
      });
    }).catch(() => {}));
  }
  if (captureResourcePattern && response.request().method() === "GET" && response.url().includes(captureResourcePattern)) {
    apiResponsePromises.push(response.text().then((body) => {
      capturedResources.push({
        status: response.status(),
        url: response.url(),
        contentType: response.headers()["content-type"] || "",
        body: body.slice(0, 10_000_000),
      });
    }).catch(() => {}));
  }
});
page.on("console", (message) => {
  if (message.type() === "error") consoleErrors.push(message.text());
});
page.on("pageerror", (error) => consoleErrors.push(error.message));

let navigationError = "";
try {
  await page.goto(targetUrl, { waitUntil: "domcontentloaded", timeout: 45_000 });
  await page.waitForTimeout(3_000);
  const necessaryCookies = page.getByRole("button", { name: /KORZYSTAJ WYŁĄCZNIE Z NIEZBĘDNYCH PLIKÓW COOKIE/i });
  if (await necessaryCookies.isVisible().catch(() => false)) {
    await necessaryCookies.click();
    await page.waitForTimeout(4_000);
  }
} catch (error) {
  navigationError = error.message;
}
await Promise.allSettled(apiResponsePromises);

const pageSummaries = [];
for (const openPage of context.pages()) {
  pageSummaries.push({
    url: openPage.url(),
    title: await openPage.title().catch(() => ""),
    bodyText: await openPage.locator("body").innerText().catch(() => "").then((value) => value.slice(0, 30_000)),
  });
}

const frameSummaries = [];
for (const frame of page.frames()) {
  frameSummaries.push({
    url: frame.url(),
    bodyText: await frame.locator("body").innerText().catch(() => "").then((value) => value.slice(0, 30_000)),
  });
}

let pimcoreSearch = null;
if (pimcoreFulltextTerms.length) {
  let pimcoreFrame = page.frames().find((frame) => frame.url().includes("/pimcore/admin/"));
  for (let attempt = 0; !pimcoreFrame && attempt < 10; attempt += 1) {
    await page.waitForTimeout(1_000);
    pimcoreFrame = page.frames().find((frame) => frame.url().includes("/pimcore/admin/"));
  }
  if (!pimcoreFrame) throw new Error("Nie znaleziono aktywnej ramki PIMCORE.");
  pimcoreSearch = await pimcoreFrame.evaluate(async (terms) => {
    const fields = ["id", "ean", "manufacturerIndex", "suppliersProductId", "timIndex", "timName", "status", "state"];
    const searchOne = async (term) => {
      const filter = {
        classId: 3,
        conditions: {
          fulltextSearchTerm: term,
          filters: [{
            fieldname: "o_published",
            fieldLabel: "opublikowano",
            filterEntryData: true,
            operator: "must",
            ignoreInheritance: "",
          }],
        },
      };
      const result = await new Promise((resolvePromise) => {
        window.Ext.Ajax.request({
          url: "/admin/bundle/advanced-object-search/admin/grid-proxy?classId=3&xaction=read",
          method: "POST",
          headers: { "X-Pimcore-CSRF-Token": window.pimcore.settings.csrfToken },
          params: {
            class: "product",
            language: "pl",
            filter: JSON.stringify(filter),
            page: 1,
            start: 0,
            limit: 100,
            "fields[]": fields,
          },
          success: (response) => resolvePromise({ status: response.status, responseText: response.responseText }),
          failure: (response) => resolvePromise({ status: response.status, responseText: response.responseText || "" }),
        });
      });
      let payload = null;
      try { payload = JSON.parse(result.responseText); } catch {}
      return {
        term,
        status: result.status,
        success: Boolean(payload?.success),
        total: Number(payload?.total || 0),
        records: (payload?.data || []).map((record) => ({
          id: record.id || record.o_id || null,
          published: Boolean(record.o_published),
          ean: record.ean || "",
          manufacturerIndex: record.manufacturerIndex || "",
          suppliersProductId: record.suppliersProductId || "",
          timIndex: record.timIndex || "",
          timName: record.timName || record.ecommerceName || record.key || "",
          manufacturerMfgid: record.manufacturerMfgid || "",
          manufacturer: record.manufacturer || "",
          category: record.category || "",
          categoryB24: record.categoryB24 || "",
          sizeCategory: record.sizeCategory || "",
          measureUnit: record.measureUnit || "",
          status: record.status?.value || record.status || "",
          state: record.state?.value || record.state || "",
          stock: record.stockLevel?.stockTotalQuantityMz ?? null,
          price: record.netCatalogPrice?.value ?? null,
          productAvailableForSale: record.productAvailableForSale || "",
        })),
        responseText: payload ? "" : result.responseText.slice(0, 20_000),
      };
    };
    const results = [];
    for (let index = 0; index < terms.length; index += 4) {
      results.push(...await Promise.all(terms.slice(index, index + 4).map(searchOne)));
    }
    return results;
  }, pimcoreFulltextTerms);
}

let pimcoreGet = null;
if (pimcoreGetPath) {
  let pimcoreFrame = page.frames().find((frame) => frame.url().includes("/pimcore/admin/"));
  for (let attempt = 0; !pimcoreFrame && attempt < 10; attempt += 1) {
    await page.waitForTimeout(1_000);
    pimcoreFrame = page.frames().find((frame) => frame.url().includes("/pimcore/admin/"));
  }
  if (!pimcoreFrame) throw new Error("Nie znaleziono aktywnej ramki PIMCORE.");
  pimcoreGet = await pimcoreFrame.evaluate(async (path) => {
    const response = await fetch(path, { method: "GET", credentials: "same-origin" });
    return {
      path,
      status: response.status,
      contentType: response.headers.get("content-type") || "",
      body: (await response.text()).slice(0, 2_000_000),
    };
  }, pimcoreGetPath);
}

let pimcoreObjects = [];
if (pimcoreObjectIds.length) {
  let pimcoreFrame = page.frames().find((frame) => frame.url().includes("/pimcore/admin/"));
  for (let attempt = 0; !pimcoreFrame && attempt < 10; attempt += 1) {
    await page.waitForTimeout(1_000);
    pimcoreFrame = page.frames().find((frame) => frame.url().includes("/pimcore/admin/"));
  }
  if (!pimcoreFrame) throw new Error("Nie znaleziono aktywnej ramki PIMCORE.");
  pimcoreObjects = await pimcoreFrame.evaluate(async (ids) => {
    const fields = [
      "ean", "manufacturer", "manufacturerMfgid", "manufacturerName", "manufacturerIndex", "suppliersProductId", "timIndex", "timName",
      "netCatalogPrice", "prize", "vatRate", "stockLevel", "availability", "measureUnit", "status", "state",
      "productAvailableForSale", "onePhotoAdded", "assignedCategory24", "category", "categoryB24", "sizeCategory",
      "crmId", "averageDeliveryTime", "deliveryTime", "timeSupplierRealization",
      "energyClass", "energyClassLabels", "energyTechnicalCards", "instructions", "dataSheet",
      "productDescriptions",
    ];
    const results = [];
    for (const id of ids) {
      const response = await fetch(`/pimcore/admin/object/get?id=${id}`, { method: "GET", credentials: "same-origin" });
      let payload = null;
      try { payload = JSON.parse(await response.text()); } catch {}
      const data = {};
      for (const field of fields) data[field] = payload?.data?.[field] ?? null;
      results.push({
        id,
        status: response.status,
        general: {
          key: payload?.general?.key || "",
          fullpath: payload?.general?.fullpath || "",
          locked: Boolean(payload?.general?.locked),
          published: Boolean(payload?.general?.published),
          versionCount: payload?.general?.versionCount ?? null,
        },
        data,
      });
    }
    return results;
  }, pimcoreObjectIds);
}

let pimcoreGrid = null;
if (Number.isFinite(pimcoreGridParentId) && pimcoreGridParentId > 0) {
  let pimcoreFrame = page.frames().find((frame) => frame.url().includes("/pimcore/admin/"));
  for (let attempt = 0; !pimcoreFrame && attempt < 10; attempt += 1) {
    await page.waitForTimeout(1_000);
    pimcoreFrame = page.frames().find((frame) => frame.url().includes("/pimcore/admin/"));
  }
  if (!pimcoreFrame) throw new Error("Nie znaleziono aktywnej ramki PIMCORE.");
  pimcoreGrid = await pimcoreFrame.evaluate(async ({ parentId, pageSize, manufacturerMfgid, maxPages }) => {
    const fields = [
      "id", "ean", "manufacturerIndex", "suppliersProductId", "timIndex", "timName", "status", "state",
      "stockLevel", "productAvailableForSale", "productDescriptions",
    ];
    const readPage = async (pageNumber) => {
      const filter = {
        classId: 3,
        conditions: {
          filters: [
            { fieldname: "manufacturerMfgid", fieldLabel: "ID producenta", filterEntryData: manufacturerMfgid, operator: "must", ignoreInheritance: "" },
            { fieldname: "o_published", fieldLabel: "opublikowano", filterEntryData: true, operator: "must", ignoreInheritance: "" },
          ],
        },
      };
      const result = await new Promise((resolvePromise) => {
        window.Ext.Ajax.request({
          url: "/admin/bundle/advanced-object-search/admin/grid-proxy?classId=3&xaction=read",
          method: "POST",
          headers: { "X-Pimcore-CSRF-Token": window.pimcore.settings.csrfToken },
          params: {
            class: "product",
            language: "pl",
            filter: JSON.stringify(filter),
            page: pageNumber,
            start: (pageNumber - 1) * pageSize,
            limit: pageSize,
            sort: JSON.stringify([{ property: "id", direction: "ASC" }]),
            "fields[]": fields,
          },
          success: (response) => resolvePromise({ status: response.status, responseText: response.responseText }),
          failure: (response) => resolvePromise({ status: response.status, responseText: response.responseText || "" }),
        });
      });
      let payload = null;
      try { payload = JSON.parse(result.responseText); } catch {}
      return { pageNumber, status: result.status, payload, responseText: payload ? "" : result.responseText.slice(0, 20_000) };
    };
    const first = await readPage(1);
    const total = Number(first.payload?.total || 0);
    const availablePages = Math.max(1, Math.ceil(total / pageSize));
    const pages = maxPages > 0 ? Math.min(maxPages, availablePages) : availablePages;
    const results = [first];
    for (let pageNumber = 2; pageNumber <= pages; pageNumber += 1) {
      let pageResult = await readPage(pageNumber);
      for (let retry = 1; retry <= 2 && (pageResult.status !== 200 || !Array.isArray(pageResult.payload?.data)); retry += 1) {
        await new Promise((resolveWait) => setTimeout(resolveWait, retry * 1_000));
        pageResult = await readPage(pageNumber);
      }
      results.push(pageResult);
    }
    return {
      parentId,
      pageSize,
      total,
      availablePages,
      pages,
      pageStatuses: results.map((item) => ({ page: item.pageNumber, status: item.status, count: item.payload?.data?.length || 0 })),
      failedPages: results.filter((item) => item.status !== 200 || !Array.isArray(item.payload?.data))
        .map((item) => ({ page: item.pageNumber, status: item.status, responseText: item.responseText })),
      records: results.flatMap((item) => item.payload?.data || []),
    };
  }, {
    parentId: pimcoreGridParentId,
    pageSize: pimcoreGridPageSize,
    manufacturerMfgid: pimcoreGridManufacturerMfgid,
    maxPages: pimcoreGridMaxPages,
  });
}

let pimcoreRuntime = null;
if (pimcoreIntrospect) {
  let pimcoreFrame = page.frames().find((frame) => frame.url().includes("/pimcore/admin/"));
  for (let attempt = 0; !pimcoreFrame && attempt < 10; attempt += 1) {
    await page.waitForTimeout(1_000);
    pimcoreFrame = page.frames().find((frame) => frame.url().includes("/pimcore/admin/"));
  }
  if (!pimcoreFrame) throw new Error("Nie znaleziono aktywnej ramki PIMCORE.");
  pimcoreRuntime = await pimcoreFrame.evaluate(() => {
    const details = (component) => ({
      xtype: component?.xtype || component?.getXType?.() || "",
      id: component?.id || "",
      itemId: component?.itemId || "",
      name: component?.name || "",
      text: component?.text || "",
      title: component?.title || "",
      tooltip: component?.tooltip || component?.getTooltip?.() || "",
      emptyText: component?.emptyText || "",
      value: component?.getValue?.() ?? null,
      hidden: Boolean(component?.hidden),
      disabled: Boolean(component?.disabled),
    });
    const globalStore = window.pimcore?.globalmanager?.store || window.pimcore?.globalmanager?.items || {};
    const searchRegistry = window.pimcore?.globalmanager?.get?.("searchImplementationRegistry");
    const searchRegistryValue = searchRegistry?.getRegistry?.() || null;
    const objectTypesStore = window.pimcore?.globalmanager?.get?.("object_types_store");
    const matchingFunctionSources = [];
    const inspected = new WeakSet();
    const scanFunctions = (value, path, depth = 0) => {
      if (!value || (typeof value !== "object" && typeof value !== "function") || depth > 5 || inspected.has(value)) return;
      inspected.add(value);
      const names = new Set([
        ...Object.getOwnPropertyNames(value).slice(0, 300),
        ...Object.getOwnPropertyNames(Object.getPrototypeOf(value) || {}).slice(0, 300),
      ]);
      for (const name of names) {
        let child;
        try { child = value[name]; } catch { continue; }
        const childPath = `${path}.${name}`;
        if (typeof child === "function") {
          const source = Function.prototype.toString.call(child);
          if (/\/admin\/search|search\/find|elastic/i.test(source)) {
            matchingFunctionSources.push({ path: childPath, source: source.slice(0, 20_000) });
          }
        }
        if (depth < 5 && child && (typeof child === "object" || typeof child === "function")) scanFunctions(child, childPath, depth + 1);
        if (matchingFunctionSources.length >= 100) return;
      }
    };
    scanFunctions(window.pimcore?.toolbar, "pimcore.toolbar");
    scanFunctions(window.pimcore?.bundle, "pimcore.bundle");
    scanFunctions(window.pimcore?.helpersFunctions, "pimcore.helpersFunctions");
    const globals = Object.keys(globalStore || {}).map((key) => {
      const value = window.pimcore?.globalmanager?.get?.(key) ?? globalStore[key];
      const prototype = value && Object.getPrototypeOf(value);
      return {
        key,
        type: typeof value,
        constructor: value?.constructor?.name || "",
        ownKeys: value && typeof value === "object" ? Object.keys(value).slice(0, 100) : [],
        prototypeMethods: prototype ? Object.getOwnPropertyNames(prototype).filter((name) => typeof value?.[name] === "function").slice(0, 100) : [],
      };
    });
    return {
      pimcoreKeys: Object.keys(window.pimcore || {}),
      pimcoreSettingKeys: Object.keys(window.pimcore?.settings || {}),
      pimcoreHelperKeys: Object.keys(window.pimcore?.helpers || {}).filter((key) => /csrf|token/i.test(key)),
      globalManagerKeys: Object.keys(globalStore || {}),
      globals,
      searchRegistry: searchRegistryValue && typeof searchRegistryValue === "object"
        ? Object.fromEntries(Object.entries(searchRegistryValue).map(([key, value]) => [key, {
          type: typeof value,
          constructor: value?.constructor?.name || "",
          ownKeys: value && typeof value === "object" ? Object.keys(value).slice(0, 100) : [],
          prototypeMethods: value ? Object.getOwnPropertyNames(Object.getPrototypeOf(value) || {}).filter((name) => typeof value?.[name] === "function").slice(0, 100) : [],
        }]))
        : searchRegistryValue,
      objectRelationInlineSearchRoute: searchRegistry?.getObjectRelationInlineSearchRoute?.() || "",
      objectTypesStore: {
        type: typeof objectTypesStore,
        constructor: objectTypesStore?.constructor?.name || "",
        ownKeys: objectTypesStore && typeof objectTypesStore === "object" ? Object.keys(objectTypesStore).slice(0, 100) : [],
        isArray: Array.isArray(objectTypesStore),
        sample: Array.isArray(objectTypesStore) ? objectTypesStore.slice(0, 20) : null,
      },
      elastic: window.pimcore?.globalmanager?.get?.("elastic") || null,
      elasticIndices: window.pimcore?.globalmanager?.get?.("elastic_indices") || null,
      searchRoutes: (() => {
        const routes = window.Routing?.getRoutes?.() || window.Routing?.getInstance?.()?.getRoutes?.() || {};
        return Object.fromEntries(Object.entries(routes).filter(([name, value]) => /search/i.test(`${name} ${JSON.stringify(value)}`)));
      })(),
      matchingFunctionSources,
      elasticsearchNamespaceKeys: Object.keys(window.pimcore?.bundle?.elasticsearch || {}),
      elasticsearchSearchConfigKeys: Object.keys(window.pimcore?.bundle?.elasticsearch?.searchConfig || {}),
      elasticsearchClassMethods: (() => {
        const classes = {
          searchConfigPanel: window.pimcore?.bundle?.elasticsearch?.searchConfigPanel,
          grid: window.pimcore?.bundle?.elasticsearch?.searchConfig?.grid,
          conditionPanel: window.pimcore?.bundle?.elasticsearch?.searchConfig?.conditionPanel,
        };
        return Object.fromEntries(Object.entries(classes).map(([key, value]) => [key,
          value?.prototype ? Object.getOwnPropertyNames(value.prototype).filter((name) => typeof value.prototype[name] === "function") : [],
        ]));
      })(),
      elasticsearchMethodSources: (() => {
        const classes = {
          searchConfigPanel: window.pimcore?.bundle?.elasticsearch?.searchConfigPanel,
          resultPanel: window.pimcore?.bundle?.elasticsearch?.searchConfig?.resultPanel,
          filtersResultPanel: window.pimcore?.bundle?.elasticsearch?.searchConfig?.filtersResultPanel,
        };
        return Object.fromEntries(Object.entries(classes).map(([key, value]) => [key,
          value?.prototype ? Object.fromEntries(Object.getOwnPropertyNames(value.prototype)
            .filter((name) => typeof value.prototype[name] === "function")
            .map((name) => [name, Function.prototype.toString.call(value.prototype[name]).slice(0, 20_000)])) : {},
        ]));
      })(),
      gridHelperMethodSources: (() => {
        const value = window.pimcore?.object?.helpers?.grid;
        return value?.prototype ? Object.fromEntries(Object.getOwnPropertyNames(value.prototype)
          .filter((name) => typeof value.prototype[name] === "function" && ["initialize", "getStore"].includes(name))
          .map((name) => [name, Function.prototype.toString.call(value.prototype[name]).slice(0, 30_000)])) : {};
      })(),
      textfields: (window.Ext?.ComponentQuery?.query?.("textfield") || []).map(details),
      buttons: (window.Ext?.ComponentQuery?.query?.("button") || []).map(details),
      windows: (window.Ext?.ComponentQuery?.query?.("window") || []).map(details),
    };
  });
}

let pimcoreTree = null;
if (Number.isFinite(pimcoreTreeNode) && pimcoreTreeNode > 0) {
  let pimcoreFrame = page.frames().find((frame) => frame.url().includes("/pimcore/admin/"));
  for (let attempt = 0; !pimcoreFrame && attempt < 10; attempt += 1) {
    await page.waitForTimeout(1_000);
    pimcoreFrame = page.frames().find((frame) => frame.url().includes("/pimcore/admin/"));
  }
  if (!pimcoreFrame) throw new Error("Nie znaleziono aktywnej ramki PIMCORE.");
  pimcoreTree = await pimcoreFrame.evaluate(async ({ node, view, pageSize }) => {
    const fetchPage = async (pageNumber) => {
      const start = (pageNumber - 1) * pageSize;
      const query = new URLSearchParams({
        limit: String(pageSize),
        page: String(pageNumber),
        start: String(start),
        node: String(node),
      });
      if (view) query.set("view", view);
      const path = `/pimcore/admin/object/tree-get-children-by-id?${query}`;
      const response = await fetch(path, { method: "GET", credentials: "same-origin" });
      let payload = null;
      try { payload = JSON.parse(await response.text()); } catch {}
      return { page: pageNumber, start, status: response.status, payload };
    };

    const first = await fetchPage(1);
    const total = Number(first.payload?.total || 0);
    const pageCount = Math.max(1, Math.ceil(total / pageSize));
    const pages = [first];
    for (let next = 2; next <= pageCount; next += 3) {
      const batch = [];
      for (let pageNumber = next; pageNumber < Math.min(next + 3, pageCount + 1); pageNumber += 1) {
        batch.push(fetchPage(pageNumber));
      }
      pages.push(...await Promise.all(batch));
    }
    const failedPages = pages.filter((item) => item.status !== 200 || !Array.isArray(item.payload?.nodes));
    return {
      node,
      view,
      pageSize,
      total,
      pageCount,
      pageStatuses: pages.map(({ page: pageNumber, start, status, payload }) => ({
        page: pageNumber,
        start,
        status,
        count: Array.isArray(payload?.nodes) ? payload.nodes.length : 0,
      })),
      failedPages: failedPages.map(({ page: pageNumber, status }) => ({ page: pageNumber, status })),
      nodes: pages.flatMap((item) => item.payload?.nodes || []),
    };
  }, { node: pimcoreTreeNode, view: pimcoreTreeView, pageSize: pimcoreTreePageSize });
}

let pimcoreOpen = null;
if (pimcoreOpenId) {
  let pimcoreFrame = page.frames().find((frame) => frame.url().includes("/pimcore/admin/"));
  for (let attempt = 0; !pimcoreFrame && attempt < 10; attempt += 1) {
    await page.waitForTimeout(1_000);
    pimcoreFrame = page.frames().find((frame) => frame.url().includes("/pimcore/admin/"));
  }
  if (!pimcoreFrame) throw new Error("Nie znaleziono aktywnej ramki PIMCORE.");
  await page.waitForTimeout(8_000);
  const readiness = await pimcoreFrame.evaluate(() => {
    const currentUser = window.pimcore?.globalmanager?.get?.("user");
    return {
      pimcore: Boolean(window.pimcore),
      helper: typeof window.pimcore?.helpers?.openObject,
      userType: typeof currentUser,
      userIsAllowed: typeof currentUser?.isAllowed,
    };
  });
  let openError = "";
  try {
    await pimcoreFrame.evaluate((id) => window.pimcore.helpers.openObject(Number(id), "object"), pimcoreOpenId);
    await page.waitForTimeout(5_000);
    if (confirmPimcoreOpen && /Inna osoba używa tego elementu/i.test(await pimcoreFrame.locator("body").innerText().catch(() => ""))) {
      await pimcoreFrame.getByText("Tak", { exact: true }).last().click();
      await page.waitForTimeout(7_000);
    }
  } catch (error) {
    openError = error.message;
  }
  pimcoreOpen = {
    id: Number(pimcoreOpenId),
    readiness,
    openError,
    bodyText: await pimcoreFrame.locator("body").innerText().catch(() => "").then((value) => value.slice(0, 80_000)),
    buttons: await pimcoreFrame.locator("button, [role=button], .x-btn").evaluateAll((nodes) => nodes.map((node) => ({
      text: (node.innerText || node.textContent || node.getAttribute("aria-label") || node.title || "").trim().replace(/\s+/g, " "),
      title: node.title || node.getAttribute("data-qtip") || "",
    })).filter((item) => item.text || item.title)),
  };
}

let pageGet = null;
if (pageGetPath) {
  pageGet = await page.evaluate(async (path) => {
    const response = await fetch(path, { method: "GET", credentials: "same-origin" });
    return {
      path,
      status: response.status,
      contentType: response.headers.get("content-type") || "",
      body: (await response.text()).slice(0, 2_000_000),
    };
  }, pageGetPath);
}

const [title, bodyText, links, buttons, headings, forms, cookieNames] = await Promise.all([
  page.title(),
  page.locator("body").innerText().catch(() => ""),
  page.locator("a").evaluateAll((nodes) => nodes.map((node) => ({
    text: (node.innerText || node.textContent || "").trim().replace(/\s+/g, " "),
    href: node.href || "",
  })).filter((item) => item.text || item.href)),
  page.locator("button, [role=button], input[type=submit]").evaluateAll((nodes) => nodes.map((node) => ({
    text: (node.innerText || node.value || node.getAttribute("aria-label") || "").trim().replace(/\s+/g, " "),
    disabled: Boolean(node.disabled || node.getAttribute("aria-disabled") === "true"),
  }))),
  page.locator("h1, h2, h3").allInnerTexts(),
  page.locator("form").evaluateAll((nodes) => nodes.map((node) => ({
    action: node.action || "",
    method: (node.method || "GET").toUpperCase(),
  }))),
  context.cookies(["https://dostawca.tim.pl/"]).then((cookies) => cookies.map((cookie) => ({
    name: cookie.name,
    domain: cookie.domain,
    expires: cookie.expires,
  }))),
]);
const resourceUrls = await page.evaluate(() => performance.getEntriesByType("resource").map((entry) => entry.name));

await page.screenshot({ path: screenshotPath, fullPage: true }).catch(() => {});

const audit = {
  generatedAt: new Date().toISOString(),
  requestedUrl: targetUrl,
  capturedResources,
  pimcoreRuntime,
  pimcoreSearch,
  finalUrl: page.url(),
  title,
  navigationError,
  authenticated: !/login|logowanie/i.test(`${page.url()} ${title} ${bodyText.slice(0, 600)}`),
  headings,
  links,
  buttons,
  forms,
  cookieNames,
  resourceUrls,
  pageSummaries,
  frameSummaries,
  pimcoreGet,
  pimcoreObjects,
  pimcoreGrid,
  pimcoreTree,
  pimcoreOpen,
  pageGet,
  bodyText: bodyText.slice(0, 30_000),
  allowedSessionRequests,
  blockedRequests,
  networkRequests,
  failedResponses,
  apiResponses,
  consoleErrors,
  screenshotPath,
};

await writeFile(outputPath, `${JSON.stringify(audit, null, 2)}\n`, "utf8");
console.log(`TIM URL: ${audit.finalUrl}`);
console.log(`Tytuł: ${audit.title}`);
console.log(`Sesja wygląda na zalogowaną: ${audit.authenticated ? "tak" : "nie"}`);
console.log(`Linki: ${links.length}; przyciski: ${buttons.length}; formularze: ${forms.length}`);
console.log(`Dopuszczone żądania sesyjne: ${allowedSessionRequests.length}`);
console.log(`Zablokowane żądania modyfikujące: ${blockedRequests.length}`);
console.log(`Raport: ${outputPath}`);

await context.close();
