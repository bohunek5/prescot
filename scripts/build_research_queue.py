#!/usr/bin/env python3
"""Build a source-verification queue for sparse Prescot catalog records.

The queue is intentionally read-only with respect to product facts.  It lists
the exact identifiers and product URL that must be checked before an editor or
another script adds web-derived facts to the description pipeline.
"""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ADMIN_FIELDS = {
    "producent odpowiedzialny",
    "podmiot odpowiedzialny",
    "nazwa galerii",
    "informacje o bezpieczeństwie",
}


def normalize(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()


def public_attribute_count(product: dict[str, Any]) -> int:
    return sum(
        bool(normalize(value)) and normalize(label).replace("_", " ").casefold() not in ADMIN_FIELDS
        for label, value in product["attributes"].items()
    )


def source_conflict_reasons(product: dict[str, Any]) -> list[str]:
    name = normalize(product["name"]).casefold()
    source = normalize(product["sourceDescription"]).casefold()
    reasons = []
    if "bez led" in name and re.search(r"zawiera (?:źródło światła|moduł led)|wyposażon\w+ w (?:źródło|moduł led)", source):
        reasons.append("nazwa wskazuje brak LED, a opis źródłowy obecność źródła")
    if "bez zasilacza" in name and re.search(r"zawiera zasilacz|zasilacz (?:jest |w )?komplecie", source):
        reasons.append("nazwa wskazuje brak zasilacza, a opis źródłowy zasilacz w komplecie")
    first_words = source[:100]
    type_prefixes = {
        "ramk": ("łącznik", "wyłącznik", "włącznik", "gniazdo"),
        "wyłącznik": ("ramka", "gniazdo"),
        "włącznik": ("ramka", "gniazdo"),
        "gniazd": ("ramka", "łącznik", "wyłącznik"),
    }
    for name_term, wrong_prefixes in type_prefixes.items():
        if name_term in name and first_words.startswith(wrong_prefixes):
            reasons.append("typ produktu w nazwie nie zgadza się z początkiem opisu źródłowego")
            break
    return reasons


def research_reasons(product: dict[str, Any]) -> list[str]:
    reasons = []
    description_length = len(normalize(product["sourceDescription"]))
    attribute_count = public_attribute_count(product)
    if not description_length:
        reasons.append("brak opisu źródłowego")
    elif description_length < 120:
        reasons.append(f"krótki opis źródłowy ({description_length} znaków)")
    if attribute_count <= 6:
        reasons.append(f"mało parametrów publicznych ({attribute_count})")
    if not product["ean"]:
        reasons.append("brak EAN — wyszukiwanie po kodzie producenta")
    reasons.extend(source_conflict_reasons(product))
    return reasons


def search_queries(product: dict[str, Any]) -> list[str]:
    queries = []
    if product["ean"]:
        queries.append(f'"{product["ean"]}"')
    code = product["manufacturerCode"] or product["code"]
    if code:
        queries.append(f'"{code}" "{product["producer"]}"')
    queries.append(f'"{product["name"]}" "{product["producer"]}"')
    return list(dict.fromkeys(queries))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--catalog", default="data/catalog.json")
    parser.add_argument("--output", default="data/source-research-queue.json")
    args = parser.parse_args()

    catalog = json.loads(Path(args.catalog).read_text(encoding="utf-8"))
    items = []
    for product in catalog["products"]:
        description_length = len(normalize(product["sourceDescription"]))
        attribute_count = public_attribute_count(product)
        if not ((description_length < 120 and attribute_count <= 6) or source_conflict_reasons(product)):
            continue
        priority = 3
        if not description_length:
            priority -= 1
        if attribute_count <= 4:
            priority -= 1
        items.append(
            {
                "key": product["key"],
                "status": "pending",
                "priority": max(1, priority),
                "name": product["name"],
                "category": product["category"],
                "producer": product["producer"],
                "ean": product["ean"],
                "code": product["code"],
                "manufacturerCode": product["manufacturerCode"],
                "productUrl": product["url"],
                "reasons": research_reasons(product),
                "queries": search_queries(product),
                "verifiedSources": [],
                "additionalFacts": {},
            }
        )

    items.sort(key=lambda item: (item["priority"], item["category"].casefold(), item["name"].casefold()))
    payload = {
        "meta": {
            "generatedAt": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "catalogSource": catalog.get("meta", {}).get("source", ""),
            "rule": "(sourceDescription < 120 and publicAttributes <= 6) or source conflict",
            "pending": len(items),
        },
        "products": items,
    }
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Kolejka researchu: {len(items)} produktów")
    print(f"Plik: {output}")


if __name__ == "__main__":
    main()
