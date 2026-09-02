#!/usr/bin/env python3
"""Build Scharfer technical cards with the current Hungarian EAN range.

The supplied Polish cards are raster-only PDFs.  This script preserves every
page pixel and replaces only the two EAN values in the top-right information
panel.  It does not alter the product specifications or source files.
"""

from __future__ import annotations

import hashlib
import json
import argparse
from pathlib import Path

import fitz


SOURCE_DIR = Path(
    "/Users/karolbohdanowicz/Desktop/_PRESCOT/_2026/TIM.PL/"
    "Karty katalogowe/ZASILACZE/Scharfer/Karty PL"
)
OUTPUT_ROOT = Path(__file__).resolve().parents[1] / "output/pdf"
FONT_PATH = Path("/System/Library/Fonts/Supplemental/Arial Bold.ttf")

NEW_EAN_BY_POWER = {
    "18": ("5999863091001", "5999863091018"),
    "20": ("5999863091025", "5999863091032"),
    "30": ("5999863091049", "5999863091063"),
    "45": ("5999863091056", "5999863091070"),
    "60": ("5999863091087", "5999863091094"),
    "100": ("5999863091100", "5999863091117"),
    "150": ("5999863091124", "5999863091131"),
    "200": ("5999863091148", "5999863091155"),
    "300": ("5999863091162", "5999863091179"),
    "400": ("5999863091186", "5999863091193"),
}

TIM_EAN_BY_POWER = {
    "18": ("5905475360008", "5905475360015"),
    "20": ("5905475360039", "5905475360022"),
    "30": ("5905475360046", "5905475360053"),
    "45": ("5905475360077", "5905475360060"),
    "60": ("5905475360084", "5905475360091"),
    "100": ("5905475360114", "5905475360107"),
    "150": ("5905475360121", "5905475360138"),
    "200": ("5905475360145", "5905475360152"),
    "300": ("5905475360176", "5905475360169"),
    "400": ("5905475364433", "5905475364440"),
}

# Coordinates in the original A4-ish PDF user space.  The patch covers the two
# model/EAN rows.  Redrawing the models also corrects a source typo in SCH-45PL,
# where the header was copied from the 18 W card.
IDENTITY_PATCH = fitz.Rect(350.0, 78.0, 570.0, 109.5)
MODEL_ROWS = (
    fitz.Rect(351.0, 79.7, 447.0, 94.0),
    fitz.Rect(351.0, 95.1, 447.0, 109.4),
)
EAN_ROWS = (
    fitz.Rect(449.0, 79.7, 570.0, 94.0),
    fitz.Rect(449.0, 95.1, 570.0, 109.4),
)
PANEL_BACKGROUND = (247 / 255, 248 / 255, 248 / 255)
PRESCOT_ORANGE = (232 / 255, 89 / 255, 50 / 255)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build_card(
    power: str,
    eans: tuple[str, str],
    output_dir: Path,
    filename_suffix: str,
    metadata_label: str,
) -> dict[str, object]:
    source = SOURCE_DIR / f"SCH-{power}PL.pdf"
    destination = output_dir / f"SCH-{power}PL-{filename_suffix}.pdf"
    if not source.is_file():
        raise FileNotFoundError(source)

    document = fitz.open(source)
    if len(document) != 1:
        raise ValueError(f"{source.name}: oczekiwano jednej strony, jest {len(document)}")
    page = document[0]
    if abs(page.rect.width - 595.2) > 1 or abs(page.rect.height - 834.72) > 1:
        raise ValueError(f"{source.name}: nieoczekiwany format strony {page.rect}")

    page.draw_rect(IDENTITY_PATCH, color=None, fill=PANEL_BACKGROUND, overlay=True)
    font_name = "ArialBold"
    page.insert_font(fontname=font_name, fontfile=str(FONT_PATH))
    models = (f"SCH-{power}-12", f"SCH-{power}-24")
    for model_row, ean_row, model, ean in zip(MODEL_ROWS, EAN_ROWS, models, eans):
        for row, value in ((model_row, model), (ean_row, ean)):
            remaining = page.insert_textbox(
                row,
                value,
                fontname=font_name,
                fontsize=10.4,
                color=PRESCOT_ORANGE,
                align=fitz.TEXT_ALIGN_CENTER,
                overlay=True,
            )
            if remaining < 0:
                raise ValueError(f"{source.name}: {value} nie mieści się w polu")

    document.set_metadata({
        **document.metadata,
        "title": f"Scharfer SCH-{power} - karta techniczna PL - {metadata_label}",
        "subject": f"Karta techniczna: {metadata_label}",
    })
    document.save(destination, garbage=4, deflate=True, clean=True)
    document.close()

    check = fitz.open(destination)
    checked_rect = check[0].rect if len(check) == 1 else fitz.Rect()
    if (
        len(check) != 1
        or abs(checked_rect.width - 595.2) > 1
        or abs(checked_rect.height - 834.72) > 1
    ):
        raise ValueError(f"{destination.name}: błąd walidacji strony")
    check.close()

    return {
        "power": power,
        "models": list(models),
        "eans": list(eans),
        "source": str(source),
        "output": str(destination),
        "sourceSha256": sha256(source),
        "outputSha256": sha256(destination),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ean-set", choices=("new", "tim-current"), default="new")
    args = parser.parse_args()
    if not FONT_PATH.is_file():
        raise FileNotFoundError(FONT_PATH)
    if args.ean_set == "new":
        ean_map = NEW_EAN_BY_POWER
        output_dir = OUTPUT_ROOT / "scharfer-new-ean-2026-09-01"
        suffix = "nowe-EAN"
        purpose = "TIM Scharfer technical cards with the current Hungarian EAN range"
        label = "aktualne EAN dostawcy"
    else:
        ean_map = TIM_EAN_BY_POWER
        output_dir = OUTPUT_ROOT / "scharfer-tim-current-ean-2026-09-01"
        suffix = "EAN-TIM"
        purpose = "TIM Scharfer technical cards matching the EAN currently locked on active TIM cards"
        label = "EAN aktualnie zapisane w TIM"
    output_dir.mkdir(parents=True, exist_ok=True)
    items = [build_card(power, eans, output_dir, suffix, label) for power, eans in ean_map.items()]
    manifest = {
        "generatedAt": "2026-09-01",
        "eanSet": args.ean_set,
        "purpose": purpose,
        "changedArea": "model identifiers and EAN values in the identity panel only",
        "items": items,
    }
    manifest_path = output_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wygenerowano {len(items)} kart w {output_dir}")
    print(manifest_path)


if __name__ == "__main__":
    main()
