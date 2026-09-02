#!/usr/bin/env python3
"""Cross-check the current TIM buffer against the live Prescot XML without writes."""

from __future__ import annotations

import json
import re
import sys
import xml.etree.ElementTree as ET
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path("/Users/karolbohdanowicz/my-ai-agents/prescot")
BUFFER_PATH = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "exports/tim/remediation/buffer-current-live-readonly-after-klus-activations-2026-09-01.json"
ACTIVE_PATH = ROOT / "exports/tim/remediation/active-brand-offer-live-readonly-post-scharfer-2026-09-01.json"
XML_PATH = ROOT / "tmp/sources/prescot-live-2026-08-31.xml"
OUTPUT_PATH = Path(sys.argv[2]) if len(sys.argv) > 2 else ROOT / "exports/tim/remediation/current-buffer-offer-audit-2026-09-01.json"

IN_SCOPE_BRANDS = {"PRESCOT", "KLUŚ DESIGN", "KLUS DESIGN", "MI-LIGHT", "*BŁĘDNE DANE *MILIGHT"}
EXCLUDED_BRANDS = {"KAJA LIGHTING", "LIGHT PRESTIGE"}


def numeric_price(value):
    if isinstance(value, dict):
        value = value.get("value")
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


xml_by_ean = {}
for product in ET.parse(XML_PATH).getroot().findall("o"):
    attrs_node = product.find("attrs")
    attrs = {
        str(node.attrib.get("name") or "").strip(): str(node.text or "").strip()
        for node in list(attrs_node) if attrs_node is not None
    }
    ean = attrs.get("EAN", "")
    if ean:
        xml_by_ean[ean] = {
            "model": attrs.get("Kod producenta", "") or attrs.get("Kod_produktu", ""),
            "price": float(product.attrib.get("price", "0") or 0),
            "stock": float(product.attrib.get("stock", "0") or 0),
            "name": str(product.attrib.get("name") or ""),
            "url": str(product.attrib.get("url") or ""),
        }

active = json.loads(ACTIVE_PATH.read_text(encoding="utf-8"))
active_by_model = {}
active_by_ean = {}
for row in active.get("products", []):
    if row.get("state") != "active":
        continue
    model = str(row.get("model") or "")
    ean = str(row.get("ean") or "")
    if model:
        active_by_model.setdefault(model, []).append(int(row["id"]))
    if ean:
        active_by_ean.setdefault(ean, []).append(int(row["id"]))

buffer = json.loads(BUFFER_PATH.read_text(encoding="utf-8"))
rows = []
for item in buffer.get("items", []):
    ean = str(item.get("ean") or "")
    model = str(item.get("model") or "")
    brand = str(item.get("manufacturerName") or "")
    xml = xml_by_ean.get(ean)
    tim_price = numeric_price(item.get("listPrice"))
    description = str(item.get("descriptionHtml") or "")
    category_path = str((item.get("categoryB24") or {}).get("path") or "")
    energy_count = {
        "class": bool(str(item.get("energyClass") or "").strip()),
        "label": len(item.get("energyClassLabels") or []) == 1,
        "fiche": len(item.get("energyTechnicalCards") or []) == 1,
    }
    exact_identity = bool(xml) and xml["model"] == model
    positive_offer = bool(xml) and xml["stock"] > 0 and xml["price"] > 0
    price_match = bool(xml) and tim_price is not None and abs(tim_price - xml["price"]) < 0.0001
    relations = {
        "dataSheet": len(item.get("dataSheet") or []),
        "certifications": len(item.get("certifications") or []),
        "instructions": len(item.get("instructions") or []),
        "energyClassLabels": len(item.get("energyClassLabels") or []),
        "energyTechnicalCards": len(item.get("energyTechnicalCards") or []),
    }
    blockers = []
    if brand.upper() in EXCLUDED_BRANDS:
        blockers.append("brand_explicitly_excluded")
    elif brand.upper() not in IN_SCOPE_BRANDS:
        blockers.append("brand_outside_core_offer")
    if item.get("state") != "new":
        blockers.append(f"state_{item.get('state')}")
    if not ean:
        blockers.append("ean_missing")
    elif not xml:
        blockers.append("ean_missing_in_xml")
    if xml and not exact_identity:
        blockers.append("xml_model_mismatch")
    if xml and xml["stock"] <= 0:
        blockers.append("xml_stock_not_positive")
    if xml and xml["price"] <= 0:
        blockers.append("xml_price_not_positive")
    if xml and not price_match:
        blockers.append("tim_xml_price_mismatch")
    if not item.get("mainPhoto"):
        blockers.append("main_photo_missing")
    if not model or model not in description or re.search(r"\b\d{13}\b", description):
        blockers.append("description_identity_guard")
    if not relations["dataSheet"]:
        blockers.append("catalog_card_missing")
    duplicates = sorted(set(active_by_model.get(model, []) + active_by_ean.get(ean, [])))
    if duplicates:
        blockers.append("active_duplicate")
    if any(energy_count.values()) and not all(energy_count.values()):
        blockers.append("partial_energy_set")
    if "/Taśmy LED" in category_path and not all(energy_count.values()):
        blockers.append("required_energy_set_missing")
    rows.append({
        "id": int(item["id"]),
        "brand": brand,
        "ean": ean,
        "model": model,
        "name": item.get("timName"),
        "state": item.get("state"),
        "status": item.get("status"),
        "published": item.get("published"),
        "locked": item.get("locked"),
        "categoryB24": category_path,
        "timPrice": tim_price,
        "xml": xml,
        "exactIdentity": exact_identity,
        "positiveOffer": positive_offer,
        "priceMatch": price_match,
        "relations": relations,
        "energyComplete": all(energy_count.values()),
        "activeDuplicates": duplicates,
        "blockers": blockers,
        "safeActivationCandidate": not blockers,
    })

counts = {
    "total": len(rows),
    "coreOffer": sum(row["brand"].upper() in IN_SCOPE_BRANDS for row in rows),
    "prescot": sum(row["brand"].upper() == "PRESCOT" for row in rows),
    "klus": sum(row["brand"].upper() in {"KLUŚ DESIGN", "KLUS DESIGN"} for row in rows),
    "milight": sum("MILIGHT" in row["brand"].upper() or "MI-LIGHT" in row["brand"].upper() for row in rows),
    "new": sum(row["state"] == "new" for row in rows),
    "newForApproval": sum(row["state"] == "new_for_approval" for row in rows),
    "positiveXml": sum(row["positiveOffer"] for row in rows),
    "safeActivationCandidates": sum(row["safeActivationCandidate"] for row in rows),
}
report = {
    "generatedAt": datetime.now(timezone.utc).isoformat(),
    "readOnly": True,
    "sources": {"buffer": str(BUFFER_PATH), "active": str(ACTIVE_PATH), "xml": str(XML_PATH)},
    "counts": counts,
    "blockerCounts": dict(Counter(blocker for row in rows for blocker in row["blockers"])),
    "safeActivationCandidates": [row for row in rows if row["safeActivationCandidate"]],
    "items": rows,
}
OUTPUT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"output": str(OUTPUT_PATH), "counts": counts, "blockerCounts": report["blockerCounts"]}, ensure_ascii=False, indent=2))
