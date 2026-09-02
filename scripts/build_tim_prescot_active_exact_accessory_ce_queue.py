#!/usr/bin/env python3
"""Build the exact-model, current Prescot accessory CE queue for active TIM cards."""

from __future__ import annotations

import json
import re
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

from pypdf import PdfReader


ROOT = Path("/Users/karolbohdanowicz/my-ai-agents/prescot")
LIVE_PATH = ROOT / "exports/tim/remediation/prescot-active-live-docs-baseline-2026-09-01.json"
XML_PATH = ROOT / "tmp/sources/prescot-live-2026-08-31.xml"
CE_PATH = Path("/Users/karolbohdanowicz/Desktop/_PRESCOT/_2026/TIM.PL/TIM - karty ce/CE stare moze sie przydac/Prescot akcesoria LED CE.pdf")
OUTPUT_PATH = ROOT / "exports/tim/remediation/prescot-active-exact-accessory-ce11-queue-2026-09-01.json"

TARGETS = {
    1343331: "GN-DC-5.5/2.5ZS",
    1343391: "WT-DC-5.5/2.1ZS",
    2117106: "WT-DC-5.5/2.5ZS",
    10649044: "WTDC5A150W",
    10649062: "WTDC5A15B",
    10649080: "WTDC5A150B",
    10649170: "GNDC3A150B",
    10649179: "GNDC3A15B",
    10649191: "GNDC5A150W",
    10649212: "GNDC5A150B",
    10649218: "GNDC5A15B",
}


def xml_by_ean():
    result = {}
    for product in ET.parse(XML_PATH).getroot().findall("o"):
        attrs = {
            str(node.attrib.get("name") or "").strip(): str(node.text or "").strip()
            for node in list(product.find("attrs") or [])
        }
        ean = attrs.get("EAN", "")
        if ean:
            result[ean] = {
                "model": attrs.get("Kod producenta", "") or attrs.get("Kod_produktu", ""),
                "price": float(product.attrib.get("price", "0") or 0),
                "stock": float(product.attrib.get("stock", "0") or 0),
            }
    return result


live = json.loads(LIVE_PATH.read_text(encoding="utf-8"))
live_by_id = {int(row["id"]): row for row in live["products"]}
xml = xml_by_ean()
ce_text = "\n".join(page.extract_text() or "" for page in PdfReader(CE_PATH).pages)
# PDF line wrapping inserts whitespace after a visible trailing hyphen.
ce_text_identity = re.sub(r"-\s+", "-", ce_text)

items = []
rejected = []
for object_id, model in TARGETS.items():
    product = live_by_id.get(object_id)
    if not product:
        rejected.append({"id": object_id, "model": model, "reason": "missing_live_product"})
        continue
    if not re.search(rf"(?<![A-Za-z0-9]){re.escape(model)}(?![A-Za-z0-9])", ce_text_identity):
        rejected.append({"id": object_id, "model": model, "reason": "model_not_exact_in_ce"})
        continue
    ean = str(product.get("ean") or "")
    xml_product = xml.get(ean)
    price = product.get("listPrice")
    tim_price = price.get("value") if isinstance(price, dict) else price
    guards = {
        "brand": product.get("expectedBrand") == "Prescot",
        "identity": product.get("model") == model,
        "active": product.get("state") == "active" and product.get("status") == "active" and product.get("published") is True,
        "positiveStock": float(product.get("stock") or 0) > 0,
        "emptyCertifications": not product.get("certifications"),
        "description": model in str(product.get("descriptionHtml") or "") and not re.search(r"\b\d{13}\b", str(product.get("descriptionHtml") or "")),
        "xmlIdentity": bool(xml_product) and xml_product["model"] == model,
        "xmlStock": bool(xml_product) and xml_product["stock"] > 0,
        "price": bool(xml_product) and abs(float(tim_price) - xml_product["price"]) < 0.0001,
    }
    if not all(guards.values()):
        rejected.append({"id": object_id, "ean": ean, "model": model, "reason": "guard_failed", "guards": guards})
        continue
    items.append({
        "id": object_id,
        "ean": ean,
        "model": model,
        "state": "active",
        "xmlStock": xml_product["stock"],
        "timListPrice": float(tim_price),
        "xmlPrice": xml_product["price"],
        "documents": {
            "certifications": {
                "source": str(CE_PATH),
                "filename": "CE_Prescot_akcesoria_LED_2026.pdf",
            }
        },
        "matchType": "exact_model_in_ce",
        "confidence": 100,
    })

report = {
    "generatedAt": datetime.now(timezone.utc).isoformat(),
    "sourceLive": str(LIVE_PATH),
    "sourceXml": str(XML_PATH),
    "sourceCe": str(CE_PATH),
    "ceNumber": "CE/PL/02/AKC/2026",
    "ceDate": "2026-07-11",
    "counts": {"items": len(items), "rejected": len(rejected)},
    "items": items,
    "rejected": rejected,
}
OUTPUT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"output": str(OUTPUT_PATH), "counts": report["counts"]}, ensure_ascii=False, indent=2))
