#!/usr/bin/env python3
"""Build a guarded 90% family-match CE queue for active Prescot accessories."""

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
OUTPUT_PATH = ROOT / "exports/tim/remediation/prescot-active-family-accessory-ce21-queue-2026-09-01.json"

# The PDF explicitly declares each XX family below. Each target is an in-family
# commercial variant; no EAN or PRE/internal identifier is inferred from the PDF.
TARGETS = {
    1343324: ("GN-DC-5.5/2.1+15", "GN-DC-5.5/2.1+XX", r"^GN-DC-5\.5/2\.1\+.+$"),
    1343329: ("GN-DC-5.5/2.5+150CZ", "GN-DC-5.5/2.5+XX", r"^GN-DC-5\.5/2\.5\+.+$"),
    1343332: ("GN-RGB-4PIN15", "GN-RGB-4PIN-XX", r"^GN-RGB-4PIN-?.+$"),
    1343341: ("LED-Z2P-Ż", "LED-Z2P-XX", r"^LED-Z2P-.+$"),
    1343386: ("WT-DC-5.5/2.1+15", "WT-DC-5.5/2.1+XX", r"^WT-DC-5\.5/2\.1\+.+$"),
    1343387: ("WT-DC-5.5/2.1+150", "WT-DC-5.5/2.1+XX", r"^WT-DC-5\.5/2\.1\+.+$"),
    1343392: ("WT-DC-5.5/2.5+15", "WT-DC-5.5/2.5+XX", r"^WT-DC-5\.5/2\.5\+.+$"),
    1343393: ("WT-DC-5.5/2.5+150", "WT-DC-5.5/2.5+XX", r"^WT-DC-5\.5/2\.5\+.+$"),
    1343395: ("WT-DC-5.5/2.5+15CZ", "WT-DC-5.5/2.5+XX", r"^WT-DC-5\.5/2\.5\+.+$"),
    2116879: ("LED-Z2P-Ż8", "LED-Z2P-XX", r"^LED-Z2P-.+$"),
    2116880: ("GN-DC-5.5/2.1+150", "GN-DC-5.5/2.1+XX", r"^GN-DC-5\.5/2\.1\+.+$"),
    2116882: ("LED-Z2P-M", "LED-Z2P-XX", r"^LED-Z2P-.+$"),
    2116891: ("DC5521-1G1G-CZ30", "DC5521-XX", r"^DC5521-.+$"),
    2116892: ("DC5521-1W1W-CZ30", "DC5521-XX", r"^DC5521-.+$"),
    2488069: ("GN-DC-5.5/2.1+150B", "GN-DC-5.5/2.1+XX", r"^GN-DC-5\.5/2\.1\+.+$"),
    2667140: ("GN-DC-5.5/2.1-OB", "GN-DC-5.5/2.1-XX", r"^GN-DC-5\.5/2\.1-.+$"),
    2667175: ("WT-DC-5.5/2.1+15CL", "WT-DC-5.5/2.1+XX", r"^WT-DC-5\.5/2\.1\+.+$"),
    2667176: ("WT-DC-5.5/2.1+150CL", "WT-DC-5.5/2.1+XX", r"^WT-DC-5\.5/2\.1\+.+$"),
    2667178: ("WT-DC-5.5/2.1+150B", "WT-DC-5.5/2.1+XX", r"^WT-DC-5\.5/2\.1\+.+$"),
    5756721: ("WT-DC-5.5/2.1+15W", "WT-DC-5.5/2.1+XX", r"^WT-DC-5\.5/2\.1\+.+$"),
    5756805: ("WT-DC-5.5/2.1+15B", "WT-DC-5.5/2.1+XX", r"^WT-DC-5\.5/2\.1\+.+$"),
}


def xml_by_ean():
    result = {}
    for product in ET.parse(XML_PATH).getroot().findall("o"):
        attrs_node = product.find("attrs")
        attrs = {
            str(node.attrib.get("name") or "").strip(): str(node.text or "").strip()
            for node in list(attrs_node) if attrs_node is not None
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
ce_text_identity = re.sub(r"-\s+", "-", ce_text)

items = []
rejected = []
for object_id, (model, declared_family, target_regex) in TARGETS.items():
    product = live_by_id.get(object_id)
    xml_product = xml.get(str(product.get("ean") or "")) if product else None
    price = product.get("listPrice") if product else None
    tim_price = price.get("value") if isinstance(price, dict) else price
    guards = {
        "liveProduct": bool(product),
        "declaredFamilyInCe": declared_family in ce_text_identity,
        "modelFitsDeclaredFamily": bool(re.fullmatch(target_regex, model)),
        "brand": bool(product) and product.get("expectedBrand") == "Prescot",
        "identity": bool(product) and product.get("model") == model,
        "active": bool(product) and product.get("state") == "active" and product.get("status") == "active" and product.get("published") is True,
        "positiveStock": bool(product) and float(product.get("stock") or 0) > 0,
        "emptyCertifications": bool(product) and not product.get("certifications"),
        "description": bool(product) and model in str(product.get("descriptionHtml") or "") and not re.search(r"\b\d{13}\b", str(product.get("descriptionHtml") or "")),
        "xmlIdentity": bool(xml_product) and xml_product["model"] == model,
        "xmlStock": bool(xml_product) and xml_product["stock"] > 0,
        "price": bool(xml_product) and abs(float(tim_price) - xml_product["price"]) < 0.0001,
    }
    if not all(guards.values()):
        rejected.append({"id": object_id, "model": model, "reason": "guard_failed", "guards": guards})
        continue
    items.append({
        "id": object_id,
        "ean": str(product.get("ean") or ""),
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
        "matchType": "declaration_family_wildcard",
        "declaredFamily": declared_family,
        "confidence": 90,
    })

report = {
    "generatedAt": datetime.now(timezone.utc).isoformat(),
    "sourceLive": str(LIVE_PATH),
    "sourceXml": str(XML_PATH),
    "sourceCe": str(CE_PATH),
    "ceNumber": "CE/PL/02/AKC/2026",
    "ceDate": "2026-07-11",
    "ceMarkYearPrinted": "24",
    "confidence": 90,
    "counts": {"items": len(items), "rejected": len(rejected)},
    "items": items,
    "rejected": rejected,
}
OUTPUT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"output": str(OUTPUT_PATH), "counts": report["counts"]}, ensure_ascii=False, indent=2))
