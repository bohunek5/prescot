#!/usr/bin/env python3
"""
MASTER GENERATOR OPISÓW TAŚM LED DLA TIM.PL & PRESCOT (V9.0 PRO)
Perfekcyjna dbałość o detale inżynierskie i językowe:
1. Jednostki miar zawsze jawne (mm, m, W, W/m, V, K, CRI).
2. Obsługa wariantów 'bez 3M' (dedykowane do wklejania na klej/taśmę termo).
3. Prawidłowa gramatyka języka polskiego: 'objęte 7-letnią / 5-letnią / 3-letnią / 2-letnią gwarancją'.
4. Dokładne barwy: 2800–3200K, 4000–4500K, 6000–7000K, CCT, RGB, RGBW, Bread 2500K.
5. Dokładne szpule: (5), (10), (25), (50), (100) z wyliczonym zasilaczem i zasilaniem sekcyjnym.
6. Miedź PCB: Delux 24V -> 4oz, Delux 12V -> 3oz, Premium 24V -> 3oz, Premium 12V -> 2oz, Economic -> 1oz.
"""

import xml.etree.ElementTree as ET
import html
import json
import re
import os
import hashlib

CATALOG_PATH = "/Users/karolbohdanowicz/my-ai-agents/prescot/data/catalog.json"
OUTPUT_DIR = "/Users/karolbohdanowicz/my-ai-agents/prescot/tmp/tim-opisy-tasmy"
HTML_OUTPUT_PATH = os.path.join(OUTPUT_DIR, "index.html")

os.makedirs(OUTPUT_DIR, exist_ok=True)

PSU_STEPS = [12, 15, 18, 20, 24, 30, 36, 40, 45, 50, 60, 75, 100, 120, 150, 200, 240, 250, 300, 350, 400, 500, 600]

def calc_psu(total_w):
    req = total_w * 1.2
    for step in PSU_STEPS:
        if step >= req:
            return step
    return int(round(req / 50.0) * 50)


def pick(seed_str, salt, options):
    h = int(hashlib.md5(f"{seed_str}_{salt}".encode("utf-8")).hexdigest(), 16)
    return options[h % len(options)]


def extract_tape_specs(name, code, ean, price):
    uname = name.upper()
    ucode = code.upper()

    # 1. Rozpoznanie taśmy montażowej (nie jest źródłem światła)
    if any(w in uname for w in ["DWUSTRONNA", "PIANKOWA", "TERMOPRZEWODZĄCA", "KOSZULKI SILIKONOWEJ"]):
        return {
            "is_led": False,
            "name": name,
            "code": code,
            "ean": ean,
            "price": price
        }

    # 2. Wariant bez 3M
    is_bez_3m = "BEZ 3M" in uname or "BEZ 3 M" in uname or "BEZ3M" in uname

    # 3. Napięcie pracy
    v_match = re.search(r'\b(12|24|48|230)\s*V\b', uname)
    voltage = f"{v_match.group(1)}V" if v_match else ("24V" if ("24D" in ucode or "24E" in ucode or "24V" in uname) else "12V")

    # 4. Seria, miedź PCB i gwarancja
    if "DELUX" in uname or "24D" in ucode:
        series = "Delux"
        pcb_oz = "4oz" if voltage == "24V" else "3oz"
        warranty = 7
        cri = 90
    elif "COB" in uname or "WCOB" in uname:
        series = "COB"
        pcb_oz = "3oz" if voltage == "24V" else "2oz"
        warranty = 3
        cri = 90
    elif "PREMIUM" in uname or "EHP" in ucode or "E007" in ucode:
        series = "Premium"
        pcb_oz = "3oz" if voltage == "24V" else "2oz"
        warranty = 5 if ("PL5Y" in uname or "5Y" in uname or "5 LAT" in uname) else 3
        cri = 90 if "CRI90" in uname else 80
    elif "ECONOMIC" in uname or "EH007" in ucode:
        series = "Standard"
        pcb_oz = "1oz"
        warranty = 2
        cri = 80
    elif "BREAD" in uname or "2500K" in uname:
        series = "Bread"
        pcb_oz = "3oz" if voltage == "24V" else "2oz"
        warranty = 3
        cri = 90
    else:
        series = "Standard"
        pcb_oz = "2oz" if voltage == "24V" else "1oz"
        warranty = 2
        cri = 80

    # Poprawna gramatyka odmiany gwarancji (narzędnik i mianownik)
    warr_map = {
        1: ("roczną gwarancją", "1 rok"),
        2: ("2-letnią gwarancją", "2 lata"),
        3: ("3-letnią gwarancją", "3 lata"),
        4: ("4-letnią gwarancją", "4 lata"),
        5: ("5-letnią gwarancją", "5 lat"),
        7: ("7-letnią gwarancją", "7 lat")
    }
    warr_adj, warr_nom = warr_map.get(warranty, (f"{warranty}-letnią gwarancją", f"{warranty} lat"))

    # 5. Barwa światła i zastosowanie optyczne
    if "RGB+CCT" in uname or "RGB + CCT" in uname:
        color_name = "RGB + CCT wielokolorowa z regulacją bieli"
        color_tag = "rgb_cct"
        color_desc = "pełnej palecie kolorów RGB oraz płynnie regulowanym odcieniu bieli (2700–6500K)"
    elif "RGBW" in uname or "RGB+W" in uname or "4W1" in uname:
        color_name = "RGBW wielokolorowa + biała"
        color_tag = "rgbw"
        color_desc = "bogatych barwach RGB uzupełnionych o niezależny kanał czystego światła białego"
    elif "RGB" in uname:
        color_name = "RGB wielokolorowa"
        color_tag = "rgb"
        color_desc = "żywych, nasyconych kolorach RGB do dekoracyjnych zmian aranżacji"
    elif "CCT" in uname:
        color_name = "CCT regulowana (2700–6500K)"
        color_tag = "cct"
        color_desc = "płynnie zmiennej temperaturze barwowej od ciepłego po chłodny odcień bieli"
    elif any(w in uname for w in ["2700K", "2800K", "3000K", "2800-3200K", "2800–3200K", "CIEPŁA", "CIEPLA"]) or re.search(r'-WW\b|-WW\d+', ucode):
        cct_val = re.search(r'(2700|2800|3000)\s*K', uname)
        val = cct_val.group(1) if cct_val else "3000"
        range_tag = "2800–3200K" if ("2800-3200" in uname or "2800–3200" in uname) else f"{val}K"
        color_name = f"ciepła biała {range_tag}"
        color_tag = "warm"
        color_desc = f"przyjemnym, ciepłym świetle {range_tag} sprzyjającym wyciszeniu i relaksowi"
    elif any(w in uname for w in ["4000K", "4500K", "4000-4500K", "4000–4500K", "NEUTRALNA"]) or re.search(r'-NW\b|-NW\d+', ucode):
        cct_val = re.search(r'(4000|4500)\s*K', uname)
        val = cct_val.group(1) if cct_val else "4000"
        range_tag = "4000–4500K" if ("4000-4500" in uname or "4000–4500" in uname) else f"{val}K"
        color_name = f"neutralna biała {range_tag}"
        color_tag = "neutral"
        color_desc = f"czystym, naturalnym świetle dziennym {range_tag} niemęczącym wzroku i wiernie oddającym kolory"
    elif any(w in uname for w in ["6000K", "6500K", "7000K", "6000-7000K", "6000–7000K", "ZIMNA"]) or re.search(r'-W\b|-CW\b|-W\d+', ucode):
        cct_val = re.search(r'(6000|6500|7000)\s*K', uname)
        val = cct_val.group(1) if cct_val else "6500"
        range_tag = "6000–7000K" if ("6000-7000" in uname or "6000–7000" in uname) else f"{val}K"
        color_name = f"zimna biała {range_tag}"
        color_tag = "cold"
        color_desc = f"chłodnym, wyrazistym świetle {range_tag} o wysokim kontraście i nowoczesnym charakterze"
    elif "BREAD" in uname or "2500K" in uname:
        color_name = "piekarnicza Bread 2500K"
        color_tag = "bread"
        color_desc = "specjalistycznym, ciepło-złocistym świetle podkreślającym świeżość pieczywa i wypieków"
    elif "CZERWONA" in uname or "-R" in ucode:
        color_name = "czerwona"
        color_tag = "red"
        color_desc = "głębokim, wyrazistym czerwonym świetle akcentującym"
    elif "ZIELONA" in uname or "-G" in ucode:
        color_name = "zielona"
        color_tag = "green"
        color_desc = "soczyście zielonym świetle dekoracyjnym"
    elif "NIEBIESKA" in uname or "-B" in ucode:
        color_name = "niebieska"
        color_tag = "blue"
        color_desc = "chłodnym błękitnym świetle nadającym futurystyczny klimat"
    elif "ŻÓŁTA" in uname or "ZOLTA" in uname or "-Y" in ucode:
        color_name = "żółta"
        color_tag = "yellow"
        color_desc = "nasyconym żółtym świetle przyciągającym wzrok"
    else:
        color_name = "neutralna biała 4000K"
        color_tag = "neutral"
        color_desc = "równomiernym, estetycznym świetle liniowym"

    # 6. Długość rolki / szpuli
    length_m = 5
    is_meter = False

    bracket_m = re.search(r'\((\d+)\)', uname)
    if bracket_m and int(bracket_m.group(1)) in [1, 5, 10, 15, 20, 25, 30, 40, 50, 100]:
        length_m = int(bracket_m.group(1))
    elif re.search(r'\b100\s*M\b|ROLKA\s*100M', uname): length_m = 100
    elif re.search(r'\b50\s*M\b|ROLKA\s*50M', uname): length_m = 50
    elif re.search(r'\b25\s*M\b|ROLKA\s*25M', uname): length_m = 25
    elif re.search(r'\b10\s*M\b|ROLKA\s*10M', uname): length_m = 10
    elif re.search(r'\b5\s*M\b|ROLKA\s*5M', uname): length_m = 5
    elif re.search(r'\b1\s*M\b|NA METRY', uname):
        length_m = 1
        is_meter = True

    # 7. Moc W/m i łączny pobór
    w_match = re.search(r'(\d+(?:[.,]\d+)?)\s*W(?:\/m)?', uname)
    if w_match:
        power_w_m = float(w_match.group(1).replace(",", "."))
    else:
        if "240LED" in uname: power_w_m = 19.2
        elif "140LED" in uname: power_w_m = 14.0
        elif "120LED" in uname: power_w_m = 9.6
        elif "60LED" in uname: power_w_m = 4.8
        elif "30LED" in uname: power_w_m = 2.4
        elif "COB" in series: power_w_m = 10.0
        else: power_w_m = 9.6

    total_power = round(power_w_m * length_m, 1)
    rec_psu = calc_psu(total_power)

    # 8. Szerokość taśmy
    w_dim_match = re.search(r'(\d+)\s*mm\b', uname)
    width = f"{w_dim_match.group(1)} mm" if w_dim_match else ("10 mm" if ("COB" in series or power_w_m >= 14 or "RGB" in uname) else "8 mm")

    # 9. Klasa szczelności
    ip = "IP67" if ("IP67" in uname or "HERMETYCZ" in uname or "WODOODPORN" in uname) else ("IP65" if "IP65" in uname else ("IP63" if "IP63" in uname else "IP20"))

    return {
        "is_led": True,
        "is_bez_3m": is_bez_3m,
        "name": name,
        "code": code,
        "ean": ean,
        "price": price,
        "series": series,
        "voltage": voltage,
        "pcb_oz": pcb_oz,
        "warranty": warranty,
        "warr_adj": warr_adj,
        "warr_nom": warr_nom,
        "cri": cri,
        "color_name": color_name,
        "color_tag": color_tag,
        "color_desc": color_desc,
        "length_m": length_m,
        "is_meter": is_meter,
        "power_w_m": power_w_m,
        "total_power": total_power,
        "rec_psu": rec_psu,
        "width": width,
        "ip": ip
    }


def generate_tape_3layers_and_faq(spec):
    if not spec["is_led"]:
        title = f"Taśma montażowa dwustronna {spec['name']} Prescot"
        w1 = f"Taśma dwustronna montażowa Prescot to profesjonalna taśma klejąca o wysokiej przyczepności, przeznaczona do pewnego mocowania profili LED, osłon oraz taśm oświetleniowych na różnych powierzchniach."
        w2 = "Stosowana przy montażu oświetlenia LED w meblach, sufitach podwieszanych, ściankach działowych oraz w zabudowach z płyt gipsowo-kartonowych."
        w3 = [
            f"Nazwa: {spec['name']}",
            f"Kod: {spec['code']}",
            "Przeznaczenie: Trwałe mocowanie elementów instalacji LED",
            "Mocny klej odporny na starzenie i podwyższone temperatury pracy"
        ]
        dobor = "Taśmę montażową nakładać na czyste, suche i odtłuszczone powierzchnie. Zapewnia pewne i czyste połączenie bez konieczności wiercenia."
        faq = [
            ("Na jakich powierzchniach można stosować tę taśmę?", "Taśma świetnie klei się do aluminium, drewna, płyt meblowych, szkła oraz tworzyw sztucznych.")
        ]
        return {"title": title, "w1": w1, "w2": w2, "w3": w3, "dobor": dobor, "faq": faq}

    name = spec["name"]
    code = spec["code"]
    series = spec["series"]
    volt = spec["voltage"]
    pcb = spec["pcb_oz"]
    warr_adj = spec["warr_adj"]
    warr_nom = spec["warr_nom"]
    cri = spec["cri"]
    pwm = spec["power_w_m"]
    len_m = spec["length_m"]
    tot_w = spec["total_power"]
    psu = spec["rec_psu"]
    col_name = spec["color_name"]
    col_desc = spec["color_desc"]
    col_tag = spec["color_tag"]
    width = spec["width"]
    ip = spec["ip"]
    is_bez_3m = spec["is_bez_3m"]
    uid = f"{code}_{name}"

    extra_3m_note = " (wersja bez taśmy samoprzylepnej 3M, przeznaczona do profesjonalnego montażu na klej silikonowy lub taśmę termoprzewodzącą)" if is_bez_3m else ""

    # -------------------------------------------------------------------------
    # WARSTWA 1: Co to jest? (1–2 zdania prostym językiem)
    # -------------------------------------------------------------------------
    if series == "Delux":
        v1_opts = [
            f"Taśma LED Prescot DELUX 7Y ({volt}, {pwm}W/m) to najwyższej klasy oświetlenie liniowe o {col_desc}, zbudowane na wzmocnionym podwójnym podkładzie miedzianym PCB {pcb} i objęte {warr_adj} producenta{extra_3m_note}.",
            f"Prescot DELUX 7Y {volt} DC to flagowy pasek świetlny na grubym miedzianym podłożu PCB {pcb}, gwarantujący idealne odwzorowanie naturalnych kolorów (CRI Ra > {cri}) bez spadków jasności na długich odcinkach{extra_3m_note}.",
            f"Wysokosprawna taśma LED z serii Delux 7Y ({col_name}, moc {pwm}W/m, długość {len_m}m) to profesjonalne źródło światła klasy Premium, zapewniające wieloletnią trwałość dzięki miedzi PCB {pcb}{extra_3m_note}."
        ]
    elif series == "COB":
        v1_opts = [
            f"Taśma LED COB Prescot {volt} ({pwm}W/m) to nowoczesny pasek świetlny w technologii Chip-on-Board, emitujący idealnie gładką, jednolitą linię światła (efekt neonu) bez widocznych pojedynczych punktów świetlnych{extra_3m_note}.",
            f"Bezszwowa taśma oświetleniowa COB {volt} DC marki Prescot tworzy ciągłą wstęgę światła o {col_desc}, eliminując efekt kropek nawet w bardzo płytkich profilach aluminiowych.",
            f"Pasek świetlny COB {volt} DC o mocy {pwm}W/m i szerokim kącie świecenia 180° to doskonały wybór do nowoczesnych aranżacji wymagających perfekcyjnie jednolitego oświetlenia liniowego."
        ]
    elif series == "Premium":
        v1_opts = [
            f"Taśma LED Prescot PREMIUM {volt} ({pwm}W/m, podkład PCB {pcb}) to solidne i wydajne źródło światła o {col_desc}, objęte {warr_adj} i przeznaczone do codziennych instalacji meblowych, sufitowych i architektonicznych{extra_3m_note}.",
            f"Profesjonalna taśma LED z serii Prescot Premium {volt} DC na miedzianym podłożu PCB {pcb} zapewnia mocny, stabilny strumień światła przy zachowaniu optymalnego chłodzenia.",
            f"Elastyczny pasek ledowy Prescot Premium ({volt}, {col_name}, moc {pwm}W/m, szpula {len_m}m) to sprawdzone rozwiązanie do estetycznego oświetlenia w domach i lokalach użytkowych."
        ]
    else:
        v1_opts = [
            f"Taśma LED Prescot Standard {volt} ({pwm}W/m, szpula {len_m}m) to sprawdzony i funkcjonalny pasek oświetleniowy o {col_desc}, objęty {warr_adj} i stworzony do estetycznych instalacji liniowych i doświetlających{extra_3m_note}.",
            f"Pasek świetlny Prescot Standard {volt} DC o mocy {pwm}W/m to niezawodne rozwiązanie do montażu w korytarzach, garderobach i wnękach meblowych.",
            f"Taśma LED Prescot {volt} ({pwm}W/m, {col_name}) to uniwersalny pasek oświetleniowy objęty {warr_adj}, przeznaczony do energooszczędnego oświetlenia liniowego i dekoracyjnego{extra_3m_note}."
        ]
    w1 = pick(uid, "w1", v1_opts)

    # -------------------------------------------------------------------------
    # WARSTWA 2: Do czego się używa / Gdzie zamontować / Dla kogo?
    # -------------------------------------------------------------------------
    if col_tag == "warm":
        v2_opts = [
            "Ciepła barwa światła wprowadza do wnętrza spokój, przytulność i harmonijny nastrój. Doskonale sprawdza się w salonach, sypialniach, strefach relaksu, a także jako nastrojowe podświetlenie półek, wnęk ściennych i cokołów.",
            "Świetnie sprawdza się w pomieszczeniach wypoczynkowych, pokojach dziennych, sypialniach oraz restauracjach i kawiarniach, gdzie zależy nam na miękkim, relaksującym klimacie."
        ]
    elif col_tag == "neutral":
        v2_opts = [
            "Neutralna barwa światła to najbardziej uniwersalny odcień zbliżony do naturalnego światła dziennego. Nie męczy wzroku i idealnie nadaje się do oświetlenia blatów roboczych w kuchni, biurek, łazienek oraz korytarzy.",
            "Znakomicie sprawdza się jako oświetlenie główne i zadaniowe w kuchniach, garderobach, domowych gabinetach, a także w biurach, gabinetach lekarskich i sklepach."
        ]
    elif col_tag == "cold":
        v2_opts = [
            "Zimne, wyraziste światło o temperaturze barwowej powyżej 6000K zapewnia wysoki kontrast i nowoczesny odbiór wizualny. Doskonale sprawdza się w nowoczesnych aranżacjach, witrynach sklepowych, gablotach jubilerskich oraz w pomieszczeniach technicznych i warsztatach.",
            "Idealny wybór do wnętrz o minimalistycznej stylistyce, stref roboczych oraz ekspozycji towarowych wymagających maksymalnej przejrzystości i wyrazistego doświetlenia detali."
        ]
    elif col_tag == "cct":
        v2_opts = [
            "Dzięki możliwości płynnej regulacji barwy bieli (CCT 2700–6500K) możesz dopasować nastrój oświetlenia do pory dnia – od relaksującego ciepłego światła wieczorem po rześką biel pobudzającą do pracy w ciągu dnia."
        ]
    elif col_tag in ["rgb", "rgbw", "rgb_cct"]:
        v2_opts = [
            "Pełna paleta barw RGB pozwala na natychmiastową zmianę klimatu wnętrza za pomocą pilota lub aplikacji. Znakomity wybór do sufitów podwieszanych, stref gamingowych, kin domowych oraz lokali gastronomicznych i klubów."
        ]
    elif col_tag == "bread":
        v2_opts = [
            "Dedykowana do witryn piekarniczych, stoisk cukierniczych, regałów ze świeżym pieczywem w marketach oraz kawiarni. Specjalne widmo eksponuje złocistą chrupkość skórki i świeży wygląd pieczywa."
        ]
    else:
        v2_opts = [
            f"Światło w kolorze {col_name} tworzy wyrazisty akcent dekoracyjny przyciągający wzrok. Sprawdzi się w reklamie, podświetleniach gablot, witryn oraz designerskich projektach oświetleniowych."
        ]
    w2 = pick(uid, "w2", v2_opts)

    # -------------------------------------------------------------------------
    # WARSTWA 3: Parametry techniczne w punktach
    # -------------------------------------------------------------------------
    montaz_punkt = "Mocowanie: Wersja bez fabrycznej taśmy 3M (do wklejania na klej silikonowy lub taśmę termoprzewodzącą)" if is_bez_3m else "Mocowanie: Fabryczna mocna taśma samoprzylepna na spodzie PCB"
    montaz_info = "Z uwagi na brak fabrycznej taśmy klejącej 3M, taśmę należy wkleić w profil za pomocą kleju silikonowego, pasty termoprzewodzącej lub dedykowanej taśmy montażowej." if is_bez_3m else "Taśma wyposażona jest w warstwę samoprzylepną ułatwiającą szybkie pozycjonowanie w rowku profilu."
    is_bulk = len_m >= 15
    is_meter = spec.get("is_meter") or len_m == 1
    psu_1m = calc_psu(pwm)

    if is_bulk:
        power_line = f"Moc znamionowa: {pwm} W/m"
        length_line = f"Forma dostawy: Szpula instalatorska {len_m} m (do cięcia na wymiar)"
        psu_line = f"Dobór zasilacza: Zasilacz dobiera się do długości docelowego odcinka (min. {psu_1m} W na każdy 1 metr bieżący z 20% rezerwą mocy)"
        install_line = "Zasada zasilania: Maksymalny odcinek zasilany jednostronnie to 5 m. Dłuższe linie zasilaj obustronnie lub sekcyjnie, aby uniknąć spadków napięcia"
        dobor = (
            f"Szpula instalatorska {len_m} m przeznaczona jest do docinania na wymiar konkretnych odcinków montażowych w meblach, sufitach i profilach.\n\n"
            f"Zasilacz dobiera się proporcjonalnie do długości docelowego odcinka oświetleniowego, przyjmując pobór mocy {pwm} W/m oraz dodając minimum 20% rezerwy mocy (np. odcinek 2 m wymaga zasilacza min. {calc_psu(pwm*2)} W, 3 m min. {calc_psu(pwm*3)} W, a 5 m min. {calc_psu(pwm*5)} W {volt} DC z oferty Prescot lub Schärfer).\n\n"
            f"ZASADA MONTAŻOWA DLA DŁUGICH LINII: Szpuli {len_m} m nie wolno zasilać z jednego punktu w całości z uwagi na naturalne zjawisko spadków napięcia na ścieżkach miedzianych. Maksymalna długość pojedynczego obwodu zasilanego jednostronnie wynosi 5 m. Dłuższe ciągi świetlne należy dzielić na niezależne sekcje lub doprowadzać zasilanie równolegle (np. co 5 m) bądź obustronnie.\n\n"
            f"Taśmę należy bezwzględnie montować w profilu aluminiowym o szerokości wewnętrznej minimum {width}. Profil aluminiowy pełni kluczową rolę radiatora – odprowadza ciepło z pracujących diod LED, chroni luminofor przed degradacją termiczną i znacząco wydłuża żywotność taśmy. {montaz_info}\n\n"
            f"Taśma w pełni współpracuje ze ściemniaczami i sterownikami LED {volt} (radiowymi 2.4GHz MiBoxer, panelami ściennymi oraz systemami Tuya/WiFi)."
        )
        faq_psu = (
            f"Jak dobrać zasilacz do taśmy ze szpuli instalatorskiej ({len_m} m)?",
            f"Szpula instalatorska {len_m} m służy do cięcia na odcinki montażowe. Zasilacz dobiera się do długości konkretnego montowanego odcinka, przyjmując moc {pwm} W na metr i dodając 20% rezerwy mocy (np. odcinek 2 m = zasilacz min. {calc_psu(pwm*2)} W, odcinek 5 m = min. {calc_psu(pwm*5)} W). Długie linie powyżej 5 m należy zasilać w sekcjach lub obustronnie, aby zapobiec spadkom napięcia."
        )
    elif is_meter:
        power_line = f"Moc znamionowa: {pwm} W/m"
        length_line = "Długość: 1 m (sprzedaż na metry bieżące)"
        psu_line = f"Zalecana moc zasilacza: minimum {psu_1m} W {volt} DC na każdy 1 metr (z 20% rezerwą mocy)"
        install_line = None
        dobor = (
            f"Do zasilenia 1 metra bieżącego taśmy LED (pobór {pwm} W) rekomendujemy zasilacz {volt} o mocy minimum {psu_1m} W z 20% rezerwą mocy. Przy montażu dłuższego ciągu zsumuj łączną moc odcinków i dobierz odpowiednio transformator z oferty Prescot lub Schärfer.\n\n"
            f"Taśmę należy bezwzględnie montować w profilu aluminiowym o szerokości wewnętrznej minimum {width}. Profil aluminiowy odprowadza ciepło z diod i znacząco wydłuża żywotność taśmy. {montaz_info}"
        )
        faq_psu = (
            "Jak dobrać zasilacz do taśmy ciętej na metry?",
            f"Zsumuj łączną długość montowanych odcinków, pomnóż przez {pwm} W/m i dodaj minimum 20% rezerwy mocy (np. 3 m x {pwm} W/m = {round(pwm*3, 1)} W, zasilacz min. {calc_psu(pwm*3)} W)."
        )
    else:
        power_line = f"Moc znamionowa: {pwm} W/m (cała rolka {len_m} m = {tot_w} W)"
        length_line = f"Długość rolki: {len_m} m"
        psu_line = f"Zalecana moc zasilacza: minimum {psu} W {volt} DC (z 20% rezerwą mocy dla pełnej rolki {len_m} m)"
        install_line = None
        dobor = (
            f"Do zasilenia całej długości {len_m} m (łączny pobór mocy {tot_w} W) rekomendujemy zasilacz impulsowy {volt} o mocy minimum {psu} W z oferty Prescot "
            f"(np. z inteligentnej serii Smart Auto PR-MAD lub hermetyczny Schärfer 7Y), co gwarantuje stabilną i bezpieczną pracę z wymaganym 20% zapasem mocy.\n\n"
            f"Taśmę należy bezwzględnie montować w profilu aluminiowym o szerokości wewnętrznej minimum {width}. "
            f"Profil aluminiowy pełni kluczową rolę radiatora – odprowadza ciepło z pracujących diod LED, chroni luminofor przed degradacją termiczną i znacząco wydłuża żywotność taśmy. {montaz_info}\n\n"
            f"Taśma w pełni współpracuje ze ściemniaczami i sterownikami LED {volt} (radiowymi 2.4GHz MiBoxer, panelami ściennymi oraz systemami Tuya/WiFi)."
        )
        faq_psu = (
            f"Jaki zasilacz dobrać do tej taśmy ({len_m} m)?",
            f"Do zasilenia pełnego odcinka {len_m} m (pobór {tot_w} W) zastosuj zasilacz {volt} o mocy co najmniej {psu} W. 20% rezerwy chroni transformator przed przegrzaniem i wydłuża jego żywotność."
        )

    w3 = [
        f"Napięcie zasilania: {volt} DC (napięcie stałe stabilizowane)",
        power_line,
        length_line,
        f"Podkład miedziany: PCB {pcb} (efektywne odprowadzanie ciepła i brak spadków napięć)",
        f"Wskaźnik oddawania barw: CRI Ra > {cri} (naturalna wierność kolorów)",
        f"Barwa światła: {col_name}",
        f"Gwarancja producenta: {warr_nom} (seria Prescot {series})",
        f"Szerokość taśmy: {width}",
        f"Klasa szczelności: {ip}",
        montaz_punkt,
        psu_line
    ]
    if install_line:
        w3.append(install_line)

    faq_3m = [
        ("Jak zamontować taśmę w wersji bez 3M?", "Taśmę bez warstwy samoprzylepnej montuje się w profilu aluminiowym przy użyciu profesjonalnego silikonu neutralnego, kleju montażowego do elektroniki lub dwustronnej taśmy termoprzewodzącej.")
    ] if is_bez_3m else []

    faq = [
        faq_psu,
        (
            "Czy taśma LED wymaga montażu w profilu aluminiowym?",
            f"Tak. Profil aluminiowy działa jak radiator chłodzący diody. Montaż w profilu z dopasowaną osłoną (mleczną lub satynową) zapobiega przegrzewaniu się taśmy i chroni ją przed kurzem i zanieczyszczeniami."
        ),
        (
            "Czy można ciąć tę taśmę na krótsze odcinki?",
            "Tak, taśmę można bezpiecznie skracać zwykłymi nożyczkami w specjalnie oznaczonych sekcjach cięcia z punktami lutowniczymi."
        ),
        (
            f"Dlaczego grubość podkładu miedzi PCB {pcb} jest tak ważna?",
            f"Gruba warstwa miedzi PCB {pcb} gwarantuje sprawne odprowadzanie ciepła z dala od chipów diodowych oraz eliminuje spadki napięć, dzięki czemu taśma świeci jednakowo jasno na całej długości."
        )
    ]
    if faq_3m:
        faq.insert(2, faq_3m[0])

    return {
        "title": f"Taśma LED Prescot {series} {volt} DC {pwm}W/m PCB {pcb} CRI>{cri}",
        "w1": w1,
        "w2": w2,
        "w3": w3,
        "dobor": dobor,
        "faq": faq
    }


def build_html_card(idx, p, copy_data, parsed):
    name = parsed["name"]
    code = parsed["code"]
    ean = parsed["ean"]
    price = p.get("price", "0.00")

    if not parsed["is_led"]:
        return f"""      <div class="tape-card" id="card-{idx}">
        <div class="card-header">
          <div class="card-top">
            <span class="card-num">{idx}.</span>
            <div class="card-badges">
              <span class="badge badge-series">Akcesoria</span>
              <span class="badge badge-ip">Taśma montażowa</span>
            </div>
          </div>
          <h3 class="card-name">{html.escape(name)}</h3>
          <div class="card-meta">
            <span class="meta-code">Kod: {html.escape(code)}</span>
            <span class="meta-ean">EAN: {html.escape(ean)}</span>
            <span class="meta-price">{price} PLN</span>
          </div>
        </div>
        <div class="card-body">
          <div class="desc-block intro">
            <div class="section-title">WARSTWA 1: CO TO JEST?</div>
            <p>{html.escape(copy_data["w1"])}</p>
          </div>
          <div class="desc-block barwa">
            <div class="section-title">WARSTWA 2: ZASTOSOWANIE I MIEJSCE MONTAŻU</div>
            <p>{html.escape(copy_data["w2"])}</p>
          </div>
          <div class="desc-block params">
            <div class="section-title">WARSTWA 3: PARAMETRY TECHNICZNE W PUNKTACH</div>
            <ul>
              {"".join([f"<li>{html.escape(item)}</li>" for item in copy_data["w3"]])}
            </ul>
          </div>
        </div>
      </div>"""

    badge_series = parsed["series"]
    badge_v = parsed["voltage"]
    badge_w = f"{parsed['power_w_m']}W/m"
    badge_len = f"📏 {parsed['length_m']}m"
    badge_psu = f"⚡ {parsed['rec_psu']}W"
    badge_war = f"🛡️ {parsed['warr_nom']}"
    badge_ip = f"💧 {parsed['ip']}"
    badge_pcb = f"Cu {parsed['pcb_oz']}"
    badge_3m = '<span class="badge" style="background:#475569; color:#f8fafc;">Bez 3M</span>' if parsed.get("is_bez_3m") else ""

    faq_html = "\n".join([
        f'              <div class="faq-item"><strong>P: {html.escape(q)}</strong><p>O: {html.escape(a)}</p></div>'
        for q, a in copy_data["faq"]
    ])

    w3_html = "\n".join([
        f'              <li>{html.escape(item)}</li>'
        for item in copy_data["w3"]
    ])

    dobor_formatted = html.escape(copy_data["dobor"]).replace("\n\n", "</p><p>")

    return f"""      <div class="tape-card" id="card-{idx}">
        <div class="card-header">
          <div class="card-top">
            <span class="card-num">{idx}.</span>
            <div class="card-badges">
              <span class="badge badge-series">{html.escape(badge_series)}</span>
              <span class="badge badge-volt">{html.escape(badge_v)}</span>
              <span class="badge badge-pcb">{html.escape(badge_pcb)}</span>
              <span class="badge badge-len">{html.escape(badge_len)}</span>
              <span class="badge badge-power">{html.escape(badge_w)}</span>
              <span class="badge badge-psu">{html.escape(badge_psu)}</span>
              <span class="badge badge-war">{html.escape(badge_war)}</span>
              <span class="badge badge-ip">{html.escape(badge_ip)}</span>
              {badge_3m}
            </div>
          </div>
          <h3 class="card-name">{html.escape(name)}</h3>
          <div class="card-meta">
            <span class="meta-code">Kod: {html.escape(code)}</span>
            <span class="meta-ean">EAN: {html.escape(ean)}</span>
            <span class="meta-price">{price} PLN</span>
          </div>
        </div>
        <div class="card-body">
          <div class="desc-block intro">
            <div class="section-title">WARSTWA 1: CO TO JEST?</div>
            <p>{html.escape(copy_data["w1"])}</p>
          </div>
          <div class="desc-block barwa">
            <div class="section-title">WARSTWA 2: ZASTOSOWANIE I MIEJSCE MONTAŻU</div>
            <p>{html.escape(copy_data["w2"])}</p>
          </div>
          <div class="desc-block params">
            <div class="section-title">WARSTWA 3: PARAMETRY TECHNICZNE W PUNKTACH</div>
            <ul>
{w3_html}
            </ul>
          </div>
          <div class="desc-block dobor">
            <div class="section-title">DOBÓR ZASILACZA I PROFILU ALUMINIOWEGO</div>
            <p>{dobor_formatted}</p>
          </div>
          <div class="desc-block faq-section">
            <div class="section-title">FAQ – NAJCZĘŚCIEJ ZADAWANE PYTANIA KLIENTÓW</div>
            <div class="faq-list">
{faq_html}
            </div>
          </div>
        </div>
      </div>"""


def main():
    print("⏳ Wczytywanie bazy produktów...")
    with open(CATALOG_PATH, "r", encoding="utf-8") as f:
        catalog = json.load(f)

    prods = catalog["products"]
    tape_prods = [p for p in prods if p.get("categoryRoot") == "Taśmy LED" or "Taśma" in str(p.get("name", ""))]
    print(f"📦 Przetwarzanie {len(tape_prods)} taśm przez silnik V9.0...")

    cards_html = []
    for idx, p in enumerate(tape_prods, 1):
        name = str(p.get("name", "")).strip()
        code = str(p.get("code", "")).strip()
        ean = str(p.get("ean", "")).strip()
        price = p.get("price", "0.00")

        parsed = extract_tape_specs(name, code, ean, price)
        copy_data = generate_tape_3layers_and_faq(parsed)
        cards_html.append(build_html_card(idx, p, copy_data, parsed))

    grid_content = "\n".join(cards_html)
    full_html = f"""<!DOCTYPE html>
<html lang="pl">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Master Opisy Taśm LED Prescot & TIM — Pełny Standard SEO / B2B</title>
  <style>
    :root {{
      --bg: #0f172a;
      --card-bg: #1e293b;
      --border: #334155;
      --text: #f8fafc;
      --text-muted: #94a3b8;
      --primary: #38bdf8;
      --accent: #f59e0b;
      --green: #10b981;
      --purple: #a855f7;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      background: var(--bg);
      color: var(--text);
      line-height: 1.6;
      padding: 30px 20px;
    }}
    .container {{ max-width: 1200px; margin: 0 auto; }}
    .header {{ text-align: center; margin-bottom: 40px; padding-bottom: 20px; border-bottom: 1px solid var(--border); }}
    .header h1 {{ font-size: 28px; font-weight: 800; color: #fff; margin-bottom: 10px; }}
    .header p {{ color: var(--text-muted); font-size: 15px; }}
    .grid {{ display: flex; flex-direction: column; gap: 30px; }}
    .tape-card {{
      background: var(--card-bg);
      border: 1px solid var(--border);
      border-radius: 16px;
      overflow: hidden;
      box-shadow: 0 4px 20px rgba(0,0,0,0.25);
    }}
    .card-header {{ padding: 22px 26px; border-bottom: 1px solid var(--border); background: rgba(255,255,255,0.02); }}
    .card-top {{ display: flex; align-items: center; justify-content: space-between; gap: 15px; margin-bottom: 12px; }}
    .card-num {{ font-size: 18px; font-weight: 800; color: var(--primary); }}
    .card-badges {{ display: flex; flex-wrap: wrap; gap: 8px; }}
    .badge {{
      display: inline-block;
      padding: 4px 10px;
      border-radius: 999px;
      font-size: 12px;
      font-weight: 700;
      letter-spacing: .3px;
    }}
    .badge-series {{ background: rgba(56, 189, 248, 0.15); color: var(--primary); border: 1px solid var(--primary); }}
    .badge-volt {{ background: rgba(245, 158, 11, 0.15); color: var(--accent); border: 1px solid var(--accent); }}
    .badge-pcb {{ background: rgba(168, 85, 247, 0.15); color: var(--purple); border: 1px solid var(--purple); }}
    .badge-len {{ background: #334155; color: #38bdf8; border: 1px solid #475569; }}
    .badge-power {{ background: rgba(16, 185, 129, 0.15); color: var(--green); border: 1px solid var(--green); }}
    .badge-psu {{ background: #334155; color: #fff; }}
    .badge-war {{ background: rgba(239, 68, 68, 0.15); color: #f87171; border: 1px solid #f87171; }}
    .badge-ip {{ background: #1e293b; color: #94a3b8; border: 1px solid #475569; }}
    .card-name {{ font-size: 20px; font-weight: 700; color: #fff; margin-bottom: 8px; }}
    .card-meta {{ display: flex; gap: 20px; color: var(--text-muted); font-size: 13px; }}
    .meta-price {{ font-weight: 700; color: var(--green); margin-left: auto; font-size: 15px; }}
    .card-body {{ padding: 24px 26px; display: flex; flex-direction: column; gap: 20px; }}
    .desc-block {{
      background: rgba(15, 23, 42, 0.6);
      padding: 18px 20px;
      border-radius: 12px;
      border: 1px solid rgba(255,255,255,0.05);
    }}
    .section-title {{
      font-size: 12px;
      font-weight: 800;
      text-transform: uppercase;
      letter-spacing: .8px;
      color: var(--primary);
      margin-bottom: 10px;
    }}
    .desc-block p {{ color: #e2e8f0; font-size: 14.5px; line-height: 1.65; }}
    .desc-block p + p {{ margin-top: 10px; }}
    .desc-block ul {{ padding-left: 20px; color: #e2e8f0; font-size: 14px; line-height: 1.7; }}
    .desc-block ul li {{ margin-bottom: 4px; }}
    .faq-list {{ display: flex; flex-direction: column; gap: 12px; }}
    .faq-item {{ padding: 12px 14px; background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.05); border-radius: 8px; }}
    .faq-item strong {{ display: block; color: var(--accent); font-size: 14px; margin-bottom: 4px; }}
    .faq-item p {{ font-size: 13.5px; color: #cbd5e1; }}
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <h1>Katalog Taśm LED Prescot & TIM — Pełny Standard SEO / B2B</h1>
      <p>Struktura 3 Warstw (Co to jest, Zastosowanie, Parametry) + Dobór Zasilacza i Profilu + FAQ zgodne z wytycznymi elektrotechnicznymi</p>
    </div>
    <div class="grid">
{grid_content}
    </div>
  </div>
</body>
</html>
"""

    with open(HTML_OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write(full_html)
    print(f"✅ Wygenerowano {HTML_OUTPUT_PATH} ({len(tape_prods)} kart produktów ze strukturą 3 warstw + FAQ V9.0)!")


if __name__ == "__main__":
    main()
