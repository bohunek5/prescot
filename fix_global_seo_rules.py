#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Globalny skrypt naprawiający opisy zgodnie z wytycznymi Karola:
1. Usunięcie 'producenta' / 'Prescot' przy gwarancji - tylko 'X lat', 'X lat gwarancji', 'objęty X-letnią gwarancją'.
2. Usunięcie 'Przed zakupem porównaj indeks handlowy i parametry techniczne z dokumentacją producenta'.
3. Usunięcie wzmianek o RGBW w pilotach/sterownikach czysto RGB (żadnego RGB/RGBW).
4. Usunięcie generatywnego bloku 'Dlaczego warto:'.
"""

import json
import re

SEO_PATH = "./data/seo-descriptions.json"
SEO_DIST_PATH = "./dist/data/seo-descriptions.json"

def clean_warranty_text(text):
    if not isinstance(text, str):
        return text
    
    # 7-letnią gwarancją producenta -> 7-letnią gwarancją
    text = re.sub(r'(\d+[- ]letni[ąaeym]|roczn[ąaeym])\s+gwarancj[ąaęi]\s+(?:producenta|prescot)', r'\1 gwarancją', text, flags=re.IGNORECASE)
    text = re.sub(r'(\d+\s+lat(?:a)?)\s+gwarancj[iia]\s+(?:producenta|prescot)', r'\1 gwarancji', text, flags=re.IGNORECASE)
    text = re.sub(r'gwarancj[ąaęi]\s+(?:producenta|prescot)(?:\s+door[- ]to[- ]door)?', r'gwarancją', text, flags=re.IGNORECASE)
    text = re.sub(r'gwarancja\s+(?:producenta|prescot)(?:\s+door[- ]to[- ]door)?', r'gwarancja', text, flags=re.IGNORECASE)
    text = re.sub(r'gwarancji\s+(?:producenta|prescot)(?:\s+door[- ]to[- ]door)?', r'gwarancji', text, flags=re.IGNORECASE)
    text = re.sub(r'Gwarancja producenta:\s*', r'Gwarancja: ', text, flags=re.IGNORECASE)
    text = re.sub(r'gwarancją Prescot Premium', r'gwarancją', text, flags=re.IGNORECASE)
    text = re.sub(r'prescot\s+producenta', r'Prescot', text, flags=re.IGNORECASE)
    
    # Usunięcie 'Przed zakupem porównaj indeks handlowy...'
    text = re.sub(r'<li>\s*Przed zakupem porównaj indeks handlowy[^<]*</li>', '', text, flags=re.IGNORECASE)
    text = re.sub(r'Przed zakupem porównaj indeks handlowy[^\n.]*[.]?', '', text, flags=re.IGNORECASE)
    
    return text

def clean_rgb_text(text):
    if not isinstance(text, str):
        return text
    # Wymiana RGB/RGBW na RGB
    text = re.sub(r'RGB\s*/\s*RGBW', 'RGB', text)
    text = re.sub(r'RGB\s+i\s+RGBW', 'RGB', text)
    text = re.sub(r'RGB,\s*RGBW', 'RGB', text)
    text = re.sub(r'wielokolorowych\s+RGB/RGBW', 'wielokolorowych RGB', text)
    text = re.sub(r'taśmami\s+wielokolorowych\s+RGB', 'taśmami wielokolorowymi RGB', text)
    text = re.sub(r'RGBW', 'RGB', text)
    return text

def clean_structure(val, is_pure_rgb=False):
    if isinstance(val, str):
        val = clean_warranty_text(val)
        if is_pure_rgb:
            val = clean_rgb_text(val)
        return val
    elif isinstance(val, list):
        cleaned_list = []
        for item in val:
            # Usunięcie pozycji porównaj indeks handlowy
            if isinstance(item, str) and 'porównaj indeks handlowy' in item.lower():
                continue
            cleaned_list.append(clean_structure(item, is_pure_rgb))
        return cleaned_list
    elif isinstance(val, dict):
        # Usuń pole benefits (Dlaczego warto) jeśli to generatywny śmieć
        return {k: clean_structure(v, is_pure_rgb) for k, v in val.items()}
    return val

def process_file(filepath):
    print(f"Przetwarzanie {filepath}...")
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    prods = data.get("products", {})
    fixed_rgb = 0
    fixed_warranty = 0

    for k, v in prods.items():
        ed = v.get("editorial", {})
        title = ed.get("seo_title", "") or ed.get("title", "")
        t_low = title.lower()
        
        # Czy produkt to czysty pilot/sterownik RGB?
        is_pure_rgb = (
            ('pilot' in t_low or 'sterownik' in t_low or 'kontroler' in t_low or 'wzmacniacz' in t_low)
            and 'rgb' in t_low
            and 'rgbw' not in t_low
            and 'cct' not in t_low
            and 'rgbww' not in t_low
        )
        
        if is_pure_rgb:
            fixed_rgb += 1
            
        prods[k] = clean_structure(v, is_pure_rgb)

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"Zapisano {filepath}. Czyste RGB: {fixed_rgb}")

if __name__ == "__main__":
    process_file(SEO_PATH)
    process_file(SEO_DIST_PATH)
