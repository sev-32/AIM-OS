#!/usr/bin/env python3
"""Summarise SEG witness entries and highlight changes for governance."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict


KEYS_TO_COMPARE = ["correlation_id", "witness_id", "constraint_proof_hash", "score"]


def format_diff(current: Dict[str, Any], previous: Dict[str, Any] | None) -> str:
    if not previous:
        return "no previous entry"
    changes = []
    for key in KEYS_TO_COMPARE:
        cur = current.get(key)
        prev = previous.get(key)
        if cur != prev:
            changes.append(f"{key}: {prev} -> {cur}")
    return "; ".join(changes) if changes else "no changes"


def main() -> None:
    seg_dir = Path("packages/cmc_service/data/seg")
    files = sorted(seg_dir.glob("plan_*.jsonl"))
    if not files:
        print("No SEG witness files found.", file=sys.stderr)
        sys.exit(1)

    print("SEG witness summary:")
    for file in files:
        lines = file.read_text(encoding="utf-8").splitlines()
        if not lines:
            print(f"  {file.name}: <empty file>", file=sys.stderr)
            sys.exit(1)
        try:
            latest = json.loads(lines[-1])
            previous = json.loads(lines[-2]) if len(lines) > 1 else None
        except json.JSONDecodeError as exc:
            print(f"  {file.name}: failed to parse JSON ({exc})", file=sys.stderr)
            sys.exit(1)
        event = latest.get("event")
        correlation_id = latest.get("correlation_id", "n/a")
        witness_id = latest.get("witness_id", "n/a")
        diff = format_diff(latest, previous)
        print(f"  {file.name}: event={event} correlation_id={correlation_id} witness_id={witness_id}")
        print(f"    diff: {diff}")


if __name__ == "__main__":
    main()
