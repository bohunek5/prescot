import re

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

tabs = ['wapro', 'tim', 'allegro', 'shoper']
models = ['PR-MAD36-1224', 'PR-MAD60-1224']

for model in models:
    for tab in tabs:
        # check if EAN button exists for this tab and model
        idx = content.find(f'id="desc-view-{tab}-{model}"')
        if idx != -1:
            # Look backwards for product controls
            controls_start = content.rfind('<div class="product-controls">', 0, idx)
            if controls_start != -1 and idx - controls_start < 1500:
                controls = content[controls_start:idx]
                if "btn-ean" in controls:
                    print(f"EAN FOUND for {tab} - {model}")
                else:
                    print(f"EAN MISSING for {tab} - {model}")
            else:
                print(f"CONTROLS MISSING ENTIRELY for {tab} - {model}")
        else:
            print(f"MODEL BLOCK MISSING for {tab} - {model}")
