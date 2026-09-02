#!/usr/bin/env python3
"""Build conservative one-page Prescot datasheets from the live XML catalog."""

from __future__ import annotations

import argparse
import io
import json
import re
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image as PilImage
from reportlab.lib.colors import HexColor, black, white
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader


ROOT = Path("/Users/karolbohdanowicz/my-ai-agents/prescot")
DEFAULT_MAPPING = ROOT / "exports/tim/remediation/prescot-active-positive-local-document-mapping-cleanlocks-2026-09-02.json"
DEFAULT_CATALOG = ROOT / "data/catalog.json"
DEFAULT_OUTPUT_DIR = ROOT / "tmp/pdfs/generated-prescot-profile-cards"
DEFAULT_QUEUE = ROOT / "exports/tim/remediation/prescot-profile-generated-datasheets-queue-2026-09-02.json"
FONT_REGULAR = Path("/System/Library/Fonts/Supplemental/Arial.ttf")
FONT_BOLD = Path("/System/Library/Fonts/Supplemental/Arial Bold.ttf")


def arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mapping", type=Path, default=DEFAULT_MAPPING)
    parser.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--queue-output", type=Path, default=DEFAULT_QUEUE)
    parser.add_argument("--category-root", default="Profile do taśm LED")
    parser.add_argument("--start", type=int, default=0)
    parser.add_argument("--limit", type=int, default=1)
    return parser.parse_args()


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def clean(value: object) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()


def wrap(text: str, font: str, size: float, width: float) -> list[str]:
    words = clean(text).split()
    lines: list[str] = []
    current = ""
    for word in words:
        candidate = f"{current} {word}".strip()
        if not current or pdfmetrics.stringWidth(candidate, font, size) <= width:
            current = candidate
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def draw_wrapped(pdf: canvas.Canvas, text: str, x: float, y: float, width: float, font: str, size: float, leading: float) -> float:
    pdf.setFont(font, size)
    for line in wrap(text, font, size, width):
        pdf.drawString(x, y, line)
        y -= leading
    return y


def category_label(category_root: str) -> str:
    labels = {
        "Profile do taśm LED": "Systemy profili LED",
        "Akcesoria do zasilaczy i taśm LED": "Akcesoria do instalacji LED",
        "Sterowniki LED": "Sterowanie oświetleniem LED",
        "Zasilacze LED": "Zasilanie oświetlenia LED",
        "Stateczniki": "Osprzęt do źródeł światła",
    }
    return labels.get(category_root, category_root)


def application_text(name: str, category_root: str) -> str:
    lowered = name.lower()
    if category_root == "Sterowniki LED":
        if "puszka" in lowered:
            return "Puszka montażowa do zgodnego panelu lub sterownika LED wskazanego w nazwie produktu. Przed montażem należy porównać wymiary elementu, głębokość zabudowy oraz sposób prowadzenia przewodów."
        return "Sterownik do regulacji zgodnego oświetlenia LED. Przed doborem należy porównać napięcie pracy, liczbę kanałów, maksymalny prąd i moc obciążenia oraz obsługiwany typ taśmy lub oprawy."
    if category_root == "Zasilacze LED":
        return "Zasilacz do zgodnych odbiorników LED. Napięcie wyjściowe musi odpowiadać napięciu odbiornika, a moc zasilacza należy dobrać do łącznego obciążenia z wymaganym zapasem i warunkami pracy instalacji."
    if category_root == "Stateczniki":
        return "Statecznik do zgodnego źródła światła i układu oprawy. Przed doborem należy porównać rodzaj oraz moc źródła, napięcie zasilania, sposób podłączenia i wymagany osprzęt współpracujący."
    if category_root == "Akcesoria do zasilaczy i taśm LED":
        if "złącz" in lowered or "zlacz" in lowered:
            return "Element połączeniowy do instalacji LED. Przed montażem należy potwierdzić liczbę torów, szerokość taśmy, rodzaj złącza oraz zgodność z wersją jednobarwną, RGB, RGBW lub CCT wskazaną w nazwie produktu."
        if "gniazdo" in lowered or "wtyk" in lowered:
            return "Element przyłączeniowy do instalacji LED i urządzeń zasilających. Przed montażem należy potwierdzić rozmiar złącza, liczbę torów, polaryzację oraz zgodność z przewodem i podłączanym urządzeniem."
        if "przewód" in lowered or "przewod" in lowered:
            return "Przewód do wykonywania połączeń w instalacjach LED. Liczbę żył i przekrój należy dobrać do rodzaju sygnału, obciążenia, długości odcinka oraz warunków prowadzenia instalacji."
        if "koszulk" in lowered:
            return "Element ochronny lub wykończeniowy do taśmy LED o wymiarze wskazanym w nazwie. Przed montażem należy sprawdzić zgodność szerokości taśmy, zaślepek i sposobu wprowadzenia przewodu."
        if "zaślep" in lowered or "zaslep" in lowered:
            return "Element wykończeniowy do akcesorium wskazanego w nazwie produktu. Przed montażem należy potwierdzić wymiar oraz wybrać właściwą wersję z otworem lub bez otworu."
        return "Akcesorium do wykonywania lub wykańczania instalacji LED. Przed montażem należy potwierdzić zgodność wymiarów, liczby torów, rodzaju taśmy lub złącza oraz warunków pracy instalacji."
    if "zaślep" in lowered or "zaslep" in lowered:
        return "Element wykończeniowy do profilu LED wskazanego w nazwie produktu. Przed montażem należy potwierdzić zgodność rodziny profilu, koloru oraz wersji z otworem lub bez otworu."
    if "osłon" in lowered or "oslon" in lowered:
        return "Osłona do profilu LED wskazanego w nazwie produktu. Przed montażem należy potwierdzić zgodność przekroju i rodziny profilu oraz wybrać właściwy sposób docinania."
    if "uchwyt" in lowered:
        return "Element montażowy do profilu LED wskazanego w nazwie produktu. Liczbę i rozstaw uchwytów należy dobrać do długości profilu, podłoża i warunków instalacji."
    return "Element systemu profili LED do wykonywania liniowych instalacji oświetleniowych. Taśmę LED, osłonę, zaślepki i sposób mocowania należy dobrać do rzeczywistego przekroju oraz warunków instalacji."


def safety_text(category_root: str, name: str = "") -> str:
    if category_root == "Sterowniki LED" and "puszka" in name.lower():
        return "Przed rozpoczęciem prac przy istniejącej instalacji należy odłączyć zasilanie. Puszkę trzeba osadzić stabilnie, bez uszkadzania przewodów, a wnętrze pozostawić dostępne do prawidłowego podłączenia zgodnego urządzenia."
    if category_root in {"Sterowniki LED", "Zasilacze LED", "Stateczniki"}:
        return "Przed montażem należy odłączyć zasilanie i sprawdzić napięcie, polaryzację, dopuszczalne obciążenie oraz warunki chłodzenia i ochrony przed wilgocią. Urządzenie należy podłączyć zgodnie ze schematem producenta. Montaż powinien wykonać wykwalifikowany instalator."
    if category_root == "Akcesoria do zasilaczy i taśm LED":
        return "Przed montażem należy odłączyć zasilanie i sprawdzić napięcie, polaryzację, obciążalność przewodów oraz zgodność łączonych elementów. Połączenie należy wykonać bez naprężeń i zabezpieczyć przed zwarciem. Elementy elektryczne powinny być montowane przez osobę posiadającą odpowiednie kwalifikacje."
    return "Przed montażem należy sprawdzić zgodność elementów systemu, wymiary oraz sposób mocowania. Obróbkę i montaż należy wykonywać odpowiednimi narzędziami, bez uszkadzania współpracujących elementów ani przewodów instalacji LED."


def download_image(url: str) -> bytes | None:
    if not url:
        return None
    request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 Prescot TIM datasheet builder"})
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            if response.status != 200:
                return None
            payload = response.read(12_000_000)
        image = PilImage.open(io.BytesIO(payload)).convert("RGB")
        output = io.BytesIO()
        image.save(output, format="JPEG", quality=92, optimize=True)
        return output.getvalue()
    except Exception:
        return None


def draw_image(pdf: canvas.Canvas, image_bytes: bytes, x: float, y: float, width: float, height: float) -> None:
    image = PilImage.open(io.BytesIO(image_bytes))
    source_width, source_height = image.size
    scale = min(width / source_width, height / source_height)
    target_width = source_width * scale
    target_height = source_height * scale
    pdf.drawImage(
        ImageReader(image),
        x + (width - target_width) / 2,
        y + (height - target_height) / 2,
        target_width,
        target_height,
        preserveAspectRatio=True,
        mask="auto",
    )


def build_pdf(path: Path, live: dict, product: dict, image_bytes: bytes | None, category_root: str) -> None:
    width, height = A4
    accent = HexColor("#861F5B")
    pale = HexColor("#F4EEF2")
    grey = HexColor("#555555")
    pdf = canvas.Canvas(str(path), pagesize=A4, pageCompression=1)
    pdf.setTitle(f"Karta katalogowa {live['modelHandlowy']}")
    pdf.setAuthor("PRESCOT Sp. z o.o.")
    pdf.setSubject("Karta katalogowa produktu")

    pdf.setFillColor(white)
    pdf.rect(0, 0, width, height, fill=1, stroke=0)

    pdf.setFillColor(accent)
    pdf.rect(0, height - 78, width, 78, fill=1, stroke=0)
    pdf.setFillColor(white)
    pdf.setFont("Arial-Bold", 22)
    pdf.drawString(36, height - 47, "PRESCOT")
    pdf.setFont("Arial", 10)
    pdf.drawRightString(width - 36, height - 46, "KARTA KATALOGOWA")
    pdf.drawRightString(width - 36, height - 61, category_label(category_root))

    name = clean(live.get("timName") or product.get("name"))
    y = height - 112
    pdf.setFillColor(black)
    for line in wrap(name, "Arial-Bold", 16, width - 72):
        pdf.setFont("Arial-Bold", 16)
        pdf.drawString(36, y, line)
        y -= 20

    card_top = y - 6
    image_x, image_y, image_w, image_h = 36, card_top - 156, 170, 150
    pdf.setStrokeColor(HexColor("#D8D8D8"))
    pdf.rect(image_x, image_y, image_w, image_h, fill=0, stroke=1)
    if image_bytes:
        draw_image(pdf, image_bytes, image_x + 6, image_y + 6, image_w - 12, image_h - 12)
    else:
        pdf.setFillColor(grey)
        pdf.setFont("Arial", 9)
        pdf.drawCentredString(image_x + image_w / 2, image_y + image_h / 2, "Zdjęcie produktu: prescot.com.pl")

    info_x = 226
    info_width = width - info_x - 36
    rows = [
        ("Indeks handlowy", live["modelHandlowy"]),
        ("EAN", live["ean"]),
        ("Producent", clean(product.get("producer")) or "Prescot"),
        ("Kategoria", category_label(category_root)),
    ]
    row_y = card_top - 4
    for label, value in rows:
        pdf.setFillColor(pale)
        pdf.rect(info_x, row_y - 30, info_width, 30, fill=1, stroke=0)
        pdf.setFillColor(grey)
        pdf.setFont("Arial", 8)
        pdf.drawString(info_x + 9, row_y - 11, label.upper())
        pdf.setFillColor(black)
        pdf.setFont("Arial-Bold", 10)
        pdf.drawString(info_x + 9, row_y - 24, clean(value)[:58])
        row_y -= 36

    section_y = image_y - 32
    pdf.setFillColor(accent)
    pdf.setFont("Arial-Bold", 12)
    pdf.drawString(36, section_y, "Dane produktu")
    section_y -= 18
    attributes = product.get("attributes") or {}
    excluded = {"Producent", "Kod_produktu", "Kod producenta", "Kod_producenta", "EAN", "Producent odpowiedzialny", "Podmiot odpowiedzialny", "Nazwa galerii"}
    technical = [(clean(key), clean(value)) for key, value in attributes.items() if key not in excluded and clean(value)]
    if category_root == "Sterowniki LED" and "puszka" in name.lower() and not technical:
        technical = [("Rodzaj", "Puszka montażowa do sterownika LED")]
    if category_root == "Stateczniki" and not technical:
        power = re.search(r"\b(\d+(?:[.,]\d+)?)\s*W\b", name, re.IGNORECASE)
        technical = []
        if "magnetyczny" in name.lower():
            technical.append(("Typ", "Statecznik magnetyczny"))
        if power:
            technical.append(("Moc źródła światła", f"{power.group(1).replace(',', '.')} W"))
    if not technical:
        technical = [("Rodzaj", category_label(category_root))]
    for index, (label, value) in enumerate(technical[:8]):
        if label.lower() == "wymiar" and re.fullmatch(r"\d+(?:[.,]\d+)?x\d+(?:[.,]\d+)?x\d+(?:[.,]\d+)?m", value, re.IGNORECASE):
            value = f"{value}m"
        if index % 2 == 0:
            pdf.setFillColor(HexColor("#F7F7F7"))
            pdf.rect(36, section_y - 18, width - 72, 22, fill=1, stroke=0)
        pdf.setFillColor(grey)
        pdf.setFont("Arial", 9)
        pdf.drawString(43, section_y - 10, label)
        pdf.setFillColor(black)
        pdf.setFont("Arial-Bold", 9)
        pdf.drawRightString(width - 43, section_y - 10, value[:70])
        section_y -= 22

    section_y -= 10
    pdf.setFillColor(accent)
    pdf.setFont("Arial-Bold", 12)
    pdf.drawString(36, section_y, "Zastosowanie i dobór")
    section_y -= 18
    pdf.setFillColor(black)
    section_y = draw_wrapped(pdf, application_text(name, category_root), 36, section_y, width - 72, "Arial", 9.5, 13)

    section_y -= 7
    pdf.setFillColor(accent)
    pdf.setFont("Arial-Bold", 12)
    pdf.drawString(36, section_y, "Montaż i bezpieczeństwo")
    section_y -= 18
    pdf.setFillColor(black)
    safety = safety_text(category_root, name)
    draw_wrapped(pdf, safety, 36, section_y, width - 72, "Arial", 9.5, 13)

    pdf.setStrokeColor(accent)
    pdf.line(36, 65, width - 36, 65)
    pdf.setFillColor(grey)
    pdf.setFont("Arial", 7.5)
    pdf.drawString(36, 51, "PRESCOT Sp. z o.o., ul. Wileńska 1, 11-500 Giżycko | info@prescot.com.pl")
    pdf.drawString(36, 39, f"Źródło danych: prescot.com.pl | Aktualizacja: {datetime.now().date().isoformat()}")
    pdf.drawRightString(width - 36, 39, f"Model: {live['modelHandlowy']}")
    pdf.save()


def main() -> None:
    args = arguments()
    pdfmetrics.registerFont(TTFont("Arial", str(FONT_REGULAR)))
    pdfmetrics.registerFont(TTFont("Arial-Bold", str(FONT_BOLD)))
    mapping = load(args.mapping.resolve())
    catalog = load(args.catalog.resolve())
    catalog_by_ean = {str(row.get("ean") or ""): row for row in catalog.get("products") or [] if row.get("ean")}
    candidates = [
        row for row in mapping.get("products") or []
        if row.get("categoryRoot") == args.category_root
        and int(row.get("currentDataSheetCount") or 0) == 0
        and float(row.get("stock") or 0) > 0
    ]
    candidates.sort(key=lambda row: (-float(row.get("stock") or 0), str(row.get("modelHandlowy") or "")))
    selected = candidates[max(0, args.start):max(0, args.start) + max(1, args.limit)]
    args.output_dir.mkdir(parents=True, exist_ok=True)
    args.queue_output.parent.mkdir(parents=True, exist_ok=True)

    items = []
    errors = []
    for live in selected:
        product = catalog_by_ean.get(str(live.get("ean") or ""))
        if not product or clean(product.get("manufacturerCode")) != clean(live.get("modelHandlowy")):
            errors.append({"id": live.get("pimcoreId"), "model": live.get("modelHandlowy"), "reason": "catalog_identity_mismatch"})
            continue
        filename = f"PRESCOT_karta_{re.sub(r'[^A-Za-z0-9._-]+', '_', clean(live['modelHandlowy']))}.pdf"
        destination = args.output_dir.resolve() / filename
        image_bytes = download_image(clean(product.get("image")))
        build_pdf(destination, live, product, image_bytes, args.category_root)
        items.append({
            "id": int(live["pimcoreId"]),
            "ean": clean(live["ean"]),
            "model": clean(live["modelHandlowy"]),
            "state": "active",
            "timName": clean(live["timName"]),
            "xmlStock": float(live["stock"]),
            "requireDescriptionModel": False,
            "documents": {"dataSheet": {"source": str(destination), "filename": filename}},
            "sourceUrl": clean(product.get("url")),
            "sourceImage": clean(product.get("image")),
        })

    report = {
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "readOnly": True,
        "policy": f"Generated Prescot datasheet for {args.category_root} from exact live EAN + trade model and current XML/catalog attributes; no inferred electrical parameters.",
        "categoryRoot": args.category_root,
        "mapping": str(args.mapping.resolve()),
        "catalog": str(args.catalog.resolve()),
        "counts": {"candidates": len(candidates), "selected": len(selected), "built": len(items), "errors": len(errors)},
        "items": items,
        "errors": errors,
    }
    args.queue_output.resolve().write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(args.queue_output.resolve()), "counts": report["counts"], "files": [item["documents"]["dataSheet"]["source"] for item in items]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
