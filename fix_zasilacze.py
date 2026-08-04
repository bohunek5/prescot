import re

html_path = '/Users/karolbohdanowicz/my-ai-agents/prescot/index.html'
with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Update the counter from (20) to (26)
html = html.replace('Zasilacze LED (20)', 'Zasilacze LED (26)')

models_data = {
    'PR-MAD36-1224': {'power': 36, 'safe': 28, 't96': 'ok. 3 metry', 't48': 'ok. 6 metrów'},
    'PR-MAD60-1224': {'power': 60, 'safe': 48, 't96': 'ok. 5 metrów', 't48': 'ok. 10 metrów'},
    'PR-MAD100-1224': {'power': 100, 'safe': 80, 't96': 'ok. 8 metrów', 't48': 'ok. 16 metrów'},
    'PR-MAD150-1224': {'power': 150, 'safe': 120, 't96': 'ok. 12 metrów', 't48': 'ok. 25 metrów'},
    'PR-MAD200-1224': {'power': 200, 'safe': 160, 't96': 'ok. 16 metrów', 't48': 'ok. 33 metry'},
    'PR-MAD300-1224': {'power': 300, 'safe': 240, 't96': 'ok. 25 metrów', 't48': 'ok. 50 metrów'},
}

platforms = ['wapro', 'tim', 'allegro', 'shoper']

blog_html = """
<div class="blog-grid" style="font-family:inherit; margin-top: 28px; background:none !important; background-color:transparent !important; color:inherit;">
<h3 style="font-family:inherit; margin:0 0 16px 0; font-size:22px; font-weight:700;">Baza Wiedzy - Zasilacze LED</h3>
<div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(220px, 1fr)); gap:14px; align-items:stretch;">
<div style="min-height:190px; padding:18px; border:1px solid currentColor; border-radius:12px; display:flex; flex-direction:column;">
<strong style="display:block; font-size:15px; line-height:1.35; margin-bottom:6px; font-weight:700;">Jak dobrać zasilacz LED do taśmy?</strong>
<small style="display:block; opacity:.76; font-size:12px; line-height:1.4; margin-bottom:15px;">obliczenia, moc, zapas bezpieczeństwa</small>
<a href="https://www.prescot.com.pl/pl/n/18" style="display:inline-block; min-width:142px; margin-top:auto; padding:10px 17px; border-radius:999px; background:#e94b25 !important; color:#ffffff !important; text-decoration:none !important; text-align:center; line-height:1.2; border:0 !important; font-weight:700; font-size:14px;">Czytaj poradnik</a>
</div>
<div style="min-height:190px; padding:18px; border:1px solid currentColor; border-radius:12px; display:flex; flex-direction:column;">
<strong style="display:block; font-size:15px; line-height:1.35; margin-bottom:6px; font-weight:700;">Zasilacze LED – gdzie użyć którego?</strong>
<small style="display:block; opacity:.76; font-size:12px; line-height:1.4; margin-bottom:15px;">różnice między seriami, zastosowania</small>
<a href="https://www.prescot.com.pl/pl/n/19" style="display:inline-block; min-width:142px; margin-top:auto; padding:10px 17px; border-radius:999px; background:#e94b25 !important; color:#ffffff !important; text-decoration:none !important; text-align:center; line-height:1.2; border:0 !important; font-weight:700; font-size:14px;">Czytaj poradnik</a>
</div>
<div style="min-height:190px; padding:18px; border:1px solid currentColor; border-radius:12px; display:flex; flex-direction:column;">
<strong style="display:block; font-size:15px; line-height:1.35; margin-bottom:6px; font-weight:700;">Stopnie IP – dlaczego to ważne?</strong>
<small style="display:block; opacity:.76; font-size:12px; line-height:1.4; margin-bottom:15px;">IP20 vs IP67, warunki pracy</small>
<a href="https://www.prescot.com.pl/pl/n/21" style="display:inline-block; min-width:142px; margin-top:auto; padding:10px 17px; border-radius:999px; background:#e94b25 !important; color:#ffffff !important; text-decoration:none !important; text-align:center; line-height:1.2; border:0 !important; font-weight:700; font-size:14px;">Czytaj poradnik</a>
</div>
</div>
</div>
"""

def escape_html_for_textarea(h):
    return h.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

for model, data in models_data.items():
    p = data['power']
    s = data['safe']
    t96 = data['t96']
    t48 = data['t48']
    
    content = f"""<section style="font-family: inherit; margin: 28px 0 18px 0; padding: 22px 24px; background: none !important; background-color: transparent !important; border: 1px solid currentColor; border-radius: 12px; color: inherit;">
<span style="font-family: inherit; display: inline-block; margin-bottom: 10px; padding: 5px 12px; border-radius: 999px; background: #e94b25 !important; background-color: #e94b25 !important; color: #ffffff !important; -webkit-text-fill-color: #ffffff !important; font-size: 11px; font-weight: bold; letter-spacing: .8px; text-transform: uppercase; line-height: 1.2;">
<span style="color: #ffffff;">Zasilacz LED Smart Auto {p}W</span>
</span>
<h3 style="font-family: inherit; margin: 0 0 8px 0; background: none !important; background-color: transparent !important; color: inherit !important; font-size: 22px; line-height: 1.3; font-weight: bold;">Kompaktowe i inteligentne zasilanie do Twojej instalacji</h3>
<p style="font-family: inherit; margin: 0; background: none !important; background-color: transparent !important; color: inherit !important; opacity: .82; font-size: 14px; line-height: 1.65;">Zasilacz <b>{model}</b> to nowoczesne rozwiązanie o mocy <b>{p}W</b>, z funkcją Smart Auto dopasowującą się do napięcia <b>12V/24V</b>. Ultra-cienka obudowa ułatwia montaż w trudnodostępnych miejscach.</p>
</section>
<section style="font-family: inherit; margin: 0 0 18px 0; padding: 22px 24px; background: none !important; background-color: transparent !important; border: 1px solid currentColor; border-radius: 12px; color: inherit;">
<span style="font-family: inherit; display: inline-block; margin-bottom: 10px; padding: 5px 12px; border-radius: 999px; background: #e94b25 !important; background-color: #e94b25 !important; color: #ffffff !important; -webkit-text-fill-color: #ffffff !important; font-size: 11px; font-weight: bold; letter-spacing: .8px; text-transform: uppercase; line-height: 1.2;">
<span style="color: #ffffff;">Użyteczność mocy ({p}W)</span>
</span>
<h3 style="font-family: inherit; margin: 0 0 8px 0; background: none !important; background-color: transparent !important; color: inherit !important; font-size: 22px; line-height: 1.3; font-weight: bold;">Co możesz podłączyć do tego zasilacza?</h3>
<p style="font-family: inherit; margin: 0; background: none !important; background-color: transparent !important; color: inherit !important; opacity: .82; font-size: 14px; line-height: 1.65;">Przy zachowaniu bezpiecznego zapasu (ok. 80% mocy znamionowej, czyli ok. <b>{s}W</b> realnego obciążenia), ten zasilacz bez problemu obsłuży np. <b>{t96}</b> standardowej taśmy LED o mocy 9.6W/m lub <b>{t48}</b> taśmy dekoracyjnej 4.8W/m.</p>
</section>
<section style="font-family: inherit; margin: 0 0 28px 0; padding: 24px; background: none !important; background-color: transparent !important; border: 1px solid currentColor; border-radius: 12px; color: inherit;">
<span style="font-family: inherit; display: inline-block; margin-bottom: 10px; padding: 5px 12px; border-radius: 999px; background: #e94b25 !important; background-color: #e94b25 !important; color: #ffffff !important; -webkit-text-fill-color: #ffffff !important; font-size: 11px; font-weight: bold; letter-spacing: .8px; text-transform: uppercase; line-height: 1.2;">
<span style="color: #ffffff;">Parametry modelu {model}</span>
</span>
<div style="font-family: inherit; display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 14px; background: none !important; background-color: transparent !important; color: inherit;">
<div style="font-family: inherit; padding: 16px; margin: 0; background: none !important; background-color: transparent !important; border: 1px solid currentColor; border-radius: 12px; box-shadow: none !important; color: inherit;">
<strong style="font-family: inherit; display: block; color: inherit !important; font-size: 15px; line-height: 1.35; margin-bottom: 6px; font-weight: bold;">Moc wyjściowa</strong>
<small style="font-family: inherit; display: block; color: inherit !important; opacity: .78; font-size: 13px; line-height: 1.45;">
<strong style="font-family: inherit; color: inherit !important;">{p}W</strong>
</small>
</div>
<div style="font-family: inherit; padding: 16px; margin: 0; background: none !important; background-color: transparent !important; border: 1px solid currentColor; border-radius: 12px; box-shadow: none !important; color: inherit;">
<strong style="font-family: inherit; display: block; color: inherit !important; font-size: 15px; line-height: 1.35; margin-bottom: 6px; font-weight: bold;">Napięcie pracy</strong>
<small style="font-family: inherit; display: block; color: inherit !important; opacity: .78; font-size: 13px; line-height: 1.45;">
<strong style="font-family: inherit; color: inherit !important;">12V/24V Auto</strong>
</small>
</div>
<div style="font-family: inherit; padding: 16px; margin: 0; background: none !important; background-color: transparent !important; border: 1px solid currentColor; border-radius: 12px; box-shadow: none !important; color: inherit;">
<strong style="font-family: inherit; display: block; color: inherit !important; font-size: 15px; line-height: 1.35; margin-bottom: 6px; font-weight: bold;">Typ obudowy</strong>
<small style="font-family: inherit; display: block; color: inherit !important; opacity: .78; font-size: 13px; line-height: 1.45;">
<strong style="font-family: inherit; color: inherit !important;">Ultra-Slim</strong>
</small>
</div>
</div>
</section>
{blog_html}
"""
    textarea_content = escape_html_for_textarea(content.strip())
    
    for platform in platforms:
        # We need to replace the content inside <div class="model-block" id="desc-view-{platform}-{model}"> ... </div>
        # and <textarea class="edit-textarea" id="textarea-{platform}-{model}" ...> ... </textarea>
        
        # Regex to match desc-view block content
        view_pattern = re.compile(f'(<div class="model-block" id="desc-view-{platform}-{model}">)(.*?)(</div>\\s*<div class="edit-block" id="desc-edit-{platform}-{model}")', re.DOTALL)
        
        # Regex to match textarea content
        textarea_pattern = re.compile(f'(<textarea class="edit-textarea" id="textarea-{platform}-{model}"[^>]*>)(.*?)(</textarea>)', re.DOTALL)
        
        html = view_pattern.sub(lambda m: m.group(1) + '\\n' + content.strip() + '\\n' + m.group(3), html)
        html = textarea_pattern.sub(lambda m: m.group(1) + textarea_content + m.group(3), html)

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html)

print("Updated index.html successfully.")
