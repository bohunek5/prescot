#!/usr/bin/env python3
"""Build a guarded CE queue from explicit Prescot declaration families."""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "exports" / "tim" / "remediation"
AUDIT = DATA / "active-brand-offer-prescot-live-after-profile-and-accessory-cards-2026-09-02.json"
DOCS = Path("/Users/karolbohdanowicz/Desktop/_PRESCOT/_2026/TIM.PL/TIM - karty ce")

ACCESSORY_CE = DOCS / "Koszulki silikonowe + akces" / "Prescot akcesoria LED CE.pdf"
PREMIUM_CE = DOCS / "Taśmy LED" / "Prescot Taśmy led Premium CE 2026.pdf"
DELUX_CE = DOCS / "Taśmy LED" / "Prescot Taśmy led Delux CE 2026.pdf"
ECONOMIC_CE = DOCS / "Taśmy LED" / "Prescot Taśmy led Economic CE.pdf"
MODULE_CE = DOCS / "CE stare moze sie przydac" / "Prescot Moduły led CE.pdf"
GU11_CE = DOCS / "CE stare moze sie przydac" / "Prescot Żarówki GU11 CE.pdf"
MAGA_CE = DOCS / "CE stare moze sie przydac" / "Prescot oprawy LED Maga CE.pdf"
TUBE_CE = DOCS / "Świetlówki LED" / "Prescot Świetlówki led CE.pdf"

ACCESSORY_PATTERNS = tuple(re.compile(f"^(?:{pattern})$", re.I) for pattern in (
    r"ZL-2PIN-KLIK-.+", r"LED-Z2P-.+", r"TAM-WZ-.+",
    r"GN-DC-5[.]5/2[.]1-.+", r"GN-DC-5[.]5/2[.]1[+].+", r"GN-DC-5[.]5/2[.]1ZS",
    r"GN-DC-5[.]5/2[.]5[+].+", r"GN-DC-5[.]5/2[.]5ZS", r"LED-ZIP-.+",
    r"GN-RGB-4PIN-.+", r"DC5521-.+", r"DC-DC-.+", r"ROZ-DC-.+", r"WT-ROZ-DC-.+",
    r"WT-DC-5[.]5/2[.]1[+].+", r"WT-DC-5[.]5/2[.]1ZS",
    r"WT-DC-5[.]5/2[.]5[+].+", r"WT-DC-5[.]5/2[.]5ZS", r"WTYK-RGB-.+", r"WT-USB-.+",
    r"ZLRGBGN", r"FC10-COB-RGB-.+", r"PR-ZLH10-.+", r"ZL-MONO-10MM-.+",
    r"PR-ZLH8-.+", r"ZL-MONO-8MM-.+", r"PR-ZLH10-RGB-.+", r"ZL-RGB-10MM-.+",
    r"ZL-RGBW-10MM-.+", r"PR-ZLH12-RGBW-.+", r"ZL-RGBW-12MM-.+", r"FC8-SMD-CCT-.+",
    r"FC8-MONO-MULTI-.+", r"FC10-MONO-MULTI-.+", r"FC10-SMD-RGB-.+", r"FC10-SMD-RGBW-.+",
    r"PR-ZL8-MONO-.+", r"PR-ZL10-MONO-.+", r"PR-ZL10-RGB-.+",
    r"WTDC5A15W", r"WTDC5A15B", r"WTDC5A150W", r"WTDC5A150B",
    r"GNDC5A15W", r"GNDC5A15B", r"GNDC5A150W", r"GNDC5A150B",
    r"GNDC3A150W", r"GNDC3A15W", r"GNDC3A15B", r"GNDC3A150B",
))

TAPE_RULES = {
    "EHP020-050-10-W": (PREMIUM_CE, 95),
    "EHP020-050-10-WW": (PREMIUM_CE, 95),
    "E007-050-8-NW-HL": (PREMIUM_CE, 90),
    "24E024-100-10-W": (PREMIUM_CE, 95),
    "EH024-050-10-G": (ECONOMIC_CE, 95),
    "24D029-166-10-RGBNW": (DELUX_CE, 95),
    "24E020-100-RGBW50": (PREMIUM_CE, 85),
    "24E020-100-RGBWW50": (PREMIUM_CE, 85),
    "E007-025-8-W100": (PREMIUM_CE, 90),
    "EH007-050-10-NW5": (ECONOMIC_CE, 90),
    "EH007-050-8-NW5": (ECONOMIC_CE, 90),
    "24D004-100-10-G": (DELUX_CE, 95),
    "24D004-050-8-WW50": (DELUX_CE, 90),
    "24E007-100-8-W": (PREMIUM_CE, 95),
    "24EC384-042-8-WWL": (PREMIUM_CE, 95),
    "24EC384-042-8-WWL50": (PREMIUM_CE, 90),
    "24E70-7-2790-810": (PREMIUM_CE, 85),
    "E008-050-8-NW100": (PREMIUM_CE, 95),
}

EXACT_RULES = {
    "PR3-GU11-SMD2835-NW": GU11_CE,
    "OP-MAGA-PLUS-59-NW": MAGA_CE,
    "OP-MAGA-59-NW": MAGA_CE,
    "OP-MAGA-38-NW": MAGA_CE,
    "OP-MAGA-30-NW": MAGA_CE,
}

MODULE_FAMILY_IDS = {1627372, 1627373, 2117117, 2117118, 5756692, 5756775, 10650896}
TUBE_DERIVED = {9568132}

ACCESSORY_SAFE_IDS = {
    1343378, 1343379, 1343380, 1343381, 1343398, 1343399, 1343400,
    2116883, 2116885, 2116887, 2116888, 2116889, 2117109, 2117110,
    2117112, 7139829, 7139832, 7139835, 7139838, 10648981, 10648990, 10649017,
    5756781,
}
SAFE_IDS = ACCESSORY_SAFE_IDS | {
    1295208, 1627535, 1627536, 1627538, 2398845,
    1341220, 1341221, 2167272, 2488530, 8659736,
    2398691, 2488662, 2488663, 2398795, 5756692, 5756775,
    # Dodatkowe pochodne 90–95% potwierdzone tekstem deklaracji rodzinnej.
    10650896, 1627372, 1627373, 2117117, 2117118,
    9568132, 8659682, 2116508,
    2667252,
}


def arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--audit", type=Path, default=AUDIT)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--start", type=int, default=0)
    parser.add_argument("--limit", type=int, default=9999)
    parser.add_argument("--exclude-ids", default="")
    return parser.parse_args()


def document(path: Path) -> dict[str, str]:
    if not path.exists():
        raise FileNotFoundError(path)
    return {"source": str(path), "filename": path.name}


def match(product: dict[str, Any]) -> tuple[Path, int, str] | None:
    model = str(product.get("model") or "").strip()
    pid = int(product.get("id") or 0)
    if pid not in SAFE_IDS:
        return None
    if model in EXACT_RULES:
        return EXACT_RULES[model], 100, "Model wpisany w deklaracji wprost."
    if pid in ACCESSORY_SAFE_IDS:
        if model == "TAM-WZ":
            return ACCESSORY_CE, 85, "Bazowy wtyk rodziny TAM-WZ; deklaracja wymienia wariant TAM-WZ-14."
        if model.startswith("WTDC3A"):
            return ACCESSORY_CE, 100, "Model wpisany w deklaracji akcesoriów wprost."
        if model.startswith("TLWY"):
            return ACCESSORY_CE, 90, "Model odpowiada rodzinie TLWY-XX i kategorii przewodów LED."
        if model == "ZL-2PIN-KLIK":
            return ACCESSORY_CE, 86, "Model jest rdzeniem rodziny ZL-2PIN-KLIK-XX."
        return ACCESSORY_CE, 98, "Model odpowiada jawnej rodzinie XX w deklaracji akcesoriów LED."
    if any(pattern.fullmatch(model) for pattern in ACCESSORY_PATTERNS):
        return ACCESSORY_CE, 95, "Model odpowiada jawnej rodzinie XX w deklaracji akcesoriów LED."
    if model in TAPE_RULES:
        path, confidence = TAPE_RULES[model]
        return path, confidence, "Model odpowiada rodzinie X/XX w deklaracji taśm; końcówka długości jest wariantem tej samej rodziny."
    if pid in MODULE_FAMILY_IDS:
        return MODULE_CE, 90, "Nazwa i model wskazują rodzinę Citi, Mini Lens lub Mini Panorama wymienioną w deklaracji modułów LED."
    if pid in TUBE_DERIVED:
        return TUBE_CE, 90, "Model jest wariantem PR15-G13-90-XXP wymienionym w deklaracji; v1 oznacza pochodną wykonania."
    return None


def main() -> None:
    args = arguments()
    excluded_ids = {int(value) for value in args.exclude_ids.split(",") if value.strip().isdigit()}
    audit = json.loads(args.audit.resolve().read_text(encoding="utf-8"))
    candidates = []
    for product in audit.get("products", []):
        if not (
            product.get("httpStatus") == 200
            and product.get("state") == "active"
            and product.get("published") is True
            and float(product.get("stock") or 0) > 0
            and int(product.get("certifications") or 0) == 0
        ):
            continue
        if int(product.get("id") or 0) in excluded_ids:
            continue
        result = match(product)
        if result is None:
            continue
        path, confidence, reason = result
        candidates.append({
            "id": int(product["id"]),
            "ean": str(product.get("ean") or ""),
            "model": str(product.get("model") or ""),
            "state": "active",
            "timName": str(product.get("timName") or ""),
            "xmlStock": float(product.get("stock") or 0),
            "confidence": confidence,
            "reason": reason,
            "requireDescriptionModel": False,
            "documents": {"certifications": document(path)},
        })
    candidates.sort(key=lambda row: (-row["confidence"], -row["xmlStock"], row["model"]))
    selected = candidates[max(0, args.start):max(0, args.start) + max(1, args.limit)]
    report = {
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "readOnly": True,
        "policy": "Only active positive products missing CE; explicit model, declaration XX family, or named module family. No product data writes.",
        "counts": {"candidates": len(candidates), "selected": len(selected)},
        "items": selected,
    }
    args.output.resolve().parent.mkdir(parents=True, exist_ok=True)
    args.output.resolve().write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(args.output.resolve()), "counts": report["counts"], "confidence": {str(level): sum(x["confidence"] == level for x in candidates) for level in sorted({x["confidence"] for x in candidates}, reverse=True)}}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
