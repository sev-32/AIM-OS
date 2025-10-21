"""Utility helpers for emitting SEG witness records."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional
from uuid import uuid4


def _default_seg_dir() -> Path:
    repo_root = Path(__file__).resolve().parents[2]
    return repo_root / "packages" / "cmc_service" / "data" / "seg"


def write_witness(
    payload: Dict[str, Any],
    *,
    seg_dir: Optional[Path] = None,
    filename: str = "witnesses.jsonl",
) -> Path:
    """Append a SEG witness payload as JSON lines.

    Args:
        payload: JSON-serialisable payload describing the witnessed event.
        seg_dir: Optional override directory for SEG witness storage.
        filename: Name of the JSONL file relative to seg_dir.

    Returns:
        Path to the file that was written.
    """
    directory = seg_dir or _default_seg_dir()
    directory.mkdir(parents=True, exist_ok=True)
    file_path = directory / filename
    hydrated = {
        "witness_id": payload.get("witness_id", f"seg:witness:{uuid4()}"),
        "recorded_at": datetime.now(timezone.utc).isoformat(),
        **payload,
    }
    with file_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(hydrated, ensure_ascii=False) + "\n")
    return file_path


__all__ = ["write_witness"]
