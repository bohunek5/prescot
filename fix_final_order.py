import re
import sys
import html

with open('index.html', 'r', encoding='utf-8') as f:
    text = f.read()

# Zastapmy ten bledny uklad
parts = text.split('<div class="product-accordion" data-model="')
out_html = parts[0]

for p in parts[1:]:
    model_id = p.split('">')[0]
    
    if '<div class="controls-bar"' in p:
        # P to zawartosc po 'data-model="MODEL"'
        # Wyciągnijmy controls-bar
        controls_start = p.find(f'<div class="controls-bar" id="controls-wapro-{model_id}">')
        if controls_start != -1:
            controls_end = p.find('</div>', p.find('</span>', controls_start)) + 6
            controls_html = p[controls_start:controls_end]
            
            # Zmieńmy klasę na product-controls i usuńmy id (lub zostawmy, chociaż stary miał?)
            controls_html = controls_html.replace('class="controls-bar"', 'class="product-controls"')
            # w starym nie bylo id na divie, ale to nie szkodzi
            
            # Usuńmy go z dołu
            p = p[:controls_start] + p[controls_end:]
            
            # Dodajmy na poczatku product-body
            body_start = p.find('<div class="product-body">')
            if body_start != -1:
                insert_pos = body_start + len('<div class="product-body">\n')
                # w starym bylo: <div class="product-controls">\n...
                p = p[:insert_pos] + controls_html + '\n' + p[insert_pos:]
                
    out_html += '<div class="product-accordion" data-model="' + model_id + '">\n' + p

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(out_html)

print("Done fixing order.")

