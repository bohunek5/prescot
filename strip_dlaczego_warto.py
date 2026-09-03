#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Globalne usunięcie wszelkich sekcji, bloków i wzmianek 'Dlaczego warto' z manual-overrides.json oraz baz danych.
"""

import json
import re

OV_PATH = "./data/manual-overrides.json"
OV_DIST_PATH = "./dist/data/manual-overrides.json"

def remove_dlaczego_warto(html):
    if not isinstance(html, str):
        return html
    
    # 1. Usunięcie całej sekcji zawierającej 'Dlaczego warto'
    html = re.sub(r'<section[^>]*>(?:(?!</section>)[\s\S])*?Dlaczego warto[\s\S]*?</section>', '', html, flags=re.IGNORECASE)
    
    # 2. Usunięcie nagłówka <h3>Dlaczego warto:?</h3> i treści do następnego nagłówka lub końca
    html = re.sub(r'<h3[^>]*>\s*Dlaczego warto:?\s*</h3>[\s\S]*?(?=<h[1-4]|</section>|$)', '', html, flags=re.IGNORECASE)

    # 3. Usunięcie nagłówka 'Najważniejsze korzyści tego wariantu'
    html = re.sub(r'<h3[^>]*>\s*Najważniejsze korzyści tego wariantu\s*</h3>[\s\S]*?(?=<h[1-4]|</section>|$)', '', html, flags=re.IGNORECASE)

    # 4. Usunięcie jakichkolwiek spanów/divów z 'Dlaczego warto'
    html = re.sub(r'<span[^>]*>[^<]*Dlaczego warto[^<]*</span>', '', html, flags=re.IGNORECASE)
    html = re.sub(r'<font[^>]*>[^<]*Dlaczego warto[^<]*</font>', '', html, flags=re.IGNORECASE)

    # 5. Usunięcie pustych linii i nadmiarowych przerw
    html = re.sub(r'\n{3,}', '\n\n', html)
    return html.strip()

def process_overrides(filepath):
    print(f"Czyszczenie {filepath} z 'Dlaczego warto'...")
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    descs = data.get("descriptions", {})
    cleaned = 0
    for k, v in descs.items():
        if "dlaczego warto" in str(v).lower():
            descs[k] = remove_dlaczego_warto(v)
            cleaned += 1

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"Zaktualizowano {cleaned} wpisów w {filepath}.")

if __name__ == "__main__":
    process_overrides(OV_PATH)
    process_overrides(OV_DIST_PATH)
