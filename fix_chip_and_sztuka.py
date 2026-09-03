#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
1. PR-MAD: usunięcie 'zaawansowana technologia' -> 'chip automatycznie rozpoznający napięcie'
2. Usunięcie 'sztuka instalatorska' / 'sztuką instalatorską' / 'sztuka instalatorstwa' z całej bazy
"""

import json
import re

FILES = ["./data/seo-descriptions.json", "./dist/data/seo-descriptions.json"]

def process_file(filepath):
    print(f"Przetwarzanie {filepath}...")
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    count_mad = 0
    count_sztuka = 0

    prods = data.get("products", {})
    for k, pdata in prods.items():
        s = json.dumps(pdata, ensure_ascii=False)
        orig = s

        # 1. PR-MAD zaawansowana technologia -> chip
        if "PR-MAD" in s or "Zas0004" in s or "Smart Auto" in s:
            s = s.replace("wyposażony w zaawansowaną technologię automatycznego rozpoznawania napięcia podłączonego obwodu", "wyposażony w chip automatycznie rozpoznający napięcie podłączonego obwodu")
            s = s.replace("zaawansowaną technologię automatycznego rozpoznawania", "chip automatycznie rozpoznający")
            s = s.replace("zaawansowaną technologią automatycznego rozpoznawania", "chipem automatycznie rozpoznającym")
            if s != orig:
                count_mad += 1

        # 2. Sztuka instalatorska / instalatorstwa
        if "sztuką instalatorską" in s or "sztuka instalatorstwa" in s or "sztuki instalatorskiej" in s:
            s = s.replace("Bezpieczny i prosty montaż zgodny ze sztuką instalatorską", "Bezpieczny i prosty montaż zgodny ze standardami instalacyjnymi")
            s = s.replace("zgodny ze sztuką instalatorską", "zgodny ze standardami instalacyjnymi")
            s = s.replace("zgodnie ze sztuką instalatorską", "zgodnie ze standardami instalacyjnymi")
            s = s.replace("ze sztuką instalatorską", "ze standardami instalacyjnymi")
            s = s.replace("sztuką instalatorską", "standardami instalacyjnymi")
            s = s.replace("sztuka instalatorstwa", "prawidłowy montaż")
            count_sztuka += 1

        prods[k] = json.loads(s)

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"Poprawiono {count_mad} modeli PR-MAD oraz {count_sztuka} produktów z frazą 'sztuka instalatorska' w {filepath}.")

for f in FILES:
    process_file(f)
