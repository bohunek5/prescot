import re

with open('/Users/karolbohdanowicz/Downloads/opisy KAROL v2.html', 'r', encoding='utf-8') as f:
    v2_content = f.read()

v2_blocks = re.findall(r'<!-- START ([^ ]+) -->(.*?)<!-- KONIEC \1 -->', v2_content, re.DOTALL)

paragraphs = []
for sku, html in v2_blocks:
    # extract h3
    h3s = re.findall(r'<h3[^>]*>(.*?)</h3>', html, re.DOTALL)
    for h3 in h3s: paragraphs.append(h3.strip())
    # extract p
    ps = re.findall(r'<p[^>]*>(.*?)</p>', html, re.DOTALL)
    for p in ps: paragraphs.append(p.strip())

unique_ps = list(set(paragraphs))
unique_ps.sort(key=len, reverse=True)

print(f"Total unique paragraphs and h3s: {len(unique_ps)}")

with open('unique_paragraphs.txt', 'w', encoding='utf-8') as f:
    for p in unique_ps:
        f.write(p + '\n---\n')

