#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Karol nakazał: w opisach shoper wyjeb te podstawowe parametry (cały ten blok globalnie)
Czyści bloki parametrów ze wszystkich manual overrides dla Shopera.
"""

import json
import re

FILES = ["./data/manual-overrides.json", "./dist/data/manual-overrides.json"]

def process_file(filepath):
    print(f"Przetwarzanie {filepath}...")
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    shoper_hashes = set()
    for p_key, b in data.get("products", {}).items():
        if "shoper" in b:
            shoper_hashes.add(b["shoper"])

    count = 0
    descs = data.get("descriptions", {})
    for h in shoper_hashes:
        text = descs.get(h, "")
        orig = text

        # 1. Usuń całe sekcje z parametrami
        text = re.sub(r'<section[^>]*>(?:(?!</section>)[\s\S])*?(?:Parametry modelu|Kluczowe parametry|Najważniejsze parametry|Parametry techniczne|Dokładne parametry)[\s\S]*?</section>', '', text, flags=re.IGNORECASE)

        # 2. Usuń nagłówki i bloki parametrów
        text = re.sub(r'<h[234][^>]*>(?:Najważniejsze\s+|Dokładne\s+|Kluczowe\s+)?parametry(?:\s+techniczne|\s+modelu|\s+do\s+zamówienia)?:?</h[234]>[\s\S]*?(?=<h[1-4]|</section>|$)', '', text, flags=re.IGNORECASE)
        text = re.sub(r'<p><strong>(?:Dokładne\s+|Kluczowe\s+)?parametry:?</strong>[\s\S]*?(?=<h[1-4]|</section>|$)', '', text, flags=re.IGNORECASE)
        text = re.sub(r'<p>Dostępne parametry:?[\s\S]*?(?=<h[1-4]|</section>|$)', '', text, flags=re.IGNORECASE)

        # Wyczyść ewentualne puste sekcje
        text = re.sub(r'<section[^>]*>\s*</section>', '', text)

        if text != orig:
            descs[h] = text.strip()
            count += 1

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"Wyczyszczono bloki parametrów z {count} opisów Shoper w {filepath}.")

for f in FILES:
    process_file(f)
