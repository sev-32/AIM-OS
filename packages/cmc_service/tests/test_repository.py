# goals: [KR-1.1, KR-1.3, KR-3.1]
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from cmc_service.models import Atom, AtomContent, AtomCreate, Snapshot, SnapshotStats, WitnessStub
from cmc_service.repository import AtomRepository, SQLiteConfig


def test_repository_roundtrip(tmp_path: Path) -> None:
    """Test atom and snapshot insertion/retrieval via SQLite."""
    db_path = tmp_path / "test.db"
    config = SQLiteConfig(path=db_path)
    repo = AtomRepository(config)

    # Create test atom
    atom = Atom(
        id="test-atom-1",
        modality="text",
        content=AtomContent(inline="Hello, SQLite!", media_type="text/plain"),
        hash="abc123",
        created_at=datetime(2025, 1, 1, 12, 0, 0, 0, tzinfo=timezone.utc),
        tags={"test": 1.0, "demo": 0.5},
        metadata={"source": "test"},
        witness=WitnessStub(correlation_id="test-corr"),
    )

    # Insert atom
    repo.insert_atom(atom)

    # Fetch atoms
    fetched = repo.fetch_atoms(limit=10)
    assert len(fetched) == 1
    assert fetched[0].id == "test-atom-1"
    assert fetched[0].content.inline == "Hello, SQLite!"
    assert fetched[0].tags["test"] == 1.0
    assert fetched[0].metadata["source"] == "test"

    # Test tag filtering
    tag_filtered = repo.fetch_atoms(tag="test", limit=10)
    assert len(tag_filtered) == 1
    assert tag_filtered[0].id == "test-atom-1"

    # Create snapshot
    snapshot = Snapshot(
        id="snap-1",
        created_at=datetime(2025, 1, 1, 12, 5, 0, 0, tzinfo=timezone.utc),
        atom_ids=["test-atom-1"],
        previous_id=None,
        note="Test snapshot",
        stats=SnapshotStats(atom_count=1, tag_counts={"test": 1}),
        witness=WitnessStub(snapshot_id="snap-1"),
    )

    # Insert snapshot
    repo.insert_snapshot(snapshot)

    # Fetch snapshot
    fetched_snap = repo.fetch_snapshot("snap-1")
    assert fetched_snap is not None
    assert fetched_snap.id == "snap-1"
    assert fetched_snap.atom_ids == ["test-atom-1"]
    assert fetched_snap.note == "Test snapshot"

    # Count atoms
    count = repo.count_atoms()
    assert count == 1

    repo.close()


def test_repository_pagination(tmp_path: Path) -> None:
    """Test atom pagination."""
    db_path = tmp_path / "test.db"
    config = SQLiteConfig(path=db_path)
    repo = AtomRepository(config)

    # Insert multiple atoms
    for i in range(25):
        atom = Atom(
            id=f"atom-{i}",
            modality="text",
            content=AtomContent(inline=f"Content {i}"),
            hash=f"hash-{i}",
            created_at=datetime(2025, 1, 1, 12, i, 0, 0, tzinfo=timezone.utc),
            tags={"page": float(i // 10)},
        )
        repo.insert_atom(atom)

    # Fetch first page
    page1 = repo.fetch_atoms(limit=10, offset=0)
    assert len(page1) == 10

    # Fetch second page
    page2 = repo.fetch_atoms(limit=10, offset=10)
    assert len(page2) == 10

    # Ensure no overlap
    page1_ids = {a.id for a in page1}
    page2_ids = {a.id for a in page2}
    assert len(page1_ids & page2_ids) == 0

    repo.close()

