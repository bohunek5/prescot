#!/usr/bin/env python3
"""Merge EC528 workflow results into a read-only activation verification queue."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path("/Users/karolbohdanowicz/my-ai-agents/prescot")
DATA = ROOT / "exports/tim/remediation"
QUEUE_PATH = DATA / "buffer-ec528-family4-activation-queue-2026-09-01.json"
OUTPUT_PATH = DATA / "buffer-ec528-family4-activation-verification-queue-2026-09-01.json"
REPORT_PATHS = [
    DATA / "buffer-ec528-family4-activation-pilot-live-2026-09-01.json",
    DATA / "buffer-ec528-family4-activation-next3-live-2026-09-01.json",
]

queue = json.loads(QUEUE_PATH.read_text(encoding="utf-8"))
by_id = {int(row["id"]): row for row in queue["items"]}
states = {}
for report_path in REPORT_PATHS:
    if not report_path.is_file():
        continue
    report = json.loads(report_path.read_text(encoding="utf-8"))
    for result in report.get("results", []):
        if result.get("status") in {"activated", "submitted_for_acceptance"}:
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
    "sourceWorkflowReports": [str(path) for path in REPORT_PATHS if path.is_file()],
    "counts": {
        "total": len(items),
        "active": sum(row["expectedState"] == "active" for row in items),
        "new_for_approval": sum(row["expectedState"] == "new_for_approval" for row in items),
    },
    "items": items,
}
OUTPUT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"output": str(OUTPUT_PATH), "counts": report["counts"]}, ensure_ascii=False, indent=2))
