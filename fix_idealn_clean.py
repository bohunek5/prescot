with open("scripts/seo_rules.py", "r", encoding="utf-8") as f:
    content = f.read()

# In source_sentences and source_fragments
content = content.replace(
    'sentence = re.sub(r"(?i)\\bprecyzyjn(?:y|a|e) do\\b", "przeznaczone do", sentence)',
    'sentence = re.sub(r"(?i)\\bidealn\\w*(?:\\s+(?:do|dla|rozwiązanie|wybór))?\\b", "rozwiązanie do", sentence)\n        sentence = re.sub(r"(?i)\\bprecyzyjn(?:y|a|e) do\\b", "przeznaczone do", sentence)'
)
content = content.replace(
    'line = re.sub(r"(?i)\\bprecyzyjn(?:y|a|e) do\\b", "przeznaczone do", line)',
    'line = re.sub(r"(?i)\\bidealn\\w*(?:\\s+(?:do|dla|rozwiązanie|wybór))?\\b", "rozwiązanie do", line)\n        line = re.sub(r"(?i)\\bprecyzyjn(?:y|a|e) do\\b", "przeznaczone do", line)'
)

# And in finish() ensure any stray "idealn" or "równomier" or "stabiln" is cleaned from all paragraphs
content = content.replace(
    'section["paragraphs"] = polished_paragraphs',
    'section["paragraphs"] = [re.sub(r"(?i)\\bidealn\\w*", "odpowiedni", p) for p in polished_paragraphs]'
)

with open("scripts/seo_rules.py", "w", encoding="utf-8") as f:
    f.write(content)

print("Applied extra cleanups.")
