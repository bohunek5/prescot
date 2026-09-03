#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Usuwa całkowicie określenia 'ciepła / ciepłe / ciepły' w odniesieniu do barwy żółtej i pomarańczowej / bursztynowej.
Żółty i pomarańczowy to barwy monochromatyczne, a nie biel ciepła!
"""

import json
import re

FILES = ["./data/seo-descriptions.json", "./dist/data/seo-descriptions.json"]

def clean_entry(data):
    # Serializuj do stringa i zamień niepożądane frazy
    s = json.dumps(data, ensure_ascii=False)

    # 1. Nagłówki i opisy żółtej
    s = s.replace("Ciepłe oświetlenie dekoracyjne w barwie żółtej", "Efektowne oświetlenie dekoracyjne w barwie żółtej")
    s = s.replace("Żółta (ciepłe światło akcentowe)", "Żółta")
    s = s.replace("ciepłym, słonecznym świetle o wyrazistej żółtej tonacji", "nasyconym świetle o wyrazistej żółtej barwie")
    s = s.replace("ciepłe, słoneczne światło o wyrazistej żółtej tonacji", "nasycone światło o wyrazistej żółtej barwie")
    s = s.replace("ciepły akcent kolorystyczny", "wyrazisty akcent kolorystyczny")

    # 2. Nagłówki i opisy pomarańczowej / bursztynowej
    s = s.replace("Nastrojowe oświetlenie w barwie bursztynowej", "Klimatyczne oświetlenie w barwie pomarańczowej")
    s = s.replace("Bursztynowa (klimatyczne światło bursztynowe)", "Pomarańczowa")
    s = s.replace("miękkim, ciepłym świetle bursztynowym sprzyjającym wyciszeniu", "głębokim, nasyconym świetle pomarańczowym")
    s = s.replace("ciepłym świetle bursztynowym", "nasyconym świetle pomarańczowym")
    s = s.replace("ciepłe światło bursztynowe", "nasycone światło pomarańczowe")

    # 3. Dodatkowe zabezpieczenia fraz
    s = re.sub(r'w barwie Żółta \(ciepłe światło akcentowe\)', 'w barwie żółtej', s)
    s = re.sub(r'w barwie Bursztynowa \(klimatyczne światło bursztynowe\)', 'w barwie pomarańczowej', s)

    return json.loads(s)

for path in FILES:
    print(f"Przetwarzanie {path}...")
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    cleaned = clean_entry(data)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(cleaned, f, indent=2, ensure_ascii=False)

    print(f"Poprawiono {path}.")
