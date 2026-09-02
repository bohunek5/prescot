#!/usr/bin/env python3
"""Exclude active duplicates and missing-photo cards from KLUŚ buffer document writes."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path("/Users/karolbohdanowicz/my-ai-agents/prescot")
QUEUE_PATH = ROOT / "exports/tim/remediation/klus-buffer-official-documents-queue-2026-09-01.json"
ACTIVE_PATH = ROOT / "exports/tim/remediation/active-brand-offer-live-readonly-post-scharfer-2026-09-01.json"
BUFFER_PATH = ROOT / "exports/tim/remediation/buffer-current-live-readonly-after-activations-2026-09-01.json"
OUTPUT_PATH = ROOT / "exports/tim/remediation/klus-buffer-official-documents-safe-queue-2026-09-01.json"


queue = json.loads(QUEUE_PATH.read_text(encoding="utf-8"))
active = json.loads(ACTIVE_PATH.read_text(encoding="utf-8"))
buffer = json.loads(BUFFER_PATH.read_text(encoding="utf-8"))
buffer_by_id = {int(row["id"]): row for row in buffer["items"]}
active_by_model = {}
for row in active["products"]:
    if row.get("state") == "active":
        active_by_model.setdefault(row.get("model"), []).append(row)

items = []
excluded = []
for index, row in enumerate(queue["items"]):
    live_buffer = buffer_by_id[int(row["id"])]
    active_duplicates = [item for item in active_by_model.get(row["model"], []) if int(item["id"]) != int(row["id"])]
    reason = ""
    if active_duplicates:
        reason = "active_model_already_exists"
    elif not live_buffer.get("mainPhoto"):
        reason = "main_photo_missing"
    elif not live_buffer.get("ean"):
        reason = "ean_missing"
    elif live_buffer.get("state") == "active" and not live_buffer.get("timIndex"):
        reason = "inconsistent_active_without_tim_index"
    if reason:
        excluded.append({
            "originalIndex": index,
            "id": row["id"],
            "ean": row["ean"],
            "model": row["model"],
            "reason": reason,
            "activeDuplicates": [
                {"id": item["id"], "ean": item.get("ean"), "timIndex": item.get("timIndex"), "timName": item.get("timName")}
                for item in active_duplicates
            ],
        })
        continue
    items.append({**row, "originalIndex": index})

report = {
    "generatedAt": datetime.now(timezone.utc).isoformat(),
    "sourceQueue": str(QUEUE_PATH),
    "sourceActiveAudit": str(ACTIVE_PATH),
    "sourceBufferSnapshot": str(BUFFER_PATH),
    "counts": {"safe": len(items), "excluded": len(excluded)},
    "items": items,
    "excluded": excluded,
}
OUTPUT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"output": str(OUTPUT_PATH), "counts": report["counts"]}, ensure_ascii=False, indent=2))
