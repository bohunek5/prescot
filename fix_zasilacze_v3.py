import re

html_path = '/Users/karolbohdanowicz/my-ai-agents/prescot/index.html'
with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

models_data = {
    'PR-MAD36-1224': {'power': 36, 'safe': 28, 't96': 'ok. 3 metry', 't48': 'ok. 6 metrów', 'dim': '145 × 50 × 29 mm'},
    'PR-MAD60-1224': {'power': 60, 'safe': 48, 't96': 'ok. 5 metrów', 't48': 'ok. 10 metrów', 'dim': '145 × 50 × 29 mm'},
    'PR-MAD100-1224': {'power': 100, 'safe': 80, 't96': 'ok. 8 metrów', 't48': 'ok. 16 metrów', 'dim': '176 × 50 × 29 mm'},
    'PR-MAD150-1224': {'power': 150, 'safe': 120, 't96': 'ok. 12 metrów', 't48': 'ok. 25 metrów', 'dim': '199 × 50 × 29 mm'},
    'PR-MAD200-1224': {'power': 200, 'safe': 160, 't96': 'ok. 16 metrów', 't48': 'ok. 33 metry', 'dim': '218 × 50 × 29 mm'},
    'PR-MAD300-1224': {'power': 300, 'safe': 240, 't96': 'ok. 25 metrów', 't48': 'ok. 50 metrów', 'dim': '240 × 50 × 29 mm'},
}

def escape_html_for_textarea(h):
    return h.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

def get_blogs_html(bg_color):
    return f"""<section style="font-family: inherit; margin: 18px 0 0 0; padding: 22px 24px; background: none !important; background-color: transparent !important; border: 1px solid currentColor; border-radius: 12px; color: inherit;">
<div style="font-family: inherit; margin-bottom: 18px; background: none !important; background-color: transparent !important; color: inherit;">
<span style="font-family: inherit; display: inline-block; margin-bottom: 10px; padding: 5px 12px; border-radius: 999px; background: {bg_color} !important; background-color: {bg_color} !important; color: #ffffff !important; -webkit-text-fill-color: #ffffff !important; font-size: 11px; font-weight: bold; letter-spacing: .8px; text-transform: uppercase; line-height: 1.2;">
<span style="color: #ffffff;">Praktyczne poradniki</span>
</span>
<h3 style="font-family: inherit; margin: 0 0 8px 0; background: none !important; background-color: transparent !important; color: inherit !important; font-size: 22px; line-height: 1.3; font-weight: bold;">Dobierz zasilacz LED bez zgadywania</h3>
<p style="font-family: inherit; margin: 0; background: none !important; background-color: transparent !important; color: inherit !important; opacity: .78; font-size: 14px; line-height: 1.6;">Sprawdź krótkie poradniki, które pomogą dobrać moc, typ obudowy, napięcie i stopień ochrony IP do konkretnej instalacji LED.</p>
</div>
<div style="font-family: inherit; display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 14px; background: none !important; background-color: transparent !important; color: inherit; align-items: stretch;">
<div style="font-family: inherit; min-height: 190px; padding: 18px; margin: 0; background: none !important; background-color: transparent !important; border: 1px solid currentColor; border-radius: 12px; box-shadow: none !important; color: inherit; display: flex; flex-direction: column;">
<strong style="font-family: inherit; display: block; color: inherit !important; font-size: 15px; line-height: 1.35; margin-bottom: 6px; font-weight: bold;">Do czego służą zasilacze LED?</strong>
<small style="font-family: inherit; display: block; color: inherit !important; opacity: .76; font-size: 12px; line-height: 1.4; margin-bottom: 15px;">taśmy LED, moduły LED i sterowniki</small>
<a href="https://www.prescot.com.pl/pl/n/26" style="font-family: inherit; display: inline-block; min-width: 142px; margin-top: auto; padding: 10px 17px; border-radius: 999px; background: {bg_color} !important; background-color: {bg_color} !important; color: #ffffff !important; -webkit-text-fill-color: #ffffff !important; text-decoration: none !important; text-align: center; line-height: 1.2; border: 0 !important; align-self: flex-start;">
<span style="color: #ffffff;"><span style="font-family: inherit; color: #ffffff !important; -webkit-text-fill-color: #ffffff !important; text-decoration: none !important; font-weight: bold; font-size: 14px;">Czytaj poradnik</span></span>
</a>
</div>
<div style="font-family: inherit; min-height: 190px; padding: 18px; margin: 0; background: none !important; background-color: transparent !important; border: 1px solid currentColor; border-radius: 12px; box-shadow: none !important; color: inherit; display: flex; flex-direction: column;">
<strong style="font-family: inherit; display: block; color: inherit !important; font-size: 15px; line-height: 1.35; margin-bottom: 6px; font-weight: bold;">Zasilacze LED - gdzie użyć którego?</strong>
<small style="font-family: inherit; display: block; color: inherit !important; opacity: .76; font-size: 12px; line-height: 1.4; margin-bottom: 15px;">desktop, gniazdkowy, siatkowy, slim i hermetyczny</small>
<a href="https://www.prescot.com.pl/pl/n/25" style="font-family: inherit; display: inline-block; min-width: 142px; margin-top: auto; padding: 10px 17px; border-radius: 999px; background: {bg_color} !important; background-color: {bg_color} !important; color: #ffffff !important; -webkit-text-fill-color: #ffffff !important; text-decoration: none !important; text-align: center; line-height: 1.2; border: 0 !important; align-self: flex-start;">
<span style="color: #ffffff;"><span style="font-family: inherit; color: #ffffff !important; -webkit-text-fill-color: #ffffff !important; text-decoration: none !important; font-weight: bold; font-size: 14px;">Czytaj poradnik</span></span>
</a>
</div>
<div style="font-family: inherit; min-height: 190px; padding: 18px; margin: 0; background: none !important; background-color: transparent !important; border: 1px solid currentColor; border-radius: 12px; box-shadow: none !important; color: inherit; display: flex; flex-direction: column;">
<strong style="font-family: inherit; display: block; color: inherit !important; font-size: 15px; line-height: 1.35; margin-bottom: 6px; font-weight: bold;">Jak dobrać zasilacz LED do taśmy?</strong>
<small style="font-family: inherit; display: block; color: inherit !important; opacity: .76; font-size: 12px; line-height: 1.4; margin-bottom: 15px;">moc W/m, długość taśmy i zapas mocy</small>
<a href="https://www.prescot.com.pl/pl/n/24" style="font-family: inherit; display: inline-block; min-width: 142px; margin-top: auto; padding: 10px 17px; border-radius: 999px; background: {bg_color} !important; background-color: {bg_color} !important; color: #ffffff !important; -webkit-text-fill-color: #ffffff !important; text-decoration: none !important; text-align: center; line-height: 1.2; border: 0 !important; align-self: flex-start;">
<span style="color: #ffffff;"><span style="font-family: inherit; color: #ffffff !important; -webkit-text-fill-color: #ffffff !important; text-decoration: none !important; font-weight: bold; font-size: 14px;">Czytaj poradnik</span></span>
</a>
</div>
</div>
</section>"""

def build_styled_html(model, data, bg_color, title_prefix, subtitle):
    p = data['power']
    s = data['safe']
    t96 = data['t96']
    t48 = data['t48']
    dim = data['dim']
    
    return f"""<section style="font-family: inherit; margin: 28px 0 18px 0; padding: 22px 24px; background: none !important; background-color: transparent !important; border: 1px solid currentColor; border-radius: 12px; color: inherit;">
<span style="font-family: inherit; display: inline-block; margin-bottom: 10px; padding: 5px 12px; border-radius: 999px; background: {bg_color} !important; background-color: {bg_color} !important; color: #ffffff !important; -webkit-text-fill-color: #ffffff !important; font-size: 11px; font-weight: bold; letter-spacing: .8px; text-transform: uppercase; line-height: 1.2;">
<span style="color: #ffffff;">{title_prefix}</span>
</span>
<h3 style="font-family: inherit; margin: 0 0 8px 0; background: none !important; background-color: transparent !important; color: inherit !important; font-size: 22px; line-height: 1.3; font-weight: bold;">{subtitle}</h3>
<p style="font-family: inherit; margin: 0; background: none !important; background-color: transparent !important; color: inherit !important; opacity: .82; font-size: 14px; line-height: 1.65;">Zasilacz <strong style="color: inherit;">{model}</strong> to innowacyjne urządzenie o mocy <strong style="color: inherit;">{p}W</strong>, wyposażone w genialną funkcję <strong style="color: inherit;">Smart Auto</strong> (cud auto-identyfikacji). Moduł samodzielnie detektuje i dostosowuje napięcie wyjściowe (12V lub 24V) do podłączonej taśmy LED! Koniec z pomyłkami i spalonymi taśmami przy montażu. Do tego ultra-cienka obudowa sprawia, że bez problemu ukryjesz go w sufitach podwieszanych i ciasnych zabudowach meblowych.</p>
</section>
<section style="font-family: inherit; margin: 0 0 18px 0; padding: 22px 24px; background: none !important; background-color: transparent !important; border: 1px solid currentColor; border-radius: 12px; color: inherit;">
<span style="font-family: inherit; display: inline-block; margin-bottom: 10px; padding: 5px 12px; border-radius: 999px; background: {bg_color} !important; background-color: {bg_color} !important; color: #ffffff !important; -webkit-text-fill-color: #ffffff !important; font-size: 11px; font-weight: bold; letter-spacing: .8px; text-transform: uppercase; line-height: 1.2;">
<span style="color: #ffffff;">Użyteczność mocy ({p}W)</span>
</span>
<h3 style="font-family: inherit; margin: 0 0 8px 0; background: none !important; background-color: transparent !important; color: inherit !important; font-size: 22px; line-height: 1.3; font-weight: bold;">Co możesz podłączyć do tego zasilacza?</h3>
<p style="font-family: inherit; margin: 0; background: none !important; background-color: transparent !important; color: inherit !important; opacity: .82; font-size: 14px; line-height: 1.65;">Przy zachowaniu bezpiecznego zapasu (ok. 80% mocy znamionowej, czyli ok. <strong style="color: inherit;">{s}W</strong> ciągłego, bezawaryjnego obciążenia), ten zasilacz swobodnie obsłuży na przykład <strong style="color: inherit;">{t96}</strong> najpopularniejszej taśmy LED 9.6W/m lub nawet <strong style="color: inherit;">{t48}</strong> standardowej taśmy dekoracyjnej 4.8W/m. Pamiętaj, żeby nie przeciążać urządzenia i cieszyć się latami bezproblemowej pracy.</p>
</section>
<section style="font-family: inherit; margin: 0 0 28px 0; padding: 24px; background: none !important; background-color: transparent !important; border: 1px solid currentColor; border-radius: 12px; color: inherit;">
<span style="font-family: inherit; display: inline-block; margin-bottom: 10px; padding: 5px 12px; border-radius: 999px; background: {bg_color} !important; background-color: {bg_color} !important; color: #ffffff !important; -webkit-text-fill-color: #ffffff !important; font-size: 11px; font-weight: bold; letter-spacing: .8px; text-transform: uppercase; line-height: 1.2;">
<span style="color: #ffffff;">Parametry techniczne {model}</span>
</span>
<div style="font-family: inherit; display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 14px; background: none !important; background-color: transparent !important; color: inherit; margin-bottom: 24px;">
<div style="font-family: inherit; padding: 16px; margin: 0; background: none !important; background-color: transparent !important; border: 1px solid currentColor; border-radius: 12px; box-shadow: none !important; color: inherit;">
<strong style="font-family: inherit; display: block; color: inherit !important; font-size: 15px; line-height: 1.35; margin-bottom: 6px; font-weight: bold;">Moc wyjściowa</strong>
<small style="font-family: inherit; display: block; color: inherit !important; opacity: .78; font-size: 13px; line-height: 1.45;"><strong style="color: inherit;">{p}W</strong></small>
</div>
<div style="font-family: inherit; padding: 16px; margin: 0; background: none !important; background-color: transparent !important; border: 1px solid currentColor; border-radius: 12px; box-shadow: none !important; color: inherit;">
<strong style="font-family: inherit; display: block; color: inherit !important; font-size: 15px; line-height: 1.35; margin-bottom: 6px; font-weight: bold;">Napięcie pracy</strong>
<small style="font-family: inherit; display: block; color: inherit !important; opacity: .78; font-size: 13px; line-height: 1.45;"><strong style="color: inherit;">12V/24V Smart Auto</strong></small>
</div>
<div style="font-family: inherit; padding: 16px; margin: 0; background: none !important; background-color: transparent !important; border: 1px solid currentColor; border-radius: 12px; box-shadow: none !important; color: inherit;">
<strong style="font-family: inherit; display: block; color: inherit !important; font-size: 15px; line-height: 1.35; margin-bottom: 6px; font-weight: bold;">Wymiary (dł/szer/wys)</strong>
<small style="font-family: inherit; display: block; color: inherit !important; opacity: .78; font-size: 13px; line-height: 1.45;"><strong style="color: inherit;">{dim}</strong></small>
</div>
<div style="font-family: inherit; padding: 16px; margin: 0; background: none !important; background-color: transparent !important; border: 1px solid currentColor; border-radius: 12px; box-shadow: none !important; color: inherit;">
<strong style="font-family: inherit; display: block; color: inherit !important; font-size: 15px; line-height: 1.35; margin-bottom: 6px; font-weight: bold;">Typ obudowy</strong>
<small style="font-family: inherit; display: block; color: inherit !important; opacity: .78; font-size: 13px; line-height: 1.45;"><strong style="color: inherit;">Ultra-Slim (Wąska)</strong></small>
</div>
</div>
<p style="font-family: inherit; margin: 0; background: none !important; background-color: transparent !important; color: inherit !important; opacity: .82; font-size: 14px; line-height: 1.65;">Najważniejsze cechy serii: <strong style="color: inherit;">automatyczna identyfikacja 12V/24V</strong>, ultrakompaktowe wymiary, cicha i bezawaryjna praca, doskonałe odprowadzanie ciepła oraz pełne zabezpieczenia przed przeciążeniem, zwarciem i przepięciem.<br><br><strong style="color: inherit;">Ważne:</strong> W przypadku podłączania bardzo krótkich odcinków taśm COB (poniżej 1 metra), zaleca się ręczne ustawienie stałego napięcia na zasilaczu (12V lub 24V) za pomocą dedykowanych pinów.</p>
</section>
{get_blogs_html(bg_color)}"""

def build_shoper_html(model, data):
    p = data['power']
    s = data['safe']
    t96 = data['t96']
    t48 = data['t48']
    dim = data['dim']
    return f"""<section>
<h2>{model} - Zasilacz LED Smart Auto {p}W</h2>
<p><strong>Cud Auto-identyfikacji (Smart Auto):</strong></p>
<ul>
<li>Moduł samodzielnie detektuje i dostosowuje napięcie wyjściowe (12V lub 24V) do podłączonej taśmy LED! Koniec z pomyłkami i spalonymi taśmami przy montażu.</li>
<li>Ultra-cienka obudowa sprawia, że bez problemu ukryjesz go w sufitach podwieszanych i ciasnych zabudowach meblowych.</li>
</ul>
<p><strong>Użyteczność mocy ({p}W):</strong></p>
<ul>
<li>Przy zachowaniu bezpiecznego zapasu (ok. 80% mocy znamionowej, czyli ok. {s}W ciągłego, bezawaryjnego obciążenia), ten zasilacz swobodnie obsłuży na przykład {t96} najpopularniejszej taśmy LED 9.6W/m lub nawet {t48} standardowej taśmy dekoracyjnej 4.8W/m.</li>
</ul>
<p><strong>Najważniejsze parametry i cechy:</strong></p>
<ul>
<li>Moc wyjściowa: {p}W</li>
<li>Napięcie pracy: 12V/24V Smart Auto</li>
<li>Wymiary (dł x szer x wys): {dim}</li>
<li>Typ obudowy: Ultra-Slim (Wąska)</li>
<li>Pełne zabezpieczenia przed przeciążeniem, zwarciem i przepięciem</li>
</ul>
<p><strong>Ważne:</strong></p>
<ul>
<li>W przypadku podłączania bardzo krótkich odcinków taśm COB (poniżej 1 metra), zaleca się ręczne ustawienie stałego napięcia na zasilaczu (12V lub 24V) za pomocą dedykowanych pinów.</li>
</ul>
</section>"""

for model, data in models_data.items():
    
    # 1. WAPRO
    wapro_html = build_styled_html(model, data, "#e94b25", "Seria PR-MAD", "Auto-identyfikacja 12V/24V - prawdziwy przełom w instalacjach")
    
    # 2. TIM
    tim_html = build_styled_html(model, data, "#e94b25", "Opis techniczny", f"{model} - zasilacz do kompletacji instalacji")
    
    # 3. ALLEGRO
    allegro_html = build_styled_html(model, data, "#16a34a", "Gotowy do montażu", f"{model} - niezawodny zasilacz do Twojego zestawu LED")
    
    # 4. SHOPER
    shoper_html = build_shoper_html(model, data)
    
    for tab, content in [('wapro', wapro_html), ('tim', tim_html), ('allegro', allegro_html), ('shoper', shoper_html)]:
        textarea_content = escape_html_for_textarea(content)
        view_pattern = re.compile(f'(<div class="model-block" id="desc-view-{tab}-{model}">)(.*?)(</div>\\s*<div class="edit-block" id="desc-edit-{tab}-{model}")', re.DOTALL)
        textarea_pattern = re.compile(f'(<textarea class="edit-textarea" id="textarea-{tab}-{model}"[^>]*>)(.*?)(</textarea>)', re.DOTALL)
        
        html = view_pattern.sub(lambda m: m.group(1) + '\n' + content + '\n' + m.group(3), html)
        html = textarea_pattern.sub(lambda m: m.group(1) + textarea_content + m.group(3), html)

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html)

print("Updated index.html successfully with V3.")
