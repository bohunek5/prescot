import { mkdir, writeFile } from "node:fs/promises";
import { dirname, resolve } from "node:path";
import { chromium } from "../../radlight/node_modules/playwright/index.mjs";

const output = resolve(process.argv[2] || "exports/tim/remediation/buffer-current-live-readonly-2026-08-31.json");
const parentId = 2385468;
const browser = await chromium.connectOverCDP("http://127.0.0.1:9222");
const context = browser.contexts()[0];
let page = null;
let frame = null;
for (const candidate of context?.pages() || []) {
  for (const candidateFrame of candidate.frames().filter((item) => item.url().includes("/pimcore/admin/"))) {
    const isAuthenticated = await candidateFrame.evaluate(() => Number(window.pimcore?.currentuser?.id) > 0
      && window.pimcore?.currentuser?.active === true).catch(() => false);
    if (isAuthenticated) {
      page = candidate;
      frame = candidateFrame;
      break;
    }
  }
  if (frame) break;
}
if (!page || !frame) throw new Error("Brak zalogowanej ramki PIMCORE.");
const authenticated = await frame.evaluate(() => Number(window.pimcore?.currentuser?.id) > 0
  && window.pimcore?.currentuser?.active === true);
if (!authenticated) throw new Error("Sesja PIMCORE nie jest aktywna.");
const currentUserId = await frame.evaluate(() => Number(window.pimcore.currentuser.id));

const tree = await frame.evaluate(async (node) => {
  const query = new URLSearchParams({ node: String(node), limit: "500", page: "1", start: "0", _: String(Date.now()) });
  const response = await fetch(`/pimcore/admin/object/tree-get-children-by-id?${query}`, {
    credentials: "same-origin",
    headers: { Accept: "application/json", "Cache-Control": "no-cache" },
  });
  const payload = await response.json();
  if (response.status !== 200 || !Array.isArray(payload?.nodes)) throw new Error(`buffer_tree_read_failed:http_${response.status}`);
  return { total: Number(payload.total || 0), nodes: payload.nodes };
}, parentId);

const ids = tree.nodes.filter((node) => node.className === "product").map((node) => Number(node.id));
const items = [];
for (let start = 0; start < ids.length; start += 5) {
  const batch = ids.slice(start, start + 5);
  items.push(...await frame.evaluate(async ({ objectIds, currentUserId }) => Promise.all(objectIds.map(async (id) => {
    const unlockOwnReadLock = async () => fetch("/pimcore/admin/element/unlock-element", {
      method: "PUT",
      credentials: "same-origin",
      headers: {
        "X-Pimcore-CSRF-Token": window.pimcore.settings.csrfToken,
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
      },
      body: new URLSearchParams({ id: String(id), type: "object" }),
    });
    try {
      let response = await fetch(`/pimcore/admin/object/get?id=${id}&_=${Date.now()}-${id}`, {
        credentials: "same-origin",
        headers: { Accept: "application/json", "Cache-Control": "no-cache" },
      });
      let payload = await response.json();
      if (payload?.editlock) {
        if (Number(payload.editlock.userId) !== currentUserId) {
          return { id, http: response.status, editlock: payload.editlock, error: "foreign_lock_skipped" };
        }
        await unlockOwnReadLock();
        response = await fetch(`/pimcore/admin/object/get?id=${id}&_=${Date.now()}-${id}-retry`, {
          credentials: "same-origin",
          headers: { Accept: "application/json", "Cache-Control": "no-cache" },
        });
        payload = await response.json();
      }
      if (payload?.editlock || !payload?.general) return { id, http: response.status, error: "object_read_unavailable" };
      const data = payload?.data || {};
      const description = String(data.productDescriptions?.data?.longMarketingDescription || "");
      const stockLevel = Array.isArray(data.stockLevel) ? data.stockLevel : [];
      const row = {
        id,
        http: response.status,
        fullpath: String(payload?.general?.fullpath || ""),
        published: Boolean(payload?.general?.published),
        locked: Boolean(payload?.general?.locked),
        version: payload?.general?.versionCount ?? null,
        ean: String(data.ean || "").trim(),
        model: String(data.manufacturerIndex || "").trim(),
        supplierId: String(data.suppliersProductId || "").trim(),
        timIndex: String(data.timIndex || "").trim(),
        timName: String(data.timName || payload?.general?.key || "").trim(),
        manufacturerName: String(data.manufacturerName || "").trim(),
        manufacturerPath: String(data.manufacturer || "").trim(),
        state: data.state?.value || data.state || "",
        status: data.status?.value || data.status || "",
        available: data.productAvailableForSale?.value || data.productAvailableForSale || "",
        stockLevel,
        stock: Math.max(0, ...stockLevel.map((row) => Number(row.stockTotalQuantityMz) || 0)),
        listPrice: data.listPrice ?? null,
        netCatalogPrice: data.netCatalogPrice ?? null,
        mainPhoto: String(data.mainPhoto || ""),
        descriptionHtml: description,
        descriptionChars: description.replace(/<[^>]*>/g, " ").replace(/\s+/g, " ").trim().length,
        descriptionHasEan: /\b\d{13}\b/.test(description),
        descriptionHasModel: Boolean(data.manufacturerIndex) && description.includes(String(data.manufacturerIndex)),
        certifications: Array.isArray(data.certifications) ? data.certifications : [],
        instructions: Array.isArray(data.instructions) ? data.instructions : [],
        dataSheet: Array.isArray(data.dataSheet) ? data.dataSheet : [],
        energyClassLabels: Array.isArray(data.energyClassLabels) ? data.energyClassLabels : [],
        energyTechnicalCards: Array.isArray(data.energyTechnicalCards) ? data.energyTechnicalCards : [],
        energyClass: data.energyClass ?? null,
        category: data.category ?? null,
        categoryB24: data.categoryB24 ?? null,
      };
      const unlockResponse = await unlockOwnReadLock();
      if (unlockResponse.status !== 200) row.error = `lock_cleanup_http_${unlockResponse.status}`;
      return row;
    } catch (error) {
      return { id, http: 0, error: error.message };
    }
  })), { objectIds: batch, currentUserId }));
  if ((start + batch.length) % 50 < 5 || start + batch.length === ids.length) {
    console.log(`Odczytano ${start + batch.length}/${ids.length}`);
  }
}

function group(item) {
  const manufacturer = `${item.manufacturerName} ${item.manufacturerPath}`.toUpperCase();
  if (/KLUŚ|KLUS/.test(manufacturer)) return "KLUŚ";
  if (/SCHARFER/.test(manufacturer)) return "Scharfer";
  if (/PRESCOT/.test(manufacturer)) return "Prescot";
  return "Pozostałe";
}
function metrics(rows) {
  const by = (field) => Object.fromEntries([...new Set(rows.map((item) => String(item[field] || "")))]
    .sort().map((value) => [value || "(puste)", rows.filter((item) => String(item[field] || "") === value).length]));
  return {
    total: rows.length,
    state: by("state"),
    status: by("status"),
    positiveStock: rows.filter((item) => item.stock > 0).length,
    missingEan: rows.filter((item) => !item.ean).length,
    missingModel: rows.filter((item) => !item.model).length,
    missingPhoto: rows.filter((item) => !item.mainPhoto).length,
    missingDescription: rows.filter((item) => !item.descriptionChars).length,
    descriptionHasEan: rows.filter((item) => item.descriptionHasEan).length,
    descriptionMissingModel: rows.filter((item) => !item.descriptionHasModel).length,
    missingDataSheet: rows.filter((item) => !item.dataSheet.length).length,
    missingCertifications: rows.filter((item) => !item.certifications.length).length,
    missingInstructions: rows.filter((item) => !item.instructions.length).length,
    missingEnergyLabel: rows.filter((item) => !item.energyClassLabels.length).length,
    missingEnergyTechnicalCard: rows.filter((item) => !item.energyTechnicalCards.length).length,
  };
}

const valid = items.filter((item) => item.http === 200 && !item.error);
const groups = Object.fromEntries(["Prescot", "Scharfer", "KLUŚ", "Pozostałe"].map((name) => [
  name,
  metrics(valid.filter((item) => group(item) === name)),
]));
const report = {
  generatedAt: new Date().toISOString(),
  source: "live PIMCORE buffer tree + object/get via logged Chrome CDP",
  readOnly: true,
  releasesOwnReadLocks: true,
  parentId,
  treeTotal: tree.total,
  requested: ids.length,
  received: valid.length,
  failed: items.filter((item) => item.http !== 200 || item.error).length,
  groups,
  outOfScope: valid.filter((item) => /KAJA|LIGHT PRESTIGE/i.test(`${item.timName} ${item.manufacturerName}`))
    .map(({ id, ean, model, timName, manufacturerName }) => ({ id, ean, model, timName, manufacturerName })),
  items,
};

await mkdir(dirname(output), { recursive: true });
await writeFile(output, `${JSON.stringify(report, null, 2)}\n`, "utf8");
console.log(JSON.stringify({ treeTotal: report.treeTotal, received: report.received, failed: report.failed, groups: report.groups }, null, 2));
console.log(`Raport: ${output}`);
process.exit(0);
