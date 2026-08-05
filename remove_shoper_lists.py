import re

file_path = '/Users/karolbohdanowicz/my-ai-agents/prescot/index.html'

with open(file_path, 'r', encoding='utf-8') as f:
    html = f.read()

def replace_lists(text):
    # Convert <li>...</li> to <p>- ...</p>
    text = re.sub(r'<li>(.*?)</li>', r'<p>- \1</p>', text, flags=re.DOTALL | re.IGNORECASE)
    # Remove <ul> and </ul>
    text = re.sub(r'<ul[^>]*>', '', text, flags=re.IGNORECASE)
    text = re.sub(r'</ul>', '', text, flags=re.IGNORECASE)
    return text

def process_match(m):
    prefix = m.group(1)
    content = m.group(2)
    suffix = m.group(3)
    content = replace_lists(content)
    return prefix + content + suffix

# Process view blocks for shoper
html = re.compile(r'(<div class="model-block" id="desc-view-shoper-[^"]+">)(.*?)(</div>\s*<div class="edit-block")', re.DOTALL).sub(process_match, html)

def replace_escaped_lists(text):
    text = re.sub(r'&lt;li&gt;(.*?)&lt;/li&gt;', r'&lt;p&gt;- \1&lt;/p&gt;', text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'&lt;ul[^&]*&gt;', '', text, flags=re.IGNORECASE)
    text = re.sub(r'&lt;/ul&gt;', '', text, flags=re.IGNORECASE)
    return text

def process_textarea_match(m):
    prefix = m.group(1)
    content = m.group(2)
    suffix = m.group(3)
    content = replace_escaped_lists(content)
    return prefix + content + suffix

# Process textarea blocks for shoper
html = re.compile(r'(<textarea class="edit-textarea" id="textarea-shoper-[^"]+"[^>]*>)(.*?)(</textarea>)', re.DOTALL).sub(process_textarea_match, html)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(html)
