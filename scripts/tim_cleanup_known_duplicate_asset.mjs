import { writeFile } from "node:fs/promises";
import { resolve } from "node:path";
import { chromium } from "../../radlight/node_modules/playwright/index.mjs";

function argumentValue(name, fallback = "") {
  const index = process.argv.indexOf(name);
  return index === -1 ? fallback : process.argv[index + 1] || fallback;
}

const profileDir = argumentValue("--profile-dir");
const outputPath = resolve(argumentValue("--output", "/tmp/tim-known-duplicate-asset-cleanup.json"));
const applyDelete = process.argv.includes("--apply");
const verifyDeleted = process.argv.includes("--verify-deleted");
if (!profileDir) throw new Error("Podaj --profile-dir.");
if (applyDelete && verifyDeleted) throw new Error("Wybierz tylko jeden tryb: --apply albo --verify-deleted.");

// This script is intentionally single-purpose. It cannot be redirected to another asset.
const target = Object.freeze({
  id: 19066757,
  parentId: 1658124,
  path: "/Import multimediow/24248/",
  filename: "PR3-GU11-SMD2835-WW_etykieta_energetyczna_1.jpg",
  checksum: "6971d8bc96f4243f000e5a002edd5b45",
  filesize: 27052,
  owner: 24248,
});
const canonical = Object.freeze({
  id: 19066756,
  path: "/Import multimediow/24248/",
  filename: "PR3-GU11-SMD2835-WW_etykieta_energetyczna.jpg",
});
const product = Object.freeze({
  id: 1295213,
  relationAssetId: 19066769,
  relationPath: "/PIM-MEDIA/Products/GLOWNA/0001/000/14/057/54/PR3-GU11-SMD2835-WW_etykieta_energetyczna.jpg",
});

const report = {
  generatedAt: new Date().toISOString(),
  mode: applyDelete ? "apply" : verifyDeleted ? "verify_deleted" : "dry_run",
  target,
  canonical,
  product,
  guards: {},
  allowedWrites: [],
  blockedWrites: [],
  deleted: false,
};
const persist = () => writeFile(outputPath, `${JSON.stringify(report, null, 2)}\n`, "utf8");

const context = await chromium.launchPersistentContext(profileDir, {
  headless: true,
  executablePath: "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
  args: ["--profile-directory=Default"],
  serviceWorkers: "block",
});

let writePhase = "";
await context.route("**/*", async (route) => {
  const request = route.request();
  const method = request.method().toUpperCase();
  if (["GET", "HEAD", "OPTIONS"].includes(method)) return route.continue();
  const requestUrl = new URL(request.url());
  const params = new URLSearchParams(request.postData() || requestUrl.searchParams);
  const exactOrigin = requestUrl.origin === "https://dostawca.tim.pl";
  const exactId = params.get("id") === String(target.id);
  const allowedRecycle = applyDelete && writePhase === "recycle"
    && exactOrigin && method === "POST" && requestUrl.pathname === "/pimcore/admin/recyclebin/add"
    && exactId && params.get("type") === "asset"
    && [...params.keys()].sort().join(",") === "id,type";
  const allowedDelete = applyDelete && writePhase === "delete"
    && exactOrigin && method === "DELETE" && requestUrl.pathname === "/pimcore/admin/asset/delete"
    && exactId && [...params.keys()].join(",") === "id";
  if (allowedRecycle || allowedDelete) {
    report.allowedWrites.push({ phase: writePhase, method, path: requestUrl.pathname, id: target.id });
    await persist();
    return route.continue();
  }
  report.blockedWrites.push({ phase: writePhase, method, url: request.url(), reason: "not_exactly_allowlisted" });
  await persist();
  return route.abort("blockedbyclient");
});

const page = context.pages()[0] || await context.newPage();
await page.goto("https://dostawca.tim.pl/pimcore/", { waitUntil: "domcontentloaded", timeout: 45_000 });
await page.waitForTimeout(2_000);
const frame = page.frames().find((item) => item.url().includes("/pimcore/admin/"));
if (!frame) throw new Error("Nie znaleziono ramki PIMCORE.");

async function readAsset(id) {
  const response = await context.request.get(`https://dostawca.tim.pl/pimcore/admin/asset/get-data-by-id?id=${id}&_=${Date.now()}`, {
    headers: { Accept: "application/json", "Cache-Control": "no-cache" },
  });
  let body = null;
  try { body = await response.json(); } catch {}
  return { status: response.status(), body };
}

function assetIdentity(asset, expected) {
  return asset.status === 200
    && Number(asset.body?.id) === expected.id
    && String(asset.body?.path || "") === expected.path
    && String(asset.body?.filename || "") === expected.filename;
}

function assetAbsent(asset) {
  return asset.status === 404
    || (asset.status === 200
      && asset.body?.success === false
      && String(asset.body?.message || "").toLowerCase().includes("doesn't exist"));
}

if (verifyDeleted) {
  const currentTarget = await readAsset(target.id);
  const currentCanonical = await readAsset(canonical.id);
  const objectResponse = await context.request.get(`https://dostawca.tim.pl/pimcore/admin/object/get?id=${product.id}&_=${Date.now()}`, {
    headers: { Accept: "application/json", "Cache-Control": "no-cache" },
  });
  const object = await objectResponse.json();
  const relation = object?.data?.energyClassLabels;
  report.guards = {
    targetAbsent: assetAbsent(currentTarget),
    canonicalExact: assetIdentity(currentCanonical, canonical)
      && String(currentCanonical.body?.customSettings?.checksum || "") === target.checksum
      && Number(currentCanonical.body?.filesize) === target.filesize,
    productRelationExact: objectResponse.status() === 200
      && Number(object?.general?.id) === product.id
      && Array.isArray(relation) && relation.length === 1
      && Number(relation[0]?.id) === product.relationAssetId
      && String(relation[0]?.path || "") === product.relationPath,
  };
  report.postVerification = { ...report.guards };
  report.deleted = Object.values(report.guards).every(Boolean);
  if (!report.deleted) {
    report.error = "Kontrola usunięcia duplikatu nie powiodła się.";
    process.exitCode = 1;
  }
  await persist();
  await context.close();
  console.log(JSON.stringify({ deleted: report.deleted, guards: report.guards, error: report.error || "" }));
  console.log(outputPath);
  process.exit(process.exitCode || 0);
}

try {
  const beforeTarget = await readAsset(target.id);
  const beforeCanonical = await readAsset(canonical.id);
  const objectResponse = await context.request.get(`https://dostawca.tim.pl/pimcore/admin/object/get?id=${product.id}&_=${Date.now()}`, {
    headers: { Accept: "application/json", "Cache-Control": "no-cache" },
  });
  const object = await objectResponse.json();
  const relation = object?.data?.energyClassLabels;
  const deleteInfoResponse = await context.request.get(`https://dostawca.tim.pl/pimcore/admin/asset/delete-info?id=${target.id}&type=asset`, {
    headers: { Accept: "application/json", "Cache-Control": "no-cache" },
  });
  const deleteInfo = await deleteInfoResponse.json();

  report.guards = {
    targetExact: assetIdentity(beforeTarget, target)
      && Number(beforeTarget.body?.parentId) === target.parentId
      && String(beforeTarget.body?.customSettings?.checksum || "") === target.checksum
      && Number(beforeTarget.body?.filesize) === target.filesize
      && Number(beforeTarget.body?.userOwner) === target.owner
      && beforeTarget.body?.locked === false
      && Number(beforeTarget.body?.userPermissions?.delete) === 1,
    canonicalExact: assetIdentity(beforeCanonical, canonical)
      && String(beforeCanonical.body?.customSettings?.checksum || "") === target.checksum
      && Number(beforeCanonical.body?.filesize) === target.filesize,
    productRelationExact: objectResponse.status() === 200
      && Number(object?.general?.id) === product.id
      && Array.isArray(relation) && relation.length === 1
      && Number(relation[0]?.id) === product.relationAssetId
      && String(relation[0]?.path || "") === product.relationPath,
    targetNotRelated: !JSON.stringify(object?.data || {}).includes(`\"id\":${target.id}`),
    deletionExactAndDependencyFree: deleteInfoResponse.status() === 200
      && deleteInfo?.errors === false
      && deleteInfo?.hasDependencies === false
      && Number(deleteInfo?.children) === 0
      && Array.isArray(deleteInfo?.itemResults) && deleteInfo.itemResults.length === 1
      && Number(deleteInfo.itemResults[0]?.id) === target.id
      && deleteInfo.itemResults[0]?.allowed === true,
  };
  await persist();
  if (!Object.values(report.guards).every(Boolean)) throw new Error("Ścisłe warunki usunięcia duplikatu nie są spełnione.");

  if (applyDelete) {
    writePhase = "recycle";
    const recycle = await frame.evaluate(async ({ type, id }) => {
      const body = new URLSearchParams({ type, id: String(id) });
      const response = await fetch("/pimcore/admin/recyclebin/add", {
        method: "POST",
        credentials: "same-origin",
        headers: {
          "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
          "X-Pimcore-CSRF-Token": window.pimcore.settings.csrfToken,
        },
        body,
      });
      return { status: response.status, text: await response.text() };
    }, { type: "asset", id: target.id });
    writePhase = "";
    report.recycleResponse = { status: recycle.status, text: recycle.text.slice(0, 1_000) };
    if (recycle.status !== 200) throw new Error(`Nie udało się dodać duplikatu do kosza: HTTP ${recycle.status}.`);

    writePhase = "delete";
    const deletion = await frame.evaluate(async (id) => {
      const body = new URLSearchParams({ id: String(id) });
      const response = await fetch("/pimcore/admin/asset/delete", {
        method: "DELETE",
        credentials: "same-origin",
        headers: {
          "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
          "X-Pimcore-CSRF-Token": window.pimcore.settings.csrfToken,
        },
        body,
      });
      return { status: response.status, text: await response.text() };
    }, target.id);
    writePhase = "";
    report.deleteResponse = { status: deletion.status, text: deletion.text.slice(0, 1_000) };
    let deletionPayload = null;
    try { deletionPayload = JSON.parse(deletion.text); } catch {}
    if (deletion.status !== 200 || deletionPayload?.success !== true) {
      throw new Error(`Usunięcie duplikatu nie zostało potwierdzone: HTTP ${deletion.status}.`);
    }
  }

  const afterTarget = await readAsset(target.id);
  const afterCanonical = await readAsset(canonical.id);
  const afterObjectResponse = await context.request.get(`https://dostawca.tim.pl/pimcore/admin/object/get?id=${product.id}&_=${Date.now()}`, {
    headers: { Accept: "application/json", "Cache-Control": "no-cache" },
  });
  const afterObject = await afterObjectResponse.json();
  const afterRelation = afterObject?.data?.energyClassLabels;
  report.postVerification = {
    targetAbsent: applyDelete ? assetAbsent(afterTarget) : assetIdentity(afterTarget, target),
    canonicalUnchanged: assetIdentity(afterCanonical, canonical)
      && String(afterCanonical.body?.customSettings?.checksum || "") === target.checksum,
    productRelationUnchanged: afterObjectResponse.status() === 200
      && Array.isArray(afterRelation) && afterRelation.length === 1
      && Number(afterRelation[0]?.id) === product.relationAssetId
      && String(afterRelation[0]?.path || "") === product.relationPath,
  };
  report.deleted = applyDelete && Object.values(report.postVerification).every(Boolean);
  if (!Object.values(report.postVerification).every(Boolean)) throw new Error("Kontrola po operacji nie powiodła się.");
} catch (error) {
  report.error = error.message;
  process.exitCode = 1;
} finally {
  writePhase = "";
  await persist();
  await context.close();
}

console.log(JSON.stringify({ deleted: report.deleted, guards: report.guards, postVerification: report.postVerification, error: report.error || "" }));
console.log(outputPath);
