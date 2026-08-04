mad_models = ['PR-MAD36-1224', 'PR-MAD60-1224', 'PR-MAD100-1224', 'PR-MAD150-1224', 'PR-MAD200-1224', 'PR-MAD300-1224']
tabs = ['tim', 'allegro', 'shoper']

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

missing = []
for model in mad_models:
    for tab in tabs:
        if f'id="btn-edit-{tab}-{model}"' not in content:
            missing.append(f"{tab}-{model}")

print("Missing controls for:", missing)
