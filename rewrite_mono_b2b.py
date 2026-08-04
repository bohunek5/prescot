import re
import html

with open('/Users/karolbohdanowicz/my-ai-agents/prescot/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

def generate_b2b_mono(width):
    return {
        f"FC{width}-MONO-MULTI": {
            "title1": f"Złączka przedłużająca do COB/SMD MONO {width}mm",
            "desc1": f"Bezlutowa złączka prosta (Taśma-Taśma) dedykowana do 2-żyłowych taśm jednokolorowych COB i SMD o szerokości laminatu {width}mm. Pozwala na szybkie i bezstratne łączenie dwóch odcinków taśmy w jedną ciągłą linię światła. Kompatybilność z obiema technologiami (MULTI) czyni ją uniwersalnym rozwiązaniem dla instalatorów.",
            "li1": "<b>Typ złącza:</b> Taśma – Taśma (połączenie proste 2-pin).",
            "li2": "<b>Uniwersalność MULTI:</b> Ostrza stykowe gwarantujące bezpieczne wpięcie zarówno do taśm SMD, jak i gęstego luminoforu COB.",
            "li3": "<b>Bezawaryjność:</b> Solidny mechanizm zaciskowy zapobiega luzowaniu się styków taśm w czasie.",
            "li4": "<b>Estetyka:</b> Przezroczysta obudowa, która eliminuje cienie i mieści się w standardowych profilach aluminiowych.",
            "title3": "Budowa ciągłych linii świetlnych",
            "desc3": "Idealna do łączenia długich obiegów jednokolorowych (MONO) z taśm, bez konieczności zabierania na montaż stacji lutowniczej."
        },
        f"FC{width}-MONO-MULTI-L": {
            "title1": f"Złączka kątowa L do COB/SMD MONO {width}mm",
            "desc1": f"Sztywny łącznik bezlutowy typu L (Taśma-Taśma), umożliwiający prowadzenie jednokolorowych taśm 2-pinowych COB i SMD ({width}mm) pod kątem prostym. Eliminuje ryzyko mechanicznego uszkodzenia laminatu przy zaginaniu taśmy, zachowując przy tym niezawodną ciągłość prądową obwodu.",
            "li1": "<b>Typ złącza:</b> Kątowa \"L\" Taśma – Taśma (2-pin).",
            "li2": "<b>Ochrona taśmy:</b> Pozwala na bezinwazyjne łamanie obwodu światła w narożnikach 90 stopni.",
            "li3": "<b>Uniwersalność MULTI:</b> Dedykowana do taśm MONO zarówno z diodami SMD, jak i nowocześniejszych COB.",
            "li4": "<b>Szybkość aplikacji:</b> Błyskawiczny, pewny zacisk szczypcami na dwóch końcach laminatu.",
            "title3": "Narożniki i wnęki ścienne",
            "desc3": "Niezbędna do precyzyjnego rozprowadzenia światła jednokolorowego wokół luster, mebli oraz we wnękach sufitów podwieszanych w geometrycznych układach."
        },
        f"FC{width}-MONO-MULTI-T": {
            "title1": f"Złączka typu T (Trójnik) do COB/SMD MONO {width}mm",
            "desc1": f"Instalacyjna złączka rozgałęźna w kształcie litery T. Pozwala na rozdzielenie zasilania taśmy 2-żyłowej ({width}mm MONO) na dwa niezależne kierunki pod kątem prostym, co skutecznie redukuje ilość potrzebnych przewodów, lutowań i długich obwodów. Kompatybilna z serią COB oraz tradycyjnym SMD.",
            "li1": "<b>Typ złącza:</b> Rozgałęziacz \"T\" Taśma – Taśma – Taśma (2-pin).",
            "li2": "<b>Uniwersalność MULTI:</b> Ostre styki przygotowane na laminat {width}mm taśm COB i SMD.",
            "li3": "<b>Funkcjonalność:</b> Rozdział głównej linii światła bez skomplikowanego drutowania węzłów prądowych.",
            "li4": "<b>Solidny docisk:</b> Poliwęglanowy zatrzask trzymający taśmę zapobiega spadkom napięcia na rozgałęzieniu.",
            "title3": "Rozbudowane sieci oświetleniowe",
            "desc3": "Używana głównie w skomplikowanych formach meblowych i kasetonach, gdzie z jednego punktu światło musi rozejść się w dwóch przeciwnych kierunkach jednocześnie."
        },
        f"FC{width}-MONO-MULTI-TP": {
            "title1": f"Szybkozłączka zasilająca do COB/SMD MONO {width}mm",
            "desc1": f"Profesjonalna złączka zasilająca (Taśma-Przewód) dla 2-pinowych taśm jednokolorowych (COB/SMD) o szerokości {width}mm. Gwarantuje mocne, odporne na drgania wyprowadzenie zasilania ze sterownika/zasilacza prosto do taśmy LED, skracając czas robocizny instalatora o 30% względem tradycyjnego lutowania.",
            "li1": "<b>Typ złącza:</b> Taśma – Przewód (wprowadzenie 2-żyłowego zasilania +/-).",
            "li2": "<b>Uniwersalność MULTI:</b> Zęby przebijające przystosowane do bezpiecznej penetracji taśm gęstych COB oraz klasycznych SMD.",
            "li3": "<b>Oszczędność czasu:</b> Proces zaciśnięcia złączki szczypcami i wpięcia kabla skraca proces podłączania prądu na obiekcie.",
            "li4": "<b>Kompaktowość:</b> Transparentna i zwarta konstrukcja świetnie chowa się w aluminiowych profilach oświetleniowych.",
            "title3": "Główne punkty wprowadzania zasilania",
            "desc3": "Stosowana przez zawodowych instalatorów jako początkowe i fundamentalne doprowadzenie napięcia do poszczególnych obwodów świetlnych MONO."
        },
        f"FC{width}-MONO-MULTI-TPT": {
            "title1": f"Złączka łączeniowa kątowa do COB/SMD MONO {width}mm",
            "desc1": f"Instalacyjna złączka bezlutowa z elastycznym kablem (Taśma-Przewód-Taśma) dla taśm {width}mm MONO. Stworzona do mostkowania dwóch odcinków taśm w miejscach z ciasnymi załamaniami, przeszkodami architektonicznymi, lub przy przechodzeniu obwodem między dwoma osobnymi profilami.",
            "li1": "<b>Typ złącza:</b> Taśma – Przewód – Taśma (połączenie 2-pin z giętkim mostkiem kablowym).",
            "li2": "<b>Elastyczne mostkowanie:</b> Zintegrowany przewód izolowany zdejmuje z instalatora wymóg lutowania w trudnodostępnych miejscach.",
            "li3": "<b>Uniwersalność MULTI:</b> Technologia docisku nożowego poprawnie styka się z pinami w COB i SMD {width}mm.",
            "li4": "<b>Szybkość realizacji:</b> Bezproblemowe omijanie filarów, wsporników i ostrych narożników ściennych.",
            "title3": "Przejścia i omijanie przeszkód architektonicznych",
            "desc3": "Niezastąpiona przy budowie wnękowych linii LED załamujących się na słupach, zmianach płaszczyzn montażowych i zaoblonych fragmentach zabudowy g-k."
        },
        f"FC{width}-MONO-MULTI-9IN1": {
            "title1": f"Multi-zestaw instalacyjny 9w1 do COB/SMD MONO {width}mm",
            "desc1": f"Kompletny, profesjonalny pakiet złączeniowy (9w1) dla instalacji taśm 2-żyłowych o szerokości {width}mm. Zestaw pozwala na modułowe tworzenie dowolnego złącza bezpośrednio u klienta. Można z niego stworzyć złączki typu TT, TP, TPT, a nawet rozgałęźniki bez potrzeby posiadania lutownicy.",
            "li1": "<b>Wielozadaniowość:</b> Jeden system zatrzasków umożliwia zrobienie prostej przedłużki, kątownika, czy kabla zasilającego na wymiar.",
            "li2": "<b>Modułowość:</b> Błyskawiczna wymiana terminali dociskowych na odcinki elastyczne pozwala dopasować instalację pod kątem.",
            "li3": "<b>Uniwersalność MULTI:</b> Zęby wpinające są kompatybilne krzyżowo dla najnowszych diod COB i sprawdzonych SMD {width}mm.",
            "li4": "<b>Zarządzanie materiałem:</b> Typowy 'Szwajcarski scyzoryk' eliminujący przestoje z powodu braku specyficznego typu złączki na placu budowy.",
            "title3": "Dynamiczne instalacje komercyjne",
            "desc3": "Produkt typu 'must-have' w walizce instalatora. Idealnie sprawdza się podczas dynamicznych zmian w planie oświetleniowym, oszczędzając czas i koszty logistyczne."
        }
    }

b2b_data = {}
b2b_data.update(generate_b2b_mono(8))
b2b_data.update(generate_b2b_mono(10))

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

print("B2B mono rewrite applied!")
