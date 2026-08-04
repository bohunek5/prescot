import re
import sys

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Let's see what is inside one of the bad product-body
# Actually, the user's screenshot showed:
# [Skopiuj kod HTML produktu (48EC480-050-8-NW1)]
# Edytuj opis   Kopiuj opis HTML   EAN: BRAK
# This looks like there is a <div class="product-wrapper"> ... inside it?
# In my earlier `fix_buttons_2.py`, I successfully injected `<div class="product-controls">`?
# Let's check what it looks like now.

start = html.find('<div class="product-accordion" data-model="48EC480-050-8-NW1">')
end = html.find('<div class="product-accordion" data-model="48EC480-050-8-NW">', start)
print(html[start:end])
