#!/usr/bin/env python3
"""Build a read-only next queue for active KLUŚ documents.

This script reads local TIM audits and previously downloaded official KLUŚ PDFs.
It never connects to TIM and never writes to PIMCORE.
"""

from __future__ import annotations

import csv
import argparse
import json
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

from pypdf import PdfReader


ROOT = Path("/Users/karolbohdanowicz/my-ai-agents/prescot")
DATA = ROOT / "exports/tim/remediation"

parser = argparse.ArgumentParser(description="Build the next read-only KLUŚ document queue.")
parser.add_argument(
    "--active",
    type=Path,
    default=DATA / "active-brand-offer-live-readonly-post-scharfer-2026-09-01.json",
)
parser.add_argument(
    "--output-json",
    type=Path,
    default=DATA / "klus-active-next-documents-readonly-2026-09-02.json",
)
parser.add_argument(
    "--output-csv",
    type=Path,
    default=DATA / "klus-active-next-documents-readonly-2026-09-02.csv",
)
args = parser.parse_args()

ACTIVE_PATH = args.active.resolve()
MAP_PATH = DATA / "klus-active-official-document-map-2026-09-01.json"
DOWNLOADS_PATH = DATA / "klus-active-official-document-downloads-2026-09-01.json"
PREVIOUS_QUEUE_PATH = DATA / "klus-active-official-documents-queue-2026-09-01.json"
POSTVERIFY_PATH = DATA / "klus-active-documents-final-postverify-2026-09-01.json"
OUTPUT_JSON = args.output_json.resolve()
OUTPUT_CSV = args.output_csv.resolve()


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def compact(value: str) -> str:
    return re.sub(r"[^A-Z0-9]+", "", str(value).upper())


def model_parts(model: str) -> list[str]:
    return [part for part in re.split(r"\s*\+\s*", str(model).upper()) if part]


def part_variants(part: str) -> list[str]:
    variants = {compact(part)}
    without_length = re.sub(r"_[0-9]+(?:[.,][0-9]+)?$", "", part)
    variants.add(compact(without_length))
    prefix = re.match(r"^([ABCZ]\d{5})", part)
    if prefix:
        variants.add(compact(prefix.group(1)))
        variants.add(compact(prefix.group(1)[1:]))
    elif re.fullmatch(r"\d{3,6}", compact(part)):
        variants.add(compact(part))
    return sorted((value for value in variants if len(value) >= 3), key=len, reverse=True)


def pdf_text(path: Path) -> str:
    try:
        reader = PdfReader(str(path))
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    except Exception:
        return ""


active = read_json(ACTIVE_PATH)
document_map = read_json(MAP_PATH)
downloads = read_json(DOWNLOADS_PATH)
previous_queue = read_json(PREVIOUS_QUEUE_PATH)
postverify = read_json(POSTVERIFY_PATH)

live_by_id = {int(row["id"]): row for row in active["products"]}
map_by_id = {int(row["id"]): row for row in document_map["records"]}
download_by_url = {row["url"]: row for row in downloads["downloads"] if row.get("ok")}
previous_by_id = {int(row["id"]): row for row in previous_queue["items"]}
postverify_by_id = {int(row["id"]): row for row in postverify["products"]}

model_counts = Counter(
    str(row.get("model") or "")
    for row in active["products"]
    if row.get("expectedBrand") == "KLUŚ" and row.get("published") and row.get("state") == "active"
)

# A verified post-check proves that these previously empty fields now have relations.
verified_fields: dict[int, set[str]] = defaultdict(set)
for row in postverify["products"]:
    if not row.get("verified"):
        continue
    for field in (row.get("expectedDocuments") or {}):
        verified_fields[int(row["id"])].add(field)

text_cache: dict[str, str] = {}


def local_pdf_evidence(download: dict, model: str) -> tuple[str, list[str], list[str]]:
    source = str(download["source"])
    if source not in text_cache:
        text_cache[source] = compact(pdf_text(Path(source)))
    text = text_cache[source]
    url_text = compact(download.get("url") or "")
    matches = []
    missing_parts = []
    for part in model_parts(model):
        variants = part_variants(part)
        found = next((variant for variant in variants if variant in text), None)
        if found:
            matches.append(found)
            continue
        found_in_url = next((variant for variant in variants if variant in url_text), None)
        if found_in_url:
            matches.append(f"URL:{found_in_url}")
        else:
            missing_parts.append(part)
    if not missing_parts and matches:
        return "family_confirmed", matches, []
    if matches:
        return "partial_family", matches, missing_parts
    return "not_found", [], missing_parts


def current_missing(live: dict, product_id: int, field: str) -> bool:
    if int(live.get(field) or 0) > 0:
        return False
    return field not in verified_fields.get(product_id, set())


exact_items = []
fuzzy_items = []
rejected = []

for record in document_map["records"]:
    product_id = int(record["id"])
    live = live_by_id.get(product_id)
    if not live:
        continue
    if (
        live.get("expectedBrand") != "KLUŚ"
        or not live.get("published")
        or live.get("state") != "active"
        or float(live.get("stock") or 0) <= 0
    ):
        continue

    target_missing = {
        field
        for field in ("dataSheet", "certifications")
        if current_missing(live, product_id, field)
    }
    if not target_missing:
        continue

    best = record.get("best") or {}
    if not best:
        rejected.append({
            "pimcoreId": product_id,
            "ean": str(live.get("ean") or ""),
            "model": str(live.get("model") or ""),
            "stock": live.get("stock"),
            "reason": "no_official_product_page",
        })
        continue

    conflicts = []
    model = str(record.get("model") or live.get("model") or "")
    ean = str(record.get("ean") or live.get("ean") or "")
    if not ean:
        conflicts.append("missing_ean")
    if model_counts.get(model, 0) > 1:
        conflicts.append(f"duplicate_active_model:{model_counts[model]}")
    if "+" in model:
        conflicts.append("composite_trade_model")

    previous_result = postverify_by_id.get(product_id)
    if previous_result and not previous_result.get("verified"):
        conflicts.append("previous_document_write_not_verified")

    documents = {}
    evidence = []
    confidences = []
    for document in best.get("documents", []):
        field = {
            "dataSheet": "dataSheet",
            "certification": "certifications",
        }.get(document.get("type"))
        if field not in target_missing or field in documents:
            continue
        downloaded = download_by_url.get(document.get("url"))
        if not downloaded or not Path(downloaded.get("source") or "").is_file():
            continue

        match_type, matched_variants, missing_parts = local_pdf_evidence(downloaded, model)
        exact_page = bool(best.get("exactModelInPage"))
        family_page = bool(best.get("familyModelInPage"))

        if exact_page and match_type == "family_confirmed":
            confidence = 100
            reason = "exact model on official KLUŚ page and every model component confirmed in the official local PDF or its official URL"
        elif exact_page and match_type == "partial_family":
            confidence = 92
            reason = "exact official product page; official PDF confirms only part of the composite/family model"
        elif exact_page:
            confidence = 88 if field == "dataSheet" else 95
            reason = (
                "exact official product page and official local PDF, but the model could not be confirmed in extracted PDF text"
                if field == "dataSheet"
                else "official declaration linked from the exact KLUŚ product page; model not found in extracted declaration text"
            )
        elif family_page and match_type in {"family_confirmed", "partial_family"}:
            confidence = 85
            reason = "official KLUŚ family page and family reference confirmed in the official local PDF"
        else:
            continue

        if conflicts:
            confidence = min(confidence, 90)
        if "previous_document_write_not_verified" in conflicts:
            confidence = min(confidence, 80)

        documents[field] = {
            "officialUrl": document["url"],
            "localFile": downloaded["source"],
            "filename": downloaded["filename"],
            "sha256": downloaded.get("sha256"),
            "bytes": downloaded.get("bytes"),
            "confidence": confidence,
            "reason": reason,
            "matchType": match_type,
            "matchedVariants": matched_variants,
            "missingModelParts": missing_parts,
        }
        evidence.append({
            "field": field,
            "exactModelInOfficialPage": exact_page,
            "familyModelInOfficialPage": family_page,
            "pdfMatch": match_type,
            "confidence": confidence,
        })
        confidences.append(confidence)

    if not documents:
        rejected.append({
            "pimcoreId": product_id,
            "ean": ean,
            "model": model,
            "stock": live.get("stock"),
            "reason": "no_downloaded_official_card_or_ce_for_missing_fields",
            "missingFields": sorted(target_missing),
            "officialProductUrl": best.get("productUrl"),
        })
        continue

    item = {
        "pimcoreId": product_id,
        "ean": ean,
        "model": model,
        "name": str(live.get("timName") or record.get("timName") or ""),
        "stock": live.get("stock"),
        "state": live.get("state"),
        "officialProductUrl": best.get("productUrl"),
        "targetFields": sorted(documents),
        "documents": documents,
        "confidence": min(confidences),
        "confidenceReason": "; ".join(sorted({doc["reason"] for doc in documents.values()})),
        "conflicts": conflicts,
        "evidence": evidence,
    }
    if item["confidence"] == 100 and not conflicts:
        exact_items.append(item)
    else:
        fuzzy_items.append(item)

exact_items.sort(key=lambda row: (-float(row["stock"] or 0), row["model"], row["pimcoreId"]))
fuzzy_items.sort(key=lambda row: (-row["confidence"], -float(row["stock"] or 0), row["model"], row["pimcoreId"]))


def failed_record(product_id: int, cause: str, safe_next_step: str) -> dict:
    live = live_by_id[product_id]
    queued = previous_by_id[product_id]
    post = postverify_by_id[product_id]
    return {
        "pimcoreId": product_id,
        "ean": str(live.get("ean") or ""),
        "model": str(live.get("model") or ""),
        "name": str(live.get("timName") or ""),
        "stock": live.get("stock"),
        "price": (live.get("listPrice") or {}).get("value") if isinstance(live.get("listPrice"), dict) else live.get("listPrice"),
        "expectedDocuments": queued.get("documents"),
        "officialProductUrl": queued.get("officialProductUrl"),
        "verification": post,
        "cause": cause,
        "safeNextStep": safe_next_step,
    }


failed_355 = [
    failed_record(
        2122722,
        "PIMCORE save returned HTTP 500: another supplier product already uses manufacturer index A01888N_3 (TIM index 0001-00017-49612).",
        "Do not retry automatically. Resolve the duplicate product identity in TIM first; the official instruction and declaration files are valid local downloads.",
    ),
    failed_record(
        2122770,
        "PIMCORE save returned HTTP 422 because the active indexed product has an empty/zero TIM net price.",
        "Not eligible for the stock>0 queue (stock is 0). Restore a valid commercial price through the authorized price source before any document retry.",
    ),
    failed_record(
        10646118,
        "PIMCORE save returned HTTP 500: another supplier product already uses manufacturer index C28284C02.",
        "Do not retry automatically. Resolve the duplicate product identity first. The previous queue only contained a generic instruction, not a data sheet or CE declaration.",
    ),
]

report = {
    "generatedAt": datetime.now(timezone.utc).isoformat(),
    "readOnly": True,
    "timWrites": 0,
    "sources": {
        "activeAudit": str(ACTIVE_PATH),
        "officialMap": str(MAP_PATH),
        "officialDownloads": str(DOWNLOADS_PATH),
        "previousQueue": str(PREVIOUS_QUEUE_PATH),
        "postVerification355": str(POSTVERIFY_PATH),
    },
    "rules": [
        "active, published KLUŚ product with stock greater than zero",
        "target only an empty dataSheet or certifications field after accounting for the 352 verified previous writes",
        "official KLUŚ product page and an already downloaded official PDF are mandatory",
        "confidence 100 requires an exact official product page and full family/model confirmation in the local PDF or its official URL",
        "identity conflicts and previous failed saves are never placed in the confidence-100 queue",
        "no TIM or PIMCORE writes are performed",
    ],
    "previous355": {
        "total": postverify["counts"]["total"],
        "verified": postverify["counts"]["verified"],
        "notVerified": postverify["counts"]["failed"],
        "records": failed_355,
    },
    "counts": {
        "exact100": len(exact_items),
        "fuzzy80to99": len(fuzzy_items),
        "exact100DataSheet": sum("dataSheet" in row["targetFields"] for row in exact_items),
        "exact100Certifications": sum("certifications" in row["targetFields"] for row in exact_items),
        "fuzzyDataSheet": sum("dataSheet" in row["targetFields"] for row in fuzzy_items),
        "fuzzyCertifications": sum("certifications" in row["targetFields"] for row in fuzzy_items),
        "rejectedNoOfficialLocalDocument": len(rejected),
    },
    "exact100": exact_items,
    "fuzzy80to99": fuzzy_items,
    "rejected": rejected,
}

OUTPUT_JSON.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

with OUTPUT_CSV.open("w", encoding="utf-8-sig", newline="") as handle:
    fieldnames = [
        "bucket",
        "pimcoreId",
        "ean",
        "model",
        "name",
        "stock",
        "targetFields",
        "officialProductUrl",
        "officialDocumentUrls",
        "localFiles",
        "confidence",
        "confidenceReason",
        "conflicts",
    ]
    writer = csv.DictWriter(handle, fieldnames=fieldnames)
    writer.writeheader()
    for bucket, rows in (("exact100", exact_items), ("fuzzy80to99", fuzzy_items)):
        for row in rows:
            writer.writerow({
                "bucket": bucket,
                "pimcoreId": row["pimcoreId"],
                "ean": row["ean"],
                "model": row["model"],
                "name": row["name"],
                "stock": row["stock"],
                "targetFields": "|".join(row["targetFields"]),
                "officialProductUrl": row["officialProductUrl"],
                "officialDocumentUrls": "|".join(doc["officialUrl"] for doc in row["documents"].values()),
                "localFiles": "|".join(doc["localFile"] for doc in row["documents"].values()),
                "confidence": row["confidence"],
                "confidenceReason": row["confidenceReason"],
                "conflicts": "|".join(row["conflicts"]),
            })

print(json.dumps({
    "json": str(OUTPUT_JSON),
    "csv": str(OUTPUT_CSV),
    "counts": report["counts"],
    "failed355": len(failed_355),
}, ensure_ascii=False, indent=2))
