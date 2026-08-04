import os
with open('ultimate_injector_v2.py', 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace("'tasmy-cob-48v-opisy.html'", "'../tasmy-cob-48v-opisy.html'")
text = text.replace("'rozdzielacze-opisy.html'", "'../rozdzielacze-opisy.html'")

with open('ultimate_injector_v2.py', 'w', encoding='utf-8') as f:
    f.write(text)
