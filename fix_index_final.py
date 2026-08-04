import re
import sys

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Szukamy uszkodzonych bloków, czyli modeli 48EC480 i innych świeżych,
# które mają ucięte tagi na końcu desc-view.
# Ostatni tag w desc-view powinien być </section>
# a potem zamknięcie desc-view czyli </div>
# Więc powinno być: </section>\n</div>
# U mnie wstrzyknięto:
# <div class="model-block" id="desc-view-wapro-{model}">{raw_html}</div>

def fix_html():
    global html
    # Znajdzmy wszystkie wstrzykniete produkty (od 100 wzwyz)
    parts = html.split('<div class="product-accordion" data-model="')
    out_html = parts[0]
    
    for part in parts[1:]:
        model_id = part.split('">')[0]
        
        # Sprawdzmy, czy to jeden ze swiezo wstrzyknietych (48EC480... lub inne)
        # Błędem jest brak </section> na koncu wewnatrz desc-view.
        # desc-view kończy się na </div>, zaraz przed <textarea
        
        if '48EC480' in model_id or 'HPD-' in model_id:
            # Wewnatrz desc-view mamy braki
            # Szukamy <textarea id="desc-wapro-{model_id}"
            
            # Najpierw policzmy otwarte/zamkniete divy i sekcje miedzy poczatkiem desc-view a textarea
            desc_start = part.find(f'<div class="model-block" id="desc-view-wapro-{model_id}">')
            textarea_start = part.find(f'<textarea id="desc-wapro-{model_id}"')
            
            if desc_start != -1 and textarea_start != -1:
                # Obejmijmy calosc model-block wlacznie z poczatkowym <div class="model-block...">
                desc_content = part[desc_start:textarea_start]
                
                # Zliczmy sekcje wewnatrz
                sec_open = desc_content.count('<section')
                sec_close = desc_content.count('</section>')
                
                # Zliczmy divy wewnatrz (uwaga na zewnetrzny div desc-view!)
                div_open = desc_content.count('<div')
                div_close = desc_content.count('</div')
                
                # Zamiast parsowania po prostu doklejmy brakujace!
                missing_sections = sec_open - sec_close
                missing_divs = div_open - div_close
                
                # Wklejamy na koncu zawartosci, PRZED zamknieciem model-block
                # Zobaczmy czy oryginalny desc_content konczy sie </div> (bo to koniec model-block)
                # Tak, part[desc_start:textarea_start] konczy sie na </div>\n
                
                # Jesli missing_divs > 0, to nawet model-block nie jest domkniety poprawnie (albo brakuje wewnetrznego diva)
                
                # Wytnijmy to co mamy
                content = desc_content
                
                # Jeśli kończy się na </div> (z model-block), usuńmy ten jeden div na moment, żeby wrzucić brakujące, i dodajmy go z powrotem.
                if content.strip().endswith('</div>'):
                    inner_content = content[:content.rfind('</div>')]
                else:
                    inner_content = content # To sie nie powinno zdarzyc
                    
                inner_sec_open = inner_content.count('<section')
                inner_sec_close = inner_content.count('</section>')
                inner_div_open = inner_content.count('<div')
                inner_div_close = inner_content.count('</div')
                
                # Ile brakuje?
                diff_sec = inner_sec_open - inner_sec_close
                diff_div = inner_div_open - inner_div_close
                
                add_str = ""
                if diff_div > 0:
                    add_str += '</div>\n' * diff_div
                if diff_sec > 0:
                    add_str += '</section>\n' * diff_sec
                
                new_desc_content = inner_content + add_str + '</div>\n'
                
                # Aktualizujemy part!
                part = part[:desc_start] + new_desc_content + part[textarea_start:]
        
        out_html += '<div class="product-accordion" data-model="' + part

    html = out_html

fix_html()

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)
