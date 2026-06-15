import re

with open('/Users/karolbohdanowicz/my-ai-agents/prescot/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add CSS for mobile fonts
css_addition = """
@media (max-width: 768px) {
  .product-body p, .edit-textarea p { font-size: 16px !important; line-height: 1.6 !important; }
  .product-body h3, .edit-textarea h3 { font-size: 20px !important; }
  .product-body span, .edit-textarea span { font-size: 12px !important; }
  .wrap { padding: 15px 10px !important; }
}
</style>"""

content = content.replace('</style>', css_addition)

# 2. Remove "lanie wody" (repetitive fluff sentences)
fluff_patterns = [
    r"Taśmę montuj na profilu aluminiowym, który odprowadza ciepło i stabilizuje linię światła\.",
    r"Cięcie wykonuj w polach co \d+mm, żeby dopasować odcinek do wymiaru półki, wnęki lub profilu\.",
    r"Optymalna długość \d+ metrów na jednej rolce świetnie sprawdza się przy średnich realizacjach sufitowych i oświetleniu meblowym\.",
    r"Zasilacz dobieraj pod \d+V i sumę wszystkich odcinków, nie pod pierwszy fragment taśmy\.",
    r"Ciepła biel dobrze wygląda przy drewnie, beżach, kamieniu i we wnętrzach klasycznych lub rustykalnych\.",
    r"Naturalna biel to najbezpieczniejszy wybór, który nie przekłamuje kolorów otoczenia – idealny do pracy i codziennych przestrzeni\.",
    r"Zimna biel świetnie podkreśla nowoczesność, stal, szkło i surowe, techniczne przestrzenie\.",
    r"Kolor biały jest tutaj chłodny i stymulujący do skupienia\.",
    r"Ta wersja jest nastawiona na czystą linię w profilu aluminiowym\.",
    r"Diody zabezpieczone przed typowym zużyciem termicznym działają dłużej i stabilniej\.",
    r"Wyselekcjonowane podzespoły pozwalają na długotrwałą pracę bez szybkiego spadku jasności\.",
    r"Wąski podkład pozwala na montaż w płytkich i dyskretnych frezach meblowych\.",
    r"Model zaprojektowany pod kątem ekonomii pracy, gdzie liczy się długość linii bez nadmiernego obciążenia zasilacza\.",
    r"Oznacza to mniejsze spadki napięć i równą jasność na całym odcinku\.",
    r"Zagęszczenie diod tworzy niemal gładką linię światła bez ciemnych przerw\.",
    r"To idealny kompromis między jasnością a zużyciem prądu\.",
    r"Szczególnie polecana tam, gdzie taśma ma być głównym oświetleniem blatu lub wnęki\.",
    r"Jest to parametr kluczowy przy projektowaniu oświetlenia architektonicznego i dekoracyjnego\.",
    r"W takich rozwiązaniach liczy się najwyższa skuteczność świetlna i brak awaryjności\.",
    r"Dzięki grubszej miedzi ciepło jest optymalnie odprowadzane\.",
    r"Ten model to bezpieczny standard do większości domowych zastosowań\.",
    r"Strumień \d+lm/m pozwala ocenić, czy taśma ma tylko budować klimat, czy realnie doświetlać blat, półkę, wnękę albo produkt w ekspozycji\.",
    r"W połączeniu z matowym kloszem punkty świetlne praktycznie zlewają się w jedną, gładką płaszczyznę\.",
    r"Szerszy podkład ułatwia rozpraszanie ładunku cieplnego generowanego przez gęste ułożenie diod\.",
    r"Wysoki współczynnik oddawania barw gwarantuje naturalne kolory oświetlanych przedmiotów\."
]

for pattern in fluff_patterns:
    content = re.sub(pattern + r"\s*", "", content)

# Remove empty paragraphs that might be left after removing sentences
content = re.sub(r'<p[^>]*>\s*</p>', '', content)

with open('/Users/karolbohdanowicz/my-ai-agents/prescot/index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Done")
