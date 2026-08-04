import re

with open('/Users/karolbohdanowicz/my-ai-agents/prescot/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

replacements = [
    (r'\bkablem\b', 'przewodem'),
    (r'\bKablem\b', 'Przewodem'),
    (r'\bkabla\b', 'przewodu'),
    (r'\bKabla\b', 'Przewodu'),
    (r'\bkabel\b', 'przewód'),
    (r'\bKabel\b', 'Przewód'),
    (r'\bkable\b', 'przewody'),
    (r'\bKable\b', 'Przewody'),
    (r'\bkablowym\b', 'przewodowym'),
    (r'\bKablowym\b', 'Przewodowym')
]

for pattern, repl in replacements:
    content = re.sub(pattern, repl, content)

with open('/Users/karolbohdanowicz/my-ai-agents/prescot/index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Kabel -> Przewód replacement completed.")
