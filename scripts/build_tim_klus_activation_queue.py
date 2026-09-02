#!/usr/bin/env python3
"""Create a price-preserving KLUŚ activation queue from the verified document queue."""

from __future__ import annotations

import json
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path("/Users/karolbohdanowicz/my-ai-agents/prescot")
DOC_QUEUE = ROOT / "exports/tim/remediation/klus-buffer-official-documents-queue-2026-09-01.json"
XML_PATH = ROOT / "tmp/sources/prescot-live-2026-08-31.xml"
ACTIVE_PATH = ROOT / "exports/tim/remediation/active-brand-offer-live-readonly-post-scharfer-2026-09-01.json"
BUFFER_PATH = ROOT / "exports/tim/remediation/buffer-current-live-readonly-after-activations-2026-09-01.json"
OUTPUT = ROOT / "exports/tim/remediation/klus-buffer-activation-queue-2026-09-01.json"


documents = json.loads(DOC_QUEUE.read_text(encoding="utf-8"))
active = json.loads(ACTIVE_PATH.read_text(encoding="utf-8"))
buffer = json.loads(BUFFER_PATH.read_text(encoding="utf-8"))
buffer_by_id = {int(row["id"]): row for row in buffer["items"]}
active_by_model = {}
for row in active["products"]:
    if row.get("state") == "active":
        active_by_model.setdefault(row.get("model"), []).append(row)
root = ET.parse(XML_PATH).getroot()
xml_by_ean = {}
for product in root.findall("o"):
    attrs = {
        str(node.attrib.get("name") or "").strip(): str(node.text or "").strip()
        for node in list(product.find("attrs") or [])
    }
    ean = attrs.get("EAN", "")
    if ean:
        xml_by_ean[ean] = {
            "price": float(product.attrib.get("price") or 0),
            "stock": float(product.attrib.get("stock") or 0),
            "model": attrs.get("Kod producenta") or attrs.get("Kod_produktu") or "",
            "url": product.attrib.get("url", ""),
        }

items = []
excluded = []
for row in documents["items"]:
    xml = xml_by_ean.get(row["ean"])
    active_duplicates = [item for item in active_by_model.get(row["model"], []) if int(item["id"]) != int(row["id"])]
    live_buffer = buffer_by_id[int(row["id"])]
    reason = ""
    if active_duplicates:
        reason = "active_model_already_exists"
    elif not live_buffer.get("mainPhoto"):
        reason = "main_photo_missing"
    elif row["state"] != "new":
        reason = f"state_{row['state']}"
    elif not xml:
        reason = "ean_missing_in_xml"
    elif xml["model"] != row["model"]:
        reason = "xml_model_mismatch"
    elif xml["stock"] <= 0:
        reason = "xml_stock_not_positive"
    elif xml["price"] <= 0:
        reason = "xml_net_price_not_positive"
    elif row.get("timListPrice") is None or abs(float(row["timListPrice"]) - xml["price"]) > 0.0001:
        reason = "tim_xml_price_mismatch"
    elif "dataSheet" not in row["documents"]:
        reason = "verified_catalog_card_missing"
    if reason:
        excluded.append({
            "id": row["id"], "ean": row["ean"], "model": row["model"], "reason": reason,
            "timPrice": row.get("timListPrice"), "xml": xml,
            "activeDuplicates": [
                {"id": item["id"], "ean": item.get("ean"), "timIndex": item.get("timIndex")}
                for item in active_duplicates
            ],
        })
        continue
    items.append({
        "id": row["id"],
        "ean": row["ean"],
        "model": row["model"],
        "price": xml["price"],
        "xmlStock": xml["stock"],
        "xmlUrl": xml["url"],
        "requiredRelations": list(row["documents"].keys()),
        "officialProductUrl": row["officialProductUrl"],
    })

report = {
    "generatedAt": datetime.now(timezone.utc).isoformat(),
    "sourceDocumentQueue": str(DOC_QUEUE),
    "sourceXml": str(XML_PATH),
    "rules": [
        "state new only",
        "exact EAN and model match in Prescot XML",
        "positive XML stock",
        "TIM list price equals XML net price; no price writes",
        "verified official KLUŚ catalog card required",
        "main photo required",
        "no active TIM card with the same manufacturer model",
    ],
    "counts": {"ready": len(items), "excluded": len(excluded)},
    "items": items,
    "excluded": excluded,
}
OUTPUT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"output": str(OUTPUT), "counts": report["counts"]}, ensure_ascii=False, indent=2))
