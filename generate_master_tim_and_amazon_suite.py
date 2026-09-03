#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MASTER GENERATOR OPISÓW TIM & AMAZON DLA CAŁEJ OFERTY PRESCOT (345 PRODUKTÓW)
Zgodny z wytycznymi z obu PDF-ów oraz zaleceniami Karola:
- PDF 1: SEO + AI – Ściąga do tworzenia opisów produktów (3 warstwy, FAQ, myślenie jak klient, synonimy, brak kopiowania z katalogu)
- PDF 2: Jak pisać dobre opisy w branży elektrotechnicznej (tłumaczenie zwykłemu człowiekowi, brak masła maślanego, semantyczne SEO)
- Dyrektywy Karola:
  1. Nowa dedykowana zakładka AMAZON z krótkimi, chwytliwymi punktami wyróżniającymi (Co to jest, Do czego, Unikalność, Montaż, Szybkie FAQ).
  2. Brak zasilaczy do rolek 100m/50m liczonych w całości (podajemy zasilacz na 1m i zasadę zasilania sekcyjnego co 5m).
  3. Wywalone bloki 'Najważniejsze cechy:' i 'Parametry i cechy techniczne:' wklejane na siłę (parametry są w atrybutach).
  4. Eksponowanie flagowych PR-MAD Smart Auto 12V/24V i Schärfer Hermetic IP67 7Y.
  5. Niezależne przyciski kopiowania: 'Kopiuj opis TIM' oraz 'Kopiuj format Amazon'.
"""

import json
import os
import re
import html
import hashlib

BASE_DIR = "/Users/karolbohdanowicz/my-ai-agents/prescot/tmp/tim-opisy-tasmy"
os.makedirs(BASE_DIR, exist_ok=True)

PSU_STEPS = [12, 15, 18, 20, 24, 30, 36, 40, 45, 50, 60, 75, 100, 120, 150, 200, 240, 250, 300, 350, 400, 500, 600]

def calc_psu(total_w):
    req = total_w * 1.20
    for step in PSU_STEPS:
        if step >= req:
            return step
    return int(round(req / 50.0) * 50)

def esc(s):
    return html.escape(str(s or ""))

def pick(seed_str, salt, options):
    h = int(hashlib.md5(f"{seed_str}_{salt}".encode("utf-8")).hexdigest(), 16)
    return options[h % len(options)]

# ==============================================================================
# 1. TAŚMY LED (135 PRODUKTÓW)
# ==============================================================================
def process_tape(p):
    name = p["name"]
    code = p["code"]
    ean = p.get("ean", "BRAK")
    price = p.get("price", "0.00")
    stock = p.get("stock", "0")
    cat = p.get("cat", "Taśmy LED")
    subcat = p.get("subcat", "Taśmy LED")
    info = p.get("parsed_info", {})

    uname = name.upper()
    ucode = code.upper()

    # Parametry
    series = info.get("series", "Standard")
    if "DELUX" in uname: series = "Delux"
    elif "COB" in uname: series = "COB"
    elif "BREAD" in uname or "2500K" in uname: series = "Bread"
    elif "PREMIUM" in uname: series = "Premium"

    volt = info.get("voltage", "24V" if "24V" in uname or "24D" in ucode else "12V")
    width = info.get("width", "10 mm" if (series == "COB" or "RGB" in uname) else "8 mm")
    ip = info.get("ip", "IP67" if "IP67" in uname else ("IP65" if "IP65" in uname else ("IP63" if "IP63" in uname else "IP20")))
    
    len_m = info.get("length_m", 5)
    bracket_m = re.search(r'\((\d+)\)', uname)
    if bracket_m and int(bracket_m.group(1)) in [1, 5, 10, 15, 20, 25, 30, 40, 50, 100]:
        len_m = int(bracket_m.group(1))
    elif "100M" in uname: len_m = 100
    elif "50M" in uname: len_m = 50
    elif "25M" in uname: len_m = 25
    elif "10M" in uname: len_m = 10
    elif "5M" in uname: len_m = 5
    elif "1M" in uname or "METRY" in uname: len_m = 1

    is_bulk = len_m >= 15
    is_meter = info.get("is_meter") or len_m == 1
    is_bez_3m = "BEZ 3M" in uname or "BEZ 3 M" in uname or "BEZ3M" in uname

    pwm = float(info.get("power_w_m", 4.8))
    total_w = round(pwm * len_m, 1)
    rec_psu = calc_psu(total_w)
    psu_1m = calc_psu(pwm)

    pcb_map = {
        "Delux": ("4oz" if volt == "24V" else "3oz"),
        "COB": ("3oz" if volt == "24V" else "2oz"),
        "Premium": ("3oz" if volt == "24V" else "2oz"),
        "Bread": ("3oz" if volt == "24V" else "2oz"),
        "Standard": ("2oz" if volt == "24V" else "1oz")
    }
    pcb = pcb_map.get(series, "2oz")

    warr_map = {"Delux": 7, "COB": 3, "Premium": 5, "Bread": 3, "Standard": 2}
    warranty = warr_map.get(series, 2)
    cri = 90 if (series in ["Delux", "COB", "Bread"] or "CRI90" in uname) else 80

    # Kolor i barwa
    if "BREAD" in uname or "2500K" in uname:
        color_name = "piekarnicza Bread 2500K"
        color_human = "ciepłym, złocisto-bursztynowym świetle 2500K"
        color_use = "specjalistycznego oświetlenia pieczywa, wyrobów cukierniczych i bagietek, podkreślającego świeżość i chrupkość wypieków"
        amazon_color = "Złocista barwa Bread 2500K eksponuje chrupkość pieczywa i wypieków."
    elif "RGB+CCT" in uname or "RGB + CCT" in uname:
        color_name = "wielokolorowa RGB + CCT z regulacją bieli"
        color_human = "pełnej palecie kolorów RGB oraz płynnie regulowanym odcieniu bieli od ciepłej do zimnej (2700–6500K)"
        color_use = "nowoczesnych aranżacji smart home, salonów, sufitów podwieszanych i stref relaksu, gdzie chcesz zmieniać klimat jednym dotknięciem"
        amazon_color = "Miliony kolorów RGB + płynna regulacja bieli od ciepłej po chłodną (2700–6500K)."
    elif "RGBW" in uname or "4W1" in uname:
        color_name = "RGBW wielokolorowa z dodatkową czystą bielą"
        color_human = "nasyconych barwach RGB uzupełnionych o niezależny kanał czystego światła białego"
        color_use = "pokojów dziennych, sypialni, kin domowych i stref gamingowych, łącząc funkcję dekoracyjną z praktycznym oświetleniem użytkowym"
        amazon_color = "Żywe kolory RGB + niezależna czysta biel użytkowa do codziennego oświetlenia."
    elif "RGB" in uname:
        color_name = "RGB wielokolorowa"
        color_human = "żywych, nasyconych barwach palety RGB"
        color_use = "efektownego podświetlenia sufitów, witryn meblowych, barów oraz stref rozrywki"
        amazon_color = "Nasycone, żywe kolory RGB do tworzenia unikalnych nastrojowych iluminacji."
    elif "CCT" in uname:
        color_name = "CCT regulowana temperatura bieli (2700–6500K)"
        color_human = "zmiennej temperaturze barwowej od przytulnego ciepła po pobudzającą chłodną biel"
        color_use = "miejsc, w których oświetlenie ma dopasowywać się do rytmu dnia – ciepłe światło wieczorem, rześka biel do pracy rano"
        amazon_color = "Płynna zmiana odcienia bieli od przytulnego ciepła 2700K do chłodnej bieli 6500K."
    elif any(k in uname for k in ["3000K", "2800K", "2700K", "CIEPŁA", "CIEPLA"]) or "-WW" in ucode:
        color_name = "ciepła biała 3000K"
        color_human = "przyjemnym, miękkim świetle ciepłym białym 3000K sprzyjającym wyciszeniu i relaksowi"
        color_use = "sypialni, salonów, stref wypoczynkowych, a także podświetlenia półek, cokołów i wnęk ściennych"
        amazon_color = "Ciepłe, przytulne światło 3000K — idealne do sypialni, salonu i stref relaksu."
    elif any(k in uname for k in ["4000K", "4500K", "NEUTRALNA"]) or "-NW" in ucode:
        color_name = "neutralna biała 4000K"
        color_human = "czystym świetle neutralnym białym 4000K zbliżonym do naturalnego światła słonecznego"
        color_use = "kuchni (szczególnie pod szafkami nad blatem roboczym), łazienek, biurek, korytarzy i gabinetów"
        amazon_color = "Czysta biel dzienna 4000K — optymalna nad blat kuchenny, do biura i łazienki."
    elif any(k in uname for k in ["6000K", "6500K", "ZIMNA"]) or "-CW" in ucode or "-W" in ucode:
        color_name = "zimna biała 6500K"
        color_human = "chłodnym, wyrazistym świetle zimnym białym 6500K o wysokim kontraście"
        color_use = "nowoczesnych aranżacji minimalistycznych, gablot sklepowych, witryn jubilerskich oraz warsztatów i pomieszczeń technicznych"
        amazon_color = "Wyraziste, chłodne światło 6500K o wysokim kontraście do nowoczesnych wnętrz i ekspozycji."
    else:
        color_name = "neutralna biała 4000K"
        color_human = "równomiernym, estetycznym świetle liniowym"
        color_use = "ogólnego oświetlenia wnętrz domowych, biurowych oraz zabudów meblowych"
        amazon_color = "Uniwersalne światło liniowe do wszechstronnych zastosowań domowych i biurowych."

    # Unikalność i zalety techniczne
    uniqueness_points = []
    if series == "COB":
        uniqueness_points.append("Technologia COB (Chip-on-Board) zapewnia jednolitą, gładką linię światła bez widocznych punktów ledowych, nawet w bardzo płytkich profilach aluminiowych.")
    elif series == "Delux":
        uniqueness_points.append(f"Elitarna seria Delux na podwójnym podkładzie miedzi PCB {pcb} objęta aż 7-letnią gwarancją — zero przegrzewania i brak spadków jasności.")
    else:
        uniqueness_points.append(f"Miedziany podkład PCB {pcb} skutecznie odprowadza ciepło z diod, co zapobiega ich wypalaniu i zapewnia stabilny strumień światła przez lata.")

    if cri >= 90:
        uniqueness_points.append(f"Wysoki wskaźnik oddawania barw CRI Ra > {cri} gwarantuje naturalny wygląd potraw, drewna meblowego i skóry bez sinych przekłamań.")
    else:
        uniqueness_points.append("Wskaźnik oddawania barw CRI Ra > 80 zapewnia wierną i przyjemną dla oka kolorystykę oświetlanych przedmiotów.")

    if volt == "24V":
        uniqueness_points.append("Bezpieczne napięcie 24V DC ogranicza prądy robocze o połowę w porównaniu z instalacjami 12V, minimalizując spadki napięcia na dłuższych odcinkach.")
    else:
        uniqueness_points.append("Stabilizowane zasilanie 12V DC idealnie sprawdza się w instalacjach meblowych, kamperach, jachtach oraz krótkich odcinkach dekoracyjnych.")

    if is_bez_3m:
        uniqueness_points.append("Wersja bez taśmy klejącej 3M — dedykowana do profesjonalnego wklejania w profile na klej silikonowy lub taśmę termoprzewodzącą.")
    else:
        uniqueness_points.append("Oryginalna, mocna taśma samoprzylepna na spodzie podkładu zapewnia błyskawiczne i pewne mocowanie w korycie profilu.")

    uniqueness_text = " ".join(uniqueness_points)

    # Reguła zasilania i montażu (z uwzględnieniem zakazu liczenia 100m na raz!)
    if is_bulk:
        montaz_zasady = (
            f"Zasady montażu i zasilania (szpula instalatorska {len_m} m):\n"
            f"• Szpula {len_m} m służy do docinania na dokładny wymiar w meblach, sufitach i profilach.\n"
            f"• Dobór zasilacza: transformator dobiera się do długości konkretnego wyciętego odcinka, przyjmując pobór {pwm} W/m oraz dodając minimum 20% rezerwy mocy (np. odcinek 2 m = zasilacz min. {calc_psu(pwm*2)} W, odcinek 3 m = min. {calc_psu(pwm*3)} W, odcinek 5 m = min. {calc_psu(pwm*5)} W {volt} DC).\n"
            f"• ZASADA ZASILANIA DŁUGICH LINII: Maksymalna długość pojedynczego odcinka zasilanego jednostronnie to 5 m. Szpuli {len_m} m nie wolno zasilać z jednego punktu w całości! Dłuższe ciągi należy dzielić na niezależne sekcje lub zasilać równolegle co 5 m.\n"
            f"• Wymagany montaż w profilu aluminiowym o szerokości wewnętrznej min. {width} (profil odprowadza ciepło i chroni diody przed degradacją termiczną)."
        )
        psu_faq_ans = f"Szpulę {len_m} m tnie się na odcinki. Zasilacz dobierz do długości montowanych odcinków, licząc {pwm} W/m z 20% rezerwą mocy (np. 3 m = zasilacz min. {calc_psu(pwm*3)} W {volt} DC). Linie powyżej 5 m zasilaj sekcyjnie."
        amz_montaz = f"Montuj w profilu aluminiowym (odprowadza ciepło). Dobieraj zasilacz do długości montowanego odcinka ({pwm} W/m + 20% zapasu). Ciągłe linie powyżej 5 m zasilaj w sekcjach lub obustronnie."
    elif is_meter:
        montaz_zasady = (
            f"Zasady montażu i zasilania (sprzedaż na metry bieżące):\n"
            f"• Pobór mocy wynosi {pwm} W na każdy 1 metr bieżący taśmy.\n"
            f"• Dobór zasilacza: na każdy 1 metr taśmy zalecany jest zasilacz {volt} o mocy min. {psu_1m} W (z 20% rezerwą bezpieczeństwa). Dla dłuższego odcinka pomnóż metry przez {pwm} W/m i dodaj 20%.\n"
            f"• Wymagany montaż w profilu aluminiowym o szerokości wewnętrznej min. {width} (radiator chłodzący diody)."
        )
        psu_faq_ans = f"Pomnóż długość montowanego odcinka przez {pwm} W/m i dodaj 20% zapasu mocy (np. odcinek 2 m wymaga zasilacza min. {calc_psu(pwm*2)} W {volt} DC)."
        amz_montaz = f"Montuj w profilu aluminiowym. Pobór mocy {pwm} W/m — dobierz zasilacz {volt} DC z 20% rezerwą mocy (np. 1m = min. {psu_1m}W, 3m = min. {calc_psu(pwm*3)}W)."
    else:
        montaz_zasady = (
            f"Zasady montażu i zasilania (rolka {len_m} m):\n"
            f"• Pobór mocy: {pwm} W/m (cała rolka {len_m} m pobiera łącznie {total_w} W).\n"
            f"• Dobór zasilacza: do zasilenia całej rolki {len_m} m rekomendujemy zasilacz impulsowy {volt} DC o mocy minimum {rec_psu} W z oferty Prescot (zapewnia wymagany 20% margines bezpieczeństwa).\n"
            f"• Odcinki do 5 m można bezpiecznie zasilać jednostronnie. Przy dłuższych liniach zaleca się zasilanie obustronne.\n"
            f"• Wymagany montaż w profilu aluminiowym o szerokości wewnętrznej min. {width} jako radiator odprowadzający ciepło."
        )
        psu_faq_ans = f"Do zasilenia całej rolki {len_m} m (pobór {total_w} W) zalecamy zasilacz {volt} o mocy min. {rec_psu} W z 20% rezerwą mocy, np. Prescot Ultra Slim."
        amz_montaz = f"Montuj w profilu aluminiowym o szerokości min. {width}. Do całej rolki {len_m} m (pobór {total_w} W) zalecany zasilacz to min. {rec_psu} W {volt} DC (np. Prescot Ultra Slim)."

    # TIM Description (3 Warstwy + Montaż + FAQ)
    tim_w1 = f"Nowoczesna taśma LED Prescot ({series}) to profesjonalne, liniowe źródło światła o {color_human}, stworzone do równomiernego i trwałego oświetlania wnętrz."
    tim_w2 = f"Zastosowanie: idealnie sprawdza się do {color_use}. Chętnie wybierana przez elektroinstalatorów, stolarzy oraz projektantów wnętrz do domów, mieszkań i lokali usługowych."
    
    faq_items = [
        ("Czy tę taśmę można ciąć na krótsze odcinki?", f"Tak, taśmę można bezpiecznie ciąć zwykłymi nożyczkami w fabrycznie oznaczonych miejscach cięcia (co kilka centymetrów w zależności od modelu)."),
        ("Czy do taśmy potrzebny jest profil aluminiowy?", "Tak, montaż w profilu aluminiowym jest bezwzględnie zalecany. Profil działa jak radiator odprowadzający ciepło z diod, co chroni je przed przedwczesnym wypaleniem i spadkiem jasności."),
        ("Jaki zasilacz dobrać do tej taśmy?", psu_faq_ans)
    ]
    tim_faq = "Najczęściej zadawane pytania (FAQ):\n" + "\n".join([f"P: {q}\nO: {a}" for q, a in faq_items])

    tim_full = f"{tim_w1}\n\n{tim_w2}\n\n{montaz_zasady}\n\n{tim_faq}"

    # Amazon Description (Punchy bullet points)
    amz_title = f"Taśma LED Prescot {series} {volt} {pwm}W/m {color_name} {len_m}m (CRI>{cri}, Miedź PCB {pcb}, {warranty} Lat Gwarancji)"
    amz_bullets = [
        f"• CO TO JEST: {tim_w1}",
        f"• GDZIE ZAMONTUJESZ: Doskonale sprawdza się do {color_use}. {amazon_color}",
        f"• DLACZEGO TEN MODEL (UNIKALNOŚĆ): {uniqueness_text}",
        f"• MONTAŻ I ZASILANIE: {amz_montaz}",
        f"• SZYBKIE FAQ: P: Czy można ciąć? O: Tak, w oznaczonych punktach co kilka cm. P: Jaki zasilacz? O: {psu_faq_ans}"
    ]
    amz_full = f"{amz_title}\n\n" + "\n\n".join(amz_bullets)

    return {
        "id": p["id"],
        "name": name,
        "code": code,
        "ean": ean,
        "cat": cat,
        "subcat": subcat,
        "price": price,
        "stock": stock,
        "description": {
            "title": amz_title,
            "intro": tim_w1,
            "barwa": f"Barwa światła i zastosowanie\n\n{tim_w2}",
            "dobor": f"Zasady montażu i dobór zasilacza\n\n{montaz_zasady}",
            "faq": faq_items,
            "full_text": tim_full,
            "amazon_title": amz_title,
            "amazon_bullets": amz_bullets,
            "amazon_full": amz_full
        },
        "parsed_info": {
            "series": series,
            "voltage": volt,
            "width": width,
            "ip": ip,
            "length_m": len_m,
            "is_meter": is_meter,
            "is_bulk": is_bulk,
            "is_bez_3m": is_bez_3m,
            "power_w_m": pwm,
            "total_power": total_w,
            "rec_psu": rec_psu,
            "pcb_oz": pcb,
            "warranty": warranty,
            "cri": cri,
            "color_name": color_name
        }
    }

# ==============================================================================
# 2. ZASILACZE LED (124 PRODUKTY)
# ==============================================================================
def process_zasilacz(p):
    name = p["name"]
    code = p["code"]
    ean = p.get("ean", "BRAK")
    price = p.get("price", "0.00")
    stock = p.get("stock", "0")
    cat = p.get("cat", "Zasilacze")
    subcat = p.get("subcat", "Zasilacze LED")
    info = p.get("parsed_info", {})

    n_lower = name.lower()
    c_lower = (code + " " + cat).lower()

    is_prmad = info.get("is_prmad") or "mad" in n_lower or "auto" in n_lower or "mad" in c_lower or "pr-mad" in c_lower
    is_scharfer = info.get("is_scharfer") or "scharfer" in n_lower or "schärfer" in n_lower or "sch-" in c_lower or "sch" in code.lower()

    # Napięcie
    if is_prmad:
        volt = "Smart Auto 12V/24V"
    elif "24V" in name or "24V" in code:
        volt = "24V DC"
    elif "12V" in name or "12V" in code:
        volt = "12V DC"
    elif "48V" in name:
        volt = "48V DC"
    else:
        volt = info.get("voltage", "12V DC")

    # Moc W
    power_w = info.get("power_w", 60)
    m_p = re.search(r'(\d+)\s*W\b', name)
    if m_p: power_w = int(m_p.group(1))

    # Typ i marka
    if is_prmad:
        brand = "Prescot PR-MAD"
        series_name = "Smart Auto 12V/24V"
        ip = "IP20 (Semi-Potted)"
        warranty = 5
        housing = "Ultra-Slim (wysokość tylko 29 mm)"
        uniqueness = (
            "Rewolucyjny mikroprocesor Smart Auto-Identify automatycznie rozpoznaje, czy podłączono taśmę 12V czy 24V, "
            "samoczynnie ustawiając właściwe napięcie — całkowicie eliminuje to błędy montażowe i ryzyko spalenia taśmy na budowie. "
            "Konstrukcja Ultra-Slim (zaledwie 29 mm wysokości) z zalewem termoprzewodzącym Semi-Potted gwarantuje bezgłośną pracę (zero piszczenia cewek) i ochronę przed wilgocią."
        )
        places = "płytkich sufitów podwieszanych w salonie i sypialni (całkowita cisza), wąskich profili meblowych, przestrzeni nad szafkami kuchennymi oraz instalacji mieszanych 12V i 24V"
        faq_q1 = "Czy muszę ręcznie przełączać napięcie między 12V a 24V?"
        faq_a1 = "Nie. Zasilacz PR-MAD ma inteligentny mikroprocesor, który po włączeniu sam mierzy obciążenie i automatycznie ustawia właściwe napięcie 12V lub 24V DC."
    elif is_scharfer:
        brand = "Schärfer"
        series_name = "Hermetic Pro IP67"
        ip = "IP67"
        warranty = 7
        housing = "Hermetyczna aluminiowa (IP67)"
        uniqueness = (
            "Najwyższej klasy zasilacz hermetyczny Schärfer objęty aż 7-letnią gwarancją. "
            "Elektronika w 100% zalana masą uszczelniającą w aluminiowej obudowie radiatorowej (IP67), co zapewnia odporność na wodę, pył, mróz oraz zmienne warunki atmosferyczne. "
            "Wysoka sprawność energetyczna (>90%) i bezawaryjna praca ciągła w najbardziej wymagających środowiskach."
        )
        places = "łazienek, kabin prysznicowych, podbitki dachowej, elewacji zewnętrznych, ogrodów oraz wilgotnych piwnic i garaży"
        faq_q1 = "Czy zasilacz Schärfer może pracować bezpośrednio na zewnątrz?"
        faq_a1 = "Tak, klasa szczelności IP67 i pełny zalew hermetyczny gwarantują całkowitą odporność na deszcz, śnieg i mróz."
    elif "din" in n_lower or "szyn" in c_lower or "hdr" in n_lower or "edr" in n_lower or "ndr" in n_lower:
        brand = "Mean Well" if any(k in n_lower for k in ("hdr", "edr", "ndr")) else "Prescot"
        series_name = "Szyna DIN"
        ip = "IP20"
        warranty = 3
        housing = "Modułowa na szynę DIN (TS-35)"
        uniqueness = "Wygodny montaż w standardowych rozdzielnicach elektrycznych na szynę DIN TS-35. Bezpieczna integracja z domową instalacją elektryczną i automatyką budynkową."
        places = "rozdzielnic elektrycznych w domach jednorodzinnych, mieszkaniach, szafach automatyki oraz tablicach bezpiecznikowych"
        faq_q1 = "Jak montuje się ten zasilacz?"
        faq_a1 = "Zasilacz zatrzaskuje się bezpośrednio na standardowej szynie DIN TS-35/7.5 lub 15 w rozdzielnicy elektrycznej."
    elif "puszk" in n_lower or "dopuszkow" in n_lower or "fi60" in n_lower:
        brand = "Prescot"
        series_name = "Dopuszkowy Mini"
        ip = "IP67"
        warranty = 3
        housing = "Okrągła do puszki fi 60 mm"
        uniqueness = "Kompaktowa, miniaturowa konstrukcja dopasowana do standardowych puszek elektroinstalacyjnych fi 60 mm (np. pod włącznikiem lub gniazdkiem). Szczelność IP67."
        places = "puszek podtynkowych fi 60 mm za tradycyjnymi włącznikami światła, luster łazienkowych oraz małych wnęk meblowych"
        faq_q1 = "Czy zasilacz zmieści się w standardowej puszce fi 60?"
        faq_a1 = "Tak, jego średnica i wysokość zostały precyzyjnie zaprojektowane do montażu w głębokich puszkach podtynkowych fi 60 mm."
    else:
        brand = "Prescot"
        series_name = "Ultra Slim"
        ip = "IP20"
        warranty = 3
        housing = "Ultra-Slim płaska meblowa"
        uniqueness = "Płaski profil obudowy Slim pozwala na dyskretne ukrycie zasilacza w miejscach niedostępnych dla tradycyjnych, grubych transformatorów modułowych."
        places = "zabudów meblowych, cokołów kuchennych, wąskich przestrzeni za szafami oraz sufitów podwieszanych"
        faq_q1 = "Czy zasilacz wymaga wentylatora?"
        faq_a1 = "Nie, zasilacz chłodzi się całkowicie pasywnie dzięki perforowanej aluminiowej obudowie, pracując w 100% bezgłośnie."

    cont_power = round(power_w * 0.8, 1)

    # TIM Description
    tim_w1 = f"Zasilacz impulsowy {name} to profesjonalne, stabilizowane źródło zasilania LED marki {brand} ({series_name}) o mocy znamionowej {power_w} W i napięciu wyjściowym {volt}."
    tim_w2 = f"Zastosowanie: idealnie sprawdza się do zasilania taśm LED, opraw meblowych i modułów oświetleniowych w {places}."
    
    zasady_doboru = (
        f"Zasady doboru mocy i bezpieczeństwa:\n"
        f"• Moc znamionowa zasilacza wynosi {power_w} W. Zgodnie z normami elektrotechnicznymi należy zachować minimum 20% rezerwy mocy (rekomendowane ciągłe obciążenie do {cont_power} W).\n"
        f"• Bezpieczeństwo instalacji: układ wyposażony jest w automatyczne zabezpieczenia przeciwzwarciowe (SCP), przeciążeniowe (OLP) oraz termiczne (OTP).\n"
        f"• Współpraca ze sterownikami: zasilacz w pełni współpracuje ze ściemniaczami i sterownikami LED (radiowymi MiBoxer, ściennymi oraz systemami smart home Tuya/Dali)."
    )

    faq_items = [
        (faq_q1, faq_a1),
        ("Ile taśmy LED mogę podłączyć do tego zasilacza?", f"Przy zachowaniu 20% rezerwy mocy (moc robocza {cont_power} W) możesz podłączyć np. do {round(cont_power/4.8, 1)} m taśmy 4.8 W/m lub do {round(cont_power/9.6, 1)} m taśmy 9.6 W/m."),
        ("Co się stanie w przypadku zwarcia na taśmie LED?", "Zasilacz odetnie napięcie wyjściowe dzięki zabezpieczeniu przeciwzwarciowemu (SCP) i powróci do normalnej pracy automatycznie po usunięciu usterki.")
    ]
    tim_faq = "Najczęściej zadawane pytania (FAQ):\n" + "\n".join([f"P: {q}\nO: {a}" for q, a in faq_items])
    tim_full = f"{tim_w1}\n\n{tim_w2}\n\n{zasady_doboru}\n\n{tim_faq}"

    # Amazon Description
    amz_title = f"{brand} {series_name} Zasilacz LED {power_w}W {volt} {housing} ({ip}, {warranty} Lat Gwarancji)"
    amz_bullets = [
        f"• CO TO JEST: {tim_w1}",
        f"• GDZIE ZAMONTUJESZ: {places.capitalize()}.",
        f"• UNIKALNOŚĆ & PRZEWAGA: {uniqueness}",
        f"• BEZPIECZEŃSTWO I MOC: Moc znamionowa {power_w} W (ciągłe obciążenie robocze z 20% rezerwą to {cont_power} W). Pełny pakiet zabezpieczeń zwarciowych i przeciążeniowych. {warranty} lat gwarancji.",
        f"• SZYBKIE FAQ: P: {faq_q1} O: {faq_a1}"
    ]
    amz_full = f"{amz_title}\n\n" + "\n\n".join(amz_bullets)

    return {
        "id": p["id"],
        "name": name,
        "code": code,
        "ean": ean,
        "cat": cat,
        "subcat": subcat,
        "price": price,
        "stock": stock,
        "description": {
            "title": amz_title,
            "intro": tim_w1,
            "gdzie": f"Gdzie użyć i montaż\n\n{tim_w2}",
            "z_czym": f"Z czym użyć i dobór mocy\n\n{zasady_doboru}",
            "faq": faq_items,
            "full_text": tim_full,
            "amazon_title": amz_title,
            "amazon_bullets": amz_bullets,
            "amazon_full": amz_full
        },
        "parsed_info": {
            "brand": brand,
            "series": series_name,
            "voltage": volt,
            "power_w": power_w,
            "ip": ip,
            "warranty": warranty,
            "is_prmad": is_prmad,
            "is_scharfer": is_scharfer
        }
    }

# ==============================================================================
# 3. AKCESORIA MONTAŻOWE (86 PRODUKTÓW)
# ==============================================================================
def process_akcesorium(p):
    name = p["name"]
    code = p["code"]
    ean = p.get("ean", "BRAK")
    price = p.get("price", "0.00")
    stock = p.get("stock", "0")
    cat = p.get("cat", "Akcesoria")
    subcat = p.get("subcat", "Akcesoria montażowe")
    info = p.get("parsed_info", {})

    n_lower = name.lower()
    c_lower = code.lower()

    if "rozdzielacz" in n_lower or "rm-" in c_lower:
        item_type = "rozdzielacz"
        title_type = "Rozdzielacz mocy LED"
        w1 = f"Rozdzielacz instalacyjny LED {name} to modułowe złącze dystrybucyjne, które umożliwia szybkie i estetyczne rozgałęzienie pojedynczej linii zasilającej na wiele niezależnych odcinków taśmy LED."
        uniqueness = "Eliminuje plątaninę przewodów i niewygodne kostki śrubowe — pozwala na czyste, centralne zasilenie kilku linii oświetleniowych z jednego wspólnego zasilacza LED."
        places = "szaf rozdzielczych, centralnych punktów zasilania w garderobach, pod szafkami kuchennymi oraz w wielostrefowych sufitach podwieszanych"
        step_inst = "Podłącz przewód wychodzący z zasilacza do portu wejściowego rozdzielacza, a poszczególne linie taśm LED wepnij w porty wyjściowe. Zwróć uwagę na sumaryczną moc obciążenia."
        faq_q = "Czy rozdzielacz wymaga lutowania?"
        faq_a = "Nie, rozdzielacz wyposażony jest w szybkie gniazda wtykowe lub zaciski, co pozwala na montaż w kilka sekund bez lutownicy."
    elif "włącznik" in n_lower or "wylacznik" in n_lower or "ściemniacz" in n_lower:
        item_type = "sterowanie"
        title_type = "Włącznik / Ściemniacz meblowy LED"
        w1 = f"Dedykowany włącznik meblowy LED {name} to miniaturowy kontroler instalowany bezpośrednio w profilu aluminiowym lub płycie meblowej, umożliwiający wygodne włączanie i płynne ściemnianie światła."
        uniqueness = "Dyskretny montaż wewnątrz profilu aluminiowego pod kloszem lub w wieńcu szafki — reaguje na dotyk, zbliżenie dłoni lub otwarcie frontu meblowego."
        places = "mebli kuchennych, szaf przesuwnych, garderób, biurek oraz podświetlenia łóżek i szafek nocnych"
        step_inst = "Wlutuj lub wepnij włącznik pomiędzy zasilacz (wejście 12V/24V) a taśmę LED (wyjście). Umieść czujnik w miejscu łatwo dostępnym dla użytkownika."
        faq_q = "Czy włącznik zapamiętuje ostatni poziom jasności?"
        faq_a = "Większość modeli włączników dotykowych Prescot posiada pamięć ostatniego stanu po zaniku zasilania."
    elif "przewód" in n_lower or "kabel" in n_lower:
        item_type = "przewod"
        title_type = "Przewód instalacyjny LED miedziany"
        w1 = f"Profesjonalny przewód instalacyjny LED {name} wykonany w 100% z czystej miedzi beztlenowej (OFC), przeznaczony do bezpiecznego łączenia taśm LED z zasilaczami i sterownikami."
        uniqueness = "Prawdziwe żyły miedziane o niskiej rezystancji gwarantują minimalne spadki napięcia i brak nagrzewania się kabla nawet przy dużych prądach obciążenia."
        places = "prowadzenia linii zasilających w ścianach, sufitach podwieszanych, cokołach meblowych oraz w korytkach instalacyjnych"
        step_inst = "Dobierz przekrój żyły (np. 0.50, 0.75 lub 1.50 mm²) proporcjonalnie do długości trasy kablowej i pobieranego prądu, aby zminimalizować spadek napięcia."
        faq_q = "Jak dobrać przekrój przewodu do LED?"
        faq_a = "Dla odcinków do 5m i mocy do 50W wystarczy 0.75 mm². Przy trasach powyżej 5m lub mocach powyżej 100W wybierz przekrój 1.50 mm²."
    elif "uszczelniacz" in n_lower or "klej" in n_lower or "silikon" in n_lower:
        item_type = "uszczelniacz"
        title_type = "Silikon neutralny / Uszczelniacz do taśm LED"
        w1 = f"Specjalistyczny uszczelniacz montażowy {name} na bazie neutralnego silikonu, przeznaczony do zabezpieczania miejsc cięcia taśm LED IP67/IP68 oraz klejenia profili."
        uniqueness = "Neutralny chemicznie utwardzacz — nie wchodzi w reakcję z luminoforem diod LED ani ścieżkami miedzianymi PCB (zwykły silikon octowy niszczy taśmy LED!)."
        places = "uszczelniania końcówek taśm hermetycznych w łazienkach, basenach, na elewacjach oraz podbitkach dachowych"
        step_inst = "Nałóż niewielką ilość silikonu na końcówkę taśmy i zaślepkę profilu, a następnie załóż osłonkę. Pozostaw do utwardzenia na 12-24 godziny."
        faq_q = "Dlaczego do LED nie wolno stosować zwykłego silikonu sanitarnego?"
        faq_a = "Zwykły silikon sanitarny zawiera kwas octowy, który wchodzi w reakcję chemiczną ze ścieżkami miedzi i diodami, powodując ich czernienie i zniszczenie w ciągu kilku tygodni."
    else:
        item_type = "zlaczka"
        title_type = "Szybkozłączka bez lutowania LED Hippo"
        w1 = f"Innowacyjna szybkozłączka zaciskowa LED {name} umożliwia błyskawiczne, pewne połączenie odcinków taśmy LED lub doprowadzenie zasilania całkowicie bez użycia lutownicy."
        uniqueness = "Hartowane styki nożowe precyzyjnie przebijają się przez laminat miedziany PCB, zapewniając trwałe połączenie o znikomej rezystancji. Skraca czas montażu o 70%!"
        places = "narożników meblowych 90°, łączenia odcinków w długie linie, omijania przeszkód w profilu oraz szybkiego serwisu bez rozgrzewania lutownicy"
        step_inst = "Wsuń odcięty odcinek taśmy w szczelinę złączki, dopasuj piny do pól lutowniczych i zaciśnij klapkę dociskową kombinerkami do wyraźnego zatrzaśnięcia."
        faq_q = "Czy połączenie złączką zaciskową jest tak samo trwałe jak lutowanie?"
        faq_a = "Tak, opatentowany docisk nożowy w złączkach Hippo gwarantuje odporność na wstrząsy, drgania i utlenianie styków porównywalną z połączeniem lutowanym."

    # TIM Description
    tim_w1 = w1
    tim_w2 = f"Zastosowanie: niezastąpiony element podczas montażu oświetlenia LED w {places}."
    tim_w3 = (
        f"Instrukcja montażu i wskazówki techniczne:\n"
        f"• {step_inst}\n"
        f"• Zgodność: akcesorium w pełni kompatybilne z systemami taśm i profili aluminiowych Prescot.\n"
        f"• Jakość: produkt objęty 2-letnią gwarancją."
    )
    faq_items = [
        (faq_q, faq_a),
        ("Czy to akcesorium pasuje do profili aluminiowych?", "Kompaktowe wymiary zostały zoptymalizowane tak, aby element bez trudu mieścił się w standardowych profilach nawierzchniowych i wpuszczanych."),
        ("Z jakimi napięciami współpracuje?", "Element jest przystosowany do bezpiecznych instalacji niskonapięciowych 12V oraz 24V DC.")
    ]
    tim_faq = "Najczęściej zadawane pytania (FAQ):\n" + "\n".join([f"P: {q}\nO: {a}" for q, a in faq_items])
    tim_full = f"{tim_w1}\n\n{tim_w2}\n\n{tim_w3}\n\n{tim_faq}"

    # Amazon Description
    amz_title = f"{title_type} — {name} (Prescot LED Accessories)"
    amz_bullets = [
        f"• CO TO JEST: {tim_w1}",
        f"• GDZIE ZASTOSUJESZ: {places.capitalize()}.",
        f"• UNIKALNOŚĆ & ZALETY: {uniqueness}",
        f"• PROSTY MONTAŻ: {step_inst}",
        f"• SZYBKIE FAQ: P: {faq_q} O: {faq_a}"
    ]
    amz_full = f"{amz_title}\n\n" + "\n\n".join(amz_bullets)

    return {
        "id": p["id"],
        "name": name,
        "code": code,
        "ean": ean,
        "cat": cat,
        "subcat": subcat,
        "price": price,
        "stock": stock,
        "description": {
            "title": amz_title,
            "intro": tim_w1,
            "gdzie": f"Gdzie użyć i funkcja w instalacji\n\n{tim_w2}",
            "z_czym": f"Z czym użyć i wskazówki montażowe\n\n{tim_w3}",
            "faq": faq_items,
            "full_text": tim_full,
            "amazon_title": amz_title,
            "amazon_bullets": amz_bullets,
            "amazon_full": amz_full
        },
        "parsed_info": {
            "item_type": item_type,
            "title_type": title_type
        }
    }

# ==============================================================================
# 4. MASTER HTML PORTAL BUILDER (Z NOWĄ ZAKŁADKĄ AMAZON)
# ==============================================================================
def render_product_card(i, p, cat_type):
    d = p["description"]
    info = p.get("parsed_info", {})
    name = p["name"]
    code = p["code"]
    ean = p["ean"]
    price = p.get("price", "0.00")
    subcat = p.get("subcat", "")

    badges = []
    card_highlight = ""

    if cat_type == "tasmy":
        if info.get("series") == "Delux":
            badges.append('<span class="badge badge-flag-delux">👑 DELUX 7 LAT GWARANCJI</span>')
            card_highlight = "card-highlight-delux"
        elif info.get("series") == "COB":
            badges.append('<span class="badge badge-flag-cob">✨ COB DOTLESS</span>')
        badges.append(f'<span class="badge badge-volt">{esc(info.get("voltage","24V"))}</span>')
        badges.append(f'<span class="badge badge-width">{esc(info.get("width","8 mm"))}</span>')
        badges.append(f'<span class="badge badge-power">{esc(str(info.get("power_w_m",4.8)))} W/m</span>')
        if info.get("is_bulk"):
            badges.append(f'<span class="badge badge-len">📏 Szpula {info.get("length_m")}m</span>')
        elif info.get("is_meter"):
            badges.append('<span class="badge badge-len">📏 Na metry</span>')
        else:
            badges.append(f'<span class="badge badge-len">📏 Rolka {info.get("length_m")}m</span>')
        badges.append(f'<span class="badge badge-war">🛡️ {info.get("warranty",2)} lat</span>')
        badges.append(f'<span class="badge badge-pcb">Cu {info.get("pcb_oz","2oz")}</span>')
        badges.append(f'<span class="badge badge-ip">{esc(info.get("ip","IP20"))}</span>')
    elif cat_type == "zasilacze":
        if info.get("is_prmad"):
            badges.append('<span class="badge badge-flag-prmad">⭐ FLAGOWY SMART AUTO 12V/24V</span>')
            card_highlight = "card-highlight-prmad"
        elif info.get("is_scharfer"):
            badges.append('<span class="badge badge-flag-sch">🏆 SCHÄRFER 7Y HERMETIC IP67</span>')
            card_highlight = "card-highlight-sch"
        badges.append(f'<span class="badge badge-volt">{esc(info.get("voltage","12V"))}</span>')
        badges.append(f'<span class="badge badge-power">{esc(str(info.get("power_w",60)))} W</span>')
        badges.append(f'<span class="badge badge-ip">{esc(info.get("ip","IP20"))}</span>')
        badges.append(f'<span class="badge badge-war">🛡️ {info.get("warranty",3)} lat</span>')
    else:
        badges.append(f'<span class="badge badge-brand">{esc(info.get("title_type","Akcesoria"))}</span>')

    # Card Body with TIM vs AMAZON toggle
    amazon_bullets_html = "".join([f'<li style="margin-bottom:8px; line-height:1.6;">{esc(b)}</li>' for b in d["amazon_bullets"]])

    faq_html = ""
    if d.get("faq"):
        faq_items_html = "".join([
            f'<div style="background:rgba(255,255,255,0.03); border:1px solid var(--border); border-radius:8px; padding:10px 14px; margin-bottom:8px;">'
            f'<strong style="color:var(--amber); font-size:13px; display:block; margin-bottom:4px;">P: {esc(q)}</strong>'
            f'<p style="margin:0; font-size:13px; color:#cbd5e1;">O: {esc(a)}</p>'
            f'</div>'
            for q, a in d["faq"]
        ])
        faq_html = f'<div class="desc-block"><div class="section-title">FAQ — NAJCZĘSTSZE PYTANIA KLIENTÓW</div>{faq_items_html}</div>'

    card_id = f"card-{cat_type}-{i}"

    return f'''
<article class="product-card {card_highlight}" id="{card_id}" data-category="{cat_type}" data-subcat="{esc(subcat)}">
  <div class="card-header">
    <div class="card-top-row">
      <span class="card-num">#{cat_type.upper()}-{i}</span>
      <div class="badges-row">{"".join(badges)}</div>
    </div>
    <h3 class="card-name">{esc(name)}</h3>
    <div class="card-meta">
      <span class="meta-code">Kod: {esc(code)}</span>
      <span class="meta-ean">EAN: {esc(ean)}</span>
      <span class="meta-subcat">Kategoria: {esc(subcat)}</span>
      <span class="meta-price">{esc(price)} PLN</span>
    </div>
  </div>

  <!-- VIEW SWITCHER (TIM VS AMAZON) -->
  <div class="card-view-switcher">
    <button type="button" class="view-btn active" onclick="toggleCardView('{card_id}', 'tim', this)">📑 Pełny opis TIM / B2B</button>
    <button type="button" class="view-btn" onclick="toggleCardView('{card_id}', 'amazon', this)">🛒 Format Amazon (Krótki &amp; Unikalny)</button>
  </div>

  <!-- TIM VIEW -->
  <div class="card-body view-tim">
    <div class="desc-block intro">
      <div class="section-title">WARSTWA 1: CO TO JEST?</div>
      <p>{esc(d["intro"])}</p>
    </div>
    <div class="desc-block">
      <div class="section-title">WARSTWA 2: ZASTOSOWANIE I MIEJSCE MONTAŻU</div>
      <p>{esc(d.get("barwa", d.get("gdzie","")))}</p>
    </div>
    <div class="desc-block">
      <div class="section-title">WARSTWA 3: MONTAŻ I DOBÓR ZASILACZA</div>
      <p>{esc(d.get("dobor", d.get("z_czym","")))}</p>
    </div>
    {faq_html}
  </div>

  <!-- AMAZON VIEW -->
  <div class="card-body view-amazon" style="display:none;">
    <div class="desc-block" style="background:rgba(233,75,37,0.05); border-color:rgba(233,75,37,0.2);">
      <div class="section-title" style="color:#fbbf24;">TYTUŁ LISTINGU AMAZON / E-COMMERCE</div>
      <p style="font-weight:700; color:#ffffff; font-size:15px; margin-bottom:12px;">{esc(d["amazon_title"])}</p>
      <div class="section-title" style="color:var(--accent); margin-top:14px;">KLUCZOWE PUNKTY (BULLET POINTS):</div>
      <ul style="padding-left:18px; color:#e2e8f0; font-size:13.5px;">
        {amazon_bullets_html}
      </ul>
    </div>
  </div>

  <div class="card-actions">
    <button class="btn-copy" onclick="copyCardDesc('{card_id}', 'tim', this)">📋 Kopiuj opis TIM (Plain Text)</button>
    <button class="btn-copy btn-copy-amz" onclick="copyCardDesc('{card_id}', 'amazon', this)">🛒 Kopiuj format Amazon</button>
    <!-- Ukryte źródła tekstu do kopiowania -->
    <textarea class="raw-tim-text" style="display:none;">{esc(d["full_text"])}</textarea>
    <textarea class="raw-amz-text" style="display:none;">{esc(d["amazon_full"])}</textarea>
  </div>
</article>'''

def build_full_portal(tapes, zasilacze, akcesoria):
    total = len(tapes) + len(zasilacze) + len(akcesoria)

    # Sort tapes: Delux 7Y and COB at top
    tapes_sorted = sorted(tapes, key=lambda p: (
        0 if p.get("parsed_info",{}).get("series") == "Delux" else (
            1 if p.get("parsed_info",{}).get("series") == "COB" else 2
        ),
        p["name"]
    ))

    # Sort zasilacze: PR-MAD first, then Schärfer, then others
    zas_sorted = sorted(zasilacze, key=lambda p: (
        0 if p.get("parsed_info",{}).get("is_prmad") else (
            1 if p.get("parsed_info",{}).get("is_scharfer") else 2
        ),
        p["name"]
    ))

    # Sort akcesoria: Hippo złączki, Rozdzielacze, Włączniki, Przewody
    akc_sorted = sorted(akcesoria, key=lambda p: (
        0 if "hippo" in p["name"].lower() or "szybkozłączka" in p["name"].lower() else (
            1 if "rozdzielacz" in p["name"].lower() else 2
        ),
        p["name"]
    ))

    all_prods = tapes_sorted + zas_sorted + akc_sorted

    tapes_cards = [render_product_card(i+1, p, "tasmy") for i, p in enumerate(tapes_sorted)]
    zas_cards = [render_product_card(i+1, p, "zasilacze") for i, p in enumerate(zas_sorted)]
    akc_cards = [render_product_card(i+1, p, "akcesoria") for i, p in enumerate(akc_sorted)]
    amazon_cards = [render_product_card(i+1, p, "amazon") for i, p in enumerate(all_prods)]

    html_page = f'''<!DOCTYPE html>
<html lang="pl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Prescot TIM &amp; Amazon — Baza Opisów Produktów ({total})</title>
<style>
*,*::before,*::after{{box-sizing:border-box}}
:root{{
  --bg:#090b10;--surface:#131620;--surface-hover:#1a1e2c;--border:#242838;
  --text:#e4e6eb;--text-dim:#949ba8;--accent:#e94b25;--accent-hover:#d63c18;
  --green:#22c55e;--blue:#3b82f6;--purple:#a855f7;--amber:#f59e0b;--cyan:#06b6d4;--gold:#fbbf24;
  --font:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;
}}
body{{margin:0;font-family:var(--font);background:var(--bg);color:var(--text);line-height:1.6}}
.wrap{{max-width:1160px;margin:0 auto;padding:24px 20px 100px}}

header{{text-align:center;padding:32px 0 20px;border-bottom:1px solid var(--border)}}
header h1{{font-size:32px;margin:0 0 8px;color:var(--accent);letter-spacing:-0.5px}}
header p{{margin:0;color:var(--text-dim);font-size:15px}}

/* Navigation Tabs */
.nav-tabs{{display:flex;gap:10px;justify-content:center;margin:24px 0 16px;flex-wrap:wrap}}
.tab-btn{{
  background:var(--surface);border:1px solid var(--border);border-radius:12px;
  padding:12px 22px;color:var(--text);font-size:15px;font-weight:700;cursor:pointer;
  display:inline-flex;align-items:center;gap:10px;transition:all .2s;
}}
.tab-btn:hover{{border-color:var(--accent);background:var(--surface-hover)}}
.tab-btn.active{{background:var(--accent);border-color:var(--accent);color:#fff;box-shadow:0 4px 16px rgba(233,75,37,0.35)}}
.tab-btn.tab-amz.active{{background:linear-gradient(135deg, #f59e0b, #d97706); border-color:#f59e0b;}}
.tab-count{{background:rgba(0,0,0,0.25);padding:2px 8px;border-radius:999px;font-size:12px;font-weight:800}}

.stats{{display:flex;gap:14px;justify-content:center;margin:20px 0 24px;flex-wrap:wrap}}
.stat{{background:var(--surface);border:1px solid var(--border);border-radius:12px;padding:10px 20px;text-align:center;min-width:130px}}
.stat-num{{font-size:24px;font-weight:800;color:var(--accent)}}
.stat-label{{font-size:11px;color:var(--text-dim);text-transform:uppercase;letter-spacing:1px;font-weight:600}}

/* Search bar */
.search-box{{
  position:sticky;top:14px;z-index:100;padding:12px 0;
  background:rgba(9,11,16,0.92);backdrop-filter:blur(14px);-webkit-backdrop-filter:blur(14px);
  margin-bottom:24px;
}}
.search-box input{{
  width:100%;padding:14px 22px;font-size:15px;border:1px solid var(--border);
  border-radius:14px;background:var(--surface);color:var(--text);
  outline:none;transition:border-color .2s,box-shadow .2s;
}}
.search-box input:focus{{border-color:var(--accent);box-shadow:0 0 0 3px rgba(233,75,37,0.25)}}
.search-box input::placeholder{{color:var(--text-dim)}}

/* Product Cards */
.tab-content{{display:none}}
.tab-content.active{{display:block}}

.product-card{{
  background:var(--surface);border:1px solid var(--border);border-radius:16px;
  margin:0 0 24px;overflow:hidden;transition:border-color .2s,background .2s;
}}
.product-card:hover{{border-color:#383e54}}

/* Flagship Highlights */
.card-highlight-prmad{{
  border:2px solid #f59e0b !important;
  background:linear-gradient(180deg, rgba(245,158,11,0.06) 0%, var(--surface) 100%);
  box-shadow:0 4px 20px rgba(245,158,11,0.12);
}}
.card-highlight-sch{{
  border:2px solid #06b6d4 !important;
  background:linear-gradient(180deg, rgba(6,182,212,0.06) 0%, var(--surface) 100%);
  box-shadow:0 4px 20px rgba(6,182,212,0.12);
}}
.card-highlight-delux{{
  border:2px solid #a855f7 !important;
  background:linear-gradient(180deg, rgba(168,85,247,0.06) 0%, var(--surface) 100%);
  box-shadow:0 4px 20px rgba(168,85,247,0.12);
}}

.card-header{{padding:18px 22px 14px;border-bottom:1px solid var(--border)}}
.card-top-row{{display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;flex-wrap:wrap;gap:8px}}
.card-num{{color:var(--accent);font-weight:800;font-size:14px}}

.badges-row{{display:flex;gap:6px;flex-wrap:wrap}}
.badge{{
  font-size:11px;font-weight:600;padding:3px 8px;border-radius:6px;
  background:#1e2333;color:var(--text-dim);letter-spacing:0.3px;
}}
.badge-volt{{background:rgba(59,130,246,0.15);color:#60a5fa;border:1px solid rgba(59,130,246,0.3)}}
.badge-width{{background:rgba(168,85,247,0.15);color:#c084fc;border:1px solid rgba(168,85,247,0.3)}}
.badge-power{{background:rgba(245,158,11,0.15);color:#fbbf24;border:1px solid rgba(245,158,11,0.3)}}
.badge-len{{background:#1e293b;color:#38bdf8;border:1px solid #475569}}
.badge-pcb{{background:rgba(244,63,94,0.15);color:#fb7185;border:1px solid rgba(244,63,94,0.3)}}
.badge-war{{background:rgba(233,75,37,0.15);color:#f87171;border:1px solid rgba(233,75,37,0.3)}}
.badge-ip{{background:rgba(14,165,233,0.15);color:#38bdf8;border:1px solid rgba(14,165,233,0.3)}}
.badge-brand{{background:rgba(6,182,212,0.15);color:#22d3ee;border:1px solid rgba(6,182,212,0.3);font-weight:700}}

.badge-flag-prmad{{background:linear-gradient(135deg, #f59e0b, #d97706);color:#000;font-weight:800;border:none;box-shadow:0 2px 8px rgba(245,158,11,0.4)}}
.badge-flag-sch{{background:linear-gradient(135deg, #06b6d4, #0891b2);color:#000;font-weight:800;border:none;box-shadow:0 2px 8px rgba(6,182,212,0.4)}}
.badge-flag-delux{{background:linear-gradient(135deg, #a855f7, #7e22ce);color:#fff;font-weight:800;border:none;box-shadow:0 2px 8px rgba(168,85,247,0.4)}}
.badge-flag-cob{{background:linear-gradient(135deg, #10b981, #059669);color:#000;font-weight:800;border:none;}}

.card-name{{margin:0 0 10px;font-size:16px;font-weight:700;line-height:1.45;color:#fff}}
.card-meta{{display:flex;gap:14px;font-size:12px;color:var(--text-dim);flex-wrap:wrap}}
.meta-code,.meta-ean{{background:#0b0d13;padding:2px 8px;border-radius:4px;font-family:ui-monospace,SFMono-Regular,Menlo,monospace}}
.meta-subcat{{color:#949ba8}}
.meta-price{{color:var(--accent);font-weight:700;margin-left:auto}}

/* Card view switcher */
.card-view-switcher{{
  display:flex;gap:8px;padding:10px 22px;background:#0d0f17;border-bottom:1px solid var(--border);
}}
.view-btn{{
  background:transparent;border:1px solid var(--border);border-radius:6px;padding:6px 14px;
  color:var(--text-dim);font-size:12.5px;font-weight:700;cursor:pointer;transition:all .15s;
}}
.view-btn:hover{{color:#fff;border-color:var(--accent)}}
.view-btn.active{{background:var(--accent);color:#fff;border-color:var(--accent)}}

.card-body{{padding:20px 22px}}
.desc-block{{margin:0 0 16px}}
.desc-block:last-child{{margin-bottom:0}}
.section-title{{font-size:11px;font-weight:800;letter-spacing:1px;color:var(--accent);margin-bottom:6px}}
.desc-block p{{margin:0;font-size:14px;color:#d1d5db;line-height:1.65;white-space:pre-line}}
.desc-block.intro p{{font-size:14.5px;color:#f3f4f6;font-weight:500}}

.card-actions{{padding:0 22px 18px;display:flex;gap:10px;flex-wrap:wrap}}
.btn-copy{{
  background:var(--accent);color:#fff;border:none;border-radius:8px;
  padding:9px 16px;font-size:13px;font-weight:700;cursor:pointer;
  transition:all .15s;display:inline-flex;align-items:center;gap:6px;
}}
.btn-copy:hover{{background:var(--accent-hover);transform:translateY(-1px)}}
.btn-copy.copied{{background:var(--green)}}

.btn-copy-amz{{
  background:#1e2333;color:#fbbf24;border:1px solid rgba(251,191,36,0.4);
}}
.btn-copy-amz:hover{{background:rgba(251,191,36,0.15);border-color:#fbbf24}}
</style>
</head>
<body>
<div class="wrap">
  <header>
    <h1>🏷️ Prescot TIM &amp; Amazon — Kompletna Baza Opisów</h1>
    <p>Standard SEO &amp; E-commerce zgodny z wytycznymi elektrotechnicznymi • 3 Warstwy, Unikalność, Montaż i FAQ</p>
  </header>

  <div class="stats">
    <div class="stat"><div class="stat-num">{len(tapes)}</div><div class="stat-label">Taśm LED (Delux 7Y TOP)</div></div>
    <div class="stat"><div class="stat-num">{len(zasilacze)}</div><div class="stat-label">Zasilaczy (PR-MAD &amp; Schärfer TOP)</div></div>
    <div class="stat"><div class="stat-num">{len(akcesoria)}</div><div class="stat-label">Akcesoriów LED</div></div>
    <div class="stat"><div class="stat-num" style="color:#fbbf24;">{total}</div><div class="stat-label">Formatów Amazon</div></div>
  </div>

  <nav class="nav-tabs">
    <button class="tab-btn active" onclick="switchTab('tasmy', this)">
      🌟 Taśmy LED <span class="tab-count">{len(tapes)}</span>
    </button>
    <button class="tab-btn" onclick="switchTab('zasilacze', this)">
      ⚡ Zasilacze LED <span class="tab-count">{len(zasilacze)}</span>
    </button>
    <button class="tab-btn" onclick="switchTab('akcesoria', this)">
      🔌 Akcesoria montażowe <span class="tab-count">{len(akcesoria)}</span>
    </button>
    <button class="tab-btn tab-amz" onclick="switchTab('amazon', this)">
      🛒 Format Amazon &amp; Marketplaces <span class="tab-count" style="background:#000; color:#fbbf24;">{total}</span>
    </button>
  </nav>

  <div class="search-box">
    <input type="search" id="search" placeholder="Szukaj po nazwie (np. Schärfer, PR-MAD, Delux, COB), kodzie, EAN, mocy (W), szerokości (mm), barwie..." autocomplete="off">
  </div>

  <main>
    <section id="tab-tasmy" class="tab-content active">
      {"".join(tapes_cards)}
    </section>

    <section id="tab-zasilacze" class="tab-content">
      {"".join(zas_cards)}
    </section>

    <section id="tab-akcesoria" class="tab-content">
      {"".join(akc_cards)}
    </section>

    <section id="tab-amazon" class="tab-content">
      <div style="padding:14px 20px; background:rgba(251,191,36,0.08); border:1px solid rgba(251,191,36,0.3); border-radius:12px; margin-bottom:20px; color:#fbbf24; font-size:14px;">
        💡 <strong>Strefa Amazon &amp; Fast Buy:</strong> Krótkie, punktorowe opisy skupione na definicji (Co to jest), zastosowaniu (Gdzie zamontujesz), unikalności produktu (Dlaczego ten model) oraz instrukcji montażu i doboru. Gotowe do natychmiastowego skopiowania.
      </div>
      {"".join(amazon_cards)}
    </section>
  </main>
</div>

<script>
function switchTab(tabName, btn) {{
  document.querySelectorAll('.nav-tabs .tab-btn').forEach(b => b.classList.remove('active'));
  document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
  btn.classList.add('active');
  document.getElementById('tab-' + tabName).classList.add('active');
  filterProducts();
}}

function toggleCardView(cardId, viewType, btn) {{
  const card = document.getElementById(cardId);
  if (!card) return;
  card.querySelectorAll('.view-btn').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');

  const timView = card.querySelector('.view-tim');
  const amzView = card.querySelector('.view-amazon');

  if (viewType === 'amazon') {{
    if (timView) timView.style.display = 'none';
    if (amzView) amzView.style.display = 'block';
  }} else {{
    if (timView) timView.style.display = 'block';
    if (amzView) amzView.style.display = 'none';
  }}
}}

function copyCardDesc(cardId, format, btn) {{
  const card = document.getElementById(cardId);
  if (!card) return;
  let text = '';
  if (format === 'amazon') {{
    const ta = card.querySelector('.raw-amz-text');
    text = ta ? ta.value : '';
  }} else {{
    const ta = card.querySelector('.raw-tim-text');
    text = ta ? ta.value : '';
  }}

  navigator.clipboard.writeText(text.trim());
  const orig = btn.textContent;
  btn.textContent = '✅ Skopiowano do schowka!';
  btn.classList.add('copied');
  setTimeout(() => {{ btn.textContent = orig; btn.classList.remove('copied'); }}, 1600);
}}

function filterProducts() {{
  const q = document.getElementById('search').value.toLowerCase();
  const activeTab = document.querySelector('.tab-content.active');
  if (!activeTab) return;
  activeTab.querySelectorAll('.product-card').forEach(card => {{
    const text = card.textContent.toLowerCase();
    card.style.display = text.includes(q) ? '' : 'none';
  }});
}}

document.getElementById('search').addEventListener('input', filterProducts);
</script>
</body>
</html>'''
    return html_page


def main():
    print("🚀 Rozpoczynanie generowania opisów TIM & Amazon...")

    # 1. Tapes
    tapes_path = os.path.join(BASE_DIR, "tim_tapes_descriptions.json")
    with open(tapes_path, "r", encoding="utf-8") as f:
        tapes_raw = json.load(f)
    print(f"📦 Przetwarzanie {len(tapes_raw)} taśm LED...")
    tapes_processed = [process_tape(p) for p in tapes_raw]
    with open(tapes_path, "w", encoding="utf-8") as f:
        json.dump(tapes_processed, f, indent=2, ensure_ascii=False)

    # 2. Zasilacze
    zas_path = os.path.join(BASE_DIR, "tim_zasilacze_descriptions.json")
    with open(zas_path, "r", encoding="utf-8") as f:
        zas_raw = json.load(f)
    print(f"⚡ Przetwarzanie {len(zas_raw)} zasilaczy LED...")
    zas_processed = [process_zasilacz(p) for p in zas_raw]
    with open(zas_path, "w", encoding="utf-8") as f:
        json.dump(zas_processed, f, indent=2, ensure_ascii=False)

    # 3. Akcesoria
    akc_path = os.path.join(BASE_DIR, "tim_akcesoria_descriptions.json")
    with open(akc_path, "r", encoding="utf-8") as f:
        akc_raw = json.load(f)
    print(f"🔌 Przetwarzanie {len(akc_raw)} akcesoriów...")
    akc_processed = [process_akcesorium(p) for p in akc_raw]
    with open(akc_path, "w", encoding="utf-8") as f:
        json.dump(akc_processed, f, indent=2, ensure_ascii=False)

    # 4. Generate Portal
    print("🌐 Generowanie master portalu TIM & Amazon...")
    portal_html = build_full_portal(tapes_processed, zas_processed, akc_processed)
    portal_path = os.path.join(BASE_DIR, "index.html")
    with open(portal_path, "w", encoding="utf-8") as f:
        f.write(portal_html)

    print(f"\n✅ SUKCES! Zaktualizowano wszystkie bazy JSON i portal:")
    print(f"   - Portal HTML: {portal_path}")
    print(f"   - Taśmy LED: {len(tapes_processed)}")
    print(f"   - Zasilacze LED: {len(zas_processed)}")
    print(f"   - Akcesoria: {len(akc_processed)}")
    print(f"   - Dedykowana zakładka AMAZON: {len(tapes_processed) + len(zas_processed) + len(akc_processed)} produktów")

if __name__ == "__main__":
    main()
