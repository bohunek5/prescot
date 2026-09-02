import { stat, readFile, writeFile } from "node:fs/promises";
import { basename, resolve } from "node:path";
import { chromium } from "../../radlight/node_modules/playwright/index.mjs";

function argumentValue(name, fallback = "") {
  const index = process.argv.indexOf(name);
  return index === -1 ? fallback : process.argv[index + 1] || fallback;
}

function relationEmpty(value) {
  return value == null || (Array.isArray(value) && value.length === 0);
}

const mappingPath = resolve(argumentValue(
  "--mapping",
  "prescot/exports/tim/remediation/prescot-active-positive-local-document-mapping-audit-2026-09-02.json",
));
const outputPath = resolve(argumentValue(
  "--output",
  "prescot/exports/tim/remediation/prescot-active-positive-exact100-documents-live-write-queue-2026-09-02.json",
));
const batchSize = Math.max(1, Number(argumentValue("--batch-size", "25")) || 25);
const mapping = JSON.parse(await readFile(mappingPath, "utf8"));
const matchSet = argumentValue("--match-set", "exact100");
const conflictFreeOnly = process.argv.includes("--conflict-free-only");
const exact = (Array.isArray(mapping[matchSet]) ? mapping[matchSet] : []).filter((match) => !conflictFreeOnly || (
  (!Array.isArray(match.conflicts) || match.conflicts.length === 0)
  && (!Array.isArray(match.productConflicts) || match.productConflicts.length === 0)
));
const productsById = new Map((mapping.products || []).map((product) => [Number(product.pimcoreId), product]));
const genericFields = new Set(["dataSheet", "certifications"]);
const exactById = new Map();
for (const match of exact) {
  const id = Number(match.pimcoreId);
  if (!exactById.has(id)) exactById.set(id, []);
  exactById.get(id).push(match);
}

const browser = await chromium.connectOverCDP("http://127.0.0.1:9222");
const context = browser.contexts()[0];
if (!context) throw new Error("Brak aktywnego kontekstu Chrome.");
let frame = null;
for (const page of context.pages()) {
  for (const candidate of page.frames().filter((item) => item.url().includes("/pimcore/admin/"))) {
    const authenticated = await candidate.evaluate(() => Boolean(window.pimcore?.settings?.csrfToken)).catch(() => false);
    if (authenticated) {
      frame = candidate;
      break;
    }
  }
  if (frame) break;
}
if (!frame) throw new Error("Brak istniejącej uwierzytelnionej ramki PIMCORE.");
const currentUserId = await frame.evaluate(() => Number(window.pimcore?.currentuser?.id));
if (!currentUserId) throw new Error("Brak aktywnego użytkownika PIMCORE.");

const liveById = new Map();
const readErrors = [];
const ids = [...exactById.keys()];
for (let start = 0; start < ids.length; start += batchSize) {
  const batch = ids.slice(start, start + batchSize);
  const reads = await frame.evaluate(async ({ objectIds, currentUserId }) => Promise.all(objectIds.map(async (id) => {
    const unlockOwnReadLock = async () => fetch("/pimcore/admin/element/unlock-element", {
      method: "PUT",
      credentials: "same-origin",
      headers: {
        "X-Pimcore-CSRF-Token": window.pimcore.settings.csrfToken,
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
      },
      body: new URLSearchParams({ id: String(id), type: "object" }),
    });
    for (let attempt = 0; attempt < 3; attempt += 1) {
      const controller = new AbortController();
      const timeout = setTimeout(() => controller.abort(), 12_000);
      try {
        const response = await fetch(`/pimcore/admin/object/get?id=${id}&_=${Date.now()}-${attempt}`, {
          credentials: "same-origin",
          headers: { Accept: "application/json", "Cache-Control": "no-cache" },
          signal: controller.signal,
        });
        let payload = null;
        try { payload = await response.json(); } catch {}
        if (response.status === 200 && payload?.editlock) {
          if (Number(payload.editlock.userId) !== currentUserId) {
            return { id, status: response.status, error: "foreign_lock_skipped" };
          }
          await unlockOwnReadLock();
          await new Promise((done) => setTimeout(done, 150));
          continue;
        }
        if (response.status === 200 && payload?.general) {
          const unlockResponse = await unlockOwnReadLock();
          return {
            id,
            status: response.status,
            payload,
            lockCleanupError: unlockResponse.status === 200 ? "" : `unlock_http_${unlockResponse.status}`,
          };
        }
      } catch (error) {
        if (attempt === 2) return { id, status: 0, error: String(error?.message || error) };
      } finally {
        clearTimeout(timeout);
      }
      await new Promise((done) => setTimeout(done, 400));
    }
    return { id, status: 0, error: "object_read_failed" };
  })), { objectIds: batch, currentUserId });
  for (const read of reads) {
    if (read.payload && !read.lockCleanupError) liveById.set(Number(read.id), read.payload);
    else readErrors.push({ id: Number(read.id), status: read.status, reason: read.error || read.lockCleanupError || "object_read_failed" });
  }
  console.log(JSON.stringify({ checked: Math.min(start + batch.length, ids.length), total: ids.length, readErrors: readErrors.length }));
}

const items = [];
const alreadyPresent = [];
const rejected = [];
const eprelExact = [];
for (const [id, matches] of exactById) {
  const source = productsById.get(id);
  const live = liveById.get(id);
  if (!source || !live) continue;
  const data = live.data || {};
  const description = String(data.productDescriptions?.data?.longMarketingDescription || "");
  const identityValid = Number(live.general?.id) === id
    && live.general?.published === true
    && String(data.ean || "") === String(source.ean || "")
    && String(data.manufacturerIndex || "") === String(source.modelHandlowy || "")
    && String(data.state || "") === "active"
    && String(data.status || "") === "active"
    && Boolean(String(data.timIndex || "").trim())
    && Number(source.stock) > 0
    && !live.general?.locked
    && !/\b\d{13}\b/.test(description);
  if (!identityValid) {
    rejected.push({
      id,
      ean: source.ean,
      model: source.modelHandlowy,
      reason: "live_identity_state_lock_or_description_guard_failed",
      live: {
        ean: data.ean,
        model: data.manufacturerIndex,
        state: data.state,
        status: data.status,
        published: live.general?.published,
        locked: live.general?.locked,
        timIndexPresent: Boolean(String(data.timIndex || "").trim()),
        descriptionHas13DigitNumber: /\b\d{13}\b/.test(description),
      },
    });
    continue;
  }

  const documents = {};
  for (const field of genericFields) {
    const fieldMatches = matches.filter((match) => match.field === field);
    const files = [...new Set(fieldMatches.map((match) => String(match.file || "")).filter(Boolean))];
    if (!files.length) continue;
    if (files.length !== 1) {
      rejected.push({ id, ean: source.ean, model: source.modelHandlowy, field, reason: "multiple_exact_files", files });
      continue;
    }
    if (!relationEmpty(data[field])) {
      alreadyPresent.push({ id, ean: source.ean, model: source.modelHandlowy, field, current: data[field] });
      continue;
    }
    try {
      const fileStat = await stat(files[0]);
      if (!fileStat.isFile()) throw new Error("not_file");
    } catch {
      rejected.push({ id, ean: source.ean, model: source.modelHandlowy, field, reason: "source_file_missing", file: files[0] });
      continue;
    }
    documents[field] = { source: files[0], filename: basename(files[0]) };
  }
  if (Object.keys(documents).length) {
    items.push({
      id,
      ean: String(source.ean),
      model: String(source.modelHandlowy),
      state: "active",
      timName: String(source.timName || data.timName || ""),
      xmlStock: Number(source.stock),
      requireDescriptionModel: false,
      documents,
    });
  }

  const eprelMatches = matches.filter((match) => ["energyClassLabel", "energyTechnicalCard"].includes(match.field));
  if (eprelMatches.length) {
    eprelExact.push({
      id,
      ean: String(source.ean),
      model: String(source.modelHandlowy),
      currentEnergyClass: String(data.energyClass || ""),
      currentEnergyClassLabels: data.energyClassLabels || [],
      currentEnergyTechnicalCards: data.energyTechnicalCards || [],
      matches: eprelMatches,
    });
  }
}

const report = {
  generatedAt: new Date().toISOString(),
  readOnly: true,
  mappingPath,
  matchSet,
  conflictFreeOnly,
  counts: {
    exactProducts: ids.length,
    liveRead: liveById.size,
    readErrors: readErrors.length,
    readyProducts: items.length,
    readyDocumentFields: items.reduce((sum, item) => sum + Object.keys(item.documents).length, 0),
    readyDataSheets: items.filter((item) => item.documents.dataSheet).length,
    readyCertifications: items.filter((item) => item.documents.certifications).length,
    alreadyPresentFields: alreadyPresent.length,
    rejected: rejected.length,
    eprelProductsForSeparateReview: eprelExact.length,
  },
  items,
  eprelExact,
  alreadyPresent,
  rejected,
  readErrors,
};
await writeFile(outputPath, `${JSON.stringify(report, null, 2)}\n`, "utf8");
console.log(JSON.stringify(report.counts));
await browser.close();
