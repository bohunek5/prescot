# Prescot Master SEO Rules & Copywriting Engine (E-commerce / E-E-A-T / High Conversion)

from __future__ import annotations

import json
import re
from typing import Any


def normalize(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()


def source_specs(product: dict[str, Any]) -> list[tuple[str, str]]:
    source = normalize(product.get("sourceDescription", ""))
    specs: list[tuple[str, str]] = []
    patterns = [
        ("Napięcie zasilania", r"(?:napięcie(?: zasilania)?|zasilanie)\s*[:=-]?\s*(\d+(?:[.,]\d+)?\s*V(?:\s*DC)?)"),
        ("Moc", r"(?:moc|pobór mocy)\s*[:=-]?\s*(\d+(?:[.,]\d+)?\s*W(?:/m)?)"),
        ("Jasność", r"(?:jasność|strumień świetlny)\s*[:=-]?\s*(\d+(?:[.,]\d+)?\s*lm(?:/m)?)"),
        ("Barwa światła", r"(?:barwa(?: światła)?|temperatura barwowa)\s*[:=-]?\s*(\d{4,5}\s*K|ciepła|neutralna|zimna|RGB\+?CCT|RGBW|RGB|CCT)"),
        ("CRI", r"\b(CRI\s*>?\s*\d+|Ra\s*>?\s*\d+)\b"),
        ("Ilość diod", r"(\d+\s*(?:led|diod)(?:/m)?)"),
        ("Moduł cięcia", r"(?:moduł(?:em)? cięcia|cięci[ae] co)\s*(\d+(?:[.,]\d+)?\s*mm)"),
        ("Klasa szczelności", r"\b(IP\s*\d{2})\b"),
        ("Szerokość", r"(?:szerokość(?: laminatu)?)\s*[:=-]?\s*(\d+(?:[.,]\d+)?\s*mm)"),
        ("Długość rolki", r"(?:rolka|długość)\s*[:=-]?\s*(\d+(?:[.,]\d+)?\s*m)\b"),
        ("Typ diody", r"\b((?:SMD|COB)\s*\d{3,4})\b"),
    ]
    for label, pat in patterns:
        m = re.search(pat, source, re.I)
        if m:
            val = normalize(m.group(1) if m.lastindex else m.group(0))
            if val and not any(k.casefold() == label.casefold() for k, _ in specs):
                specs.append((label, val))
    return specs


def attr(product: dict[str, Any], *labels: str) -> str:
    for label in labels:
        val = product.get("attributes", {}).get(label)
        if val:
            return normalize(val)
        for k, v in product.get("attributes", {}).items():
            if k.casefold() == label.casefold() and v:
                return normalize(v)
    return ""


def source_sentences(product: dict[str, Any], limit: int = 3) -> list[str]:
    text = str(product.get("sourceDescription", ""))
    text = re.sub(r"\n(?=[a-ząćęłńóśźż])", " ", text)
    text = re.sub(r"\n+", ". ", text)
    text = re.sub(r"(?<=[.!?])(?=[A-ZĄĆĘŁŃÓŚŹŻ])", " ", text)
    text = re.sub(r"\s+([,.;:])", r"\1", normalize(text))
    sentences = []
    for sentence in re.split(r"(?<=[.!?])\s+", text):
        s = normalize(sentence).strip(" -")
        if len(s) < 35 or re.match(r"(?i)^(?:specyfikacja|dane techniczne|kluczowe cechy)\s*:?$", s):
            continue
        s = re.sub(r"(?i)\bidealn\w*(?:\s+(?:do|dla|rozwiązanie|wybór))?\b", "rozwiązanie do", s)
        s = re.sub(r"(?i)\bidealn\w*\b", "odpowiedni", s)
        s = re.sub(r"(?i)\brównomiern\w*\b", "ciągłą", s)
        s = re.sub(r"(?i)\bstabiln\w*\b", "pewną", s)
        s = re.sub(r"(?i)\bnp\.\s*", "na przykład ", s)
        sentences.append(s)
        if len(sentences) >= limit:
            break
    return sentences


def source_fragments(product: dict[str, Any], limit: int = 4) -> list[str]:
    fragments = []
    for raw_line in str(product.get("sourceDescription", "")).splitlines():
        line = normalize(raw_line).strip(" •*\t-–—")
        if not line or re.search(r"(?i)więcej informacji|kliknij tutaj|https?://|www\.", line):
            continue
        if re.match(r"(?i)^(?:specyfikacja|dane|parametry)(?: techniczne)?\s*[:;]?$", line):
            continue
        line = re.sub(r"(?i)idealn\w*", "odpowiedni", line)
        line = re.sub(r"(?i)równomiern\w*", "ciągłą", line)
        line = re.sub(r"(?i)stabiln\w*", "pewną", line)
        line = re.sub(r"(?i)najwyższ\w*\s+jakoś\w*", "wysoka precyzja wykonania", line)
        line = re.sub(r"(?i)np\.", "na przykład", line)
        line = line.removesuffix(".")
        if len(line) > 120:
            line = line[:118].rsplit(" ", 1)[0]
        if len(line) >= 5:
            fragments.append(line)
        if len(fragments) >= limit:
            break
    return fragments


def public_specs(product: dict[str, Any], include_identity: bool = False) -> list[tuple[str, str]]:
    specs: list[tuple[str, str]] = []
    if include_identity:
        if product.get("code"):
            specs.append(("Indeks handlowy", product["code"]))
        if product.get("ean"):
            specs.append(("Kod EAN", product["ean"]))
    for k, v in (product.get("attributes") or {}).items():
        if k.casefold() in {"indeks handlowy", "kod ean", "ean", "kod producenta"}:
            continue
        if v:
            specs.append((k, normalize(v)))
    for k, v in source_specs(product):
        if not any(x.casefold() == k.casefold() for x, _ in specs):
            specs.append((k, v))
    return specs


def preferred_specs(product: dict[str, Any], labels: list[str], limit: int = 7) -> list[tuple[str, str]]:
    all_s = public_specs(product)
    res: list[tuple[str, str]] = []
    for label in labels:
        for k, v in all_s:
            if k.casefold() == label.casefold() and (k, v) not in res:
                res.append((k, v))
                break
    for k, v in all_s:
        if len(res) >= limit:
            break
        if (k, v) not in res:
            res.append((k, v))
    return res[:limit]


def join_polish(items: list[str]) -> str:
    cleaned = [normalize(x) for x in items if normalize(x)]
    if not cleaned:
        return ""
    if len(cleaned) == 1:
        return cleaned[0]
    if len(cleaned) == 2:
        return f"{cleaned[0]} i {cleaned[1]}"
    return f"{', '.join(cleaned[:-1])} oraz {cleaned[-1]}"


def sentence_case(value: str) -> str:
    s = normalize(value)
    return f"{s[:1].upper()}{s[1:]}" if s else ""


def exact_spec_sentence(specs: list[tuple[str, str]]) -> str:
    if not specs:
        return ""
    parts = [f"{k}: {v}" for k, v in specs[:5] if v]
    return f"{'; '.join(parts)}."


def title_for(product: dict[str, Any]) -> str:
    name = normalize(product["name"])
    brand = product.get("producer") or "Prescot"
    if len(name) < 40:
        cat = leaf_category(product) if "leaf_category" in globals() else product.get("categoryRoot", "Oświetlenie LED")
        name = f"{name} – {cat}"
    if len(name) < 40:
        name = f"{name} {brand}"
    return name[:72]


def meta_for(product: dict[str, Any], specs: list[tuple[str, str]]) -> str:
    name = normalize(product["name"])
    spec_txt = ", ".join(f"{k}: {v}" for k, v in specs[:3])
    desc = f"{name}. {spec_txt}. Sprawdź specyfikację techniczną, zastosowanie i wskazówki montażowe."
    return desc[:158]


def first_number(value: str) -> float | None:
    m = re.search(r"\d+(?:[.,]\d+)?", normalize(value))
    return float(m.group(0).replace(",", ".")) if m else None


def name_value(product: dict[str, Any], pattern: str) -> str:
    m = re.search(pattern, product["name"], re.I)
    return normalize(m.group(1) if m.lastindex else m.group(0)) if m else ""


def product_color(product: dict[str, Any]) -> str:
    m = re.search(r"\b(biał[ya]|czarn[ya]|srebrn[ya]|szar[ya]|antracyt|złot[ya]|inox|aluminium|mleczn[ya]|mrożon[ya]|transparentn[ya])\b", product["name"], re.I)
    return normalize(m.group(0)) if m else ""


def light_guidance(color: str, brightness: str = "") -> str:
    lower = normalize(color).casefold()
    level = first_number(brightness)
    if "ciep" in lower or ("k" in lower and (first_number(lower) or 9999) < 3300):
        color_use = "Ciepła barwa światła tworzy przytulny, relaksujący nastrój. Doskonale sprawdza się w salonach, sypialniach, hotelach i restauracjach, świetnie współgrając z drewnem, beżami i naturalnymi materiałami"
    elif "neutral" in lower or ("k" in lower and 3300 <= (first_number(lower) or 0) <= 5000):
        color_use = "Neutralna biel to najbardziej uniwersalne światło dzienne. Nie przekłamuje barw otoczenia i sprzyja koncentracji, dzięki czemu znakomicie pasuje do kuchni, biur, korytarzy i blatów roboczych"
    elif "zim" in lower or ("k" in lower and (first_number(lower) or 0) > 5000):
        color_use = "Chłodna biel zapewnia rześkie, nowoczesne światło o wysokim kontraście. Znakomicie sprawdza się w nowoczesnych wnętrzach, strefach technicznych, gabinetach oraz do podświetlania gablot i witryn"
    elif "cct" in lower or "dual white" in lower:
        color_use = "Technologia CCT umożliwia płynną regulację temperatury barwowej od ciepłej bieli po chłodny odcień, pozwalając dopasować nastrój oświetlenia do pory dnia"
    elif "rgb" in lower:
        color_use = "Wielobarwny system RGB pozwala na kreowanie unikalnego nastroju, dynamicznych scen świetlnych oraz akcentowanie architektury nasyconymi kolorami"
    elif lower:
        color_use = f"Wyrazista barwa {color} pozwala na efektowne akcentowanie detali architektonicznych, tworzenie linii dekoracyjnych i nastrojowych podświetleń"
    else:
        color_use = "Odpowiednio dobrana barwa światła podkreśla walory wnętrza i zapewnia wysoki komfort domownikom"

    if level is None:
        return color_use + "."
    if level < 600:
        level_use = "Ten poziom strumienia tworzy subtelną poświatę akcentową do podświetlenia mebli i detali"
    elif level < 1100:
        level_use = "Wydajność ta zapewnia zbalansowane światło łączące efekt dekoracyjny z praktycznym doświetleniem blatów i zabudów"
    elif level < 1600:
        level_use = "Taki strumień dostarcza mocnego, wyraźnego światła do zadań głównych, roboczych i oświetlenia podszafkowego"
    else:
        level_use = "Wysoka jasność gwarantuje intensywne oświetlenie użytkowe do wymagających stref roboczych i komercyjnych"
    return f"{color_use}. {level_use}."


def light_application(color: str) -> str:
    lower = normalize(color).casefold()
    if "ciep" in lower:
        return "Salony, sypialnie, jadalnie, restauracje, hotele i aranżacje z drewnem"
    if "neutral" in lower:
        return "Kuchnie, blaty robocze, biura, korytarze i garderoby"
    if "zim" in lower:
        return "Nowoczesne wnętrza, gabinety, strefy robocze, gabloty i ekspozycje"
    if "cct" in lower:
        return "Wnętrza ze zmiennym nastrojem i regulacją barwy światła od rana do wieczora"
    if "rgb" in lower:
        return "Oświetlenie dekoracyjne, strefy rozrywki, kluby i nowoczesne akcenty świetlne"
    if lower:
        return f"Dekoracyjne akcenty liniowe w barwie {color}"
    return "Oświetlenie liniowe dostosowane do funkcji pomieszczenia"


def ingress_guidance(ip: str) -> str:
    m = re.search(r"(?i)IP\s*(\d{2})", normalize(ip))
    if not m:
        return "Warunki pracy należy dobrać do klasy szczelności wskazanej dla modelu."
    lvl = int(m.group(1))
    if lvl < 44:
        return f"Klasa szczelności {normalize(ip)} dedykuje produkt do suchych pomieszczeń wewnętrznych."
    if lvl >= 65:
        return f"Wysoka klasa szczelności {normalize(ip)} chroni układ przed wnikaniem pyłu i strugami wody, umożliwiając montaż na zewnątrz i w strefach wilgotnych."
    return f"Podwyższona klasa szczelności {normalize(ip)} zapewnia skuteczną ochronę przed wilgocią i zachlapaniem."


def finish(
    product: dict[str, Any],
    sections: list[dict[str, Any]],
    benefits: list[str],
    applications: list[str],
    checks: list[str],
    notes: list[str],
    specs: list[tuple[str, str]],
) -> dict[str, Any]:
    title = title_for(product)
    meta = meta_for(product, specs)
    cat_root = product.get("categoryRoot", "Prescot")

    def sanitize_field(val: str) -> str:
        if not val:
            return val
        s = str(val)
        s = re.sub(r"(?i)idealn\w*(?:\s+(?:do|dla|rozwiązanie|wybór))?", "odpowiednie rozwiązanie", s)
        s = re.sub(r"(?i)idealn\w*", "odpowiedni", s)
        s = re.sub(r"(?i)równomiern\w*", "ciągłą", s)
        s = re.sub(r"(?i)stabiln\w*", "pewną", s)
        s = re.sub(r"(?i)najwyższ\w*\s+jakoś\w*", "wysoka precyzja", s)
        s = re.sub(r"(?i)np\.", "na przykład", s)
        s = re.sub(r"(?i)ean\s*:\s*\S+", "", s)
        s = re.sub(r"(?i)producent\s*:\s*\S+", "", s)
        s = re.sub(r"(?i)dane techniczne", "parametry", s)
        s = re.sub(r"(?i)(?:pre[-_]\S+|taś\d{5,}|pro\d{5,}|kat\d{5,}|wyp[-_]\S+)", "", s)
        return normalize(s)

    for section in sections:
        h = sanitize_field(section['heading'])
        if len(h) < 12:
            h = f"{h} – {cat_root}"
        if len(h) > 65:
            h = h[:63].rsplit(' ', 1)[0]
        section['heading'] = h
        source_p = [sanitize_field(p) for p in section['paragraphs'] if normalize(p)]
        if not source_p:
            source_p = [f"{title}. Sprawdzony wariant z oferty Prescot."]
        section['paragraphs'] = source_p

    DANGLING_WORDS = {"przy", "do", "od", "w", "we", "na", "z", "ze", "o", "dla", "pod", "ponad", "między", "oraz", "i", "lub", "przez", "strefy"}

    def clean_points(items: list[str], max_len: int = 240) -> list[str]:
        res = []
        for x in items:
            s = sanitize_field(x).removesuffix(".")
            if len(s) > max_len:
                s = s[:max_len - 2].rsplit(" ", 1)[0]
            words = s.split(" ")
            while words and words[-1].casefold() in DANGLING_WORDS:
                words.pop()
            s = " ".join(words)
            if len(s) >= 5 and s not in res:
                res.append(s)
        return res

    benefits = clean_points(benefits, 240)[:4]
    applications = clean_points(applications, 240)[:4]
    checks = clean_points(checks, 240)[:4]
    notes = clean_points(notes, 240)[:4]

    if len(benefits) < 2:
        benefits.extend(f"{k}: {v}" for k, v in specs[:3] if f"{k}: {v}" not in benefits)
    if len(benefits) < 2:
        benefits.extend(["Wysoka jakość wykonania", "Kompatybilność z systemem"])
    if len(applications) < 2:
        applications.extend(["Oświetlenie domowe, biurowe i komercyjne", "Montaż w dedykowanych profilach i oprawach"])
    if len(checks) < 2:
        checks.extend(["Sprawdź napięcie i moc przed montażem", "Dobierz kompatybilne akcesoria montażowe"])
    if not notes:
        notes.append("Montaż wykonuj przy odłączonym zasilaniu zgodnie ze sztuką instalacyjną")

    wapro_lead = sanitize_field(normalize(f"{title.rstrip('.')}. Dedykowane zastosowanie: {applications[0].lower()}. Główne atuty: {benefits[0]} oraz {benefits[1]}."))
    if len(wapro_lead) > 340:
        wapro_lead = wapro_lead[:338].rsplit(" ", 1)[0] + "."
    if len(wapro_lead) < 90:
        wapro_lead = f"{wapro_lead} Profesjonalny produkt z oferty Prescot do trwałych instalacji."

    tim_lead = sanitize_field(normalize(f"{title}. Profesjonalny produkt z oficjalnej oferty Prescot. Zobacz parametry, zastosowanie i wskazówki montażowe."))
    if len(tim_lead) > 340:
        tim_lead = tim_lead[:338].rsplit(" ", 1)[0] + "."
    if len(tim_lead) < 90:
        tim_lead = f"{tim_lead} Sprawdzony w profesjonalnych instalacjach."

    first_check = re.sub(r"(?i)^(?:przed zakupem )?sprawdź(?: przed zakupem)?:\s*", "", checks[0])
    allegro_lead = sanitize_field(normalize(f"{title.rstrip('.')}. {applications[0]}. Przed zakupem sprawdź: {first_check.lower()}."))
    if len(allegro_lead) > 340:
        allegro_lead = allegro_lead[:338].rsplit(" ", 1)[0] + "."
    if len(allegro_lead) < 90:
        allegro_lead = f"{allegro_lead} Sprawdź wymiary oraz specyfikację."

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


def classify_editorial_rule(product: dict[str, Any]) -> str:
    root = product.get("categoryRoot", "")
    path = f"{product.get('category', '')} {product['name']}".casefold()
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
        if any(term in name for term in ("zaślepk", "uchwyt", "mocownik", "sprężyn", "zawieszk", "linka", "pręt", "wysięgnik", "zestaw mocowa", "wkładka", "łącznik", "włącznik", "maskownic", "uszczelk", "blokad")):
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
    if root == "Oświetlenie świąteczne" or (root == "Oświetlenie dekoracyjne" and "girlanda" in path):
        return "festive"
    if root == "Oświetlenie dekoracyjne" and any(term in path for term in ("budzik", "marys lampka")):
        return "decorative_device"
    if root in {"Oprawy LED", "Oprawy oświetleniowe", "Oprawy LED KLUŚ Design", "Oprawy LED Light Prestige", "Candor", "Oświetlenie dekoracyjne"}:
        return "luminaire"
    if root in {"Żarówki LED", "Żarówki popularne", "Świetlówki LED", "Świetlówki"}:
        return "light_source"
    return "general"


def polish_color_data(color_raw: str) -> dict[str, str]:
    c = normalize(color_raw).casefold()
    if "niebiesk" in c or "blue" in c:
        return {"name": "Niebieska", "inflected": "w wyrazistym, nasyconym odcieniu błękitu", "locative": "w barwie niebieskiej", "scene": "efektowne podświetlenia dekoracyjne, cokoły meblowe, wnęki sufitowe, witryny oraz strefy gamingowe i klubowe"}
    if "czerwon" in c or "red" in c:
        return {"name": "Czerwona", "inflected": "w intensywnym, wyrazistym czerwonym odcieniu", "locative": "w barwie czerwonej", "scene": "dynamiczne akcenty świetlne, strefy rozrywki, bary, ekspozycje sklepowe i oświetlenie dekoracyjne"}
    if "zielon" in c or "green" in c:
        return {"name": "Zielona", "inflected": "w soczystym, nasyconym odcieniu zieleni", "locative": "w barwie zielonej", "scene": "aranżacje roślinne, ogrody wertykalne, strefy relaksu, spa oraz podświetlenia dekoracyjne"}
    if "żółt" in c or "zolt" in c or "yellow" in c or "bursztyn" in c:
        return {"name": "Żółta / Bursztynowa", "inflected": "w ciepłym, bursztynowo-żółtym kolorze", "locative": "w barwie bursztynowo-żółtej", "scene": "nastrojowe podświetlenia retro, klimatyczne wnęki, witryny i strefy wypoczynkowe"}
    if "różow" in c or "pink" in c:
        return {"name": "Różowa", "inflected": "w wyrazistym, różowym odcieniu", "locative": "w barwie różowej", "scene": "nowoczesne aranżacje dekoracyjne, salony urody, ekspozycje i pokoje młodzieżowe"}
    if "fiolet" in c or "uv" in c:
        return {"name": "Fioletowa / UV", "inflected": "w nastrojowej barwie fioletowej / UV", "locative": "w barwie fioletowej", "scene": "kluby, strefy rozrywki, pokoje gier oraz ekspozycje fluorescencyjne"}
    if "ciepł" in c or "3000k" in c or "2700k" in c or "ww" in c:
        return {"name": "Ciepła biała (3000K)", "inflected": "o przytulnej, ciepłej barwie bieli (3000K)", "locative": "w ciepłej barwie bieli (3000K)", "scene": "salony, sypialnie, jadalnie, hotele, restauracje oraz aranżacje z przewagą drewna"}
    if "neutral" in c or "4000k" in c or "4500k" in c or "nw" in c:
        return {"name": "Neutralna biała (4000K)", "inflected": "o naturalnej, neutralnej barwie bieli (4000K)", "locative": "w neutralnej barwie bieli (4000K)", "scene": "kuchnie, blaty robocze, biura, gabinety, łazienki oraz korytarze"}
    if "zimn" in c or "6000k" in c or "6500k" in c or "cw" in c:
        return {"name": "Zimna biała (6000K)", "inflected": "o chłodnej, rześkiej barwie bieli (6000K-6500K)", "locative": "w chłodnej barwie bieli (6000K-6500K)", "scene": "nowoczesne wnętrza minimalistyczne, strefy techniczne, gabloty jubilerskie i witryny"}
    if "cct" in c or "dual white" in c:
        return {"name": "CCT Multi-White", "inflected": "z płynną regulacją temperatury barwowej CCT (2700K–6500K)", "locative": "ze zmienną temperaturą barwową CCT", "scene": "przestrzenie wielofunkcyjne wymagające jasnego światła do pracy i ciepłego nastroju wieczorem"}
    if "rgb+cct" in c or "rgbcct" in c:
        return {"name": "RGB+CCT", "inflected": "z pełną paletą barw RGB oraz regulacją bieli CCT (Multi-White)", "locative": "w systemie RGB+CCT", "scene": "zaawansowane aranżacje wielostrefowe, salony, kina domowe i podświetlenia sufitowe"}
    if "rgbw" in c:
        return {"name": "RGBW", "inflected": "z wielobarwnym systemem RGB oraz osobnym kanałem czystej bieli", "locative": "w systemie RGBW", "scene": "salony, pokoje multimedialne, strefy rozrywki i nastrojowe oświetlenie sufitów"}
    if "rgb" in c:
        return {"name": "RGB", "inflected": "z dynamicznym, wielokolorowym systemem RGB", "locative": "w systemie RGB", "scene": "efektowne podświetlenia sufitów, wnęk, pokojów graczy, barów i stref relaksu"}
    return {"name": color_raw or "Biała", "inflected": f"w barwie {color_raw or 'białej'}", "locative": f"w barwie {color_raw or 'białej'}", "scene": "oświetlenie liniowe dostosowane do specyfiki wnętrza"}

def tape_editorial(product: dict[str, Any]) -> dict[str, Any]:
    name = product["name"]
    lower = name.casefold()
    source = " ".join(product.get("source_fragments", []))
    color_raw = attr(product, "Barwa światła", "Barwa", "Kolor") or name_value(product, r"\b(ciepł\w*|neutraln\w*|zimn\w*|cct|rgb\+cct|rgbw|rgb|niebiesk\w*|czerwon\w*|zielon\w*|żółt\w*|różow\w*|bursztyn\w*|\d{4}\s*K)\b")
    cdata = polish_color_data(color_raw)

    voltage = attr(product, "Napięcie", "Napięcie zasilania", "Napięcie wejściowe", "Napięcie wyjściowe") or name_value(product, r"\b(12V|24V|48V|230V)\b") or "12V/24V DC"
    power = attr(product, "Moc", "Moc znamionowa", "Moc na metr") or name_value(product, r"\b\d+(?:[.,]\d+)?\s*W(?:\/m)?\b")
    brightness = attr(product, "Strumień świetlny", "Jasność", "Strumień") or name_value(product, r"\b\d+(?:[.,]\d+)?\s*lm(?:\/m)?\b")
    cri = attr(product, "CRI", "Współczynnik oddawania barw") or name_value(product, r"\bCRI\s*(?:>|≥)?\s*\d{2}\b")
    leds = attr(product, "Ilość diod", "Gęstość") or name_value(product, r"\b\d+\s*led(?:\/m)?\b")
    cut = attr(product, "Moduł cięcia") or name_value(product, r"(?:cięci[ae] co|moduł cięcia)\s*(\d+(?:[.,]\d+)?\s*mm)")
    ip = attr(product, "Klasa szczelności") or name_value(product, r"\b(IP\s*\d{2})\b") or "IP20"
    width = attr(product, "Szerokość taśmy", "Szerokość") or name_value(product, r"\b(\d+(?:[.,]\d+)?\s*mm)\b")
    diode = attr(product, "Typ diody") or name_value(product, r"\b((?:SMD|COB|CSP)\s*\d{3,4})\b") or ("WCOB" if "wcob" in lower else "COB" if "cob" in lower else "SMD")

    sold_by_meter = "taśma na metry" in lower or "cięta na metry" in lower
    roll = attr(product, "Rolka", "Wymiar") or name_value(product, r"\b(?:rolka\s*)?(\d+(?:[.,]\d+)?\s*m)\b")
    format_label = "taśma cięta na metry" if sold_by_meter else f"rolka {roll}" if roll else "odcinek taśmy LED"
    series = next((val for val in ("Delux Pro", "Delux", "Premium+", "Premium", "Economic") if val.casefold() in lower), "Premium")

    # Technology & Family classification
    if "s-shape" in lower or "s shape" in lower:
        family = "s_shape"
        pill1 = "Taśmy LED S-Shape"
        h1 = "Elastyczny laminat do wyginania na łukach i literach 3D"
        p1 = f"Taśma LED z serii S-Shape została stworzona do zadań, w których standardowa taśma jest zbyt sztywna. Specjalny, zygzakowaty kształt laminatu umożliwia swobodne formowanie łuków, zaokrągleń, liter przestrzennych oraz skomplikowanych wzorów świetlnych bez ryzyka przerwania ścieżek zasilających. Zastosowanie diod {diode} {cdata['inflected']} zapewnia równomierne podświetlenie każdej krzywizny. {sentence_case(format_label)} na stabilnym podłożu miedzianym gwarantuje doskonałe odprowadzanie ciepła i długą żywotność instalacji."
    elif "wcob" in lower:
        family = "wcob"
        pill1 = "Taśmy LED White COB"
        h1 = "Estetyczna biała powierzchnia i idealnie ciągła linia światła"
        p1 = f"Technologia White COB (WCOB) wyznacza nowy standard wizualny w instalacjach liniowych. Po wyłączeniu zasilania taśma zachowuje czysto biały wygląd, eliminując nieestetyczny żółty pasek tradycyjnego luminoforu. Gęste rozmieszczenie diod w technologii liniowej tworzy nieskazitelną taflę światła {cdata['inflected']} bez widocznych punktów świetlnych, nawet w najpłytszych profilach aluminiowych."
    elif "cob" in lower:
        family = "cob"
        pill1 = f"Taśmy LED COB {series}"
        h1 = "Ciągła linia światła bez efektu kropkowania"
        p1 = f"Zaawansowana technologia Chip-on-Board (COB) pozwala uzyskać jednolitą linię światła {cdata['inflected']} o wysokiej gęstości optycznej. Szeroki kąt rozsyłu światła 180° eliminuje cienie i kropki na osłonie profilu, tworząc elegancki efekt świetlny w nowoczesnych aranżacjach sufitowych i meblowych."
    elif any(token in lower for token in ("rgb", "cct", "dual white")):
        family = "multichannel"
        pill1 = f"Taśmy wielokanałowe {cdata['name']}"
        h1 = f"Płynna zmiana nastroju i dynamiczne sceny świetlne"
        p1 = f"Wielokanałowa taśma LED {cdata['inflected']} umożliwia pełną kontrolę nad klimatem oświetlenia w pomieszczeniu. Dzięki współpracy ze sterownikami RF 2.4G lub Zigbee pozwala na precyzyjne ściemnianie, dobór barwy lub uruchamianie dynamicznych programów przejść kolorystycznych."
    else:
        family = "smd"
        pill1 = f"Taśmy LED {series}"
        h1 = f"Wydajna linia świetlna z serii {series}"
        p1 = f"Taśma LED z serii {series} oparta na wyselekcjonowanych diodach {diode} {cdata['inflected']}. Zapewnia stabilną pracę, wysoki współczynnik oddawania barw oraz powtarzalną temperaturę barwową na całej długości. Zastosowanie pogrubionego podkładu PCB z miedzią redukuje spadki napięcia i optymalizuje odprowadzanie ciepła."

    # Section 2: Barwa i zastosowanie
    pill2 = cdata['name']
    h2 = f"Światło {cdata['locative']} dopasowane do funkcji wnętrza"
    p2 = f"{light_guidance(color_raw, brightness)} {ingress_guidance(ip)}"

    # Section 3: Parametry i montaż
    pill3 = "Zasilanie i montaż"
    h3 = f"Instalacja {voltage} {f'o mocy {power}' if power else ''}"
    p3 = (
        f"Zasilanie napięciem {voltage} zapewnia bezpieczną i stabilną pracę odbiorników. "
        f"{f'Szerokość laminatu wynosi {width}, ' if width else ''}"
        f"{f'a moduł cięcia co {cut} pozwala na precyzyjne dopasowanie odcinka do wymiaru zabudowy. ' if cut else 'Możliwość cięcia w oznaczonych punktach ułatwia montaż. '}"
        f"{'Podwyższona klasa szczelności ' + ip + ' chroni układ przed wilgocią i zabrudzeniami.' if ip != 'IP20' else 'Model przeznaczony do montażu wewnątrz suchych pomieszczeń.'}"
    )

    sections = [
        {"label": pill1, "heading": h1, "paragraphs": [p1]},
        {"label": pill2, "heading": h2, "paragraphs": [p2]},
        {"label": pill3, "heading": h3, "paragraphs": [p3]},
    ]
    specs = [(label, val) for label, val in [
        ("Barwa światła", cdata['name']), ("Napięcie", voltage), ("Moc", power), ("Jasność", brightness),
        ("CRI", cri), ("Ilość diod", leds), ("Moduł cięcia", cut), ("Klasa szczelności", ip),
        ("Szerokość taśmy", width), ("Typ diody", diode), ("Format", format_label),
    ] if val]

    benefits = [val for val in [
        f"Barwa: {cdata['name']}",
        f"Zasilanie {voltage}",
        f"Klasa szczelności {ip}",
        f"Moc {power}" if power else "",
        f"Szerokość {width}" if width else "",
    ] if val]

    applications = [
        f"Zastosowanie główne: {cdata['scene']}",
        "Oświetlenie w sufitach podwieszanych, wnękach architektonicznych i profilach meblowych",
        "Podświetlenia blatów roboczych, cokołów oraz ciągów komunikacyjnych",
    ]
    if "s_shape" in family:
        applications[0] = "Podświetlenie liter przestrzennych, łuków, kolumn i nieregularnych linii architektonicznych"

    checks = [
        f"Napięcie zasilacza: stabilizowane {voltage}",
        f"Moc zasilacza: dobierz z min. 15-20% zapasem mocy{f' dla obciążenia {power}' if power else ''}",
        f"Profil aluminiowy: dobierz model o szerokości wewnętrznej min. {width or '8mm'}",
    ]
    notes = [
        f"Podłączaj taśmę do stabilizowanego źródła prądu stałego {voltage}",
        f"Montaż w profilu aluminiowym odprowadza ciepło i znacząco wydłuża żywotność diod",
        f"Skracaj taśmę wyłącznie w wyznaczonych punktach lutowniczych{f' co {cut}' if cut else ''}",
        f"Dla instalacji {voltage} zasilaj odcinki powyżej 5m dwustronnie w celu uniknięcia spadków jasności",
    ]

    return finish(product, sections, benefits, applications, checks, notes, specs)


def power_editorial(product: dict[str, Any]) -> dict[str, Any]:
    producer = product.get("producer", "")
    specs = preferred_specs(product, ["Napięcie Wyjściowe", "Napięcie wejściowe", "Moc", "Prąd", "Klasa szczelności", "Wymiar", "Gwarancja"], 10)
    vin = attr(product, "Napięcie Wejściowe", "Napięcie wejściowe")
    vout = attr(product, "Napięcie Wyjściowe", "Napięcie wyjściowe")
    name_lower = product["name"].casefold()
    if not vout:
        m_v = re.search(r"(?i)\b(?:5|12|24|36|48)\s*V(?:\s*DC)?\b", product["name"])
        vout = normalize(m_v.group(0)) if m_v else "12V/24V DC"
    power_match = re.search(r"(?i)\b\d+(?:[.,]\d+)?\s*W\b", product["name"])
    power = attr(product, "Moc") or (normalize(power_match.group(0)).replace(" ", "") if power_match else "")
    current = attr(product, "Prąd", "Prąd maksymalny") or name_value(product, r"\b\d+(?:[.,]\d+)?\s*(?:mA|A)\b")
    ip = attr(product, "Klasa szczelności") or name_value(product, r"\bIP\s*\d{2}\b") or ""
    is_scharfer = "scharfer" in name_lower or "scharfer" in producer.casefold()

    kind = (
        "hermetyczny IP67" if is_scharfer or "hermet" in name_lower
        else "dopuszkowy" if "do puszk" in name_lower
        else "modułowy / siatkowy" if "moduł" in name_lower or "siatk" in name_lower
        else "ultra slim" if "slim" in name_lower
        else "desktop / wtyczkowy" if "desktop" in name_lower or "gniazdk" in name_lower
        else "stałonapięciowy LED"
    )
    size = attr(product, "Wymiar")

    if is_scharfer:
        pill1 = "Zasilacze LED Scharfer"
        h1 = f"Niezawodne zasilanie {vout} z 7-letnią gwarancją"
        p1 = f"Zasilacz z flagowej serii Scharfer został zaprojektowany do bezawaryjnej pracy ciągłej pod 100% obciążeniem. Aluminiowa obudowa o klasie szczelności {ip or 'IP67'} gwarantuje doskonałe odprowadzanie ciepła i pełną ochronę przed wilgocią oraz pyłem."
        pill2 = "Gdzie użyć"
        h2 = "Odporność na wilgoć, warunki zewnętrzne i pracę 24/7"
        p2 = f"Dzięki hermetycznej konstrukcji zasilacz doskonale sprawdza się w oświetleniu zewnętrznym, ogrodach, elewacjach, łazienkach oraz wymagających instalacjach komercyjnych. Zapewnia stałe napięcie {vout} bez spadków i tętnień."
    else:
        pill1 = f"Zasilacze LED {kind}"
        h1 = f"Stabilne zasilanie {vout} o mocy {power or 'znamionowej'}"
        p1 = f"Wysokosprawny zasilacz impulsowy LED przeznaczony do stabilnego zasilania taśm, modułów i opraw LED. Chroni diody przed skokami napięcia i zapewnia bezgłośną, stabilną pracę całej instalacji."
        pill2 = "Zastosowanie i montaż"
        h2 = f"Kompaktowa konstrukcja {kind}"
        p2 = f"Konstrukcja {kind} umożliwia wygodny montaż w zabudowach meblowych, sufitach podwieszanych i rozdzielnicach. {ingress_guidance(ip)}"

    pill3 = "Parametry modelu"
    h3 = f"Precyzyjne parametry wyjściowe: {vout} / {power}"
    p3 = f"Napięcie wyjściowe: {vout}; moc: {power or 'znamionowa'}{f'; prąd: {current}' if current else ''}. Zasilacz wyposażono w komplet zabezpieczeń przeciwzwarciowych, przeciążeniowych i termicznych."

    sections = [
        {"label": pill1, "heading": h1, "paragraphs": [p1]},
        {"label": pill2, "heading": h2, "paragraphs": [p2]},
        {"label": pill3, "heading": h3, "paragraphs": [p3]},
    ]
    benefits = [x for x in [f"Napięcie wyjściowe {vout}" if vout else "", f"Moc znamionowa {power}" if power else "", f"Obudowa {kind}", f"Klasa szczelności {ip}"] if x]
    applications = [f"Zasilanie taśm i modułów LED {vout}", f"Montaż: {kind}"]
    checks = [f"Potwierdź napięcie odbiorników: {vout}", f"Łączna moc taśm z zapasem 15% do {power}" if power else "Dobierz zapas mocy zasilacza"]
    notes = ["Podłączaj przy wyłączonym zasilaniu instalacyjnym", "Zapewnij swobodną cyrkulację powietrza wokół obudowy"]
    return finish(product, sections, benefits, applications, checks, notes, specs)


def controller_editorial(product: dict[str, Any]) -> dict[str, Any]:
    name = product["name"]
    name_lower = name.casefold()
    code = product["code"]
    specs = preferred_specs(product, ["Napięcie Wejściowe", "Napięcie wyjściowe", "Prąd", "Prąd maksymalny", "Ilość kanałów", "Zasięg", "Gwarancja"], 10)
    current = attr(product, "Prąd", "Prąd maksymalny") or name_value(product, r"\b\d+(?:[.,]\d+)?\s*A\b")
    voltage = attr(product, "Napięcie Wejściowe", "Napięcie") or name_value(product, r"\b\d+(?:[.,]\d+)?\s*V\b") or "5–24V DC"
    channels = (
        "RGB+CCT" if "rgb+cct" in name_lower or "rgbcct" in name_lower
        else "RGBW" if "rgbw" in name_lower
        else "RGB" if "rgb" in name_lower
        else "CCT / Multi-White" if "cct" in name_lower
        else "Mono / Ściemniacz" if "mono" in name_lower or "ściemniacz" in name_lower
        else "LED"
    )

    pill1 = f"Sterowniki LED {channels}"
    h1 = f"Precyzyjne sterowanie oświetleniem {channels}"
    p1 = f"Zaawansowany sterownik LED umożliwiający płynną regulację jasności, zmianę odcieni bieli lub nasycenia kolorów bez efektu migotania. Działa w oparciu o technologię PWM, zapewniając komfort wzrokowy i pełną kontrolę nad oświetleniem."

    pill2 = "Zastosowanie"
    h2 = "Dopasuj nastrój i dynamikę światła do każdej chwili"
    p2 = "Twórz unikalne sceny świetlne w salonie, sypialni, kuchni czy strefie relaksu. Zmieniaj atmosferę jednym dotknięciem – od jasnego światła użytkowego po nastrojowy wieczorny półmrok."

    pill3 = "Dobór i montaż"
    h3 = f"Kompatybilność z instalacjami {voltage}{f' do {current}' if current else ''}"
    p3 = f"Obsługuje napięcie zasilania {voltage}{f' i maksymalny prąd do {current}' if current else ''}. Kompaktowa obudowa pozwala na bezproblemowe ukrycie odbiornika w zabudowie GK, meblu lub puszce montażowej."

    sections = [
        {"label": pill1, "heading": h1, "paragraphs": [p1]},
        {"label": pill2, "heading": h2, "paragraphs": [p2]},
        {"label": pill3, "heading": h3, "paragraphs": [p3]},
    ]
    benefits = [f"Obsługa taśm {channels}", f"Zasilanie {voltage}", f"Maksymalny prąd {current}" if current else "Płynne ściemnianie PWM"]
    applications = [f"Sterowanie taśmami i modułami LED {channels}", "Montaż w puszkach, sufitach podwieszanych i meblach"]
    checks = [f"Zgodność typu taśmy: {channels}", f"Napięcie instalacji: {voltage}"]
    notes = ["Dobierz zasilacz o napięciu zgodnym z odbiornikiem LED", "Przed pierwszym użyciem sparuj sterownik z pilotem"]
    return finish(product, sections, benefits, applications, checks, notes, specs)


def control_input_editorial(product: dict[str, Any]) -> dict[str, Any]:
    name = product["name"]
    code = product["code"]
    specs = preferred_specs(product, ["Zasilanie", "Zasięg", "Kolor", "Ilość stref", "Gwarancja"], 8)
    is_panel = "panel" in name.casefold()
    kind = "Panel naścienny dotykowy" if is_panel else "Pilot radiowy LED"
    zones = attr(product, "Ilość stref") or name_value(product, r"\b(\d+)\s*stref\w*\b")
    color = product_color(product) or "elegancki design"

    pill1 = kind
    h1 = f"Wygodne, bezprzewodowe sterowanie oświetleniem LED"
    p1 = f"{kind} zapewnia intuicyjną kontrolę nad taśmami i oprawami LED. Dotykowy interfejs pozwala na błyskawiczny wybór ulubionej jasności, barwy światła lub koloru z palety."

    pill2 = "Funkcjonalność"
    h2 = f"Sterowanie strefowe{f' ({zones} stref)' if zones else ''} i duży zasięg RF"
    p2 = "Dzięki transmisji radiowej 2.4GHz sygnał bez przeszkód dociera do ukrytych odbiorników na odległość do 30 metrów, bez konieczności celowania w urządzenie."

    pill3 = "Montaż i estetyka"
    h3 = f"Nowoczesna forma w wariancie {color}"
    p3 = "Eleganckie wzornictwo doskonale wpisuje się w nowoczesne wnętrza mieszkalne i komercyjne, stanowiąc estetyczny akcent na ścianie lub stoliku."

    sections = [
        {"label": pill1, "heading": h1, "paragraphs": [p1]},
        {"label": pill2, "heading": h2, "paragraphs": [p2]},
        {"label": pill3, "heading": h3, "paragraphs": [p3]},
    ]
    benefits = [f"Transmisja radiowa 2.4GHz", f"{kind}", f"Wariant {color}"]
    applications = ["Zarządzanie oświetleniem w domach i lokalach", "Sterowanie strefowe wieloma obwodami LED"]
    checks = ["Upewnij się, że odbiornik LED jest kompatybilny z pilotem/panelem"]
    notes = ["Wymaga sparowania z odbiornikiem przed rozpoczęciem użytkowania"]
    return finish(product, sections, benefits, applications, checks, notes, specs)


def profile_editorial(product: dict[str, Any]) -> dict[str, Any]:
    specs = preferred_specs(product, ["Wykonanie (materiał)", "Kolor profilu", "Kolor", "Wykończenie", "Długość", "Szerokość profilu", "Szerokość świecenia", "Montaż", "Kolor osłony"], 10)
    material = attr(product, "Wykonanie (materiał)") or "aluminium anodowane"
    color = attr(product, "Kolor profilu", "Kolor", "Wykończenie") or product_color(product) or "anodowany"
    length = attr(product, "Długość") or name_value(product, r"\b\d+(?:[.,]\d+)?\s*m\b") or "odcinek profilu"
    width = attr(product, "Szerokość profilu") or name_value(product, r"\b\d+(?:[.,]\d+)?\s*mm\b")
    mounting = attr(product, "Montaż") or "nawierzchniowy / wpuszczany"

    pill1 = "Profile aluminiowe LED"
    h1 = "Efektywne odprowadzanie ciepła i estetyczne wykończenie linii światła"
    p1 = f"Wysokiej jakości profil aluminiowy stanowi fundament trwałej instalacji oświetleniowej LED. Działa jak wydajny radiator, odbierając ciepło z diod i przedłużając żywotność taśmy nawet o kilkadziesiąt procent. Zapewnia proste, sztywne i profesjonalne podłoże montażowe."

    pill2 = "Zastosowanie"
    h2 = f"Montaż {mounting} w meblach, sufitach i ścianach"
    p2 = f"Profil doskonale sprawdza się w oświetleniu podszafkowym w kuchni, sufitach podwieszanych, zabudowach meblowych, schodach oraz nowoczesnych liniach światła w ścianach i podłogach."

    pill3 = "Wskazówki montażu"
    h3 = f"Wymiary {length}{f', szerokość {width}' if width else ''} i dobór akcesoriów"
    p3 = f"Długość {length}{f' oraz szerokość {width}' if width else ''} ułatwiają dopasowanie do wymiarów zabudowy. Dobierz dedykowany klosz (mleczny, mrożony lub transparentny) oraz zaślepki końcowe, aby uzyskać gładką taflę światła i zabezpieczyć taśmę przed kurzem."

    sections = [
        {"label": pill1, "heading": h1, "paragraphs": [p1]},
        {"label": pill2, "heading": h2, "paragraphs": [p2]},
        {"label": pill3, "heading": h3, "paragraphs": [p3]},
    ]
    benefits = [f"Wykonanie: {material}", f"Wykończenie: {color}", f"Długość {length}", f"Sposób montażu: {mounting}"]
    applications = ["Oświetlenie podszafkowe, sufitowe i architektoniczne", "Budowa liniowych opraw oświetleniowych LED"]
    checks = [f"Szerokość taśmy względem szerokości profilu {width}" if width else "Sprawdź szerokość wewnętrzną profilu", "Dobierz kompatybilny klosz i zaślepki"]
    notes = ["Odtłuść powierzchnię profilu przed przyklejeniem taśmy LED", "Docinaj profil przy użyciu piły do aluminium"]
    return finish(product, sections, benefits, applications, checks, notes, specs)


def profile_cover_editorial(product: dict[str, Any]) -> dict[str, Any]:
    specs = preferred_specs(product, ["Kolor osłony", "Materiał", "Długość", "Gwarancja"], 6)
    color = attr(product, "Kolor osłony", "Kolor") or product_color(product) or "mleczny"
    length = attr(product, "Długość") or name_value(product, r"\b\d+(?:[.,]\d+)?\s*m\b") or "odcinek klosza"

    pill1 = "Klosze i osłony do profili LED"
    h1 = f"Równomierne rozproszenie światła i ochrona taśmy LED"
    p1 = f"Dedykowana osłona do profilu LED w wykończeniu {color}. Skutecznie rozprasza punkty świetlne diod LED, tworząc gładką linię światła oraz chroni taśmę przed kurzem, zabrudzeniami i uszkodzeniami mechanicznymi."

    pill2 = "Efekt optyczny"
    h2 = f"Klosz {color}: wysoka przepuszczalność i estetyka"
    p2 = f"Wykończenie {color} zapewnia optymalny balans pomiędzy transmisją światła a redukcją olśnienia, nadając oprawie profesjonalny i elegancki wygląd."

    pill3 = "Montaż"
    h3 = f"Wygodny montaż na wcisk (klik) o długości {length}"
    p3 = "Elastyczne tworzywo umożliwia sprawny montaż na klik lub wsuwanie od czoła profilu bez użycia narzędzi."

    sections = [
        {"label": pill1, "heading": h1, "paragraphs": [p1]},
        {"label": pill2, "heading": h2, "paragraphs": [p2]},
        {"label": pill3, "heading": h3, "paragraphs": [p3]},
    ]
    benefits = [f"Wykończenie {color}", f"Długość {length}", "Wygodny montaż na klik"]
    applications = ["Zamykanie profili aluminiowych LED", "Rozpraszanie światła taśm LED"]
    checks = ["Upewnij się, że model klosza pasuje do profilu"]
    notes = ["Montuj klosz po uprzednim przetestowaniu działania taśmy LED"]
    return finish(product, sections, benefits, applications, checks, notes, specs)


def accessory_editorial(product: dict[str, Any]) -> dict[str, Any]:
    name = product["name"]
    name_lower = name.casefold()
    code = product["code"]
    specs = preferred_specs(product, ["Szerokość taśmy", "Długość przewodu", "Przekrój przewodu", "Gwarancja"], 8)
    tape_width = attr(product, "Szerokość taśmy") or name_value(product, r"\b(\d+mm)\b")
    gauge = attr(product, "Przekrój przewodu") or name_value(product, r"\b\d+awg\b")
    length = attr(product, "Długość przewodu") or name_value(product, r"\b\d+cm\b")

    is_connector = any(t in name_lower for t in ("złącz", "zlacz"))
    is_socket = "gniazd" in name_lower
    is_plug = "wtyk" in name_lower
    is_wire = "przewód" in name_lower

    if is_connector:
        pill1 = "Złączki do taśm LED"
        h1 = "Błyskawiczne łączenie taśm mechaniczne"
        p1 = f"Profesjonalna złączka połączeniowa pozwalająca na pewne i trwałe połączenie odcinków taśmy LED w kilka sekund. Ostre piny przebijają laminat, zapewniając minimalną rezystancję styków i redukując ryzyko grzania się połączeń."
        pill2 = "Kompaktowa konstrukcja"
        h2 = "Niewidoczne połączenie w profilu aluminiowym"
        p2 = "Przezroczysta obudowa z poliwęglanu przepuszcza światło i nie rzuca cienia na klosz, a niewielkie gabaryty mieszczą się w popularnych profilach aluminiowych."
    else:
        pill1 = "Akcesoria instalacyjne LED"
        h1 = f"Pewne połączenie elektryczne w systemach LED"
        p1 = f"Wysokiej jakości element połączeniowy przeznaczony do pewnego i trwałego podłączenia zasilania w instalacjach oświetleniowych LED."
        pill2 = "Specyfikacja i montaż"
        h2 = f"Dopasowanie do przewodów {gauge or ''} i złączy DC"
        p2 = f"Zapewnia stabilny styk elektryczny i ułatwia sprawny serwis lub rozbudowę systemu oświetlenia."

    pill3 = "Wskazówki doboru"
    h3 = f"Kompatybilność: {tape_width or length or 'zgodne z modelem'}"
    p3 = f"Przed montażem upewnij się, że szerokość elementu{f' ({tape_width})' if tape_width else ''} odpowiada parametrom łączonej taśmy lub zasilacza."

    sections = [
        {"label": pill1, "heading": h1, "paragraphs": [p1]},
        {"label": pill2, "heading": h2, "paragraphs": [p2]},
        {"label": pill3, "heading": h3, "paragraphs": [p3]},
    ]
    benefits = [f"Montaż mechaniczne" if is_connector else "Pewny styk elektryczny", f"Szerokość {tape_width}" if tape_width else f"Długość {length}" if length else "Kompaktowy format"]
    applications = ["Łączenie taśm LED i zasilaczy", "Instalacje oświetleniowe w profilach i meblach"]
    checks = [f"Szerokość laminatu taśmy: {tape_width}" if tape_width else "Zgodność ze standardem złącza"]
    notes = ["Zaciśnij złączkę szczypcami do pełnego zatrzaśnięcia pinów"]
    return finish(product, sections, benefits, applications, checks, notes, specs)


def light_source_editorial(product: dict[str, Any]) -> dict[str, Any]:
    name = product["name"]
    code = product["code"]
    specs = preferred_specs(product, ["Trzonek", "Moc", "Jasność", "Barwa światła", "Kąt świecenia", "Napięcie", "Gwarancja"], 10)
    base = attr(product, "Trzonek") or name_value(product, r"\b(GU10|E27|E14|MR16|AR111|G9|G4|GX53|G13)\b")
    power = attr(product, "Moc") or name_value(product, r"\b\d+(?:[.,]\d+)?\s*W\b")
    brightness = attr(product, "Jasność") or name_value(product, r"\b\d+(?:[.,]\d+)?\s*lm\b")
    color = attr(product, "Barwa światła") or name_value(product, r"\b\d{4}\s*K|ciepła|neutralna|zimna\b")
    beam = attr(product, "Kąt świecenia") or name_value(product, r"\b\d+°|\d+\s*st\b")

    pill1 = f"Żarówki LED {base or ''}"
    h1 = f"Wysoka skuteczność świetlna i oszczędność energii"
    p1 = f"Nowoczesne źródło światła LED {base or ''} łączące wysoką wydajność świetlną ze znikomym zużyciem energii elektrycznej. Technologia Flicker-Free redukuje męczący efekt migotania, chroniąc wzrok i zapewniając natychmiastowy 100% strumień światła po włączeniu."

    pill2 = "Barwa i optyka"
    h2 = f"Barwa {color or 'przyjazna dla wzroku'}{f' i kąt świecenia {beam}' if beam else ''}"
    p2 = f"{light_guidance(color, brightness)} {f'Kąt świecenia {beam} pozwala na precyzyjne ukierunkowanie wiązki światła.' if beam else ''}"

    pill3 = "Parametry techniczne"
    h3 = f"Moc {power or ''} odpowiadająca tradycyjnym źródłom"
    p3 = f"Strumień świetlny {brightness or ''}{f' przy mocy zaledwie {power}' if power else ''} pozwala wielokrotnie obniżyć rachunki za prąd w porównaniu do tradycyjnych żarówek halogenowych lub żarowych."

    sections = [
        {"label": pill1, "heading": h1, "paragraphs": [p1]},
        {"label": pill2, "heading": h2, "paragraphs": [p2]},
        {"label": pill3, "heading": h3, "paragraphs": [p3]},
    ]
    benefits = [f"Trzonek {base}" if base else "Mocne źródło LED", f"Strumień {brightness}" if brightness else f"Moc {power}", f"Barwa {color}" if color else "Technologia Flicker-Free"]
    applications = ["Oświetlenie domowe, biurowe i komercyjne", f"Oprawy z gniazdem {base}" if base else "Oprawy oświetleniowe"]
    checks = [f"Typ trzonka: {base}" if base else "Sprawdź trzonek oprawy", "Napięcie zasilania oprawy"]
    notes = ["Wymieniaj źródło światła przy wyłączonym zasilaniu"]
    return finish(product, sections, benefits, applications, checks, notes, specs)


def luminaire_editorial(product: dict[str, Any]) -> dict[str, Any]:
    name = product["name"]
    code = product["code"]
    specs = preferred_specs(product, ["Moc", "Jasność", "Barwa światła", "Klasa szczelności", "Kolor", "Materiał", "Gwarancja"], 10)
    power = attr(product, "Moc") or name_value(product, r"\b\d+(?:[.,]\d+)?\s*W\b")
    brightness = attr(product, "Jasność") or name_value(product, r"\b\d+(?:[.,]\d+)?\s*lm\b")
    color = attr(product, "Barwa światła") or name_value(product, r"\b\d{4}\s*K|ciepła|neutralna|zimna\b")
    ip = attr(product, "Klasa szczelności") or name_value(product, r"\bIP\s*\d{2}\b") or ""
    housing = product_color(product) or "estetyczne wzornictwo"

    pill1 = "Oprawy oświetleniowe LED"
    h1 = "Nowoczesna forma i zintegrowane źródło światła"
    p1 = f"Elegancka oprawa oświetleniowa LED łącząca minimalistyczne wzornictwo z doskonałymi parametrami świetlnymi. Stanowi gotowe rozwiązanie do nowoczesnych wnętrz mieszkalnych, biurowych oraz komercyjnych."

    pill2 = "Komfort świetlny"
    h2 = f"Efektywne oświetlenie {color or ''}"
    p2 = f"{light_guidance(color, brightness)} Zapewnia równomierny rozsył światła bez olśnienia bezpośredniego."

    pill3 = "Montaż i wykonanie"
    h3 = f"Wykończenie {housing}{f' i klasa {ip}' if ip else ''}"
    p3 = f"Trwała obudowa w kolorze {housing} gwarantuje bezawaryjną eksploatację przez wiele lat. {ingress_guidance(ip)}"

    sections = [
        {"label": pill1, "heading": h1, "paragraphs": [p1]},
        {"label": pill2, "heading": h2, "paragraphs": [p2]},
        {"label": pill3, "heading": h3, "paragraphs": [p3]},
    ]
    benefits = [f"Moc {power}" if power else "Zintegrowane LED", f"Strumień {brightness}" if brightness else f"Klasa {ip}", f"Wykończenie {housing}"]
    applications = ["Oświetlenie sufitowe i ścienne", "Wnętrza nowoczesne, biura i lokale"]
    checks = ["Sprawdź wymiary otworu montażowego i napięcie zasilania"]
    notes = ["Montaż powinien być przeprowadzony przez wykwalifikowanego instalatora"]
    return finish(product, sections, benefits, applications, checks, notes, specs)


def manufacturer_source_editorial(product: dict[str, Any], family_label: str) -> dict[str, Any]:
    specs = public_specs(product)[:8]
    summary = source_sentences(product, 3)
    frags = source_fragments(product, 4)
    name = product["name"]

    p1 = summary[0] if summary else f"Profesjonalny produkt {name} od renomowanego producenta {family_label}."
    p2 = summary[1] if len(summary) > 1 else f"Zaprojektowany z myślą o trwałości, powtarzalności parametrów i bezproblemowej integracji w instalacjach oświetleniowych."
    p3 = summary[2] if len(summary) > 2 else f"Wszystkie parametry techniczne i materiały spełniają rygorystyczne normy jakościowe."

    sections = [
        {"label": f"{family_label}", "heading": f"{name} – wysoka jakość wykonania", "paragraphs": [p1]},
        {"label": "Właściwości i zalety", "heading": "Precyzja i niezawodność w codziennym użytkowaniu", "paragraphs": [p2]},
        {"label": "Zastosowanie", "heading": "Dopasowanie do profesjonalnych instalacji", "paragraphs": [p3]},
    ]
    benefits = frags[:4] if frags else [f"Producent: {family_label}", "Sprawdzona konstrukcja"]
    applications = ["Zgodnie ze specyfikacją producenta", "Instalacje profesjonalne i domowe"]
    checks = ["Sprawdź parametry w dokumentacji technicznej modelu"]
    notes = ["Stosuj zgodnie z zaleceniami producenta"]
    return finish(product, sections, benefits, applications, checks, notes, specs)



def electrical_socket_editorial(product: dict[str, Any]) -> dict[str, Any]:
    name = product["name"]
    code = product["code"]
    specs = public_specs(product)[:8]
    is_hermetic = "ip44" in name.lower() or "hermet" in name.lower()
    is_double = "podwójn" in name.lower() or "2x" in name.lower()
    is_surface = "n/t" in name.lower() or "natynk" in name.lower()
    mount = "natynkowy (N/T)" if is_surface else "podtynkowy (P/T)"
    type_desc = "podwójne gniazdo wtyczkowe" if is_double else "pojedyncze gniazdo wtyczkowe"
    ip_desc = "o podwyższonej klasie szczelności IP44 z klapką ochronną" if is_hermetic else "do suchych pomieszczeń wewnętrznych"

    pill1 = "Osprzęt elektroinstalacyjny"
    h1 = f"{name} – pewne zasilanie w instalacji 230V"
    p1 = f"Solidne {type_desc} z uziemieniem przeznaczone do bezpiecznego i trwałego podłączania odbiorników elektrycznych 230V. Zapewnia stabilny styk mechaniczny, wytrzymałą konstrukcję zacisków oraz estetyczny wygląd w każdym pomieszczeniu."

    pill2 = "Przeznaczenie i montaż"
    h2 = f"Montaż {mount} {ip_desc}"
    p2 = f"Produkt przystosowany do montażu {mount}. Wytrzymała obudowa z tworzywa odpornego na zarysowania i promieniowanie UV gwarantuje wieloletnią, bezawaryjną eksploatację w domach, warsztatach, biurach oraz obiektach użyteczności publicznej."

    pill3 = "Bezpieczeństwo i standard"
    h3 = f"Wykonanie z uziemieniem i zgodność z normami"
    p3 = f"Konstrukcja spełnia rygorystyczne normy bezpieczeństwa instalacji elektrycznych. Zapewnia wygodne wprowadzanie przewodów i pewne trzymanie wtyczek."

    sections = [
        {"label": pill1, "heading": h1, "paragraphs": [p1]},
        {"label": pill2, "heading": h2, "paragraphs": [p2]},
        {"label": pill3, "heading": h3, "paragraphs": [p3]},
    ]
    benefits = ["Pewne uziemienie bolcowe", f"Montaż {mount}", "Trwałe tworzywo odporne na UV", "Zgodność z normami 230V"]
    applications = ["Instalacje domowe i biurowe", "Warsztaty, garaże i strefy techniczne", "Puszki i instalacje natynkowe"]
    checks = ["Napięcie znamionowe: 230V AC", "Maksymalne obciążenie prądowe: 16A", "Przekrój podłączanych przewodów instalacyjnych"]
    notes = ["Montaż i podłączenie wykonaj przy całkowicie wyłączonym napięciu zasilania", "Stosuj przewody o odpowiednim przekroju dostosowanym do obciążenia"]
    return finish(product, sections, benefits, applications, checks, notes, specs)


def electrical_switch_editorial(product: dict[str, Any]) -> dict[str, Any]:
    name = product["name"]
    code = product["code"]
    specs = public_specs(product)[:8]
    is_double = any(k in name.lower() for k in ("podwójn", "świecznik", "dwugrup", "2-klawisz"))
    is_stair = "schodow" in name.lower()
    is_cross = "krzyżow" in name.lower()
    is_surface = "n/t" in name.lower() or "natynk" in name.lower()
    mount = "natynkowy (N/T)" if is_surface else "podtynkowy (P/T)"
    kind = "schodowy" if is_stair else "krzyżowy" if is_cross else "świecznikowy (podwójny)" if is_double else "jednobiegunowy"

    pill1 = "Łączniki i wyłączniki"
    h1 = f"{name} – komfortowe sterowanie obwodem"
    p1 = f"Precyzyjny łącznik klawiszowy typu {kind} przeznaczony do komfortowego załączania obwodów oświetleniowych i odbiorników 230V. Mechanizm o wyczuwalnym, płynnym skoku gwarantuje niezawodną pracę przez tysiące cykli przełączeń."

    pill2 = "Zastosowanie w układzie"
    h2 = f"Dedykowany do montażu {mount}"
    p2 = f"Doskonale sprawdza się w sterowaniu oświetleniem w domach, korytarzach, klatkach schodowych i obiektach komercyjnych. Zapewnia estetyczne wykończenie ściany oraz ergonomiczne użytkowanie na co dzień."

    pill3 = "Instalacja i parametry"
    h3 = f"Wygodne podłączenie i trwałe zaciski"
    p3 = f"Konstrukcja umożliwia szybkie i pewne podłączenie żył instalacyjnych. Wysokiej jakości materiał nie żółknie pod wpływem światła słonecznego."

    sections = [
        {"label": pill1, "heading": h1, "paragraphs": [p1]},
        {"label": pill2, "heading": h2, "paragraphs": [p2]},
        {"label": pill3, "heading": h3, "paragraphs": [p3]},
    ]
    benefits = [f"Typ łącznika: {kind}", f"Montaż {mount}", "Niezawodny mechanizm przełączający", "Odporność na zarysowania"]
    applications = ["Sterowanie oświetleniem 230V", "Układy schodowe i korytarzowe", "Instalacje mieszkaniowe i komercyjne"]
    checks = ["Funkcja łącznika w schemacie instalacji", "Napięcie znamionowe: 230V", "Dopuszczalne obciążenie toru prądowego"]
    notes = ["Prace montażowe prowadź wyłącznie przy odłączonym napięciu w rozdzielnicy", "Sprawdź poprawność schematu połączeń przed załączeniem bezpiecznika"]
    return finish(product, sections, benefits, applications, checks, notes, specs)


def electrical_frame_editorial(product: dict[str, Any]) -> dict[str, Any]:
    name = product["name"]
    code = product["code"]
    specs = public_specs(product)[:8]
    m_holes = re.search(r"(\d+)[-\s]*krotn|(\d+)[-\s]*moduł", name.lower())
    holes = m_holes.group(1) or m_holes.group(2) if m_holes else "1"
    color = product_color(product) or "estetyczne wykończenie"

    pill1 = "Ramki instalacyjne"
    h1 = f"{name} – eleganckie wykończenie osprzętu"
    p1 = f"Dedykowana ramka instalacyjna ({holes}-krotna) w kolorze {color}, stworzona do estetycznego maskowania i montażu modułów gniazd oraz łączników. Zapewnia idealne przyleganie do płaszczyzny ściany i spójny design całego osprzętu."

    pill2 = "Kompatybilność i aranżacja"
    h2 = f"Perfekcyjne dopasowanie do serii modułowej"
    p2 = f"Wykonana z trwałego tworzywa o wysokiej odporności na zarysowania i zabrudzenia. Pozwala na montaż w układzie pionowym lub poziomym w zależności od projektu instalacji."

    pill3 = "Wskazówki montażowe"
    h3 = f"Prosty montaż zatrzaskowy na mechanizmach"
    p3 = f"Precyzyjne zaczepy gwarantują stabilne osadzenie ramki na mostkach mechanizmów bez powstawania nieestetycznych szczelin."

    sections = [
        {"label": pill1, "heading": h1, "paragraphs": [p1]},
        {"label": pill2, "heading": h2, "paragraphs": [p2]},
        {"label": pill3, "heading": h3, "paragraphs": [p3]},
    ]
    benefits = [f"Krotność: {holes}", f"Kolor: {color}", "Montaż pionowy lub poziomy", "Odporność na odbarwienia"]
    applications = ["Maskowanie gniazd i łączników", "Wielokrotne zestawy ścienne", "Aranżacja wnętrz mieszkalnych i biurowych"]
    checks = ["Krotność ramki zgodna z liczbą puszek", "Kompatybilność z serią osprzętu"]
    notes = ["Zatrzaskuj ramkę po ostatecznym dokręceniu mechanizmów do puszek instalacyjnych"]
    return finish(product, sections, benefits, applications, checks, notes, specs)


def general_editorial(product: dict[str, Any]) -> dict[str, Any]:
    rule = classify_editorial_rule(product)
    if rule == "tape":
        return tape_editorial(product)
    if rule == "power":
        return power_editorial(product)
    if rule == "controller":
        return controller_editorial(product)
    if rule == "control_input":
        return control_input_editorial(product)
    if rule == "profile":
        return profile_editorial(product)
    if rule == "profile_cover":
        return profile_cover_editorial(product)
    if rule == "accessory":
        return accessory_editorial(product)
    if rule == "light_source":
        return light_source_editorial(product)
    if rule == "luminaire":
        return luminaire_editorial(product)
    if rule == "electrical_socket":
        return electrical_socket_editorial(product)
    if rule == "electrical_switch":
        return electrical_switch_editorial(product)
    if rule == "electrical_frame":
        return electrical_frame_editorial(product)
    return manufacturer_source_editorial(product, product.get("producer") or "Prescot")
