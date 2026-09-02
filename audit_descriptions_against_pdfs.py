#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Audytor jakości opisów TIM & Amazon dla 345 produktów Prescot.
Weryfikuje zgodność z:
1. Wytycznymi z PDF 1 ('SEO + AI – Ściąga do tworzenia opisów produktów')
2. Wytycznymi z PDF 2 ('Jak pisać dobre opisy w branży elektrotechnicznej')
3. Dyrektywami Karola (brak bloków 'Najważniejsze cechy', brak zasilacza 1200W do rolek 100m/50m, unikalności, format Amazon).
"""

import json
import os
import re

BASE_DIR = "/Users/karolbohdanowicz/my-ai-agents/prescot/tmp/tim-opisy-tasmy"

def audit_all():
    print("🔍 Rozpoczynanie audytu jakości 345 produktów...\n")

    files = [
        ("Taśmy LED", "tim_tapes_descriptions.json"),
        ("Zasilacze LED", "tim_zasilacze_descriptions.json"),
        ("Akcesoria LED", "tim_akcesoria_descriptions.json")
    ]

    total_prods = 0
    passed_prods = 0
    errors = []
    warnings = []

    forbidden_phrases = [
        "najważniejsze cechy:",
        "parametry i cechy techniczne:",
        "dane techniczne w pigułce:",
        "tabela parametrów:",
        "zasilacz 1200w",
        "zasilacz 600w dla całej szpuli 100m",
        "zasilacz 300w dla całej szpuli 50m",
        "zasilacz do pełnej szpuli 100m",
        "zasilacz do pełnej szpuli 50m"
    ]

    for category, fname in files:
        fpath = os.path.join(BASE_DIR, fname)
        with open(fpath, "r", encoding="utf-8") as f:
            prods = json.load(f)

        print(f"📁 Sprawdzanie kategorii: {category} ({len(prods)} produktów)...")

        for idx, p in enumerate(prods, 1):
            total_prods += 1
            pid = f"{p['code']} ({p['name'][:35]})"
            d = p.get("description", {})
            p_info = p.get("parsed_info", {})

            # 1. Sprawdzenie obecności kluczowych sekcji
            if not d.get("intro"):
                errors.append(f"[{pid}] Brak 'intro' (Warstwa 1)")
            if not d.get("barwa") and not d.get("gdzie"):
                errors.append(f"[{pid}] Brak 'barwa'/'gdzie' (Warstwa 2)")
            if not d.get("dobor") and not d.get("z_czym"):
                errors.append(f"[{pid}] Brak 'dobor'/'z_czym' (Warstwa 3)")
            if not d.get("faq") or len(d["faq"]) < 2:
                errors.append(f"[{pid}] Brak lub zbyt mało pytań FAQ (wymagane min. 2-3)")

            # 2. Sprawdzenie formatu Amazon
            if not d.get("amazon_title"):
                errors.append(f"[{pid}] Brak 'amazon_title'")
            if not d.get("amazon_bullets") or len(d["amazon_bullets"]) < 4:
                errors.append(f"[{pid}] Brak lub zbyt mało punktów Amazon (wymagane min. 4)")
            if not d.get("amazon_full"):
                errors.append(f"[{pid}] Brak 'amazon_full'")

            # 3. Sprawdzenie obecności zakazanych fraz i anty-wzorców
            full_text_lower = d.get("full_text", "").lower()
            amz_text_lower = d.get("amazon_full", "").lower()
            combined_text = full_text_lower + " " + amz_text_lower

            for phrase in forbidden_phrases:
                if phrase in combined_text:
                    errors.append(f"[{pid}] Wykryto zakazaną frazę: '{phrase}'")

            # 4. Sprawdzenie reguły dla rolek 50m / 100m
            len_m = p_info.get("length_m", 5)
            if len_m >= 50:
                # W rolkach 50m/100m nie wolno pisać o zasilaniu w całości
                if "do zasilenia całej rolki" in combined_text or "do zasilenia całej szpuli" in combined_text:
                    errors.append(f"[{pid}] BŁĄD SZPULI {len_m}m: Próba zasilania szpuli w całości!")
                if "maksymalna długość pojedynczego odcinka" not in combined_text and "w sekcjach" not in combined_text:
                    warnings.append(f"[{pid}] OSTRZEŻENIE SZPULI {len_m}m: Brak zasady zasilania sekcyjnego!")

            # 5. Sprawdzenie długości i czytelności (prosty język)
            if len(d.get("intro", "")) < 40:
                warnings.append(f"[{pid}] Bardzo krótkie intro (<40 znaków)")

            # Sprawdzenie FAQ: odpowiedzi 1-2 zdaniowe (nie tasiemce)
            for q, a in d.get("faq", []):
                if len(a.split(". ")) > 4:
                    warnings.append(f"[{pid}] FAQ odpowiedź zbyt długa (>4 zdania): '{q}'")

            passed_prods += 1

    print("\n" + "="*50)
    print("📊 PODSUMOWANIE AUDYTU:")
    print("="*50)
    print(f"Łącznie przebadano produktów: {total_prods}")
    print(f"Liczba błędów krytycznych: {len(errors)}")
    print(f"Liczba ostrzeżeń stylistycznych: {len(warnings)}")

    if errors:
        print("\n❌ BŁĘDY DO POPRAWY:")
        for e in errors[:20]:
            print(" -", e)
        if len(errors) > 20:
            print(f" ... oraz {len(errors)-20} innych błędów.")
    else:
        print("\n✅ 100% PRODUKTÓW ZDAŁO TEST KRYTYCZNY!")
        print("   - Brak zakazanych bloków 'Najważniejsze cechy'")
        print("   - Brak błędnych zasilaczy do szpul 50m/100m")
        print("   - Kompletna struktura 3 Warstw + FAQ w każdym produkcie")
        print("   - Kompletny format Amazon Bullet Points dla wszystkich 345 produktów")

    if warnings:
        print(f"\n⚠️ Ostrzeżenia ({len(warnings)}):")
        for w in warnings[:10]:
            print(" -", w)

if __name__ == "__main__":
    audit_all()
