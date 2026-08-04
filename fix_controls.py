import re

html_path = 'index.html'
with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Make search-container sticky
if 'position: sticky; top: 0px; z-index: 1001;' not in html:
    html = html.replace('.search-container" style="margin-bottom: 25px;"', '.search-container" style="margin-bottom: 25px; position: sticky; top: 0px; z-index: 1001; background: #f8f9fa; padding-top: 10px; padding-bottom: 10px;"')

# Also adjust main-tabs and sub-tabs if we added search-container at top 0
html = html.replace('.main-tabs {\n  position: sticky;\n  top: 10px;', '.main-tabs {\n  position: sticky;\n  top: 80px;')
html = html.replace('.sub-tabs {\n  position: sticky;\n  top: 90px;', '.sub-tabs {\n  position: sticky;\n  top: 155px;')

models_eans = {
    'PR-MAD300-1224': '5905475368127',
    'PR-MAD200-1224': '5905475368110',
    'PR-MAD150-1224': '5905475368103',
    'PR-MAD100-1224': '5905475368097',
    'PR-MAD60-1224': '5905475368080',
    'PR-MAD36-1224': '5905475368073'
}

platforms = ['wapro', 'tim', 'allegro', 'shoper']

for model, ean in models_eans.items():
    for platform in platforms:
        # Check if already has product-controls
        pattern_check = re.compile(rf'<div class="product-body">\s*<div class="product-controls">.*?<div class="model-block" id="desc-view-{platform}-{model}">', re.DOTALL)
        if pattern_check.search(html):
            continue # already added
        
        controls = f"""
<div class="product-controls">
<button class="control-btn btn-edit" id="btn-edit-{platform}-{model}" onclick="toggleEdit('{platform}', 'zasilacze', '{model}')">Edytuj opis</button>
<button class="control-btn btn-save" id="btn-save-{platform}-{model}" onclick="saveDescription('{platform}', 'zasilacze', '{model}')" style="display: none;">Zapisz opis</button>
<button class="control-btn btn-copy" onclick="copyDescriptionHtml('{platform}', '{model}', this)" style="border-color: #f59e0b; color: #f59e0b;" title="Kopiuj opis HTML">Kopiuj opis HTML</button>
<button class="control-btn btn-ean" onclick="navigator.clipboard.writeText('{ean}'); this.innerText='Skopiowano!'; setTimeout(()=>this.innerText='EAN: {ean}', 2000);" style="border-color: #0ea5e9; color: #0ea5e9;" title="Skopiuj EAN">EAN: {ean}</button>
<span class="control-status" id="status-{platform}-{model}"></span>
</div>
"""
        
        # We need to inject `controls` right after `<div class="product-body">` for this specific model and platform.
        # However, the structure is `<div class="product-accordion" data-model="PR-MAD36-1224"> ... <div class="product-body"><div class="model-block" id="desc-view-wapro-PR-MAD36-1224">`
        # Because we generated it in a loop for each platform, we can find the exact match:
        target = f'<div class="product-body"><div class="model-block" id="desc-view-{platform}-{model}">'
        replacement = f'<div class="product-body">{controls}<div class="model-block" id="desc-view-{platform}-{model}">'
        html = html.replace(target, replacement)

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html)
print("Updated successfully")
