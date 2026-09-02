#!/usr/bin/env python3
"""Build a guarded 90% family-match datasheet queue for active Prescot products."""

from __future__ import annotations

import json
import re
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path("/Users/karolbohdanowicz/my-ai-agents/prescot")
LIVE_PATH = ROOT / "exports/tim/remediation/prescot-active-live-docs-baseline-2026-09-01.json"
XML_PATH = ROOT / "tmp/sources/prescot-live-2026-08-31.xml"
BASE = Path("/Users/karolbohdanowicz/Desktop/_PRESCOT/_2026/TIM.PL/TIM - karty ce/Karty katalogowe")
OUTPUT_PATH = ROOT / "exports/tim/remediation/prescot-active-family-datasheet8-queue-2026-09-01.json"
SAFE_EP_OUTPUT_PATH = ROOT / "exports/tim/remediation/prescot-active-family-datasheet-eprel4-queue-2026-09-01.json"
E009_OUTPUT_PATH = ROOT / "exports/tim/remediation/prescot-active-family-datasheet-24e009-queue-2026-09-01.json"
SAFE_EP_IDS = {2488530, 2488663, 8659682, 9568132}
E009_IDS = {9567950, 10047335}

TARGETS = {
    2116508: ("E007-050-8-NW-HL", "E007-050-8-XX", BASE / "Taśmy LED/PREMIUM/E007-050-8-XX.pdf"),
    2398691: ("EH024-050-10-G", "EH024-050-10-XX", BASE / "Taśmy LED/ECONOMIC/EH024-050-10-XX.pdf"),
    2488530: ("E007-025-8-W100", "E007-025-8-XX", BASE / "Taśmy LED/PREMIUM/E007-025-8-XX.pdf"),
    2488663: ("EH007-050-8-NW5", "EH007-050-8-NWXX", BASE / "Taśmy LED/ECONOMIC/EH007-050-8-NWXX.pdf"),
    8659682: ("24D004-050-8-WW50", "24D004-050-8-XX", BASE / "Taśmy LED/DELUX/24D004-050-8-XX.pdf"),
    9567950: ("24E009-050-8-NW100", "24E009-050-8-XX", BASE / "Taśmy LED/PREMIUM/24E009-050-8-XX.pdf"),
    9568132: ("PR15-G13-90-NWPv1", "PR15-G13-90-XX", BASE / "Świetlówki LED/Standard/PR15-G13-90-XX.pdf"),
    10047335: ("24E009-050-8-W100", "24E009-050-8-XX", BASE / "Taśmy LED/PREMIUM/24E009-050-8-XX.pdf"),
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


def family_regex(pattern: str) -> re.Pattern[str]:
    return re.compile("^" + re.escape(pattern).replace("XX", ".+") + "$")


live = json.loads(LIVE_PATH.read_text(encoding="utf-8"))
live_by_id = {int(row["id"]): row for row in live["products"]}
xml = xml_by_ean()
items = []
rejected = []

for object_id, (model, card_pattern, source) in TARGETS.items():
    product = live_by_id.get(object_id)
    ean = str(product.get("ean") or "") if product else ""
    xml_product = xml.get(ean)
    price = product.get("listPrice") if product else None
    tim_price = price.get("value") if isinstance(price, dict) else price
    # Document-family matching ignores only the documented XX colour/variant
    # suffix and an approved sale-length suffix (5/50/100 or -HL/Pv1).
    normalized_model = re.sub(r"(?:50|100|-HL|Pv1)$", "", model)
    card_prefix = card_pattern.split("XX", 1)[0]
    guards = {
        "liveProduct": bool(product),
        "pdfExists": source.is_file(),
        "modelFamily": normalized_model.startswith(card_prefix.rstrip("-")) or bool(family_regex(card_pattern).fullmatch(model)),
        "brand": bool(product) and product.get("expectedBrand") == "Prescot",
        "identity": bool(product) and product.get("model") == model,
        "active": bool(product) and product.get("state") == "active" and product.get("status") == "active" and product.get("published") is True,
        "positiveStock": bool(product) and float(product.get("stock") or 0) > 0,
        "emptyDataSheet": bool(product) and not product.get("dataSheet"),
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
        "ean": ean,
        "model": model,
        "state": "active",
        "xmlStock": xml_product["stock"],
        "timListPrice": float(tim_price),
        "xmlPrice": xml_product["price"],
        "documents": {
            "dataSheet": {
                "source": str(source),
                "filename": f"{model}_karta_katalogowa.pdf",
            }
        },
        "matchType": "datasheet_family_length_variant",
        "cardPattern": card_pattern,
        "confidence": 90,
    })

report = {
    "generatedAt": datetime.now(timezone.utc).isoformat(),
    "sourceLive": str(LIVE_PATH),
    "sourceXml": str(XML_PATH),
    "confidence": 90,
    "counts": {"items": len(items), "rejected": len(rejected)},
    "items": items,
    "rejected": rejected,
}
OUTPUT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
safe_report = {
    **report,
    "scope": "products_with_verified_energy_class_label_and_fiche",
    "items": [row for row in items if int(row["id"]) in SAFE_EP_IDS],
}
safe_report["counts"] = {"items": len(safe_report["items"]), "rejected": 0}
SAFE_EP_OUTPUT_PATH.write_text(json.dumps(safe_report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
e009_report = {
    **report,
    "scope": "24E009 products after official EPREL relation repair",
    "items": [row for row in items if int(row["id"]) in E009_IDS],
}
e009_report["counts"] = {"items": len(e009_report["items"]), "rejected": 0}
E009_OUTPUT_PATH.write_text(json.dumps(e009_report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({
    "output": str(OUTPUT_PATH),
    "safeEprelOutput": str(SAFE_EP_OUTPUT_PATH),
    "counts": report["counts"],
    "safeEprelCounts": safe_report["counts"],
    "e009Output": str(E009_OUTPUT_PATH),
    "e009Counts": e009_report["counts"],
}, ensure_ascii=False, indent=2))
