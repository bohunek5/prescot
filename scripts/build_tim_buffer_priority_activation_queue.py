#!/usr/bin/env python3
"""Build the activation queue for the three fully completed Prescot buffer cards."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path("/Users/karolbohdanowicz/my-ai-agents/prescot")
BUFFER_PATH = ROOT / "exports/tim/remediation/buffer-current-live-readonly-after-klus-activations-2026-09-01.json"
AUDIT_PATH = ROOT / "exports/tim/remediation/current-buffer-offer-audit-2026-09-01.json"
EPREL_QUEUE_PATH = ROOT / "exports/tim/remediation/buffer-eprel-priority-family3-queue-2026-09-01.json"
EPREL_VERIFY_PATH = ROOT / "exports/tim/remediation/buffer-eprel-priority-family3-final-postverify-2026-09-01.json"
OUTPUT_PATH = ROOT / "exports/tim/remediation/buffer-priority3-activation-queue-2026-09-01.json"

buffer = json.loads(BUFFER_PATH.read_text(encoding="utf-8"))
buffer_by_id = {int(row["id"]): row for row in buffer["items"]}
audit = json.loads(AUDIT_PATH.read_text(encoding="utf-8"))
audit_by_id = {int(row["id"]): row for row in audit["items"]}
eprel_queue = json.loads(EPREL_QUEUE_PATH.read_text(encoding="utf-8"))
verify = json.loads(EPREL_VERIFY_PATH.read_text(encoding="utf-8"))
verified_ids = {int(row["expected"]["pimcoreId"]) for row in verify["products"] if row.get("verified")}

items = []
rejected = []
for row in eprel_queue["items"]:
    object_id = int(row["pimcoreId"])
    product = buffer_by_id.get(object_id)
    audit_row = audit_by_id.get(object_id)
    guards = {
        "verifiedEprel": object_id in verified_ids,
        "liveEvidence": bool(product),
        "identity": bool(product) and str(product.get("ean") or "") == row["ean"] and str(product.get("model") or "") == row["manufacturerCode"],
        "state": bool(product) and product.get("state") == "new" and product.get("status") == "new" and product.get("published") is True,
        "description": bool(product) and product.get("descriptionHasModel") is True and product.get("descriptionHasEan") is False,
        "catalogCard": bool(product) and len(product.get("dataSheet") or []) == 1,
        "certification": bool(product) and len(product.get("certifications") or []) == 1,
        "price": float(row["timListPrice"]) == float(row["xmlPrice"]),
        "positiveStock": float(row["xmlStock"]) > 0,
        "noActiveDuplicate": bool(audit_row) and not audit_row.get("activeDuplicates"),
    }
    if not all(guards.values()):
        rejected.append({"id": object_id, "model": row["manufacturerCode"], "reason": "guard_failed", "guards": guards})
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
        "matchType": row["matchType"],
        "confidence": row["confidence"],
    })

report = {
    "generatedAt": datetime.now(timezone.utc).isoformat(),
    "rules": [
        "verified complete EPREL set",
        "exact EAN and trade model in TIM and XML",
        "positive XML stock and identical TIM/XML net price",
        "catalog card and certification already attached",
        "no active duplicate",
        "no writes to price, EAN, name, stock or description",
    ],
    "counts": {"items": len(items), "rejected": len(rejected)},
    "items": items,
    "rejected": rejected,
}
OUTPUT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"output": str(OUTPUT_PATH), "counts": report["counts"]}, ensure_ascii=False, indent=2))
