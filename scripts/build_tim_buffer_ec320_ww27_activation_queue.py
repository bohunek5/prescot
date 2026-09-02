#!/usr/bin/env python3
"""Build the activation queue for completed EC320 WW27 50 m buffer card."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path("/Users/karolbohdanowicz/my-ai-agents/prescot")
DATA = ROOT / "exports/tim/remediation"
SOURCE_PATH = DATA / "buffer-eprel-ec320-ww27-family1-queue-2026-09-01.json"
EPREL_VERIFY_PATH = DATA / "buffer-eprel-ec320-ww27-family1-final-postverify-2026-09-01.json"
DOCUMENT_VERIFY_PATH = DATA / "buffer-ec320-ww27-family1-documents-final-postverify-2026-09-01.json"
OUTPUT_PATH = DATA / "buffer-ec320-ww27-family1-activation-queue-2026-09-01.json"

source = json.loads(SOURCE_PATH.read_text(encoding="utf-8"))
eprel_verify = json.loads(EPREL_VERIFY_PATH.read_text(encoding="utf-8"))
document_verify = json.loads(DOCUMENT_VERIFY_PATH.read_text(encoding="utf-8"))
eprel_ids = {int(row["expected"]["pimcoreId"]) for row in eprel_verify["products"] if row.get("verified")}
document_ids = {int(row["id"]) for row in document_verify["products"] if row.get("verified")}

items = []
rejected = []
for row in source["items"]:
    object_id = int(row["pimcoreId"])
    guards = {
        "verifiedEprel": object_id in eprel_ids,
        "verifiedDocuments": object_id in document_ids,
        "price": float(row["timListPrice"]) == float(row["xmlPrice"]),
        "positiveStock": float(row["xmlStock"]) > 0,
    }
    if not all(guards.values()):
        rejected.append({"id": object_id, "model": row["manufacturerCode"], "guards": guards})
        continue
    items.append({
        "id": object_id,
        "ean": row["ean"],
        "model": row["manufacturerCode"],
        "price": float(row["xmlPrice"]),
        "xmlStock": float(row["xmlStock"]),
        "requiredRelations": ["certifications", "dataSheet", "energyClassLabels", "energyTechnicalCards"],
        "eprelId": row["eprelId"],
        "eprelModel": row["eprelModel"],
        "energyClass": row["energyClass"],
        "matchType": row["matchType"],
        "confidence": row["confidence"],
    })

report = {
    "generatedAt": datetime.now(timezone.utc).isoformat(),
    "counts": {"items": len(items), "rejected": len(rejected)},
    "items": items,
    "rejected": rejected,
}
OUTPUT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"output": str(OUTPUT_PATH), "counts": report["counts"]}, ensure_ascii=False, indent=2))
