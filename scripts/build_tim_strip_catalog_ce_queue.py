#!/usr/bin/env python3
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLAN_PATH = ROOT / "exports/tim/remediation/buffer-document-plan-2026-08-31.json"
OUTPUT_PATH = ROOT / "exports/tim/remediation/buffer-strip-catalog-ce-queue-2026-09-01.json"
DOC_ROOT = Path("/Users/karolbohdanowicz/Desktop/_PRESCOT/_2026/TIM.PL/TIM - karty ce")
CARD_ROOT = DOC_ROOT / "Karty katalogowe/Taśmy LED/PREMIUM"
CE_PATH = DOC_ROOT / "Taśmy LED/Prescot Taśmy led Premium CE 2026.pdf"

CARD_BY_MODEL = {
    "12EC480WW275": CARD_ROOT / "12EC480XX.pdf",
    "24EC320WW1IP67": CARD_ROOT / "24EC320XXIP67.pdf",
    "24EC320NW1IP67": CARD_ROOT / "24EC320XXIP67.pdf",
    "24EC320W1IP67": CARD_ROOT / "24EC320XXIP67.pdf",
    "48EC480-050-8-WW1": CARD_ROOT / "48EC480-050-8-XX.pdf",
    "48EC480-050-8-WW50": CARD_ROOT / "48EC480-050-8-XX.pdf",
    "48EC480-050-8-WW": CARD_ROOT / "48EC480-050-8-XX.pdf",
    "48EC480-050-8-NW50": CARD_ROOT / "48EC480-050-8-XX.pdf",
    "48EC480-050-8-NW": CARD_ROOT / "48EC480-050-8-XX.pdf",
    "ES009-025-4-W20K": CARD_ROOT / "ES009-025-4-W20K.pdf",
    "ES009-050-4-W20K": CARD_ROOT / "ES009-050-4-W20K.pdf",
    "E009-050-8-W6K100": CARD_ROOT / "E009-050-8-XX100.pdf",
}

# The 2026 declaration names these families and its voltage range covers them.
# 48EC480 is named in the declaration, but the stated voltage range omits 48 V,
# so those five models are intentionally held for clarification instead of upload.
CE_MODELS = {
    "12EC480WW275",
    "EC608-013-8-CCT",
    "24EC320WW1IP67",
    "24EC320NW1IP67",
    "24EC320W1IP67",
    "24EC624-019-8-CCT",
    "ES009-025-4-W20K",
    "ES009-050-4-W20K",
    "E009-050-8-W6K100",
    "24E003-050-10-WW",
}

TARGET_MODELS = set(CARD_BY_MODEL) | CE_MODELS


def require_pdf(path: Path) -> None:
    if not path.is_file():
        raise FileNotFoundError(path)
    if path.read_bytes()[:4] != b"%PDF":
        raise ValueError(f"Not a PDF: {path}")


def main() -> None:
    plan = json.loads(PLAN_PATH.read_text(encoding="utf-8"))
    by_model = {record["model"]: record for record in plan["records"]}
    missing = sorted(TARGET_MODELS - set(by_model))
    if missing:
        raise RuntimeError(f"Models missing from buffer plan: {missing}")
    require_pdf(CE_PATH)
    for path in set(CARD_BY_MODEL.values()):
        require_pdf(path)

    items = []
    for model in sorted(TARGET_MODELS, key=lambda value: (-float(by_model[value].get("xmlStock") or 0), value)):
        record = by_model[model]
        documents = {}
        card = CARD_BY_MODEL.get(model)
        if card:
            documents["dataSheet"] = {
                "source": str(card),
                "filename": f"{model}_karta_katalogowa.pdf",
            }
        if model in CE_MODELS:
            documents["certifications"] = {
                "source": str(CE_PATH),
                "filename": "CE_Prescot_tasmy_LED_Premium_2026.pdf",
            }
        items.append({
            "id": int(record["id"]),
            "ean": record["ean"],
            "model": model,
            "timListPrice": record["timListPrice"],
            "xmlPrice": record["xmlPrice"],
            "xmlStock": record["xmlStock"],
            "documents": documents,
        })

    output = {
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "sourcePlan": str(PLAN_PATH),
        "items": items,
        "held": [
            {
                "models": sorted(model for model in TARGET_MODELS if model.startswith("48EC480")),
                "field": "certifications",
                "reason": "Deklaracja CE wymienia rodzinę 48EC480, ale zakres napięcia w tym samym dokumencie podaje tylko 5/12/24 V; brak 48 V.",
            },
            {
                "models": ["EC608-013-8-CCT", "24EC624-019-8-CCT", "24E003-050-10-WW"],
                "field": "dataSheet",
                "reason": "Brak lokalnej karty katalogowej zgodnej z dokładnym modelem lub rodziną XX.",
            },
        ],
    }
    OUTPUT_PATH.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "output": str(OUTPUT_PATH),
        "items": len(items),
        "withDataSheet": sum("dataSheet" in item["documents"] for item in items),
        "withCE": sum("certifications" in item["documents"] for item in items),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
