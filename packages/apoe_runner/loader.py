from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

import yaml


def load_plan(path: Path) -> Dict[str, Any]:
    """Load an ACL plan from disk."""
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("Plan root must be a mapping")
    data.setdefault("id", path.stem)
    return data


__all__ = ["load_plan"]
