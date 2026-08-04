import re
with open('ultimate_injector_v3.py', 'r', encoding='utf-8') as f:
    text = f.read()

# For 48V
old_48 = """</textarea>
</div>
<div class="product-controls">"""
new_48 = """</textarea>
<div class="product-controls">"""

old_48_2 = """<span class="control-status" id="status-wapro-{model}"></span>
</div>
</div>'''"""
new_48_2 = """<span class="control-status" id="status-wapro-{model}"></span>
</div>
</div>
</div>'''"""

text = text.replace(old_48, new_48)
text = text.replace(old_48_2, new_48_2)

with open('ultimate_injector_v4.py', 'w', encoding='utf-8') as f:
    f.write(text)
