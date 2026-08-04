import re

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Zastąpmy wszystkie dziwne struktury na końcu produktów na te właściwe (jeśli są 2 razy, albo jest źle)
# Sprawdźmy, gdzie jest problem z wizualizacją wg screenshota.
# Na screenie widać że produkty mają ucieknięty (pokazany) kod HTML. To dlatego, że wrzucono go w model-block jako tekst,
# a nie jako wyrenderowany HTML! A dlaczego?
# Sprawdźmy to!
start = html.find('<div class="model-block" id="desc-view-wapro-48EC480-050-8-NW1">')
end = html.find('</section>', start)
print(html[start:end+50])
