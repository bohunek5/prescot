#!/usr/bin/env python3
"""Build the Prescot description catalog from the current WAPRO XML feed.

Only purchasable products with avail="1" and basket="1" are exported.  The
script also migrates hand-edited descriptions from the former static panel so
they remain available as overrides in the new data-driven UI.
"""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
import urllib.request
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DEFAULT_FEED = "https://prescot.wapromag.pl/prescotcloud.xml"
PLATFORMS = ("shoper", "wapro", "tim", "allegro")


def normalize_space(value: str | None) -> str:
    return re.sub(r"\s+", " ", value or "").strip()


def read_source(source: str) -> bytes:
    path = Path(source)
    if path.exists():
        return path.read_bytes()

    request = urllib.request.Request(
        source,
        headers={"User-Agent": "Prescot-Catalog-Sync/1.0"},
    )
    with urllib.request.urlopen(request, timeout=120) as response:
        return response.read()


def plain_description(raw_html: str) -> str:
    """Turn legacy HTML into conservative, readable source text."""
    if not raw_html:
        return ""

    value = raw_html
    value = re.sub(r"(?is)<(?:script|style)[^>]*>.*?</(?:script|style)>", " ", value)
    value = re.sub(r"(?i)<br\s*/?>|</(?:p|li|h[1-6]|div|section)>", "\n", value)
    value = re.sub(r"(?s)<[^>]+>", " ", value)
    value = html.unescape(value)
    lines = [normalize_space(line) for line in value.splitlines()]
    lines = [line for line in lines if line]

    # Remove accidental boilerplate copied into a few product descriptions.
    cleaned: list[str] = []
    for line in lines:
        low = line.lower()
        if low in {"czytaj poradnik", "praktyczne poradniki"}:
            continue
        if "https://www.prescot.com.pl/pl/n/" in low:
            continue
        cleaned.append(line)

    return "\n".join(cleaned)[:6000]


def product_key(product_id: str, ean: str, code: str, duplicate_eans: set[str]) -> str:
    if ean and ean not in duplicate_eans:
        return f"ean:{ean}"
    if ean and code:
        return f"ean:{ean}|code:{code}"
    if code:
        return f"code:{code}"
    return f"id:{product_id}"


def build_catalog(xml_bytes: bytes) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    root = ET.fromstring(xml_bytes.decode("utf-8-sig"))
    all_offers = root.findall("o")
    active = [
        offer
        for offer in all_offers
        if offer.get("avail") == "1" and offer.get("basket") == "1"
    ]

    active_eans: list[str] = []
    for offer in active:
        attrs = {
            item.get("name", ""): normalize_space(item.text)
            for item in offer.findall("./attrs/a")
        }
        if attrs.get("EAN"):
            active_eans.append(attrs["EAN"])
    duplicate_eans = {ean for ean, count in Counter(active_eans).items() if count > 1}

    products: list[dict[str, Any]] = []
    for offer in active:
        attrs = {
            item.get("name", ""): normalize_space(item.text)
            for item in offer.findall("./attrs/a")
            if item.get("name")
        }
        attrs = {key: value for key, value in attrs.items() if value and value != "-"}

        product_id = offer.get("id", "")
        ean = attrs.get("EAN", "")
        code = attrs.get("Kod_produktu", "")
        category = normalize_space(offer.findtext("cat"))
        images = []
        image_container = offer.find("imgs")
        if image_container is not None:
            images = [
                image.get("url", "")
                for image in image_container
                if image.get("url")
            ]

        products.append(
            {
                "key": product_key(product_id, ean, code, duplicate_eans),
                "id": product_id,
                "name": normalize_space(offer.findtext("name")),
                "category": category,
                "categoryRoot": category.split("/", 1)[0].strip(),
                "producer": attrs.get("Producent", ""),
                "code": code,
                "manufacturerCode": attrs.get("Kod_producenta", ""),
                "ean": ean,
                "url": offer.get("url", ""),
                "price": offer.get("price", ""),
                "stock": offer.get("stock", ""),
                "image": images[0] if images else "",
                "images": images[1:],
                "attributes": attrs,
                "sourceDescription": plain_description(offer.findtext("desc") or ""),
            }
        )

    products.sort(
        key=lambda product: (
            product["categoryRoot"].casefold(),
            product["category"].casefold(),
            product["name"].casefold(),
            product["code"].casefold(),
        )
    )

    missing_ean = sum(not product["ean"] for product in products)
    categories = Counter(product["categoryRoot"] for product in products)
    metadata = {
        "generatedAt": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "source": DEFAULT_FEED,
        "allOffers": len(all_offers),
        "activeProducts": len(products),
        "withEan": len(products) - missing_ean,
        "withoutEan": missing_ean,
        "duplicateEans": sorted(duplicate_eans),
        "categoryRoots": dict(sorted(categories.items(), key=lambda item: (-item[1], item[0]))),
    }
    return products, metadata


def minify_description(fragment: str) -> str:
    fragment = re.sub(r"<!--.*?-->", "", fragment, flags=re.S)
    fragment = re.sub(r">\s+<", "><", fragment)
    fragment = re.sub(r"\s{2,}", " ", fragment)
    return fragment.strip()


def load_legacy_overrides(
    legacy_path: Path,
    products: list[dict[str, Any]],
) -> tuple[dict[str, Any], dict[str, int]]:
    if not legacy_path.exists():
        return {"descriptions": {}, "products": {}}, {"cards": 0, "matched": 0}

    try:
        from bs4 import BeautifulSoup
    except ImportError as exc:  # pragma: no cover - developer environment guard
        raise RuntimeError("BeautifulSoup4 is required to migrate legacy descriptions") from exc

    by_ean: dict[str, list[dict[str, Any]]] = defaultdict(list)
    by_code: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for product in products:
        if product["ean"]:
            by_ean[product["ean"]].append(product)
        for code in (product["code"], product["manufacturerCode"]):
            if code:
                by_code[code.casefold()].append(product)

    soup = BeautifulSoup(legacy_path.read_text(encoding="utf-8"), "html.parser")
    descriptions: dict[str, str] = {}
    assignments: dict[str, dict[str, str]] = defaultdict(dict)
    cards = 0
    matched = 0

    for view in soup.select("div.model-block[id^='desc-view-']"):
        identifier = view.get("id", "")
        match = re.match(r"desc-view-(shoper|wapro|tim|allegro)-(.+)$", identifier)
        if not match:
            continue
        cards += 1
        platform, model = match.groups()
        accordion = view.find_parent("div", class_="product-accordion")

        ean = ""
        if accordion:
            ean_button = accordion.select_one("button.btn-ean")
            if ean_button:
                ean_match = re.search(r"\b(\d{8,14})\b", ean_button.get_text(" ", strip=True))
                if ean_match:
                    ean = ean_match.group(1)

        candidates = by_ean.get(ean, []) if ean else []
        if len(candidates) != 1:
            code_matches = by_code.get(model.casefold(), [])
            if code_matches:
                candidates = code_matches
        if len(candidates) > 1:
            exact = [
                product
                for product in candidates
                if model.casefold()
                in {product["code"].casefold(), product["manufacturerCode"].casefold()}
            ]
            if len(exact) == 1:
                candidates = exact
        if len(candidates) != 1:
            continue

        sections = [
            str(section)
            for section in view.find_all("section", recursive=False)
            if "product-parameters-section" not in (section.get("class") or [])
        ]
        raw_html = "".join(sections) if sections else view.decode_contents()
        raw_html = minify_description(raw_html)
        if len(plain_description(raw_html)) < 40:
            continue

        description_id = hashlib.sha256(raw_html.encode("utf-8")).hexdigest()[:16]
        descriptions.setdefault(description_id, raw_html)
        assignments[candidates[0]["key"]][platform] = description_id
        matched += 1

    used_description_ids = {
        description_id
        for platform_assignments in assignments.values()
        for description_id in platform_assignments.values()
    }
    payload = {
        "descriptions": {
            description_id: description
            for description_id, description in descriptions.items()
            if description_id in used_description_ids
        },
        "products": dict(assignments),
    }
    return payload, {"cards": cards, "matched": matched}


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, separators=(",", ":")),
        encoding="utf-8",
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", default=DEFAULT_FEED)
    parser.add_argument("--legacy", default="index.html")
    parser.add_argument("--output-dir", default="data")
    args = parser.parse_args()

    xml_bytes = read_source(args.source)
    products, metadata = build_catalog(xml_bytes)
    output_dir = Path(args.output_dir)
    overrides, migration = load_legacy_overrides(Path(args.legacy), products)
    existing_overrides_path = output_dir / "manual-overrides.json"
    if not migration["cards"] and existing_overrides_path.exists():
        overrides = json.loads(existing_overrides_path.read_text(encoding="utf-8"))
        active_keys = {product["key"] for product in products}
        overrides["products"] = {
            key: value
            for key, value in overrides.get("products", {}).items()
            if key in active_keys
        }
        used_ids = {
            description_id
            for assignments in overrides["products"].values()
            for description_id in assignments.values()
        }
        overrides["descriptions"] = {
            description_id: description
            for description_id, description in overrides.get("descriptions", {}).items()
            if description_id in used_ids
        }
        migration = {
            "cards": 0,
            "matched": sum(len(value) for value in overrides["products"].values()),
            "source": "existing manual-overrides.json",
        }
    metadata["legacyMigration"] = migration
    metadata["manualOverrideProducts"] = len(overrides["products"])
    metadata["manualOverrideDescriptions"] = len(overrides["descriptions"])

    write_json(output_dir / "catalog.json", {"meta": metadata, "products": products})
    write_json(output_dir / "manual-overrides.json", overrides)

    print(f"Aktywne produkty: {metadata['activeProducts']}")
    print(f"EAN obecny: {metadata['withEan']}; brak EAN: {metadata['withoutEan']}")
    print(
        "Ręczne opisy: "
        f"{metadata['manualOverrideProducts']} produktów / "
        f"{metadata['manualOverrideDescriptions']} unikalnych wersji"
    )
    print(f"Zapisano: {output_dir / 'catalog.json'}")
    print(f"Zapisano: {output_dir / 'manual-overrides.json'}")


if __name__ == "__main__":
    main()
