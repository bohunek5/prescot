#!/usr/bin/env python3
"""Generate source-locked, example-guided SEO descriptions with Ollama.

The generator is deliberately separate from the catalog sync.  It learns tone
and section logic from the hand-edited legacy descriptions, but the facts for a
new description may only come from the target product.  Every result is passed
through factual, editorial, HTML and similarity gates before it is saved.
"""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import math
import re
import time
import urllib.error
import urllib.request
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

from seo_rules import general_editorial


OLLAMA_URL = "http://127.0.0.1:11434/api/chat"
DEFAULT_MODEL = "qwen3.5:latest"
PLATFORMS = ("shoper", "wapro", "tim", "allegro")
ADMIN_ATTRIBUTE_LABELS = {
    "producent odpowiedzialny",
    "podmiot odpowiedzialny",
    "nazwa galerii",
    "informacje o bezpieczeństwie",
}

BANNED_GENERIC = (
    "produkt należy do kategorii",
    "dokładny wariant",
    "przy zakupie porównaj",
    "idealne rozwiązanie",
    "idealny wybór",
    "doskonałe rozwiązanie",
    "najwyższa jakość",
    "nowoczesny design",
    "szerokie zastosowanie",
    "spełni oczekiwania",
    "niezależnie od tego",
    "warto zwrócić uwagę",
    "powiązane poradniki",
    "wydłużony kabel",
    "wydłużony przewód",
    "w długości",
    "idealnie nadaje",
    "idealne do",
    "idealny do",
    "idealn",
    "inwestycja na lata",
    "np.",
    "różnych konfiguracjach",
    "mocna wydajność",
    "solidny wybór",
    "solidne źródło",
    "w specyfikacji wariantu",
    "dane odnoszą się do modelu",
    "oznaczenie występuje w pełnej nazwie produktu",
    "zastosowanie zgodne z grupą",
    "kompletacja systemu po pełnym kodzie",
    "wariant producenta",
    "jednoznaczny kod modelu",
    "parametry wariantu są podane w tabeli technicznej",
    "parametr tego wariantu",
)

STYLE = {
    "section": "font-family:inherit;margin:0 0 18px 0;padding:22px 24px;background:none!important;background-color:transparent!important;border:1px solid currentColor;border-radius:12px;color:inherit;",
    "pill": "font-family:inherit;display:inline-block;margin-bottom:10px;padding:5px 12px;border-radius:999px;background:#e94b25!important;background-color:#e94b25!important;color:#ffffff!important;-webkit-text-fill-color:#ffffff!important;font-size:11px;font-weight:700;letter-spacing:.8px;text-transform:uppercase;line-height:1.2;",
    "heading": "font-family:inherit;margin:0 0 8px 0;background:none!important;background-color:transparent!important;color:inherit!important;font-size:22px;line-height:1.3;font-weight:700;",
    "paragraph": "font-family:inherit;margin:0;background:none!important;background-color:transparent!important;color:inherit!important;opacity:.84;font-size:14px;line-height:1.65;",
    "list": "font-family:inherit;margin:0;padding:0 0 0 20px;color:inherit!important;opacity:.86;font-size:14px;line-height:1.65;",
}

BLOG_GUIDES = {
    "Taśmy LED": {
        "heading": "Dobierz taśmę LED bez zgadywania",
        "description": "Cztery poradniki prowadzą przez parametry, barwę, profil i warunki montażu potrzebne przed zakupem taśmy.",
        "items": [
            ("Jak czytać parametry taśmy LED?", "Moc, lumeny, CRI, napięcie i IP", "https://www.prescot.com.pl/pl/n/23"),
            ("Montaż taśmy LED na zewnątrz", "IP, uszczelnienie i ochrona połączeń", "https://www.prescot.com.pl/pl/n/16"),
            ("Jak dobrać taśmę LED do mieszkania?", "Barwa, moc i miejsce montażu", "https://www.prescot.com.pl/pl/n/12"),
            ("Jak dobrać profil aluminiowy?", "Profil, klosz, chłodzenie i linia światła", "https://www.prescot.com.pl/pl/n/15"),
        ],
    },
    "Profile do taśm LED": {
        "heading": "Dobierz profil i taśmę jako jeden układ",
        "description": "Poradniki pomagają zestawić profil, klosz i taśmę oraz zaplanować chłodzenie i wygląd linii światła.",
        "items": [
            ("Jak dobrać profil aluminiowy?", "Profil, klosz, chłodzenie i estetyka linii światła", "https://www.prescot.com.pl/pl/n/15"),
            ("Jak czytać parametry taśmy LED?", "Moc, lumeny, CRI, napięcie i IP", "https://www.prescot.com.pl/pl/n/23"),
            ("Jak dobrać taśmę LED do mieszkania?", "Barwa, moc i miejsce montażu", "https://www.prescot.com.pl/pl/n/12"),
        ],
    },
    "Zasilacze LED": {
        "heading": "Dobierz zasilacz LED do instalacji",
        "description": "Sprawdź sposób obliczania mocy, typ obudowy i stopień ochrony przed skompletowaniem układu LED.",
        "items": [
            ("Jak dobrać zasilacz LED do taśmy?", "Moc W/m, długość taśmy i zapas mocy", "https://www.prescot.com.pl/pl/n/24"),
            ("Zasilacze LED — gdzie użyć którego?", "Desktop, gniazdkowy, siatkowy, slim i hermetyczny", "https://www.prescot.com.pl/pl/n/25"),
            ("Do czego służą zasilacze LED?", "Taśmy LED, moduły LED i sterowniki", "https://www.prescot.com.pl/pl/n/26"),
            ("Stopnie IP — dlaczego to ważne?", "IP20, IP33, IP44 i IP67 w praktyce", "https://www.prescot.com.pl/pl/n/27"),
        ],
    },
    "Sterowniki LED": {
        "heading": "Skompletuj sterowanie i zasilanie LED",
        "description": "Materiały wyjaśniają zależności między sterownikiem, taśmą, zasilaczem i profilem w jednym układzie.",
        "items": [
            ("Jak dobrać zasilacz LED do taśmy?", "Moc W/m, długość odcinka i zapas mocy", "https://www.prescot.com.pl/pl/n/24"),
            ("Do czego służą zasilacze LED?", "Zasilacz, sterownik i taśma w jednym układzie", "https://www.prescot.com.pl/pl/n/26"),
            ("Jak czytać parametry taśmy LED?", "Napięcie, moc, lumeny i CRI w praktyce", "https://www.prescot.com.pl/pl/n/23"),
        ],
    },
    "Akcesoria do zasilaczy i taśm LED": {
        "heading": "Sprawdź zgodność elementów instalacji LED",
        "description": "Poradniki pomagają porównać napięcie, taśmę, profil i warunki montażu przed doborem osprzętu.",
        "items": [
            ("Jak czytać parametry taśmy LED?", "Moc, lumeny, CRI, napięcie i IP", "https://www.prescot.com.pl/pl/n/23"),
            ("Jak dobrać profil aluminiowy?", "Profil, klosz, chłodzenie i linia światła", "https://www.prescot.com.pl/pl/n/15"),
            ("Montaż taśmy LED na zewnątrz", "IP, uszczelnienie i ochrona połączeń", "https://www.prescot.com.pl/pl/n/16"),
        ],
    },
}

OUTPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "seo_title": {"type": "string"},
        "meta_description": {"type": "string"},
        "sections": {
            "type": "array",
            "minItems": 3,
            "maxItems": 3,
            "items": {
                "type": "object",
                "properties": {
                    "label": {"type": "string"},
                    "heading": {"type": "string"},
                    "paragraphs": {
                        "type": "array",
                        "minItems": 1,
                        "maxItems": 2,
                        "items": {"type": "string"},
                    },
                },
                "required": ["label", "heading", "paragraphs"],
                "additionalProperties": False,
            },
        },
        "benefits": {
            "type": "array",
            "minItems": 2,
            "maxItems": 4,
            "items": {"type": "string"},
        },
        "applications": {
            "type": "array",
            "minItems": 2,
            "maxItems": 4,
            "items": {"type": "string"},
        },
        "selection_checks": {
            "type": "array",
            "minItems": 2,
            "maxItems": 4,
            "items": {"type": "string"},
        },
        "installation_notes": {
            "type": "array",
            "minItems": 1,
            "maxItems": 3,
            "items": {"type": "string"},
        },
        "channel_leads": {
            "type": "object",
            "properties": {
                platform: {"type": "string"}
                for platform in ("wapro", "tim", "allegro")
            },
            "required": ["wapro", "tim", "allegro"],
            "additionalProperties": False,
        },
    },
    "required": [
        "seo_title",
        "meta_description",
        "sections",
        "benefits",
        "applications",
        "selection_checks",
        "installation_notes",
        "channel_leads",
    ],
    "additionalProperties": False,
}


def normalize(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()


def unique_seo_title(title: str, product: dict[str, Any], used_titles: set[str]) -> str:
    """Keep the title readable while disambiguating identically named variants."""
    normalized = normalize(title)
    if normalized.casefold() not in used_titles:
        return normalized

    identifier = normalize(product.get("code") or product.get("manufacturerCode") or product.get("ean"))
    suffix = f" | {identifier}"
    maximum_base_length = 75 - len(suffix)
    base = normalized[:maximum_base_length].rstrip(" –—-|,/")
    if len(normalized) > maximum_base_length and " " in base:
        base = base.rsplit(" ", 1)[0].rstrip(" –—-|,/")
    return f"{base}{suffix}"


def unique_meta_description(meta: str, product: dict[str, Any], used_descriptions: set[str]) -> str:
    """Add the unique catalog code only when two variants share the same meta copy."""
    normalized = normalize(meta)
    if normalized.casefold() not in used_descriptions:
        return normalized

    identifier = normalize(product.get("code") or product.get("manufacturerCode") or product.get("ean"))
    suffix = f"; kod produktu: {identifier}."
    maximum_base_length = 170 - len(suffix)
    base = normalized[:maximum_base_length].rstrip(" .;,–—-|")
    if len(normalized) > maximum_base_length and " " in base:
        base = base.rsplit(" ", 1)[0].rstrip(" .;,–—-|")
    return f"{base}{suffix}"


def strip_html(value: str) -> str:
    value = re.sub(r"(?is)<(?:script|style)[^>]*>.*?</(?:script|style)>", " ", value)
    value = re.sub(r"(?i)<br\s*/?>|</(?:p|li|h[1-6]|section|div)>", "\n", value)
    value = re.sub(r"(?s)<[^>]+>", " ", value)
    return normalize(html.unescape(value))


def words(value: str) -> set[str]:
    tokens = {
        token
        for token in re.findall(r"[a-ząćęłńóśźż0-9]+", value.lower())
        if len(token) >= 3 or any(character.isdigit() for character in token)
    }
    # Preserve compound model codes as a single comparison token.  Splitting
    # CQ-AN1ML and CC-AN1ML into fragments made distinct variants appear
    # identical because the two-letter family prefix was discarded.
    tokens.update(
        re.sub(r"[^a-ząćęłńóśźż0-9]", "", compound.lower())
        for compound in re.findall(
            r"(?i)\b[a-ząćęłńóśźż0-9]+(?:[-_/\.][a-ząćęłńóśźż0-9]+)+\b",
            value,
        )
    )
    return tokens


def jaccard(left: set[str], right: set[str]) -> float:
    if not left or not right:
        return 0.0
    return len(left & right) / len(left | right)


def product_family(product: dict[str, Any]) -> str:
    root = product["categoryRoot"].lower()
    path = f"{product['category']} {product['name']}".lower()
    if root == "taśmy led":
        if "cob" in path:
            return "tasmy:cob"
        if any(value in path for value in ("rgb+cct", "rgbcct", "rgbw", "rgb", "cct", "kolorowe")):
            return "tasmy:kolorowe"
        if "niska jasność" in path or "low brightness" in path or " lb " in f" {path} ":
            return "tasmy:niska"
        if "wysoka jasność" in path:
            return "tasmy:wysoka"
        return "tasmy:standard"
    if root == "profile do taśm led":
        if "zaślepk" in path:
            return "profile:zaslepki"
        if "osłon" in path or "klosz" in path:
            return "profile:oslony"
        if any(value in path for value in ("uchwyt", "sprężyn", "mocowa", "akcesoria montażowe")):
            return "profile:montaz"
        if "pcv" in path or "pvc" in path:
            return "profile:pcv"
        return "profile:aluminium"
    if root == "zasilacze led":
        for key, needle in (
            ("hermetyczne", "hermetycz"),
            ("desktop", "desktop"),
            ("din", "din"),
            ("slim", "slim"),
            ("modulowe", "modułow"),
            ("gniazdkowe", "gniazdkow"),
        ):
            if needle in path:
                return f"zasilacze:{key}"
        return "zasilacze:inne"
    if root == "sterowniki led":
        for key, needle in (
            ("pilot", "pilot"),
            ("panel", "panel"),
            ("wzmacniacz", "wzmacniacz"),
            ("kontroler", "kontroler"),
        ):
            if needle in path:
                return f"sterowniki:{key}"
        return "sterowniki:odbiornik"
    if root == "akcesoria do zasilaczy i taśm led":
        leaf = product["category"].split("/")[-1].lower()
        if "złącz" in leaf:
            return "akcesoria:zlaczki"
        if "wtycz" in leaf:
            return "akcesoria:wtyczki"
        if "gniazd" in leaf:
            return "akcesoria:gniazda"
        if "przew" in leaf or "przedłuż" in leaf:
            return "akcesoria:przewody"
        if "rozdziel" in leaf or "rozgałę" in leaf:
            return "akcesoria:rozdzielacze"
        return "akcesoria:inne"
    if root == "osprzęt elektryczny":
        return f"osprzet:{product['category'].split('/')[-1].lower()}"
    if root == "oprawy led":
        return f"oprawy-led:{product['category'].split('/')[-1].lower()}"
    if root in {"żarówki led", "żarówki standardowe"}:
        return f"zarowki:{product['category'].split('/')[-1].lower()}"
    if root in {"świetlówki led", "świetlówki"}:
        return f"swietlowki:{product['category'].split('/')[-1].lower()}"
    return f"{root}:{product['category'].split('/')[-1].lower()}"


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


def needs_source_research(product: dict[str, Any]) -> bool:
    public_attribute_count = sum(
        bool(normalize(value))
        and normalize(label).replace("_", " ").casefold() not in ADMIN_ATTRIBUTE_LABELS
        for label, value in product["attributes"].items()
    )
    sparse = len(normalize(product["sourceDescription"])) < 120 and public_attribute_count <= 6
    return sparse or bool(source_conflict_reasons(product))


def legacy_sections(raw_html: str) -> list[dict[str, str]]:
    sections = []
    for raw_section in re.findall(r"(?is)<section\b[^>]*>(.*?)</section>", raw_html):
        heading_match = re.search(r"(?is)<h[23][^>]*>(.*?)</h[23]>", raw_section)
        paragraph_matches = re.findall(r"(?is)<p[^>]*>(.*?)</p>", raw_section)
        label_match = re.search(r"(?is)<(?:font|span)[^>]*>(.*?)</(?:font|span)>", raw_section)
        heading = strip_html(heading_match.group(1)) if heading_match else ""
        body = " ".join(strip_html(value) for value in paragraph_matches if strip_html(value))
        label = strip_html(label_match.group(1)) if label_match else ""
        if heading or body:
            sections.append({"label": label[:80], "heading": heading[:180], "body": body[:1400]})
    if not sections:
        text = strip_html(raw_html)
        if text:
            sections.append({"label": "", "heading": "", "body": text[:1800]})
    return sections[:4]


def example_quality(raw_html: str) -> float:
    text = strip_html(raw_html)
    if not text:
        return -100.0
    score = 0.0
    length = len(text)
    if 500 <= length <= 2400:
        score += 4
    elif 300 <= length <= 3200:
        score += 2
    score += min(4, len(re.findall(r"(?i)<section\b", raw_html)))
    score += min(2, len(re.findall(r"(?i)<h3\b", raw_html)))
    score -= sum(2 for phrase in BANNED_GENERIC if phrase in text.lower())
    score -= text.count("!") * 0.4
    if re.search(r"\b(?:najlepszy|rewolucyjny|perfekcyjny)\b", text.lower()):
        score -= 3
    return score


def build_example_index(
    products: list[dict[str, Any]],
    overrides: dict[str, Any],
) -> tuple[dict[str, list[dict[str, Any]]], dict[str, list[dict[str, Any]]]]:
    product_by_key = {product["key"]: product for product in products}
    by_family: dict[str, list[dict[str, Any]]] = defaultdict(list)
    by_root: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for key, assignments in overrides.get("products", {}).items():
        product = product_by_key.get(key)
        if not product:
            continue
        # WAPRO is usually the closest to the sectioned target style.  Fall
        # back to Shoper only when no WAPRO version exists.
        description_id = assignments.get("wapro") or assignments.get("shoper")
        raw_html = overrides.get("descriptions", {}).get(description_id, "")
        if not raw_html:
            continue
        entry = {
            "key": key,
            "name": product["name"],
            "producer": product["producer"],
            "family": product_family(product),
            "root": product["categoryRoot"],
            "tokens": words(f"{product['name']} {product['category']}"),
            "score": example_quality(raw_html),
            "sections": legacy_sections(raw_html),
        }
        by_family[entry["family"]].append(entry)
        by_root[entry["root"]].append(entry)
    for entries in list(by_family.values()) + list(by_root.values()):
        entries.sort(key=lambda item: item["score"], reverse=True)
    return by_family, by_root


def select_examples(
    product: dict[str, Any],
    by_family: dict[str, list[dict[str, Any]]],
    by_root: dict[str, list[dict[str, Any]]],
    limit: int = 3,
) -> list[dict[str, Any]]:
    target_tokens = words(f"{product['name']} {product['category']}")
    # A nearby but functionally different product is a dangerous example:
    # a connector can be solderless while a socket from the same root is not.
    # Use only examples from the exact functional family.
    candidates = by_family.get(product_family(product), [])
    ranked = []
    for candidate in candidates:
        if candidate["key"] == product["key"]:
            continue
        similarity = jaccard(target_tokens, candidate["tokens"])
        producer_bonus = 1.0 if candidate["producer"] == product["producer"] else 0.0
        ranked.append((candidate["score"] + similarity * 4 + producer_bonus, candidate))
    ranked.sort(key=lambda item: item[0], reverse=True)
    return [item[1] for item in ranked[:limit]]


def facts_payload(product: dict[str, Any]) -> dict[str, Any]:
    public_attributes = {
        normalize(label).replace("_", " "): normalize(value)
        for label, value in product["attributes"].items()
        if normalize(label).replace("_", " ").lower() not in ADMIN_ATTRIBUTE_LABELS and normalize(value)
    }
    return {
        "nazwa": product["name"],
        "kategoria": product["category"],
        "producent": product["producer"],
        "kod_produktu": product["code"],
        "kod_producenta": product["manufacturerCode"],
        "ean": product["ean"],
        "parametry": public_attributes,
        "opis_zrodlowy": normalize(product["sourceDescription"])[:3500],
    }


def attribute_value(product: dict[str, Any], *labels: str) -> str:
    wanted = {normalize(label).replace("_", " ").casefold() for label in labels}
    for label, value in product["attributes"].items():
        if normalize(label).replace("_", " ").casefold() in wanted:
            return normalize(value)
    return ""


def critical_constraints(product: dict[str, Any]) -> list[str]:
    constraints: list[str] = []
    sold_by_meter = attribute_value(product, "Taśma na metry").casefold()
    if sold_by_meter == "nie":
        constraints.append("Produkt nie jest sprzedawany na metry. Nie pisz o cięciu z metra ani wyborze dowolnej długości przy zakupie.")
    elif sold_by_meter == "tak":
        constraints.append("Produkt jest oznaczony jako taśma sprzedawana na metry; nie nazywaj go pełną rolką, jeśli dane nie podają rolki.")

    ip_value = attribute_value(product, "Klasa szczelności", "Stopień ochrony")
    ip_match = re.search(r"(?i)IP\s*(\d{2})", ip_value)
    if ip_match and int(ip_match.group(1)) < 44:
        constraints.append(f"Klasa {ip_value} nie daje podstaw do zastosowań mokrych ani zewnętrznych. Nie polecaj produktu do łazienki, pod wodę ani na zewnątrz.")

    polish_production = attribute_value(product, "Polska produkcja").casefold()
    if polish_production == "nie":
        constraints.append("Pole „Polska produkcja” ma wartość „Nie”. Nie opisuj produktu jako polskiej produkcji.")

    color = attribute_value(product, "Barwa światła")
    if color and not re.search(r"(?i)RGB|CCT|wielobarw", f"{color} {product['name']}"):
        constraints.append(f"Wariant ma jedną barwę: {color}. Nie pisz o zmianie kolorów ani sterowaniu barwą, nawet jeśli ogólny opis serii to sugeruje.")

    name_lower = product["name"].casefold()
    if "bez led" in name_lower or "bez źródła" in name_lower:
        constraints.append("Produkt jest sprzedawany bez źródła LED. Nie sugeruj, że źródło światła znajduje się w zestawie.")
    if "bez zasilacza" in name_lower:
        constraints.append("Produkt jest sprzedawany bez zasilacza. Nie sugeruj, że zasilacz znajduje się w zestawie.")
    return constraints


def examples_text(examples: list[dict[str, Any]]) -> str:
    if not examples:
        return "Brak ręcznego wzorca dla tej rodziny. Zachowaj ten sam układ trzech konkretnych sekcji."
    blocks = []
    for index, example in enumerate(examples, 1):
        lines = [f"WZORZEC {index} — {example['name']} (tylko styl i logika, nie fakty):"]
        for section in example["sections"]:
            lines.append(f"- ETYKIETA: {section['label']}")
            lines.append(f"  NAGŁÓWEK: {section['heading']}")
            lines.append(f"  TREŚĆ: {section['body']}")
        blocks.append("\n".join(lines))
    return "\n\n".join(blocks)


def system_prompt() -> str:
    return """Jesteś redaktorem opisów produktowych Prescot LED. Piszesz po polsku dla klienta, instalatora i osoby kompletującej system.

NAJWAŻNIEJSZE:
- Fakty wolno brać WYŁĄCZNIE z bloku DANE PRODUKTU. Wzorce pokazują styl, nigdy parametry.
- Nie dopisuj napięcia, mocy, prądu, IP, wymiarów, gwarancji, materiału, kompatybilności ani funkcji, których nie ma w danych.
- Nie przenoś z wzorców takich cech jak: bez lutowania, liczba pinów lub żył, rodzaj montażu, wodoodporność, zasięg, zabezpieczenia czy kompatybilność. Jeśli nie ma ich w danych produktu, pomiń je.
- Nie dopisuj przykładów miejsc montażu po „np.”. Nie deklaruj współpracy z innymi markami, standardowego złącza, rozgałęziania, lutowania, zaciskania, klejenia ani ukrywania przewodu, jeśli dane nie mówią o tym wprost.
- Nie zamieniaj „pewnego połączenia” w obietnicę eliminowania luźnych styków lub ryzyka. Nie wzmacniaj znaczenia źródła.
- Jeśli nazwa, parametry i opis źródłowy się różnią, pierwszeństwo mają parametry i pełna nazwa.
- Nie używaj tekstów o kodach, EAN-ie, kategorii katalogowej ani "dokładnym wariancie" w narracji sprzedażowej.
- Nie pisz: idealny wybór, doskonałe rozwiązanie, najwyższa jakość, nowoczesny design, szerokie zastosowanie, spełni oczekiwania.
- Każda sekcja ma odpowiadać na inne pytanie: co ten wariant realnie daje; gdzie ma sens; co sprawdzić przy doborze lub montażu.
- Nagłówki muszą wynikać z konkretnego parametru, konstrukcji lub zastosowania produktu. Żadnych pustych nagłówków typu "Najważniejsze informacje".
- Pisz rzeczowo, naturalnie i technicznie. Bez wykrzykników, bez lania wody i bez zdań o "inwestycji na lata".
- Nie powtarzaj tej samej informacji w dwóch sekcjach.
- Trzecia sekcja ma dotyczyć konkretnego doboru albo montażu tego produktu. Nie nazywaj jej "Powiązane poradniki" ani "Najważniejsze informacje".
- benefits: 2–4 krótkie, konkretne korzyści wynikające wprost z danych. Każda ma mówić coś innego.
- applications: 2–4 konkretne zastosowania właściwe dla tego produktu. Nie poszerzaj zastosowania poza dane i oczywistą funkcję produktu.
- selection_checks: 2–4 rzeczy, które klient rzeczywiście powinien porównać przed zakupem tego wariantu.
- installation_notes: 1–3 praktyczne uwagi montażowe. Jeśli dane nie potwierdzają szczegółowej metody montażu, ogranicz się do jednej uwagi o sprawdzeniu zgodności; niczego nie wymyślaj.
- Listy mają być krótkie: jeden punkt 25–120 znaków, bez kropki na końcu. Nie kopiuj całych zdań z trzech sekcji.
- SEO ma wynikać z naturalnego użycia nazwy produktu, rodzaju, producenta i kluczowego parametru. Nie upychaj fraz.
- Dla taśm 1 m, 3 m i 5 m nie używaj słów rolka, szpula ani rolki; pisz odcinek lub wariant cięty z metra.
- Dla taśm 50 m i 100 m możesz opisać zaletę dłuższego wariantu, ale lepszą cenę tylko wtedy, gdy wynika to z nazwy lub opisu źródłowego.
- Nie próbuj osiągać długości kosztem nowych tez. Dla produktu z małą liczbą parametrów lepszy jest krótki, precyzyjny opis niż rozbudowane przypuszczenia.
- Wolno odmieniać zdania, używać naturalnych synonimów i poprawiać składnię, ale sens każdej tezy musi pozostać nie szerszy niż w danych. „Pewne połączenie” nie znaczy „eliminuje luźne styki”, a „kompatybilność z wieloma urządzeniami” nie znaczy „zgodność ze wszystkimi markami”.
- Przed zwróceniem JSON-u wykonaj cichy audyt zdanie po zdaniu: wskaż sobie konkretny fragment DANYCH PRODUKTU, który potwierdza każdą cechę, korzyść, zastosowanie i uwagę. Jeśli nie potrafisz, usuń tę tezę.

Zwróć wyłącznie JSON w poniższej strukturze; nie zamieniaj obiektów ani list na zwykły tekst:
{
  "seo_title": "tekst",
  "meta_description": "tekst",
  "sections": [{"label": "tekst", "heading": "tekst", "paragraphs": ["tekst"]}, {"label": "tekst", "heading": "tekst", "paragraphs": ["tekst"]}, {"label": "tekst", "heading": "tekst", "paragraphs": ["tekst"]}],
  "benefits": ["tekst", "tekst"],
  "applications": ["tekst", "tekst"],
  "selection_checks": ["tekst", "tekst"],
  "installation_notes": ["tekst"],
  "channel_leads": {
    "wapro": "krótki akapit",
    "tim": "krótki akapit",
    "allegro": "krótki akapit"
  }
}
Trzy główne sekcje są bazą merytoryczną. channel_leads mają być trzema krótkimi, naprawdę różnymi akapitami dla WAPRO, TIM i Allegro:
- WAPRO: konkretnie i handlowo, bez ozdobników.
- TIM: technicznie, pod dobór i zgodność.
- Allegro: korzyść użytkowa oraz jedna rzecz do sprawdzenia przed zakupem.
"""


def user_prompt(product: dict[str, Any], examples: list[dict[str, Any]], retry_feedback: str = "") -> str:
    feedback = f"\nBŁĘDY POPRZEDNIEJ PRÓBY — popraw je wszystkie:\n{retry_feedback}\n" if retry_feedback else ""
    constraints = critical_constraints(product)
    constraints_text = "\n".join(f"- {value}" for value in constraints) or "- Brak dodatkowych konfliktów wykrytych w polach strukturalnych."
    return f"""RODZINA PRODUKTU: {product_family(product)}

DANE PRODUKTU (jedyne dozwolone źródło faktów):
{json.dumps(facts_payload(product), ensure_ascii=False, indent=2)}

OGRANICZENIA TEGO WARIANTU (ważniejsze niż ogólny opis serii):
{constraints_text}

WZORCE Z ISTNIEJĄCEJ BAZY:
{examples_text(examples)}
{feedback}
Napisz opis tego jednego produktu. SEO title: 45–70 znaków. Meta description: 130–165 znaków. Każda z trzech sekcji ma mieć konkretny nagłówek i 1–2 krótkie akapity. Łączna narracja może mieć 380–1400 znaków; dopasuj długość do ilości wiarygodnych danych. Wypełnij też cztery listy potrzebne do osobnych układów Shoper, TIM i Allegro."""


def call_ollama(model: str, prompt: str, seed: int, timeout: int, thinking: bool) -> dict[str, Any]:
    payload = {
        "model": model,
        "think": thinking,
        "messages": [
            {"role": "system", "content": system_prompt()},
            {"role": "user", "content": prompt},
        ],
        "format": "json" if model.endswith("-cloud") else OUTPUT_SCHEMA,
        "stream": False,
        "options": {
            "temperature": 0.35,
            "top_p": 0.85,
            "repeat_penalty": 1.12,
            "num_ctx": 24576 if thinking else 16384,
            "num_predict": 8192 if thinking else 3200,
            "seed": seed,
        },
    }
    request = urllib.request.Request(
        OLLAMA_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        result = json.loads(response.read().decode("utf-8"))
    content = result.get("message", {}).get("content", "")
    if not content:
        thinking = result.get("message", {}).get("thinking", "")
        raise json.JSONDecodeError(
            f"Model zwrócił pustą treść (thinking={len(thinking)} znaków)",
            content,
            0,
        )
    return json.loads(content)


def all_generated_text(result: dict[str, Any]) -> str:
    parts = [result.get("seo_title", ""), result.get("meta_description", "")]
    for section in result.get("sections", []):
        if not isinstance(section, dict):
            continue
        parts.extend([section.get("label", ""), section.get("heading", "")])
        paragraphs = section.get("paragraphs", [])
        if isinstance(paragraphs, list):
            parts.extend(paragraphs)
    leads = result.get("channel_leads", {})
    for lead in leads.values() if isinstance(leads, dict) else []:
        if isinstance(lead, str):
            parts.append(lead)
    for field in ("benefits", "applications", "selection_checks", "installation_notes"):
        values = result.get(field, [])
        if isinstance(values, list):
            parts.extend(values)
    return normalize(" ".join(parts))


def normalize_measure(value: str) -> str:
    normalized = value.lower().replace(",", ".")
    normalized = re.sub(r"\bip\s*[:\-]?\s*(\d+)", r"ip\1", normalized)
    normalized = re.sub(r"\s+", "", normalized)
    normalized = re.sub(r"(?:diod|diód|dioda)/m$", "led/m", normalized)
    normalized = re.sub(r"mies(?:iąc|iące|ięcy)$", "miesiące", normalized)
    normalized = re.sub(r"(?:rok|roku|lata|lat)$", "lat", normalized)
    return normalized


def measurement_tokens(value: str) -> set[str]:
    value = re.sub(r"(?i)(\d)\s+w\s+(?=(?:specyfikacji|tym wariancie|wariancie))", r"\1 ", value)
    value = re.sub(r"(?<=\d)\s*\.{2,3}\s*(?=\d)", "-", value)
    value = re.sub(r"(?i)\bIP\s*[:\-]?\s*(\d+)", r"IP\1", value)
    value = re.sub(
        r"(?i)\[(V|W|A|mA|Hz|lm|mm|cm)\][^0-9]{0,12}(\d+(?:[.,]\d+)?(?:\s*[-–]\s*\d+(?:[.,]\d+)?)?)",
        lambda match: f"{match.group(2)}{match.group(1)}",
        value,
    )
    unit = r"lm/w|lm/m|w/m|led/m|diod/m|diód/m|dioda/m|hz|v|w|a|ma|awg|lm|k|mm|cm|m|h|led|oz|pin|lat|lata|rok|roku|miesiąc|miesiące|miesięcy|°"
    tokens: set[str] = set()
    range_pattern = re.compile(
        rf"(?i)\b(\d+(?:[.,]\d+)?)\s*[-–]\s*(\d+(?:[.,]\d+)?)\s*({unit})\b"
    )
    for match in range_pattern.finditer(value):
        lower, upper, range_unit = match.groups()
        tokens.add(normalize_measure(f"{lower}{range_unit}"))
        tokens.add(normalize_measure(f"{upper}{range_unit}"))
    pattern = re.compile(
        rf"(?i)(?:\bip\s*\d+\b|\bcri\s*\d+\b|\bra\s*\d+\b|"
        rf"\b\d+(?:[.,]\d+)?\s*[-–]?\s*(?:{unit})\b)"
    )
    tokens.update(normalize_measure(match.group(0)) for match in pattern.finditer(value))
    return tokens


def validate_result(
    product: dict[str, Any],
    result: dict[str, Any],
    family_texts: list[set[str]],
    family_similarity_limit: float = 0.64,
    lead_similarity_limit: float = 0.48,
) -> tuple[list[str], dict[str, Any]]:
    errors: list[str] = []
    if not isinstance(result, dict):
        return ["Odpowiedź nie jest obiektem JSON."], {"score": 0}
    if not isinstance(result.get("sections"), list) or any(
        not isinstance(section, dict) or not isinstance(section.get("paragraphs"), list)
        for section in result.get("sections", [])
    ):
        errors.append("Nieprawidłowa struktura sections; wymagane obiekty z listą paragraphs.")
    for field in ("benefits", "applications", "selection_checks", "installation_notes"):
        if not isinstance(result.get(field), list) or any(not isinstance(value, str) for value in result.get(field, [])):
            errors.append(f"Nieprawidłowa struktura {field}; wymagana lista tekstów.")
    leads = result.get("channel_leads")
    if not isinstance(leads, dict) or any(
        platform not in leads or not isinstance(leads.get(platform), str)
        for platform in ("wapro", "tim", "allegro")
    ):
        errors.append("Nieprawidłowa struktura channel_leads; wymagane teksty WAPRO, TIM i Allegro.")
    if errors:
        return errors, {"score": 0, "narrationLength": 0}

    sections = result.get("sections", [])
    if len(sections) != 3:
        errors.append("Opis musi mieć dokładnie 3 sekcje.")
    title = normalize(result.get("seo_title"))
    meta = normalize(result.get("meta_description"))
    if not 40 <= len(title) <= 75:
        errors.append(f"SEO title ma {len(title)} znaków; wymagane 40–75.")
    if not 120 <= len(meta) <= 170:
        errors.append(f"Meta description ma {len(meta)} znaków; wymagane 120–170.")

    narration_parts = []
    for index, section in enumerate(sections, 1):
        label = normalize(section.get("label"))
        heading = normalize(section.get("heading"))
        paragraphs = [normalize(value) for value in section.get("paragraphs", []) if normalize(value)]
        if not 3 <= len(label) <= 55:
            errors.append(f"Sekcja {index}: etykieta ma złą długość.")
        if not 12 <= len(heading) <= 130:
            errors.append(f"Sekcja {index}: nagłówek ma złą długość.")
        if not paragraphs or any(len(value) < 45 for value in paragraphs):
            errors.append(f"Sekcja {index}: akapit jest zbyt krótki.")
        narration_parts.extend([heading, *paragraphs])
    narration = normalize(" ".join(narration_parts))
    if not 360 <= len(narration) <= 1600:
        errors.append(f"Narracja ma {len(narration)} znaków; wymagane 360–1600.")

    structured_points: list[tuple[str, str]] = []
    list_rules = {
        "benefits": (2, 4, "Korzyści"),
        "applications": (2, 4, "Zastosowania"),
        "selection_checks": (2, 4, "Kontrola doboru"),
        "installation_notes": (1, 3, "Uwagi montażowe"),
    }
    for field, (minimum, maximum, label) in list_rules.items():
        values = [normalize(value).removesuffix(".") for value in result.get(field, []) if normalize(value)]
        if not minimum <= len(values) <= maximum:
            errors.append(f"{label}: wymagane {minimum}–{maximum} punktów.")
        for value in values:
            if not 5 <= len(value) <= 135:
                errors.append(f"{label}: punkt ma {len(value)} znaków; wymagane 5–135.")
            if value.startswith(("-", "•", "✓")):
                errors.append(f"{label}: punkt zawiera ręcznie dodany punktor.")
            structured_points.append((field, value))

    repeated_points = set()
    for left_index, (left_field, left_value) in enumerate(structured_points):
        for right_field, right_value in structured_points[left_index + 1 :]:
            if normalize(left_value).lower() == normalize(right_value).lower():
                repeated_points.add(f"{left_field}/{right_field}")
    if repeated_points:
        errors.append("Listy powtarzają punkty: " + ", ".join(sorted(repeated_points)) + ".")

    all_text = all_generated_text(result)
    lower = all_text.lower()
    for phrase in BANNED_GENERIC:
        if phrase in lower:
            errors.append(f"Generyczna fraza: „{phrase}”.")
    if "!" in all_text:
        errors.append("Opis zawiera wykrzyknik.")
    if re.search(r"\b(?:rewolucyjny|perfekcyjny|bezkonkurencyjny)\b", lower):
        errors.append("Opis zawiera nieuzasadnione superlatywy.")

    source_facts = json.dumps(facts_payload(product), ensure_ascii=False)
    allowed_measurements = measurement_tokens(source_facts)
    diode_count = attribute_value(product, "Ilość diod")
    diode_match = re.search(r"(?i)\b(\d+(?:[.,]\d+)?)\s*/\s*m\b", diode_count)
    if diode_match:
        allowed_measurements.add(normalize_measure(f"{diode_match.group(1)}led/m"))
    output_measurements = measurement_tokens(all_text)
    foreign_measurements = sorted(output_measurements - allowed_measurements)
    if foreign_measurements:
        errors.append("Obce liczby lub jednostki: " + ", ".join(foreign_measurements))

    product_data = source_facts.lower()
    guarded_claims = {
        "polska produkcja": ("polska produkcja",),
        "wodoodporn": ("ip6", "wodoodporn"),
        "na zewnątrz": ("ip6", "na zewnątrz", "zewnętrz"),
        "do łazienki": ("ip6", "łazien"),
        "bez migotania": ("bez migotania",),
        "zabezpieczenie przeciwzwarciowe": ("zabezpieczenie przeciwzwarciowe",),
        "zabezpieczenia przeciwzwarciowe": ("zabezpieczenia przeciwzwarciowe",),
        "bez lutowania": ("bez lutowania",),
        "bezlutow": ("bezlutow",),
        "standardow": ("standardow",),
        "bez konieczności stosowania dodatkowych": ("bez konieczności stosowania dodatkowych",),
        "łatwy montaż": ("łatwy montaż", "łatwa instalacja", "łatwą instalację"),
        "łatwe podłączenie": ("łatwe podłączenie", "łatwa instalacja", "łatwą instalację"),
        "szybki montaż": ("szybki montaż",),
        "stabilne zasilanie": ("stabilne zasilanie",),
        "bezpieczn": ("bezpieczn",),
        "energooszczęd": ("energooszczęd",),
        "odporny na wilgoć": ("ip6", "wilgo"),
        "odporna na wilgoć": ("ip6", "wilgo"),
        "odporność na wilgoć": ("ip6", "wilgo"),
        "pełne obciążenie": ("pełne obciążenie", "100% obciążenia"),
        "innych marek": ("innych marek",),
        "elimin": ("elimin",),
        "luźnych styk": ("luźnych styk",),
        "rozgałę": ("rozgałę",),
        "lutow": ("lutow",),
        "zacisk": ("zacisk",),
        "doklej": ("doklej",),
        "sieciow": ("sieciow",),
        "ograniczonej przestrzeni": ("ograniczonej przestrzeni",),
        "uszkodzenia izolacji": ("uszkodzenia izolacji",),
        "oszczędza miejsce": ("oszczędza miejsce",),
        "estetyczny montaż": ("estetyczny montaż",),
        "nie rzuca się w oczy": ("nie rzuca się w oczy",),
        "listw sufit": ("listw sufit",),
        "niskim pobor": ("niskim pobor",),
        "równomier": ("równomier",),
        "nie żółknie": ("nie żółknie",),
        "bez laboratoryjnego efektu": ("bez laboratoryjnego efektu",),
        "unikając odpad": ("odpad",),
        "stabiln": ("stabiln",),
        "dodatkowego źródła": ("dodatkowego źródła",),
        "wnęk": ("wnęk",),
    }
    for claim, evidence_options in guarded_claims.items():
        if claim in lower and not any(evidence in product_data for evidence in evidence_options):
            errors.append(f"Brak źródła dla twierdzenia: „{claim}”.")

    name_lower = product["name"].lower()
    if ("bez led" in name_lower or "bez źródła" in name_lower) and re.search(r"zawiera źródło|ze źródłem", lower):
        errors.append("Sprzeczność: produkt bez LED opisano jako zawierający źródło.")
    if "bez zasilacza" in name_lower and re.search(r"zasilacz (?:jest |w )?komplecie|zawiera zasilacz", lower):
        errors.append("Sprzeczność: produkt bez zasilacza opisano jako zestaw z zasilaczem.")

    sold_by_meter = attribute_value(product, "Taśma na metry").casefold()
    if sold_by_meter == "nie" and re.search(r"(?:cięt\w* z metra|sprzedawan\w* na metry|dostępn\w* na metry|wybór dowolnej długości)", lower):
        errors.append("Sprzeczność: taśmę oznaczoną „Taśma na metry: Nie” opisano jako sprzedawaną z metra.")

    ip_value = attribute_value(product, "Klasa szczelności", "Stopień ochrony")
    ip_match = re.search(r"(?i)IP\s*(\d{2})", ip_value)
    if ip_match and int(ip_match.group(1)) < 44 and re.search(r"(?:łazien|na zewnątrz|zewnętrz|mokrych|wilgotnych|pod wod)", lower):
        errors.append(f"Sprzeczność: zastosowanie mokre lub zewnętrzne przy klasie {ip_value}.")

    polish_production = attribute_value(product, "Polska produkcja").casefold()
    if polish_production == "nie" and "polska produkcja" in lower:
        errors.append("Sprzeczność: pole „Polska produkcja” ma wartość „Nie”.")

    light_color = attribute_value(product, "Barwa światła")
    if light_color and not re.search(r"(?i)RGB|CCT|wielobarw", f"{light_color} {product['name']}") and re.search(
        r"(?:zmian\w* (?:barw|kolor)|sterowan\w* barw|wielobarw)", lower
    ):
        errors.append(f"Sprzeczność: wariant {light_color} opisano jak produkt ze zmianą barwy.")

    text_words = words(narration)
    max_similarity = max((jaccard(text_words, previous) for previous in family_texts), default=0.0)
    if max_similarity > family_similarity_limit:
        errors.append(f"Zbyt duże podobieństwo do opisu w tej rodzinie: {max_similarity:.0%}.")

    section_word_sets = [words(normalize(" ".join(section.get("paragraphs", [])))) for section in sections]
    internal_similarity = max(
        (jaccard(section_word_sets[i], section_word_sets[j]) for i in range(len(section_word_sets)) for j in range(i + 1, len(section_word_sets))),
        default=0.0,
    )
    if internal_similarity > 0.52:
        errors.append(f"Sekcje powtarzają tę samą treść: {internal_similarity:.0%} podobieństwa.")

    core_word_sets = [
        words(normalize(f"{section.get('heading', '')} {' '.join(section.get('paragraphs', []))}"))
        for section in sections
    ]
    lead_similarities = []
    for platform, lead in result.get("channel_leads", {}).items():
        lead_text = normalize(lead)
        lead_words = words(lead_text)
        lead_similarity = max((jaccard(lead_words, core_words) for core_words in core_word_sets), default=0.0)
        lead_similarities.append(lead_similarity)
        if lead_similarity > lead_similarity_limit:
            errors.append(f"Lead {platform} kopiuje główną sekcję: {lead_similarity:.0%} podobieństwa.")
        if not 80 <= len(lead_text) <= 360:
            errors.append(f"Lead {platform} ma {len(lead_text)} znaków; wymagane 80–360.")

    score = max(0, 100 - len(errors) * 12 - round(max_similarity * 10))
    metrics = {
        "score": score,
        "narrationLength": len(narration),
        "maxFamilySimilarity": round(max_similarity, 4),
        "internalSimilarity": round(internal_similarity, 4),
        "maxLeadSimilarity": round(max(lead_similarities, default=0.0), 4),
        "measurements": sorted(output_measurements),
    }
    return errors, metrics


def pill_style(color: str) -> str:
    return STYLE["pill"].replace("#e94b25", color)


def render_section(section: dict[str, Any], color: str = "#e94b25", label: str = "", heading: str = "") -> str:
    paragraphs = "".join(
        f'<p style="{STYLE["paragraph"]}{"margin-top:10px;" if index else ""}">{html.escape(normalize(value))}</p>'
        for index, value in enumerate(section["paragraphs"])
    )
    section_label = normalize(label or section["label"])
    section_heading = normalize(heading or section["heading"])
    return (
        f'<section style="{STYLE["section"]}">'
        f'<span style="{pill_style(color)}"><font color="#ffffff">{html.escape(section_label)}</font></span>'
        f'<h3 style="{STYLE["heading"]}">{html.escape(section_heading)}</h3>'
        f"{paragraphs}</section>"
    )


def render_lead(label: str, heading: str, paragraph: str, color: str = "#e94b25") -> str:
    return render_section(
        {
            "label": label,
            "heading": heading,
            "paragraphs": [paragraph],
        },
        color=color,
    )


def product_specs(product: dict[str, Any]) -> list[tuple[str, str]]:
    specs: list[tuple[str, str]] = []
    seen: set[str] = set()
    for label, value in product["attributes"].items():
        display_label = normalize(label).replace("_", " ")
        clean_value = normalize(value)
        identity = display_label.lower()
        if identity in ADMIN_ATTRIBUTE_LABELS or identity in seen or not clean_value or clean_value == "-":
            continue
        seen.add(identity)
        specs.append((display_label, clean_value))
    return specs


def render_specs(product: dict[str, Any], color: str = "#475569") -> str:
    items = []
    for label, value in product_specs(product):
        items.append(
            '<div style="display:flex;flex-direction:column;min-width:0;word-break:break-word;">'
            f'<span style="font-size:12px;color:#64748b;margin-bottom:4px;text-transform:uppercase;letter-spacing:.5px;">{html.escape(label)}</span>'
            f'<span style="font-size:15px;font-weight:700;color:inherit;">{html.escape(value)}</span>'
            "</div>"
        )
    return (
        f'<section style="{STYLE["section"]}">'
        f'<span style="{pill_style(color)}"><font color="#ffffff">Parametry</font></span>'
        f'<h3 style="{STYLE["heading"]}">Dane wariantu {html.escape(product["manufacturerCode"] or product["code"])}</h3>'
        '<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:16px;margin-top:6px;">'
        f'{"".join(items)}</div></section>'
    )


def render_points_section(label: str, heading: str, points: list[str], color: str = "#e94b25") -> str:
    items = "".join(
        f'<li style="font-family:inherit;margin-bottom:7px;">{html.escape(normalize(point).removesuffix("."))}</li>'
        for point in points
    )
    return (
        f'<section style="{STYLE["section"]}">'
        f'<span style="{pill_style(color)}"><font color="#ffffff">{html.escape(label)}</font></span>'
        f'<h3 style="{STYLE["heading"]}">{html.escape(heading)}</h3>'
        f'<ul style="{STYLE["list"]}">{items}</ul></section>'
    )


def render_benefits_grid(points: list[str]) -> str:
    cards = "".join(
        '<div style="display:flex;gap:10px;align-items:flex-start;padding:12px 14px;border:1px solid currentColor;border-radius:10px;">'
        '<span style="display:inline-flex;align-items:center;justify-content:center;flex:0 0 22px;width:22px;height:22px;border-radius:999px;background:#16a34a!important;color:#ffffff!important;-webkit-text-fill-color:#ffffff!important;font-weight:800;line-height:1;">✓</span>'
        f'<span style="font-size:14px;line-height:1.45;color:inherit;">{html.escape(normalize(point).removesuffix("."))}</span></div>'
        for point in points
    )
    return (
        f'<section style="{STYLE["section"]}">'
        f'<span style="{pill_style("#16a34a")}"><font color="#ffffff">Dlaczego warto</font></span>'
        f'<h3 style="{STYLE["heading"]}">Najważniejsze korzyści tego wariantu</h3>'
        '<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:10px;margin-top:10px;">'
        f'{cards}</div></section>'
    )


def render_blog_guides(product: dict[str, Any]) -> str:
    guide = BLOG_GUIDES.get(product["categoryRoot"])
    if not guide:
        return ""
    cards = "".join(
        '<div style="font-family:inherit;min-height:190px;padding:18px;margin:0;background:none!important;background-color:transparent!important;border:1px solid currentColor;border-radius:12px;box-shadow:none!important;color:inherit;display:flex;flex-direction:column;">'
        f'<strong style="font-family:inherit;display:block;color:inherit!important;font-size:15px;line-height:1.35;margin-bottom:6px;">{html.escape(title)}</strong>'
        f'<small style="font-family:inherit;display:block;color:inherit!important;opacity:.78;font-size:13px;line-height:1.45;margin-bottom:14px;">{html.escape(description)}</small>'
        f'<a href="{html.escape(url, quote=True)}" style="font-family:inherit;margin-top:auto;color:inherit!important;font-size:13px;font-weight:700;text-decoration:underline;">Czytaj poradnik</a>'
        "</div>"
        for title, description, url in guide["items"]
    )
    return (
        f'<section style="{STYLE["section"]}">'
        '<div style="font-family:inherit;margin-bottom:18px;background:none!important;background-color:transparent!important;color:inherit;">'
        f'<span style="{pill_style("#e94b25")}"><font color="#ffffff">Praktyczne poradniki</font></span>'
        f'<h3 style="{STYLE["heading"]}">{html.escape(guide["heading"])}</h3>'
        f'<p style="{STYLE["paragraph"]}">{html.escape(guide["description"])}</p></div>'
        '<div style="font-family:inherit;display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:14px;background:none!important;background-color:transparent!important;color:inherit;align-items:stretch;">'
        f'{cards}</div></section>'
    )


def render_shoper(product: dict[str, Any], result: dict[str, Any]) -> str:
    identifier_labels = {"producent", "kod produktu", "kod producenta", "ean"}
    feature_specs = [item for item in product_specs(product) if item[0].lower() not in identifier_labels][:7]
    identifiers = [item for item in product_specs(product) if item[0].lower() in {"kod produktu", "kod producenta", "ean"}]

    def paragraph_points(points: list[str]) -> str:
        return "".join(f'<p>- {html.escape(normalize(point).removesuffix("."))}</p>' for point in points)

    intro = " ".join(normalize(value) for value in result["sections"][0]["paragraphs"])
    features = [f"{label}: {value}" for label, value in feature_specs]
    checks = list(result["selection_checks"]) + [f"{label}: {value}" for label, value in identifiers]
    return (
        "<section>"
        f'<h2>{html.escape(product["name"])}</h2>'
        f'<p>{html.escape(intro)}</p>'
        "<h3>Najważniejsze cechy:</h3>"
        f'{paragraph_points(features)}'
        "<h3>Dlaczego warto:</h3>"
        f'{paragraph_points(result["benefits"])}'
        "<h3>Gdzie użyć:</h3>"
        f'{paragraph_points(result["applications"])}'
        "<h3>Dobór bez pomyłki:</h3>"
        f'{paragraph_points(checks)}'
        "</section>"
    )


def render_channels(product: dict[str, Any], result: dict[str, Any]) -> dict[str, str]:
    leads = result["channel_leads"]
    model_code = product["manufacturerCode"] or product["code"]
    wapro_parts = [render_section(section) for section in result["sections"]]
    guides = render_blog_guides(product)
    if guides:
        wapro_parts.append(guides)
    return {
        "shoper": render_shoper(product, result),
        "wapro": "\n".join(wapro_parts),
        "tim": "\n".join(
            [
                render_lead("Opis techniczny", f"{model_code} — dane do doboru", leads["tim"]),
                render_section(result["sections"][1], label="Zastosowanie i dobór"),
                render_points_section(
                    "Parametry do zamówienia",
                    f"Co sprawdzić przed zakupem modelu {model_code}",
                    result["selection_checks"],
                ),
                render_specs(product),
                render_points_section(
                    "Uwagi instalacyjne",
                    "Przed podłączeniem i montażem",
                    result["installation_notes"],
                ),
            ]
        ),
        "allegro": "\n".join(
            [
                render_lead("Sprawdź przed zakupem", result["seo_title"], leads["allegro"], color="#16a34a"),
                render_benefits_grid(result["benefits"]),
                render_section(result["sections"][1], color="#16a34a", label="Gdzie użyć"),
                render_specs(product, color="#16a34a"),
                render_points_section(
                    "Dobór bez pomyłki",
                    "Co sprawdzić przed montażem",
                    result["selection_checks"] + result["installation_notes"],
                    color="#16a34a",
                ),
            ]
        ),
    }


def load_output(path: Path, model: str) -> dict[str, Any]:
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {
        "meta": {
            "model": model,
            "createdAt": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "updatedAt": "",
        },
        "products": {},
        "failures": {},
    }


def write_output(path: Path, output: dict[str, Any]) -> None:
    output["meta"]["updatedAt"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def apply_source_resolutions(
    products: list[dict[str, Any]],
    resolutions: dict[str, Any],
) -> list[dict[str, Any]]:
    resolved_products = []
    by_key = resolutions.get("products", {})
    for product in products:
        resolution = by_key.get(product["key"])
        if not resolution:
            resolved_products.append(product)
            continue
        resolved = {**product, "attributes": dict(product.get("attributes", {}))}
        if resolution.get("ignoreSourceDescription"):
            resolved["sourceDescription"] = ""
        resolved["attributes"].update(resolution.get("additionalAttributes", {}))
        resolved["_sourceResolution"] = resolution
        resolved_products.append(resolved)
    return resolved_products


def select_products(
    products: list[dict[str, Any]],
    overrides: dict[str, Any],
    output: dict[str, Any],
    args: argparse.Namespace,
) -> list[dict[str, Any]]:
    # A stable key-level guard prevents the same cloud record from being
    # processed twice if an upstream export ever repeats a row.
    selected = list({product["key"]: product for product in products}.values())
    if args.keys:
        keys = {value.strip() for value in args.keys.split(",") if value.strip()}
        selected = [
            product
            for product in selected
            if product["key"] in keys
            or product["ean"] in keys
            or product["code"] in keys
            or product["manufacturerCode"] in keys
        ]
    if args.category:
        needle = args.category.lower()
        selected = [product for product in selected if needle in product["category"].lower()]
    if args.family:
        selected = [product for product in selected if product_family(product) == args.family]
    if not args.include_manual:
        selected = [product for product in selected if product["key"] not in overrides.get("products", {})]
    if not args.include_research_needed:
        selected = [product for product in selected if not needs_source_research(product)]
    elif not args.include_source_conflicts:
        selected = [product for product in selected if not source_conflict_reasons(product)]
    if not args.force:
        selected = [product for product in selected if product["key"] not in output.get("products", {})]
    if args.per_root:
        per_root_counts: Counter[str] = Counter()
        sampled = []
        for product in selected:
            root = product["categoryRoot"]
            if per_root_counts[root] >= args.per_root:
                continue
            sampled.append(product)
            per_root_counts[root] += 1
        selected = sampled
    if args.limit:
        selected = selected[: args.limit]
    return selected


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--catalog", default="data/catalog.json")
    parser.add_argument("--manual-overrides", default="data/manual-overrides.json")
    parser.add_argument("--source-resolutions", default="data/source-resolutions.json")
    parser.add_argument("--output", default="data/seo-descriptions.json")
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--per-root", type=int, default=0)
    parser.add_argument("--keys", default="")
    parser.add_argument("--category", default="")
    parser.add_argument("--family", default="")
    parser.add_argument("--include-manual", action="store_true")
    parser.add_argument("--include-research-needed", action="store_true")
    parser.add_argument("--include-source-conflicts", action="store_true")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--max-retries", type=int, default=3)
    parser.add_argument("--timeout", type=int, default=300)
    parser.add_argument("--thinking", action="store_true")
    parser.add_argument("--rules-only", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--quiet", action="store_true")
    parser.add_argument("--checkpoint-every", type=int, default=50)
    parser.add_argument("--editorial-only", action="store_true")
    args = parser.parse_args()

    catalog = json.loads(Path(args.catalog).read_text(encoding="utf-8"))
    overrides = json.loads(Path(args.manual_overrides).read_text(encoding="utf-8"))
    resolutions_path = Path(args.source_resolutions)
    resolutions = json.loads(resolutions_path.read_text(encoding="utf-8")) if resolutions_path.exists() else {"products": {}}
    output_path = Path(args.output)
    generator_name = "rules-v1" if args.rules_only else args.model
    output = load_output(output_path, generator_name)
    products = apply_source_resolutions(catalog["products"], resolutions)
    by_family, by_root = build_example_index(products, overrides)
    selected = select_products(products, overrides, output, args)
    if not selected:
        print("Brak produktów do wygenerowania dla podanych filtrów.")
        return

    print(f"Generator: {generator_name}")
    print(f"Produkty do przetworzenia: {len(selected)}")
    if args.dry_run:
        product = selected[0]
        examples = select_examples(product, by_family, by_root)
        print(user_prompt(product, examples))
        return

    accepted_family_texts: dict[str, list[set[str]]] = defaultdict(list)
    selected_keys = {product["key"] for product in selected}
    used_seo_titles = {
        normalize(saved.get("seoTitle") or saved.get("editorial", {}).get("seo_title")).casefold()
        for saved_key, saved in output.get("products", {}).items()
        if saved_key not in selected_keys
    }
    used_meta_descriptions = {
        normalize(saved.get("metaDescription") or saved.get("editorial", {}).get("meta_description")).casefold()
        for saved_key, saved in output.get("products", {}).items()
        if saved_key not in selected_keys
    }
    for saved_key, saved in output.get("products", {}).items():
        if saved_key in selected_keys:
            continue
        accepted_family_texts[saved.get("family", "")].append(words(saved.get("canonicalText", saved.get("plainText", ""))))

    start_time = time.monotonic()
    for position, product in enumerate(selected, 1):
        family = product_family(product)
        examples = select_examples(product, by_family, by_root)
        retry_feedback = ""
        accepted = None
        last_result: dict[str, Any] | None = None
        last_errors: list[str] = []
        if not args.quiet:
            print(f"[{position}/{len(selected)}] {product['manufacturerCode'] or product['code']} — {product['name']}", flush=True)

        attempt_limit = 1 if args.rules_only else args.max_retries
        for attempt in range(1, attempt_limit + 1):
            seed = int(hashlib.sha256(f"{product['key']}:{attempt}".encode()).hexdigest()[:8], 16)
            if args.rules_only:
                result = general_editorial(product)
            else:
                try:
                    result = call_ollama(
                        args.model,
                        user_prompt(product, examples, retry_feedback),
                        seed,
                        args.timeout,
                        args.thinking,
                    )
                except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, KeyError) as error:
                    last_errors = [f"Błąd modelu: {error}"]
                    retry_feedback = "\n".join(last_errors)
                    if not args.quiet:
                        print(f"  próba {attempt}: {last_errors[0]}", flush=True)
                    continue

            result["seo_title"] = unique_seo_title(result.get("seo_title", ""), product, used_seo_titles)
            result["meta_description"] = unique_meta_description(
                result.get("meta_description", ""), product, used_meta_descriptions
            )
            last_result = result
            errors, metrics = validate_result(
                product,
                result,
                accepted_family_texts[family],
                family_similarity_limit=0.995 if args.rules_only else 0.64,
                lead_similarity_limit=0.90 if args.rules_only else 0.48,
            )
            if not errors:
                channels = render_channels(product, result)
                canonical_text = normalize(
                    " ".join(
                        normalize(f"{section['heading']} {' '.join(section['paragraphs'])}")
                        for section in result["sections"]
                    )
                )
                plain_text = normalize(" ".join(strip_html(value) for value in channels.values()))
                accepted = {
                    "family": family,
                    "model": generator_name,
                    "generatedAt": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                    "seoTitle": normalize(result["seo_title"]),
                    "metaDescription": normalize(result["meta_description"]),
                    "editorial": result,
                    "channels": channels,
                    "canonicalText": canonical_text,
                    "plainText": plain_text,
                    "metrics": metrics,
                    "exampleKeys": [example["key"] for example in examples],
                }
                if product.get("_sourceResolution"):
                    accepted["sourceResolution"] = product["_sourceResolution"]
                if args.editorial_only:
                    accepted = {
                        key: value
                        for key, value in accepted.items()
                        if key
                        in {
                            "family",
                            "model",
                            "generatedAt",
                            "seoTitle",
                            "metaDescription",
                            "editorial",
                            "canonicalText",
                            "metrics",
                            "sourceResolution",
                        }
                    }
                if not args.quiet:
                    print(f"  zaakceptowano: wynik {metrics['score']}/100, {metrics['narrationLength']} znaków", flush=True)
                break

            last_errors = errors
            retry_feedback = "\n".join(f"- {error}" for error in errors)
            if not args.quiet:
                print(f"  próba {attempt}: odrzucono — {'; '.join(errors[:4])}", flush=True)

        if accepted:
            output["products"][product["key"]] = accepted
            output.get("failures", {}).pop(product["key"], None)
            accepted_family_texts[family].append(words(accepted["canonicalText"]))
            used_seo_titles.add(accepted["seoTitle"].casefold())
            used_meta_descriptions.add(accepted["metaDescription"].casefold())
        else:
            output.get("products", {}).pop(product["key"], None)
            output.setdefault("failures", {})[product["key"]] = {
                "name": product["name"],
                "family": family,
                "errors": last_errors,
                "editorialAttempt": last_result,
                "attemptedAt": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            }
        checkpoint_every = max(1, args.checkpoint_every)
        if position % checkpoint_every == 0:
            write_output(output_path, output)

    elapsed = time.monotonic() - start_time
    write_output(output_path, output)
    print(f"Gotowe: {len(output['products'])} zaakceptowanych, {len(output.get('failures', {}))} odrzuconych.")
    print(f"Czas tej partii: {elapsed / 60:.1f} min.")
    print(f"Plik: {output_path}")


if __name__ == "__main__":
    main()
