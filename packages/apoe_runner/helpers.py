from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def read_json(path: str | Path) -> Any:
    """Read JSON file and return decoded object."""
    resolved = Path(path)
    return json.loads(resolved.read_text(encoding="utf-8"))


__all__ = ["read_json"]
