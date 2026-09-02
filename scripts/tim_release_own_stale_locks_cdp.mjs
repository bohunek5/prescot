import { readFile, writeFile } from "node:fs/promises";
import { resolve } from "node:path";
import { chromium } from "../../radlight/node_modules/playwright/index.mjs";

function argumentValue(name, fallback = "") {
  const index = process.argv.indexOf(name);
  return index === -1 ? fallback : process.argv[index + 1] || fallback;
}

const cdpUrl = argumentValue("--cdp-url", "http://127.0.0.1:9222");
const queueArgument = argumentValue("--queue", "");
const auditArgument = argumentValue("--audit", "");
const queuePath = queueArgument ? resolve(queueArgument) : "";
const auditPath = auditArgument ? resolve(auditArgument) : "";
const stage = argumentValue("--stage", "activePositiveNeedsUpdate");
const outputPath = resolve(argumentValue("--output", "/tmp/tim-release-own-stale-locks-cdp.json"));
const minAgeMinutes = Math.max(1, Number(argumentValue("--min-age-minutes", "10")) || 10);
const maxUnlocks = Math.max(1, Number(argumentValue("--max-unlocks", "1")) || 1);
const concurrency = Math.max(1, Math.min(40, Number(argumentValue("--concurrency", "15")) || 15));
const apply = process.argv.includes("--apply");
if ((!queuePath && !auditPath) || (queuePath && auditPath) || !apply) {
  throw new Error("Podaj dokładnie jedno z --queue/--audit oraz --apply.");
}

let queue;
if (queuePath) {
  const queueDocument = JSON.parse(await readFile(queuePath, "utf8"));
  queue = queueDocument?.stages?.[stage] ?? queueDocument?.[stage];
  if (!Array.isArray(queue) || !queue.length) throw new Error(`Brak kolejki ${stage}.`);
} else {
  const audit = JSON.parse(await readFile(auditPath, "utf8"));
  const auditProducts = Array.isArray(audit?.products)
    ? audit.products
    : Array.isArray(audit?.items)
      ? audit.items
      : audit?.results;
  if (!Array.isArray(auditProducts) || !auditProducts.length) throw new Error("Audyt nie zawiera produktów.");
  queue = auditProducts.map((product) => ({
    pimcoreId: Number(product.id),
    ean: String(product.ean || ""),
    manufacturerCode: String(product.model || ""),
  }));
}
const selected = queue.slice(0, maxUnlocks);
const report = { generatedAt: new Date().toISOString(), apply, queuePath, auditPath, stage, minAgeMinutes, maxUnlocks, concurrency, currentUserId: 0, results: [], fatalError: "" };

let frame;
try {
  const browser = await chromium.connectOverCDP(cdpUrl);
  const context = browser.contexts()[0];
  for (const page of context.pages()) {
    frame = page.frames().find((candidate) => candidate.url() === "https://dostawca.tim.pl/pimcore/admin/");
    if (frame) break;
  }
  if (!frame) throw new Error("Brak aktywnej ramki PIMCORE.");
  const session = await frame.evaluate(() => ({
    ext: Boolean(window.Ext), csrf: Boolean(window.pimcore?.settings?.csrfToken),
    userId: Number(window.pimcore?.currentuser?.id), active: window.pimcore?.currentuser?.active === true,
  }));
  if (!session.ext || !session.csrf || !session.userId || !session.active) throw new Error("Sesja PIMCORE nie jest aktywna.");
  report.currentUserId = session.userId;

  for (let start = 0; start < selected.length; start += concurrency) {
    const batch = selected.slice(start, start + concurrency).map((product) => ({
      id: Number(product.pimcoreId ?? product.id),
      ean: String(product.ean || ""),
      model: String(product.manufacturerCode ?? product.model ?? ""),
    }));
    const batchResults = await frame.evaluate(async ({ products, currentUserId, minimumAgeMinutes }) => Promise.all(products.map(async (product) => {
      const beforeResponse = await fetch(`/pimcore/admin/object/get?id=${product.id}&_=${Date.now()}-${product.id}`, {
        credentials: "same-origin", cache: "no-store", headers: { Accept: "application/json", "Cache-Control": "no-cache" },
      });
      let payload = null; try { payload = await beforeResponse.json(); } catch {}
      const item = { ...product, beforeStatus: beforeResponse.status, unlocked: false };
      const lock = payload?.editlock;
      if (lock) {
        item.lock = { id: lock.id, cid: lock.cid, ctype: lock.ctype, userId: lock.userId, date: lock.date, user: lock.user?.name || "" };
        item.ageMinutes = Math.floor((Date.now() / 1000 - Number(lock.date)) / 60);
        if (Number(lock.cid) !== product.id || String(lock.ctype) !== "object") {
          item.reason = "invalid_lock_identity";
          return item;
        }
        if (Number(lock.userId) !== currentUserId) {
          item.reason = "foreign_lock_skipped";
          return item;
        }
        if (item.ageMinutes < minimumAgeMinutes) {
          item.reason = "own_lock_too_fresh";
          return item;
        }
      } else if (Number(payload?.general?.id) !== product.id) {
        item.reason = "object_read_unexpected";
        return item;
      } else {
        // object/get may establish a lock for the current user even when the
        // response contains the object, so release it as part of read cleanup.
        item.reason = "own_read_lock_cleanup";
      }

      const body = new URLSearchParams({ id: String(product.id), type: "object" });
      const unlockResponse = await fetch("/pimcore/admin/element/unlock-element", {
        method: "PUT", credentials: "same-origin",
        headers: {
          "X-Pimcore-CSRF-Token": window.pimcore.settings.csrfToken,
          "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        },
        body,
      });
      item.unlockResponse = { status: unlockResponse.status, body: String(await unlockResponse.text()).slice(0, 10_000) };
      item.unlocked = unlockResponse.status === 200;
      if (!item.unlocked) item.reason = `unlock_http_${unlockResponse.status}`;
      return item;
    })), { products: batch, currentUserId: session.userId, minimumAgeMinutes: minAgeMinutes });
    report.results.push(...batchResults);
    if ((start + batch.length) % 150 < concurrency || start + batch.length === selected.length) {
      console.log(`Obsłużono ${start + batch.length}/${selected.length}`);
    }
  }
} catch (error) {
  report.fatalError = error instanceof Error ? error.message : String(error);
}

await writeFile(outputPath, `${JSON.stringify(report, null, 2)}\n`, "utf8");
const counts = {
  selected: selected.length,
  unlocked: report.results.filter((item) => item.unlocked).length,
  foreignSkipped: report.results.filter((item) => item.reason === "foreign_lock_skipped").length,
  tooFresh: report.results.filter((item) => item.reason === "own_lock_too_fresh").length,
  failed: report.results.filter((item) => !item.unlocked && !["foreign_lock_skipped", "own_lock_too_fresh"].includes(item.reason)).length,
};
console.log(JSON.stringify({ currentUserId: report.currentUserId, counts, fatalError: report.fatalError }, null, 2));
if (report.fatalError) process.exitCode = 1;
process.exit(process.exitCode || 0);
