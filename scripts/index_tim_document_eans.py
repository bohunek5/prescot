#!/usr/bin/env python3
import json
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

from pypdf import PdfReader

ROOT = Path("/Users/karolbohdanowicz/Desktop/_PRESCOT/_2026/TIM.PL/TIM - karty ce")
OUTPUT = Path("/Users/karolbohdanowicz/my-ai-agents/prescot/exports/tim/remediation/local-document-ean-index-2026-09-01.json")
EAN_RE = re.compile(r"(?<!\d)(\d{13})(?!\d)")


def inspect(path: Path):
    try:
        reader = PdfReader(str(path))
        text = "\n".join((page.extract_text() or "") for page in reader.pages)
        return str(path), sorted(set(EAN_RE.findall(text))), ""
    except Exception as error:
        return str(path), [], f"{type(error).__name__}: {error}"


paths = sorted(ROOT.rglob("*.pdf"))
records = []
with ThreadPoolExecutor(max_workers=8) as executor:
    futures = [executor.submit(inspect, path) for path in paths]
    for future in as_completed(futures):
        path, eans, error = future.result()
        records.append({"path": path, "eans": eans, "error": error})

by_ean = {}
for record in records:
    for ean in record["eans"]:
        by_ean.setdefault(ean, []).append(record["path"])
for paths_for_ean in by_ean.values():
    paths_for_ean.sort()

payload = {
    "generatedAt": datetime.now(timezone.utc).isoformat(),
    "root": str(ROOT),
    "counts": {
        "pdfs": len(paths),
        "indexed": sum(not row["error"] for row in records),
        "failed": sum(bool(row["error"]) for row in records),
        "uniqueEans": len(by_ean),
    },
    "byEan": dict(sorted(by_ean.items())),
    "errors": [row for row in sorted(records, key=lambda item: item["path"]) if row["error"]],
}
OUTPUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"output": str(OUTPUT), **payload["counts"]}, ensure_ascii=False))
