#!/usr/bin/env python3
"""Build document queue for two verified EC608 length-derived buffer cards."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path("/Users/karolbohdanowicz/my-ai-agents/prescot")
DATA = ROOT / "exports/tim/remediation"
BUFFER_PATH = DATA / "buffer-current-live-after-priority-activations-2026-09-01.json"
AUDIT_PATH = DATA / "current-buffer-offer-audit-after-priority-activations-2026-09-01.json"
EPREL_QUEUE_PATH = DATA / "buffer-eprel-next-derived3-queue-2026-09-01.json"
EPREL_VERIFY_PATH = DATA / "buffer-eprel-next-derived2-final-postverify-2026-09-01.json"
OUTPUT_PATH = DATA / "buffer-next-derived2-documents-queue-2026-09-01.json"
CE_PATH = Path("/Users/karolbohdanowicz/Desktop/_PRESCOT/_2026/TIM.PL/TIM - karty ce/Taśmy LED/Prescot Taśmy led Premium CE 2026.pdf")
CARD_608_026 = Path("/Users/karolbohdanowicz/Desktop/_PRESCOT/_2026/TIM.PL/TIM - karty ce/Karty katalogowe/Taśmy LED/PREMIUM/EC608-026-5-CCT.pdf")

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
    documents = {
        "certifications": {"source": str(CE_PATH), "filename": "CE_Prescot_Tasmy_LED_Premium_2026.pdf"},
    }
    if object_id == 10648972:
        documents["dataSheet"] = {"source": str(CARD_608_026), "filename": f"{source['manufacturerCode']}_karta_katalogowa.pdf"}
    guards = {
        "verifiedEprel": object_id in verified_ids,
        "identity": bool(product) and product.get("ean") == source["ean"] and product.get("model") == source["manufacturerCode"],
        "state": bool(product) and product.get("state") == "new" and product.get("status") == "new" and product.get("published") is True,
        "emptyTargetDocuments": bool(product) and all(not product.get(field) for field in documents),
        "description": bool(product) and product.get("descriptionHasModel") is True and product.get("descriptionHasEan") is False,
        "files": CE_PATH.is_file() and (object_id != 10648972 or CARD_608_026.is_file()),
        "price": float(source["timListPrice"]) == float(source["xmlPrice"]),
        "positiveStock": float(source["xmlStock"]) > 0,
        "noActiveDuplicate": bool(audit_row) and not audit_row.get("activeDuplicates"),
    }
    if not all(guards.values()):
        rejected.append({"id": object_id, "model": source["manufacturerCode"], "reason": "guard_failed", "guards": guards})
        continue
    items.append({
        "id": object_id,
        "ean": source["ean"],
        "model": source["manufacturerCode"],
        "state": "new",
        "timListPrice": float(source["timListPrice"]),
        "xmlPrice": float(source["xmlPrice"]),
        "xmlStock": float(source["xmlStock"]),
        "documents": documents,
        "matchType": "product_family_and_sale_length_variant",
        "confidence": 90,
    })

report = {
    "generatedAt": datetime.now(timezone.utc).isoformat(),
    "rules": [
        "verified complete EPREL set",
        "CE covers EC608-013-X-XX and EC608-026-X-XX",
        "EC608-026 card covers exact registered light-source family",
        "EC608-013-8-CCT50 deliberately receives no mismatching 5 mm catalog card",
        "exact TIM/XML EAN, trade model and net price; positive XML stock",
    ],
    "counts": {"items": len(items), "rejected": len(rejected)},
    "items": items,
    "rejected": rejected,
}
OUTPUT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"output": str(OUTPUT_PATH), "counts": report["counts"]}, ensure_ascii=False, indent=2))
