#!/usr/bin/env python3
"""Build a guarded active-KLUŚ document queue from official manufacturer pages."""

from __future__ import annotations

import json
import re
import argparse
from datetime import datetime, timezone
from pathlib import Path

from pypdf import PdfReader


ROOT = Path("/Users/karolbohdanowicz/my-ai-agents/prescot")
parser = argparse.ArgumentParser()
parser.add_argument("--map", default=str(ROOT / "exports/tim/remediation/klus-active-official-document-map-2026-09-01.json"))
parser.add_argument("--downloads", default=str(ROOT / "exports/tim/remediation/klus-active-official-document-downloads-2026-09-01.json"))
parser.add_argument("--active", default=str(ROOT / "exports/tim/remediation/active-brand-offer-live-readonly-post-scharfer-2026-09-01.json"))
parser.add_argument("--output", default=str(ROOT / "exports/tim/remediation/klus-active-official-documents-queue-2026-09-01.json"))
args = parser.parse_args()

MAP_PATH = Path(args.map).resolve()
DOWNLOAD_PATH = Path(args.downloads).resolve()
ACTIVE_PATH = Path(args.active).resolve()
OUTPUT_PATH = Path(args.output).resolve()


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def pdf_text(path: Path) -> str:
    try:
        reader = PdfReader(path)
        return "\n".join(page.extract_text() or "" for page in reader.pages).upper()
    except Exception:
        return ""


document_map = read_json(MAP_PATH)
downloads = read_json(DOWNLOAD_PATH)
active = read_json(ACTIVE_PATH)
download_by_url = {row["url"]: row for row in downloads["downloads"] if row.get("ok")}
live_by_id = {int(row["id"]): row for row in active["products"]}

text_by_source = {}
for row in download_by_url.values():
    if row["type"] == "dataSheet":
        text_by_source[row["source"]] = pdf_text(Path(row["source"]))

items = []
rejected = []
for record in document_map["records"]:
    best = record.get("best") or {}
    live = live_by_id.get(int(record["id"]))
    if not live or live.get("expectedBrand") != "KLUŚ" or not live.get("published") or live.get("state") != "active":
        rejected.append({"id": record["id"], "model": record["model"], "reason": "not_live_active_klus"})
        continue
    description = str(live.get("descriptionHtml") or "")
    if record["model"] not in description or re.search(r"\b\d{13}\b", description):
        rejected.append({"id": record["id"], "model": record["model"], "reason": "description_guard"})
        continue
    if not best.get("exactModelInPage"):
        rejected.append({"id": record["id"], "model": record["model"], "reason": "no_exact_official_product_page"})
        continue
    documents = {}
    evidence = []
    for document in best.get("documents", []):
        source_type = document.get("type")
        field = {
            "dataSheet": "dataSheet",
            "instruction": "instructions",
            "certification": "certifications",
        }.get(source_type)
        if not field or field in documents or int(live.get(field) or 0) > 0:
            continue
        downloaded = download_by_url.get(document["url"])
        if not downloaded:
            continue
        if field == "dataSheet":
            model = str(record["model"]).upper()
            family_model = re.sub(r"_[123]$", "", model)
            text = text_by_source.get(downloaded["source"], "")
            if model not in text and family_model not in text:
                evidence.append({"field": field, "url": document["url"], "accepted": False, "reason": "model_not_found_in_pdf_text"})
                continue
        documents[field] = {"source": downloaded["source"], "filename": downloaded["filename"]}
        evidence.append({
            "field": field,
            "url": document["url"],
            "officialProductUrl": best["productUrl"],
            "accepted": True,
        })
    if not documents:
        rejected.append({"id": record["id"], "model": record["model"], "reason": "no_missing_verified_documents", "evidence": evidence})
        continue
    list_price = live.get("listPrice")
    if isinstance(list_price, dict):
        list_price = list_price.get("value")
    items.append({
        "id": int(record["id"]),
        "ean": str(record["ean"]),
        "model": str(record["model"]),
        "state": "active",
        "timName": str(record["timName"]),
        "timListPrice": list_price,
        "documents": documents,
        "officialProductUrl": best["productUrl"],
        "evidence": evidence,
    })

report = {
    "generatedAt": datetime.now(timezone.utc).isoformat(),
    "sourceMap": str(MAP_PATH),
    "sourceDownloads": str(DOWNLOAD_PATH),
    "sourceActiveAudit": str(ACTIVE_PATH),
    "rules": [
        "live active published KLUŚ product",
        "description already contains the trade model and no EAN",
        "exact model result on official KLUŚ website",
        "catalog card contains the exact or explicit length-family model in PDF text",
        "only currently empty TIM document fields are queued",
    ],
    "counts": {
        "items": len(items),
        "dataSheet": sum("dataSheet" in row["documents"] for row in items),
        "instruction": sum("instructions" in row["documents"] for row in items),
        "certification": sum("certifications" in row["documents"] for row in items),
        "rejected": len(rejected),
    },
    "items": items,
    "rejected": rejected,
}
OUTPUT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"output": str(OUTPUT_PATH), "counts": report["counts"]}, ensure_ascii=False, indent=2))
