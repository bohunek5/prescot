import os
import re
import sys
import json
import requests
from bs4 import BeautifulSoup

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "qwen2.5-coder:7b"
SKILL_PATH = "/Users/karolbohdanowicz/my-ai-agents/.agent/skills/prescot-copywriter-seo/SKILL.md"
INDEX_PATH = "/Users/karolbohdanowicz/my-ai-agents/prescot/index.html"
CHECKPOINT_PATH = "/Users/karolbohdanowicz/my-ai-agents/prescot/checkpoint_skus.json"

# Load copywriter skill rules
with open(SKILL_PATH, "r", encoding="utf-8") as f:
    skill_content = f.read()

# Load source contexts
# 1. Controllers Manual
controllers_manual = ""
manual_path = "/Users/karolbohdanowicz/Downloads/USER MANUAL - Instrukcja obsługi sterowniki Prescot LED.txt"
if os.path.exists(manual_path):
    with open(manual_path, "r", encoding="utf-8") as f:
        controllers_manual = f.read()

# 2. Scharfer Data
scharfer_data = ""
scharfer_path = "/Users/karolbohdanowicz/Downloads/TOP Scharfer - OSTATECZNY POPRAWIONY.txt"
if os.path.exists(scharfer_path):
    with open(scharfer_path, "r", encoding="utf-8") as f:
        scharfer_data = f.read()

# 3. Connectors Data
connectors_data = ""
connectors_path = "/Users/karolbohdanowicz/Downloads/Złączki_PRESCOT_extracted.txt"
if os.path.exists(connectors_path):
    with open(connectors_path, "r", encoding="utf-8") as f:
        connectors_data = f.read()

def get_category(sku):
    if sku.startswith(('WZ-', 'V1', 'T1', 'V2', 'RT1', 'RT6', 'DIM-')) or 'RGB' in sku and len(sku) < 10 or sku.startswith('PR-'):
        return 'sterowniki'
    if sku.startswith(('SC-', 'LRS-', 'RS-', 'SCH-')):
        return 'zasilacze'
    if sku.startswith(('B8547', '18032', 'A01587', 'A02966')):
        return 'profile'
    if sku.startswith(('FC10', 'FC8', 'ZLC', 'M4-')):
        return 'zlaczki'
    return 'tasmy'

def call_ollama(prompt, system_prompt):
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "system": system_prompt,
        "stream": False,
        "options": {
            "temperature": 0.2,
            "top_p": 0.9,
            "num_predict": 4096
        }
    }
    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=180)
        response.raise_for_status()
        return response.json().get("response", "")
    except Exception as e:
        print(f"Error calling Ollama: {e}")
        return ""

def parse_badge(badge):
    badge = badge.strip()
    series = "KLUŚ"
    length = ""
    color = ""
    
    if "–" in badge:
        parts = badge.split("–")
        series = parts[0].strip()
        rest = parts[1].strip()
    elif "-" in badge:
        parts = badge.split("-")
        series = parts[0].strip()
        rest = parts[1].strip()
    else:
        rest = badge
        
    if "," in rest:
        subparts = rest.split(",")
        length = subparts[0].strip()
        color = subparts[1].strip()
    else:
        length = rest
        
    return series, length, color

def generate_description_json(sku, category, spec_dict, badge=""):
    spec_str = "\n".join([f"- {k}: {v}" for k, v in spec_dict.items()])
    
    if category == 'sterowniki':
        cat_data = f"""
Informacje techniczne:
{controllers_manual}

Zasady:
- Dotyczy sterownika radiowego RF 2.4GHz: {sku}.
- Gwarancja wynosi 5 lat!
- Nigdy nie wspominaj o złączkach zaciskowych ani o marce Scharfer.
- BEZWZGLĘDNY ZAKAZ pisania o "awariach zasilania", "zanikach prądu", "braku dostępu do prądu" lub "niskich temperaturach". To są bzdurne cechy w kontekście zastosowania sterownika LED.
- Sekcja ZASTOSOWANIE/GDZIE UŻYĆ musi opisywać podział oświetlenia na strefy, podwieszane sufity, wnęki sufitowe, sypialnie, kuchnie, salony, płynną regulację natężenia światła pilotem lub panelem naściennym bez kucia ścian.
"""
    elif category == 'zasilacze':
        sku_match = re.search(rf"START {sku}.*?KONIEC {sku}", scharfer_data, re.DOTALL)
        source_context = sku_match.group(0) if sku_match else scharfer_data[:2000]
        cat_data = f"""
Informacje techniczne:
{source_context}

Zasady:
- Dotyczy zasilacza hermetycznego Scharfer {sku}.
- Gwarancja wynosi 7 lat!
- Pasywne chłodzenie, obudowa hermetyczna metalowa IP67, praca pod 100% obciążeniem, brak głośnych wentylatorów / cichy montaż.
- Sekcja 1 (ZASADA DZIAŁANIA) musi bezpośrednio i wyraźnie podkreślać jako główne zalety:
  1. Ciągłą pracę pod pełnym 100% obciążeniem bez ryzyka awarii czy spadku napięcia.
  2. Konstrukcję bezwentylatorową (pasywne chłodzenie) gwarantującą cichą pracę i eliminującą problem pisków cewek.
  3. Wytrzymałą, metalową obudowę hermetyczną o klasie szczelności IP67, która całkowicie chroni elektronikę przed kurzem, pyłem i bezpośrednim kontaktem z wodą.
  4. Wyjątkowo długi okres ochronny - aż 7 lat gwarancji producenta, będący potwierdzeniem najwyższej niezawodności komponentów.
- Nigdy nie wspominaj o sterownikach 2.4G ani o złączkach.
"""
    elif category == 'profile':
        series, length, color = parse_badge(badge)
        if "NK" in series:
            type_desc = "wpuszczany (meblowy lub do płyt gipsowo-kartonowych GK), montowany we wcięciu/rowku (frezie), którego boczne skrzydełka (kołnierz) idealnie maskują ewentualne niedoskonałości krawędzi frezu"
            montaz_szczegoly = "idealny do dyskretnego montażu zlicowanego w szafkach meblowych, garderobach czy sufitach"
        else:
            type_desc = "nawierzchniowy/natynkowy o minimalnej wysokości, montowany bezpośrednio do powierzchni sufitów, blatów, szafek (np. za pomocą dedykowanych zaczepów/sprężynek, wkrętów lub taśmy dwustronnej)"
            montaz_szczegoly = "doskonały do oświetlenia blatów kuchennych, półek lub jako nawierzchniowy element dekoracyjny"
            
        prompt = f"""
Jesteś profesjonalnym copywriterem e-commerce. Stwórz opisy produktu w formacie JSON po polsku dla profilu aluminiowego marki KLUŚ.
SKU: {sku}
Specyfikacja techniczna:
{spec_str}

Dane wejściowe produktu do wykorzystania:
- Seria profilu: {series}
- Typ profilu: {type_desc}
- Sposób montażu: {montaz_szczegoly}
- Długość profilu: {length}
- Kolor/wykończenie: {color}

Wymagany format JSON (zwróć tylko czysty JSON bez ```json, bez innych znaków, tylko czysty kod JSON):
{{
  "wapro": [
    {{ "pill": "PROFIL KLUŚ", "head": "Nagłówek sekcji 1 (unikalny synonim do 'Fundament trwałego systemu LED')", "text": "Opis sekcji 1" }},
    {{ "pill": "RODZAJE I ZASTOSOWANIE", "head": "Nagłówek sekcji 2 (o montażu wpuszczanym lub nawierzchniowym)", "text": "Opis sekcji 2" }},
    {{ "pill": "IDEALNA LINIA ŚWIATŁA", "head": "Klosz i rozproszenie (Brak w zestawie)", "text": "Opis sekcji 3" }}
  ],
  "tim": [
    {{ "pill": "PROFIL KLUŚ", "head": "Inny nagłówek sekcji 1", "text": "Opis sekcji 1" }},
    {{ "pill": "RODZAJE I ZASTOSOWANIE", "head": "Inny nagłówek sekcji 2", "text": "Opis sekcji 2" }},
    {{ "pill": "IDEALNA LINIA ŚWIATŁA", "head": "Klosz i rozproszenie (Brak w zestawie)", "text": "Opis sekcji 3" }}
  ],
  "allegro": [
    {{ "pill": "PROFIL KLUŚ", "head": "Inny nagłówek sekcji 1", "text": "Opis sekcji 1" }},
    {{ "pill": "RODZAJE I ZASTOSOWANIE", "head": "Inny nagłówek sekcji 2", "text": "Opis sekcji 2" }},
    {{ "pill": "IDEALNA LINIA ŚWIATŁA", "head": "Klosz i rozproszenie (Brak w zestawie)", "text": "Opis sekcji 3" }}
  ]
}}

Zasady:
1. Pisz WYŁĄCZNIE w języku polskim.
2. Zakazane słowa: "wysokiej jakości", "innowacyjny", "lider rynku", "kompleksowy", "najlepszy", "wyjątkowy".
3. Żadna sekcja NIE MOŻE zawierać list <ul>/<li> ani innych tagów HTML (tylko czysty tekst, min. 3 zdania na opis).
4. Sekcja 1 (PROFIL KLUŚ):
   - Nagłówek (head) musi być unikalną frazą oznaczającą chłodzenie lub stabilność taśm (synonim do "Fundament trwałego systemu LED", np. "Baza niezawodnej instalacji LED", "Trwałe chłodzenie dla diod LED", "Filar stabilnego oświetlenia LED", "Ochrona i optymalna temperatura diod" itp.). Baw się synonimami, nie pisz w kółko tego samego dla różnych platform i modeli!
   - W tekście sekcji opisz konkretną długość ({length}) oraz kolor ({color}). Napisz np. "Profil o długości {length} w kolorze {color}..." lub "Wersja o długości {length} w wykończeniu {color}...".
   - Opisz funkcję radiatora: profil efektywnie odprowadza ciepło wydzielane przez diody LED, zapobiegając ich przegrzaniu i drastycznie przedłużając żywotność taśmy.
5. Sekcja 2 (RODZAJE I ZASTOSOWANIE):
   - Nagłówek (head) musi opisywać sposób montażu lub typ profilu (np. "Dyskretny montaż wpuszczany", "Zlicowana linia światła", "Uniwersalny montaż nawierzchniowy").
   - W tekście sekcji opisz dokładnie typ profilu: {type_desc} oraz sposób montażu: {montaz_szczegoly}. Pisz o konkretnym wariancie (np. jeśli to {series}, napisz o nim).
6. Sekcja 3 (IDEALNA LINIA ŚWIATŁA):
   - Nagłówek (head) musi brzmieć dokładnie: "Klosz i rozproszenie (Brak w zestawie)" lub "Klosz i osłona (Brak w zestawie)".
   - W tekście opisz klosze. Wyjaśnij, że klosz nie jest częścią zestawu (sprzedawany oddzielnie).
   - Wyjaśnij różnicę między kloszami: mleczny (tworzy jednolitą, gładką linie światła bez widocznych punktów świetlnych/efektu kropkowania) a transparentny (maksymalna przepustowość światła, optymalna jasność).
   - Zaznacz, że pasują do niego wsuwane klosze (np. KA, HS) oraz mleczny klosz LIGER-11 (wciskany).
"""
        response_str = call_ollama(prompt, skill_content)
        response_str = response_str.strip()
        if response_str.startswith("```json"):
            response_str = response_str[7:]
        if response_str.endswith("```"):
            response_str = response_str[:-3]
        response_str = response_str.strip()
        try:
            data = json.loads(response_str)
            return data
        except Exception as e:
            print(f"Error parsing JSON for {sku}: {e}\nResponse was:\n{response_str}")
            return None
    elif category == 'zlaczki':
        cat_data = f"""
Informacje techniczne:
{connectors_data}

Zasady:
- Dotyczy złączki bezlutowej {sku}.
- Brak cieni w linii światła dzięki obudowie z przezroczystego poliwęglanu PC.
- Kształty L (kątowa), T (trójnik), proste lub zestawy 9w1. Szerokości 8mm, 10mm lub 12mm.
- Nigdy nie wspominaj o sterownikach radiowych, parowaniu ani o marce Scharfer. Nie podawaj 5 ani 7 lat gwarancji dla złączek (tylko standardowa).
"""
    else:
        return None

    prompt = f"""
Jesteś profesjonalnym copywriterem e-commerce. Stwórz opisy produktu w formacie JSON po polsku.
SKU: {sku}
Kategoria: {category}
Specyfikacja:
{spec_str}

{cat_data}

Zasady:
1. Pisz WYŁĄCZNIE w języku polskim (ani słowa po angielsku!).
2. Wygeneruj 3 wersje opisu (wapro, tim, allegro). Każda wersja musi zawierać dokładnie 3 unikalne sekcje (Section 1, Section 2, Section 3). Nie powtarzaj nagłówków ani treści sekcji.
   - Sekcja 1: Zasada działania i wstęp. (Pill np. ZASADA DZIAŁANIA, STABILNE ZASILANIE)
   - Sekcja 2: Lista kluczowych funkcji w HTML (zawsze w formacie <ul><li><b>Cecha:</b> korzyść i opis</li>...</ul>, minimum 3 rozbudowane punkty). (Pill np. KLUCZOWE CECHY, PARAMETRY TECHNICZNE)
   - Sekcja 3: Praktyczne zastosowanie i zalety dla instalatora/użytkownika. (Pill np. GDZIE UŻYĆ, ZASTOSOWANIE)
3. Zakazane słowa: "wysokiej jakości", "innowacyjny", "lider rynku", "kompleksowy", "najlepszy", "wyjątkowy".
4. Text w sekcji nie może zawierać tagów <p> ani </p>.
5. Nagłówek 'head' dla KAŻDEJ z trzech sekcji jest obowiązkowy! Nie może być pusty. Musi to być konkretna, chwytliwa fraza (np. "Cicha praca dzięki chłodzeniu pasywnemu", "Montaż bez użycia lutownicy").

Zwróć wyłącznie czysty, poprawny kod JSON (bez markdown blocks, bez ```json, tylko czysty JSON):
{{
  "wapro": [
    {{ "pill": "Pill1", "head": "Nagłówek1", "text": "Opis w języku polskim (min. 3 zdania)" }},
    {{ "pill": "Pill2", "head": "Nagłówek2", "text": "<ul><li><b>Cecha 1:</b> opis po polsku</li><li><b>Cecha 2:</b> opis po polsku</li><li><b>Cecha 3:</b> opis po polsku</li></ul>" }},
    {{ "pill": "Pill3", "head": "Nagłówek3", "text": "Opis w języku polskim (min. 3 zdania)" }}
  ],
  "tim": [
    ...
  ],
  "allegro": [
    ...
  ]
}}
"""
    response_str = call_ollama(prompt, skill_content)
    response_str = response_str.strip()
    if response_str.startswith("```json"):
        response_str = response_str[7:]
    if response_str.endswith("```"):
        response_str = response_str[:-3]
    response_str = response_str.strip()
    
    try:
        data = json.loads(response_str)
        return data
    except Exception as e:
        print(f"Error parsing JSON for {sku}: {e}\nResponse was:\n{response_str}")
        return None

blog_html_tasmy = """
<section style="font-family:inherit; margin:18px 0 28px 0; padding:22px 24px; background:none !important; background-color:transparent !important; border:1px solid currentColor; border-radius:12px; color:inherit;">
  <div style="font-family:inherit; margin-bottom:18px; background:none !important; background-color:transparent !important; color:inherit;">
    <span style="font-family:inherit; display:inline-block; margin-bottom:10px; padding:5px 12px; border-radius:999px; background:#e94b25 !important; background-color:#e94b25 !important; color:#ffffff !important; -webkit-text-fill-color:#ffffff !important; font-size:11px; font-weight:700; letter-spacing:.8px;  line-height:1.2;">
    <font color="#ffffff">Praktyczne poradniki</font>
  </span>
    <h3 style="font-family:inherit; margin:0 0 8px 0; background:none !important; background-color:transparent !important; color:inherit !important; font-size:22px; line-height:1.3; font-weight:700;">
      Dobierz komponenty bez zgadywania
    </h3>
    <p style="font-family:inherit; margin:0; background:none !important; background-color:transparent !important; color:inherit !important; opacity:.78; font-size:14px; line-height:1.6;">
      Poradniki prowadzą przez parametry, zasilanie, profile aluminiowe i montaż, czyli decyzje, które naprawdę wpływają na efekt końcowy.
    </p>
  </div>
  <div style="font-family:inherit; display:grid; grid-template-columns:repeat(auto-fit, minmax(220px, 1fr)); gap:14px; background:none !important; background-color:transparent !important; color:inherit; align-items:stretch;">
    <div style="font-family:inherit; min-height:190px; padding:18px; margin:0; background:none !important; background-color:transparent !important; border:1px solid currentColor; border-radius:12px; box-shadow:none !important; color:inherit; display:flex; flex-direction:column;">
      <strong style="font-family:inherit; display:block; color:inherit !important; font-size:15px; line-height:1.35; margin-bottom:6px; font-weight:700;">Jak czytać parametry taśmy LED?</strong>
      <small style="font-family:inherit; display:block; color:inherit !important; opacity:.76; font-size:12px; line-height:1.4; margin-bottom:15px;">moc, lumeny, CRI, napięcie i IP</small>
      <a href="https://www.prescot.com.pl/pl/n/23" style="font-family:inherit; display:inline-block; min-width:142px; margin-top:auto; padding:10px 17px; border-radius:999px; background:#e94b25 !important; background-color:#e94b25 !important; color:#ffffff !important; -webkit-text-fill-color:#ffffff !important; text-decoration:none !important; text-align:center; line-height:1.2; border:0 !important; align-self:flex-start;">
        <font color="#ffffff"><span style="font-family:inherit; color:#ffffff !important; -webkit-text-fill-color:#ffffff !important; text-decoration:none !important; font-weight:700; font-size:14px;">Czytaj poradnik</span></font>
      </a>
    </div>
    <div style="font-family:inherit; min-height:190px; padding:18px; margin:0; background:none !important; background-color:transparent !important; border:1px solid currentColor; border-radius:12px; box-shadow:none !important; color:inherit; display:flex; flex-direction:column;">
      <strong style="font-family:inherit; display:block; color:inherit !important; font-size:15px; line-height:1.35; margin-bottom:6px; font-weight:700;">Montaż taśmy LED na zewnątrz</strong>
      <small style="font-family:inherit; display:block; color:inherit !important; opacity:.76; font-size:12px; line-height:1.4; margin-bottom:15px;">IP, uszczelnienie i ochrona połączeń</small>
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
</section>"""

blog_html_zasilacze = """
<section style="font-family:inherit; margin:18px 0 0 0; padding:22px 24px; background:none !important; background-color:transparent !important; border:1px solid currentColor; border-radius:12px; color:inherit;">
  <div style="font-family:inherit; margin-bottom:18px; background:none !important; background-color:transparent !important; color:inherit;">
    <span style="font-family:inherit; display:inline-block; margin-bottom:10px; padding:5px 12px; border-radius:999px; background:#e94b25 !important; background-color:#e94b25 !important; color:#ffffff !important; -webkit-text-fill-color:#ffffff !important; font-size:11px; font-weight:700; letter-spacing:.8px; text-transform:uppercase; line-height:1.2;">
      <font color="#ffffff">Praktyczne poradniki</font>
    </span>

    <h3 style="font-family:inherit; margin:0 0 8px 0; background:none !important; background-color:transparent !important; color:inherit !important; font-size:22px; line-height:1.3; font-weight:700;">
      Dobierz zasilacz LED bez zgadywania
    </h3>

    <p style="font-family:inherit; margin:0; background:none !important; background-color:transparent !important; color:inherit !important; opacity:.78; font-size:14px; line-height:1.6;">
      Sprawdź krótkie poradniki, które pomogą dobrać moc, typ obudowy, napięcie i stopień ochrony IP do konkretnej instalacji LED.
    </p>
  </div>

  <div style="font-family:inherit; display:grid; grid-template-columns:repeat(auto-fit, minmax(220px, 1fr)); gap:14px; background:none !important; background-color:transparent !important; color:inherit; align-items:stretch;">
    <div style="font-family:inherit; min-height:190px; padding:18px; margin:0; background:none !important; background-color:transparent !important; border:1px solid currentColor; border-radius:12px; box-shadow:none !important; color:inherit; display:flex; flex-direction:column;">
      <strong style="font-family:inherit; display:block; color:inherit !important; font-size:15px; line-height:1.35; margin-bottom:6px; font-weight:700;">Do czego służą zasilacze LED?</strong>
      <small style="font-family:inherit; display:block; color:inherit !important; opacity:.76; font-size:12px; line-height:1.4; margin-bottom:15px;">taśmy LED, moduły LED i sterowniki</small>
      <a href="https://www.prescot.com.pl/pl/n/26" style="font-family:inherit; display:inline-block; min-width:142px; margin-top:auto; padding:10px 17px; border-radius:999px; background:#e94b25 !important; background-color:#e94b25 !important; color:#ffffff !important; -webkit-text-fill-color:#ffffff !important; text-decoration:none !important; text-align:center; line-height:1.2; border:0 !important; align-self:flex-start;">
        <font color="#ffffff"><span style="font-family:inherit; color:#ffffff !important; -webkit-text-fill-color:#ffffff !important; text-decoration:none !important; font-weight:700; font-size:14px;">Czytaj poradnik</span></font>
      </a>
    </div>

    <div style="font-family:inherit; min-height:190px; padding:18px; margin:0; background:none !important; background-color:transparent !important; border:1px solid currentColor; border-radius:12px; box-shadow:none !important; color:inherit; display:flex; flex-direction:column;">
      <strong style="font-family:inherit; display:block; color:inherit !important; font-size:15px; line-height:1.35; margin-bottom:6px; font-weight:700;">Zasilacze LED - gdzie użyć którego?</strong>
      <small style="font-family:inherit; display:block; color:inherit !important; opacity:.76; font-size:12px; line-height:1.4; margin-bottom:15px;">desktop, gniazdkowy, siatkowy, slim i hermetyczny</small>
      <a href="https://www.prescot.com.pl/pl/n/25" style="font-family:inherit; display:inline-block; min-width:142px; margin-top:auto; padding:10px 17px; border-radius:999px; background:#e94b25 !important; background-color:#e94b25 !important; color:#ffffff !important; -webkit-text-fill-color:#ffffff !important; text-decoration:none !important; text-align:center; line-height:1.2; border:0 !important; align-self:flex-start;">
        <font color="#ffffff"><span style="font-family:inherit; color:#ffffff !important; -webkit-text-fill-color:#ffffff !important; text-decoration:none !important; font-weight:700; font-size:14px;">Czytaj poradnik</span></font>
      </a>
    </div>

    <div style="font-family:inherit; min-height:190px; padding:18px; margin:0; background:none !important; background-color:transparent !important; border:1px solid currentColor; border-radius:12px; box-shadow:none !important; color:inherit; display:flex; flex-direction:column;">
      <strong style="font-family:inherit; display:block; color:inherit !important; font-size:15px; line-height:1.35; margin-bottom:6px; font-weight:700;">Jak dobrać zasilacz LED do taśmy?</strong>
      <small style="font-family:inherit; display:block; color:inherit !important; opacity:.76; font-size:12px; line-height:1.4; margin-bottom:15px;">moc W/m, długość taśmy i zapas mocy</small>
      <a href="https://www.prescot.com.pl/pl/n/24" style="font-family:inherit; display:inline-block; min-width:142px; margin-top:auto; padding:10px 17px; border-radius:999px; background:#e94b25 !important; background-color:#e94b25 !important; color:#ffffff !important; -webkit-text-fill-color:#ffffff !important; text-decoration:none !important; text-align:center; line-height:1.2; border:0 !important; align-self:flex-start;">
        <font color="#ffffff"><span style="font-family:inherit; color:#ffffff !important; -webkit-text-fill-color:#ffffff !important; text-decoration:none !important; font-weight:700; font-size:14px;">Czytaj poradnik</span></font>
      </a>
    </div>

    <div style="font-family:inherit; min-height:190px; padding:18px; margin:0; background:none !important; background-color:transparent !important; border:1px solid currentColor; border-radius:12px; box-shadow:none !important; color:inherit; display:flex; flex-direction:column;">
      <strong style="font-family:inherit; display:block; color:inherit !important; font-size:15px; line-height:1.35; margin-bottom:6px; font-weight:700;">Stopnie IP - dlaczego to ważne?</strong>
      <small style="font-family:inherit; display:block; color:inherit !important; opacity:.76; font-size:12px; line-height:1.4; margin-bottom:15px;">IP20, IP33, IP44 i <strong style="font-family:inherit; color:inherit !important;">IP67</strong> w praktyce</small>
      <a href="https://www.prescot.com.pl/pl/n/27" style="font-family:inherit; display:inline-block; min-width:142px; margin-top:auto; padding:10px 17px; border-radius:999px; background:#e94b25 !important; background-color:#e94b25 !important; color:#ffffff !important; -webkit-text-fill-color:#ffffff !important; text-decoration:none !important; text-align:center; line-height:1.2; border:0 !important; align-self:flex-start;">
        <font color="#ffffff"><span style="font-family:inherit; color:#ffffff !important; -webkit-text-fill-color:#ffffff !important; text-decoration:none !important; font-weight:700; font-size:14px;">Czytaj poradnik</span></font>
      </a>
    </div>
  </div>
</section>"""

blog_html_sterowniki = """
<section style="font-family:inherit; margin:18px 0 28px 0; padding:22px 24px; background:none !important; background-color:transparent !important; border:1px solid currentColor; border-radius:12px; color:inherit;">
  <div style="font-family:inherit; margin-bottom:18px; background:none !important; background-color:transparent !important; color:inherit;">
    <span style="font-family:inherit; display:inline-block; margin-bottom:10px; padding:5px 12px; border-radius:999px; background:#e94b25 !important; background-color:#e94b25 !important; color:#ffffff !important; -webkit-text-fill-color:#ffffff !important; font-size:11px; font-weight:700; letter-spacing:.8px;  line-height:1.2;">
    <font color="#ffffff">Praktyczne poradniki</font>
  </span>

    <h3 style="font-family:inherit; margin:0 0 8px 0; background:none !important; background-color:transparent !important; color:inherit !important; font-size:22px; line-height:1.3; font-weight:700;">
      Dobierz komponenty bez zgadywania
    </h3>

    <p style="font-family:inherit; margin:0; background:none !important; background-color:transparent !important; color:inherit !important; opacity:.78; font-size:14px; line-height:1.6;">
      Poradniki prowadzą przez parametry, zasilanie, profile aluminiowe i montaż, czyli decyzje, które naprawdę wpływają na efekt końcowy.
    </p>
  </div>

  <div style="font-family:inherit; display:grid; grid-template-columns:repeat(auto-fit, minmax(220px, 1fr)); gap:14px; background:none !important; background-color:transparent !important; color:inherit; align-items:stretch;">
    <div style="font-family:inherit; min-height:190px; padding:18px; margin:0; background:none !important; background-color:transparent !important; border:1px solid currentColor; border-radius:12px; box-shadow:none !important; color:inherit; display:flex; flex-direction:column;">
      <strong style="font-family:inherit; display:block; color:inherit !important; font-size:15px; line-height:1.35; margin-bottom:6px; font-weight:700;">Rodzaje sterowania taśmami LED</strong>
      <small style="font-family:inherit; display:block; color:inherit !important; opacity:.76; font-size:12px; line-height:1.4; margin-bottom:15px;">piloty, panele, WiFi i Smart Home</small>
      <a href="https://www.prescot.com.pl/pl/n/18" style="font-family:inherit; display:inline-block; min-width:142px; margin-top:auto; padding:10px 17px; border-radius:999px; background:#e94b25 !important; background-color:#e94b25 !important; color:#ffffff !important; -webkit-text-fill-color:#ffffff !important; text-decoration:none !important; text-align:center; line-height:1.2; border:0 !important; align-self:flex-start;">
        <font color="#ffffff"><span style="font-family:inherit; color:#ffffff !important; -webkit-text-fill-color:#ffffff !important; text-decoration:none !important; font-weight:700; font-size:14px;">Czytaj poradnik</span></font>
      </a>
    </div>
    <div style="font-family:inherit; min-height:190px; padding:18px; margin:0; background:none !important; background-color:transparent !important; border:1px solid currentColor; border-radius:12px; box-shadow:none !important; color:inherit; display:flex; flex-direction:column;">
      <strong style="font-family:inherit; display:block; color:inherit !important; font-size:15px; line-height:1.35; margin-bottom:6px; font-weight:700;">Jak dobrać zasilacz do taśmy i sterownika?</strong>
      <small style="font-family:inherit; display:block; color:inherit !important; opacity:.76; font-size:12px; line-height:1.4; margin-bottom:15px;">napięcie, rezerwa mocy i miejsce montażu</small>
      <a href="https://www.prescot.com.pl/pl/n/20" style="font-family:inherit; display:inline-block; min-width:142px; margin-top:auto; padding:10px 17px; border-radius:999px; background:#e94b25 !important; background-color:#e94b25 !important; color:#ffffff !important; -webkit-text-fill-color:#ffffff !important; text-decoration:none !important; text-align:center; line-height:1.2; border:0 !important; align-self:flex-start;">
        <font color="#ffffff"><span style="font-family:inherit; color:#ffffff !important; -webkit-text-fill-color:#ffffff !important; text-decoration:none !important; font-weight:700; font-size:14px;">Czytaj poradnik</span></font>
      </a>
    </div>
  </div>
</section>"""

def build_section_html(sku, pill, head, text):
    pill_clean = pill.strip()
    head_clean = head.strip()
    
    if not head_clean:
        if pill_clean:
            head_clean = pill_clean.capitalize()
        else:
            head_clean = f"Zalety i funkcje {sku}"

    text_clean = text.strip()
    text_clean = re.sub(r'^<p[^>]*>', '', text_clean)
    text_clean = re.sub(r'</p>$', '', text_clean)
    text_clean = text_clean.strip()

    if text_clean.startswith('<ul>') or text_clean.startswith('<li>'):
        return f"""<section style="font-family:inherit; margin:0 0 18px 0; padding:22px 24px; background:none !important; background-color:transparent !important; border:1px solid currentColor; border-radius:12px; color:inherit;">
  <span style="font-family:inherit; display:inline-block; margin-bottom:10px; padding:5px 12px; border-radius:999px; background:#e94b25 !important; background-color:#e94b25 !important; color:#ffffff !important; -webkit-text-fill-color:#ffffff !important; font-size:11px; font-weight:700; letter-spacing:.8px; text-transform:uppercase; line-height:1.2;">
    <font color="#ffffff">{pill_clean}</font>
  </span>
  <h3 style="font-family:inherit; margin:0 0 8px 0; background:none !important; background-color:transparent !important; color:inherit !important; font-size:22px; line-height:1.3; font-weight:700;">
    {head_clean}
  </h3>
  {text_clean}
</section>"""
    else:
        return f"""<section style="font-family:inherit; margin:0 0 18px 0; padding:22px 24px; background:none !important; background-color:transparent !important; border:1px solid currentColor; border-radius:12px; color:inherit;">
  <span style="font-family:inherit; display:inline-block; margin-bottom:10px; padding:5px 12px; border-radius:999px; background:#e94b25 !important; background-color:#e94b25 !important; color:#ffffff !important; -webkit-text-fill-color:#ffffff !important; font-size:11px; font-weight:700; letter-spacing:.8px; text-transform:uppercase; line-height:1.2;">
    <font color="#ffffff">{pill_clean}</font>
  </span>
  <h3 style="font-family:inherit; margin:0 0 8px 0; background:none !important; background-color:transparent !important; color:inherit !important; font-size:22px; line-height:1.3; font-weight:700;">
    {head_clean}
  </h3>
  <p style="font-family:inherit; margin:0; background:none !important; background-color:transparent !important; color:inherit !important; opacity:.82; font-size:14px; line-height:1.65;">
    {text_clean}
  </p>
</section>"""

def extract_scharfer_sec3(sku, platform):
    try:
        with open(INDEX_PATH, "r", encoding="utf-8") as f:
            soup = BeautifulSoup(f, "html.parser")
        view_div = soup.find("div", id=f"desc-view-{platform}-{sku}")
        if view_div:
            sections = view_div.find_all("section", recursive=False)
            if len(sections) >= 3:
                sec3 = sections[2]
                pill_span = sec3.find("span")
                head_h3 = sec3.find("h3")
                text_p = sec3.find("p")
                
                pill = pill_span.text.strip() if pill_span else "GDZIE UŻYĆ"
                head = head_h3.text.strip() if head_h3 else ""
                text = text_p.text.strip() if text_p else ""
                
                return {"pill": pill, "head": head, "text": text}
    except Exception as e:
        print(f"Error extracting section 3 for {sku} {platform}: {e}")
    return None

def process_sku(sku, category, spec_dict, badge=""):
    data = generate_description_json(sku, category, spec_dict, badge)
    if not data:
        return None
    
    results = {}
    for platform in ['wapro', 'tim', 'allegro']:
        sections = data.get(platform)
        if not sections or len(sections) < 3:
            continue
            
        # Override Section 3 for Scharfer zasilacze
        if category == 'zasilacze':
            orig_sec3 = extract_scharfer_sec3(sku, platform)
            if orig_sec3:
                sections[2] = orig_sec3
            else:
                print(f"Warning: Could not find original Section 3 for {sku} {platform}, using generated one.")
            
        desc_html = ""
        for sec in sections:
            desc_html += build_section_html(sku, sec.get('pill', ''), sec.get('head', ''), sec.get('text', ''))
            
        desc_html += blog_html_tasmy
            
        results[platform] = desc_html
        
    return results

def main():
    if os.path.exists(CHECKPOINT_PATH):
        try:
            with open(CHECKPOINT_PATH, "r", encoding="utf-8") as f:
                completed_skus = set(json.load(f))
        except Exception:
            completed_skus = set()
    else:
        completed_skus = set()

    with open(INDEX_PATH, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")
        
    cards = soup.find_all("div", class_="product-accordion")
    sku_to_cards = {}
    
    for card in cards:
        sku = card.get("data-model")
        if not sku:
            continue
        cat = get_category(sku)
        if cat in ['sterowniki', 'zasilacze', 'zlaczki', 'profile']:
            if sku not in sku_to_cards:
                badge_elem = card.find("span", class_="product-label-badge")
                badge_text = badge_elem.text.strip() if badge_elem else ""
                sku_to_cards[sku] = {
                    "category": cat,
                    "cards": [],
                    "specs": {},
                    "badge": badge_text
                }
            sku_to_cards[sku]["cards"].append(card)
            
            if not sku_to_cards[sku]["specs"]:
                spec_section = card.find("section", class_="product-parameters-section")
                if spec_section:
                    divs = spec_section.find_all("div", style=lambda v: v and "flex-direction: column" in v)
                    for d in divs:
                        spans = d.find_all("span")
                        if len(spans) >= 2:
                            k = spans[0].text.strip()
                            v = spans[1].text.strip()
                            sku_to_cards[sku]["specs"][k] = v
            
    print(f"Found {len(sku_to_cards)} unique SKUs to update.")
    
    skus_to_process = []
    for sku, info in sku_to_cards.items():
        if sku in completed_skus:
            print(f"Skipping already completed SKU: {sku}")
            continue
        skus_to_process.append((sku, info["category"], info["specs"], info["badge"]))
        
    print(f"Pending SKUs to process: {len(skus_to_process)}")
    
    if not skus_to_process:
        print("All SKUs are already processed!")
        return
 
    updated_count = 0
    for sku, cat, specs, badge in skus_to_process:
        print(f"Generating for {sku} ({cat}) [Badge: {badge}]...")
        results = process_sku(sku, cat, specs, badge)
        if not results:
            print(f"Failed to generate for SKU: {sku}")
            continue
            
        info = sku_to_cards[sku]
        for card in info["cards"]:
            for platform, new_html in results.items():
                view_div = card.find("div", id=f"desc-view-{platform}-{sku}")
                edit_textarea = card.find("textarea", id=f"textarea-{platform}-{sku}")
                
                if view_div:
                    view_div.clear()
                    new_soup = BeautifulSoup(new_html, "html.parser")
                    view_div.append(new_soup)
                    
                if edit_textarea:
                    edit_textarea.string = new_html.strip()
            
        completed_skus.add(sku)
        with open(CHECKPOINT_PATH, "w", encoding="utf-8") as f:
            json.dump(list(completed_skus), f)
            
        with open(INDEX_PATH, "w", encoding="utf-8") as f:
            f.write(str(soup))
            
        updated_count += 1
        print(f"Updated {sku} successfully ({updated_count}/{len(skus_to_process)}) and saved checkpoint.")
            
    print(f"Finished. All {len(skus_to_process)} SKUs completed.")

if __name__ == "__main__":
    main()
