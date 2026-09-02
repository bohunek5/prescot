#!/usr/bin/env python3
"""Read-only mapping of active Prescot TIM products to local datasheets, CE and EPREL."""

from __future__ import annotations

import csv
import argparse
import json
import re
import unicodedata
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path("/Users/karolbohdanowicz/my-ai-agents/prescot")
REM = ROOT / "exports/tim/remediation"

parser = argparse.ArgumentParser(description="Map active positive Prescot TIM products to local documents.")
parser.add_argument(
    "--live",
    type=Path,
    default=REM / "active-brand-offer-live-readonly-post-scharfer-2026-09-01.json",
)
parser.add_argument(
    "--output-json",
    type=Path,
    default=REM / "prescot-active-positive-local-document-mapping-audit-2026-09-02.json",
)
parser.add_argument(
    "--output-csv",
    type=Path,
    default=REM / "prescot-active-positive-local-document-mapping-audit-2026-09-02.csv",
)
args = parser.parse_args()

LIVE_PATH = args.live.resolve()
CATALOG_PATH = ROOT / "data/catalog.json"
EAN_INDEX_PATH = REM / "local-document-ean-index-2026-09-01.json"
EPREL_PATH = ROOT / "data/eprel-candidates.json"
EPREL_ALIAS_PATH = ROOT / "data/eprel-model-aliases.json"
DOC_ROOT = Path("/Users/karolbohdanowicz/Desktop/_PRESCOT/_2026/TIM.PL/TIM - karty ce")
SECOND_CARD_ROOT = Path("/Users/karolbohdanowicz/Desktop/_PRESCOT/_2026/TIM.PL/Karty katalogowe")
EPREL_QR_ROOT = Path("/Users/karolbohdanowicz/Desktop/_PRESCOT/_2026/TIM.PL/Eprel QR")
OUTPUT_JSON = args.output_json.resolve()
OUTPUT_CSV = args.output_csv.resolve()


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def fold(value: str) -> str:
    text = unicodedata.normalize("NFKD", str(value or ""))
    return "".join(ch for ch in text if not unicodedata.combining(ch)).upper()


def compact(value: str) -> str:
    return re.sub(r"[^A-Z0-9]+", "", fold(value))


def trade_model(snapshot_model: str, catalog_product: dict | None) -> tuple[str, list[str]]:
    live = str(snapshot_model or "").strip()
    catalog_model = str((catalog_product or {}).get("manufacturerCode") or "").strip()
    conflicts: list[str] = []
    internal = bool(re.match(r"^PRE(?:-|$)", live, re.I) or "PRE-PRE" in live.upper())
    if internal:
        if catalog_model and not re.match(r"^PRE(?:-|$)", catalog_model, re.I) and "PRE-PRE" not in catalog_model.upper():
            conflicts.append("snapshot_model_internal_PRE_replaced_with_catalog_trade_index")
            return catalog_model, conflicts
        conflicts.append("no_safe_trade_model_internal_PRE_only")
        return "", conflicts
    return live or catalog_model, conflicts


def doc_field(path: Path) -> str:
    folded = fold(str(path))
    return "dataSheet" if "/KARTY KATALOGOWE/" in folded.replace("\\", "/") else "certifications"


def candidate_tokens(stem: str) -> set[str]:
    raw = fold(stem).replace("—", "-").replace("–", "-")
    raw = re.sub(r"\bKOPIA\b.*$", "", raw).strip()
    tokens = set(re.findall(r"[A-Z0-9]+(?:[-+./][A-Z0-9]+){1,}", raw))
    full = sorted((token for token in tokens if token.count("-") >= 2), key=len, reverse=True)
    if full:
        base = full[0].rsplit("-", 1)[0] + "-"
        for part in re.split(r"[,;()]", raw)[1:]:
            variant = re.sub(r"[^A-Z0-9+]", "", part)
            if 1 < len(variant) <= 16 and any(ch.isdigit() for ch in variant):
                tokens.add(base + variant)
    return tokens


def wildcard_regex(token: str) -> re.Pattern[str] | None:
    if not re.search(r"X{1,4}", token):
        return None
    parts = re.split(r"(X{1,4})", token)
    pattern = ""
    for part in parts:
        if re.fullmatch(r"X{1,4}", part or ""):
            pattern += r"[A-Z0-9+]+"
        else:
            pattern += re.escape(part)
    return re.compile("^" + pattern + "$", re.I)


def filename_score(model: str, path: Path) -> tuple[int, str]:
    model_folded = fold(model)
    model_compact = compact(model)
    stem_folded = fold(path.stem)
    stem_compact = compact(path.stem)
    if model_compact and model_compact == stem_compact:
        return 100, "exact_trade_model_filename"
    if model_compact and len(model_compact) >= 5 and model_compact in stem_compact:
        return 100, "exact_trade_model_in_filename"
    for token in candidate_tokens(path.stem):
        if compact(token) == model_compact:
            return 100, "exact_trade_model_variant_token_in_filename"
        pattern = wildcard_regex(token)
        if pattern and pattern.fullmatch(model_folded):
            return 90, f"explicit_family_wildcard_{token}"
    return 0, ""


def add_match(container: dict[int, list[dict]], product_id: int, match: dict) -> None:
    key = (match["field"], match["file"])
    current = next((row for row in container[product_id] if (row["field"], row["file"]) == key), None)
    if current is None:
        container[product_id].append(match)
    elif int(match["confidence"]) > int(current["confidence"]):
        current.update(match)


live = load(LIVE_PATH)
catalog = load(CATALOG_PATH)
catalog_by_ean = {str(row.get("ean") or ""): row for row in catalog["products"] if row.get("ean")}

active = []
for row in live["products"]:
    if row.get("expectedBrand") != "Prescot":
        continue
    if not (row.get("state") == "active" and row.get("status") == "active" and row.get("published") is True):
        continue
    if float(row.get("stock") or 0) <= 0:
        continue
    catalog_product = catalog_by_ean.get(str(row.get("ean") or ""))
    model, model_conflicts = trade_model(str(row.get("model") or ""), catalog_product)
    category_root = str((catalog_product or {}).get("categoryRoot") or "")
    is_tape = category_root == "Taśmy LED" or "TAŚMA" in fold(str(row.get("timName") or ""))
    active.append({
        **row,
        "tradeModel": model,
        "modelConflicts": model_conflicts + ([] if row.get("ean") else ["missing_ean_in_tim_snapshot"]),
        "catalogProduct": catalog_product,
        "categoryRoot": category_root,
        "category": str((catalog_product or {}).get("category") or ""),
        "isTape": is_tape,
    })

active_by_id = {int(row["id"]): row for row in active}
matches: dict[int, list[dict]] = defaultdict(list)
product_conflicts: dict[int, list[str]] = defaultdict(list)

# Reuse already-reviewed active queues. These encode exact-model and explicit-family decisions.
for queue_path in sorted(REM.glob("prescot-active*queue*.json")):
    try:
        queue = load(queue_path)
    except Exception:
        continue
    queue_confidence = queue.get("confidence")
    for item in queue.get("items") or []:
        product_id = int(item.get("id") or 0)
        if product_id not in active_by_id or not item.get("documents"):
            continue
        confidence = int(item.get("confidence") or queue_confidence or (100 if "exact" in queue_path.name else 90))
        match_type = str(item.get("matchType") or ("reviewed_exact_queue" if confidence == 100 else "reviewed_family_queue"))
        for field, spec in item["documents"].items():
            specs = spec if isinstance(spec, list) else [spec]
            for document in specs:
                source = str((document or {}).get("source") or "")
                if not source:
                    continue
                add_match(matches, product_id, {
                    "field": field,
                    "file": source,
                    "matchType": match_type,
                    "confidence": confidence,
                    "reason": f"Wcześniej zweryfikowana kolejka aktywnych produktów: {queue_path.name}",
                    "conflicts": [],
                    "source": "reviewed_active_queue",
                })

# Exact EAN evidence extracted from local PDFs.
ean_index = load(EAN_INDEX_PATH)
for product in active:
    product_id = int(product["id"])
    ean = str(product.get("ean") or "")
    model = product["tradeModel"]
    if not ean or not model:
        continue
    grouped: dict[str, list[Path]] = defaultdict(list)
    for value in ean_index.get("byEan", {}).get(ean, []):
        path = Path(value)
        if path.is_file():
            grouped[doc_field(path)].append(path)
    for field, paths in grouped.items():
        unique_paths = sorted(set(paths), key=str)
        if len(unique_paths) == 1:
            path = unique_paths[0]
            conflicts = ["source_path_named_legacy_review_document_date"] if "CE stare moze sie przydac" in str(path) else []
            add_match(matches, product_id, {
                "field": field,
                "file": str(path),
                "matchType": "exact_ean_in_pdf",
                "confidence": 100,
                "reason": f"PDF zawiera dokładny EAN {ean}; model handlowy z TIM: {model}.",
                "conflicts": conflicts,
                "source": "local_pdf_ean_index",
            })
            continue
        ranked = sorted(((filename_score(model, path), path) for path in unique_paths), key=lambda row: (-row[0][0], str(row[1])))
        best_score = ranked[0][0][0] if ranked else 0
        best = [row for row in ranked if row[0][0] == best_score and best_score >= 90]
        if len(best) == 1:
            (_, why), path = best[0]
            add_match(matches, product_id, {
                "field": field,
                "file": str(path),
                "matchType": "exact_ean_and_model_filename",
                "confidence": 100,
                "reason": f"PDF zawiera dokładny EAN {ean}, a nazwa pliku odpowiada modelowi ({why}).",
                "conflicts": [],
                "source": "local_pdf_ean_index",
            })
        elif unique_paths:
            product_conflicts[product_id].append(f"ambiguous_{field}_same_ean_{len(unique_paths)}_local_pdfs")

# Conservative filename mapping for datasheets not covered by exact EAN.
card_paths = []
for card_root in (DOC_ROOT / "Karty katalogowe", SECOND_CARD_ROOT):
    if card_root.is_dir():
        card_paths.extend(card_root.rglob("*.pdf"))
card_paths = sorted(set(path for path in card_paths if path.is_file()), key=str)

for product in active:
    product_id = int(product["id"])
    model = product["tradeModel"]
    if not model:
        continue
    if any(row["field"] == "dataSheet" and int(row["confidence"]) == 100 for row in matches[product_id]):
        continue
    candidates = []
    for path in card_paths:
        score, reason = filename_score(model, path)
        if score >= 80:
            candidates.append((score, reason, path))
    if not candidates:
        continue
    candidates.sort(key=lambda row: (-row[0], 0 if "TIM - karty ce" in str(row[2]) else 1, str(row[2])))
    best_score = candidates[0][0]
    best = [row for row in candidates if row[0] == best_score]
    distinct_stems = {compact(row[2].stem) for row in best}
    if len(distinct_stems) > 1:
        product_conflicts[product_id].append(f"ambiguous_dataSheet_filename_candidates_{len(best)}")
        continue
    score, reason, path = best[0]
    add_match(matches, product_id, {
        "field": "dataSheet",
        "file": str(path),
        "matchType": reason,
        "confidence": score,
        "reason": "Dokładny indeks handlowy w nazwie pliku." if score == 100 else "Jawny wzorzec rodziny XX w nazwie karty obejmuje wariant handlowy.",
        "conflicts": ["family_document_requires_manual_confirmation"] if score < 100 else [],
        "source": "local_datasheet_filename",
    })

# Official EPREL assignments: exact model, reviewed packaging variant, or explicit alias only.
eprel = load(EPREL_PATH)
eprel_products = eprel.get("products") or {}
aliases = (load(EPREL_ALIAS_PATH).get("aliases") or {})
local_eprel_files = []
for path in (ROOT / "tmp/pdfs").rglob("*"):
    if path.is_file() and "eprel" in fold(str(path)) and path.suffix.lower() in {".pdf", ".png", ".jpg", ".jpeg"}:
        local_eprel_files.append(path)
if EPREL_QR_ROOT.is_dir():
    local_eprel_files.extend(path for path in EPREL_QR_ROOT.rglob("*") if path.is_file() and path.suffix.lower() in {".pdf", ".png", ".jpg", ".jpeg"})

for product in active:
    product_id = int(product["id"])
    ean = str(product.get("ean") or "")
    model = product["tradeModel"]
    if not model:
        continue
    entry = eprel_products.get(f"ean:{ean}")
    alias = aliases.get(model.lower())
    chosen = None
    confidence = 0
    match_type = ""
    if entry and entry.get("status") == "verified_exact_model" and fold(entry.get("officialModelIdentifier")) == fold(model):
        chosen, confidence, match_type = entry, 100, "eprel_verified_exact_model"
    elif entry and entry.get("status") == "verified_packaging_variant":
        chosen, confidence, match_type = entry, 95, "eprel_verified_packaging_variant"
    elif alias:
        chosen = {
            "eprelId": alias.get("eprelId"),
            "officialModelIdentifier": alias.get("modelIdentifier"),
            "productInformationSheetPl": f"https://eprel.ec.europa.eu/fiches/lightsources/Fiche_{alias.get('eprelId')}_PL.pdf",
        }
        confidence, match_type = 95, "eprel_explicit_reviewed_length_alias"
    elif entry and entry.get("status") in {"review_variant_model", "blocked_model_mismatch"}:
        product_conflicts[product_id].append(f"eprel_{entry.get('status')}_official_{entry.get('officialModelIdentifier')}")
    if not chosen:
        continue
    eprel_id = str(chosen.get("eprelId") or "")
    official_url = str(chosen.get("productInformationSheetPl") or "")
    if official_url:
        add_match(matches, product_id, {
            "field": "energyTechnicalCard",
            "file": official_url,
            "matchType": match_type,
            "confidence": confidence,
            "reason": f"Oficjalne przypisanie EPREL {eprel_id}; model rejestrowy: {chosen.get('officialModelIdentifier') or model}.",
            "conflicts": [] if confidence == 100 else ["reviewed_variant_mapping_not_exact_commercial_model"],
            "source": "eprel_candidates",
            "eprelId": eprel_id,
        })
    model_key = compact(model)
    for path in sorted(set(local_eprel_files), key=str):
        name_key = compact(path.stem)
        if not ((eprel_id and eprel_id in path.stem) or (model_key and model_key in name_key)):
            continue
        field = "energyTechnicalCard" if path.suffix.lower() == ".pdf" else "energyClassLabel"
        add_match(matches, product_id, {
            "field": field,
            "file": str(path),
            "matchType": match_type + "_local_asset",
            "confidence": confidence,
            "reason": f"Lokalny plik EPREL odpowiada zatwierdzonemu przypisaniu {eprel_id}.",
            "conflicts": [] if confidence == 100 else ["reviewed_variant_mapping_not_exact_commercial_model"],
            "source": "local_eprel_asset",
            "eprelId": eprel_id,
        })

products = []
flat_exact = []
flat_fuzzy = []
flat_csv = []
for product in active:
    product_id = int(product["id"])
    rows = sorted(matches[product_id], key=lambda row: (row["field"], -int(row["confidence"]), row["file"]))
    conflicts = list(dict.fromkeys(product["modelConflicts"] + product_conflicts[product_id] + [c for row in rows for c in row.get("conflicts", [])]))
    exact = [row for row in rows if int(row["confidence"]) == 100]
    fuzzy = [row for row in rows if 80 <= int(row["confidence"]) < 100]
    data_sheets = [row for row in rows if row["field"] == "dataSheet"]
    certifications = [row for row in rows if row["field"] == "certifications"]
    eprel_rows = [row for row in rows if row["field"] in {"energyClassLabel", "energyTechnicalCard"}]
    record = {
        "pimcoreId": product_id,
        "ean": str(product.get("ean") or ""),
        "modelHandlowy": product["tradeModel"],
        "timName": str(product.get("timName") or ""),
        "stock": float(product.get("stock") or 0),
        "categoryRoot": product["categoryRoot"],
        "category": product["category"],
        "isTape": bool(product["isTape"]),
        "currentDataSheetCount": int(product.get("dataSheet") or 0),
        "currentCertificationsCount": int(product.get("certifications") or 0),
        "proposedDataSheet": data_sheets[0]["file"] if data_sheets else "",
        "proposedCertifications": [row["file"] for row in certifications],
        "eprel": [{key: row.get(key) for key in ("field", "file", "eprelId", "matchType", "confidence", "reason") if row.get(key) not in (None, "")} for row in eprel_rows],
        "matches": rows,
        "mappingClass": "fuzzy_80_99" if fuzzy else ("exact_100" if exact else "unmatched"),
        "bestConfidence": max((int(row["confidence"]) for row in rows), default=0),
        "conflicts": conflicts,
    }
    products.append(record)
    base = {
        "pimcoreId": product_id,
        "ean": record["ean"],
        "modelHandlowy": record["modelHandlowy"],
        "stock": record["stock"],
        "category": record["category"],
        "isTape": record["isTape"],
        "productConflicts": conflicts,
    }
    for row in rows:
        flat = {**base, **row}
        (flat_exact if int(row["confidence"]) == 100 else flat_fuzzy).append(flat)
        flat_csv.append(flat)
    if not rows:
        flat_csv.append({**base, "field": "", "file": "", "matchType": "unmatched", "confidence": 0, "reason": "Brak bezpiecznego lokalnego lub EPREL dopasowania.", "conflicts": conflicts, "source": ""})

products.sort(key=lambda row: (not row["isTape"], -row["stock"], row["modelHandlowy"], row["pimcoreId"]))
flat_exact.sort(key=lambda row: (not row["isTape"], -row["stock"], row["modelHandlowy"], row["field"], row["file"]))
flat_fuzzy.sort(key=lambda row: (not row["isTape"], -row["stock"], row["modelHandlowy"], row["field"], row["file"]))

payload = {
    "generatedAt": datetime.now(timezone.utc).isoformat(),
    "readOnly": True,
    "rules": {
        "scope": "TIM Prescot active+published products with stock > 0",
        "tradeModelOnly": True,
        "internalPreIdentifiersRejected": True,
        "exact": "confidence 100: exact EAN, exact trade model, or official EPREL exact model",
        "fuzzy": "confidence 80-99: explicit XX family, previously reviewed family mapping, packaging/length alias",
        "noTimWrites": True,
    },
    "sources": {
        "liveSnapshot": str(LIVE_PATH),
        "liveSnapshotGeneratedAt": live.get("generatedAt"),
        "catalog": str(CATALOG_PATH),
        "localDocumentEanIndex": str(EAN_INDEX_PATH),
        "documentRoot": str(DOC_ROOT),
        "secondCardRoot": str(SECOND_CARD_ROOT),
        "eprelCandidates": str(EPREL_PATH),
        "eprelAliases": str(EPREL_ALIAS_PATH),
    },
    "counts": {
        "activePositiveProducts": len(products),
        "activePositiveTapes": sum(row["isTape"] for row in products),
        "productsWithAnyMapping": sum(bool(row["matches"]) for row in products),
        "productsUnmatched": sum(not row["matches"] for row in products),
        "productsWithExactMapping": sum(any(int(match["confidence"]) == 100 for match in row["matches"]) for row in products),
        "productsWithFuzzyMapping": sum(row["mappingClass"] == "fuzzy_80_99" for row in products),
        "tapesWithAnyMapping": sum(row["isTape"] and bool(row["matches"]) for row in products),
        "tapesWithExactMapping": sum(row["isTape"] and any(int(match["confidence"]) == 100 for match in row["matches"]) for row in products),
        "tapesWithFuzzyMapping": sum(row["isTape"] and any(80 <= int(match["confidence"]) < 100 for match in row["matches"]) for row in products),
        "tapesUnmatched": sum(row["isTape"] and not row["matches"] for row in products),
        "exact100Matches": len(flat_exact),
        "fuzzy80to99Matches": len(flat_fuzzy),
        "dataSheetMatches": sum(row["field"] == "dataSheet" for row in flat_exact + flat_fuzzy),
        "certificationMatches": sum(row["field"] == "certifications" for row in flat_exact + flat_fuzzy),
        "eprelMatches": sum(row["field"] in {"energyClassLabel", "energyTechnicalCard"} for row in flat_exact + flat_fuzzy),
    },
    "exact100": flat_exact,
    "fuzzy80to99": flat_fuzzy,
    "products": products,
}

OUTPUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

fieldnames = [
    "pimcoreId", "ean", "modelHandlowy", "stock", "category", "isTape", "field", "file",
    "matchType", "confidence", "reason", "conflicts", "productConflicts", "source", "eprelId",
]
with OUTPUT_CSV.open("w", encoding="utf-8-sig", newline="") as handle:
    writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
    writer.writeheader()
    for row in sorted(flat_csv, key=lambda item: (not item["isTape"], -float(item["stock"]), item["modelHandlowy"], item.get("field", ""), item.get("file", ""))):
        cooked = dict(row)
        cooked["conflicts"] = " | ".join(row.get("conflicts") or [])
        cooked["productConflicts"] = " | ".join(row.get("productConflicts") or [])
        writer.writerow(cooked)

print(json.dumps({"json": str(OUTPUT_JSON), "csv": str(OUTPUT_CSV), "counts": payload["counts"]}, ensure_ascii=False, indent=2))
