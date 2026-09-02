#!/usr/bin/env python3
"""Build a guarded TIM document queue from exact official KLUŚ product pages."""

from __future__ import annotations

import json
import re
from pathlib import Path

from pypdf import PdfReader


ROOT = Path("/Users/karolbohdanowicz/my-ai-agents/prescot")
MAP_PATH = ROOT / "exports/tim/remediation/klus-official-document-map-2026-09-01.json"
DOWNLOAD_PATH = ROOT / "exports/tim/remediation/klus-official-document-downloads-2026-09-01.json"
SNAPSHOT_PATH = ROOT / "exports/tim/remediation/buffer-current-live-readonly-after-activations-2026-09-01.json"
OUTPUT_PATH = ROOT / "exports/tim/remediation/klus-buffer-official-documents-queue-2026-09-01.json"


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
snapshot = read_json(SNAPSHOT_PATH)
download_by_url = {row["url"]: row for row in downloads["downloads"] if row.get("ok")}
live_by_id = {int(row["id"]): row for row in snapshot["items"]}

text_by_source: dict[str, str] = {}
for row in download_by_url.values():
    if row["type"] == "dataSheet":
        text_by_source[row["source"]] = pdf_text(Path(row["source"]))

items = []
rejected = []
for record in document_map["records"]:
    best = record.get("best") or {}
    if not best.get("exactModelInPage"):
        rejected.append({
            "id": record["id"], "model": record["model"], "reason": "no_exact_official_product_page"
        })
        continue
    live = live_by_id[int(record["id"])]
    documents = {}
    evidence = []
    for document in best.get("documents", []):
        source_type = document.get("type")
        field = {
            "dataSheet": "dataSheet",
            "instruction": "instructions",
            "certification": "certifications",
        }.get(source_type)
        if not field or field in documents:
            continue
        downloaded = download_by_url.get(document["url"])
        if not downloaded:
            continue
        if field == "dataSheet":
            model = str(record["model"]).upper()
            family_model = re.sub(r"_[123]$", "", model)
            text = text_by_source.get(downloaded["source"], "")
            if model not in text and family_model not in text:
                evidence.append({
                    "field": field,
                    "url": document["url"],
                    "accepted": False,
                    "reason": "model_not_found_in_pdf_text",
                })
                continue
        documents[field] = {
            "source": downloaded["source"],
            "filename": downloaded["filename"],
        }
        evidence.append({
            "field": field,
            "url": document["url"],
            "officialProductUrl": best["productUrl"],
            "accepted": True,
            "reason": "exact_model_on_official_page"
            + ("_and_in_pdf" if field == "dataSheet" else "_and_linked_by_manufacturer"),
        })
    if not documents:
        rejected.append({
            "id": record["id"], "model": record["model"], "reason": "no_verified_documents",
            "evidence": evidence,
        })
        continue
    items.append({
        "id": int(record["id"]),
        "ean": str(record["ean"]),
        "model": str(record["model"]),
        "state": str(record["state"]),
        "timName": str(record["timName"]),
        "timListPrice": (
            live.get("listPrice", {}).get("value")
            if isinstance(live.get("listPrice"), dict)
            else live.get("listPrice")
        ),
        "documents": documents,
        "officialProductUrl": best["productUrl"],
        "evidence": evidence,
    })

report = {
    "generatedAt": __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat(),
    "sourceMap": str(MAP_PATH),
    "sourceDownloads": str(DOWNLOAD_PATH),
    "rules": [
        "only exact model result on the official KLUŚ website",
        "catalog card additionally contains the exact model or the explicit length-family model in PDF text",
        "instruction and declaration are linked directly by KLUŚ from that exact product page",
        "no generic corporate certificates are used as product CE",
    ],
    "counts": {
        "items": len(items),
        "new": sum(row["state"] == "new" for row in items),
        "new_for_approval": sum(row["state"] == "new_for_approval" for row in items),
        "active": sum(row["state"] == "active" for row in items),
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
