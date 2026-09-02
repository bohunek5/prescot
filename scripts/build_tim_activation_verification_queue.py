#!/usr/bin/env python3
"""Build a read-only verification queue from an activation queue and workflow reports."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


parser = argparse.ArgumentParser()
parser.add_argument("--queue", required=True, type=Path)
parser.add_argument("--report", required=True, action="append", type=Path)
parser.add_argument("--output", required=True, type=Path)
args = parser.parse_args()

queue = json.loads(args.queue.read_text(encoding="utf-8"))
by_id = {int(row["id"]): row for row in queue["items"]}
states = {}
for report_path in args.report:
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

result = {
    "generatedAt": datetime.now(timezone.utc).isoformat(),
    "sourceQueue": str(args.queue),
    "sourceWorkflowReports": [str(path) for path in args.report if path.is_file()],
    "counts": {
        "total": len(items),
        "active": sum(row["expectedState"] == "active" for row in items),
        "new_for_approval": sum(row["expectedState"] == "new_for_approval" for row in items),
    },
    "items": items,
}
args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"output": str(args.output), "counts": result["counts"]}, ensure_ascii=False, indent=2))
