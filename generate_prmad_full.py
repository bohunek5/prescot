import re
import requests
import time
from bs4 import BeautifulSoup
import json
from datetime import datetime

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "qwen2.5-coder:7b"

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)

def call_ollama(prompt, system_prompt):
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "system": system_prompt,
        "stream": False,
        "options": {
            "temperature": 0.2,
            "top_p": 0.9,
            "num_predict": 4096,
            "num_ctx": 16384
        }
    }
    try:
        t0 = time.time()
        response = requests.post(OLLAMA_URL, json=payload, timeout=240)
        response.raise_for_status()
        res = response.json().get("response", "")
        log(f"Ollama returned {len(res)} chars in {time.time()-t0:.1f}s")
        return res
    except Exception as e:
        log(f"Error calling Ollama: {e}")
        return ""

models = [
    {"sku": "PR-MAD36-1224", "power": "36W", "current": "3A(12V)/1.5A(24V)", "dim": "145 × 50 × 29 mm", "weight": "180g"},
    {"sku": "PR-MAD60-1224", "power": "60W", "current": "5A(12V)/2.5A(24V)", "dim": "145 × 50 × 29 mm", "weight": "200g"},
    {"sku": "PR-MAD100-1224", "power": "100W", "current": "8.3A(12V)/4.16A(24V)", "dim": "176 × 50 × 29 mm", "weight": "310g"},
    {"sku": "PR-MAD150-1224", "power": "150W", "current": "12.5A(12V)/6.25A(24V)", "dim": "199 × 50 × 29 mm", "weight": "390g"},
    {"sku": "PR-MAD200-1224", "power": "200W", "current": "16.6A(12V)/8.3A(24V)", "dim": "218 × 50 × 29 mm", "weight": "460g"},
    {"sku": "PR-MAD300-1224", "power": "300W", "current": "25A(12V)/12.5A(24V)", "dim": "240 × 50 × 29 mm", "weight": "590g"}
]

def generate_wapro_html(model):
    return f"""<section style="font-family:inherit; margin:28px 0 18px 0; padding:22px 24px; background:none !important; background-color:transparent !important; border:1px solid currentColor; border-radius:12px; color:inherit;">
<span style="font-family:inherit; display:inline-block; margin-bottom:10px; padding:5px 12px; border-radius:999px; background:#e94b25 !important; background-color:#e94b25 !important; color:#ffffff !important; -webkit-text-fill-color:#ffffff !important; font-size:11px; font-weight:700; letter-spacing:.8px; text-transform:uppercase; line-height:1.2;">
<font color="#ffffff">Innowacja</font>
</span>
<h3 style="font-family:inherit; margin:0 0 8px 0; background:none !important; background-color:transparent !important; color:inherit !important; font-size:22px; line-height:1.3; font-weight:700;">Smart Auto-Identify 12V/24V</h3>
<p style="font-family:inherit; margin:0; background:none !important; background-color:transparent !important; color:inherit !important; opacity:.82; font-size:14px; line-height:1.65;">Wbudowany procesor impulsowy po podłączeniu wykonuje szybki pomiar impedancji i automatycznie ustala napięcie wyjściowe (12V lub 24V). Zabezpiecza to taśmy przed uszkodzeniem i niedozasileniem.</p>
</section>
<section style="font-family:inherit; margin:0 0 18px 0; padding:22px 24px; background:none !important; background-color:transparent !important; border:1px solid currentColor; border-radius:12px; color:inherit;">
<span style="font-family:inherit; display:inline-block; margin-bottom:10px; padding:5px 12px; border-radius:999px; background:#e94b25 !important; background-color:#e94b25 !important; color:#ffffff !important; -webkit-text-fill-color:#ffffff !important; font-size:11px; font-weight:700; letter-spacing:.8px; text-transform:uppercase; line-height:1.2;">
<font color="#ffffff">Chłodzenie i Ochrona</font>
</span>
<h3 style="font-family:inherit; margin:0 0 8px 0; background:none !important; background-color:transparent !important; color:inherit !important; font-size:22px; line-height:1.3; font-weight:700;">Technologia Semi-Potted & Pasywne Chłodzenie</h3>
<p style="font-family:inherit; margin:0; background:none !important; background-color:transparent !important; color:inherit !important; opacity:.82; font-size:14px; line-height:1.65;">Wnętrze zasilacza zostało wypełnione masą silikonowo-epoksydową, co perfekcyjnie odprowadza ciepło i chroni przed wilgocią. Ultra-Slim (29mm wysokości) oraz brak wentylatora zapewniają absolutnie bezgłośną pracę, co pozwala na montaż w najwęższych szczelinach i sufitach podwieszanych.</p>
</section>
<section style="font-family:inherit; margin:0 0 18px 0; padding:22px 24px; background:none !important; background-color:transparent !important; border:1px solid currentColor; border-radius:12px; color:inherit;">
<span style="font-family:inherit; display:inline-block; margin-bottom:10px; padding:5px 12px; border-radius:999px; background:#e94b25 !important; background-color:#e94b25 !important; color:#ffffff !important; -webkit-text-fill-color:#ffffff !important; font-size:11px; font-weight:700; letter-spacing:.8px; text-transform:uppercase; line-height:1.2;">
<font color="#ffffff">Smart Protection Suite</font>
</span>
<h3 style="font-family:inherit; margin:0 0 8px 0; background:none !important; background-color:transparent !important; color:inherit !important; font-size:22px; line-height:1.3; font-weight:700;">Zabezpieczenia na lata (OLP, SCP, OTP, OVP)</h3>
<p style="font-family:inherit; margin:0; background:none !important; background-color:transparent !important; color:inherit !important; opacity:.82; font-size:14px; line-height:1.65;">Pełne bezpieczeństwo instalacji: zabezpieczenia przeciążeniowe, przeciwzwarciowe, termiczne (odcięcie powyżej 85°C) i przepięciowe. Zasilacz działa w klasie bezpieczeństwa II (SELV) i oferuje trwałość (MTBF) ponad 50 000 godzin ciągłej pracy.</p>
</section>
<section style="font-family:inherit; margin:0 0 28px 0; padding:24px; background:none !important; background-color:transparent !important; border:1px solid currentColor; border-radius:12px; color:inherit;">
<span style="font-family:inherit; display:inline-block; margin-bottom:10px; padding:5px 12px; border-radius:999px; background:#e94b25 !important; background-color:#e94b25 !important; color:#ffffff !important; -webkit-text-fill-color:#ffffff !important; font-size:11px; font-weight:700; letter-spacing:.8px; text-transform:uppercase; line-height:1.2;">
<font color="#ffffff">Parametry modelu {model['sku']}</font>
</span>
<div style="font-family:inherit; display:grid; grid-template-columns:repeat(auto-fit, minmax(180px, 1fr)); gap:14px; background:none !important; background-color:transparent !important; color:inherit;">
<div style="font-family:inherit; padding:16px; margin:0; background:none !important; background-color:transparent !important; border:1px solid currentColor; border-radius:12px; box-shadow:none !important; color:inherit;">
<strong style="font-family:inherit; display:block; color:inherit !important; font-size:15px; line-height:1.35; margin-bottom:6px; font-weight:700;">Moc wyjściowa</strong>
<small style="font-family:inherit; display:block; color:inherit !important; opacity:.78; font-size:13px; line-height:1.45;">
<strong style="font-family:inherit; color:inherit !important;">{model['power']}</strong>
</small>
</div>
<div style="font-family:inherit; padding:16px; margin:0; background:none !important; background-color:transparent !important; border:1px solid currentColor; border-radius:12px; box-shadow:none !important; color:inherit;">
<strong style="font-family:inherit; display:block; color:inherit !important; font-size:15px; line-height:1.35; margin-bottom:6px; font-weight:700;">Wyjście DC</strong>
<small style="font-family:inherit; display:block; color:inherit !important; opacity:.78; font-size:13px; line-height:1.45;">
<strong style="font-family:inherit; color:inherit !important;">12V/24V Auto</strong><br>{model['current']}
</small>
</div>
<div style="font-family:inherit; padding:16px; margin:0; background:none !important; background-color:transparent !important; border:1px solid currentColor; border-radius:12px; box-shadow:none !important; color:inherit;">
<strong style="font-family:inherit; display:block; color:inherit !important; font-size:15px; line-height:1.35; margin-bottom:6px; font-weight:700;">Wymiary i Waga</strong>
<small style="font-family:inherit; display:block; color:inherit !important; opacity:.78; font-size:13px; line-height:1.45;">
{model['dim']}<br>{model['weight']}
</small>
</div>
</div>
</section>"""

system_prompt = (
    "Jesteś zaawansowanym copywriterem i specjalistą e-commerce. "
    "Otrzymasz opis bazowy produktu (kod HTML w tagach <section>). "
    "Twoim zadaniem jest stworzyć NOWĄ WERSJĘ opisu dla innej platformy sprzedażowej, "
    "zmieniając treść nagłówków i akapitów, by uniknąć duplikacji (SEO), ale zachowując układ i logikę HTML. "
    "ZACHOWAJ oryginalny format HTML (tagi <section>, <h3>, <p>, style CSS), w szczególności tag parametry na dole. "
    "Zwróć TYLKO zaktualizowany kod HTML, bez komentarzy, znaczników markdown (```html) itp."
)

prompts = {
    "tim": "Przepisz podany opis dla platformy TIM (klient B2B, profesjonaliści, instalatorzy). Skup się na szybkości montażu, niezawodności i bezawaryjności. Język techniczny i konkretny.",
    "allegro": "Przepisz podany opis dla platformy Allegro (klient B2C, konsumenci). Podkreśl łatwość użycia, bezpieczeństwo domowe, ciszę i małe rozmiary. Język przystępny i korzyściowe call-to-action.",
    "shoper": "Przepisz podany opis dla sklepu e-commerce Shoper (klient Premium, design). Skup się na nowoczesności, inteligentnej technologii i estetyce instalacji (brak widocznego zasilacza). Język luksusowy i nowoczesny."
}

def main():
    log("Loading index.html...")
    with open("index.html", "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f.read(), "html.parser")
        
    for model in models:
        sku = model['sku']
        log(f"Processing model {sku}...")
        
        # 1. GENERATE AND UPDATE WAPRO
        wapro_html = generate_wapro_html(model)
        
        wapro_view = soup.find('div', id=f'desc-view-wapro-{sku}')
        wapro_edit = soup.find('textarea', id=f'textarea-wapro-{sku}')
        
        if wapro_view and wapro_edit:
            wapro_view.clear()
            wapro_view.append(BeautifulSoup(wapro_html, "html.parser"))
            wapro_edit.string = wapro_html
            log(f"Updated WAPRO for {sku}")
        else:
            log(f"Could not find WAPRO elements for {sku}")
            continue

        # 2. GENERATE FOR TIM, ALLEGRO, SHOPER via Ollama
        for tab in ['tim', 'allegro', 'shoper']:
            view = soup.find('div', id=f'desc-view-{tab}-{sku}')
            edit = soup.find('textarea', id=f'textarea-{tab}-{sku}')
            
            if not view or not edit:
                log(f"Could not find {tab} elements for {sku}")
                continue
                
            prompt = f"{prompts[tab]}\n\n--- OPIS BAZOWY ---\n{wapro_html}"
            
            log(f"Calling Ollama for {tab} - {sku}...")
            response = call_ollama(prompt, system_prompt)
            
            if response:
                response = response.replace("```html", "").replace("```", "").strip()
                view.clear()
                view.append(BeautifulSoup(response, "html.parser"))
                edit.string = response
                log(f"Updated {tab} for {sku}")
            else:
                log(f"Failed to generate for {tab} - {sku}")

    log("Saving index.html...")
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(str(soup))
    log("Done!")

if __name__ == "__main__":
    main()
