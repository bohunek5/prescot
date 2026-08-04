import re
with open('ultimate_injector_v3.py', 'r', encoding='utf-8') as f:
    text = f.read()

# Change how we clean raw_html
# We want to remove the last </div> which closed the id="..." div
# AND we want to make sure it is balanced.
old_code = """        # Remove trailing </div> of product-wrapper
        raw_html = raw_html[:raw_html.rfind('</div>')]
        raw_html = raw_html.strip()"""

new_code = """        # Remove trailing </div> of id="..." div AND product-wrapper
        raw_html = raw_html[:raw_html.rfind('</div>')]
        raw_html = raw_html[:raw_html.rfind('</div>')]
        raw_html = raw_html.strip()
        
        # Now balance the raw_html just in case
        d_op = raw_html.count('<div')
        d_cl = raw_html.count('</div')
        s_op = raw_html.count('<section')
        s_cl = raw_html.count('</section')
        while s_cl < s_op:
            raw_html += '\\n</section>'
            s_cl += 1
        while d_cl < d_op:
            raw_html += '\\n</div>'
            d_cl += 1"""

text = text.replace(old_code, new_code)
with open('ultimate_injector_v3.py', 'w', encoding='utf-8') as f:
    f.write(text)
