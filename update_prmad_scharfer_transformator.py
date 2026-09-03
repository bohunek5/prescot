#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Aktualizuje opisy PR-MAD (6 modeli) oraz Schärfer (20 modeli):
Zgodnie z poleceniem Karola:
'w pr mad jak piszesz transformator napisz: zasilacz LED ( "transformator" ) w scharfer tez 20 modeli scharfer i 5 madó∑'
"""

import json

FILES = ["./data/seo-descriptions.json", "./dist/data/seo-descriptions.json"]

def replace_in_obj(obj, is_mad, is_sch):
    if isinstance(obj, str):
        val = obj
        if is_mad:
            val = val.replace("to transformator wyposażony", 'to zasilacz LED ("transformator") wyposażony')
            val = val.replace("to transformator", 'to zasilacz LED ("transformator")')
        if is_sch:
            val = val.replace("to bezkompromisowy transformator impulsowy", 'to bezkompromisowy zasilacz LED ("transformator")')
            val = val.replace("to transformator impulsowy", 'to zasilacz LED ("transformator")')
            val = val.replace("to transformator", 'to zasilacz LED ("transformator")')
            val = val.replace("transformator impulsowy", 'zasilacz LED ("transformator")')
        return val
    elif isinstance(obj, list):
        return [replace_in_obj(item, is_mad, is_sch) for item in obj]
    elif isinstance(obj, dict):
        return {k: replace_in_obj(v, is_mad, is_sch) for k, v in obj.items()}
    return obj

def process_file(filepath):
    print(f"Aktualizacja {filepath}...")
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    prods = data.get("products", {})
    count_mad = 0
    count_sch = 0

    for key, pdata in prods.items():
        title = pdata.get("editorial", {}).get("seo_title", "")
        p_str = json.dumps(pdata, ensure_ascii=False)

        is_mad = "PR-MAD" in title or "Smart Auto" in p_str or "Zas0004" in p_str
        is_sch = "Schärfer" in title or "Scharfer" in title or any(f"Zas0000{i}" in p_str for i in range(62, 80)) or "Zas00024" in p_str

        if is_mad:
            prods[key] = replace_in_obj(pdata, True, False)
            count_mad += 1
        elif is_sch:
            prods[key] = replace_in_obj(pdata, False, True)
            count_sch += 1

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"Zaktualizowano {count_mad} modeli PR-MAD oraz {count_sch} modeli Schärfer w {filepath}.")

for f in FILES:
    process_file(f)
