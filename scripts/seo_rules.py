"""Fact-locked editorial rules for Prescot product families.

The module does not invent specifications.  Every number and product property
comes from the normalized catalog record.  Family rules only explain how a
confirmed field affects selection, ordering or installation.
"""

from __future__ import annotations

import re
from typing import Any


ADMIN_FIELDS = {
    "producent odpowiedzialny",
    "podmiot odpowiedzialny",
    "nazwa galerii",
    "informacje o bezpieczeństwie",
}
# Nazwy pól w surowym eksporcie. Publicznie pokazujemy wyłącznie własny
# `product["code"]` pod nazwą „Indeks handlowy”.
IDENTITY_FIELDS = {"producent", "kod produktu", "kod producenta", "ean"}


def normalize(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()


def source_specs(product: dict[str, Any]) -> list[tuple[str, str]]:
    specs = []
    seen = set()
    for raw_line in str(product.get("sourceDescription", "")).splitlines():
        line = normalize(raw_line)
        match = re.match(r"^([^:]{2,42}):\s*(.{1,100})$", line)
        if not match:
            continue
        label, value = (normalize(part) for part in match.groups())
        label = re.sub(r"^[•*\-–—]+\s*", "", label)
        # Some source descriptions put a hard fact in the pseudo-label and a
        # marketing explanation after the colon, e.g. "Moc 1W: ...".  Keep
        # the fact instead of treating the promotional tail as a parameter.
        inline_value = re.search(
            r"(?i)\b\d+(?:[.,]\d+)?\s*(?:mAh|lm|W|V|A|mA|mm|cm|m|h|%|miesiące|lat)\s*$",
            label,
        )
        if inline_value:
            value = normalize(inline_value.group(0))
            label = normalize(label[: inline_value.start()]).rstrip(" -–—")
        material_inline = re.match(r"(?i)^materiał\s+(.+)$", label)
        if material_inline:
            label = "Materiał"
            value = normalize(material_inline.group(1))
        if re.match(r"(?i)^w zestawie\b", label):
            continue
        value = re.sub(r"(?i)\bidealn(?:e|a|y) do\b", "przeznaczone do", value).rstrip(" ,;")
        if re.search(r"(?i)\b(?:idealn\w*|doskonał\w*|najwyższ\w*|bez utraty jakości|duże obwody|elimin\w* cieni|wydajne połączenie)\b", value):
            continue
        key = label.casefold()
        if key in seen or key in {"specyfikacja techniczna", "dane techniczne"} or "więcej informacji" in key:
            continue
        if re.search(r"(?i)https?://|www\.|kliknij tutaj", value):
            continue
        seen.add(key)
        specs.append((label[:1].upper() + label[1:], value))
    return specs


def source_sentences(product: dict[str, Any], limit: int = 3) -> list[str]:
    text = str(product.get("sourceDescription", ""))
    text = re.sub(r"\n(?=[a-ząćęłńóśźż])", " ", text)
    text = re.sub(r"\n+", ". ", text)
    text = re.sub(r"(?<=[.!?])(?=[A-ZĄĆĘŁŃÓŚŹŻ])", " ", text)
    text = re.sub(r"\s+([,.;:])", r"\1", normalize(text))
    sentences = []
    for sentence in re.split(r"(?<=[.!?])\s+", text):
        sentence = normalize(sentence).strip(" -")
        if len(sentence) < 35 or re.match(r"(?i)^(?:specyfikacja|dane techniczne)\s*:?$", sentence):
            continue
        sentence = re.sub(r"(?i)\bidealnie nadaje się do\b", "służy do", sentence)
        sentence = re.sub(r"(?i)\bidealnie nadaje się dla\b", "jest przeznaczony dla", sentence)
        sentence = re.sub(r"(?i)\bidealn(?:y|a|e) produkt do\b", "produkt do", sentence)
        sentence = re.sub(r"(?i)\bidealn(?:e|a|y) dopasowanie do\b", "dopasowanie do", sentence)
        sentence = re.sub(r"(?i)\bidealn(?:y|a|e) do\b", "przeznaczone do", sentence)
        sentence = re.sub(r"(?i),?\s*co czyni (?:go|ją|je) idealn\w* do .*?$", ".", sentence)
        sentence = re.sub(r"(?i)\bnp\.\s*", "na przykład ", sentence)
        sentence = re.sub(r"(?i)\bszerokie zastosowanie\b", "określone zastosowania", sentence)
        sentences.append(sentence)
        if len(sentences) >= limit:
            break
    return sentences


def source_fragments(product: dict[str, Any], limit: int = 4) -> list[str]:
    """Return short, usable facts from list-like source descriptions."""
    fragments = []
    for raw_line in str(product.get("sourceDescription", "")).splitlines():
        line = normalize(raw_line).strip(" •*\t-–—")
        if not line or re.search(r"(?i)więcej informacji|kliknij tutaj|https?://|www\.", line):
            continue
        if re.match(r"(?i)^(?:specyfikacja|dane|parametry)(?: techniczne)?\s*[:;]?$", line):
            continue
        line = re.sub(r"(?i)^doskonale rozprasza", "Rozprasza", line)
        line = re.sub(r"(?i)^estetyczn(?:a|y|e)\s+", "", line)
        line = re.sub(r"(?i)\bidealn(?:e|a|y) dopasowanie do\b", "Dopasowanie do", line)
        line = re.sub(r"(?i)\bidealn(?:y|a|e) do\b", "przeznaczone do", line)
        line = re.sub(r"(?i)która jest bardzo łatwa w instalacji\s*[–-]\s*na klik", "montowanej na klik", line)
        fragments.append(line.removesuffix("."))
        if len(fragments) >= limit:
            break
    return fragments


def attr(product: dict[str, Any], *labels: str) -> str:
    lookup = {
        normalize(label).replace("_", " ").casefold(): normalize(value)
        for label, value in product["attributes"].items()
    }
    for label in labels:
        value = lookup.get(normalize(label).replace("_", " ").casefold(), "")
        if value:
            return value
    source_lookup = {label.casefold(): value for label, value in source_specs(product)}
    for label in labels:
        value = source_lookup.get(normalize(label).replace("_", " ").casefold(), "")
        if value:
            return value
    return ""


def public_specs(product: dict[str, Any], include_identity: bool = False) -> list[tuple[str, str]]:
    specs = []
    seen = set()
    for raw_label, raw_value in product["attributes"].items():
        label = normalize(raw_label).replace("_", " ")
        value = normalize(raw_value)
        key = label.casefold()
        if not value or value == "-" or key in ADMIN_FIELDS or key in seen:
            continue
        if not include_identity and key in IDENTITY_FIELDS:
            continue
        seen.add(key)
        specs.append((label, value))
    for label, value in source_specs(product):
        key = label.casefold()
        if key in seen or key in IDENTITY_FIELDS:
            continue
        seen.add(key)
        specs.append((label, value))
    return specs


def preferred_specs(product: dict[str, Any], labels: list[str], limit: int = 7) -> list[tuple[str, str]]:
    chosen = []
    used = set()
    for label in labels:
        if label.casefold() in used:
            continue
        value = attr(product, label)
        if value:
            chosen.append((label, value))
            used.add(label.casefold())
    for label, value in public_specs(product):
        if label.casefold() not in used:
            chosen.append((label, value))
            used.add(label.casefold())
        if len(chosen) >= limit:
            break
    return chosen[:limit]


def join_polish(items: list[str]) -> str:
    items = [normalize(item).removesuffix(".") for item in items if normalize(item)]
    if not items:
        return ""
    if len(items) == 1:
        return items[0]
    return ", ".join(items[:-1]) + " oraz " + items[-1]


def sentence_case(value: str) -> str:
    value = normalize(value)
    return value[:1].upper() + value[1:] if value else value


def exact_spec_sentence(specs: list[tuple[str, str]]) -> str:
    if not specs:
        return ""
    return sentence_case("; ".join(f"{label.lower()}: {value}" for label, value in specs)) + "."


def title_for(product: dict[str, Any]) -> str:
    name = normalize(product["name"]).replace(" | ", " – ")
    code = normalize(product["code"])
    title = name
    if len(title) < 45 and code and code.casefold() not in title.casefold():
        title = f"{title} – indeks handlowy {code}"
    if len(title) < 40:
        title = f"{title} – indeks handlowy {code}"
    if len(title) < 40 and product.get("ean"):
        title = f"{title} | EAN {product['ean']}"
    if len(title) > 70:
        shortened = re.sub(r"\s*\([^)]*\)\s*$", "", title)
        words = shortened.split()
        while len(" ".join(words)) > 70 and len(words) > 4:
            words.pop()
        title = " ".join(words).rstrip(" ,;–-")
    return title


def meta_for(product: dict[str, Any], specs: list[tuple[str, str]]) -> str:
    name = normalize(product["name"])
    code = normalize(product["code"])
    ean = normalize(product["ean"])
    facts = [f"{label.lower()} {value}" for label, value in specs[:5]]
    prefix = f"{name.rstrip('.')}. "
    suffixes = []
    if facts:
        suffixes.append(sentence_case(join_polish(facts)) + ".")
    identity = []
    if code:
        identity.append(f"indeks handlowy {code}")
    if identity:
        suffixes.append(sentence_case(join_polish(identity)) + ".")
    if ean:
        suffixes.append(f"EAN {ean}.")

    meta = prefix
    for suffix in suffixes:
        if len(meta + suffix) <= 166 or len(meta) < 120:
            meta += suffix + " "
    meta = normalize(meta)
    if len(meta) < 120:
        exact_additions = [
            f"Indeks handlowy: {code}." if code and code.casefold() not in meta.casefold() else "",
            f"EAN: {ean}." if ean and ean not in meta else "",
            f"Typ: {product['category'].split('/')[-1]}." if product.get("category") else "",
        ]
        for addition in exact_additions:
            if addition and len(meta) < 120 and len(f"{meta} {addition}") <= 170:
                meta = f"{meta} {addition}"
    if len(meta) < 120 and code:
        addition = f"Wariant identyfikowany indeksem handlowym {code}."
        if len(f"{meta} {addition}") <= 170:
            meta = f"{meta} {addition}"
    if len(meta) < 120:
        addition = "Przed zakupem porównaj indeks handlowy i EAN."
        if len(f"{meta} {addition}") <= 170:
            meta = f"{meta} {addition}"
    if len(meta) > 170:
        compact_name = title_for(product)
        meta = f"{compact_name.rstrip('.')}. {sentence_case(join_polish(facts[:4]))}."
        if len(meta) < 120 and code:
            meta += f" Indeks handlowy {code}."
    if len(meta) > 170:
        cut = meta[:167].rsplit(" ", 1)[0].rstrip(" ,;:-")
        meta = cut + "."
    if len(meta) < 120:
        addition = "Przed zakupem porównaj indeks handlowy i EAN."
        if len(f"{meta} {addition}") <= 170:
            meta = f"{meta} {addition}"
    meta = re.sub(r"(?<=\d)\.{2,3}(?=\d)", "–", meta)
    meta = re.sub(r"\.{2,}", ".", meta)
    if len(meta) < 120:
        addition = "Przed zakupem porównaj indeks handlowy i EAN."
        if len(f"{meta} {addition}") <= 170:
            meta = f"{meta} {addition}"
    return meta


def classify_editorial_rule(product: dict[str, Any]) -> str:
    root = product["categoryRoot"]
    path = f"{product['category']} {product['name']}".casefold()
    name = product["name"].casefold()
    if "czujnik" in path or "detektor" in path:
        return "sensor"
    if any(term in path for term in ("statecznik", "układ zapłonowy", "starter")) or "oprawka" in name:
        return "technical_component"
    electrical_roots = {"Osprzęt elektryczny", "Outlet"}
    electrical_series = root == "Osprzęt elektryczny" or (root == "Outlet" and "logo" in path)
    if root in electrical_roots and any(term in path for term in ("rozdzielnic", "skrzynk")):
        return "distribution_board"
    if electrical_series and "ramk" in path:
        return "electrical_frame"
    if electrical_series and (
        any(term in path for term in ("wyłącznik", "włącznik", "przycisk"))
        or ("łącznik" in path and not any(term in path for term in ("łącznik kątowy", "łącznik prosty", "szynoprzewod")))
    ):
        return "electrical_switch"
    if electrical_series and "gniazd" in path:
        return "electrical_socket"
    if root == "Outlet" and any(term in path for term in ("oprawa", "projektor", "plafon", "naświetlacz")):
        return "luminaire"
    if root == "Outlet":
        if "taśm" in path:
            return "tape"
        if "zasilacz" in path:
            return "power"
        if any(term in path for term in ("złącz", "wtyk", "gniazd", "przewód")):
            return "accessory"
        if "kondensator" in path:
            return "technical_component"
    if root == "Taśmy LED":
        return "tape"
    if root == "Baterie":
        return "battery"
    if root == "Akcesoria do świetlówek i lamp wyładowczych":
        return "technical_component"
    if root == "Profile do taśm LED":
        if re.match(r"\s*(?:osłona|klosz)\b", name):
            return "profile_cover"
        if any(
            term in name
            for term in (
                "zaślepk",
                "uchwyt",
                "mocownik",
                "sprężyn",
                "zawieszk",
                "linka",
                "pręt",
                "wysięgnik",
                "zestaw mocowa",
                "wkładka",
                "łącznik",
                "włącznik",
                "maskownic",
                "uszczelk",
                "blokad",
            )
        ):
            return "profile_accessory"
        return "profile"
    if root == "Zasilacze LED":
        return "power"
    if root == "Sterowniki LED":
        if "akcesoria" in path or any(term in name for term in ("puszka", "uchwyt do pilota", "adapter do sterownika")):
            return "control_accessory"
        if "/piloty" in product["category"].casefold() or name.startswith("pilot ") or "/panele dotykowe" in product["category"].casefold() or name.startswith("panel "):
            return "control_input"
        return "controller"
    if root == "Akcesoria do zasilaczy i taśm LED":
        return "accessory"
    if root == "Candor" and "akcesoria" in path:
        return "accessory"
    if root == "Moduły LED":
        return "module"
    if root == "Zestawy LED":
        return "kit"
    if root == "Oświetlenie świąteczne":
        return "festive"
    if root == "Oświetlenie dekoracyjne" and "girlanda" in path:
        return "festive"
    if root == "Oświetlenie dekoracyjne" and any(term in path for term in ("budzik", "marys lampka")):
        return "decorative_device"
    if root in {"Oprawy LED", "Oprawy oświetleniowe", "Oprawy LED KLUŚ Design", "Oprawy LED Light Prestige", "Candor", "Oświetlenie dekoracyjne"}:
        return "luminaire"
    if root in {"Żarówki LED", "Żarówki standardowe", "Świetlówki LED", "Świetlówki"}:
        return "light_source"
    if root == "Osprzęt elektryczny":
        return "electrical"
    return "fallback"


def general_editorial(product: dict[str, Any]) -> dict[str, Any]:
    rule_name = classify_editorial_rule(product)
    rules = {
        "sensor": sensor_editorial,
        "technical_component": technical_component_editorial,
        "tape": tape_editorial,
        "battery": battery_editorial,
        "profile": profile_editorial,
        "profile_cover": profile_cover_editorial,
        "profile_accessory": profile_accessory_editorial,
        "power": power_editorial,
        "controller": controller_editorial,
        "control_input": control_input_editorial,
        "control_accessory": control_accessory_editorial,
        "accessory": accessory_editorial,
        "module": module_editorial,
        "kit": kit_editorial,
        "festive": festive_editorial,
        "decorative_device": decorative_device_editorial,
        "luminaire": luminaire_editorial,
        "light_source": light_source_editorial,
        "electrical": electrical_editorial,
        "distribution_board": distribution_board_editorial,
        "electrical_frame": electrical_frame_editorial,
        "electrical_switch": electrical_switch_editorial,
        "electrical_socket": electrical_socket_editorial,
        "fallback": fallback_editorial,
    }
    result = rules[rule_name](product)
    result["rule_family"] = rule_name
    return result


def finish(
    product: dict[str, Any],
    sections: list[dict[str, Any]],
    benefits: list[str],
    applications: list[str],
    checks: list[str],
    notes: list[str],
    specs: list[tuple[str, str]],
) -> dict[str, Any]:
    code = product["code"]
    title = title_for(product)
    meta = meta_for(product, specs)
    code = normalize(code)

    for section in sections:
        if len(normalize(section["heading"])) < 12:
            section["heading"] = f"{normalize(section['heading'])} — {product['category'].split('/')[-1]}"
        source_paragraphs = [
            re.sub(
                r"\.{2,}",
                ".",
                re.sub(r"(?<=\d)\.{2,3}(?=\d)", "–", re.sub(r"\s+([,.;:])", r"\1", normalize(paragraph))),
            )
            for paragraph in section["paragraphs"]
            if normalize(paragraph)
        ]
        polished_paragraphs = []
        pending = ""
        for paragraph in source_paragraphs:
            if pending:
                paragraph = f"{pending.removesuffix('.')} — {paragraph[:1].lower()}{paragraph[1:]}"
                pending = ""
            if len(paragraph) < 45 and not polished_paragraphs:
                pending = paragraph
            elif len(paragraph) < 45:
                polished_paragraphs[-1] = f"{polished_paragraphs[-1]} {paragraph}"
            else:
                polished_paragraphs.append(paragraph)
        if pending:
            if polished_paragraphs:
                polished_paragraphs[-1] = f"{pending} {polished_paragraphs[-1]}"
            else:
                polished_paragraphs.append(pending)
        section["paragraphs"] = polished_paragraphs

    benefits = list(dict.fromkeys(normalize(x).removesuffix(".") for x in benefits if normalize(x)))[:4]
    applications = list(dict.fromkeys(normalize(x).removesuffix(".") for x in applications if normalize(x)))[:4]
    checks = list(dict.fromkeys(normalize(x).removesuffix(".") for x in checks if normalize(x)))[:4]
    notes = list(dict.fromkeys(normalize(x).removesuffix(".") for x in notes if normalize(x)))[:3]

    # Rich records normally supply these naturally.  Conservative exact-field
    # fallbacks keep the schema complete without inventing another use case.
    if len(benefits) < 2:
        benefits.extend(f"{label}: {value}" for label, value in specs if f"{label}: {value}" not in benefits)
    if len(benefits) < 2:
        benefits.extend([f"Typ produktu: {product['category'].split('/')[-1]}", f"Kod modelu: {code}"])
    if len(applications) < 2:
        applications.extend([f"Dobór według kategorii: {product['category'].split('/')[-1]}", f"Identyfikacja wariantu po kodzie {code}"])
    if len(checks) < 2:
        checks.extend(f"Porównaj parametr „{label}”: {value}" for label, value in specs)
    if len(checks) < 2:
        checks.extend([f"Porównaj pełny indeks handlowy {code}", f"Zweryfikuj EAN {product['ean']} przed zamówieniem"])
    if not notes:
        notes.append("Przed montażem porównaj parametry wszystkich łączonych elementów")

    benefits = list(dict.fromkeys(benefits))
    applications = list(dict.fromkeys(applications))
    checks = list(dict.fromkeys(checks))
    notes = list(dict.fromkeys(notes))

    # The same confirmed parameter may be useful as both a feature and an
    # ordering check.  Keep the fact, but make the latter an instruction so
    # the channel lists do not repeat verbatim.
    benefit_keys = {value.casefold() for value in benefits}
    checks = [
        f"Sprawdź zgodność — {value[:1].lower()}{value[1:]}"
        if value.casefold() in benefit_keys
        else value
        for value in checks
    ]

    lead_facts = exact_spec_sentence(specs[:3]) if specs else f"Indeks handlowy: {code}."
    wapro_lead = normalize(f"{title.rstrip('.')}. Najważniejsze dane: {benefits[0].lower()} oraz {benefits[1].lower()}. Indeks handlowy: {code}.")
    tim_lead = normalize(f"Model {code}. {lead_facts} Dane służą do porównania wariantu przed zamówieniem. EAN: {product['ean']}.")
    first_check = re.sub(r"(?i)^(?:przed zakupem )?sprawdź(?: przed zakupem)?:\s*", "", checks[0])
    allegro_lead = normalize(f"{applications[0]}. Przed zakupem sprawdź: {first_check.lower()}. Indeks handlowy: {code}.")
    return {
        "seo_title": title,
        "meta_description": meta,
        "sections": sections,
        "benefits": benefits[:4],
        "applications": applications[:4],
        "selection_checks": checks[:4],
        "installation_notes": notes[:3],
        "channel_leads": {
            "wapro": wapro_lead,
            "tim": tim_lead,
            "allegro": allegro_lead,
        },
    }


def first_number(value: str) -> float | None:
    match = re.search(r"\d+(?:[.,]\d+)?", normalize(value))
    return float(match.group(0).replace(",", ".")) if match else None


def light_guidance(color: str, brightness: str = "") -> str:
    lower = normalize(color).casefold()
    level = first_number(brightness)
    if "ciep" in lower or ("k" in lower and (first_number(lower) or 9999) < 3300):
        color_use = "Ciepła barwa wspiera spokojny charakter salonu, restauracji, hotelu oraz aranżacji z drewnem i tkaninami"
    elif "neutral" in lower or ("k" in lower and 3300 <= (first_number(lower) or 0) <= 5000):
        color_use = "Neutralna biel pasuje do kuchni, biura, garderoby i oświetlenia blatów, gdzie światło nie powinno wyraźnie ocieplać ani ochładzać kolorów"
    elif "zim" in lower or ("k" in lower and (first_number(lower) or 0) > 5000):
        color_use = "Chłodna biel sprawdza się w oświetleniu technicznym, roboczym i ekspozycyjnym, gdy ważny jest wyraźny, chłodny efekt"
    elif "rgb" in lower or "cct" in lower:
        color_use = "System barwy wybiera się do instalacji, w której kolor lub odcień bieli ma być regulowany przez zgodny sterownik"
    elif lower:
        color_use = f"Barwa {color} jest przeznaczona przede wszystkim do światła dekoracyjnego, oznaczeń i kolorystycznych akcentów"
    else:
        color_use = "Charakter światła należy dobrać do funkcji miejsca i barwy wskazanej w pełnej nazwie wariantu"

    if level is None:
        return color_use + "."
    if level < 500:
        level_use = "Taki poziom strumienia służy głównie do orientacji, podświetlenia cokołu, półki lub małej ekspozycji"
    elif level < 1000:
        level_use = "Ten poziom strumienia pasuje do oświetlenia akcentowego i pomocniczego"
    elif level < 1600:
        level_use = "Ten poziom strumienia pozwala planować wyraźne światło liniowe i oświetlenie robocze po sprawdzeniu całej instalacji"
    else:
        level_use = "Wysoki strumień wymaga świadomego doboru profilu, odprowadzania ciepła i mocy zasilacza"
    return f"{color_use}. {level_use}."


def light_application(color: str) -> str:
    lower = normalize(color).casefold()
    if "ciep" in lower:
        return "Salony, restauracje, hotele i aranżacje z drewnem"
    if "neutral" in lower:
        return "Kuchnie, biura, garderoby i oświetlenie blatów"
    if "zim" in lower:
        return "Strefy robocze, techniczne i ekspozycyjne"
    if "rgb" in lower or "cct" in lower:
        return "Instalacje z regulacją koloru lub odcienia bieli"
    if lower:
        return f"Dekoracyjne akcenty w barwie {color}"
    return "Oświetlenie dobrane do barwy wskazanej dla wariantu"


def ingress_guidance(ip: str) -> str:
    match = re.search(r"(?i)IP\s*(\d{2})", normalize(ip))
    if not match:
        return "Warunki pracy trzeba dobrać do klasy szczelności zapisanej dla konkretnego wariantu."
    level = int(match.group(1))
    if level < 44:
        return f"Oznaczenie {normalize(ip)} kieruje ten wariant do suchych, osłoniętych miejsc wewnątrz pomieszczeń."
    if level >= 65:
        return f"Klasa {normalize(ip)} pozwala brać pod uwagę miejsca narażone na pył i strugi wody, pod warunkiem poprawnego zabezpieczenia połączeń."
    return f"Klasa {normalize(ip)} daje podwyższoną ochronę, ale sposób montażu i uszczelnienie połączeń nadal trzeba dopasować do miejsca pracy."


def tape_editorial(product: dict[str, Any]) -> dict[str, Any]:
    name = product["name"]
    lower = name.casefold()
    source = normalize(product.get("sourceDescription", ""))
    code = product["code"]

    def found(pattern: str, *values: str) -> str:
        for value in values:
            match = re.search(pattern, value or "", re.I)
            if match:
                return normalize(match.group(1) if match.lastindex else match.group(0))
        return ""

    color_name = found(
        r"\b(biała\s+(?:ciepła|neutralna|zimna)|ciepła\s+biała|neutralna\s+biała|zimna\s+biała|dzienna\s+biała|czerwona|zielona|niebieska|żółta|pomarańczowa|różowa|RGB\+?CCT|RGBCCT|RGBW|RGB|CCT)\b",
        name,
    )
    cct = found(r"\b(\d{4,5}(?:[–-]\d{4,5})?\s*K)\b", name, source).replace(" ", "")
    color = attr(product, "Barwa światła") or " ".join(x for x in [color_name, cct] if x)
    voltage = attr(product, "Napięcie wejściowe", "Napięcie") or found(r"\b(\d+(?:[.,]\d+)?\s*V)\b", name)
    power = attr(product, "Moc") or found(r"\b(\d+(?:[.,]\d+)?\s*W/m)\b", name, source)
    brightness = attr(product, "Jasność") or found(r"\b(\d+(?:[.,]\d+)?\s*lm/m)\b", name, source)
    cri = attr(product, "CRI") or found(r"\b(CRI\s*>?\s*\d+)\b", name, source)
    leds = attr(product, "Ilość diod") or found(r"\b(\d+\s*(?:led|diod)/m)\b", name, source)
    if re.fullmatch(r"\d+\s*/m", leds, re.I):
        leds = leds.replace("/m", " LED/m")
    cut = attr(product, "Moduł cięcia") or found(r"(?:moduł(?:em)? cięcia|cięci[ae] co)\s*(\d+(?:[.,]\d+)?\s*mm)", source)
    ip = attr(product, "Klasa szczelności") or found(r"\b(IP\s*\d{2})\b", name, source)
    width = attr(product, "Szerokość taśmy") or found(r"\b(\d+(?:[.,]\d+)?mm)\b", name)
    diode = attr(product, "Typ diody") or found(r"\b((?:SMD|COB)\s*\d{3,4})\b", name, source)
    sold_by_meter = "taśma na metry" in lower or "cięta na metry" in lower
    roll = attr(product, "Rolka", "Wymiar") or found(r"(?:rolka(?:\s+o\s+długości)?\s*)?(\d+(?:[.,]\d+)?\s*m)(?:\b|\s*$)", name, source)
    format_label = "taśma cięta na metry" if sold_by_meter else f"rolka {roll}" if roll else "wariant długości wskazany w nazwie"

    if "s-shape" in lower or "s shape" in lower:
        family = "s_shape"
        series_label = "Taśmy LED S-Shape"
        first_heading = "Linia światła prowadzona po łukach i nieregularnych kształtach"
        first_text = f"Model {code} ma elastyczny laminat S-Shape przeznaczony do łuków, liter, zaokrągleń i dekoracyjnych linii światła. Format produktu to {format_label}."
    elif "wcob" in lower:
        family = "wcob"
        series_label = f"Seria WCOB{f' {ip}' if ip else ''}"
        first_heading = "Biała powierzchnia taśmy i ciągła linia światła WCOB"
        first_text = f"Model {code} wykorzystuje technologię White COB: po wyłączeniu widoczna jest biała powierzchnia zamiast intensywnie żółtego paska luminoforu. {f'Układ {leds} tworzy równą linię światła. ' if leds else ''}Format handlowy: {format_label}."
    elif "cob" in lower:
        family = "cob"
        series_label = "Seria Premium COB" if "premium" in lower else "Taśmy LED COB"
        first_heading = f"Ciągła linia światła w modelu {code}"
        first_text = f"Taśma COB {code} tworzy jednolitą linię bez wyraźnych punktów świetlnych. {f'Zasilanie {voltage} ułatwia planowanie odcinków. ' if voltage else ''}Format produktu: {format_label}."
    elif any(token in lower for token in ("rgb", "cct", "dual white")):
        family = "multichannel"
        series_label = "Taśmy LED wielokanałowe"
        first_heading = f"Sterowana barwa światła w wariancie {code}"
        first_text = f"Model {code} jest taśmą {color_name or cct or 'wielokanałową'} i wymaga sterownika zgodnego z układem kanałów. Napięcie zasilania to {voltage or 'wartość wskazana dla modelu'}, a format produktu to {format_label}."
    else:
        family = "smd"
        series = next((value for value in ("Delux Pro", "Delux", "Premium+", "Premium", "Economic") if value.casefold() in lower), "LED")
        series_label = f"Seria {series}"
        first_heading = f"Taśma {series} w wariancie {code}"
        first_text = f"Model {code} to taśma {diode or 'LED'} o zasilaniu {voltage or 'określonym dla wariantu'}. {f'Gęstość {leds} wpływa na rozstaw punktów światła. ' if leds else ''}Format produktu: {format_label}."

    brightness_heading = (
        f"{brightness}: wyraźne światło liniowe do zadań użytkowych" if brightness and (first_number(brightness) or 0) >= 1000
        else f"{brightness}: światło pomocnicze i akcentowe" if brightness
        else f"Moc {power} i przeznaczenie wariantu {code}" if power
        else f"Przeznaczenie modelu {code}"
    )
    brightness_text = (
        f"Strumień {brightness}{f' przy mocy {power}' if power else ''} pozwala dobrać model do roli światła, a nie tylko do wyglądu taśmy. "
        f"{light_guidance('', brightness).split('.', 1)[-1].strip()}"
        if brightness
        else f"Dobierając model {code}, porównaj moc na metr, gęstość diod oraz rolę planowanego oświetlenia. Parametry tego wariantu identyfikuje pełna nazwa produktu."
    )
    color_heading = (
        f"{color}: barwa dobrana do konkretnego wnętrza" if color
        else f"Miejsce użycia i format {format_label}"
    )
    color_text = light_guidance(color) if color else f"Model {code} stosuj w oświetleniu liniowym po dobraniu zasilacza, profilu i warunków pracy do danych tego wariantu."
    format_text = (
        "Wariant cięty na metry pozwala zamówić długość dopasowaną do projektu; liczbę odcinków i punktów zasilania trzeba rozplanować przed montażem."
        if sold_by_meter
        else f"{sentence_case(format_label)} określa ilość materiału w opakowaniu. Odcinki dziel wyłącznie w oznaczonych miejscach{f' co {cut}' if cut else ''}."
    )

    if family == "s_shape":
        second = {"label": color_name or cct or "Barwa światła", "heading": color_heading, "paragraphs": [color_text]}
        third = {"label": brightness or "Zastosowanie", "heading": brightness_heading, "paragraphs": [brightness_text, format_text]}
    elif family == "wcob":
        second = {"label": "Gdzie sprawdzi się najlepiej", "heading": color_heading, "paragraphs": [color_text, f"{ingress_guidance(ip)} {format_text}" if ip else format_text]}
        third = {
            "label": "Parametry i montaż",
            "heading": "Zasilanie, cięcie i odprowadzanie ciepła",
            "paragraphs": [
                f"Napięcie {voltage or 'dobierz według modelu'}{f', moc {power}' if power else ''}{f', szerokość {width}' if width else ''}{f' i moduł cięcia {cut}' if cut else ''} wyznaczają sposób kompletacji instalacji.",
                f"Profil oraz zasilacz dobierz do mocy i długości planowanego odcinka. {format_text}",
            ],
        }
    elif family == "cob" and voltage == "48V":
        second = {"label": "Barwa światła", "heading": color_heading, "paragraphs": [color_text]}
        third = {"label": "Zastosowanie", "heading": f"{sentence_case(format_label)} w systemie 48V", "paragraphs": [brightness_text, format_text]}
    else:
        second = {"label": brightness or "Przeznaczenie modelu", "heading": brightness_heading, "paragraphs": [brightness_text]}
        third = {"label": "Barwa i miejsce użycia", "heading": color_heading, "paragraphs": [color_text, f"{format_text} {ingress_guidance(ip)}" if ip else format_text]}

    sections = [
        {"label": series_label, "heading": first_heading, "paragraphs": [first_text]},
        second,
        third,
    ]
    specs = [(label, value) for label, value in [
        ("Barwa światła", color), ("Napięcie", voltage), ("Moc", power), ("Jasność", brightness),
        ("CRI", cri), ("Ilość diod", leds), ("Moduł cięcia", cut), ("Klasa szczelności", ip),
        ("Szerokość taśmy", width), ("Typ diody", diode), ("Format", format_label),
    ] if value]
    benefits = [value for value in [
        f"Strumień {brightness}{f' przy mocy {power}' if power else ''}" if brightness else "",
        f"Zasilanie {voltage}" if voltage else "",
        f"Szerokość taśmy {width}" if width else "",
        f"Moduł cięcia {cut}" if cut else "",
    ] if value]
    applications = [
        light_application(color) if color else "Oświetlenie liniowe dobrane do parametrów wariantu",
        "Łuki, litery i nieregularne linie" if family == "s_shape" else "Montaż w profilu aluminiowym dobranym do szerokości taśmy",
    ]
    checks = [value for value in [
        f"Napięcie zasilania: {voltage}" if voltage else "",
        f"Moc na metr: {power}" if power else "",
        f"Szerokość taśmy: {width}" if width else "",
        f"Format handlowy: {format_label}",
    ] if value]
    notes = [
        f"Stosuj zasilacz zgodny z napięciem {voltage}" if voltage else "Sprawdź napięcie przed podłączeniem",
        f"Dziel taśmę zgodnie z modułem cięcia {cut}" if cut else "Dziel taśmę wyłącznie w oznaczonych miejscach",
        f"Profil i złączki dobierz do szerokości {width}" if width else "Profil dobierz do szerokości i mocy taśmy",
    ]
    return finish(product, sections, benefits, applications, checks, notes, specs)


def manufacturer_source_editorial(product: dict[str, Any], family_label: str) -> dict[str, Any]:
    """Preserve manufacturer copy for external brands while adding only catalog identity and checks."""
    code = product["code"]
    specs = public_specs(product)[:10]
    source = source_sentences(product, 4)
    raw_source = normalize(product.get("sourceDescription", ""))
    if not source and len(raw_source) >= 45:
        source = [raw_source]

    # Producent bywa autorem wartościowej treści, ale część kart zawiera stare,
    # czysto reklamowe sformułowania odrzucane przez bramkę jakości. Zachowujemy
    # sens i dane, wygładzając wyłącznie te zwroty — bez dopisywania nowych cech.
    def clean_source(value: str) -> str:
        value = re.sub(r"(?i)\bidealn\w*\s+rozwiązani\w*\b", "dobry wybór", value)
        value = re.sub(r"(?i)\bidealn\w*\b", "dobrze", value)
        value = re.sub(r"(?i)\bnowoczesn\w*\s+design\w*\b", "współczesna forma", value)
        value = value.replace("!", ".")
        return normalize(value)

    source = [clean_source(value) for value in source if clean_source(value)]
    identity = f"Pełna nazwa wariantu: {product['name']}. Indeks handlowy: {code}."
    first = source[0] if source else identity
    second = source[1] if len(source) > 1 else f"Produkt należy do grupy {product['category'].split('/')[-1]} i zachowuje oznaczenie modelu {code} nadane przez producenta."
    third = source[2] if len(source) > 2 else f"Przeznaczenie i zgodność wariantu należy potwierdzić po symbolu {code}, a nie wyłącznie po wyglądzie elementu."
    fourth = source[3] if len(source) > 3 else "Elementy współpracujące oraz sposób montażu dobiera się według oznaczeń podanych dla tej samej rodziny producenta."
    spec_sentence = exact_spec_sentence(specs[:6])
    if not spec_sentence or spec_sentence in {first, second, third}:
        spec_sentence = f"Identyfikatory tego wariantu to indeks handlowy {code} oraz EAN {product['ean']}."
    first_paragraphs = [first]
    if first != identity:
        first_paragraphs.append(identity)
    sections = [
        {"label": f"Opis {family_label}", "heading": f"{product['name']} — model {code}", "paragraphs": first_paragraphs},
        {"label": "Zastosowanie producenta", "heading": f"Przeznaczenie wariantu {code}", "paragraphs": [second, third]},
        {"label": "Dobór i kompletacja", "heading": "Kod, wymiary i zgodne elementy systemu", "paragraphs": [spec_sentence, fourth]},
    ]
    benefits = [f"Parametr {label.casefold()}: {value}" for label, value in specs[:4]] or [f"Oznaczenie producenta {code}", f"Numer EAN {product['ean']}"]
    applications = [
        f"Zastosowanie przewidziane dla grupy {product['category'].split('/')[-1]}",
        f"Kompletacja systemu {family_label} po potwierdzeniu symbolu modelu",
    ]
    checks = [f"Sprawdź indeks handlowy {code}", f"Porównaj EAN {product['ean']}"]
    checks.extend(f"Zweryfikuj {label.casefold()}: {value}" for label, value in specs[:2])
    notes = ["Przed montażem porównaj indeks handlowy elementu i zgodność z pozostałymi częściami systemu"]
    return finish(product, sections, benefits, applications, checks, notes, specs)


def battery_editorial(product: dict[str, Any]) -> dict[str, Any]:
    specs = public_specs(product)[:8]
    name = product["name"]
    code = product["code"]
    format_match = re.search(r"(?i)\bCR\s*\d{4}\b", name)
    voltage_match = re.search(r"(?i)\b\d+(?:[.,]\d+)?\s*V\b", name)
    battery_format = normalize(format_match.group(0)).replace(" ", "").upper() if format_match else code
    voltage = normalize(voltage_match.group(0)).replace(" ", "") if voltage_match else attr(product, "Napięcie")
    exact = [(label, value) for label, value in [("Format baterii", battery_format), ("Napięcie", voltage)] if value]
    sections = [
        {
            "label": "Format ogniwa",
            "heading": f"Bateria {battery_format}{f' o napięciu {voltage}' if voltage else ''}",
            "paragraphs": [
                f"Pełna nazwa wariantu: {name}. Indeks handlowy: {code}; EAN: {product['ean']}.",
                "Oznaczenie formatu określa wymiary i układ styków ogniwa, dlatego zamiennik należy dobrać po pełnym symbolu baterii.",
            ],
        },
        {
            "label": "Zgodność z urządzeniem",
            "heading": f"Ten sam format {battery_format} i napięcie {voltage or 'z danych urządzenia'}",
            "paragraphs": [
                exact_spec_sentence(exact),
                "Przed wymianą porównaj oznaczenie starej baterii, napięcie oraz polaryzację pokazaną w komorze urządzenia.",
            ],
        },
        {
            "label": "Wymiana baterii",
            "heading": "Polaryzacja, styki i właściwy model ogniwa",
            "paragraphs": [
                f"Do urządzenia wymagającego formatu {battery_format} zastosuj wariant o napięciu {voltage or 'wskazanym przez producenta urządzenia'}.",
                "Podczas wymiany nie zwieraj biegunów i nie łącz w jednym urządzeniu ogniw o różnych oznaczeniach lub stopniu zużycia.",
            ],
        },
    ]
    benefits = [f"Format baterii {battery_format}", f"Napięcie znamionowe {voltage}" if voltage else f"Kod ogniwa {code}"]
    applications = [
        f"Urządzenia wymagające baterii {battery_format}",
        "Wymiana ogniwa na wariant o tym samym formacie i napięciu",
    ]
    checks = [
        f"Porównaj oznaczenie baterii: {battery_format}",
        f"Sprawdź napięcie: {voltage}" if voltage else "Sprawdź napięcie wymagane przez urządzenie",
        "Potwierdź polaryzację przed włożeniem ogniwa",
    ]
    notes = [
        "Nie zwieraj biegunów baterii podczas przechowywania ani wymiany",
        "Zużyte ogniwo oddaj do właściwego punktu zbiórki baterii",
    ]
    return finish(product, sections, benefits, applications, checks, notes, specs or exact)


def profile_cover_editorial(product: dict[str, Any]) -> dict[str, Any]:
    if "KLUŚ" in product.get("producer", "").upper():
        return manufacturer_source_editorial(product, "KLUŚ")
    specs = preferred_specs(
        product,
        [
            "Długość",
            "Kolor osłony",
            "Wykonanie (materiał)",
            "Szerokość osłony",
            "Szerokość świecenia",
            "Przepuszczalność świetlna",
            "Przeznaczenie produktu",
            "Gwarancja",
        ],
        10,
    )
    name = product["name"]
    code = product["code"]
    length_match = re.search(r"(?i)\b\d+(?:[.,]\d+)?\s*m\b", name)
    length = attr(product, "Długość") or (normalize(length_match.group(0)).replace(" ", "") if length_match else "")
    color = attr(product, "Kolor osłony", "Kolor")
    if not color:
        color_match = re.search(
            r"(?i)\b(?:mleczn\w*|matow\w*\s+opal|prze(?:z|ź)rocz\w*|czarn\w*|biał\w*|satyn\w*)\b",
            name,
        )
        color = normalize(color_match.group(0)) if color_match else ""
    material = attr(product, "Wykonanie (materiał)")
    width = attr(product, "Szerokość osłony", "Szerokość świecenia")
    transmission = attr(product, "Przepuszczalność świetlna")
    purpose = attr(product, "Przeznaczenie produktu")

    raw_target = re.sub(r"(?i)^\s*(?:osłona|klosz)\s*(?:do\s+(?:profilu|profili?))?\s*", "", name)
    target = re.split(
        r"(?i)\s+(?=(?:\d+(?:[.,]\d+)?\s*m\b|mleczn|matow|prze(?:z|ź)rocz|czarn|biał|satyn|KLUŚ\b|PRESCOT\b))",
        raw_target,
        maxsplit=1,
    )[0].strip(" ,;-")
    target = target or "rodzina wskazana w nazwie produktu"
    fragments = source_fragments(product, 3)
    source_line = sentence_case("; ".join(fragments)) + "." if fragments else ""

    color_lower = color.casefold()
    if "mlecz" in color_lower or "opal" in color_lower:
        optical_note = "Mleczne lub opalowe wykończenie wpływa na odbiór linii światła; końcowy efekt zależy również od taśmy i geometrii profilu."
    elif "prze" in color_lower:
        optical_note = "Przezroczysty wariant osłania taśmę bez mlecznego wykończenia, dlatego przy doborze trzeba świadomie porównać wygląd obu wersji."
    elif "czarn" in color_lower:
        optical_note = "Czarny wariant zmienia wygląd profilu także po wyłączeniu światła; efekt należy ocenić z wybraną taśmą i profilem."
    else:
        optical_note = "Osłona zakrywa wnętrze profilu, lecz sama nie przesądza o szczelności kompletnej oprawy bez potwierdzenia dla całego systemu."

    sections = [
        {
            "label": "Zgodność z profilem",
            "heading": f"Osłona do systemu {target}",
            "paragraphs": [
                f"Pełna nazwa wariantu: {name}. Indeks handlowy: {code}.",
                f"Element należy dobrać do profilu z rodziny {target}; podobny przekrój lub kolor nie potwierdza zgodności mocowania.",
            ],
        },
        {
            "label": "Światło i materiał",
            "heading": f"Osłona {color.casefold() if color else 'w wykończeniu wskazanym w nazwie'}{f', materiał {material}' if material else ''}",
            "paragraphs": [
                exact_spec_sentence(
                    [(key, value) for key, value in [("Kolor osłony", color), ("Materiał", material), ("Szerokość", width), ("Przepuszczalność", transmission)] if value]
                ),
                source_line or optical_note,
            ],
        },
        {
            "label": "Długość i zamówienie",
            "heading": f"Długość {length or 'określona pełnym kodem'} dla wariantu {code}",
            "paragraphs": [
                f"Długość elementu: {length}; przeznaczenie: {purpose}." if length and purpose else f"Długość elementu: {length}." if length else f"Właściwy wariant identyfikuje pełny kod {code}.",
                "Przed zamówieniem porównaj rodzinę profilu, długość, kolor oraz sposób zatrzaskiwania osłony; tych cech nie należy przenosić z podobnego modelu.",
            ],
        },
    ]
    benefits = [
        value
        for value in [
            f"Osłona do systemu {target}",
            f"Długość {length}" if length else "",
            f"Kolor osłony {color}" if color else "",
            f"Materiał {material}" if material else "",
            f"Przepuszczalność {transmission}" if transmission else "",
        ]
        if value
    ]
    applications = [
        f"Zamknięcie profilu z rodziny {target}",
        purpose or "Osłonięcie taśmy i ukształtowanie wyglądu linii światła",
    ]
    checks = [
        f"Potwierdź zgodność z profilem {target}",
        f"Porównaj długość osłony: {length}" if length else f"Porównaj pełny kod osłony: {code}",
        f"Sprawdź kolor osłony: {color}" if color else "",
        f"Sprawdź szerokość: {width}" if width else "",
    ]
    notes = [
        "Nie wciskaj osłony przed potwierdzeniem zgodności przekroju z profilem",
        "Cięcie i montaż wykonaj metodą przewidzianą dla konkretnej rodziny profilu",
    ]
    return finish(product, sections, benefits, applications, checks, notes, specs)


def profile_accessory_editorial(product: dict[str, Any]) -> dict[str, Any]:
    if "KLUŚ" in product.get("producer", "").upper():
        return manufacturer_source_editorial(product, "KLUŚ")
    specs = preferred_specs(
        product,
        ["Wykonanie (materiał)", "Kolor", "Długość", "Wymiar", "Montaż", "Przeznaczenie produktu", "Gwarancja"],
        9,
    )
    name = product["name"]
    lower = name.casefold()
    code = product["code"]
    accessory_type, role, application = next(
        (
            entry
            for token, entry in (
                ("zaślepk", ("zaślepka", "Element zamyka zakończenie kompatybilnego profilu i porządkuje jego wykończenie.", "Wykończenie zakończenia zgodnego profilu LED")),
                ("zawieszk", ("zawieszka", "Element służy do kompletacji mocowania zwieszanego w systemie wskazanym przez producenta.", "Kompletacja zwieszanego systemu profilu LED")),
                ("linka", ("linka", "Linka jest częścią systemu podwieszenia i wymaga zgodnych uchwytów oraz zakończeń.", "Podwieszenie zgodnego profilu LED")),
                ("pręt", ("pręt", "Pręt jest częścią systemu podwieszenia i wymaga zgodnych uchwytów oraz zakończeń.", "Podwieszenie zgodnego profilu LED")),
                ("mocownik", ("mocownik", "Mocownik łączy profil z podłożem lub elementem nośnym zgodnie z opisem danego systemu.", "Mocowanie zgodnego profilu LED")),
                ("uchwyt", ("uchwyt", "Uchwyt ustala położenie kompatybilnego profilu w przygotowanym miejscu montażu.", "Mocowanie zgodnego profilu LED")),
                ("sprężyn", ("sprężyna montażowa", "Sprężyna jest elementem mocującym dobieranym do konkretnego profilu i sposobu zabudowy.", "Mocowanie zgodnego profilu LED")),
                ("wkładka", ("wkładka", "Wkładkę kompletuje się z profilem wskazanym w nazwie lub dokumentacji systemu.", "Uzupełnienie zgodnego systemu profilu LED")),
                ("włącznik", ("włącznik do profilu", "Włącznik jest elementem sterującym przeznaczonym do zabudowy w zgodnym profilu LED.", "Sterowanie oświetleniem zabudowanym w profilu LED")),
                ("łącznik", ("łącznik profilu", "Łącznik służy do zestawienia elementów profilu w układzie przewidzianym dla tej rodziny.", "Łączenie elementów zgodnego profilu LED")),
                ("uszczelk", ("uszczelka", "Uszczelkę dobiera się do dokładnego przekroju i elementów kompletnego systemu profilu.", "Uszczelnienie zgodnego systemu profilu LED")),
                ("maskownic", ("maskownica", "Maskownica wykańcza wskazany element systemu i wymaga zgodności wymiarowej.", "Wykończenie zgodnego systemu profilu LED")),
            )
            if token in lower
        ),
        ("akcesorium montażowe", "Element służy do kompletacji profilu LED zgodnie z pełnym kodem i dokumentacją systemu.", "Kompletacja zgodnego systemu profilu LED"),
    )
    material = attr(product, "Wykonanie (materiał)")
    color = product_color(product)
    length = attr(product, "Długość")
    size = attr(product, "Wymiar")
    mounting = attr(product, "Montaż")
    fragments = source_fragments(product, 4)
    confirmed = sentence_case("; ".join(fragments)) + "." if fragments else ""
    if confirmed and len(confirmed) < 45:
        confirmed = f"{confirmed.removesuffix('.')}; informacja dotyczy elementu o kodzie {code}."
    sections = [
        {
            "label": "Rola elementu",
            "heading": f"{sentence_case(accessory_type)} — model {code}",
            "paragraphs": [f"Pełna nazwa wariantu: {name}. Indeks handlowy: {code}.", role],
        },
        {
            "label": "Wykonanie i montaż",
            "heading": f"{sentence_case(material or color or mounting or accessory_type)} w konkretnym systemie profilu",
            "paragraphs": [
                exact_spec_sentence([(key, value) for key, value in [("Materiał", material), ("Kolor", color), ("Długość", length), ("Wymiar", size), ("Montaż", mounting)] if value]),
                confirmed or f"Element {code} należy kompletować z profilem o zgodnym systemie mocowania; decydujące są oznaczenie rodziny oraz dokumentacja profilu.",
            ],
        },
        {
            "label": "Dobór bez pomyłki",
            "heading": "Rodzina profilu, funkcja elementu i pełny kod",
            "paragraphs": [
                f"Indeks handlowy: {code}; EAN: {product['ean']}; typ elementu: {accessory_type}.",
                "Nie dobieraj akcesorium wyłącznie na podstawie zdjęcia — porównaj nazwę rodziny, wymiary, funkcję oraz sposób mocowania.",
            ],
        },
    ]
    benefits = [
        f"Typ elementu: {accessory_type}",
        f"Kod systemowy {code}",
        *([f"Materiał {material}"] if material else []),
        *([f"Kolor {color}"] if color else []),
    ]
    applications = [application, f"Kompletacja profilu zgodnie z funkcją elementu: {accessory_type}"]
    checks = [
        f"Potwierdź rodzinę kompatybilnego profilu dla kodu {code}",
        f"Sprawdź funkcję elementu: {accessory_type}",
        f"Porównaj wymiar: {size}" if size else "",
        f"Porównaj sposób montażu: {mounting}" if mounting else "",
    ]
    notes = [
        "Montaż wykonaj dopiero po potwierdzeniu zgodności elementu z profilem",
        "Przed obciążeniem systemu sprawdź sposób mocowania wskazany przez producenta",
    ]
    return finish(product, sections, benefits, applications, checks, notes, specs)


def profile_editorial(product: dict[str, Any]) -> dict[str, Any]:
    if "KLUŚ" in product.get("producer", "").upper():
        return manufacturer_source_editorial(product, "KLUŚ")
    specs = preferred_specs(product, ["Wykonanie (materiał)", "Kolor profilu", "Kolor", "Wykończenie", "Długość", "Szerokość profilu", "Szerokość świecenia", "Montaż", "Kolor osłony", "Przeznaczenie produktu", "Gwarancja"], 11)
    code = product["code"]
    material = attr(product, "Wykonanie (materiał)") or ("aluminium" if "alumini" in f"{product['category']} {product['name']}".casefold() else "")
    color = attr(product, "Kolor profilu", "Kolor", "Wykończenie") or product_color(product)
    length = attr(product, "Długość") or name_value(product, r"\b\d+(?:[.,]\d+)?\s*m\b")
    width = attr(product, "Szerokość profilu")
    light_width = attr(product, "Szerokość świecenia")
    mounting = attr(product, "Montaż")
    cover = attr(product, "Kolor osłony")
    purpose = attr(product, "Przeznaczenie produktu")
    spaces = attr(product, "Przestrzeń")
    source_lower = product.get("sourceDescription", "").casefold()
    source_summary = source_sentences(product, 2)
    sold_without_cover = "bez osłony" in source_lower or "osłon" in source_lower and "sprzedawan" in source_lower
    thermal_text = "Aluminiowy korpus odbiera ciepło z taśmy LED, dlatego profil jest częścią układu montażowego, a nie wyłącznie wykończeniem." if "alumini" in material.casefold() else "Profil porządkuje montaż taśmy LED i wyznacza formę gotowej linii światła."
    sections = [
        {"label": "Konstrukcja", "heading": f"{sentence_case(material) if material else 'Profil LED'} w wariancie {color or product['code']}", "paragraphs": [f"Pełna nazwa wariantu: {product['name']}. Indeks handlowy: {product['code']}. {exact_spec_sentence(specs[:4])}", thermal_text]},
        {"label": "Wymiar i montaż", "heading": f"{f'Długość {length}' if length else f'Model {code}'} i montaż {mounting or 'w systemie profilu'}", "paragraphs": [exact_spec_sentence([(k, v) for k, v in [("Długość", length), ("Szerokość profilu", width), ("Szerokość świecenia", light_width), ("Montaż", mounting)] if v]), source_summary[0] if source_summary and ("montaż" in source_summary[0].casefold() or "sufit" in source_summary[0].casefold()) else "Wymiary profilu należy porównać z taśmą, osłoną, zaślepkami i dostępną przestrzenią montażową."]},
        {"label": "Kompletacja systemu", "heading": "Osłona, zaślepki i akcesoria do właściwego modelu", "paragraphs": [f"Profil jest sprzedawany bez osłony; klosz i elementy końcowe dobierz do rodziny {product['code']}." if sold_without_cover else f"Kolor osłony: {cover}; pozostałe elementy dobierz do kodu profilu." if cover else "Osłonę i elementy końcowe dobierz do konkretnej rodziny oraz kodu profilu.", f"Przeznaczenie wskazane w danych: {purpose}." if purpose else "Przed cięciem sprawdź długość elementu i sposób mocowania podany dla tego wariantu."]},
    ]
    benefits = [x for x in [f"Wykonanie: {material}" if material else "", f"Wariant kolorystyczny: {color}" if color else "", f"Długość elementu: {length}" if length else "", f"Szerokość świecenia: {light_width}" if light_width else "", f"Sposób montażu: {mounting}" if mounting else "", "Osłona dobierana osobno" if sold_without_cover else ""] if x]
    clean_spaces = re.sub(r",(?=\S)", ", ", spaces).replace("/", " / ") if spaces else ""
    applications = [f"{sentence_case(purpose)}" if purpose else "Budowa liniowej oprawy z taśmą LED", f"Przestrzenie wskazane w danych: {clean_spaces}" if clean_spaces else "Porządkowanie montażu taśmy i osłony w jednym systemie"]
    checks = [x for x in [f"Długość: {length}" if length else "", f"Szerokość profilu: {width}" if width else "", f"Montaż: {mounting}" if mounting else "", f"Kolor osłony: {cover}" if cover else ""] if x]
    notes = ["Osłonę, zaślepki i uchwyty dobierz po kodzie rodziny profilu", "Przed obróbką porównaj wymiary profilu z miejscem montażu"]
    return finish(product, sections, benefits, applications, checks, notes, specs)


def power_editorial(product: dict[str, Any]) -> dict[str, Any]:
    producer = product.get("producer", "")
    if producer and not producer.casefold().startswith("prescot") and "scharfer" not in producer.casefold():
        return manufacturer_source_editorial(product, producer)
    specs = preferred_specs(product, ["Napięcie Wejściowe", "Napięcie wejściowe", "Napięcie Wyjściowe", "Napięcie wyjściowe", "Moc", "Prąd", "Prąd maksymalny", "Klasa szczelności", "Typ", "Wymiar", "Długość przewodu", "Gwarancja"], 11)
    vin = attr(product, "Napięcie Wejściowe", "Napięcie wejściowe")
    vout = attr(product, "Napięcie Wyjściowe", "Napięcie wyjściowe")
    name_lower = product["name"].casefold()
    if not vout:
        low_voltage = re.search(r"(?i)\b(?:5|12|24|36|48)\s*V(?:\s*DC)?\b", product["name"])
        vout = normalize(low_voltage.group(0)) if low_voltage else ""
    power_match = re.search(r"(?i)\b\d+(?:[.,]\d+)?\s*W\b", product["name"])
    power = attr(product, "Moc") or (normalize(power_match.group(0)).replace(" ", "") if power_match else "")
    if power and not any(label.casefold() == "moc" for label, _ in specs):
        specs.insert(2, ("Moc", power))
    current = attr(product, "Prąd", "Prąd maksymalny") or name_value(product, r"\b\d+(?:[.,]\d+)?\s*(?:mA|A)\b")
    ip = attr(product, "Klasa szczelności") or name_value(product, r"\bIP\s*\d{2}\b")
    is_constant_current = "prądow" in name_lower
    kind = (
        "do puszki"
        if "do puszk" in name_lower
        else "gniazdkowy"
        if "gniazdk" in name_lower
        else "hermetyczny"
        if "hermet" in name_lower
        else "modułowy"
        if "moduł" in name_lower
        else "ściemnialny TRIAC"
        if "triac" in name_lower
        else "stałoprądowy"
        if is_constant_current
        else attr(product, "Typ") or product["category"].split("/")[-1]
    )
    size = attr(product, "Wymiar")
    code = product["code"]
    output_facts = [(label, value) for label, value in [("Napięcie wyjściowe", vout), ("Prąd wyjściowy", current), ("Moc", power)] if value]
    electrical_facts = [(label, value) for label, value in [("Napięcie wejściowe", vin), ("Napięcie wyjściowe", vout), ("Prąd", current), ("Moc", power)] if value]
    output_heading = (
        f"Prąd {current}{f' i moc {power}' if power else ''}"
        if is_constant_current and current
        else f"{vout}{f' i moc {power}' if power else ''}"
        if vout
        else f"Moc {power} — model {code}"
        if power
        else f"Parametry wyjściowe modelu {code}"
    )
    sections = [
        {"label": "Parametry wyjściowe", "heading": output_heading, "paragraphs": [f"{product['name']}. Indeks handlowy: {code}. {exact_spec_sentence(output_facts)}", "W zasilaczu stałoprądowym wartość prądu musi odpowiadać wymaganiom modułu LED, a zakres napięcia pracy trzeba potwierdzić w karcie modelu." if is_constant_current else "Napięcie wyjściowe musi odpowiadać odbiornikom LED, a ich łączne obciążenie powinno mieścić się w mocy znamionowej zasilacza."]},
        {"label": "Obudowa i miejsce pracy", "heading": f"{sentence_case(kind)}{f' i klasa {ip}' if ip else ''}", "paragraphs": [exact_spec_sentence([(k, v) for k, v in [("Typ", kind), ("Klasa szczelności", ip), ("Wymiar", size)] if v]), f"{ingress_guidance(ip)} Wymiary i sposób zabudowy porównaj z miejscem przeznaczonym na zasilacz." if ip else "Wymiary, wentylację i sposób zabudowy porównaj z miejscem przeznaczonym na zasilacz."]},
        {"label": "Dobór zasilania", "heading": "Prąd, napięcie i obciążenie kompletowanego obwodu", "paragraphs": [exact_spec_sentence(electrical_facts or specs[:3]), "Przed podłączeniem sprawdź zgodność parametrów wyjściowych z odbiornikiem oraz nie przekraczaj wartości znamionowych przypisanych do modelu."]},
    ]
    benefits = [x for x in [f"Napięcie wyjściowe {vout}" if vout else "", f"Moc znamionowa {power}" if power else "", f"Prąd {current}" if current else "", f"Obudowa typu {kind}" if kind else ""] if x]
    applications = [f"Zasilanie modułów LED wymagających prądu {current}" if is_constant_current and current else f"Zasilanie odbiorników LED pracujących przy {vout}" if vout else "Zasilanie odbiorników LED po porównaniu parametrów wyjściowych", f"Montaż typu: {kind}; obciążenie do mocy znamionowej {power}" if power else f"Montaż typu: {kind}"]
    checks = [x for x in [f"Napięcie wyjściowe: {vout}" if vout else "", f"Łączna moc odbiorników względem {power}" if power else "", f"Klasa szczelności: {ip}" if ip else "", f"Wymiary: {size}" if size else ""] if x]
    notes = ["Przed podłączeniem odłącz zasilanie i porównaj parametry wejścia oraz wyjścia", "Dla zasilacza stałoprądowego sprawdź wymagany prąd i zakres napięcia modułu LED" if is_constant_current else "Nie przekraczaj mocy znamionowej podanej dla modelu"]
    return finish(product, sections, benefits, applications, checks, notes, specs)


def controller_editorial(product: dict[str, Any]) -> dict[str, Any]:
    producer = product.get("producer", "")
    if producer and not producer.casefold().startswith("prescot"):
        return manufacturer_source_editorial(product, producer)
    specs = preferred_specs(product, ["Napięcie Wejściowe", "Napięcie Wyjściowe", "Moc", "Prąd maksymalny", "Prąd na 1 kanał", "Ilość stref", "Komunikacja", "Zasięg", "Ilość programów", "Zasilanie pilota", "Wymiar", "Kolor", "Gwarancja"], 12)
    code = product["code"]
    voltage = attr(product, "Napięcie Wejściowe", "Napięcie Wyjściowe") or name_value(product, r"\b\d+(?:[.,]\d+)?\s*[-–]\s*\d+(?:[.,]\d+)?\s*V(?:DC)?\b") or name_value(product, r"\b(?:5|12|24|36|48|230)\s*V(?:DC)?\b")
    current = attr(product, "Prąd maksymalny", "Prąd", "Prąd na 1 kanał") or name_value(product, r"\b\d+(?:[.,]\d+)?\s*A\s*/\s*(?:kan\.?|kanał)\b") or name_value(product, r"\bmax\.?\s*\d+(?:[.,]\d+)?\s*A\b")
    zones = attr(product, "Ilość stref")
    name_lower = product["name"].casefold()
    if not zones:
        zone_match = re.search(r"(?i)\b(\d+)\s*[- ]?stref", product["name"])
        zones = f"{zone_match.group(1)} stref" if zone_match else ""
    communication = attr(product, "Komunikacja") or ("RF" if re.search(r"\bRF\b", product["name"], re.I) else "Wi-Fi" if "wi-fi" in name_lower or "wifi" in name_lower else "")
    reach = attr(product, "Zasięg")
    mode = "RGB+CCT" if "rgb" in name_lower and "cct" in name_lower else "RGB" if "rgb" in name_lower else "CCT" if "cct" in name_lower else "MONO" if "mono" in name_lower else "LED"
    control_use = {
        "MONO": "regulacji jasności jednobarwnej taśmy LED",
        "CCT": "regulacji jasności i odcienia bieli w taśmie CCT",
        "RGB": "sterowania kolorami w taśmie RGB",
        "RGB+CCT": "sterowania kolorami RGB oraz odcieniem bieli CCT",
    }.get(mode, "sterowania zgodnym odbiornikiem LED")
    sections = [
        {"label": "Sterowanie", "heading": f"Sterownik {mode}{f' dla napięcia {voltage}' if voltage else f' — model {code}'}", "paragraphs": [f"{product['name']}. Kod: {code}. {exact_spec_sentence(specs[:5])}", f"Ten wariant służy do {control_use}; liczba kanałów i obciążenie muszą odpowiadać kompletowanemu obwodowi."]},
        {"label": "Komunikacja i obsługa", "heading": f"{communication or 'Parowanie z elementem sterującym'}{f', zasięg {reach}' if reach else ''}", "paragraphs": [exact_spec_sentence([(k, v) for k, v in [("Komunikacja", communication), ("Zasięg", reach), ("Ilość stref", zones)] if v]), "Parametry obsługi porównaj z pilotem, panelem lub nadajnikiem przewidzianym dla danego systemu."]},
        {"label": "Dobór do układu", "heading": "Napięcie, rodzaj taśmy i dopuszczalne obciążenie", "paragraphs": [f"Napięcie: {voltage}; prąd: {current}." if voltage or current else exact_spec_sentence(specs[:3]), "Przed podłączeniem sprawdź zgodność kanałów oraz nie przekraczaj wartości prądu i mocy podanych dla sterownika."]},
    ]
    benefits = [x for x in [f"Obsługa systemu {mode}", f"Zakres napięcia {voltage}" if voltage else "", f"Prąd maksymalny {current}" if current else "", f"Komunikacja {communication}" if communication else "", f"Liczba stref: {zones}" if zones else ""] if x]
    applications = [f"Układy przeznaczone do {control_use}", "Kompletacja układu z odpowiednim zasilaczem i elementem sterującym"]
    checks = [x for x in [f"Typ sterowania: {mode}", f"Napięcie: {voltage}" if voltage else "", f"Prąd lub obciążenie: {current}" if current else "", f"Komunikacja: {communication}" if communication else ""] if x]
    notes = ["Podłączaj przy odłączonym zasilaniu i zgodnie z oznaczeniami kanałów", "Zasilacz oraz odbiornik muszą pracować w zakresie napięcia sterownika"]
    return finish(product, sections, benefits, applications, checks, notes, specs)


def control_input_editorial(product: dict[str, Any]) -> dict[str, Any]:
    """Wall panels and handheld remotes select zones; they do not carry the LED load."""
    specs = preferred_specs(product, ["Ilość stref", "Komunikacja", "Zasięg", "Zasilanie pilota", "Napięcie Wejściowe", "Kolor", "Wymiar", "Gwarancja"], 9)
    name = product["name"]
    lower = name.casefold()
    code = product["code"]
    device = "pilot" if lower.startswith("pilot ") else "panel sterujący"
    mode = "RGB+CCT" if "rgb" in lower and "cct" in lower else "RGBW" if "rgbw" in lower else "RGB" if "rgb" in lower else "CCT" if "cct" in lower else "MONO" if "mono" in lower else "ALL" if re.search(r"\bALL\b", name, re.I) else "LED"
    zones = attr(product, "Ilość stref")
    if not zones:
        zone_match = re.search(r"(?i)\b(\d+)\s*[- ]?stref(?:a|y)?\b", name)
        zones = f"{zone_match.group(1)} strefy" if zone_match and zone_match.group(1) not in {"1"} else "1 strefa" if zone_match else ""
    communication = attr(product, "Komunikacja") or ("RF" if re.search(r"\bRF\b", name, re.I) else "")
    reach = attr(product, "Zasięg")
    supply = attr(product, "Zasilanie pilota", "Napięcie Wejściowe")
    if not supply:
        supply = "zasilanie bateryjne" if re.search(r"(?i)\bbat(?:eryjn\w*)?\b", name) else name_value(product, r"\b230\s*V\b")
    color = product_color(product)
    mounting = "magnetyczny" if "magnet" in lower else "naścienny" if "naścien" in lower else ""
    known = [(label, value) for label, value in [("System światła", mode), ("Liczba stref", zones), ("Komunikacja", communication), ("Zasilanie", supply), ("Kolor", color)] if value]
    sections = [
        {"label": "Element sterujący", "heading": f"{sentence_case(device)} {mode} — model {code}", "paragraphs": [f"{name}. {exact_spec_sentence(known[:4])}", f"Ten {device} służy do wybierania funkcji zgodnego systemu {mode}; prąd obciążenia określa sparowany odbiornik, nie sam nadajnik."]},
        {"label": "Strefy i obsługa", "heading": f"{zones or 'Obsługa przypisanego odbiornika'}{f' przez {communication}' if communication else ''}", "paragraphs": [exact_spec_sentence([(label, value) for label, value in [("Liczba stref", zones), ("Komunikacja", communication), ("Zasięg", reach), ("Sposób montażu", mounting)] if value]), "Przed zakupem porównaj system światła, liczbę obsługiwanych stref i sposób komunikacji z odbiornikiem zamontowanym przy taśmie lub oprawie." ]},
        {"label": "Zasilanie i parowanie", "heading": f"{sentence_case(supply or 'Parowanie z odbiornikiem')} — {code}", "paragraphs": [f"Zasilanie elementu sterującego: {supply}; kolor: {color}; indeks handlowy: {code}." if supply or color else f"Indeks handlowy: {code}; indeks handlowy: {product['code']}; EAN: {product['ean']}.", "Parowanie, przypisanie stref i zmianę trybu wykonaj według instrukcji zgodnego odbiornika oraz tego panelu lub pilota."]},
    ]
    benefits = [f"Sterowanie systemem {mode}", f"Obsługa {zones}" if zones else f"Typ urządzenia: {device}", f"Komunikacja {communication}" if communication else "", f"Wariant kolorystyczny {color}" if color else ""]
    applications = [f"Obsługa odbiorników pracujących w systemie {mode}", "Sterowanie naścienne" if device == "panel sterujący" else "Zdalna obsługa sparowanego odbiornika"]
    checks = [f"System światła: {mode}", f"Liczba stref: {zones}" if zones else f"Kod nadajnika: {code}", f"Komunikacja: {communication}" if communication else f"Zasilanie: {supply}" if supply else ""]
    notes = ["Przed parowaniem sprawdź zgodność panelu lub pilota z odbiornikiem", "Baterię dobierz wyłącznie według oznaczenia w instrukcji" if "bat" in supply.casefold() else "Podłączenie zasilania wykonaj według schematu producenta"]
    return finish(product, sections, benefits, applications, checks, notes, specs or known)


def control_accessory_editorial(product: dict[str, Any]) -> dict[str, Any]:
    specs = public_specs(product)[:8]
    name = product["name"]
    lower = name.casefold()
    code = product["code"]
    if "puszka" in lower:
        role = "puszka podtynkowa do osadzenia panelu sterującego LED"
        selection = "Porównaj wymiary panelu, sposób mocowania i głębokość przygotowanego otworu montażowego."
    elif "uchwyt" in lower:
        role = "uchwyt do odkładania pilota systemu sterowania LED"
        selection = "Dobierz uchwyt do dokładnego modelu pilota oraz zaplanowanego miejsca mocowania."
    elif "adapter" in lower:
        role = "adapter współpracujący ze sterownikiem wskazanym w pełnej nazwie"
        selection = "Porównaj kod sterownika, złącze i sposób zasilania przed połączeniem adaptera z systemem."
    else:
        role = "akcesorium montażowe do systemu sterowania LED"
        selection = "Zgodność potwierdź po pełnym kodzie obu łączonych elementów systemu."
    source_summary = source_sentences(product, 1)
    compatibility = source_summary[0] if source_summary else f"Akcesorium {code} należy kompletować z elementem sterującym wskazanym w jego pełnej nazwie lub instrukcji systemu."
    sections = [
        {"label": "Funkcja akcesorium", "heading": f"{sentence_case(role)} — {code}", "paragraphs": [f"{name}. Indeks handlowy: {code}; EAN: {product['ean']}.", f"To {role}; element nie zastępuje sterownika, panelu ani pilota."]},
        {"label": "Zgodność systemowa", "heading": "Model współpracujący i sposób mocowania", "paragraphs": [compatibility, selection]},
        {"label": "Przed montażem", "heading": f"Wymiary, mocowanie i indeks {code}", "paragraphs": [exact_spec_sentence(specs[:4]) if specs else f"Indeks handlowy: {code}; EAN: {product['ean']}.", "Nie dobieraj tego elementu wyłącznie po wyglądzie obudowy — sprawdź pełny symbol zgodnego panelu, pilota lub sterownika."]},
    ]
    benefits = [f"Funkcja: {role}", f"Identyfikacja kodem {code}"]
    applications = [sentence_case(role), "Kompletacja zgodnego systemu sterowania LED"]
    checks = [f"Kod akcesorium: {code}", "Model współpracującego elementu sterującego", "Wymiary i sposób mocowania"]
    notes = ["Montaż wykonaj po potwierdzeniu zgodności wymiarowej i systemowej"]
    return finish(product, sections, benefits, applications, checks, notes, specs or [("Typ", role), ("Kod", code)])


def accessory_editorial(product: dict[str, Any]) -> dict[str, Any]:
    producer = product.get("producer", "")
    if producer and not producer.casefold().startswith("prescot"):
        return manufacturer_source_editorial(product, producer)
    specs = preferred_specs(product, ["Długość przewodu", "Przekrój przewodu", "Szerokość taśmy", "Zakończenie przewodu 1", "Zakończenie przewodu 2", "Napięcie Wyjściowe", "Wykonanie (materiał)", "Wymiar", "Kolor", "Gwarancja"], 10)
    leaf = product["category"].split("/")[-1]
    length = attr(product, "Długość przewodu")
    gauge = attr(product, "Przekrój przewodu")
    tape_width = attr(product, "Szerokość taśmy")
    ends = join_polish([attr(product, "Zakończenie przewodu 1"), attr(product, "Zakończenie przewodu 2")])
    color = attr(product, "Kolor")
    name_lower = product["name"].casefold()
    role = next(
        (
            text
            for token, text in (
                ("zaślepk", "Zaślepka zamyka zakończenie elementu wskazanego w nazwie; jej wymiar musi odpowiadać koszulce, profilowi lub obudowie."),
                ("złącz", "Złączka służy do połączenia zgodnych elementów instalacji; przed zakupem trzeba porównać liczbę styków, przekrój i wymiary."),
                ("gniazd", "Gniazdo jest elementem połączeniowym dobieranym do pasującego wtyku, wymiaru styku oraz sposobu montażu."),
                ("wtyk", "Wtyk jest elementem połączeniowym dobieranym do pasującego gniazda, wymiaru styku oraz sposobu montażu."),
                ("przewód", "Przewód dobiera się według liczby żył, przekroju, długości i rodzaju zakończeń podanych dla konkretnego wariantu."),
                ("uchwyt", "Uchwyt służy do mocowania elementu wskazanego w nazwie i wymaga zgodności wymiarowej z przygotowanym miejscem montażu."),
                ("włącznik", "Włącznik jest elementem sterującym dobieranym według sposobu zabudowy, funkcji i parametrów kompletowanego obwodu."),
                ("wyłącznik", "Wyłącznik jest elementem sterującym dobieranym według sposobu zabudowy, funkcji i parametrów kompletowanego obwodu."),
            )
            if token in name_lower
        ),
        "Akcesorium służy do kompletacji instalacji zgodnie z funkcją, wymiarami i sposobem połączenia wskazanymi w pełnej nazwie.",
    )
    sections = [
        {"label": "Wariant akcesorium", "heading": f"{leaf}: model {product['code']}", "paragraphs": [exact_spec_sentence(specs[:5]), role]},
        {"label": "Połączenie", "heading": f"{length or tape_width or ends or 'Parametry'} do porównania z instalacją", "paragraphs": [exact_spec_sentence([(k, v) for k, v in [("Długość przewodu", length), ("Przekrój przewodu", gauge), ("Szerokość taśmy", tape_width), ("Zakończenia", ends)] if v]), "Przed zakupem porównaj typ złącza, liczbę styków, szerokość taśmy i zakończenia przewodu tylko w zakresie podanym dla tego modelu."]},
        {"label": "Identyfikacja", "heading": "Kod, EAN i wariant kolorystyczny", "paragraphs": [f"Indeks handlowy: {product['code']}; EAN: {product['ean']}; kolor: {color or 'zgodny z nazwą produktu'}.", "Identyfikatory pozwalają odróżnić ten element od podobnych wtyków, gniazd, przewodów i złączek w tej samej grupie."]},
    ]
    benefits = [x for x in [f"Przewód o długości {length}" if length else "", f"Przekrój przewodu {gauge}" if gauge else "", f"Wariant do taśmy o szerokości {tape_width}" if tape_width else "", f"Kolor {color}" if color else ""] if x]
    applications = [f"Kompletacja instalacji w grupie: {leaf}", "Połączenie elementów zgodnych z typem i parametrami tego wariantu"]
    checks = [x for x in [f"Typ i kod elementu: {product['code']}", f"Długość przewodu: {length}" if length else "", f"Przekrój przewodu: {gauge}" if gauge else "", f"Szerokość taśmy: {tape_width}" if tape_width else ""] if x]
    notes = ["Przed podłączeniem porównaj typ złącza po obu stronach instalacji", "Nie opieraj doboru wyłącznie na wyglądzie elementu; sprawdź kod i wymiary"]
    return finish(product, sections, benefits, applications, checks, notes, specs)


def luminaire_editorial(product: dict[str, Any]) -> dict[str, Any]:
    producer = normalize(product.get("producer", ""))
    producer_key = producer.casefold()
    source_for_brand = normalize(product.get("sourceDescription", ""))
    source_key = source_for_brand.casefold()
    name_key = product["name"].casefold()
    source_conflicts_with_name = (
        (any(term in name_key for term in ("bez led", "bez źródła")) and re.search(r"zawiera\s+źródło\s+światła|ze\s+źródłem\s+światła", source_key))
        or ("bez zasilacza" in name_key and re.search(r"zawiera\s+zasilacz|zasilacz\s+w\s+zestawie", source_key))
    )
    if any(brand in producer_key for brand in ("milight", "mi-light", "kluś", "klus")) and len(source_for_brand) >= 120 and not source_conflicts_with_name:
        return manufacturer_source_editorial(product, producer)
    specs = preferred_specs(product, ["Źródło światła", "Gwint", "Moc", "Napięcie Wejściowe", "Barwa światła", "Jasność", "CRI", "Kąt świecenia", "Klasa szczelności", "Wymiar", "Kolor", "Wykonanie (materiał)", "Gwarancja"], 12)
    name = product["name"]
    source_text = normalize(product.get("sourceDescription", ""))
    lower = f"{name} {source_text}".casefold()
    source = attr(product, "Źródło światła", "Gwint")
    power_match = re.search(r"(?i)\b\d+(?:[.,]\d+)?\s*W\b", name)
    source_power_match = re.search(r"(?i)(?:moc(?:y| wynoszącej)?|LED\s+o\s+mocy)\s*(\d+(?:[.,]\d+)?\s*W)\b", source_text)
    power = attr(product, "Moc") or (normalize(power_match.group(0)) if power_match else "") or (normalize(source_power_match.group(1)) if source_power_match else "")
    color_temp = attr(product, "Barwa światła")
    cct_match = re.search(r"(?i)\b(?:temperatur\w*\s+barwow\w*|barw\w*\s+światła)?\s*(\d{4,5}\s*K)\b", source_text)
    cct = normalize(cct_match.group(1)) if cct_match else ""
    lumens = attr(product, "Jasność")
    lumen_match = re.search(r"(?i)strumie\w*\s+świetln\w*\D{0,12}(\d+(?:[.,]\d+)?\s*lm)\b", source_text)
    lumens = lumens or (normalize(lumen_match.group(1)) if lumen_match else "")
    ip_match = re.search(r"(?i)\bIP\s*\d{2}\b", name)
    ip = attr(product, "Klasa szczelności") or (normalize(ip_match.group(0)) if ip_match else "")
    size = attr(product, "Wymiar")
    color = product_color(product)
    if not color:
        source_color = re.search(r"(?i)\b(?:kolorystyk\w*|kolorze)\s+(czarn\w*|biał\w*|srebr\w*|złot\w*|szar\w*)", source_text)
        color = normalize(source_color.group(1)) if source_color else ""
    voltage_match = re.search(r"(?i)\b\d{1,3}(?:\s*[-–]\s*\d{1,3})?\s*V\b", name)
    source_voltage_match = re.search(r"(?i)(?:zasilani\w*|napięci\w*)\s*(\d{1,3}(?:\s*[-–]\s*\d{1,3})?\s*V)\b", source_text)
    voltage = attr(product, "Napięcie Wejściowe") or (normalize(voltage_match.group(0)) if voltage_match else "") or (normalize(source_voltage_match.group(1)) if source_voltage_match else "")
    mounting = attr(product, "Montaż")
    form = f"montaż {mounting.casefold()}" if mounting else next(
        (
            label
            for token, label in (
                ("zwieszan", "montaż zwieszany"),
                ("wisząc", "lampa wisząca"),
                ("wpuszcz", "montaż wpuszczany"),
                ("natynk", "montaż natynkowy"),
                ("kinkiet", "oprawa ścienna"),
                ("plafon", "oprawa sufitowa"),
                ("naświetl", "naświetlacz"),
                ("projektor", "projektor szynowy"),
                ("szynow", "reflektor szynowy"),
                ("stołow", "lampa stołowa"),
                ("ogrod", "oprawa ogrodowa"),
            )
            if token in lower
        ),
        "oprawa systemu Candor" if product["categoryRoot"] == "Candor" else f"oprawa {product['category'].split('/')[-1].casefold()}" if "/" in product["category"] else "oprawa dekoracyjna",
    )
    derived_specs = [("Moc", power), ("Napięcie", voltage), ("Strumień świetlny", lumens), ("Temperatura barwowa", cct), ("Kolor", color), ("Klasa szczelności", ip)]
    existing = {label.casefold() for label, _ in specs}
    for label, value in derived_specs:
        if value and label.casefold() not in existing:
            specs.append((label, value))
            existing.add(label.casefold())
    equipment = join_polish([
        "bez źródła LED" if "bez led" in lower else "",
        "bez zasilacza" if "bez zasilacza" in lower else "",
        "klosz mleczny" if "klosz mlecz" in lower else "",
        "klosz mikropryzmatyczny" if "mikropryz" in lower else "",
        "regulacja CCT" if "cct" in lower else "",
        "głośnik Bluetooth" if "bluetooth" in name.casefold() and "głośnik" in name.casefold() else "",
    ])
    code = product["code"]
    sections = [
        {"label": "Światło", "heading": f"{power or source or 'Oprawa'} w wariancie {color_temp or color or code}", "paragraphs": [f"Pełna nazwa wariantu: {name}. {exact_spec_sentence(specs[:5])}", f"Zasilanie: {voltage}{f'; moc: {power}' if power else ''}{f'; wyposażenie: {equipment}' if equipment else ''}." if voltage else f"Kod {code} identyfikuje sposób zasilania i elementy przyłączeniowe{f'; wyposażenie wariantu: {equipment}' if equipment else ''}."]},
        {"label": "Forma oprawy", "heading": f"{sentence_case(form)}{f', kolor {color}' if color else ''}", "paragraphs": [exact_spec_sentence([(k, v) for k, v in [("Kolor", color), ("Wymiar", size), ("Klasa szczelności", ip), ("Forma", form)] if v]), "Wymiar, wykończenie i sposób montażu decydują o dopasowaniu oprawy do przygotowanego miejsca."]},
        {"label": "Dobór", "heading": "Zasilanie, źródło światła i warunki pracy", "paragraphs": [f"Dla modelu {code} porównaj napięcie {voltage or 'z karty produktu'}{f', moc {power}' if power else ''}{f' i klasę {ip}' if ip else ''} z przygotowaną instalacją.", f"Ten wariant jest oznaczony jako {equipment}; wskazane elementy trzeba uwzględnić przy kompletacji." if equipment else f"Sposób mocowania {form} oraz wymagane elementy instalacyjne sprawdź przed zamówieniem oprawy {code}."],
        },
    ]
    benefits = [x for x in [f"Moc oprawy {power}" if power else "", f"Strumień świetlny {lumens}" if lumens else "", f"Temperatura barwowa {cct}" if cct else "", f"Napięcie zasilania {voltage}" if voltage else "", f"Wymiar oprawy {size}" if size else "", f"Wariant kolorystyczny {color}" if color else "", sentence_case(form), sentence_case(equipment) if equipment else ""] if x]
    applications = [f"Zastosowanie oprawy w formie: {form}", f"Montaż w warunkach zgodnych z klasą {ip}" if ip else f"Montaż po sprawdzeniu miejsca pracy dla oprawy {code}"]
    checks = [x for x in [f"Sprawdź źródło lub trzonek: {source}" if source else "", f"Porównaj moc oprawy: {power}" if power else "", f"Porównaj strumień: {lumens}" if lumens else "", f"Porównaj wymiar montażowy: {size}" if size else "", f"Dobierz warunki do klasy szczelności {ip}" if ip else ""] if x]
    notes = ["Przed pracami odłącz zasilanie i sprawdź kompletność elementów", "Warunki montażu dopasuj do klasy szczelności wskazanej w danych"]
    return finish(product, sections, benefits, applications, checks, notes, specs)


def light_source_editorial(product: dict[str, Any]) -> dict[str, Any]:
    specs = preferred_specs(product, ["Trzonek", "Gwint", "Moc", "Napięcie Wejściowe", "Barwa światła", "Jasność", "CRI", "Kąt świecenia", "Klasa Energetyczna", "Klasa energetyczna", "Trwałość", "Wymiar", "Gwarancja"], 12)
    name = product["name"]
    source = normalize(product.get("sourceDescription", ""))
    lower = f"{name} {source}".casefold()
    is_tube = "świetlów" in lower
    is_uvc = "uv-c" in lower or "uvc" in lower or "bakteriobój" in lower
    base_match = re.search(r"(?i)\b(?:E14|E27|E40|G4|G6\.35|G9|G10Q|G13|G24Q-?\d|GX24Q-?\d|GR8|GR10Q|GU10|GU11|GX53|2G7|2G11|R7S|T5|T8|T9|MR11|MR16|AR111)\b", name)
    power_match = re.search(r"(?i)\b\d+(?:[.,]\d+)?\s*W\b", name)
    base = attr(product, "Trzonek", "Gwint") or (base_match.group(0).upper() if base_match else "")
    power = attr(product, "Moc") or (normalize(power_match.group(0)).replace(" ", "") if power_match else "")
    if power and not any(label.casefold() == "moc" for label, _ in specs):
        specs.insert(0, ("Moc", power))
    if base and not any(label.casefold() in {"trzonek", "gwint"} for label, _ in specs):
        specs.insert(0, ("Trzonek", base))
    cct = name_value(product, r"\b\d{4,5}\s*K\b")
    color = attr(product, "Barwa światła") or cct
    lumens = attr(product, "Jasność") or name_value(product, r"\b\d+(?:[.,]\d+)?\s*lm\b")
    cri = attr(product, "CRI")
    size = attr(product, "Wymiar")
    if not size and is_tube:
        size = attr(product, "Długość przewodu") or name_value(product, r"\b\d+(?:[.,]\d+)?\s*cm\b")
    voltage = attr(product, "Napięcie Wejściowe") or name_value(product, r"\b(?:12|24|230)\s*V(?:\s*AC/DC)?\b")
    angle = attr(product, "Kąt świecenia") or name_value(product, r"\b\d{2,3}\s*(?:°|st\.?)\b")
    if is_tube:
        specs = [("Długość", value) if label.casefold() == "długość przewodu" else (label, value) for label, value in specs]
    derived = [(label, value) for label, value in [("Trzonek lub format", base), ("Moc", power), ("Napięcie", voltage), ("Barwa światła", color), ("Strumień świetlny", lumens), ("CRI", cri), ("Kąt świecenia", angle), ("Długość", size)] if value]
    existing = {label.casefold() for label, _ in specs}
    for label, value in derived:
        if label.casefold() not in existing:
            specs.append((label, value))
            existing.add(label.casefold())

    code = product["code"]
    if is_uvc:
        sections = [
            {"label": "Promieniowanie UV-C", "heading": f"Świetlówka {base or 'UV-C'} o mocy {power or code}", "paragraphs": [f"{name}. Opis źródłowy wskazuje emisję promieniowania UV-C o efekcie bakteriobójczym.", f"Indeks handlowy: {code}; EAN: {product['ean']}; {exact_spec_sentence(derived[:4])}"]},
            {"label": "Dopasowanie do urządzenia", "heading": f"Format {base or 'świetlówki'}{f' i długość {size}' if size else ''}", "paragraphs": [exact_spec_sentence([(label, value) for label, value in [("Format", base), ("Moc", power), ("Długość", size)] if value]), "To źródło należy stosować wyłącznie w urządzeniu przewidzianym dla świetlówki UV-C o zgodnym formacie, mocy i wymiarze."]},
            {"label": "Użytkowanie", "heading": "Osłona urządzenia, instrukcja i wymiana źródła", "paragraphs": ["Promieniowanie UV-C wymaga przestrzegania instrukcji urządzenia; świetlówki nie należy traktować jak zwykłego źródła do oświetlania pomieszczenia.", "Wymianę wykonuj przy odłączonym zasilaniu, a sposób osłonięcia źródła i procedurę uruchomienia zachowaj zgodnie z dokumentacją urządzenia."]},
        ]
        benefits = [f"Źródło UV-C o mocy {power}" if power else "Źródło promieniowania UV-C", f"Format {base}" if base else f"Kod modelu {code}", f"Długość {size}" if size else ""]
        applications = ["Urządzenia przeznaczone do pracy ze świetlówką UV-C", "Wymiana źródła po zgodności formatu, mocy i wymiaru"]
        checks = [f"Format źródła: {base}" if base else f"Indeks handlowy: {code}", f"Moc: {power}" if power else "", f"Długość: {size}" if size else "", "Instrukcja i osłona urządzenia UV-C"]
        notes = ["Nie używaj świetlówki UV-C jako zwykłego oświetlenia pomieszczenia", "Wymieniaj źródło przy odłączonym zasilaniu i według instrukcji urządzenia"]
        return finish(product, sections, benefits, applications, checks, notes, specs or derived)

    kind = "świetlówka LED" if "świetlówka led" in lower else "świetlówka" if is_tube else "żarówka LED" if "led" in lower else "źródło światła"
    light_text = (
        "Barwa mięsna jest przeznaczona do ekspozycji produktów, dla których ważne jest podkreślenie czerwonych odcieni."
        if "mięsn" in lower or "food" in lower
        else light_guidance(color, lumens)
        if color
        else f"Wariant {code} dobiera się po mocy, formacie źródła i parametrach oprawy."
    )
    sections = [
        {"label": "Parametry światła", "heading": f"{sentence_case(kind)} {color or code}{f' — {power}' if power else ''}", "paragraphs": [f"{name}. {exact_spec_sentence([(label, value) for label, value in [('Barwa światła', color), ('Strumień świetlny', lumens), ('CRI', cri), ('Moc', power), ('Kąt świecenia', angle)] if value])}", light_text]},
        {"label": "Dopasowanie do oprawy", "heading": f"{base or kind}{f' — długość {size}' if size else ''}", "paragraphs": [exact_spec_sentence([(label, value) for label, value in [("Trzonek lub format", base), ("Długość lub wymiar", size), ("Napięcie", voltage)] if value]), "Przed zakupem sprawdź standard mocowania, ilość miejsca w oprawie oraz napięcie wymagane przez konkretny wariant źródła."]},
        {"label": "Wybór wariantu", "heading": "Moc, strumień, barwa i pełny indeks handlowy", "paragraphs": [f"W tej rodzinie różnice mogą dotyczyć mocy {power or 'źródła'}, barwy {color or 'światła'}, strumienia, kąta oraz wymiaru; porównuj wyłącznie wartości przypisane do indeksu {code}.", f"Indeks handlowy: {code}; EAN: {product['ean']}."]},
    ]
    benefits = [x for x in [f"Barwa światła {color}" if color else "", f"Strumień świetlny {lumens}" if lumens else "", f"Moc źródła {power}" if power else "", f"Trzonek w standardzie {base}" if base else ""] if x]
    applications = [f"Oprawy przeznaczone dla formatu {base}" if base else f"Oprawy przeznaczone dla źródła typu {kind}", "Ekspozycja produktów spożywczych wymagająca barwy mięsnej" if "mięsn" in lower or "food" in lower else light_application(color) if color else "Wymiana źródła po zgodności mocy, napięcia i wymiaru"]
    checks = [x for x in [f"Trzonek lub format: {base}" if base else "", f"Moc: {power}" if power else "", f"Barwa: {color}" if color else "", f"Strumień: {lumens}" if lumens else "", f"Wymiar: {size}" if size else ""] if x]
    notes = ["Wymieniaj źródło światła przy odłączonym zasilaniu"]
    if size:
        notes.append("Sprawdź, czy wymiar źródła mieści się w oprawie")
    elif base:
        notes.append(f"Przed montażem porównaj trzonek oprawy z oznaczeniem {base}")
    else:
        notes.append("Przed montażem porównaj typ źródła z oznaczeniem oprawy")
    return finish(product, sections, benefits, applications, checks, notes, specs)


def electrical_editorial(product: dict[str, Any]) -> dict[str, Any]:
    specs = preferred_specs(product, ["Napięcie Wejściowe", "Napięcie Wyjściowe", "Prąd", "Klasa szczelności", "Wymiar", "Kolor", "Długość", "Gwarancja"], 9)
    name = product["name"]
    lower = name.casefold()
    leaf = product["category"].split("/")[-1]
    code = product["code"]
    voltage = attr(product, "Napięcie Wejściowe", "Napięcie Wyjściowe") or name_value(product, r"\b\d+(?:[.,]\d+)?\s*V\b")
    current = attr(product, "Prąd") or name_value(product, r"\b\d+(?:[.,]\d+)?\s*A\b")
    ip = attr(product, "Klasa szczelności") or name_value(product, r"\bIP\s*\d{2}\b")
    color = product_color(product)
    size = attr(product, "Wymiar")
    range_match = re.search(r"(?i)\b\d+(?:[.,]\d+)?\s*m\b", name)
    range_value = normalize(range_match.group(0)) if range_match else ""
    tones_match = re.search(r"(?i)\b(\d+)\s*dźwięk", name)
    tones = f"{tones_match.group(1)} dźwięków" if tones_match else ""
    wireless = "bezprzewod" in lower

    if "dzwonek" in lower:
        kind = "dzwonek bezprzewodowy" if wireless else "dzwonek przewodowy"
        tone_type = "dwutonowy" if "dwuton" in lower else "jednotonowy" if "jednoton" in lower else "gong" if "gong" in lower else ""
        mounting = "na szynę" if "szyn" in lower else ""
        known = [(label, value) for label, value in [("Zasilanie", voltage or ("bateryjne" if "bat" in lower else "")), ("Zasięg", range_value), ("Liczba melodii", tones), ("Sygnał", tone_type), ("Montaż", mounting), ("Kolor", color)] if value]
        sections = [
            {"label": "Sygnał wejściowy", "heading": f"{sentence_case(kind)}{f' — {tones}' if tones else ''}", "paragraphs": [f"{name}. Indeks handlowy: {code}.", f"Model jest przeznaczony do sygnalizowania wywołania{f' i oferuje {tones}' if tones else f' w wersji {tone_type}' if tone_type else ''}."]},
            {"label": "Zasilanie i zasięg", "heading": f"{voltage or ('Zasilanie bateryjne' if 'bat' in lower else 'Parametry montażowe')}{f'; zasięg {range_value}' if range_value else ''}", "paragraphs": [exact_spec_sentence(known), "Dla wersji bezprzewodowej porównaj miejsce nadajnika i odbiornika z deklarowanym zasięgiem, a dla wariantu zasilanego z instalacji przygotuj właściwe napięcie." if wireless else "Przed montażem porównaj napięcie z instalacją oraz sposób zamocowania dzwonka w wybranym miejscu."]},
            {"label": "Dobór wariantu", "heading": f"Model {code}, sposób zasilania i sygnał", "paragraphs": [f"Indeks handlowy: {code}; indeks handlowy: {product['code']}; EAN: {product['ean']}.", "Przed zakupem sprawdź, czy zestaw obejmuje potrzebny nadajnik i odbiornik oraz jaki rodzaj zasilania przewidziano dla każdego elementu."]},
        ]
        benefits = [sentence_case(kind), f"Zasięg {range_value}" if range_value else f"Sygnał {tone_type}" if tone_type else f"Kod modelu {code}", f"Wybór spośród {tones}" if tones else f"Zasilanie {voltage}" if voltage else ""]
        applications = ["Sygnalizacja wejścia w domu, lokalu lub pomieszczeniu użytkowym", "Montaż bezprzewodowy" if wireless else f"Montaż {mounting}" if mounting else "Instalacja dzwonkowa zgodna z napięciem modelu"]
        checks = [f"Sposób zasilania: {voltage or ('bateryjny' if 'bat' in lower else 'z instalacji')}", f"Zasięg: {range_value}" if range_value else f"Rodzaj sygnału: {tone_type}" if tone_type else f"Kod modelu: {code}", "Zawartość zestawu: nadajnik i odbiornik" if wireless else f"Sposób montażu: {mounting}" if mounting else ""]
        notes = ["Przed uruchomieniem zaprogramuj nadajnik zgodnie z instrukcją modelu" if wireless else "Przed podłączeniem odłącz napięcie w obwodzie dzwonka", "Baterie dobierz według oznaczeń producenta" if "bat" in lower else "Podłączenie do instalacji powierz osobie z odpowiednimi kwalifikacjami"]
        return finish(product, sections, benefits, applications, checks, notes, specs or known)

    kind_roles = [
        (("przewód", "przedłużacz"), "przewód zasilający lub instalacyjny", "łączenie punktów instalacji przy zachowaniu liczby żył, przekroju i napięcia znamionowego"),
        (("złączka", "końcówka", "wtyczka", "adapter", "przejściówka", "łącznik"), "element połączeniowy", "łączenie elementów o zgodnym przekroju, standardzie styku lub typie złącza"),
        (("dławik",), "dławik kablowy", "wprowadzenie przewodu do obudowy z doborem gwintu i uszczelnienia"),
        (("puszka", "kaseta"), "element zabudowy instalacyjnej", "osadzenie osprzętu w miejscu i systemie wskazanym dla danego modelu"),
        (("bezpiecznik",), "wkładka bezpiecznikowa", "zabezpieczenie obwodu po doborze charakterystyki, prądu i formatu wkładki"),
        (("licznik energii",), "licznik energii", "pomiar energii w instalacji o parametrach zgodnych z oznaczeniem licznika"),
        (("ładowarka usb",), "moduł ładowarki USB", "uzupełnienie zgodnego systemu osprzętu o punkt ładowania USB"),
        (("cyna",), "materiał lutowniczy", "lutowanie po dobraniu średnicy i składu spoiwa do wykonywanego połączenia"),
        (("maskownica", "nakrętka"), "element wykończeniowy", "wykończenie lub zamknięcie elementu o zgodnym wymiarze i kodzie"),
        (("oprawa",), "oprawa oświetleniowa", "montaż źródeł światła zgodnych z liczbą punktów, mocą i sposobem zasilania"),
    ]
    kind, role = next(((kind, role) for tokens, kind, role in kind_roles if any(token in lower for token in tokens)), (leaf.casefold(), "kompletacja instalacji po porównaniu kodu, wymiaru i parametrów elektrycznych"))
    form_values = []
    for pattern, label in [
        (r"\b\d+\s*x\s*\d+(?:[.,]\d+)?\b", "Układ żył lub pól"),
        (r"\bPG\s*-?\s*\d+(?:[.,]\d+)?\b", "Rozmiar gwintu"),
        (r"\b\d+(?:[.,]\d+)?\s*mm\b", "Wymiar"),
        (r"\b\d+(?:[.,]\d+)?\s*m\b", "Długość"),
    ]:
        value = name_value(product, pattern)
        if value:
            form_values.append((label, value))
    electrical = [(label, value) for label, value in [("Napięcie", voltage), ("Prąd", current), ("Klasa szczelności", ip)] if value]
    sections = [
        {"label": "Funkcja elementu", "heading": f"{sentence_case(kind)} — model {code}", "paragraphs": [f"{name}. Indeks handlowy: {code}; EAN: {product['ean']}.", f"Zastosowanie elementu: {role}."]},
        {"label": "Parametry doboru", "heading": f"{join_polish([value for _, value in (electrical + form_values)[:3]]) or code}: cechy konkretnego wariantu", "paragraphs": [exact_spec_sentence((electrical + form_values) or specs[:4]), "Przed zamówieniem porównaj wszystkie wymiary, standard połączenia oraz wartości elektryczne występujące przy tym kodzie."]},
        {"label": "Montaż i zgodność", "heading": "Pełny indeks, element współpracujący i miejsce instalacji", "paragraphs": [source_sentences(product, 1)[0] if source_sentences(product, 1) else f"Indeks handlowy: {code}; EAN: {product['ean']}.", "Nie zastępuj tego wariantu podobnym elementem wyłącznie na podstawie wyglądu — potwierdź funkcję, format i sposób połączenia."]},
    ]
    benefits = [sentence_case(kind), *[f"{label}: {value}" for label, value in (electrical + form_values)[:3]]]
    applications = [sentence_case(role), f"Kompletacja instalacji w grupie {leaf}"]
    checks = [f"Kod elementu: {code}", *[f"{label}: {value}" for label, value in (electrical + form_values)[:3]]]
    notes = ["Montaż instalacji elektrycznej powierz osobie z odpowiednimi kwalifikacjami", "Przed pracami odłącz zasilanie i sprawdź brak napięcia"]
    return finish(product, sections, benefits, applications, checks, notes, specs or electrical + form_values)


def name_value(product: dict[str, Any], pattern: str) -> str:
    match = re.search(pattern, f"{product['name']} {product.get('sourceDescription', '')}", re.I)
    return normalize(match.group(0)) if match else ""


def product_color(product: dict[str, Any]) -> str:
    direct = attr(product, "Kolor", "Kolor profilu", "Wykończenie")
    if direct:
        return direct
    match = re.search(
        r"(?i)\b(?:biały|biała|białe|beż|beżowy|beżowa|czarny|czarna|czarne|srebro|srebrny|srebrna|"
        r"złoty|złota|ecru|czekolada|grafit|szary|szara|zielony|zielona|żółty|żółta|różowy|różowa)\b",
        product["name"],
    )
    return normalize(match.group(0)) if match else ""


def electrical_frame_editorial(product: dict[str, Any]) -> dict[str, Any]:
    specs = public_specs(product)[:8]
    name = product["name"]
    lower = name.casefold()
    code = product["code"]
    series = name.split()[0].upper() if name.split() else product["producer"]
    color = product_color(product)
    count_names = [
        ("pięciokrot", "pięć modułów"),
        ("poczwór", "cztery moduły"),
        ("czterokrot", "cztery moduły"),
        ("potrój", "trzy moduły"),
        ("trójkrot", "trzy moduły"),
        ("podwójn", "dwa moduły"),
        ("dwukrot", "dwa moduły"),
        ("pojedyncz", "jeden moduł"),
    ]
    capacity = next((value for token, value in count_names if token in lower), "")
    frame_type = attr(product, "Typ") or ("ramka ozdobna mocująca" if "ozdobn" in lower and "mocując" in lower else "ramka osprzętowa")
    orientation = "pionowa" if "pionow" in lower else "pozioma" if "poziom" in lower else "pionowa lub pozioma" if "uniwersal" in product.get("sourceDescription", "").casefold() else ""
    aligned_source = source_sentences(product, 1) if "ramk" in product.get("sourceDescription", "").casefold() else []
    sections = [
        {
            "label": "Ramka osprzętowa",
            "heading": f"Seria {series}, {capacity or frame_type}{f', kolor {color}' if color else ''}",
            "paragraphs": [
                f"{name}. Indeks handlowy {code} wskazuje konkretną ramkę w obrębie serii {series}.",
                aligned_source[0] if aligned_source else f"Wariant przewidziano na {capacity}; mechanizmy i elementy wykończeniowe trzeba dobrać z tej samej serii." if capacity else f"To {frame_type}; zgodny mechanizm i elementy wykończeniowe trzeba dobrać z tej samej serii.",
            ],
        },
        {
            "label": "Układ i wykończenie",
            "heading": f"{sentence_case(capacity or frame_type)}{f' w układzie {orientation}' if orientation else ''}",
            "paragraphs": [
                f"Kolor ramki: {color}; orientacja: {orientation}." if color and orientation else f"Wykończenie: {color or 'zgodne z pełną nazwą'}; typ: {frame_type}{f'; pojemność: {capacity}' if capacity else ''}.",
                "Przy zestawie wielokrotnym sprawdź liczbę mechanizmów, ich rozmieszczenie oraz zgodność mocowań z ramką." if capacity else "Przed kompletacją porównaj typ mechanizmu, serię oraz sposób mocowania z pełnym kodem ramki.",
            ],
        },
        {
            "label": "Kompletacja serii",
            "heading": "Mechanizmy, klawisze i ramka z jednego systemu",
            "paragraphs": [
                f"Do zamówienia użyj pełnego oznaczenia {code} i numeru EAN {product['ean']}; sam kolor nie wystarcza do potwierdzenia zgodności.",
                "Przed montażem ułóż komplet mechanizmów w docelowej kolejności i porównaj go z liczbą pól ramki." if capacity else "Przed montażem porównaj sposób osadzenia mechanizmu z funkcją ramki mocującej.",
            ],
        },
    ]
    benefits = [f"Miejsce na {capacity}" if capacity else sentence_case(frame_type), f"Kolor {color}" if color else f"Ramka serii {series}"]
    if orientation:
        benefits.append(f"Orientacja {orientation}")
    applications = [f"Wykończenie punktu osprzętowego w serii {series}", "Budowa zestawu pojedynczego lub wielokrotnego zgodnie z liczbą pól" if capacity else "Mocowanie mechanizmu zgodnego z kodem i serią ramki"]
    checks = [f"Seria osprzętu: {series}", f"Liczba pól: {capacity}" if capacity else f"Rodzaj ramki: {frame_type}", f"Kolor: {color}" if color else f"Kod ramki: {code}"]
    if orientation:
        checks.append(f"Orientacja: {orientation}")
    notes = ["Przed montażem sprawdź zgodność ramki z mechanizmami i sposobem mocowania", "Najpierw rozplanuj kolejność mechanizmów w ramce wielokrotnej"]
    return finish(product, sections, benefits, applications, checks, notes, specs or [("Seria", series), ("Liczba pól", capacity or "zgodna z kodem"), ("Kolor", color)])


def electrical_switch_editorial(product: dict[str, Any]) -> dict[str, Any]:
    specs = public_specs(product)[:9]
    name = product["name"]
    lower = f"{name} {product.get('sourceDescription', '')}".casefold()
    code = product["code"]
    series = name.split()[0].upper() if name.split() else product["producer"]
    color = product_color(product)
    switch_type = (
        "krzyżowy"
        if "krzyżow" in lower
        else "schodowy podwójny"
        if "schodow" in lower and "podwójn" in lower
        else "schodowy"
        if "schodow" in lower
        else "podwójny"
        if "podwójn" in lower
        else "przycisk dzwonkowy"
        if "dzwonek" in lower or "dzwonk" in lower
        else "pojedynczy"
        if "pojedyncz" in lower
        else "zgodny z oznaczeniem produktu"
    )
    voltage = attr(product, "Napięcie", "Napięcie Wejściowe") or name_value(product, r"\b\d{2,3}\s*V\b")
    current = attr(product, "Prąd") or name_value(product, r"(?<![\d.,])\d{1,2}(?:[.,]\d+)?\s*A\b")
    ip = attr(product, "Klasa szczelności") or name_value(product, r"\bIP\s*\d{2}\b")
    aligned_source = source_sentences(product, 2) if any(term in product.get("sourceDescription", "").casefold() for term in ("łącznik", "wyłącznik", "włącznik")) else []
    function_text = {
        "krzyżowy": "Łącznik krzyżowy stosuje się pomiędzy łącznikami schodowymi, gdy jeden obwód ma być sterowany z co najmniej trzech miejsc.",
        "schodowy": "Łącznik schodowy jest elementem układu, w którym jednym obwodem oświetlenia steruje się z dwóch miejsc.",
        "schodowy podwójny": "Wariant podwójny łączy dwa tory łącznika schodowego w jednym mechanizmie; schemat połączenia trzeba dobrać do obu obwodów.",
        "podwójny": "Dwa klawisze pozwalają rozdzielić sterowanie dwoma obwodami, o ile instalacja została przygotowana do takiego układu.",
        "przycisk dzwonkowy": "Mechanizm opisany jako dzwonkowy dobiera się do obwodu wymagającego przycisku chwilowego i zgodnego schematu połączenia.",
    }.get(switch_type, "Funkcję mechanizmu określa pełne oznaczenie producenta; dobór trzeba oprzeć na schemacie instalacji.")
    parameter_text = aligned_source[1] if len(aligned_source) > 1 else "Typ łącznika musi odpowiadać schematowi obwodu, liczbie punktów sterowania i pozostałym mechanizmom w układzie."
    if len(parameter_text) < 45:
        parameter_text = f"{parameter_text.removesuffix('.')} — funkcję mechanizmu trzeba porównać ze schematem przygotowanego obwodu."
    sections = [
        {"label": "Funkcja łącznika", "heading": f"{sentence_case(switch_type)} w serii {series}", "paragraphs": [aligned_source[0] if aligned_source else function_text, f"Pełna nazwa wariantu: {name}. Indeks handlowy: {code}."]},
        {"label": "Obwód i parametry", "heading": f"{voltage or 'Parametry z oznaczenia'}{f', {current}' if current else ''}{f', {ip}' if ip else ''}", "paragraphs": [exact_spec_sentence([(k, v) for k, v in [("Napięcie", voltage), ("Prąd", current), ("Klasa szczelności", ip)] if v]), parameter_text]},
        {"label": "Seria i wykończenie", "heading": f"{f'Kolor {color}' if color else f'Wariant {code}'} oraz osprzęt serii {series}", "paragraphs": [f"Wariant kolorystyczny: {color}; seria: {series}; EAN: {product['ean']}." if color else f"Seria: {series}; kod: {code}; EAN: {product['ean']}.", "Ramkę, klawisz i pozostałe elementy wykończeniowe dobierz do tej samej serii osprzętu."]},
    ]
    benefits = [f"Funkcja: łącznik {switch_type}", f"Seria osprzętu {series}", f"Kolor {color}" if color else f"Kod {code}"]
    applications = [function_text.removesuffix("."), f"Kompletacja punktu sterowania w serii {series}"]
    checks = [f"Schemat łącznika: {switch_type}", f"Seria i kod: {series}, {code}", f"Napięcie: {voltage}" if voltage else f"Kolor: {color}" if color else f"EAN: {product['ean']}"]
    if ip:
        checks.append(f"Klasa szczelności: {ip}")
    notes = ["Montaż powierz osobie z odpowiednimi kwalifikacjami", "Przed pracami odłącz zasilanie i potwierdź brak napięcia"]
    return finish(product, sections, benefits, applications, checks, notes, specs or [("Typ", switch_type), ("Seria", series), ("Kolor", color)])


def electrical_socket_editorial(product: dict[str, Any]) -> dict[str, Any]:
    specs = public_specs(product)[:9]
    name = product["name"]
    lower = f"{name} {product.get('sourceDescription', '')}".casefold()
    code = product["code"]
    series = name.split()[0].upper() if name.split() else product["producer"]
    color = product_color(product)
    voltage = attr(product, "Napięcie", "Napięcie Wejściowe") or name_value(product, r"\b\d{2,3}\s*V\b")
    current = attr(product, "Prąd") or name_value(product, r"(?<![\d.,])\d{1,2}(?:[.,]\d+)?\s*A\b")
    ip = attr(product, "Klasa szczelności") or name_value(product, r"\bIP\s*\d{2}\b")
    socket_type = join_polish([
        "podwójne" if "podwójn" in lower else "pojedyncze",
        "z uziemieniem" if "uziem" in lower else "",
        "z USB" if "usb" in lower else "",
    ])
    sections = [
        {"label": "Typ gniazda", "heading": f"Gniazdo {socket_type} w serii {series}", "paragraphs": [f"{name}. Oznaczenie wskazuje gniazdo {socket_type}{f' w kolorze {color}' if color else ''}.", f"Indeks handlowy {code} oraz EAN {product['ean']} identyfikują konkretny mechanizm i jego wykończenie."]},
        {"label": "Parametry instalacji", "heading": f"{voltage or f'Model {code}'}{f', {current}' if current else ''}{f' i klasa {ip}' if ip else ''}", "paragraphs": [exact_spec_sentence([(k, v) for k, v in [("Napięcie", voltage), ("Prąd", current), ("Klasa szczelności", ip)] if v]), "Parametry gniazda trzeba porównać z obwodem, przewodami ochronnymi oraz warunkami w miejscu montażu."]},
        {"label": "Kompletacja osprzętu", "heading": f"Ramka i elementy serii {series}", "paragraphs": [f"Kolor: {color}; seria: {series}." if color else f"Seria osprzętu: {series}; kod mechanizmu: {code}.", "Przed zamówieniem sprawdź, czy produkt jest mechanizmem, kompletem z ramką czy elementem wymagającym osobnego wykończenia."]},
    ]
    benefits = [f"Gniazdo {socket_type}", f"Seria osprzętu {series}", f"Kolor {color}" if color else f"Kod {code}"]
    applications = ["Punkt zasilający zgodny z parametrami obwodu", f"Kompletacja osprzętu w serii {series}"]
    checks = [f"Typ: {socket_type}", f"Seria i kod: {series}, {code}", f"Napięcie: {voltage}" if voltage else f"Kolor: {color}" if color else f"EAN: {product['ean']}"]
    if current:
        checks.append(f"Prąd znamionowy: {current}")
    if ip and len(checks) < 4:
        checks.append(f"Klasa szczelności: {ip}")
    notes = ["Montaż powierz osobie z odpowiednimi kwalifikacjami", "Przed pracami odłącz zasilanie i potwierdź brak napięcia"]
    return finish(product, sections, benefits, applications, checks, notes, specs or [("Typ", socket_type), ("Seria", series), ("Kolor", color)])


def distribution_board_editorial(product: dict[str, Any]) -> dict[str, Any]:
    specs = public_specs(product)[:10]
    code = product["code"]
    kind = attr(product, "Typ") or "rozdzielnica"
    voltage = attr(product, "Zasilanie", "Napięcie", "Napięcie Wejściowe")
    size = attr(product, "Wymiar")
    color = product_color(product)
    fields = attr(product, "Uwagi")
    sections = [
        {"label": "Rozdzielnica", "heading": f"{sentence_case(kind)} — model {code}", "paragraphs": [f"Pełna nazwa produktu: {product['name']}. {exact_spec_sentence(specs[:5])}", "Typ obudowy oraz wyposażenie przyłączeniowe trzeba porównać z projektem rozdziału obwodów."]},
        {"label": "Wymiary i pojemność", "heading": f"{size or 'Wymiary z danych'}{f'; {fields}' if fields else ''}", "paragraphs": [exact_spec_sentence([(k, v) for k, v in [("Wymiar", size), ("Pola", fields), ("Kolor", color)] if v]), "Przed montażem sprawdź miejsce na obudowę, liczbę wymaganych pól i sposób wprowadzenia przewodów."]},
        {"label": "Parametry elektryczne", "heading": f"Zasilanie {voltage or 'zgodne z projektem instalacji'}", "paragraphs": [f"Zasilanie: {voltage}; indeks handlowy: {code}; EAN: {product['ean']}." if voltage else f"Indeks handlowy: {code}; indeks handlowy: {product['code']}; EAN: {product['ean']}.", "Aparaturę, listwy i przewody dobierz według dokumentacji rozdzielnicy oraz parametrów zabezpieczanych obwodów."]},
    ]
    benefits = [f"Typ: {kind}", f"Wymiar {size}" if size else f"Model {code}", f"Liczba pól: {fields}" if fields else f"Kolor {color}" if color else ""]
    applications = ["Rozdział i uporządkowanie obwodów instalacji", "Montaż aparatury zgodnej z pojemnością obudowy"]
    checks = [f"Typ obudowy: {kind}", f"Wymiar: {size}" if size else f"Kod: {code}", f"Zasilanie: {voltage}" if voltage else f"EAN: {product['ean']}"]
    if fields:
        checks.append(f"Pojemność: {fields}")
    notes = ["Dobór i montaż rozdzielnicy powierz osobie z odpowiednimi kwalifikacjami", "Przed pracami odłącz zasilanie i potwierdź brak napięcia"]
    return finish(product, sections, benefits, applications, checks, notes, specs)


def sensor_editorial(product: dict[str, Any]) -> dict[str, Any]:
    specs = public_specs(product)[:12]
    code = product["code"]
    text = normalize(product.get("sourceDescription", ""))
    lower = f"{product['name']} {text}".casefold()
    summaries = source_sentences(product, 3)
    functions = []
    if "dym" in lower:
        functions.append("wykrywanie obecności dymu")
    if "tlenku węgla" in lower or "czad" in lower:
        functions.append("wykrywanie tlenku węgla")
    if "ruch" in lower:
        functions.append("wykrywanie ruchu")
    if "zmierzch" in lower:
        functions.append("reakcja na poziom oświetlenia")
    if not functions:
        functions.append("detekcja zgodna z funkcją podaną przez producenta")

    power = attr(product, "Zasilanie", "Napięcie Wejściowe")
    reach = attr(product, "Zasięg", "Zasięg detekcji")
    sound = attr(product, "Głośność")
    standard = attr(product, "Spełniane normy", "Norma")
    name_power = name_value(product, r"\b\d+(?:[.,]\d+)?\s*W\b")
    ip = attr(product, "Klasa szczelności") or name_value(product, r"\bIP\s*\d{2}\b")
    angle = name_value(product, r"\b(?:90|120|140|160|180|240|270|300|360)\s*(?:°|ST\.?|STOPNI)\b")
    is_alarm = any(term in lower for term in ("dym", "tlenku węgla", "czad"))
    technical = [(label, value) for label, value in [("Zasilanie", power), ("Zasięg", reach), ("Głośność", sound), ("Norma", standard), ("Moc z oznaczenia", name_power), ("Klasa szczelności", ip), ("Kąt detekcji", angle)] if value]
    if not technical:
        technical = specs[:5]

    sections = [
        {
            "label": "Funkcja czujnika",
            "heading": sentence_case(join_polish(functions)),
            "paragraphs": [
                summaries[0] if is_alarm and summaries else f"{product['name']}. Model {code} realizuje funkcję: {join_polish(functions)}.",
                summaries[1] if is_alarm and len(summaries) > 1 else f"Indeks handlowy: {code}; indeks handlowy: {product['code']}; EAN: {product['ean']}.",
            ],
        },
        {
            "label": "Sygnalizacja i test" if is_alarm else "Detekcja i regulacja",
            "heading": "Sposób alarmowania oraz kontrola działania" if is_alarm else "Kąt, zasięg i ustawienia czujnika",
            "paragraphs": [
                summaries[2] if is_alarm and len(summaries) > 2 else exact_spec_sentence(technical),
                "Przed montażem sprawdź rodzaj sygnalizacji, sposób zasilania i procedurę testową właściwą dla tego modelu." if is_alarm else "Przed montażem porównaj kąt oraz zasięg detekcji, dopuszczalne obciążenie i dostępny zakres regulacji.",
            ],
        },
        {
            "label": "Identyfikacja i montaż",
            "heading": f"{'Instrukcja alarmu' if is_alarm else 'Ustawienie czujnika'} dla modelu {code}",
            "paragraphs": [
                f"Indeks handlowy: {code}; indeks handlowy: {product['code']}; EAN: {product['ean']}.",
                "Miejsce instalacji, odstępy, testy okresowe i wymianę zasilania wykonuj według instrukcji producenta konkretnego urządzenia." if is_alarm else "Położenie czujnika i nastawy dobierz tak, aby wymagany obszar mieścił się w polu detekcji podanym dla modelu.",
            ],
        },
    ]
    benefits = [sentence_case(value) for value in functions]
    if "sygnalizacj" in lower:
        benefits.append("Sygnalizacja opisana w danych producenta")
    if "przycisk test" in lower:
        benefits.append("Przycisk TEST do kontroli działania urządzenia")
    if name_power:
        benefits.append(f"Wartość mocy w oznaczeniu: {name_power}")
    if ip:
        benefits.append(f"Klasa szczelności {ip}")
    if angle:
        benefits.append(f"Kąt detekcji {angle}")
    applications = [f"Monitoring w zakresie: {value}" for value in functions[:2]] if is_alarm else [f"Detekcja w zakresie: {functions[0]}", "Automatyczne sterowanie obwodem zgodnie z ustawieniami czujnika"]
    if len(applications) < 2:
        applications.append("Monitoring przestrzeni zgodnie z przeznaczeniem czujnika")
    checks = [f"Sprawdź zgodność — {label.casefold()}: {value}" for label, value in technical[:4]]
    checks.append(f"Zweryfikuj dokładny model: {code}")
    notes = ["Po montażu wykonaj test zgodnie z instrukcją producenta", "Nie zastępuj wskazanej procedury testowej oceną wizualną urządzenia"] if is_alarm else ["Przed regulacją odłącz zasilanie zgodnie z instrukcją", "Po montażu sprawdź reakcję czujnika w całym wymaganym obszarze"]
    return finish(product, sections, benefits, applications, checks, notes, specs or technical)


def technical_component_editorial(product: dict[str, Any]) -> dict[str, Any]:
    specs = public_specs(product)[:10]
    code = product["code"]
    leaf = product["category"].split("/")[-1]
    summaries = source_sentences(product, 2)
    base = attr(product, "Trzonek", "Gwint")
    voltage = attr(product, "Napięcie", "Napięcie Wejściowe", "Napięcie Wyjściowe")
    current = attr(product, "Natężenie", "Prąd")
    length_match = re.search(r"(?i)\b\d+(?:[.,]\d+)?\s*cm\b", product["name"])
    length = attr(product, "Długość przewodu") or (normalize(length_match.group(0)).replace(" ", "") if length_match else "")
    power_range = name_value(product, r"\b\d+(?:[.,]\d+)?\s*[-–]\s*\d+(?:[.,]\d+)?\s*W\b")
    load = name_value(product, r"\b\d+\s*x\s*\d+(?:[.,]\d+)?\s*W\b")
    power = name_value(product, r"(?<![-–])\b\d+(?:[.,]\d+)?\s*W\b")
    lamp_family = name_value(product, r"\b(?:T5|T8|G5|G8\.5|G12|G13|E27|E40|2G7|2G11)\b")
    control = join_polish(["DALI" if "dali" in product["name"].casefold() else "", "1-10V" if "1-10v" in product["name"].casefold() else ""])
    technical = [(label, value) for label, value in [("Rodzina źródła", base or lamp_family), ("Napięcie", voltage), ("Prąd lub natężenie", current), ("Długość przewodu", length), ("Układ mocy", load or power_range or power), ("Sterowanie", control)] if value]
    if not technical:
        technical = specs[:4]
    name_lower = product["name"].casefold()
    if "oprawk" in name_lower:
        role_text = f"Oprawka {code} jest przeznaczona do źródła z trzonkiem {base or lamp_family or 'zgodnym z oznaczeniem'}; element należy zamontować w kompatybilnej oprawie."
    elif "starter" in name_lower:
        role_text = f"Starter {code} jest elementem układu zapłonowego świetlówki o zakresie mocy podanym przy tym wariancie."
    elif "statecznik" in name_lower:
        role_text = summaries[0] if summaries else f"Statecznik {code} zasila układ źródeł o mocy i liczbie lamp zapisanej w oznaczeniu wariantu."
    elif "układ zapłonowy" in name_lower:
        role_text = summaries[0] if summaries else f"Układ zapłonowy {code} dobiera się do typu lampy oraz zakresu mocy podanego dla tego modelu."
    else:
        role_text = summaries[0] if summaries else f"Element {code} kompletuje układ o parametrach zapisanych przy tym wariancie."
    if len(role_text) < 45:
        role_text = f"{role_text.removesuffix('.')} — funkcję elementu potwierdza pełne oznaczenie producenta {code}."
    sections = [
        {"label": "Funkcja elementu", "heading": f"{leaf}: model {code}", "paragraphs": [role_text]},
        {"label": "Parametry zgodności", "heading": f"{base or lamp_family or load or power_range or voltage or code}: dane do porównania z oprawą", "paragraphs": [exact_spec_sentence(technical), "Dobór wymaga zgodności typu źródła, złącza i wartości elektrycznych podanych dla elementu."]},
        {"label": "Montaż i identyfikacja", "heading": "Pełny indeks przed wymianą lub kompletacją", "paragraphs": [f"Indeks handlowy: {code}; EAN: {product['ean']}.", "Przed pracami odłącz zasilanie, a zamiennik dobierz po pełnym oznaczeniu oraz parametrach urządzenia współpracującego."]},
    ]
    benefits = [f"{label}: {value}" for label, value in technical[:4]]
    if len(benefits) < 2:
        benefits.append(f"Typ elementu: {leaf}")
    if "oprawk" in leaf.casefold() or "oprawk" in product["name"].casefold():
        applications = [f"Mocowanie źródła z trzonkiem {base}" if base else "Mocowanie źródła zgodnego z typem oprawki", "Kompletacja oprawy po parametrach elektrycznych i wymiarach"]
    else:
        applications = [f"Kompletacja układu w grupie {leaf}", "Wymiana elementu po pełnym kodzie i parametrach znamionowych"]
    checks = [f"Sprawdź zgodność — {label.casefold()}: {value}" for label, value in technical[:4]]
    notes = ["Przed montażem odłącz zasilanie i sprawdź brak napięcia", "Podłączenie wykonaj zgodnie ze schematem urządzenia współpracującego"]
    return finish(product, sections, benefits, applications, checks, notes, specs or technical)


def module_editorial(product: dict[str, Any]) -> dict[str, Any]:
    specs = preferred_specs(product, ["Barwa światła", "Napięcie Wejściowe", "Moc", "Prąd", "Ilość diod", "Typ diody", "Klasa szczelności", "Wymiar", "Gwarancja"], 9)
    name = product["name"]
    lower = name.casefold()
    color = attr(product, "Barwa światła")
    if not color:
        color_terms = [
            ("biały neutralny", "Biała neutralna"), ("biała neutralna", "Biała neutralna"),
            ("biały zimny", "Biała zimna"), ("biała zimna", "Biała zimna"),
            ("biały ciepły", "Biała ciepła"), ("biała ciepła", "Biała ciepła"),
            ("czerwony", "Czerwona"), ("czerwona", "Czerwona"), ("zielony", "Zielona"),
            ("zielona", "Zielona"), ("niebieski", "Niebieska"), ("blue", "Niebieska"),
            ("red", "Czerwona"), ("green", "Zielona"), ("rgb", "RGB"),
        ]
        color = next((value for token, value in color_terms if token in lower), "")
    voltage = attr(product, "Napięcie Wejściowe") or name_value(product, r"\b(?:5|12|24|36|48)\s*V(?:\s*DC)?\b")
    power = attr(product, "Moc") or name_value(product, r"\b\d+(?:[.,]\d+)?\s*W\b")
    current = attr(product, "Prąd") or name_value(product, r"\b\d+(?:[.,]\d+)?\s*[-–]\s*\d+(?:[.,]\d+)?\s*mA\b") or name_value(product, r"\b\d+(?:[.,]\d+)?\s*mA\b")
    diode = attr(product, "Typ diody") or name_value(product, r"\b(?:COB|SMD\s*\d{4})\b")
    diode_count = attr(product, "Ilość diod") or name_value(product, r"\b\d+\s*LED\b")
    ip = attr(product, "Klasa szczelności") or name_value(product, r"\bIP\s*\d{2}\b")
    cct = name_value(product, r"\b\d{4,5}\s*K\b")
    angle = name_value(product, r"\b\d{2,3}\s*(?:ST\.?|°)\b")
    code = product["code"]
    derived = [(label, value) for label, value in [("Barwa światła", color), ("Temperatura barwowa", cct), ("Napięcie", voltage), ("Moc", power), ("Prąd", current), ("Typ diody", diode), ("Liczba diod", diode_count), ("Kąt świecenia", angle), ("Klasa szczelności", ip)] if value]
    existing = {label.casefold() for label, _ in specs}
    for label, value in derived:
        if label.casefold() not in existing:
            specs.append((label, value))
            existing.add(label.casefold())

    if "nakładka" in lower:
        sections = [
            {"label": "Funkcja akcesorium", "heading": f"Nakładka do szyb — model {code}", "paragraphs": [f"{name}. Indeks handlowy: {code}; EAN: {product['ean']}.", "Nazwa identyfikuje nakładkę do szyb w systemie FIBI LED; produkt jest elementem uzupełniającym, a nie modułem zasilającym diody."]},
            {"label": "Zgodność", "heading": "Szyba, system oprawy i sposób osadzenia", "paragraphs": [exact_spec_sentence(specs[:4]) if specs else f"Indeks handlowy: {code}; EAN: {product['ean'] or 'nie nadano'}.", "Przed zamówieniem porównaj oznaczenie systemu, grubość szyby i sposób mocowania z oprawą, w której nakładka ma zostać użyta."]},
            {"label": "Identyfikacja", "heading": f"Pełny symbol {code} zamiast doboru ze zdjęcia", "paragraphs": [f"Indeks handlowy: {code}; indeks handlowy: {product['code']}; EAN: {product['ean'] or 'nie nadano'}.", "Podobny kształt nie potwierdza zgodności — właściwy wariant należy ustalić po oznaczeniu rodziny i wymiarach elementu współpracującego."]},
        ]
        return finish(product, sections, ["Nakładka do szyb systemu FIBI LED", f"Identyfikacja kodem {code}"], ["Kompletacja zgodnej oprawy lub systemu szybowego", "Wymiana nakładki po pełnym oznaczeniu"], [f"Kod systemowy: {code}", "Grubość szyby i sposób mocowania"], ["Przed montażem sprawdź zgodność wymiarową z szybą i oprawą"], specs or [("Typ", "Nakładka do szyb"), ("Kod", code)])

    module_kind = "dioda mocy COB" if "cob" in lower else "hermetyczny moduł LED" if "hermet" in lower or ip else "moduł LED"
    headline_facts = join_polish([color or cct, voltage, power, current])
    source_summary = source_sentences(product, 1)
    source_use = source_summary[0] if source_summary else ""
    source_use = re.sub(r"(?i),?\s*i wielu innych miejsc.*$", ".", source_use)
    source_use = re.sub(r"(?i)^moduły LED\s*,", "Moduły LED", source_use)
    sections = [
        {"label": "Moduł i światło", "heading": f"{sentence_case(module_kind)}{f' — {headline_facts}' if headline_facts else f' — {code}'}", "paragraphs": [f"{name}. {exact_spec_sentence(derived[:6])}", f"Wartości dotyczą wyłącznie modelu {code}; napięcia, prądu i mocy nie należy przenosić na moduł o podobnej obudowie."]},
        {"label": "Zastosowanie", "heading": "Źródło punktowe do kompletowanej instalacji LED", "paragraphs": [source_use if source_use else f"{sentence_case(module_kind)} {code} służy jako źródło światła w układzie dobranym do jego parametrów elektrycznych.", "Liczbę modułów oraz zasilacz dobierz po zsumowaniu obciążenia i porównaniu wymaganego napięcia lub prądu każdego elementu."]},
        {"label": "Dobór i chłodzenie", "heading": "Zasilanie, polaryzacja i odprowadzanie ciepła", "paragraphs": [exact_spec_sentence([(label, value) for label, value in [("Kod", code), ("Napięcie", voltage), ("Prąd", current), ("Moc", power), ("Klasa szczelności", ip)] if value]), "Dla diody mocy COB sprawdź wymagany prąd sterujący, zgodność zasilacza i sposób odprowadzania ciepła." if "cob" in lower else "Przed podłączeniem sprawdź polaryzację, parametry zasilacza i warunki pracy wynikające z oznaczonej klasy szczelności."]},
    ]
    benefits = [x for x in [sentence_case(module_kind), f"Barwa światła {color or cct}" if color or cct else "", f"Napięcie pracy {voltage}" if voltage else "", f"Moc modułu {power}" if power else "", f"Diody typu {diode}" if diode else "", f"Klasa szczelności {ip}" if ip else ""] if x]
    applications = ["Budowa punktowego oświetlenia z modułów LED", "Kompletacja oprawy dla diody mocy COB" if "cob" in lower else "Podświetlenie elementów zgodnie z barwą i napięciem modułu"]
    checks = [x for x in [f"Napięcie pracy: {voltage}" if voltage else "", f"Prąd sterujący: {current}" if current else "", f"Barwa światła: {color or cct}" if color or cct else "", f"Klasa szczelności: {ip}" if ip else "", f"Kod modułu: {code}"] if x]
    notes = ["Podłączaj moduł przy odłączonym zasilaniu i z zachowaniem polaryzacji", "Zapewnij odprowadzanie ciepła odpowiednie dla diody mocy" if "cob" in lower else "Zsumuj obciążenie wszystkich modułów przed doborem zasilacza"]
    return finish(product, sections, benefits, applications, checks, notes, specs)


def kit_editorial(product: dict[str, Any]) -> dict[str, Any]:
    specs = preferred_specs(product, ["Barwa światła", "Napięcie wejściowe", "Moc", "Ilość diod", "Moduł cięcia", "Klasa szczelności", "Szerokość taśmy", "Typ diody", "Wymiar", "Gwarancja"], 10)
    color = attr(product, "Barwa światła")
    voltage = attr(product, "Napięcie wejściowe")
    power = attr(product, "Moc")
    ip = attr(product, "Klasa szczelności")
    size = attr(product, "Wymiar")
    code = product["code"]
    name_lower = product["name"].casefold()
    system = "RGB+CCT" if "rgb" in name_lower and "cct" in name_lower else "RGB" if "rgb" in name_lower else "CCT" if "cct" in name_lower else "MONO"
    supplied_power = "zasilacz w zestawie" if "z zasilaczem" in name_lower or "plug & play" in name_lower else ""
    format_facts = [(label, value) for label, value in [("Format zestawu", size), ("Klasa szczelności", ip), ("Wyposażenie", supplied_power)] if value]
    electrical_facts = [(label, value) for label, value in [("Napięcie wejściowe", voltage), ("Moc zestawu", power), ("Kod", code)] if value]
    sections = [
        {"label": "Zestaw LED", "heading": f"System {system}{f', barwa {color}' if color else ''}{f' i moc {power}' if power else ''}", "paragraphs": [exact_spec_sentence(specs[:6]), f"Dane dotyczą kompletnego wariantu {code}, a nie pojedynczej taśmy lub zasilacza kupowanego osobno."]},
        {"label": "Zastosowanie", "heading": f"System {system} do oświetlenia dekoracyjnego", "paragraphs": [light_guidance(color or system), f"{exact_spec_sentence(format_facts)} {ingress_guidance(ip) if ip else f'Miejsce montażu zestawu {code} dobierz po sprawdzeniu sposobu zasilania i ochrony wszystkich elementów.'}"]},
        {"label": "Przed uruchomieniem", "heading": "Sprawdzenie elementów zestawu i miejsca montażu", "paragraphs": [exact_spec_sentence(electrical_facts), "Przed montażem sprawdź komplet, instrukcję połączeń oraz warunki pracy wszystkich elementów zestawu."]},
    ]
    benefits = [x for x in [f"System światła {system}", f"Zestaw w barwie {color}" if color else "", f"Moc całego wariantu {power}" if power else "", f"Format zestawu {size}" if size else "", f"Klasa szczelności {ip}" if ip else "", sentence_case(supplied_power) if supplied_power else ""] if x]
    applications = [light_application(color or system), "Montaż kompletnego wariantu bez dobierania taśmy jako osobnej pozycji"]
    checks = [x for x in [f"Sprawdź barwę lub system: {color}" if color else "", f"Porównaj moc zestawu: {power}" if power else "", f"Dobierz warunki do klasy {ip}" if ip else "", f"Zweryfikuj kod zestawu: {code}"] if x]
    notes = ["Przed podłączeniem sprawdź wszystkie elementy i instrukcję zestawu", "Nie stosuj zestawu w warunkach przekraczających podaną klasę szczelności"]
    return finish(product, sections, benefits, applications, checks, notes, specs)


def festive_editorial(product: dict[str, Any]) -> dict[str, Any]:
    specs = preferred_specs(product, ["Napięcie Wejściowe", "Napięcie Wyjściowe", "Moc", "Klasa szczelności", "Wymiar", "Kolor", "Gwint", "Ilość programów", "Gwarancja"], 11)
    name = product["name"]
    source = normalize(product.get("sourceDescription", ""))
    lower = f"{name} {source}".casefold()
    code = product["code"]
    led_match = re.search(r"(?i)\b\d+\s*LED\b", name)
    led_count = normalize(led_match.group(0)) if led_match else ""
    size = attr(product, "Wymiar")
    if not size:
        size_match = re.search(r"(?i)\b\d+(?:[.,]\d+)?\s*[*x×]\s*\d+(?:[.,]\d+)?\s*m\b|\b\d+(?:[.,]\d+)?\s*(?:mb|metr(?:ów|y)?|m)\b", name)
        size = normalize(size_match.group(0)) if size_match else ""
    voltage = attr(product, "Napięcie Wejściowe") or name_value(product, r"\b(?:DC\s*)?\d+(?:[.,]\d+)?\s*V\b")
    power = attr(product, "Moc")
    ip = attr(product, "Klasa szczelności") or name_value(product, r"\bIP\s*\d{2}\b")
    cct = name_value(product, r"\b\d{4,5}\s*K\b")
    programs = attr(product, "Ilość programów") or name_value(product, r"\b\d+\s*program(?:ów|y)?\b")
    effect = join_polish([
        "ciepła biel" if "ciepł" in lower or cct.startswith("3000") else "chłodna biel" if "zimn" in lower or cct.startswith("6500") else "",
        "wielokolorowy" if any(term in lower for term in ("multikolor", "milion kolor", "1mln kolor", "rgb")) else "",
        "efekt FLASH" if any(term in lower for term in ("flash", "flesz")) else "",
        "efekt płynący" if "płynąc" in lower else "",
    ])
    kind = "projektor laserowy" if "laser" in lower else "girlanda z oprawkami" if "girlanda" in lower else "kurtyna LED" if "kurtyna" in lower else "sople LED" if "sople" in lower else "łańcuch lampek LED"
    name_lower = name.casefold()
    interior = "wewnętrz" in name_lower
    exterior = any(term in lower for term in ("zewnętrz", "ogrod", "ip65", "ip67"))

    if "laser" in lower:
        colors = join_polish(["czerwony" if any(term in lower for term in ("czerw", "red")) else "", "zielony" if any(term in lower for term in ("ziel", "green")) else "", "niebieski" if any(term in lower for term in ("niebies", "nie bies", "blue")) else ""])
        laser_class = (attr(product, "Klasa lasera") or name_value(product, r"\bKlasa lasera\s*:?\s*[0-9A-Z]+\b")).rstrip(" ,;")
        output_power = (attr(product, "Moc wyjściowa") or name_value(product, r"\b\d+(?:[.,]\d+)?\s*mW\s*[-–]\s*\d+(?:[.,]\d+)?\s*mW\b")).rstrip(" ,;")
        voltage = (attr(product, "Napięcie Wyjściowe", "Napięcie robocze") or voltage).rstrip(" ,;")
        control = "radiowy pilot" if "radiow" in lower and "pilot" in lower else "pilot" if "pilot" in lower else ""
        known = [(label, value) for label, value in [("Kolory lasera", colors), ("Klasa lasera", laser_class), ("Moc wyjściowa", output_power), ("Napięcie", voltage), ("Sterowanie", control)] if value]
        sections = [
            {"label": "Efekt projekcyjny", "heading": f"Laser {colors or code} — model {code}", "paragraphs": [f"{name}. {exact_spec_sentence(known[:4])}", "Projektor tworzy ruchome punkty i wzory na skierowanej powierzchni; wariant identyfikuje zestaw kolorów zapisany przy tym kodzie."]},
            {"label": "Sterowanie i ustawienie", "heading": f"{sentence_case(control or 'Ustawienie projekcji')}{f' przy zasilaniu {voltage}' if voltage else ''}", "paragraphs": [source_sentences(product, 1)[0] if source_sentences(product, 1) else exact_spec_sentence(known), "Przed uruchomieniem zamocuj projektor w przewidziany sposób, dobierz powierzchnię projekcji i sprawdź funkcje pilota przypisane do konkretnego modelu."]},
            {"label": "Zasady użycia", "heading": f"Klasa lasera {laser_class or 'podana w instrukcji'} i kierunek wiązki", "paragraphs": [f"Indeks handlowy: {code}; indeks handlowy: {product['code']}; EAN: {product['ean']}.", "Przestrzegaj ostrzeżeń dla klasy lasera, nie kieruj wiązki na ludzi, zwierzęta ani pojazdy i nie patrz bezpośrednio w źródło światła."]},
        ]
        benefits = [f"Projekcja w kolorach: {colors}" if colors else "Projektor efektów laserowych", f"Sterowanie: {control}" if control else f"Kod modelu {code}", f"Zasilanie {voltage}" if voltage else ""]
        applications = ["Dekoracyjna projekcja na ścianie, elewacji lub innej przygotowanej powierzchni", "Aranżacje sezonowe w miejscu dopuszczonym przez instrukcję urządzenia"]
        checks = [f"Kolory projekcji: {colors}" if colors else f"Kod modelu: {code}", f"Klasa lasera: {laser_class}" if laser_class else "Ostrzeżenia i strefa projekcji opisana w instrukcji", f"Sterowanie: {control}" if control else f"Napięcie: {voltage}" if voltage else ""]
        notes = ["Nie kieruj wiązki na ludzi, zwierzęta ani pojazdy", "Zamocuj urządzenie w sposób opisany w instrukcji producenta"]
        return finish(product, sections, benefits, applications, checks, notes, specs or known)

    if "girlanda" in lower and "e27" in lower:
        sockets_match = re.search(r"(?i)\b\d+\s*x\s*E27\b", name)
        sockets = normalize(sockets_match.group(0)) if sockets_match else "oprawki E27"
        max_power = "40W na gniazdo" if re.search(r"(?i)40\s*W\s+na\s+gniazdo", source) else power
        known = [(label, value) for label, value in [("Liczba oprawek", sockets), ("Długość", size), ("Napięcie", voltage), ("Maksymalna moc źródła", max_power), ("Klasa szczelności", ip), ("Kolor przewodu", product_color(product))] if value]
        sections = [
            {"label": "Girlanda ogrodowa", "heading": f"{sockets} na długości {size or code}", "paragraphs": [f"{name}. {exact_spec_sentence(known[:5])}", "Źródła E27 dobiera się osobno, dzięki czemu można ustalić ich barwę, kształt i moc w granicach wskazanych dla pojedynczego gniazda."]},
            {"label": "Rozmieszczenie światła", "heading": f"Oprawki E27 i przewód {size or code}", "paragraphs": [source_sentences(product, 1)[0] if source_sentences(product, 1) else exact_spec_sentence(known), "Przed rozwieszeniem zaplanuj punkty mocowania i sprawdź, czy wszystkie zastosowane źródła mają gwint E27 oraz dopuszczalną moc."]},
            {"label": "Łączenie i montaż", "heading": f"Klasa {ip or 'ochrony z instrukcji'} oraz obciążenie girlandy", "paragraphs": [f"Indeks handlowy: {code}; EAN: {product['ean']}; zasilanie: {voltage or 'według dokumentacji modelu'}.", "Liczbę łączonych odcinków dobierz według mocy zastosowanych źródeł i limitów podanych przez producenta dla tego wariantu."]},
        ]
        benefits = [f"Układ {sockets}", f"Długość {size}" if size else f"Kod modelu {code}", f"Klasa szczelności {ip}" if ip else "", f"Maksymalna moc {max_power}" if max_power else ""]
        applications = ["Oświetlenie tarasu, altany lub strefy ogrodowej", "Dekoracyjna linia światła z indywidualnie dobranymi źródłami E27"]
        checks = [f"Liczba i gwint oprawek: {sockets}", f"Maksymalna moc źródła: {max_power}" if max_power else f"Kod modelu: {code}", f"Klasa szczelności: {ip}" if ip else "Warunki pracy z instrukcji produktu"]
        notes = ["Przed montażem odłącz zasilanie i sprawdź stan przewodu oraz oprawek", "Nie przekraczaj limitu mocy ani liczby łączonych girland podanych przez producenta"]
        return finish(product, sections, benefits, applications, checks, notes, specs or known)

    known = [(label, value) for label, value in [("Liczba diod", led_count), ("Barwa lub efekt", effect or cct), ("Wymiar", size), ("Napięcie", voltage), ("Moc", power), ("Klasa szczelności", ip), ("Programy", programs)] if value]
    place = "do wnętrz oraz aranżacji ogrodowych" if interior and exterior else "do wnętrz" if interior else "do zastosowań zewnętrznych" if exterior else "do miejsca dopasowanego do ochrony przewodu i zasilacza"
    arrangement = (
        "Kurtynę można rozplanować na oknie, ścianie lub tle dekoracyjnym; jej szerokość i wysokość wynikają z formatu konkretnego wariantu."
        if kind == "kurtyna LED"
        else "Sople należy rozmieścić wzdłuż wybranej krawędzi, zachowując długość przewodu i odstępy przewidziane dla tego wariantu."
        if kind == "sople LED"
        else "Łańcuch lampek można prowadzić wzdłuż wybranego elementu dekoracji, bez napinania przewodu i przypadkowego łączenia różnych systemów."
    )
    electrical_sentence = exact_spec_sentence([(label, value) for label, value in [("Napięcie", voltage), ("Moc", power), ("Klasa szczelności", ip)] if value])
    sections = [
        {"label": "Dekoracja świetlna", "heading": f"{sentence_case(kind)} — {join_polish([led_count, effect or cct]) or code}", "paragraphs": [f"{name}. {exact_spec_sentence(known[:6])}", f"Efekt wariantu: {effect or cct or 'dekoracyjny układ punktów świetlnych'}; format: {size or kind.casefold()}."]},
        {"label": "Format i zastosowanie", "heading": f"{size or led_count or code} — wariant {place}", "paragraphs": [arrangement, f"Rozmieszczenie przewodu oraz punktów świetlnych zaplanuj przed mocowaniem; ten wariant jest opisany jako {place}."]},
        {"label": "Zasilanie i montaż", "heading": f"{voltage or f'Model {code}: przewód i zasilacz'}{f', klasa {ip}' if ip else ''}", "paragraphs": [f"Indeks handlowy: {code}; EAN: {product['ean']}.{f' {electrical_sentence}' if electrical_sentence else ''}", "Przed zawieszeniem rozwiń dekorację, sprawdź przewód oraz zasilacz i zastosuj wyłącznie sposób łączenia przewidziany dla tego modelu."]},
    ]
    benefits = [x for x in [sentence_case(kind), f"Układ {led_count}" if led_count else "", f"Efekt {effect or cct}" if effect or cct else "", f"Format {size}" if size else "", f"Klasa szczelności {ip}" if ip else ""] if x]
    applications = [f"Dekoracje świetlne {place}", "Aranżacje sezonowe dopasowane do formatu kurtyny, sopli lub łańcucha"]
    checks = [x for x in [f"Liczba diod: {led_count}" if led_count else f"Kod modelu: {code}", f"Barwa i efekt: {effect or cct}" if effect or cct else "", f"Wymiar: {size}" if size else "", f"Klasa szczelności: {ip}" if ip else ""] if x]
    notes = ["Przed zawieszeniem rozwiń dekorację i sprawdź komplet przewodów", "Zasilacz i złącza umieść zgodnie z ich własną klasą ochrony"]
    return finish(product, sections, benefits, applications, checks, notes, specs or known)


def decorative_device_editorial(product: dict[str, Any]) -> dict[str, Any]:
    """Small rechargeable lamps and clocks sold in the decorative-lighting root."""
    specs = public_specs(product)[:10]
    name = product["name"]
    source = normalize(product.get("sourceDescription", ""))
    lower = f"{name} {source}".casefold()
    code = product["code"]
    is_clock = "budzik" in name.casefold()

    def first_match(pattern: str) -> str:
        match = re.search(pattern, source, re.I)
        return normalize(match.group(0)) if match else ""

    capacity = first_match(r"\b\d{3,5}\s*mAh\b")
    power = first_match(r"\b\d+(?:[.,]\d+)?\s*W\b")
    charge_match = re.search(r"(?:ładowani\w*[^.]{0,45})?(\d+(?:[.,]\d+)?)\s*godzin(?:y|ę)?", source, re.I)
    charge = f"{charge_match.group(1)} godziny" if charge_match else ""
    runtime_match = re.search(r"od\s+(\d+)\s+do\s+(\d+)\s+godzin|(\d+)\s+tygodni(?:e|a)?\s+pracy", source, re.I)
    runtime = f"od {runtime_match.group(1)} do {runtime_match.group(2)} godzin" if runtime_match and runtime_match.group(1) else f"{runtime_match.group(3)} tygodnie" if runtime_match else ""
    material = first_match(r"(?:ABS|PC|HIPS|silikon)(?:\s*\+\s*(?:ABS|PC|HIPS|silikon)){0,3}")
    charging = "USB-C" if "usb-c" in lower else "USB" if "usb" in lower else ""
    rgb = "rgb" in lower
    remote = "pilot" in lower
    color_match = re.search(r"(?i)\b(?:biały|biała|białe|beżowy|beżowa|zielony|zielona|żółty|żółta|różowy|różowa)\b", name)
    color = normalize(color_match.group(0)) if color_match else ""

    identity_heading = "Budzik z funkcją światła dekoracyjnego" if is_clock and "świat" in lower else "Budzik dekoracyjny" if is_clock else "Lampka dekoracyjna LED"
    light_mode = join_polish(["ciepłe światło" if "ciepł" in lower else "", "kolory RGB" if rgb else ""])
    first_facts = [("Akumulator", capacity), ("Moc", power), ("Ładowanie", charging), ("Kolor", color)]
    first_facts = [(label, value) for label, value in first_facts if value]
    time_facts = [("Czas pracy", runtime), ("Czas ładowania", charge), ("Materiał", material)]
    time_facts = [(label, value) for label, value in time_facts if value]

    sections = [
        {
            "label": "Funkcja i forma",
            "heading": f"{identity_heading}: {name}",
            "paragraphs": [
                exact_spec_sentence(first_facts),
                f"Model {code} łączy funkcję {'budzika' if is_clock else 'lampki'} z dekoracyjną formą{f' w kolorze {color}' if color else ''}{f' oraz trybem {light_mode}' if light_mode else ''}.",
            ],
        },
        {
            "label": "Zasilanie i czas pracy",
            "heading": f"{capacity or 'Wbudowane zasilanie'}{f' i ładowanie {charging}' if charging else ''}",
            "paragraphs": [
                exact_spec_sentence(time_facts),
                "Czas pracy zależy od sposobu użytkowania; do porównania wariantów służą wartości podane w opisie producenta." if runtime else "Sposób zasilania i ładowania należy porównać z wyposażeniem wskazanym dla tego modelu.",
            ],
        },
        {
            "label": "Obsługa",
            "heading": "Alarm, ładowanie i wyposażenie zestawu" if is_clock and not light_mode else "Światło, ładowanie i wyposażenie zestawu",
            "paragraphs": [
                f"{sentence_case(light_mode) if light_mode else 'Funkcja budzika' if is_clock else 'Tryb świecenia wynika z opisu modelu'}{'; sterowanie pilotem' if remote else ''}{f'; port ładowania {charging}' if charging else ''}.",
                f"Przed użyciem sprawdź elementy zestawu oraz sposób obsługi opisany dla kodu {code}; EAN produktu to {product['ean']}.",
            ],
        },
    ]
    benefits = [
        value
        for value in [
            f"Wbudowany akumulator {capacity}" if capacity else "",
            f"Czas pracy {runtime}" if runtime else "",
            f"Ładowanie przez {charging}" if charging else "",
            f"Światło {light_mode}" if light_mode else "",
            "Sterowanie pilotem" if remote else "",
        ]
        if value
    ]
    applications = [
        "Budzik do sypialni lub pokoju dziecięcego" if is_clock else "Pomocnicze światło nocne i dekoracyjne",
        f"Dekoracyjny wariant w kolorze {color}" if color else "Dekoracyjny akcent świetlny we wnętrzu",
    ]
    checks = [
        value
        for value in [
            f"Pojemność akumulatora: {capacity}" if capacity else "",
            f"Czas pracy: {runtime}" if runtime else "",
            f"Sposób ładowania: {charging}" if charging else "",
            "Pilot w zestawie" if remote else "",
            f"Kod modelu: {code}",
        ]
        if value
    ]
    notes = [
        f"Ładowanie wykonuj przez złącze {charging} zgodnie z instrukcją urządzenia" if charging else "Przed użyciem sprawdź sposób zasilania podany w instrukcji",
        "Sprawdź zawartość zestawu przed pierwszym uruchomieniem",
    ]
    return finish(product, sections, benefits, applications, checks, notes, specs or first_facts + time_facts)


def fallback_editorial(product: dict[str, Any]) -> dict[str, Any]:
    specs = public_specs(product)[:10]
    code = product["code"]
    first = specs[:4]
    second = specs[4:7] or specs[:3]
    sections = [
        {"label": "Opis wariantu", "heading": f"{product['name']}", "paragraphs": [exact_spec_sentence(first), f"Indeks handlowy: {code}; indeks handlowy: {product['code']}; EAN: {product['ean']}."]},
        {"label": "Dane użytkowe", "heading": "Parametry do porównania przed zakupem", "paragraphs": [exact_spec_sentence(second), "Dobór oprzyj na pełnej nazwie, kodzie i parametrach przypisanych do tego wariantu."]},
        {"label": "Kompletacja", "heading": "Zgodność z pozostałymi elementami", "paragraphs": ["Przed montażem porównaj wymiary, napięcie, sposób połączenia i warunki pracy — wyłącznie w zakresie pól dostępnych dla produktu.", f"Kod: {code}; EAN: {product['ean']}."]},
    ]
    benefits = [f"{label}: {value}" for label, value in specs[:4]]
    applications = [f"Zastosowanie zgodne z grupą {product['category'].split('/')[-1]}", "Kompletacja systemu po pełnym kodzie produktu"]
    checks = [f"Porównaj parametr „{label}”: {value}" for label, value in specs[:4]]
    notes = ["Przed montażem sprawdź zgodność wszystkich łączonych elementów"]
    return finish(product, sections, benefits, applications, checks, notes, specs)
