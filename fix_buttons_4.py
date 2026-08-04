import re
import sys

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

def clean_and_fix():
    global html
    # Split by accordion
    parts = html.split('<div class="product-accordion" data-model="')
    out_html = parts[0]
    
    for part in parts[1:]:
        model_id = part.split('">')[0]
        
        # O kurcze, widzę, że do "part" dorzuciło się mnóstwo syfu typu:
        # <div class="product-wrapper">
        # <button class="copy-btn" onclick="copyHtml('48EC480-050-8-NW')">Skopiuj kod HTML produktu (48EC480-050-8-NW)</button>
        # <div id="48EC480-050-8-NW">
        # To są znaczniki ze starego pliku wygenerowanego z opisami, których w ogóle nie powinno tu być. 
        # Powinien być CZYSTY HTML do wklejenia w <textarea>. Widać, że oryginalne skrypty to źle wrzuciły.
        
        # W starych (prawidłowych) produktach, struktura to:
        # <div class="product-accordion" data-model="xxx">
        #   <button class="product-trigger">...</button>
        #   <div class="product-body">
        #      <div class="model-block" id="desc-view-wapro-xxx"> ... (caly czysty HTML) ... </div>
        #      <textarea id="desc-wapro-xxx" style="display:none;"> ... (ten sam html wylistowany i zescape'owany) ... </textarea>
        #      <div class="product-controls"> ... przyciski ... </div>
        #   </div>
        # </div>
        
        # Widzę że nowo wklejone elementy NIE MAJĄ w ogóle <textarea id="desc-wapro-xxx">! 
        # Zamiast tego mają ucieknięty kod HTML ( &lt;h3 style=... ) wrzucony po prostu do jakiegoś diva.
        # Moje dodawanie było mocno nieprawidłowe.
        pass

# Usunę wszystkie nowo dodane z index.html i wstrzyknę poprawnie od nowa.
def remove_new_injections():
    global html
    
    # Znajdz gdzie sie zaczynają nowe. Nowe miały numery 100, 101... zaczynały się od "100. 48EC480-050-8-NW1"
    # Pierwszy dodany model to data-model="48EC480-050-8-NW1"
    start_new = html.find('<div class="product-accordion" data-model="48EC480-050-8-NW1">')
    
    # Usuwamy je stamtad do końca sekcji wapro-tasmy
    if start_new != -1:
        # Zobaczmy gdzie konczy sie wapro-tasmy (tuz przed id="wapro-sterowniki")
        end_section = html.find('<div class="sub-tab-panel" id="wapro-sterowniki">', start_new)
        
        # Zachowajmy poprawne zamkniecie
        html = html[:start_new] + '</div>\n' + html[end_section:]
    
remove_new_injections()

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)
