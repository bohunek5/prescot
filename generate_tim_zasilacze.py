#!/usr/bin/env python3
"""
Generator opisów zasilaczy LED do TIM.pl — format plain text (bez HTML).
Priorytet na samej górze listy (TOP):
1. ⭐ Prescot PR-MAD Smart Auto-Identify 12V/24V (PR-MAD36, 60, 100, 150, 200, 300)
2. 🏆 Schärfer Hermetyczne IP67 7 Lat Gwarancji (SCH-18 .. SCH-400W 12V/24V)
3. Pozostałe zasilacze Mean Well, Prescot Slim, DIN, Dopuszkowe, Modułowe.
"""

import xml.etree.ElementTree as ET
import json
import re
import os

XML_PATH = "/Users/karolbohdanowicz/Downloads/PRESCOT_TIM_MASTER_BULK_IMPORT_2026.xml"
CATALOG_PATH = "/Users/karolbohdanowicz/my-ai-agents/prescot/data/catalog.json"
OUTPUT_DIR = "/Users/karolbohdanowicz/my-ai-agents/prescot/tmp/tim-opisy-tasmy"


def parse_zasilacz(name: str, code: str, ean: str, cat: str, attrs: dict) -> dict:
    """Ekstrakcja i normalizacja parametrów zasilacza LED z flagami priorytetu."""
    n_lower = name.lower()
    c_lower = (code + " " + cat).lower()

    # Priority flags
    is_prmad = "mad" in n_lower or "auto" in n_lower or "mad" in c_lower or code.startswith("Zas00040") or "pr-mad" in c_lower
    is_scharfer = "scharfer" in n_lower or "schärfer" in n_lower or "sch-" in c_lower or "sch" in code.lower() or "scharfer" in c_lower

    # 1. Napięcie wyjściowe
    voltage = "12V"
    if is_prmad:
        voltage = "Smart Auto 12V/24V"
    elif "24V" in name or "24V" in code or attrs.get("Napięcie wyjściowe") == "24V":
        voltage = "24V"
    elif "48V" in name or "48V" in code or attrs.get("Napięcie wyjściowe") == "48V":
        voltage = "48V"
    elif "5V" in name or "5V" in code:
        voltage = "5V"

    # 2. Moc znamionowa (W)
    power_w = 0
    m_p = re.search(r'(\d+)\s*W\b', name)
    if m_p:
        power_w = int(m_p.group(1))
    elif attrs.get("Moc"):
        m_ap = re.search(r'(\d+)', attrs["Moc"])
        if m_ap:
            power_w = int(m_ap.group(1))
    if power_w == 0:
        power_w = 60

    # 3. Typ obudowy / konstrukcja
    if is_prmad:
        ptype = "prmad_auto"
        ip = "IP20 (Semi-Potted)"
        brand = "Prescot PR-MAD"
        warranty = 5
    elif is_scharfer:
        ptype = "scharfer_hermetic"
        ip = "IP67"
        brand = "Schärfer"
        warranty = 7
    elif "puszki" in n_lower or "dopuszkowy" in n_lower or "ip-20-12-o" in code.lower() or "fi60" in n_lower:
        ptype = "dopuszkowy"
        ip = "IP67"
        brand = "Prescot"
        warranty = 3
    elif "din" in n_lower or "szynę din" in c_lower or "hdr" in n_lower or "edr" in n_lower or "ndr" in n_lower:
        ptype = "din"
        ip = "IP20"
        brand = "Mean Well" if any(k in n_lower for k in ("hdr", "edr", "ndr")) else "Prescot"
        warranty = 3
    elif "slim" in n_lower or "wąski" in c_lower or "płaski" in c_lower or "meblowy" in n_lower:
        ptype = "slim"
        ip = "IP20"
        brand = "Prescot"
        warranty = 3
    elif "gniazdkowy" in n_lower or "gniazdkowe" in c_lower or "desktop" in n_lower:
        ptype = "desktop"
        ip = "IP20"
        brand = "Prescot"
        warranty = 2
    elif "hermetyczny" in n_lower or "herm" in n_lower or "wodoodporne" in c_lower or "lpv" in n_lower or "xlg" in n_lower or "gpv" in n_lower:
        ptype = "hermetyczny"
        ip = "IP67"
        if "xlg" in n_lower:
            brand = "Mean Well"
            warranty = 5
        elif "lpv" in n_lower:
            brand = "Mean Well"
            warranty = 3
        elif "gpv" in n_lower or "glp" in n_lower:
            brand = "Global Leader Power (GLP)"
            warranty = 3
        else:
            brand = "Prescot"
            warranty = 3
    else:
        ptype = "modułowy"
        ip = "IP20"
        brand = "Mean Well" if "lrs" in n_lower else "Prescot"
        warranty = 2 if "standard" in n_lower else 3

    # 4. Wyliczenia mocy użytecznej i długości taśm (zapas 20%)
    usable_power = round(power_w * 0.8, 1)
    len_4_8 = round(usable_power / 4.8, 1)
    len_9_6 = round(usable_power / 9.6, 1)
    len_14_4 = round(usable_power / 14.4, 1)

    # Sort priority (0 = PR-MAD, 1 = Schärfer, 2 = Reszta)
    priority_order = 2
    if is_prmad:
        priority_order = 0
    elif is_scharfer:
        priority_order = 1

    return {
        "raw_name": name,
        "code": code,
        "ean": ean,
        "cat": cat,
        "subcat": cat.split("/")[-1],
        "voltage": voltage,
        "power_w": power_w,
        "usable_power": usable_power,
        "len_4_8": len_4_8,
        "len_9_6": len_9_6,
        "len_14_4": len_14_4,
        "type": ptype,
        "ip": ip,
        "brand": brand,
        "warranty": warranty,
        "is_prmad": is_prmad,
        "is_scharfer": is_scharfer,
        "priority_order": priority_order,
    }


def generate_zasilacz_intro(info: dict) -> str:
    """Zdanie wstępne zoptymalizowane pod markę i serię."""
    ptype = info["type"]
    p = info["power_w"]
    v = info["voltage"]
    brand = info["brand"]
    w = info["warranty"]

    if info["is_prmad"]:
        return (
            f"Flagowy zasilacz impulsowy Prescot PR-MAD {p}W z innowacyjną technologią Smart Auto-Identify 12V/24V. "
            f"Wbudowany procesor automatycznie rozpoznaje napięcie podłączonej taśmy LED (12V lub 24V), całkowicie eliminując błędy doboru i ryzyko uszkodzenia odbiorników. "
            f"Konstrukcja Ultra-Slim (wysokość zaledwie 29 mm) z zalewem termoprzewodzącym Semi-Potted gwarantuje bezgłośną pracę i wydłużoną żywotność. "
            f"Produkt objęty jest 5-letnią gwarancją producenta."
        )
    elif info["is_scharfer"]:
        return (
            f"Profesjonalny zasilacz hermetyczny Schärfer {v} {p}W o stopniu ochrony IP67, zaprojektowany do bezkompromisowej, ciągłej pracy w najtrudniejszych warunkach. "
            f"Wytrzymała obudowa z litego aluminium doskonale odprowadza ciepło i chroni elektronikę przed wilgocią, kurzem oraz skrajnymi temperaturami. "
            f"Produkt należy do linii premium i jest objęty 7-letnią gwarancją (7Y)."
        )
    else:
        type_desc = {
            "hermetyczny": f"profesjonalny zasilacz stałonapięciowy w szczelnej obudowie o stopniu ochrony {info['ip']}",
            "modułowy": "niezawodny zasilacz stałonapięciowy w perforowanej obudowie metalowej o swobodnym chłodzeniu konwekcyjnym",
            "slim": "kompaktowy zasilacz stałonapięciowy w wąskiej obudowie typu Ultra Slim, dedykowany do ciasnych przestrzeni meblowych",
            "din": "wysokosprawny zasilacz przemysłowo-budynkowy przystosowany do bezpośredniego montażu na standardowej szynie DIN TS-35",
            "dopuszkowy": f"miniaturowy zasilacz stałonapięciowy o szczelności {info['ip']}, zaprojektowany do montażu w standardowych puszkach elektroinstalacyjnych fi 60 mm",
            "desktop": "wygodny zasilacz wtyczkowy / desktop z przewodem, niewymagający ingerencji w stałą instalację elektryczną",
        }.get(ptype, "profesjonalny zasilacz stałonapięciowy do systemów oświetlenia LED")

        return f"Zasilacz LED {brand} {v} o mocy {p} W to {type_desc}. Zapewnia stabilne napięcie wyjściowe {v} DC, wysoką sprawność energetyczną oraz pełne bezpieczeństwo podłączonych odbiorników LED. Produkt objęty jest {w}-letnią gwarancją."


def generate_zasilacz_gdzie(info: dict) -> str:
    """Sekcja: Gdzie użyć i montaż."""
    lines = ["Gdzie użyć i montaż"]
    ptype = info["type"]

    if info["is_prmad"]:
        lines.append(
            "Zasilacz PR-MAD dzięki ultra-płaskiemu profilowi (29 mm) oraz całkowicie bezgłośnemu, pasywnemu chłodzeniu doskonale sprawdzi się w najbardziej wymagających przestrzeniach:\n"
            "• Płytkie sufity podwieszane i zabudowy gipsowo-kartonowe w salonach i sypialniach (brak hałasu wentylatora),\n"
            "• Meble kuchenne, cokoły, przestrzenie nad szafkami i garderoby,\n"
            "• Wnęki oświetleniowe, korytarze i lamele ścienne z podświetleniem LED,\n"
            "• Instalacje mieszane, w których w jednym obiekcie stosowane są zarówno obwody 12V, jak i 24V."
        )
    elif info["is_scharfer"]:
        lines.append(
            "Hermetyczna aluminiowa obudowa IP67 sprawia, że zasilacze Schärfer są pierwszym wyborem do instalacji narażonych na wilgoć, zapylenie i zmienne warunki atmosferyczne:\n"
            "• Łazienki, kabiny prysznicowe, strefy basenowe i SPA (pełna odporność na parę wodną),\n"
            "• Oświetlenie zewnętrzne budynków, podbitki dachowe, tarasy, balkony i elewacje,\n"
            "• Kasetony reklamowe, litery 3D, banery świetlne i witryny handlowe pracujące 24/7,\n"
            "• Hale produkcyjne, magazyny i pomieszczenia techniczne o podwyższonej wilgotności."
        )
    elif ptype == "hermetyczny":
        lines.append(
            f"Dzięki szczelnej obudowie o klasie {info['ip']}, zasilacz jest w pełni odporny na działanie wilgoci i kurzu. "
            "Sprawdzi się idealnie w trudnych warunkach środowiskowych:\n"
            "• Łazienki i strefy mokre (strefy 1 i 2),\n"
            "• Oświetlenie zewnętrzne budynków, podbitki dachowe, tarasy i balkony,\n"
            "• Reklamy świetlne, kasetony oraz witryny sklepowe,\n"
            "• Kuchnie (strefy nad zlewem i płytą grzewczą) oraz pomieszczenia techniczne."
        )
    elif ptype == "dopuszkowy":
        lines.append(
            "Kompaktowa, okrągła forma mieści się w standardowej puszce podtynkowej fi 60 mm (głębokiej lub z kieszenią). "
            "Znakomity wybór do:\n"
            "• Ukrytego zasilania opraw schodowych i przypodłogowych,\n"
            "• Zasilania kinkietów ściennych LED bez konieczności kucia ścian pod duży zasilacz,\n"
            "• Dyskretnego montażu bezpośrednio za łącznikiem światła w ścianie."
        )
    elif ptype == "slim":
        lines.append(
            "Wąska i niska konstrukcja typu Ultra Slim pozwala na bezproblemowy montaż w miejscach o ograniczonej przestrzeni:\n"
            "• Meble kuchenne, podszafkowe ciągi robocze, cokoły i wieńce szafek,\n"
            "• Garderoby, szafy wnękowe z drzwiami przesuwnymi,\n"
            "• Płytkie profile aluminiowe, półki szklane i wnęki meblowe."
        )
    elif ptype == "din":
        lines.append(
            "Zasilacz wyposażony jest w zintegrowany zatrzask na szynę DIN TS-35. Przeznaczony do profesjonalnych instalacji rozdzielczych:\n"
            "• Rozdzielnice elektryczne (oświetlenie LED całego budynku),\n"
            "• Szafy automatyki budynkowej (Smart Home, KNX, Loxone, DALI),\n"
            "• Szafy sterownicze w obiektach komercyjnych i biurowych."
        )
    else:
        lines.append(
            "Perforowana metalowa obudowa zapewnia wydajne chłodzenie konwekcyjne (IP20). "
            "Zasilacz sprawdzi się w instalacjach wewnętrznych:\n"
            "• Sufity podwieszane i zabudowy g-k,\n"
            "• Wnęki oświetleniowe i gzymsy z oświetleniem liniowym LED,\n"
            "• Zaplecza techniczne i skrzynki montażowe."
        )

    return "\n\n".join(lines)


def generate_zasilacz_z_czym(info: dict) -> str:
    """Sekcja: Z czym użyć i dobór mocy z przelicznikiem."""
    lines = ["Z czym użyć i dobór mocy"]
    v = info["voltage"]
    p = info["power_w"]
    up = info["usable_power"]
    l48 = info["len_4_8"]
    l96 = info["len_9_6"]
    l144 = info["len_14_4"]

    if info["is_prmad"]:
        lines.append(
            f"Kompatybilność Smart: Zasilacz współpracuje zarówno z taśmami 12V DC, jak i 24V DC. "
            "Inteligentny procesor po włączeniu zasilania mierzy parametry obciążenia i automatycznie ustawia odpowiednie napięcie wyjściowe. "
            "Współpracuje ze wszystkimi taśmami jednokolorowymi, CCT, RGB, RGBW, COB oraz sterownikami i ściemniaczami LED Prescot."
        )
    else:
        lines.append(
            f"Zasilacz jest w pełni kompatybilny ze wszystkimi odbiornikami stałonapięciowymi {v} DC z oferty Prescot:\n"
            f"• Taśmy LED {v} (MONO, CCT regulowana, RGB, RGBW, RGB+CCT oraz COB),\n"
            f"• Ściemniacze i sterowniki radiowe / Wi-Fi / Zigbee {v} Prescot,\n"
            f"• Moduły LED i oprawy meblowe zasilane napięciem {v} DC."
        )

    lines.append(
        f"Moc znamionowa zasilacza wynosi {p} W. Zgodnie z wytycznymi technicznymi Prescot, dla zapewnienia stabilności i trwałości instalacji, "
        f"należy zachować bezpieczny 20% zapas mocy. Dostępna moc ciągła wynosi ok. {up} W, co pozwala na bezpieczne podłączenie:\n"
        f"• do {l48} m taśmy LED o mocy 4.8 W/m (oświetlenie dekoracyjne i akcentujące),\n"
        f"• do {l96} m taśmy LED o mocy 9.6 W/m (oświetlenie użytkowe i liniowe),\n"
        f"• do {l144} m taśmy LED o mocy 14.4 W/m (mocne oświetlenie główne i robocze)."
    )

    lines.append(
        "Układ wyposażony jest w komplet zabezpieczeń: przeciwzwarciowe (SCP), przeciążeniowe (OLP) oraz termiczne (OTP). "
        f"Przed montażem należy sprawdzić polaryzację przewodów wyjściowych (V+ dodatni, V- ujemny). "
        "W przypadku zasilaczy IP20 należy zapewnić swobodną cyrkulację powietrza w miejscu montażu."
    )

    return "\n\n".join(lines)


def generate_zasilacz_title(info: dict) -> str:
    """Krótki nagłówek zasilacza."""
    brand = info["brand"]
    v = info["voltage"]
    p = info["power_w"]
    ptype = info["type"]

    if info["is_prmad"]:
        return f"Zasilacz LED {brand} Smart Auto 12V/24V {p}W Ultra-Slim"
    elif info["is_scharfer"]:
        return f"Zasilacz LED {brand} {v} {p}W Hermetyczny IP67 7Y"

    type_name = {
        "hermetyczny": f"Hermetyczny {info['ip']}",
        "modułowy": "Modułowy siatkowy",
        "slim": "Ultra Slim meblowy",
        "din": "Na szynę DIN",
        "dopuszkowy": f"Dopuszkowy fi60 {info['ip']}",
        "desktop": "Wtyczkowy / Desktop",
    }.get(ptype, "Stałonapięciowy")

    return f"Zasilacz LED {brand} {v} {p}W {type_name}"


def generate_zasilacz_description(info: dict) -> dict:
    """Generuje kompletny opis zasilacza do TIM."""
    title = generate_zasilacz_title(info)
    intro = generate_zasilacz_intro(info)
    gdzie = generate_zasilacz_gdzie(info)
    z_czym = generate_zasilacz_z_czym(info)

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
    catalog_all = []
    if os.path.exists(CATALOG_PATH):
        with open(CATALOG_PATH, "r", encoding="utf-8") as f:
            cat_data = json.load(f)
            catalog_all = cat_data.get("products", [])
            for p in catalog_all:
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
    processed_codes = set()

    for o in root.findall('.//o'):
        name_el = o.find('name')
        name = name_el.text if name_el is not None else ''
        cat_el = o.find('cat')
        cat = cat_el.text if cat_el is not None else ''

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

        # Check if Zasilacz (also capture Schärfer under Oświetlenie LED)
        is_zas_cat = cat.startswith('Zasilacze LED')
        is_sch_named = ('scharfer' in name.lower() or 'schärfer' in name.lower() or 'sch-' in code.lower()) and ('zasilacz' in name.lower() or 'sch-' in code.lower())
        is_prmad_named = ('mad' in name.lower() or 'auto' in name.lower()) and 'zasilacz' in name.lower()

        if not (is_zas_cat or is_sch_named or is_prmad_named):
            continue

        if code in processed_codes:
            continue
        processed_codes.add(code)

        cat_item = catalog_by_ean.get(ean) or catalog_by_code.get(code)
        attrs = cat_item.get("attributes", {}) if cat_item else {}

        info = parse_zasilacz(name, code, ean, cat, attrs)
        desc = generate_zasilacz_description(info)

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

    # Also make sure all 20 Schärfer and 6 PR-MAD from catalog are present!
    for p in catalog_all:
        code = p.get('code', '') or p.get('manufacturerCode', '')
        name = p.get('name', '')
        nl = name.lower()
        cl = code.lower()
        if (('scharfer' in nl or 'sch-' in cl) and 'zasilacz' in nl) or (('mad' in nl or 'auto' in nl) and 'zasilacz' in nl):
            if code not in processed_codes and len(code) > 2:
                processed_codes.add(code)
                attrs = p.get('attributes', {})
                cat = p.get('category', 'Zasilacze LED')
                info = parse_zasilacz(name, code, p.get('ean',''), cat, attrs)
                desc = generate_zasilacz_description(info)
                products.append({
                    "id": str(p.get('id', '')),
                    "name": name,
                    "code": code,
                    "ean": p.get('ean', ''),
                    "cat": cat,
                    "subcat": info["subcat"],
                    "price": str(p.get('price', '0.00')),
                    "stock": str(p.get('stock', '0')),
                    "info": info,
                    "description": desc,
                })

    # SORT: PR-MAD (0) first, Schärfer (1) second, then others by power and name
    products.sort(key=lambda p: (
        p["info"]["priority_order"],
        p["info"]["voltage"],
        p["info"]["power_w"],
        p["name"]
    ))

    # 3. Save JSON
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    json_path = os.path.join(OUTPUT_DIR, "tim_zasilacze_descriptions.json")

    json_products = []
    for p in products:
        jp = {k: v for k, v in p.items() if k != "info"}
        jp["parsed_info"] = {k: v for k, v in p["info"].items() if k != "raw_name"}
        json_products.append(jp)

    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(json_products, f, ensure_ascii=False, indent=2)

    prmad_cnt = sum(1 for p in products if p["info"]["is_prmad"])
    sch_cnt = sum(1 for p in products if p["info"]["is_scharfer"])
    print(f"✅ Wygenerowano precyzyjne opisy dla {len(products)} zasilaczy LED:")
    print(f"   ⭐ PR-MAD Smart Auto: {prmad_cnt}")
    print(f"   🏆 Schärfer 7Y Hermetic: {sch_cnt}")
    print(f"   📦 Standardowe / Mean Well: {len(products) - prmad_cnt - sch_cnt}")
    print(f"   JSON: {json_path}")

    return products


if __name__ == "__main__":
    main()
