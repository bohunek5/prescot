"""Add the Hippo-M Max connectors to every sales-channel panel.

The script is intentionally idempotent. It removes any earlier versions of the
four cards (including the broken Gemini markup) and then appends one canonical
card to each connector panel.
"""

from __future__ import annotations

import argparse
import html
import re
from pathlib import Path


INDEX_PATH = Path(__file__).with_name("index.html")
PLATFORMS = ("shoper", "tim", "allegro", "wapro")
START_INDEX = 23
EXPECTED_CONNECTOR_COUNT = 26

SECTION_STYLE = (
    "font-family:inherit; margin:0 0 18px 0; padding:22px 24px; "
    "background:none !important; background-color:transparent !important; "
    "border:1px solid currentColor; border-radius:12px; color:inherit;"
)
TAG_STYLE = (
    "font-family:inherit; display:inline-block; margin-bottom:10px; "
    "padding:5px 12px; border-radius:999px; background:#e94b25 !important; "
    "background-color:#e94b25 !important; color:#ffffff !important; "
    "-webkit-text-fill-color:#ffffff !important; font-size:11px; "
    "font-weight:700; letter-spacing:.8px; text-transform:uppercase; line-height:1.2;"
)
MUTED_TAG_STYLE = TAG_STYLE.replace("#e94b25", "#475569")
HEADING_STYLE = (
    "font-family:inherit; margin:0 0 8px 0; color:inherit !important; "
    "font-size:22px; line-height:1.3; font-weight:700;"
)
PARAGRAPH_STYLE = (
    "font-family:inherit; margin:0; color:inherit !important; opacity:.84; "
    "font-size:14px; line-height:1.65;"
)


PRODUCTS = (
    {
        "sku": "FC8-COB-MONO-TP-NW",
        "ean": "5905475368424",
        "badge": "Hippo-M Max – 8mm, taśma–przewód, 4A",
        "name": "Złączka Hippo-M Max do taśmy LED SMD/COB MONO 8mm – taśma–przewód, 4A",
        "type": "taśma–przewód",
        "current": "4A",
        "wire": "własny przewód",
        "summary": (
            "Złączka 2-pin do wyprowadzenia zasilania z taśmy jednobarwnej SMD lub COB "
            "o szerokości 8mm. Przewód dobiera i przycina instalator; połączenie nie wymaga lutowania."
        ),
        "use": (
            "Do zasilania początku odcinka taśmy oraz do wykonywania przewodu o długości "
            "dopasowanej do miejsca montażu."
        ),
        "selection": (
            "Sprawdź szerokość PCB 8mm, układ MONO 2-pin i obciążenie obwodu do 4A. "
            "Dobierz przekrój przewodu do prądu oraz długości połączenia."
        ),
        "mounting": (
            "Wsuń taśmę i przewód do oporu, zachowaj polaryzację +/−, a następnie zamknij "
            "zatrzask równomiernym dociskiem. Przed uruchomieniem sprawdź, czy styki trzymają oba elementy."
        ),
        "benefits": (
            "połączenie taśmy z przewodem bez lutowania",
            "przewód docinany do potrzeb instalacji",
            "zgodność z taśmami MONO SMD i COB o szerokości 8mm",
            "obciążalność do 4A",
        ),
    },
    {
        "sku": "FC8-COB-MONO-TT-L",
        "ean": "5905475368417",
        "badge": "Hippo-M Max – 8mm, narożna L, 4A",
        "name": "Złączka narożna Hippo-M Max do taśmy LED SMD/COB MONO 8mm – taśma–taśma, 4A",
        "type": "taśma–taśma, narożna L",
        "current": "4A",
        "wire": "bez przewodu",
        "summary": (
            "Złączka 2-pin do połączenia dwóch odcinków taśmy jednobarwnej SMD lub COB "
            "o szerokości 8mm pod kątem 90°. Połączenie nie wymaga lutowania."
        ),
        "use": (
            "Do narożników mebli, półek, wnęk i profili, gdy taśmy nie należy zaginać "
            "bezpośrednio na laminacie."
        ),
        "selection": (
            "Sprawdź szerokość PCB 8mm, układ MONO 2-pin, kierunek narożnika oraz "
            "obciążenie obwodu do 4A."
        ),
        "mounting": (
            "Wsuń oba odcinki równo do oporu i dopasuj + do + oraz − do −. Zamknij oba "
            "zatrzaski równomiernym dociskiem, bez zginania laminatu przy obudowie."
        ),
        "benefits": (
            "połączenie dwóch taśm pod kątem 90° bez lutowania",
            "brak konieczności zaginania laminatu w narożniku",
            "zgodność z taśmami MONO SMD i COB o szerokości 8mm",
            "obciążalność do 4A",
        ),
    },
    {
        "sku": "FC8-COB-MONO-TT",
        "ean": "5905475368400",
        "badge": "Hippo-M Max – 8mm, prosta, 4A",
        "name": "Złączka prosta Hippo-M Max do taśmy LED SMD/COB MONO 8mm – taśma–taśma, 4A",
        "type": "taśma–taśma, prosta",
        "current": "4A",
        "wire": "bez przewodu",
        "summary": (
            "Złączka 2-pin do połączenia dwóch odcinków taśmy jednobarwnej SMD lub COB "
            "o szerokości 8mm w jednej linii. Połączenie nie wymaga lutowania."
        ),
        "use": (
            "Do przedłużania prostych odcinków i wykorzystania dociętych fragmentów taśmy "
            "w profilach, meblach oraz zabudowie."
        ),
        "selection": (
            "Sprawdź szerokość PCB 8mm, układ MONO 2-pin oraz obciążenie obwodu do 4A. "
            "Oba odcinki muszą mieć pola stykowe dostępne w miejscu cięcia."
        ),
        "mounting": (
            "Wsuń oba odcinki do oporu, zachowując polaryzację. Zamknij zatrzaski równomiernym "
            "dociskiem i sprawdź ciągłość połączenia przed umieszczeniem taśmy w profilu."
        ),
        "benefits": (
            "proste połączenie dwóch odcinków bez lutowania",
            "możliwość wykorzystania dociętych fragmentów taśmy",
            "zgodność z taśmami MONO SMD i COB o szerokości 8mm",
            "obciążalność do 4A",
        ),
    },
    {
        "sku": "FC8-COB-MONO-TP",
        "ean": "5905475368394",
        "badge": "Hippo-M Max – 8mm, przewód 15cm, 5A",
        "name": "Złączka Hippo-M Max do taśmy LED SMD/COB MONO 8mm – przewód 15cm, 5A",
        "type": "taśma–przewód",
        "current": "5A",
        "wire": "przewód 15cm",
        "summary": (
            "Złączka 2-pin do wyprowadzenia zasilania z taśmy jednobarwnej SMD lub COB "
            "o szerokości 8mm. Ma zamontowany przewód o długości 15cm i nie wymaga lutowania po stronie taśmy."
        ),
        "use": (
            "Do podłączenia początku odcinka taśmy do zasilacza, sterownika albo przewodu "
            "instalacyjnego, gdy wystarcza gotowe wyprowadzenie 15cm."
        ),
        "selection": (
            "Sprawdź szerokość PCB 8mm, układ MONO 2-pin, długość przewodu 15cm oraz "
            "obciążenie obwodu do 5A."
        ),
        "mounting": (
            "Wsuń taśmę do oporu, zachowaj polaryzację +/− i zamknij zatrzask równomiernym "
            "dociskiem. Drugi koniec przewodu podłącz zgodnie ze schematem instalacji."
        ),
        "benefits": (
            "gotowy przewód 15cm",
            "połączenie z taśmą bez lutowania",
            "zgodność z taśmami MONO SMD i COB o szerokości 8mm",
            "obciążalność do 5A",
        ),
    },
)


def styled_section(tag: str, heading: str, body: str, *, muted: bool = False) -> str:
    tag_style = MUTED_TAG_STYLE if muted else TAG_STYLE
    return f'''<section style="{SECTION_STYLE}">
<span style="{tag_style}"><font color="#ffffff">{tag}</font></span>
<h3 style="{HEADING_STYLE}">{heading}</h3>
<p style="{PARAGRAPH_STYLE}">{body}</p>
</section>'''


def parameter_grid(product: dict[str, object]) -> str:
    values = (
        ("System", "MONO, 2-pin"),
        ("Szerokość taśmy", "8mm"),
        ("Typ połączenia", str(product["type"])),
        ("Prąd maksymalny", str(product["current"])),
        ("Przewód", str(product["wire"])),
        ("Kod produktu", str(product["sku"])),
    )
    cells = "".join(
        f'''<div style="display:flex; flex-direction:column; min-width:0; word-break:break-word;">
<span style="font-size:12px; color:#64748b; margin-bottom:4px; text-transform:uppercase; letter-spacing:.5px;">{label}</span>
<span style="font-size:15px; font-weight:700; color:inherit;">{value}</span>
</div>'''
        for label, value in values
    )
    return f'''<section class="product-parameters-section" style="{SECTION_STYLE}">
<span style="{MUTED_TAG_STYLE}"><font color="#ffffff">Parametry</font></span>
<div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(150px, 1fr)); gap:16px; margin-top:6px;">{cells}</div>
</section>'''


def blog_section() -> str:
    articles = (
        ("Jak czytać parametry taśmy LED?", "moc, lumeny, CRI, napięcie i IP", "https://www.prescot.com.pl/pl/n/23"),
        ("Montaż taśmy LED na zewnątrz", "IP, uszczelnienie i ochrona połączeń", "https://www.prescot.com.pl/pl/n/16"),
        ("Jak dobrać taśmę LED do mieszkania?", "barwa, moc i miejsce montażu", "https://www.prescot.com.pl/pl/n/12"),
        ("Jak dobrać profil aluminiowy do taśmy LED?", "profil, klosz, chłodzenie i montaż", "https://www.prescot.com.pl/pl/n/15"),
    )
    cards = "".join(
        f'''<div style="font-family:inherit; padding:18px; margin:0; background:none !important; background-color:transparent !important; border:1px solid currentColor; border-radius:12px; box-shadow:none !important; color:inherit;">
<strong style="font-family:inherit; display:block; color:inherit !important; font-size:15px; line-height:1.35; margin-bottom:6px; font-weight:700;">{title}</strong>
<small style="font-family:inherit; display:block; color:inherit !important; opacity:.76; font-size:12px; line-height:1.4; margin-bottom:15px;">{lead}</small>
<a href="{url}" style="font-family:inherit; display:inline-block; min-width:142px; padding:10px 17px; border-radius:999px; background:#e94b25 !important; background-color:#e94b25 !important; color:#ffffff !important; -webkit-text-fill-color:#ffffff !important; text-decoration:none !important; text-align:center; line-height:1.2; border:0 !important;"><font color="#ffffff"><span style="font-family:inherit; color:#ffffff !important; -webkit-text-fill-color:#ffffff !important; text-decoration:none !important; font-weight:700; font-size:14px;">Czytaj poradnik</span></font></a>
</div>'''
        for title, lead, url in articles
    )
    return f'''<section style="font-family:inherit; margin:0 0 28px 0; padding:24px; background:none !important; background-color:transparent !important; border:1px solid currentColor; border-radius:12px; color:inherit;">
<div style="font-family:inherit; margin-bottom:22px; background:none !important; background-color:transparent !important; color:inherit;">
<span style="{TAG_STYLE}"><font color="#ffffff">Praktyczne poradniki</font></span>
<h3 style="font-family:inherit; margin:0 0 8px 0; color:inherit !important; font-size:24px; line-height:1.25; font-weight:700;">Dobierz i zamontuj elementy instalacji</h3>
<p style="{PARAGRAPH_STYLE}">Materiały o doborze taśmy, profilu oraz zabezpieczeniu połączeń.</p>
</div>
<div style="font-family:inherit; display:grid; grid-template-columns:repeat(auto-fit, minmax(230px, 1fr)); gap:14px; background:none !important; background-color:transparent !important; color:inherit;">{cards}</div>
</section>'''


def shoper_description(product: dict[str, object]) -> str:
    benefits = "\n".join(f"<p>- {item}</p>" for item in product["benefits"])
    return f'''<section>
<h2>{product["name"]}</h2>
<p>{product["summary"]}</p>
<h3>Najważniejsze cechy</h3>
{benefits}
<h3>Zastosowanie</h3>
<p>{product["use"]}</p>
<h3>Parametry</h3>
<p>- System: MONO, 2-pin</p>
<p>- Szerokość taśmy: 8mm</p>
<p>- Typ połączenia: {product["type"]}</p>
<p>- Prąd maksymalny: {product["current"]}</p>
<p>- Przewód: {product["wire"]}</p>
<p>- Kod produktu: {product["sku"]}</p>
<h3>Montaż</h3>
<p>{product["mounting"]}</p>
</section>'''


def tim_description(product: dict[str, object]) -> str:
    return "\n".join(
        (
            styled_section(
                "Opis techniczny",
                f'{product["sku"]} - złączka Hippo-M Max do taśmy LED 8mm',
                f'<strong>{product["sku"]}</strong> — {product["summary"]}',
            ),
            styled_section(
                "Dobór do instalacji",
                f'{product["type"]} dla systemu MONO',
                str(product["selection"]),
            ),
            styled_section(
                "Parametry do zamówienia",
                f'Co sprawdzić przed zakupem modelu {product["sku"]}',
                f'Typ połączenia: <strong>{product["type"]}</strong>. Przewód: <strong>{product["wire"]}</strong>. '
                f'Prąd maksymalny: <strong>{product["current"]}</strong>.',
            ),
            parameter_grid(product),
            styled_section(
                "Uwagi montażowe",
                "Kontrola przed uruchomieniem",
                str(product["mounting"]),
                muted=True,
            ),
        )
    )


def allegro_description(product: dict[str, object]) -> str:
    checks = "<br/>".join(f'✓ {item}' for item in product["benefits"])
    return "\n".join(
        (
            styled_section(
                "Gotowy do montażu",
                str(product["name"]),
                str(product["summary"]),
            ),
            styled_section(
                "Najważniejsze cechy",
                "Co otrzymujesz",
                checks,
            ),
            styled_section(
                "Dobór bez pomyłki",
                f'Gdzie użyć modelu {product["sku"]}',
                f'{product["use"]} {product["selection"]}',
            ),
            parameter_grid(product),
            styled_section(
                "Przed zakupem",
                "Sprawdź pola stykowe i polaryzację",
                str(product["mounting"]),
                muted=True,
            ),
        )
    )


def wapro_description(product: dict[str, object]) -> str:
    features = "\n".join(
        f'<li style="font-family:inherit; margin-bottom:6px;">{item}.</li>'
        for item in product["benefits"]
    )
    features_section = f'''<section style="{SECTION_STYLE}">
<span style="{TAG_STYLE}"><font color="#ffffff">Kluczowe cechy</font></span>
<ul style="font-family:inherit; margin:0; padding:0 0 0 20px; color:inherit !important; opacity:.84; font-size:14px; line-height:1.65;">{features}</ul>
</section>'''
    return "\n".join(
        (
            styled_section(
                "Złączka LED Hippo-M Max",
                str(product["name"]),
                str(product["summary"]),
            ),
            features_section,
            styled_section("Zastosowanie", str(product["type"]), str(product["use"])),
            blog_section(),
        )
    )


DESCRIPTION_BUILDERS = {
    "shoper": shoper_description,
    "tim": tim_description,
    "allegro": allegro_description,
    "wapro": wapro_description,
}


def build_accordion(product: dict[str, object], index: int, platform: str) -> str:
    sku = str(product["sku"])
    ean = str(product["ean"])
    description = DESCRIPTION_BUILDERS[platform](product)
    escaped_description = html.escape(description, quote=False)
    return f'''<div class="product-accordion" data-model="{sku}">
<button class="product-trigger" onclick="toggleProduct(this)">
<div class="product-info">
<span class="product-model">{index}. {sku}</span>
<span class="product-label-badge">{product["badge"]}</span>
</div>
<span class="product-arrow">▼</span>
</button>
<div class="product-body">
<div class="model-block" id="desc-view-{platform}-{sku}">
{description}
</div>
<div class="edit-block" id="desc-edit-{platform}-{sku}" style="display: none;">
<textarea class="edit-textarea" id="textarea-{platform}-{sku}" oninput="onDescriptionInput('{platform}', 'zlaczki', '{sku}')">{escaped_description}</textarea>
</div>
<div class="product-controls">
<button class="control-btn btn-edit" id="btn-edit-{platform}-{sku}" onclick="toggleEdit('{platform}', 'zlaczki', '{sku}')">Edytuj opis</button>
<button class="control-btn btn-save" id="btn-save-{platform}-{sku}" onclick="saveDescription('{platform}', 'zlaczki', '{sku}')" style="display: none;">Zapisz opis</button>
<button class="control-btn btn-copy" onclick="copyDescriptionHtml('{platform}', '{sku}', this)" style="border-color: #f59e0b; color: #f59e0b;" title="Kopiuj opis HTML">Kopiuj opis HTML</button>
<button class="control-btn btn-ean" onclick="navigator.clipboard.writeText('{ean}'); this.innerText='Skopiowano!'; setTimeout(()=&gt;this.innerText='EAN: {ean}', 2000);" style="border-color: #0ea5e9; color: #0ea5e9;" title="Skopiuj EAN">EAN: {ean}</button>
<span class="control-status" id="status-{platform}-{sku}"></span>
</div></div>
</div>'''


def matching_div_end(source: str, start: int) -> int:
    """Return the end offset just after the div opened at *start*."""
    if not source.startswith("<div", start):
        raise ValueError(f"Expected <div at offset {start}")
    depth = 0
    for match in re.finditer(r"<div\b|</div\s*>", source[start:], flags=re.IGNORECASE):
        token = match.group(0).lower()
        depth += -1 if token.startswith("</") else 1
        if depth == 0:
            return start + match.end()
    raise ValueError(f"Unclosed div at offset {start}")


def remove_existing_cards(source: str) -> str:
    for product in PRODUCTS:
        marker = f'<div class="product-accordion" data-model="{product["sku"]}">'
        while True:
            start = source.find(marker)
            if start == -1:
                break
            end = matching_div_end(source, start)
            while start > 0 and source[start - 1] == "\n":
                start -= 1
            while end < len(source) and source[end] == "\n":
                end += 1
            source = source[:start] + source[end:]
    return source


def panel_bounds(source: str, platform: str) -> tuple[int, int]:
    marker = f'<div class="sub-tab-panel" id="{platform}-zlaczki">'
    start = source.find(marker)
    if start == -1:
        raise ValueError(f"Missing connector panel for {platform}")
    return start, matching_div_end(source, start)


def card_count(source: str, platform: str) -> int:
    start, end = panel_bounds(source, platform)
    return source[start:end].count('<div class="product-accordion"')


def update_html(source: str) -> str:
    source = remove_existing_cards(source)

    for platform in PLATFORMS:
        existing_count = card_count(source, platform)
        if existing_count != START_INDEX - 1:
            raise ValueError(
                f"Expected {START_INDEX - 1} existing cards in {platform}-zlaczki, found {existing_count}"
            )
        _, panel_end = panel_bounds(source, platform)
        cards = "\n".join(
            build_accordion(product, START_INDEX + offset, platform)
            for offset, product in enumerate(PRODUCTS)
        )
        closing_div_start = source.rfind("</div>", 0, panel_end)
        prefix = source[:closing_div_start].rstrip("\n")
        source = prefix + "\n" + cards + "\n" + source[closing_div_start:]

    source, replacements = re.subn(
        r"Złączki i rozdzielacze LED \(\d+\)",
        f"Złączki i rozdzielacze LED ({EXPECTED_CONNECTOR_COUNT})",
        source,
    )
    if replacements != len(PLATFORMS):
        raise ValueError(f"Expected {len(PLATFORMS)} connector counters, updated {replacements}")
    return source


def validate(source: str) -> list[str]:
    errors: list[str] = []
    if "toggleAccordion" in source or 'class="accordion-header"' in source:
        errors.append("legacy Gemini accordion markup is still present")

    for platform in PLATFORMS:
        try:
            count = card_count(source, platform)
        except ValueError as exc:
            errors.append(str(exc))
            continue
        if count != EXPECTED_CONNECTOR_COUNT:
            errors.append(f"{platform}-zlaczki contains {count} cards, expected {EXPECTED_CONNECTOR_COUNT}")
        for product in PRODUCTS:
            sku = str(product["sku"])
            checks = (
                f'id="desc-view-{platform}-{sku}"',
                f'id="textarea-{platform}-{sku}"',
                f"toggleEdit('{platform}', 'zlaczki', '{sku}')",
                f"copyDescriptionHtml('{platform}', '{sku}', this)",
                f"navigator.clipboard.writeText('{product['ean']}')",
                f">EAN: {product['ean']}</button>",
            )
            start, end = panel_bounds(source, platform)
            panel = source[start:end]
            for check in checks:
                if panel.count(check) != 1:
                    errors.append(f"{platform}/{sku}: expected one {check!r}")

    for product in PRODUCTS:
        sku = str(product["sku"])
        expected_occurrences = len(PLATFORMS)
        actual = source.count(f'<div class="product-accordion" data-model="{sku}">')
        if actual != expected_occurrences:
            errors.append(f"{sku}: found {actual} cards, expected {expected_occurrences}")

    expected_counter = f"Złączki i rozdzielacze LED ({EXPECTED_CONNECTOR_COUNT})"
    if source.count(expected_counter) != len(PLATFORMS):
        errors.append("connector counters are not consistent")
    return errors


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="validate index.html without changing it")
    args = parser.parse_args()

    source = INDEX_PATH.read_text(encoding="utf-8")
    if not args.check:
        source = update_html(source)
        INDEX_PATH.write_text(source, encoding="utf-8")

    errors = validate(source)
    if errors:
        raise SystemExit("\n".join(f"ERROR: {error}" for error in errors))
    print("Hippo-M Max cards: OK (4 products × 4 platforms, 26 connector cards per panel)")


if __name__ == "__main__":
    main()
