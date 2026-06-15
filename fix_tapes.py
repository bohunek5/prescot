import re

with open('/Users/karolbohdanowicz/my-ai-agents/prescot/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# We only want to process textareas for tapes/connectors (IDs not starting with A0)
def clean_tape_text(match):
    textarea_html = match.group(0)
    
    # Remove bad phrases
    textarea_html = re.sub(r'\(3m\)', '', textarea_html)
    textarea_html = re.sub(r',\s*wariant cięty z metra', '', textarea_html)
    textarea_html = re.sub(r'wariant cięty z metra\s*', '', textarea_html)
    textarea_html = re.sub(r'Ten pozwala na optymalne docięcie taśmy i dopasowanie odcinków do wymiarów blatów lub sufitów podwieszanych\.', '', textarea_html)
    textarea_html = re.sub(r'Ten wariant cięty z metra pozwala na optymalne docięcie taśmy i dopasowanie odcinków do wymiarów blatów lub sufitów podwieszanych\.', '', textarea_html)
    
    # Also clean any leftover "odcinek 3m" or similar if they slipped in
    textarea_html = re.sub(r'odcinek 3m', 'odcinek', textarea_html)
    
    # Fix double spaces or empty parentheses that might have been created
    textarea_html = re.sub(r'\s{2,}', ' ', textarea_html)
    
    return textarea_html

# Apply substitution only to textareas whose IDs do not contain 'A0'
# (The KLUŚ profiles start with A0, e.g., A01587)
content = re.sub(r'<textarea class="edit-textarea" id="textarea-[a-z]+-(?!A0)[^"]*">.*?</textarea>', clean_tape_text, content, flags=re.DOTALL)

with open('/Users/karolbohdanowicz/my-ai-agents/prescot/index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Fixed tape text")
