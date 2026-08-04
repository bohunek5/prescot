import re

def strip_newlines_in_params(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Regex to find <small...> \n <strong...>...</strong> \n </small>
    # and replace with single line
    
    # 1. Unencoded version
    pattern_unencoded = re.compile(
        r'(<small[^>]*>)\s*(<strong[^>]*>.*?</strong>)\s*(</small>)',
        re.DOTALL
    )
    content = pattern_unencoded.sub(r'\1\2\3', content)
    
    # 2. Encoded version
    pattern_encoded = re.compile(
        r'(&lt;small[^&]*&gt;)\s*(&lt;strong[^&]*&gt;.*?&lt;/strong&gt;)\s*(&lt;/small&gt;)',
        re.DOTALL
    )
    content = pattern_encoded.sub(r'\1\2\3', content)

    # Some parameters have <br> or multiple lines. Let's see if there are other cases.
    # We should just save this.
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Stripped newlines inside small tags.")

if __name__ == '__main__':
    strip_newlines_in_params('/Users/karolbohdanowicz/my-ai-agents/prescot/index.html')
