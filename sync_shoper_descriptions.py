#!/usr/bin/env python3
"""Keep Shoper descriptions simple and free of presentation-specific HTML."""

import html
import re
from pathlib import Path

from bs4 import BeautifulSoup

from generate_wcob_models import WCOB_MODELS, build_shoper_description


INDEX_PATH = Path(__file__).with_name("index.html")
GUIDE_TITLES = {
    "https://www.prescot.com.pl/pl/n/12": "Jak dobrać taśmę LED do mieszkania?",
    "https://www.prescot.com.pl/pl/n/15": "Jak dobrać profil aluminiowy do taśmy LED?",
    "https://www.prescot.com.pl/pl/n/16": "Montaż taśmy LED na zewnątrz",
    "https://www.prescot.com.pl/pl/n/23": "Jak czytać parametry taśmy LED?",
}


def replace_exactly_once(source, pattern, replacement, label):
    updated, count = re.subn(pattern, replacement, source, count=1, flags=re.DOTALL)
    if count != 1:
        raise RuntimeError(f"Expected one {label}, found {count}")
    return updated


def view_pattern(sku):
    escaped_sku = re.escape(sku)
    return (
        rf'(<div class="model-block" id="desc-view-shoper-{escaped_sku}">\n?)'
        rf'(.*?)'
        rf'(\n?</div>\n?<div class="(?:desc-edit|edit-block)" id="desc-edit-shoper-{escaped_sku}")'
    )


def textarea_pattern(sku):
    escaped_sku = re.escape(sku)
    return (
        rf'(<textarea class="edit-textarea" id="textarea-shoper-{escaped_sku}"[^>]*>)'
        rf'.*?'
        rf'(</textarea>)'
    )


def simplify_description(source):
    fragment = BeautifulSoup(source, "html.parser")

    for blog_grid in fragment.select(".blog-grid"):
        links = []
        for link in blog_grid.find_all("a"):
            href = link.get("href")
            card = link.find_parent("div")
            card_heading = card.find("strong") if card else None
            title = GUIDE_TITLES.get(href)
            if not title and card_heading:
                title = card_heading.get_text(" ", strip=True)
            links.append((href, title or link.get_text(" ", strip=True)))
        section = fragment.find("section")
        if section and links:
            heading = fragment.new_tag("h3")
            heading.string = "Powiązane poradniki"
            section.append(heading)
            for href, title in links:
                paragraph = fragment.new_tag("p")
                paragraph.append("- ")
                link = fragment.new_tag("a", href=href)
                link.string = title
                paragraph.append(link)
                section.append(paragraph)
        blog_grid.decompose()

    for link in fragment.find_all("a", href=True):
        title = GUIDE_TITLES.get(link.get("href"))
        if title and link.get_text(" ", strip=True) == "Czytaj poradnik":
            link.string = title

    for tag in fragment.find_all(True):
        for attribute in ("style", "class", "color", "width", "height", "align"):
            tag.attrs.pop(attribute, None)
        if tag.name == "font":
            tag.unwrap()
        elif tag.name == "b":
            tag.name = "strong"

    return str(fragment).strip()


def set_description(page, sku, description):
    page = replace_exactly_once(
        page,
        view_pattern(sku),
        lambda match: match.group(1) + description + match.group(3),
        f"Shoper view for {sku}",
    )
    return replace_exactly_once(
        page,
        textarea_pattern(sku),
        lambda match: match.group(1) + html.escape(description) + match.group(2),
        f"Shoper textarea for {sku}",
    )


def main():
    page = INDEX_PATH.read_text(encoding="utf-8")

    for model in WCOB_MODELS:
        page = set_description(page, model["id"], build_shoper_description(model))

    matches = list(
        re.finditer(
            r'<div class="model-block" id="desc-view-shoper-([^"]+)">\n?'
            r'(.*?)'
            r'\n?</div>\n?<div class="(?:desc-edit|edit-block)" id="desc-edit-shoper-\1"',
            page,
            flags=re.DOTALL,
        )
    )
    simplified = 0
    for match in matches:
        sku, description = match.group(1), match.group(2)
        needs_cleanup = any(
            marker in description
            for marker in ("style=", "<font", "blog-grid")
        )
        if not needs_cleanup:
            continue
        page = set_description(page, sku, simplify_description(description))
        simplified += 1

    INDEX_PATH.write_text(page, encoding="utf-8")
    print(
        f"Updated {len(WCOB_MODELS)} WCOB descriptions and simplified "
        f"{simplified} other Shoper descriptions"
    )


if __name__ == "__main__":
    main()
