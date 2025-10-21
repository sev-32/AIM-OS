from __future__ import annotations

import json
from pathlib import Path

from cmc_service.memory_store import MemoryStore
from cmc_service.models import AtomContent, AtomCreate

DATA_DIR = Path(__file__).resolve().parents[1] / "data"
RAW_EXCERPT = Path("analysis/raw/A Total System of Memory.txt")


def main() -> None:
    store = MemoryStore(DATA_DIR)

    text = RAW_EXCERPT.read_text(encoding="utf-8", errors="ignore")[:1000]
    atom = store.create_atom(
        AtomCreate(
            modality="text",
            content=AtomContent(inline=text, media_type="text/plain"),
            tags={"source": 1.0, "doc": 1.0},
            metadata={"path": str(RAW_EXCERPT)},
        )
    )
    snapshot = store.create_snapshot(note="Phase1 demo")

    print("Atom created:")
    print(json.dumps(atom.to_record(), indent=2))
    print("\nSnapshot manifest:")
    print(json.dumps(snapshot.to_record(), indent=2))


if __name__ == "__main__":
    main()
