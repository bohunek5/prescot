import os

files = ['old_index.html', 'index.html']
css_to_add = """
@media (max-width: 768px) {
  .product-model { font-size: 21px !important; }
  .product-label-badge { font-size: 15px !important; padding: 6px 14px !important; }
  .product-info { gap: 16px !important; }
  .product-trigger { padding: 22px 18px !important; }
}
"""

for file in files:
    with open(file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if ".product-model { font-size: 21px" not in content:
        content = content.replace("</style>", f"{css_to_add}\n</style>")
        with open(file, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Updated CSS in {file}")
    else:
        print(f"Already updated {file}")
