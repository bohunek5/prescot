import re

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Przyjrzyjmy się strukturze z oryginalnego zrzutu ekranu 2:
# Tam widać "100. 48EC480-050-8-NW1 [button ze strzalka w dół]".
# A niżej napis "Skopiuj kod HTML produktu (48EC480-050-8-NW)"
# I obok niego przyciski "Edytuj opis", "Kopiuj opis HTML", "EAN: BRAK"
# To sugeruje, że to NIE JEST nowo wstrzyknięty kod (który ma czyste kontrolki, zob. fix_buttons_4.py i reinject_script2.py)
# To musi być kod z PRZED ROZPOCZĘCIEM dzisiejszej sesji - stąd to pomieszanie!
# Albo to screenshot ZANIM usunąłem i przepisałem z reinject_script2.py. Zobaczmy to!

start = html.find('100. 48EC480-050-8-NW1')
print(html[start-300:start+300])

