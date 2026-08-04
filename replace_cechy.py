import re

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

old_p_start = "Najważniejsze cechy serii: stabilne napięcie wyjściowe, wysoka wydajność transferu"
new_p = "Najważniejsze cechy serii: stabilne napięcie wyjściowe, genialna funkcja Smart Auto (samodzielnie detektuje 12V/24V), wysoka wydajność transferu, praca przy <strong style=\"font-family: inherit; color: inherit !important;\">100% obciążenia</strong>, zabezpieczenie przed przeciążeniem i zwarciem, ultra-cienka obudowa. Przy planowaniu instalacji dobierz odpowiedni przekrój przewodu do obciążenia i długości prowadzenia. Poniżej 1m COB zaleca się ustawić odpowiednie napięcie (stałe 12V lub 24V) za pomocą pinów na zasilaczu."

mad_models = ['PR-MAD36-1224', 'PR-MAD60-1224', 'PR-MAD100-1224', 'PR-MAD150-1224', 'PR-MAD200-1224', 'PR-MAD300-1224']

# We just replace any paragraph containing old_p_start inside PR-MAD models with new_p.
# Actually, the old paragraph might just be `Najważniejsze cechy serii: stabilne napięcie wyjściowe, wysoka wydajność transferu...`
# Let's do a regex to replace the text inside the <p> that starts with "Najważniejsze cechy serii:" for these models.

def replace_for_model(content, model):
    # Find all occurrences of the model's tech params
    pattern_view = fr'(<span style="color: #ffffff;">Parametry techniczne {model}</span>.*?</section>)'
    pattern_edit = fr'(&lt;span style="color: #ffffff;"&gt;Parametry techniczne {model}&lt;/span&gt;.*?&lt;/section&gt;)'
    
    def repl(m):
        block = m.group(1)
        # Find the Najwazniejsze cechy paragraph text and replace it.
        # It could be encoded or unencoded.
        block = re.sub(r'Najważniejsze cechy serii:.*?(</p>|&lt;/p&gt;)', new_p + r'\1', block, flags=re.DOTALL)
        return block

    content = re.sub(pattern_view, repl, content, flags=re.DOTALL)
    content = re.sub(pattern_edit, repl, content, flags=re.DOTALL)
    return content

for model in mad_models:
    content = replace_for_model(content, model)

# Let's also check if Zasilacze Scharfer is anywhere and rename to Zasilacze LED
content = content.replace("Zasilacze Scharfer", "Zasilacze LED")
content = content.replace("Zasilacze SCHARFER", "Zasilacze LED")
content = content.replace("ZASILACZE SCHARFER", "ZASILACZE LED")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated Najważniejsze cechy serii and renamed Scharfer to LED.")

