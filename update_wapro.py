import re

with open("/Users/karolbohdanowicz/my-ai-agents/prescot/index.html", "r", encoding="utf-8") as f:
    content = f.read()

# Find all TIM textareas
tim_pattern = r'<textarea[^>]*id="desc-view-tim-([^"]+)"[^>]*>(.*?)</textarea>'
tim_matches = re.findall(tim_pattern, content, flags=re.DOTALL)

print(f"Found {len(tim_matches)} TIM descriptions.")

# Replace WAPRO textareas with TIM's content
for sku, tim_desc in tim_matches:
    wapro_pattern = rf'(<textarea[^>]*id="desc-view-wapro-{sku}"[^>]*>)(.*?)(</textarea>)'
    
    def replacer(match):
        return match.group(1) + tim_desc + match.group(3)
        
    content = re.sub(wapro_pattern, replacer, content, flags=re.DOTALL)

with open("/Users/karolbohdanowicz/my-ai-agents/prescot/index.html", "w", encoding="utf-8") as f:
    f.write(content)

print("Updated WAPRO descriptions to match TIM.")
