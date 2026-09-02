#!/usr/bin/env python3
"""
Generator opisów akcesoriów do zasilaczy i taśm LED do TIM.pl — format plain text (bez HTML).
Struktura opisu dla Akcesoriów:
1. Zdanie wstępne (typ akcesorium, konstrukcja/standard, funkcja w instalacji oświetleniowej, gwarancja)
2. Gdzie użyć i funkcja w instalacji (narożniki 90°, łączenie bez lutowania, ukryty montaż w profilu, wyprowadzenie zasilania, rozdzielanie linii, uszczelnianie)
3. Z czym użyć i wskazówki montażowe (kompatybilność z szerokością taśmy 8mm/10mm/12mm, typem diod COB/SMD, liczbą pinów MONO/RGB/RGBW/CCT, dopasowanie do profili aluminiowych Prescot, krok po kroku montaż)
"""

import xml.etree.ElementTree as ET
import html
import json
import re
import os

XML_PATH = "/Users/karolbohdanowicz/Downloads/PRESCOT_TIM_MASTER_BULK_IMPORT_2026.xml"
CATALOG_PATH = "/Users/karolbohdanowicz/my-ai-agents/prescot/data/catalog.json"
OUTPUT_DIR = "/Users/karolbohdanowicz/my-ai-agents/prescot/tmp/tim-opisy-tasmy"


def parse_akcesorium(name: str, code: str, ean: str, cat: str, attrs: dict) -> dict:
    """Parsowanie parametrów technicznych i właściwości akcesorium."""
    n_lower = name.lower()
    c_lower = cat.lower()

    # 1. Kategoria funkcjonalna
    if "koszulka" in n_lower or "koszulki" in c_lower:
        item_group = "koszulka"
    elif "włącznik" in n_lower or "wylacznik" in n_lower or "włączniki" in c_lower:
        item_group = "wlacznik"
    elif "przewód" in n_lower or "przewoód" in n_lower or "przewody" in c_lower or "kabel" in n_lower:
        item_group = "przewod"
    elif "rozdzielacz" in n_lower or "rozdzielacze" in c_lower:
        item_group = "rozdzielacz"
    elif "uszczelniacz" in n_lower or "klej" in n_lower or "uszczelniacze" in c_lower:
        item_group = "uszczelniacz"
    elif "gniazdo" in n_lower or "gniazda" in c_lower:
        item_group = "gniazdo"
    elif "wtyk" in n_lower or "wtyczka" in n_lower or "wtyczki" in c_lower:
        item_group = "wtyk"
    else:
        item_group = "zlaczka"

    # 2. Szerokość taśmy
    width = "8 mm"
    m_w = re.search(r'(\d+)\s*mm\b', name)
    if m_w:
        width = f"{m_w.group(1)} mm"
    elif "10mm" in code.lower() or "10" in code:
        if "fc10" in code.lower() or "zl10" in code.lower() or "8mm" not in name:
            width = "10 mm"
    elif "12mm" in code.lower() or "12mm" in name:
        width = "12 mm"

    # 3. Liczba pinów i typ taśmy
    if "rgb+cct" in n_lower or "6pin" in n_lower or "6-pin" in n_lower:
        pin_type = "RGB+CCT (6-pin)"
        pin_count = 6
    elif "rgbw" in n_lower or "5pin" in n_lower or "5-pin" in n_lower:
        pin_type = "RGBW (5-pin)"
        pin_count = 5
    elif "rgb" in n_lower or "4pin" in n_lower or "4-pin" in n_lower or "tlwy" in n_lower:
        pin_type = "RGB (4-pin)"
        pin_count = 4
    elif "cct" in n_lower or "3pin" in n_lower or "3-pin" in n_lower:
        pin_type = "CCT Dual White (3-pin)"
        pin_count = 3
    else:
        pin_type = "jednokolorowa MONO (2-pin)"
        pin_count = 2

    # 4. Typ diody (COB vs SMD)
    if "cob" in n_lower and "smd" not in n_lower:
        led_target = "taśmy COB (ciągła linia światła)"
    elif "smd" in n_lower and "cob" not in n_lower:
        led_target = "taśmy SMD (SMD2835, SMD5050, SMD2216)"
    else:
        led_target = "taśmy SMD oraz COB"

    # 5. Kształt i konstrukcja złączki
    if " l " in n_lower or "kąt" in n_lower or "pcb l" in n_lower or "-l-" in code.lower() or code.endswith("L"):
        shape = "kątowa L (90°)"
    elif " t " in n_lower or "pcb t" in n_lower or "-t-" in code.lower() or code.endswith("T"):
        shape = "trójnik T"
    elif " x " in n_lower or "pcb x" in n_lower or "-x-" in code.lower() or code.endswith("X"):
        shape = "krzyżak X"
    elif "push" in n_lower:
        shape = "szybkozłączka zaciskowa PUSH"
    elif "przewód" in n_lower or "przewoód" in n_lower or "kabel" in n_lower or "15cm" in n_lower or "300cm" in n_lower:
        shape = "połączeniowa z przewodem"
    else:
        shape = "prosta taśma-taśma"

    # Długość przewodu jeśli występuje
    wire_len = ""
    m_wl = re.search(r'(\d+)\s*(?:cm|m)\b', name)
    if m_wl:
        wire_len = m_wl.group(0)

    return {
        "raw_name": name,
        "code": code,
        "ean": ean,
        "cat": cat,
        "subcat": cat.split("/")[-1],
        "item_group": item_group,
        "width": width,
        "pin_type": pin_type,
        "pin_count": pin_count,
        "led_target": led_target,
        "shape": shape,
        "wire_len": wire_len,
        "warranty": 2,
    }


def generate_akcesorium_intro(info: dict) -> str:
    """Zdanie wstępne dla akcesorium."""
    ig = info["item_group"]
    w = info["width"]
    pt = info["pin_type"]
    shape = info["shape"]

    desc_map = {
        "zlaczka": f"Profesjonalna złączka połączeniowa do taśm LED ({shape}), dedykowana do taśm o szerokości {w} ({pt}).",
        "wtyk": f"Wysokiej jakości element połączeniowy (wtyk) dedykowany do bezpiecznego łączenia i rozłączania linii zasilających w instalacjach LED ({pt}).",
        "gniazdo": f"Dedykowane gniazdo montażowe LED ({pt}) umożliwiające szybkie, rozłączne podłączenie zasilania lub sterownika.",
        "przewod": f"Dedykowany elastyczny przewód montażowy do instalacji oświetleniowych LED ({pt}), gwarantujący niskie spadki napięcia i łatwe układanie w profilach i korytkach.",
        "koszulka": f"Przezroczysta koszulka silikonowa o szerokości wewnętrznej {w}, zapewniająca skuteczną ochronę mechaniczną i podwyższenie szczelności taśmy LED.",
        "wlacznik": "Miniaturowy włącznik / sterownik doprofilowy dedykowany do bezpośredniego, ukrytego montażu w profilach aluminiowych LED 12V/24V.",
        "rozdzielacz": "Rozdzielacz instalacyjny zasilania LED umożliwiający bezproblemowe podłączenie wielu niezależnych odcinków taśm do jednego zasilacza.",
        "uszczelniacz": "Specjalistyczny uszczelniacz / klej do taśm LED zapewniający trwałą ochronę hermetyczną połączeń i końcówek taśm w profilach.",
    }

    intro_text = desc_map.get(ig, f"Profesjonalne akcesorium montażowe Prescot do systemów oświetlenia LED.")
    parts = [
        intro_text,
        "Umożliwia szybki, estetyczny i w pełni bezpieczny montaż bez konieczności czasochłonnego lutowania.",
        "Produkt objęty jest 2-letnią gwarancją."
    ]
    return " ".join(parts)


def generate_akcesorium_gdzie(info: dict) -> str:
    """Sekcja: Gdzie użyć i funkcja w instalacji."""
    lines = ["Gdzie użyć i funkcja w instalacji"]
    ig = info["item_group"]
    shape = info["shape"]
    w = info["width"]

    if ig == "zlaczka":
        if "kątowa" in shape or "L" in shape:
            lines.append(
                "Złączka kątowa L (90°) służy do estetycznego prowadzenia linii światła w narożnikach bez załamywania i uszkadzania taśmy:\n"
                "• Narożniki sufitów podwieszanych i wnęk gipsowo-kartonowych,\n"
                "• Zabudowy meblowe (ciągi szafek kuchennych w kształcie L lub U),\n"
                "• Ramki i oprawy oświetleniowe z profili aluminiowych Prescot,\n"
                "• Schody, podstopnice i cokoły wymagające precyzyjnego zakrętu pod kątem prostym."
            )
        elif "trójnik" in shape or "krzyżak" in shape:
            lines.append(
                f"Złączka typu {shape} pozwala na rozgałęzienie jednej linii zasilającej na kilka kierunków:\n"
                "• Skomplikowane sufity podwieszane i układy geometryczne z profili LED,\n"
                "• Podświetlenia meblowe wielosekcyjne (np. oświetlenie regałów, garderób, witryn),\n"
                "• Równoległe łączenie kilku odcinków taśmy w celu zminimalizowania spadków napięcia."
            )
        elif "przewodem" in shape or "push" in shape:
            lines.append(
                "Złączka umożliwia szybkie wyprowadzenie zasilania lub połączenie dwóch oddalonych od siebie odcinków taśm:\n"
                "• Przejścia między szafkami kuchennymi (np. ominięcie okapu kuchennego lub wnęki),\n"
                "• Połączenie taśmy w profilu z przewodem biegnącym do zasilacza lub sterownika,\n"
                "• Szybkie łączenie przewodów instalacyjnych bez użycia lutownicy i narzędzi specjalistycznych."
            )
        else:
            lines.append(
                "Złączka służy do bezlutowego łączenia dwóch odcinków taśmy LED w jeden ciągły odcinek liniowy:\n"
                "• Wykorzystanie krótszych ścinków taśmy bez strat materiału,\n"
                "• Łączenie długich linii światła w profilach aluminiowych,\n"
                "• Szybka naprawa lub przedłużenie instalacji w miejscu montażu."
            )
    elif ig == "wlacznik":
        lines.append(
            "Włącznik montuje się bezpośrednio wewnątrz profilu aluminiowego pod kloszem (np. za pomocą taśmy dwustronnej):\n"
            "• Meble kuchenne – bezdotykowe włączanie oświetlenia blatu roboczego mokrą lub brudną dłonią,\n"
            "• Szafy, garderoby i szuflady – automatyczne zapalanie światła po otwarciu drzwi (funkcja zbliżeniowa / PIR),\n"
            "• Kinkiety ścienne i lampy meblowe z funkcją płynnego ściemniania dotykowego."
        )
    elif ig == "koszulka":
        lines.append(
            f"Koszulka silikonowa służy do zabezpieczenia taśm LED o szerokości {w} przed działaniem wilgoci, kurzu i uszkodzeń mechanicznych:\n"
            "• Łazienki, kabiny prysznicowe, wanny i strefy wokół umywalki,\n"
            "• Podbitki dachowe, tarasy, balkony i instalacje zewnętrzne,\n"
            "• Oświetlenie blatów kuchennych i stref narażonych na zachlapanie wodą."
        )
    elif ig == "przewod":
        lines.append(
            "Przewód dedykowany do niskonapięciowych instalacji LED 12V / 24V / 48V:\n"
            "• Połączenia zasilacza ze sterownikiem lub taśmą LED,\n"
            "• Prowadzenie linii zasilających w bruzdach ściennych, rurkach peszla i korytkach meblowych,\n"
            "• Łączenie wielokanałowych taśm RGB / RGBW / CCT z odbiornikami radiowymi."
        )
    elif ig in ("wtyk", "gniazdo"):
        lines.append(
            "Element umożliwia stworzenie wygodnego, rozłącznego połączenia w instalacji LED:\n"
            "• Szybkie odłączanie opraw meblowych podczas serwisu lub wymiany,\n"
            "• Połączenie taśmy LED z zasilaczem wtyczkowym lub sterownikiem,\n"
            "• Montaż w meblach modułowych i ekspozycjach targowych."
        )
    elif ig == "rozdzielacz":
        lines.append(
            "Rozdzielacz pozwala na równomierne rozdzielenie napięcia zasilającego z jednego zasilacza na wiele odbiorników:\n"
            "• Oświetlenie wielopoziomowych półek w garderobach i regałach,\n"
            "• Zasilanie kilku niezależnych profili LED w jednym pomieszczeniu,\n"
            "• Uniknięcie plątaniny kabli przy zasilaczu centralnym."
        )
    else:
        lines.append(
            "Akcesorium przeznaczone do profesjonalnego montażu i uszczelniania elementów systemów oświetlenia LED w profilach aluminiowych."
        )

    return "\n\n".join(lines)


def generate_akcesorium_z_czym(info: dict) -> str:
    """Sekcja: Z czym użyć i wskazówki montażowe."""
    lines = ["Z czym użyć i wskazówki montażowe"]
    w = info["width"]
    pt = info["pin_type"]
    lt = info["led_target"]
    shape = info["shape"]

    lines.append(
        f"Kompatybilność: Akcesorium jest w pełni dopasowane do {lt} o szerokości PCB {w} w standardzie {pt} (instalacje 12V oraz 24V DC)."
    )

    lines.append(
        f"Dopasowanie do profili: Kompaktowe wymiary pozwalają na bezproblemowy montaż w profilach aluminiowych Prescot o szerokości wewnętrznej min. {w} "
        "(np. profile nawierzchniowe, wpuszczane, kątowe oraz głębokie profile architektoniczne)."
    )

    lines.append(
        "Wskazówki montażowe:\n"
        "1. Upewnij się, że taśma LED została przycięta dokładnie w wyznaczonym miejscu cięcia (oznaczonym symbolem nożyczek).\n"
        "2. Wsuń taśmę pod blaszki stykowe złączki, dbając o idealne dopasowanie pól lutowniczych taśmy do pinów złączki.\n"
        "3. Sprawdź poprawność polaryzacji (+/- lub oznaczenia kolorów R/G/B/W) przed zatrzaśnięciem klapki dociskowej.\n"
        "4. Zaciśnij złączkę (ręcznie lub szczypcami) do wyraźnego oporu – połączenie jest gotowe do pracy bez lutowania."
    )

    return "\n\n".join(lines)


def generate_akcesorium_title(info: dict) -> str:
    """Krótki nagłówek akcesorium."""
    ig_title = {
        "zlaczka": f"Złączka do taśmy LED {info['width']} {info['pin_type']}",
        "wtyk": f"Wtyk połączeniowy LED {info['pin_type']}",
        "gniazdo": f"Gniazdo połączeniowe LED {info['pin_type']}",
        "przewod": f"Przewód montażowy LED {info['pin_type']}",
        "koszulka": f"Koszulka silikonowa hermetyczna {info['width']}",
        "wlacznik": "Włącznik do profilu LED 12V/24V",
        "rozdzielacz": "Rozdzielacz zasilania LED",
        "uszczelniacz": "Klej / Uszczelniacz silikonowy do LED",
    }.get(info["item_group"], "Akcesorium do taśm LED")

    return f"{ig_title} (Kod: {info['code']})"


def generate_akcesorium_description(info: dict) -> dict:
    """Generuje kompletny opis akcesorium do TIM."""
    title = generate_akcesorium_title(info)
    intro = generate_akcesorium_intro(info)
    gdzie = generate_akcesorium_gdzie(info)
    z_czym = generate_akcesorium_z_czym(info)

    full_text = f"{title}\n{intro}\n\n{gdzie}\n\n{z_czym}"

    return {
        "title": title,
        "intro": intro,
        "gdzie": gdzie,
        "z_czym": z_czym,
        "full_text": full_text,
    }


def main():
    # 1. Load catalog for rich attribute matching
    catalog_by_ean = {}
    catalog_by_code = {}
    if os.path.exists(CATALOG_PATH):
        with open(CATALOG_PATH, "r", encoding="utf-8") as f:
            cat_data = json.load(f)
            for p in cat_data.get("products", []):
                if p.get("ean"):
                    catalog_by_ean[p["ean"]] = p
                if p.get("code"):
                    catalog_by_code[p["code"]] = p
                if p.get("manufacturerCode"):
                    catalog_by_code[p["manufacturerCode"]] = p

    # 2. Parse XML
    tree = ET.parse(XML_PATH)
    root = tree.getroot()

    products = []
    for o in root.findall('.//o'):
        name_el = o.find('name')
        name = name_el.text if name_el is not None else ''
        cat_el = o.find('cat')
        cat = cat_el.text if cat_el is not None else ''

        if not cat.startswith('Akcesoria do zasilaczy i taśm LED'):
            continue

        code = ''
        ean = ''
        for a in o.findall('.//a'):
            if a.get('name') == 'Kod_produktu':
                code = a.text or ''
            if a.get('name') == 'EAN':
                ean = a.text or ''

        price = o.get('price', '')
        stock = o.get('stock', '')
        oid = o.get('id', '')

        cat_item = catalog_by_ean.get(ean) or catalog_by_code.get(code)
        attrs = cat_item.get("attributes", {}) if cat_item else {}

        info = parse_akcesorium(name, code, ean, cat, attrs)
        desc = generate_akcesorium_description(info)

        products.append({
            "id": oid,
            "name": name,
            "code": code,
            "ean": ean,
            "cat": cat,
            "subcat": info["subcat"],
            "price": price,
            "stock": stock,
            "info": info,
            "description": desc,
        })

    products.sort(key=lambda p: (p["subcat"], p["name"]))

    # 3. Save JSON
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    json_path = os.path.join(OUTPUT_DIR, "tim_akcesoria_descriptions.json")

    json_products = []
    for p in products:
        jp = {k: v for k, v in p.items() if k != "info"}
        jp["parsed_info"] = {k: v for k, v in p["info"].items() if k != "raw_name"}
        json_products.append(jp)

    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(json_products, f, ensure_ascii=False, indent=2)

    print(f"✅ Wygenerowano precyzyjne opisy dla {len(products)} akcesoriów LED")
    print(f"   JSON: {json_path}")

    return products


if __name__ == "__main__":
    main()
