#!/usr/bin/env python3
"""Merge successful KLUŚ workflow reports into a read-only verification queue."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path("/Users/karolbohdanowicz/my-ai-agents/prescot")
QUEUE_PATH = ROOT / "exports/tim/remediation/klus-buffer-activation-queue-2026-09-01.json"
OUTPUT_PATH = ROOT / "exports/tim/remediation/klus-buffer-activation-verification-queue-2026-09-01.json"


queue = json.loads(QUEUE_PATH.read_text(encoding="utf-8"))
by_id = {int(row["id"]): row for row in queue["items"]}
reports = sorted((ROOT / "exports/tim/remediation").glob("klus-buffer-activation-*-live-2026-09-01.json"))
states = {}
sources = []
for report_path in reports:
    report = json.loads(report_path.read_text(encoding="utf-8"))
    sources.append(str(report_path))
    for result in report.get("results", []):
        if result.get("status") not in {"activated", "submitted_for_acceptance"}:
            continue
        states[int(result["id"])] = str(result.get("afterState") or "")

items = []
for object_id, expected_state in states.items():
    source = by_id[object_id]
    items.append({
        "id": object_id,
        "ean": source["ean"],
        "model": source["model"],
        "price": source["price"],
        "expectedState": expected_state,
        "requiredRelations": source["requiredRelations"],
    })

report = {
    "generatedAt": datetime.now(timezone.utc).isoformat(),
    "sourceQueue": str(QUEUE_PATH),
    "sourceWorkflowReports": sources,
    "counts": {
        "total": len(items),
        "active": sum(row["expectedState"] == "active" for row in items),
        "new_for_approval": sum(row["expectedState"] == "new_for_approval" for row in items),
    },
    "items": items,
}
OUTPUT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"output": str(OUTPUT_PATH), "counts": report["counts"]}, ensure_ascii=False, indent=2))
