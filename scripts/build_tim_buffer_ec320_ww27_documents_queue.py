#!/usr/bin/env python3
"""Build the guarded catalog-card and CE queue for EC320 WW27 50 m."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path("/Users/karolbohdanowicz/my-ai-agents/prescot")
DATA = ROOT / "exports/tim/remediation"
BUFFER_PATH = DATA / "buffer-current-live-after-priority-activations-2026-09-01.json"
AUDIT_PATH = DATA / "current-buffer-offer-audit-after-priority-activations-2026-09-01.json"
EPREL_QUEUE_PATH = DATA / "buffer-eprel-ec320-ww27-family1-queue-2026-09-01.json"
EPREL_VERIFY_PATH = DATA / "buffer-eprel-ec320-ww27-family1-final-postverify-2026-09-01.json"
OUTPUT_PATH = DATA / "buffer-ec320-ww27-family1-documents-queue-2026-09-01.json"
CARD_PATH = Path("/Users/karolbohdanowicz/Desktop/_PRESCOT/_2026/TIM.PL/Karty katalogowe/TASMY/PREMIUM/EC320-025-8-WW27.pdf")
CE_PATH = Path("/Users/karolbohdanowicz/Desktop/_PRESCOT/_2026/TIM.PL/TIM - karty ce/Taśmy LED/Prescot Taśmy led Premium CE 2026.pdf")

buffer = json.loads(BUFFER_PATH.read_text(encoding="utf-8"))
buffer_by_id = {int(row["id"]): row for row in buffer["items"]}
audit = json.loads(AUDIT_PATH.read_text(encoding="utf-8"))
audit_by_id = {int(row["id"]): row for row in audit["items"]}
eprel_queue = json.loads(EPREL_QUEUE_PATH.read_text(encoding="utf-8"))
eprel_verify = json.loads(EPREL_VERIFY_PATH.read_text(encoding="utf-8"))
verified_ids = {int(row["expected"]["pimcoreId"]) for row in eprel_verify["products"] if row.get("verified")}

items = []
rejected = []
for source in eprel_queue["items"]:
    object_id = int(source["pimcoreId"])
    product = buffer_by_id.get(object_id)
    audit_row = audit_by_id.get(object_id)
    guards = {
        "verifiedEprel": object_id in verified_ids,
        "identity": bool(product) and product.get("ean") == source["ean"] and product.get("model") == source["manufacturerCode"],
        "state": bool(product) and product.get("state") == "new" and product.get("status") == "new" and product.get("published") is True,
        "emptyDocuments": bool(product) and not product.get("dataSheet") and not product.get("certifications"),
        "description": bool(product) and product.get("descriptionHasModel") is True and product.get("descriptionHasEan") is False,
        "files": CARD_PATH.is_file() and CE_PATH.is_file(),
        "price": float(source["timListPrice"]) == float(source["xmlPrice"]),
        "positiveStock": float(source["xmlStock"]) > 0,
        "noActiveDuplicate": bool(audit_row) and not audit_row.get("activeDuplicates"),
    }
    if not all(guards.values()):
        rejected.append({"id": object_id, "model": source["manufacturerCode"], "reason": "guard_failed", "guards": guards})
        continue
    model = source["manufacturerCode"]
    items.append({
        "id": object_id,
        "ean": source["ean"],
        "model": model,
        "state": "new",
        "timListPrice": float(source["timListPrice"]),
        "xmlPrice": float(source["xmlPrice"]),
        "xmlStock": float(source["xmlStock"]),
        "documents": {
            "dataSheet": {"source": str(CARD_PATH), "filename": f"{model}_karta_katalogowa.pdf"},
            "certifications": {"source": str(CE_PATH), "filename": "CE_Prescot_Tasmy_LED_Premium_2026.pdf"},
        },
        "cardPattern": "EC320-025-8-WW27",
        "cePattern": "EC320-025-X-XX",
        "matchType": "product_family_and_sale_length_variant",
        "confidence": 90,
    })

report = {
    "generatedAt": datetime.now(timezone.utc).isoformat(),
    "rules": [
        "verified complete EPREL set",
        "card covers exact EC320-025-8-WW27 light-source model",
        "CE explicitly covers EC320-025-X-XX",
        "50 m sale-length mapping approved by supplier",
        "exact TIM/XML EAN, trade model and net price; positive XML stock",
    ],
    "counts": {"items": len(items), "rejected": len(rejected)},
    "items": items,
    "rejected": rejected,
}
OUTPUT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"output": str(OUTPUT_PATH), "counts": report["counts"]}, ensure_ascii=False, indent=2))
