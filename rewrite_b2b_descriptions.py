import re
import html

with open('/Users/karolbohdanowicz/my-ai-agents/prescot/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

b2b_data = {
    "FC10-COB-RGB-TP": {
        "title1": "Szybkozłączka zasilająca do COB RGB 10mm",
        "desc1": "Profesjonalna złączka bezlutowa (Taśma-Przewód) dedykowana do 4-żyłowych taśm wielokolorowych COB o szerokości laminatu 10mm. Gwarantuje pewne wyprowadzenie zasilania bez lutowania, skracając czas pracy instalatora. Konstrukcja zębów tnących została przystosowana do pracy z ciągłą warstwą luminoforu, zapewniając bezstratny przesył sygnału.",
        "li1": "<b>Typ złącza:</b> Taśma – Przewód (wyprowadzenie zasilania / 4-pin RGB).",
        "li2": "<b>Bezpieczeństwo styku:</b> Zęby penetrujące zaprojektowane specjalnie do gęstej struktury COB.",
        "li3": "<b>Wytrzymałość:</b> Przystosowana do standardowych obciążeń prądowych taśm wielokolorowych.",
        "li4": "<b>Estetyka:</b> Transparentna obudowa z poliwęglanu (PC) nie generuje cieni wewnątrz profilu.",
        "title3": "Instalacje bezpunktowe RGB",
        "desc3": "Rekomendowana przy montażu jednolitych, wielokolorowych linii światła (COB), gdzie kluczowy jest szybki i niezawodny montaż punktów zasilania w trudno dostępnych miejscach."
    },
    "FC10-SMD-RGB-TP": {
        "title1": "Szybkozłączka zasilająca do SMD RGB 10mm",
        "desc1": "Instalacyjna złączka bezlutowa (Taśma-Przewód) do klasycznych, 4-żyłowych taśm SMD RGB o szerokości 10mm. Pozwala na błyskawiczne i solidne podłączenie odcinka taśmy do sterownika lub zasilacza. Standardowy rozstaw 4 pinów idealnie trafia w miedziane pady lutownicze taśm SMD.",
        "li1": "<b>Typ złącza:</b> Taśma – Przewód (wprowadzenie zasilania do obwodu).",
        "li2": "<b>Kompatybilność:</b> Standardowe taśmy SMD RGB 4-pinowe o szerokości laminatu 10mm.",
        "li3": "<b>Trwałość połączenia:</b> Zaciskowy mechanizm eliminujący konieczność czasochłonnego lutowania.",
        "li4": "<b>Profilowanie:</b> Niewielkie gabaryty pozwalają na ukrycie złączki w standardowych profilach aluminiowych.",
        "title3": "Podstawowe obwody wielokolorowe",
        "desc3": "Podstawowy element montażowy dla instalatorów przy sufitach podwieszanych i oświetleniu dekoracyjnym z wykorzystaniem standardowych diod SMD RGB."
    },
    "FC10-SMD-RGB-TPT": {
        "title1": "Złączka łączeniowa kątowa do SMD RGB 10mm",
        "desc1": "Złączka bezlutowa z elastycznym przewodem 4-żyłowym (Taśma-Przewód-Taśma), przeznaczona do łączenia dwóch odcinków taśm SMD RGB o szerokości 10mm. Umożliwia swobodne układanie taśmy w miejscach wymagających załamania linii bez przerywania ciągłości sygnału kolorystycznego.",
        "li1": "<b>Typ złącza:</b> Taśma – Przewód – Taśma (prosta złączka z elastycznym kablem).",
        "li2": "<b>Elastyczność:</b> Kabel pozwala na omijanie narożników, profili i tworzenie łagodnych zagięć.",
        "li3": "<b>Kompatybilność:</b> 4-pinowe taśmy SMD RGB 10mm.",
        "li4": "<b>Oszczędność czasu:</b> Błyskawiczne mostkowanie przerw instalacyjnych bez użycia lutownicy.",
        "title3": "Mostkowanie i łamanie ciągów świetlnych",
        "desc3": "Niezbędna do sprawnego prowadzenia linii światła przez narożniki 90 stopni, słupy konstrukcyjne czy zmiany płaszczyzn montażowych (np. przejścia między półkami)."
    },
    "FC10-COB-RGB-TPT": {
        "title1": "Złączka łączeniowa kątowa do COB RGB 10mm",
        "desc1": "Bezlutowa złączka z kablem (Taśma-Przewód-Taśma) zaprojektowana pod wymagania technologiczne 4-żyłowych taśm COB RGB 10mm. Zapewnia stabilne połączenie na jednorodnej warstwie luminoforu oraz swobodę zmiany kierunku prowadzenia taśmy dzięki elastycznemu łącznikowi.",
        "li1": "<b>Typ złącza:</b> Taśma – Przewód – Taśma (transmisja sygnału 4-pin RGB).",
        "li2": "<b>Technologia COB:</b> Specjalne noże stykowe dostosowane do bezinwazyjnego przebijania laminatu taśm bezpunktowych.",
        "li3": "<b>Pełna elastyczność:</b> Łącznik przewodowy umożliwia dowolne kątowanie instalacji świetlnej.",
        "li4": "<b>Estetyka:</b> Transparentna obudowa z PC minimalizuje efekt martwych punktów świetlnych.",
        "title3": "Złożone projekty architektoniczne",
        "desc3": "Dedykowana do profesjonalnych instalacji wymagających ciągłej, bezpunktowej linii światła z licznymi zakrętami – wnęki, ramy, sufity wielopoziomowe."
    },
    "FC10-SMD-RGBW-TP": {
        "title1": "Szybkozłączka zasilająca do SMD RGBW 10mm",
        "desc1": "Profesjonalna 5-pinowa złączka (Taśma-Przewód) stworzona do wielokolorowych taśm SMD z dodatkowym kanałem białym (RGBW) o szerokości 10mm. Pozwala na pewne doprowadzenie pięciu kanałów zasilania ze sterownika, z pominięciem procesu lutowania.",
        "li1": "<b>Typ złącza:</b> Taśma – Przewód (wprowadzenie 5-żyłowego zasilania).",
        "li2": "<b>Kompatybilność:</b> 5-pinowe taśmy SMD RGBW o szerokości laminatu 10mm.",
        "li3": "<b>Stabilność napięciowa:</b> Zapewnia równomierne obciążenie wszystkich 5 styków miedzianych na taśmie.",
        "li4": "<b>Szybkość montażu:</b> Drastyczna redukcja czasu w porównaniu do lutowania 5 drobnych żył prądowych.",
        "title3": "Instalacje RGBW (Multicolor + White)",
        "desc3": "Kluczowy element instalacyjny przy wdrażaniu taśm RGBW w przestrzeniach komercyjnych i domowych, zapewniający stabilne napięcie zasilacza 5-kanałowego."
    }
}

def generate_html(data):
    return f"""<section style="font-family:inherit; margin:0 0 18px 0; padding:22px 24px; background:none !important; background-color:transparent !important; border:1px solid currentColor; border-radius:12px; color:inherit;">
<span style="font-family:inherit; display:inline-block; margin-bottom:10px; padding:5px 12px; border-radius:999px; background:#e94b25 !important; background-color:#e94b25 !important; color:#ffffff !important; -webkit-text-fill-color:#ffffff !important; font-size:11px; font-weight:700; letter-spacing:.8px; text-transform:uppercase; line-height:1.2;">
<font color="#ffffff">ZŁĄCZKA LED</font>
</span>
<h3 style="font-family:inherit; margin:0 0 8px 0; background:none !important; background-color:transparent !important; color:inherit !important; font-size:22px; line-height:1.3; font-weight:700;">{data['title1']}</h3>
<p style="font-family:inherit; margin:0; background:none !important; background-color:transparent !important; color:inherit !important; opacity:.82; font-size:14px; line-height:1.65;">{data['desc1']}</p>
</section><section style="font-family:inherit; margin:0 0 18px 0; padding:22px 24px; background:none !important; background-color:transparent !important; border:1px solid currentColor; border-radius:12px; color:inherit;">
<span style="font-family:inherit; display:inline-block; margin-bottom:10px; padding:5px 12px; border-radius:999px; background:#e94b25 !important; background-color:#e94b25 !important; color:#ffffff !important; -webkit-text-fill-color:#ffffff !important; font-size:11px; font-weight:700; letter-spacing:.8px; text-transform:uppercase; line-height:1.2;">
<font color="#ffffff">KLUCZOWE CECHY</font>
</span>
<ul style="margin:0; padding-left:20px; line-height:1.6; opacity:.9;">
<li style="margin-bottom:6px;">{data['li1']}</li>
<li style="margin-bottom:6px;">{data['li2']}</li>
<li style="margin-bottom:6px;">{data['li3']}</li>
<li style="margin-bottom:6px;">{data['li4']}</li>
</ul>
</section><section style="font-family:inherit; margin:0 0 18px 0; padding:22px 24px; background:none !important; background-color:transparent !important; border:1px solid currentColor; border-radius:12px; color:inherit;">
<span style="font-family:inherit; display:inline-block; margin-bottom:10px; padding:5px 12px; border-radius:999px; background:#e94b25 !important; background-color:#e94b25 !important; color:#ffffff !important; -webkit-text-fill-color:#ffffff !important; font-size:11px; font-weight:700; letter-spacing:.8px; text-transform:uppercase; line-height:1.2;">
<font color="#ffffff">ZASTOSOWANIE</font>
</span>
<h3 style="font-family:inherit; margin:0 0 8px 0; background:none !important; background-color:transparent !important; color:inherit !important; font-size:22px; line-height:1.3; font-weight:700;">{data['title3']}</h3>
<p style="font-family:inherit; margin:0; background:none !important; background-color:transparent !important; color:inherit !important; opacity:.82; font-size:14px; line-height:1.65;">{data['desc3']}</p>
</section>"""

guides_html = """
<section style="font-family:inherit; margin:18px 0 28px 0; padding:22px 24px; background:none !important; background-color:transparent !important; border:1px solid currentColor; border-radius:12px; color:inherit;">
<div style="font-family:inherit; margin-bottom:18px; background:none !important; background-color:transparent !important; color:inherit;">
<span style="font-family:inherit; display:inline-block; margin-bottom:10px; padding:5px 12px; border-radius:999px; background:#e94b25 !important; background-color:#e94b25 !important; color:#ffffff !important; -webkit-text-fill-color:#ffffff !important; font-size:11px; font-weight:700; letter-spacing:.8px; text-transform:uppercase; line-height:1.2;">
<font color="#ffffff">POWIĄZANE PORADNIKI</font>
</span>
<h3 style="font-family:inherit; margin:0 0 8px 0; background:none !important; background-color:transparent !important; color:inherit !important; font-size:22px; line-height:1.3; font-weight:700;">Dowiedz się więcej o taśmach LED</h3>
</div>
<div style="display:grid; grid-template-columns:repeat(3, 1fr); gap:16px;">
<div style="font-family:inherit; min-height:190px; padding:18px; margin:0; background:none !important; background-color:transparent !important; border:1px solid currentColor; border-radius:12px; box-shadow:none !important; color:inherit; display:flex; flex-direction:column;">
<strong style="font-family:inherit; display:block; color:inherit !important; font-size:15px; line-height:1.35; margin-bottom:6px; font-weight:700;">Jak łączyć taśmy LED? Bezlutowe złączki vs Lutowanie</strong>
<small style="font-family:inherit; display:block; color:inherit !important; opacity:.76; font-size:12px; line-height:1.4; margin-bottom:15px;">szybkość, trwałość i koszty</small>
<a href="https://www.prescot.com.pl/pl/n/16" style="font-family:inherit; display:inline-block; min-width:142px; margin-top:auto; padding:10px 17px; border-radius:999px; background:#e94b25 !important; background-color:#e94b25 !important; color:#ffffff !important; -webkit-text-fill-color:#ffffff !important; text-decoration:none !important; text-align:center; line-height:1.2; border:0 !important; align-self:flex-start;">
<font color="#ffffff"><span style="font-family:inherit; color:#ffffff !important; -webkit-text-fill-color:#ffffff !important; text-decoration:none !important; font-weight:700; font-size:14px;">Czytaj poradnik</span></font>
</a>
</div>
<div style="font-family:inherit; min-height:190px; padding:18px; margin:0; background:none !important; background-color:transparent !important; border:1px solid currentColor; border-radius:12px; box-shadow:none !important; color:inherit; display:flex; flex-direction:column;">
<strong style="font-family:inherit; display:block; color:inherit !important; font-size:15px; line-height:1.35; margin-bottom:6px; font-weight:700;">Jak dobrać taśmę LED do mieszkania?</strong>
<small style="font-family:inherit; display:block; color:inherit !important; opacity:.76; font-size:12px; line-height:1.4; margin-bottom:15px;">barwa, moc i miejsce montażu</small>
<a href="https://www.prescot.com.pl/pl/n/12" style="font-family:inherit; display:inline-block; min-width:142px; margin-top:auto; padding:10px 17px; border-radius:999px; background:#e94b25 !important; background-color:#e94b25 !important; color:#ffffff !important; -webkit-text-fill-color:#ffffff !important; text-decoration:none !important; text-align:center; line-height:1.2; border:0 !important; align-self:flex-start;">
<font color="#ffffff"><span style="font-family:inherit; color:#ffffff !important; -webkit-text-fill-color:#ffffff !important; text-decoration:none !important; font-weight:700; font-size:14px;">Czytaj poradnik</span></font>
</a>
</div>
<div style="font-family:inherit; min-height:190px; padding:18px; margin:0; background:none !important; background-color:transparent !important; border:1px solid currentColor; border-radius:12px; box-shadow:none !important; color:inherit; display:flex; flex-direction:column;">
<strong style="font-family:inherit; display:block; color:inherit !important; font-size:15px; line-height:1.35; margin-bottom:6px; font-weight:700;">Jak dobrać profil aluminiowy do taśmy LED?</strong>
<small style="font-family:inherit; display:block; color:inherit !important; opacity:.76; font-size:12px; line-height:1.4; margin-bottom:15px;">profil, klosz, chłodzenie i estetyka linii światła</small>
<a href="https://www.prescot.com.pl/pl/n/15" style="font-family:inherit; display:inline-block; min-width:142px; margin-top:auto; padding:10px 17px; border-radius:999px; background:#e94b25 !important; background-color:#e94b25 !important; color:#ffffff !important; -webkit-text-fill-color:#ffffff !important; text-decoration:none !important; text-align:center; line-height:1.2; border:0 !important; align-self:flex-start;">
<font color="#ffffff"><span style="font-family:inherit; color:#ffffff !important; -webkit-text-fill-color:#ffffff !important; text-decoration:none !important; font-weight:700; font-size:14px;">Czytaj poradnik</span></font>
</a>
</div>
</div>
</section>
"""

# Replace descriptions in the content
for sku, data in b2b_data.items():
    new_html = generate_html(data) + "\n" + guides_html
    for platform in ['wapro', 'tim', 'allegro']:
        div_id = f'desc-view-{platform}-{sku}'
        start_tag = f'<div class="model-block" id="{div_id}">'
        start_idx = content.find(start_tag)
        if start_idx != -1:
            start_content_idx = start_idx + len(start_tag)
            
            # Find the end of the block
            i = start_content_idx
            div_count = 1
            while i < len(content):
                if content[i:i+4] == '<div':
                    div_count += 1
                    i += 4
                elif content[i:i+6] == '</div>':
                    div_count -= 1
                    if div_count == 0:
                        break
                    i += 6
                else:
                    i += 1
            end_idx = i
            content = content[:start_content_idx] + "\n" + new_html + "\n" + content[end_idx:]
            
            # Update textarea
            ta_id = f'textarea-{platform}-{sku}'
            ta_start_tag = f'<textarea class="edit-textarea" id="{ta_id}" oninput="onDescriptionInput(\'{platform}\', \'zlaczki\', \'{sku}\')">'
            ta_start = content.find(ta_start_tag)
            if ta_start != -1:
                ta_content_start = ta_start + len(ta_start_tag)
                ta_end = content.find('</textarea>', ta_content_start)
                if ta_end != -1:
                    escaped_html = html.escape(new_html)
                    content = content[:ta_content_start] + escaped_html + content[ta_end:]

with open('/Users/karolbohdanowicz/my-ai-agents/prescot/index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("B2B rewrite applied!")
