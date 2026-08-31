import { readFile, writeFile } from "node:fs/promises";
import { basename, resolve } from "node:path";

const BASE_V3 = resolve("exports/tim/remediation/full-description-queue-v3.json");
const BASE_V4 = resolve("exports/tim/remediation/full-description-queue-v4.json");
const DELTA_V4 = resolve("exports/tim/remediation/description-delta-queue.json");
const SUPPLEMENTAL = resolve("exports/tim/remediation/supplemental-description-queue-v4.json");

const reportGroups = {
  basePositive: [
    "/tmp/tim-description-v3-pilot1.json",
    "/tmp/tim-description-v3-pilot10.json",
    "/tmp/tim-description-v3-positive-010-476.json",
    "/tmp/tim-description-v3-positive-137-476-retry.json",
    "/tmp/tim-description-v3-positive-477-943.json",
    "/tmp/tim-description-v3-positive-944-1410.json",
  ],
  baseZero: [
    "/tmp/tim-description-v3-zero-pilot1.json",
    "/tmp/tim-description-v3-zero-pilot10.json",
    "/tmp/tim-description-v3-zero-010-254.json",
    "/tmp/tim-description-v3-zero-041-254-retry.json",
    "/tmp/tim-description-v3-zero-085-254-retry2.json",
    "/tmp/tim-description-v3-zero-255-498.json",
    "/tmp/tim-description-v3-zero-286-498-retry.json",
    "/tmp/tim-description-v3-zero-499-742.json",
  ],
  deltaPositive: ["/tmp/tim-description-v4-delta-positive-final.json"],
  deltaZero: ["/tmp/tim-description-v4-delta-zero-final.json"],
  supplementalPositive: [
    "/tmp/tim-description-supp-positive-pilot1.json",
    "/tmp/tim-description-supp-positive-pilot10.json",
    "/tmp/tim-description-supp-positive-rest34.json",
  ],
  supplementalZero: [
    "/tmp/tim-description-supp-zero-pilot1.json",
    "/tmp/tim-description-supp-zero-pilot10.json",
    "/tmp/tim-description-supp-zero-rest46.json",
  ],
  bufferNew: [
    "/tmp/tim-description-buffer-new-pilot1.json",
    "/tmp/tim-description-buffer-new-pilot10.json",
    "/tmp/tim-description-buffer-new-rest64.json",
  ],
  bufferApproval: [
    "/tmp/tim-description-buffer-approval-pilot1.json",
    "/tmp/tim-description-buffer-approval-pilot10.json",
    "/tmp/tim-description-buffer-approval-rest9.json",
  ],
};

async function json(path) {
  return JSON.parse(await readFile(path, "utf8"));
}

function accepted(result) {
  if (result?.status === "already_current") return true;
  return ["saved", "saved_with_validation"].includes(result?.status)
    && result.protectedFieldsUnchanged === true
    && result.identityUnchanged === true
    && result.workflowUnchanged === true;
}

async function evidenceMap(paths) {
  const map = new Map();
  for (const path of paths) {
    const report = await json(path);
    for (const result of report.results || []) {
      map.set(Number(result.objectId), { ...result, evidenceFile: basename(path) });
    }
  }
  return map;
}

function byId(rows) {
  return new Map((rows || []).map((row) => [Number(row.pimcoreId), row]));
}

function verification(queuePath, stageName, rows, primaryEvidence, overrideEvidence = new Map(), overrideIds = new Set()) {
  const results = rows.map((expected, index) => {
    const objectId = Number(expected.pimcoreId);
    const evidence = overrideIds.has(objectId) ? overrideEvidence.get(objectId) : primaryEvidence.get(objectId);
    const ok = accepted(evidence);
    return {
      index,
      objectId,
      ean: String(expected.ean || ""),
      manufacturerCode: String(expected.manufacturerCode || ""),
      name: String(expected.name || ""),
      timIndex: evidence?.timIndex || expected.timIndex || "",
      liveState: expected.liveState || (stageName === "bufferNewNeedsUpdate" ? "new" : stageName === "bufferApprovalNeedsUpdate" ? "new_for_approval" : "active"),
      liveStock: evidence?.liveStock ?? expected.liveStock ?? null,
      status: ok ? "verified" : "mismatch",
      descriptionLength: String(expected.descriptionHtml || "").length,
      protectedFieldsUnchanged: evidence?.protectedFieldsUnchanged ?? null,
      identityUnchanged: evidence?.identityUnchanged ?? null,
      workflowUnchanged: evidence?.workflowUnchanged ?? null,
      verificationMode: "immediate_post_save_live_readback",
      evidenceFile: evidence?.evidenceFile || "",
      evidenceStatus: evidence?.status || "missing",
      reason: ok ? "" : evidence?.reason || "missing_accepted_post_save_evidence",
    };
  });
  return {
    generatedAt: new Date().toISOString(),
    mode: "compiled_immediate_post_save_live_readback",
    queuePath,
    stageName,
    counts: {
      total: results.length,
      verified: results.filter((row) => row.status === "verified").length,
      mismatch: results.filter((row) => row.status === "mismatch").length,
      failed: 0,
      locked: 0,
    },
    results,
  };
}

const [baseV3, baseV4, deltaV4, supplemental] = await Promise.all([
  json(BASE_V3), json(BASE_V4), json(DELTA_V4), json(SUPPLEMENTAL),
]);
const maps = Object.fromEntries(await Promise.all(Object.entries(reportGroups).map(async ([key, paths]) => [key, await evidenceMap(paths)])));

for (const stage of ["activePositiveNeedsUpdate", "activeZeroNeedsUpdate"]) {
  const oldRows = byId(baseV3.stages[stage]);
  const deltaIds = new Set((deltaV4.stages[stage] || []).map((row) => Number(row.pimcoreId)));
  for (const row of baseV4.stages[stage] || []) {
    const previous = oldRows.get(Number(row.pimcoreId));
    if (!previous) throw new Error(`Brak pozycji V3 dla ${stage}/${row.pimcoreId}.`);
    if (!deltaIds.has(Number(row.pimcoreId)) && previous.descriptionHtml !== row.descriptionHtml) {
      throw new Error(`Niezarejestrowana różnica V3/V4 dla ${stage}/${row.pimcoreId}.`);
    }
  }
}

const outputs = [
  ["/tmp/tim-description-v4-positive-verification.json", verification(BASE_V4, "activePositiveNeedsUpdate", baseV4.stages.activePositiveNeedsUpdate, maps.basePositive, maps.deltaPositive, new Set((deltaV4.stages.activePositiveNeedsUpdate || []).map((row) => Number(row.pimcoreId))))],
  ["/tmp/tim-description-v4-zero-verification.json", verification(BASE_V4, "activeZeroNeedsUpdate", baseV4.stages.activeZeroNeedsUpdate, maps.baseZero, maps.deltaZero, new Set((deltaV4.stages.activeZeroNeedsUpdate || []).map((row) => Number(row.pimcoreId))))],
  ["/tmp/tim-description-supp-positive-verification.json", verification(SUPPLEMENTAL, "activePositiveNeedsUpdate", supplemental.stages.activePositiveNeedsUpdate, maps.supplementalPositive)],
  ["/tmp/tim-description-supp-zero-verification.json", verification(SUPPLEMENTAL, "activeZeroNeedsUpdate", supplemental.stages.activeZeroNeedsUpdate, maps.supplementalZero)],
  ["/tmp/tim-description-buffer-new-verification.json", verification(SUPPLEMENTAL, "bufferNewNeedsUpdate", supplemental.stages.bufferNewNeedsUpdate, maps.bufferNew)],
  ["/tmp/tim-description-buffer-approval-verification.json", verification(SUPPLEMENTAL, "bufferApprovalNeedsUpdate", supplemental.stages.bufferApprovalNeedsUpdate, maps.bufferApproval)],
];

for (const [path, report] of outputs) await writeFile(path, `${JSON.stringify(report, null, 2)}\n`, "utf8");
console.log(JSON.stringify(Object.fromEntries(outputs.map(([path, report]) => [basename(path), report.counts])), null, 2));
