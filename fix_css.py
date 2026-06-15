with open("/Users/karolbohdanowicz/my-ai-agents/prescot/index.html", "r", encoding="utf-8") as f:
    content = f.read()

css_addition = """
@media (max-width: 768px) {
  .product-body p, .edit-textarea p { font-size: 16px !important; line-height: 1.6 !important; }
  .product-body h3, .edit-textarea h3 { font-size: 20px !important; }
  .product-body span, .edit-textarea span { font-size: 12px !important; }
  .wrap { padding: 15px 10px !important; }
}
</style>"""

if "@media (max-width: 768px)" not in content:
    content = content.replace("</style>", css_addition)

with open("/Users/karolbohdanowicz/my-ai-agents/prescot/index.html", "w", encoding="utf-8") as f:
    f.write(content)
