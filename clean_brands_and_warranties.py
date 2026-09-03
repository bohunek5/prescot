#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Skrypt czyszczący zgodnie z najnowszymi wytycznymi Karola:
1. Gwarancje: usunięcie WSZELKICH nawiasów (np. '(seria Prescot Standard)', '(seria Prescot Premium)', itp.) - sama liczba lat!
2. Marka: ZAKAZ pisania "Produkt marki X" dla kogokolwiek.
   Dozwolone marki w opisach:
   - Taśmy LED: Prescot
   - Schärfer: Schärfer
   - MiLight / MiBoxer: MiBoxer / MiLight
   - KLUŚ: KLUŚ
   - Sterowniki Prescot: TYLKO jeśli kod zaczyna się od PR-
   - Zasilacze Prescot: TYLKO jeśli kod zaczyna się od PR-, IP-, PD-, PG-
   Wszystkie inne produkty: BEZ MARKI (żadnego Prescot, żadnego MeanWell, itp. - "inne nie są moje").
"""

import json
import re

SEO_PATH = "./data/seo-descriptions.json"
SEO_DIST_PATH = "./dist/data/seo-descriptions.json"
CAT_PATH = "./data/catalog.json"

with open(CAT_PATH, "r", encoding="utf-8") as f:
    cat_products = json.load(f).get("products", [])

# Mapuj produkty po key, ean, code
cat_by_key = {}
for p in cat_products:
    if p.get("key"):
        cat_by_key[p["key"]] = p
    if p.get("ean"):
        cat_by_key[f"ean:{p['ean']}"] = p
        cat_by_key[p["ean"]] = p
    if p.get("code"):
        cat_by_key[f"code:{p['code']}"] = p
        cat_by_key[p["code"]] = p

def get_allowed_brand(product):
    if not product:
        return None
    name = str(product.get("name", "")).lower()
    code = str(product.get("code", "")).upper()
    mfg = str(product.get("manufacturerCode", "")).upper()
    root = str(product.get("categoryRoot", "")).lower()
    cat_str = str(product.get("category", "")).lower()

    # 1. Schärfer
    if "schärfer" in name or "scharfer" in name or mfg.startswith("SCH-") or code.startswith("SCH-"):
        return "Schärfer"
    # 2. MiLight / MiBoxer
    if "miboxer" in name or "milight" in name or "mi-light" in name or mfg.startswith("FUT") or mfg.startswith("LS"):
        return "MiBoxer"
    # 3. KLUŚ
    if "kluś" in name or "klus" in name or mfg.startswith("KLU-") or code.startswith("KLU-") or "kluś" in cat_str:
        return "KLUŚ"
    # 4. Taśmy LED - Prescot
    if "taśmy led" in root or "taśma" in name or "tasma" in name:
        return "Prescot"
    # 5. Sterowniki Prescot: TYLKO PR-
    if "sterowniki led" in root or "sterownik" in name or "pilot" in name or "kontroler" in name:
        if mfg.startswith("PR-") or code.startswith("PR-") or "pr-" in name:
            return "Prescot"
        return None
    # 6. Zasilacze Prescot: TYLKO PR-, IP-, PD-, PG-
    if "zasilacze led" in root or "zasilacz" in name:
        if any(mfg.startswith(p) or code.startswith(p) for p in ["PR-", "IP-", "PD-", "PG-"]):
            return "Prescot"
        if any(p in name for p in ["pr-mad", "pr-", "ip-"]):
            return "Prescot"
        return None
    return None

def clean_value(text, allowed_brand):
    if not isinstance(text, str):
        return text

    # 1. Wywal nawiasy przy gwarancjach - tylko sama liczba lat!
    # np. gwarancją: 2 lata (seria Prescot Standard) -> gwarancją: 2 lata
    text = re.sub(r'(gwarancj[a-ząćęłńóśźż]*:\s*\d+\s+lat(?:a)?)\s*\([^)]*\)', r'\1', text, flags=re.IGNORECASE)
    text = re.sub(r'(\d+[- ]letni[ąaeym]\s+gwarancj[ąaęi])\s*\([^)]*\)', r'\1', text, flags=re.IGNORECASE)
    text = re.sub(r'(\d+\s+lat(?:a)?\s+gwarancj[iia])\s*\([^)]*\)', r'\1', text, flags=re.IGNORECASE)
    text = re.sub(r'gwarancja:\s*(\d+\s+lat(?:a)?)\s*\([^)]*\)', r'Gwarancja: \1', text, flags=re.IGNORECASE)
    # wyczyść sam nawias (seria Prescot Standard) jeśli został
    text = re.sub(r'\s*\(\s*(?:seria\s+Prescot\s+(?:Standard|Premium|Delux)|seria\s+Schärfer|producenta)[^)]*\)', '', text, flags=re.IGNORECASE)

    # 2. Wywal 'Produkt marki X to' -> 'Profesjonalny...' lub wyczyść
    text = re.sub(r'Produkt\s+marki\s+[A-Za-z0-9_/.-]+\s+to\s+profesjonalny', 'Profesjonalny', text, flags=re.IGNORECASE)
    text = re.sub(r'Produkt\s+marki\s+[A-Za-z0-9_/.-]+\s+to\s+', '', text, flags=re.IGNORECASE)
    text = re.sub(r'Produkt\s+marki\s+[A-Za-z0-9_/.-]+', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\bmarki\s+[A-Za-z0-9_/.-]+\b', '', text, flags=re.IGNORECASE)

    # 3. Jeśli produkt to NIE Prescot, usuń wszelkie przypisania Prescot!
    if allowed_brand != "Prescot":
        text = re.sub(r'\bPrescot\s+LED\b', 'LED', text, flags=re.IGNORECASE)
        text = re.sub(r'\bLED\s+Prescot\b', 'LED', text, flags=re.IGNORECASE)
        text = re.sub(r'\bPrescot\b', '', text, flags=re.IGNORECASE)

    # 4. Czysta gwarancja - żadnego 'producenta' ani 'Prescot'
    text = re.sub(r'gwarancj[ąaęi]\s+(?:producenta|prescot)', 'gwarancją', text, flags=re.IGNORECASE)
    text = re.sub(r'gwarancja\s+(?:producenta|prescot)', 'gwarancja', text, flags=re.IGNORECASE)
    text = re.sub(r'gwarancji\s+(?:producenta|prescot)', 'gwarancji', text, flags=re.IGNORECASE)
    text = re.sub(r'Gwarancja producenta:\s*', 'Gwarancja: ', text, flags=re.IGNORECASE)

    # 5. Podwójne spacje
    text = re.sub(r'[ \t]{2,}', ' ', text)
    return text.strip()

def clean_data_structure(data, allowed_brand):
    if isinstance(data, str):
        return clean_value(data, allowed_brand)
    elif isinstance(data, list):
        return [clean_data_structure(item, allowed_brand) for item in data]
    elif isinstance(data, dict):
        return {k: clean_data_structure(v, allowed_brand) for k, v in data.items()}
    return data

def process_file(filepath):
    print(f"Czyszczenie {filepath}...")
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    prods = data.get("products", {})
    cleaned_count = 0
    non_prescot_cleaned = 0

    for k, v in prods.items():
        cat_p = cat_by_key.get(k)
        if not cat_p and ":" in k:
            cat_p = cat_by_key.get(k.split(":", 1)[1])
        allowed = get_allowed_brand(cat_p)
        if allowed != "Prescot":
            non_prescot_cleaned += 1
        prods[k] = clean_data_structure(v, allowed)
        cleaned_count += 1

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"Zapisano {filepath}. Łącznie produktów: {cleaned_count}, produkty bez marki Prescot: {non_prescot_cleaned}")

if __name__ == "__main__":
    process_file(SEO_PATH)
    process_file(SEO_DIST_PATH)
