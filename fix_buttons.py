import re
import sys

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Usunąć zbedny tag [Skopiuj kod HTML...] - ale zauwazylem, ze dodany kod 
# wcale nie ma controls-bar! W poprzednim skrypcie nie dodałem <div class="product-controls">!
# Poprawmy to przez wyrazenia regularne.

def fix_added_items():
    global html
    
    # Najpierw znajdujemy wszystkie nowe elementy dodane na koncu
    # Kazdy wyglada np. <div class="model-block" id="desc-view-wapro-48EC480-050-8-NW1">[Skopiuj kod HTML produktu (48EC480-050-8-NW)]<br>...

    # Wyrzućmy ten tekst [Skopiuj kod HTML produktu (xxx)]
    html = re.sub(r'\[Skopiuj kod HTML produktu \([^)]+\)\](?:<br>)?', '', html)

    # Dalej: te nowo dodane akordeony NIE MAJĄ panelu sterowania "product-controls" na koncu.
    # A każdy z nich kończy się na </section></div>\n</div></div>
    # My potrzebujemy </section></div>\n<div class="product-controls">\n...przyciski...\n</div>\n</div></div>
    
    # Szukamy modeli z nowych blokow, np. data-model="48EC480..."
    # Lepszy sposob - przejedziemy przez cale cialo nowo dodanych elementow.
    # W nowo dodanych brakuje <div class="product-controls">, a stary kod go ma.
    
    pass

fix_added_items()

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)
