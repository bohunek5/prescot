#!/usr/bin/env python3

import argparse
from datetime import datetime
import glob
import json
import os
import re

import pdfplumber


def normalize(value):
    return " ".join(str(value or "").split()).casefold()


def extract_card(path):
    with pdfplumber.open(path) as pdf:
        page_text = pdf.pages[0].extract_text() or ""
    text = " ".join(page_text.split())
    supplier_match = re.search(
        r"Nazwa dostawcy lub znak towarowy:\s*(.*?)\s+Adres dostawcy:", text, re.I
    )
    model_match = re.search(
        r"Identyfikator modelu:\s*(.*?)\s+Rodzaj źródła światła", text, re.I
    )
    return {
        "supplier": supplier_match.group(1).strip() if supplier_match else "",
        "modelIdentifier": model_match.group(1).strip() if model_match else "",
    }


parser = argparse.ArgumentParser()
parser.add_argument("--input", default="data/eprel-candidates.json")
parser.add_argument("--catalog", default="data/catalog.json")
parser.add_argument("--pdf-dir", default="/tmp/pdfs/prescot-eprel")
parser.add_argument("--aliases", default="data/eprel-model-aliases.json")
parser.add_argument("--output", default="data/eprel-candidates.json")
args = parser.parse_args()

with open(args.input, encoding="utf-8") as handle:
    candidates = json.load(handle)
with open(args.catalog, encoding="utf-8") as handle:
    catalog = json.load(handle)
try:
    with open(args.aliases, encoding="utf-8") as handle:
        aliases = json.load(handle).get("aliases", {})
except FileNotFoundError:
    aliases = {}
aliases = {normalize(code): value for code, value in aliases.items()}

products_by_key = {product["key"]: product for product in catalog["products"]}
cards = {}
for path in glob.glob(os.path.join(args.pdf_dir, "*.pdf")):
    cards[os.path.splitext(os.path.basename(path))[0]] = extract_card(path)

status_counts = {
    "verified_exact_model": 0,
    "verified_packaging_variant": 0,
    "review_variant_model": 0,
    "blocked_model_mismatch": 0,
    "blocked_missing_official_pdf": 0,
}
for product_key, assignment in candidates["products"].items():
    product = products_by_key[product_key]
    card = cards.get(str(assignment.get("eprelId", "")))
    if not card or not card["modelIdentifier"]:
        status = "blocked_missing_official_pdf"
    else:
        code = normalize(product.get("manufacturerCode"))
        model = normalize(card["modelIdentifier"])
        alias = aliases.get(code)
        if code == model:
            status = "verified_exact_model"
        elif (
            alias
            and str(alias.get("eprelId", "")) == str(assignment.get("eprelId", ""))
            and normalize(alias.get("modelIdentifier")) == model
        ):
            status = "verified_packaging_variant"
        elif code and model and (code.startswith(model) or model.startswith(code)):
            status = "review_variant_model"
        else:
            status = "blocked_model_mismatch"
    assignment.update(
        {
            "status": status,
            "officialSupplier": card["supplier"] if card else "",
            "officialModelIdentifier": card["modelIdentifier"] if card else "",
            "catalogManufacturerCode": product.get("manufacturerCode", ""),
            "verifiedFromOfficialPdf": bool(card),
            "packagingVariantOf": card["modelIdentifier"] if status == "verified_packaging_variant" else "",
        }
    )
    status_counts[status] += 1

candidates["meta"].update(
    {
        "verifiedAt": datetime.now().astimezone().isoformat(timespec="seconds"),
        "officialPdfsChecked": len(cards),
        "modelStatusCounts": status_counts,
        "status": "official_pdf_model_check_completed",
        "note": (
            "Do automatycznego użycia dopuszczone są wpisy verified_exact_model oraz "
            "jawnie zatwierdzone verified_packaging_variant. Inne warianty wymagają "
            "dowodu producenta, a niedopasowania są zablokowane."
        ),
    }
)

with open(args.output, "w", encoding="utf-8") as handle:
    json.dump(candidates, handle, ensure_ascii=False, indent=2)
    handle.write("\n")

print(
    "EPREL modele: "
    f"{status_counts['verified_exact_model']} zgodnych, "
    f"{status_counts['verified_packaging_variant']} wariantów długościowych, "
    f"{status_counts['review_variant_model']} wariantów do decyzji, "
    f"{status_counts['blocked_model_mismatch']} niedopasowanych, "
    f"{status_counts['blocked_missing_official_pdf']} bez PDF."
)
