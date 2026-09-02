#!/usr/bin/env python3
"""Build the guarded catalog-card and CE queue for four completed EC528 cards."""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path("/Users/karolbohdanowicz/my-ai-agents/prescot")
DATA = ROOT / "exports/tim/remediation"
BUFFER_PATH = DATA / "buffer-current-live-readonly-after-klus-activations-2026-09-01.json"
AUDIT_PATH = DATA / "current-buffer-offer-audit-2026-09-01.json"
EPREL_QUEUE_PATH = DATA / "buffer-eprel-ec528-family5-queue-2026-09-01.json"
EPREL_VERIFY_PATH = DATA / "buffer-eprel-ec528-family4-final-postverify-2026-09-01.json"
OUTPUT_PATH = DATA / "buffer-ec528-family4-documents-queue-2026-09-01.json"
CARDS = Path("/Users/karolbohdanowicz/Desktop/_PRESCOT/_2026/TIM.PL/Karty katalogowe/TASMY/PREMIUM")
CE_PATH = Path("/Users/karolbohdanowicz/Desktop/_PRESCOT/_2026/TIM.PL/TIM - karty ce/Taśmy LED/Prescot Taśmy led Premium CE 2026.pdf")

CARD_MAP = {
    10647886: (CARDS / "24EC528-045-10-XX.pdf", "24EC528-045-10-XX"),
    10648789: (CARDS / "EC528-045-10-NW i WW.pdf", "EC528-045-10-XX"),
    10648891: (CARDS / "EC528-045-10-W.pdf", "EC528-045-10-XX"),
    10648960: (CARDS / "24EC528-045-10-XX.pdf", "24EC528-045-10-XX"),
}

buffer = json.loads(BUFFER_PATH.read_text(encoding="utf-8"))
buffer_by_id = {int(row["id"]): row for row in buffer["items"]}
audit = json.loads(AUDIT_PATH.read_text(encoding="utf-8"))
audit_by_id = {int(row["id"]): row for row in audit["items"]}
eprel_queue = json.loads(EPREL_QUEUE_PATH.read_text(encoding="utf-8"))
eprel_by_id = {int(row["pimcoreId"]): row for row in eprel_queue["items"]}
verify = json.loads(EPREL_VERIFY_PATH.read_text(encoding="utf-8"))
verified_ids = {int(row["expected"]["pimcoreId"]) for row in verify["products"] if row.get("verified")}

items = []
rejected = []
for object_id, (card_path, card_pattern) in CARD_MAP.items():
    product = buffer_by_id.get(object_id)
    audit_row = audit_by_id.get(object_id)
    source = eprel_by_id.get(object_id)
    model = str(product.get("model") or "") if product else ""
    guards = {
        "verifiedEprel": object_id in verified_ids,
        "source": bool(source),
        "identity": bool(product) and source and str(product.get("ean") or "") == source["ean"] and model == source["manufacturerCode"],
        "state": bool(product) and product.get("state") == "new" and product.get("status") == "new" and product.get("published") is True,
        "emptyDocuments": bool(product) and not product.get("dataSheet") and not product.get("certifications"),
        "description": bool(product) and model in str(product.get("descriptionHtml") or "") and not re.search(r"\b\d{13}\b", str(product.get("descriptionHtml") or "")),
        "cardExists": card_path.is_file(),
        "ceExists": CE_PATH.is_file(),
        "price": bool(source) and float(source["timListPrice"]) == float(source["xmlPrice"]),
        "positiveStock": bool(source) and float(source["xmlStock"]) > 0,
        "noActiveDuplicate": bool(audit_row) and not audit_row.get("activeDuplicates"),
    }
    if not all(guards.values()):
        rejected.append({"id": object_id, "model": model, "reason": "guard_failed", "guards": guards})
        continue
    items.append({
        "id": object_id,
        "ean": source["ean"],
        "model": model,
        "state": "new",
        "timListPrice": float(source["timListPrice"]),
        "xmlPrice": float(source["xmlPrice"]),
        "xmlStock": float(source["xmlStock"]),
        "documents": {
            "dataSheet": {"source": str(card_path), "filename": f"{model}_karta_katalogowa.pdf"},
            "certifications": {"source": str(CE_PATH), "filename": "CE_Prescot_Tasmy_LED_Premium_2026.pdf"},
        },
        "cardPattern": card_pattern,
        "cePattern": "EC528-045-X-XX or 24EC528-045-X-XX",
        "matchType": "product_family_and_sale_length_variant",
        "confidence": 90,
    })

report = {
    "generatedAt": datetime.now(timezone.utc).isoformat(),
    "rules": [
        "complete EPREL set independently verified",
        "catalog card visibly covers the exact EC528/24EC528 family and colour",
        "declaration explicitly covers EC528-045-X-XX and 24EC528-045-X-XX",
        "sale-length variant mapping approved by supplier",
        "exact TIM/XML EAN, trade model and net price; positive XML stock",
        "no active duplicate and no existing catalog/CE relation",
    ],
    "ceDocument": {"number": "CE/PL/03/T2/2026", "date": "2026-06-14", "printedCeMarkYear": "22"},
    "counts": {"items": len(items), "rejected": len(rejected)},
    "items": items,
    "rejected": rejected,
}
OUTPUT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"output": str(OUTPUT_PATH), "counts": report["counts"]}, ensure_ascii=False, indent=2))
