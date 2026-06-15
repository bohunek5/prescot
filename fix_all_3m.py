import re

with open('/Users/karolbohdanowicz/my-ai-agents/prescot/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Remove " (3m)" from badges/labels outside textareas
content = re.sub(r',\s*wariant cięty z metra \(3m\)', '', content)
content = re.sub(r'wariant cięty z metra \(3m\)', '', content)

# 2. Remove the specific sentence about "cięty z metra (3m)" globally
content = re.sub(r'Ten wariant cięty z metra \(3m\) pozwala na optymalne docięcie taśmy i dopasowanie odcinków do wymiarów blatów lub sufitów podwieszanych\.\s*', '', content, flags=re.DOTALL)
content = re.sub(r'Ten wariant cięty z metra pozwala na optymalne docięcie taśmy i dopasowanie odcinków do wymiarów blatów lub sufitów podwieszanych\.\s*', '', content, flags=re.DOTALL)

with open('/Users/karolbohdanowicz/my-ai-agents/prescot/index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Fixed globally")
