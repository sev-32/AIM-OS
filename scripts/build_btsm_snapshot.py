#!/usr/bin/env python3
"""Stub CLI for exporting BTSM nodes and edges into the snapshots directory.

Future work will import `schemas.mpd` and `schemas.edge`, pull data from the CMC
store, and write bitemporal audit packs. For now we just guarantee the target
folder exists and remind operators to wire the real exporter.
"""

from pathlib import Path

SNAPSHOT_DIR = Path(__file__).resolve().parent.parent / "snapshots"


def main() -> None:
    SNAPSHOT_DIR.mkdir(exist_ok=True)
    placeholder = SNAPSHOT_DIR / "README.md"
    if not placeholder.exists():
        placeholder.write_text(
            "BTSM snapshots will be written here once the exporter is wired.\n"
            "Expected format: JSON list of MPD nodes + edge list with bitemporal fields.\n"
        )
    print(f"[TODO] Export BTSM data into {SNAPSHOT_DIR}")  # noqa: T201


if __name__ == "__main__":
    main()
