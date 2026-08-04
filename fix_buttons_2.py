import re
import sys

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Szukamy nowo dodanych elementow (np. data-model="48EC480..." i "Z05-096...")
# ktore na koncu desc-view NIE MAJA panelu z przyciskami
# <div class="model-block" id="desc-view-wapro-48EC480-050-8-NW1">

# Zeby byc bezpiecznym, usunmy to smieciowe zamkniecie z nawiasami:
html = re.sub(r'\[Skopiuj kod HTML produktu \([^)]+\)\](<br>)?', '', html)
html = re.sub(r'\[Edytuj opis\].*?\[EAN: BRAK\]', '', html)
html = html.replace('[Edytuj opis]        [Kopiuj opis HTML]        [EAN: BRAK]', '')
html = html.replace('Edytuj opis\n        Kopiuj opis HTML\n        EAN: BRAK', '')

# Przejdziemy po wszystkich <div class="product-accordion" i zrobimy to porzadnie
def fix_controls():
    global html
    parts = html.split('<div class="product-accordion" data-model="')
    out_html = parts[0]
    
    for part in parts[1:]:
        model_id = part.split('">')[0]
        
        # Sprawdz, czy part posiada '<div class="product-controls">' (oryginalne maja 'controls-bar')
        # Zobaczylem w starym kodzie ze to wyglada tak:
        # <div class="product-controls">
        # <button class="control-btn btn-edit" id="btn-edit-wapro-XXX"...
        if '<div class="product-controls">' not in part and 'controls-bar' not in part:
            # Brakuje kontrolek! 
            # Wstawimy je tuz przed ZAMKNIECIEM <div class="product-body">
            # Zwykle kod ciala to: ... </section></div>\n</div></div>
            # Poszukajmy przedostatniego </div>, zeby to wpiac.
            controls_html = f"""
<div class="product-controls">
<button class="control-btn btn-edit" id="btn-edit-wapro-{model_id}" onclick="toggleEdit('wapro', 'tasmy', '{model_id}')">Edytuj opis</button>
<button class="control-btn btn-save" id="btn-save-wapro-{model_id}" onclick="saveDescription('wapro', 'tasmy', '{model_id}')" style="display: none;">Zapisz opis</button>
<button class="control-btn btn-copy" onclick="copyDescriptionHtml('wapro', '{model_id}', this)" style="border-color: #f59e0b; color: #f59e0b;" title="Kopiuj opis HTML">Kopiuj opis HTML</button>
<button class="control-btn btn-ean" onclick="navigator.clipboard.writeText('BRAK'); this.innerText='Skopiowano!'; setTimeout(()=>this.innerText='EAN: BRAK', 2000);" style="border-color: #0ea5e9; color: #0ea5e9;" title="Skopiuj EAN">EAN: BRAK</button>
<span class="control-status" id="status-wapro-{model_id}"></span>
</div>"""
            # Znajdz gdzie konczy sie cialo (czyli ostatnie </section></div>)
            # Uzyjemy re.sub na tym part'cie, by wrzucic to tuz przed zakonczeniem product-body
            # part to caly blok az do nastepnego akordeonu, np <div class="product-body">...</div></div>
            # Sprobujmy podmienic ostatnie </div></div> na </div> \n controls_html \n </div>
            
            # Najpierw wywalmy ewentualne stare przyciski w tekscie:
            clean_part = re.sub(r'Edytuj opis.*?Kopiuj opis HTML.*?EAN: BRAK', '', part, flags=re.DOTALL)
            
            # Gdzie jest zamek product body?
            # To powinnno byc </section></div>, co konczy desc-view
            # Potem mozna dac kontrole.
            idx = clean_part.rfind('</div>\n</div>')
            if idx != -1:
                 clean_part = clean_part[:idx] + '</div>\n' + controls_html + '\n</div>' + clean_part[idx+12:]
            elif clean_part.endswith('</div></div>\n'):
                 clean_part = clean_part[:-13] + '</div>\n' + controls_html + '\n</div>\n'
            elif clean_part.endswith('</div></div>'):
                 clean_part = clean_part[:-12] + '</div>\n' + controls_html + '\n</div>'
                 
            part = clean_part
            
        out_html += '<div class="product-accordion" data-model="' + part

    html = out_html

fix_controls()

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)
