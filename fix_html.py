import re
import sys

def fix_html(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Fix sticky search and tabs
    # Make search sticky
    if 'style="margin-bottom: 25px;"' in content:
        content = content.replace(
            '<div class="search-container" style="margin-bottom: 25px;">',
            '<div class="search-container" style="margin-bottom: 25px; position: sticky; top: 0; z-index: 1001; background: #fff; padding-top: 15px; padding-bottom: 10px;">'
        )
    # Update main-tabs top
    content = re.sub(
        r'(\.main-tabs\s*\{\s*position:\s*sticky;\s*top:\s*)80px(;\s*z-index:\s*1000;)',
        r'\g<1>80px\g<2>',  # Keep at 80px? If search bar takes space, we can adjust. Let's make it 85px.
        content
    )
    # Update sub-tabs top
    content = re.sub(
        r'(\.sub-tabs\s*\{\s*position:\s*sticky;\s*top:\s*)155px(;\s*z-index:\s*999;)',
        r'\g<1>155px\g<2>', 
        content
    )
    
    # Actually wait, if the search bar is sticky, it will cover the top.
    # The search bar height is roughly 60px (padding 16px top/bottom + borders).
    content = re.sub(
        r'(\.main-tabs\s*\{\s*position:\s*sticky;\s*top:\s*)\d+px(;\s*z-index:\s*1000;)',
        r'\g<1>80px\g<2>',
        content
    )
    content = re.sub(
        r'(\.sub-tabs\s*\{\s*position:\s*sticky;\s*top:\s*)\d+px(;\s*z-index:\s*999;)',
        r'\g<1>160px\g<2>',
        content
    )

    # 2. Add product-controls for PR-MAD in tim, allegro, shoper
    mad_models = ['PR-MAD36-1224', 'PR-MAD60-1224', 'PR-MAD100-1224', 'PR-MAD150-1224', 'PR-MAD200-1224', 'PR-MAD300-1224']
    eans = {}
    for model in mad_models:
        ean_match = re.search(fr'navigator\.clipboard\.writeText\(\'(\d+)\'\).*?EAN: \1.*?id="status-wapro-{model}"', content, re.DOTALL)
        if ean_match:
            eans[model] = ean_match.group(1)
        else:
            eans[model] = ''

    tabs = ['tim', 'allegro', 'shoper']
    for model in mad_models:
        for tab in tabs:
            pattern = fr'(<div class="product-body">)(<div class="model-block" id="desc-view-{tab}-{model}">)'
            ean = eans[model]
            ean_btn = f'<button class="control-btn btn-ean" onclick="navigator.clipboard.writeText(\'{ean}\'); this.innerText=\'Skopiowano!\'; setTimeout(()=>this.innerText=\'EAN: {ean}\', 2000);" style="border-color: #0ea5e9; color: #0ea5e9;" title="Skopiuj EAN">EAN: {ean}</button>' if ean else ''
            
            controls_html = f'''<div class="product-controls">
<button class="control-btn btn-edit" id="btn-edit-{tab}-{model}" onclick="toggleEdit('{tab}', 'zasilacze', '{model}')">Edytuj opis</button>
<button class="control-btn btn-save" id="btn-save-{tab}-{model}" onclick="saveDescription('{tab}', 'zasilacze', '{model}')" style="display: none;">Zapisz opis</button>
<button class="control-btn btn-copy" onclick="copyDescriptionHtml('{tab}', '{model}', this)" style="border-color: #f59e0b; color: #f59e0b;" title="Kopiuj opis HTML">Kopiuj opis HTML</button>
{ean_btn}
<span class="control-status" id="status-{tab}-{model}"></span>
</div>'''
            if f'id="btn-edit-{tab}-{model}"' not in content:
                content = re.sub(pattern, rf'\1\n{controls_html}\n\2', content)

    # 3. Add "Najważniejsze cechy serii" paragraph to all PR-MAD models
    # We will find the closing </div></div> of the grid, which occurs right before </section> (in view) or &lt;/section&gt; (in textarea)
    # The grid starts after `Parametry techniczne {model}`
    
    extra_paragraph = '''<p style="font-family: inherit; margin: 16px 0 0 0; background: none !important; background-color: transparent !important; color: inherit !important; opacity: .82; font-size: 14px; line-height: 1.65;">
Najważniejsze cechy serii: stabilne napięcie wyjściowe, genialna funkcja Smart Auto (samodzielnie detektuje 12V/24V), wysoka wydajność transferu, praca przy <strong style="font-family: inherit; color: inherit !important;">100% obciążenia</strong>, zabezpieczenie przed przeciążeniem i zwarciem, ultra-cienka obudowa. Przy planowaniu instalacji dobierz odpowiedni przekrój przewodu do obciążenia i długości prowadzenia. Poniżej 1m COB zaleca się ustawić odpowiednie napięcie (stałe 12V lub 24V) za pomocą pinów na zasilaczu.
</p>'''
    
    extra_paragraph_encoded = extra_paragraph.replace('<', '&lt;').replace('>', '&gt;')

    all_tabs = ['wapro', 'tim', 'allegro', 'shoper']
    for model in mad_models:
        for tab in all_tabs:
            # Add to desc-view
            view_marker = f'<span style="color: #ffffff;">Parametry techniczne {model}</span>'
            if view_marker in content:
                # Find the next </section> after view_marker
                start_idx = content.find(view_marker)
                end_idx = content.find('</section>', start_idx)
                if end_idx != -1:
                    # We inject the extra_paragraph right before </section>
                    # But only if it's not already there
                    section_content = content[start_idx:end_idx]
                    if 'Najważniejsze cechy serii' not in section_content:
                        content = content[:end_idx] + extra_paragraph + '\n' + content[end_idx:]

            # Add to desc-edit textarea
            edit_marker = f'&lt;span style="color: #ffffff;"&gt;Parametry techniczne {model}&lt;/span&gt;'
            if edit_marker in content:
                # Find the next &lt;/section&gt; after edit_marker
                start_idx = content.find(edit_marker)
                end_idx = content.find('&lt;/section&gt;', start_idx)
                if end_idx != -1:
                    section_content = content[start_idx:end_idx]
                    if 'Najważniejsze cechy serii' not in section_content:
                        content = content[:end_idx] + extra_paragraph_encoded + '\n' + content[end_idx:]

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Done applying fixes.")

if __name__ == '__main__':
    fix_html('/Users/karolbohdanowicz/my-ai-agents/prescot/index.html')
