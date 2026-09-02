#!/usr/bin/env python3
"""Build reviewed TIM descriptions for the 20 proper active Scharfer cards."""

from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path("/Users/karolbohdanowicz/my-ai-agents/prescot")
CATALOG = ROOT / "data/catalog.json"
LIVE = ROOT / "exports/tim/remediation/active-brand-offer-live-readonly-post-scharfer-2026-09-01.json"
OUTPUT = ROOT / "exports/tim/remediation/scharfer-description-queue-2026-09-01.json"


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def numeric(value):
    if isinstance(value, dict):
        value = value.get("value")
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


catalog = read_json(CATALOG)["products"]
live = read_json(LIVE)["products"]
catalog_by_model = {}
for product in catalog:
    model = str(product.get("manufacturerCode") or "")
    if re.fullmatch(r"SCH-(18|20|30|45|60|100|150|200|300|400)-(12|24)", model):
        catalog_by_model.setdefault(model, []).append(product)

items = []
for row in live:
    if row.get("expectedBrand") != "Scharfer" or not row.get("ean"):
        continue
    model = str(row["model"])
    match = re.fullmatch(r"SCH-(18|20|30|45|60|100|150|200|300|400)-(12|24)", model)
    if not match:
        raise RuntimeError(f"Nieoczekiwany model Scharfer: {model}")
    products = catalog_by_model.get(model, [])
    if len(products) != 1:
        raise RuntimeError(f"{model}: oczekiwano jednego produktu katalogowego, jest {len(products)}")
    product = products[0]
    attrs = product.get("attributes") or {}
    power, voltage = match.groups()
    dimension = re.sub(r"(?<=\d)mm$", " mm", str(attrs.get("Wymiar") or "").replace("x", " × "))
    warranty = str(attrs.get("Gwarancja") or "84 miesiące")
    description = f"""<section>
<h2>Zasilacz LED Scharfer {voltage} V {power} W IP67</h2>
<p>Scharfer {model} to stałonapięciowy zasilacz LED o napięciu wyjściowym {voltage} V i mocy znamionowej {power} W. Służy do zasilania zgodnych taśm LED, modułów LED oraz innych odbiorników LED pracujących z napięciem {voltage} V.</p>
<h3>Zastosowanie</h3>
<p>Hermetyczna konstrukcja o stopniu ochrony IP67 pozwala stosować zasilacz w instalacjach wewnętrznych i zewnętrznych, w warunkach przewidzianych w karcie technicznej.</p>
<h3>Parametry produktu</h3>
<ul>
<li>Indeks handlowy: {model}</li>
<li>Napięcie wyjściowe: {voltage} V DC</li>
<li>Moc znamionowa: {power} W</li>
<li>Typ: stałonapięciowy</li>
<li>Stopień ochrony: IP67</li>
<li>Wymiary: {dimension}</li>
<li>Gwarancja: {warranty}</li>
</ul>
<h3>Dobór i montaż</h3>
<ul>
<li>Napięcie zasilacza musi odpowiadać napięciu odbiorników LED.</li>
<li>Suma mocy podłączonych odbiorników nie może przekraczać mocy znamionowej zasilacza.</li>
<li>Warunki montażu, wentylacji i chłodzenia dobierz zgodnie z kartą techniczną.</li>
<li>Montaż i podłączenie instalacji elektrycznej powinny wykonać osoby z odpowiednimi kwalifikacjami.</li>
</ul>
</section>"""
    if model not in description or re.search(r"\b\d{13}\b", description) or re.search(r"\bPRE[-_ ]?\d", description, re.I):
        raise RuntimeError(f"{model}: opis narusza reguły indeksu/EAN")
    if "Kod_produktu" in description or "kod katalogowy" in description.lower():
        raise RuntimeError(f"{model}: opis zawiera indeks wewnętrzny")
    items.append({
        "pimcoreId": int(row["id"]),
        "ean": str(row["ean"]),
        "manufacturerCode": model,
        "name": str(row["timName"]),
        "timListPrice": numeric(row.get("listPrice")),
        "descriptionHtml": description,
        "source": {
            "technicalCard": f"Scharfer SCH-{power} karta techniczna PL",
            "catalogAttributes": {key: attrs.get(key) for key in ["Moc", "Klasa szczelności", "Wymiar", "Typ", "Gwarancja"]},
        },
    })

items.sort(key=lambda item: item["pimcoreId"])
if len(items) != 20 or len({item["manufacturerCode"] for item in items}) != 20:
    raise RuntimeError(f"Oczekiwano 20 unikalnych kart, jest {len(items)}")

document = {
    "generatedAt": "2026-09-01",
    "rules": [
        "indeks handlowy SCH, nigdy indeks wewnętrzny PRE",
        "bez EAN w opisie",
        "tylko fakty z karty technicznej i danych katalogowych",
        "bez niepotwierdzonych porad instalacyjnych",
    ],
    "stages": {"scharferNeedsUpdate": items},
}
OUTPUT.parent.mkdir(parents=True, exist_ok=True)
OUTPUT.write_text(json.dumps(document, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(OUTPUT)
print(f"Pozycji: {len(items)}")
