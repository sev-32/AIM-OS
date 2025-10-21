"""End-to-end integration tests for CMC + HHNI.

These tests validate the full workflow from atom creation through HHNI indexing
to semantic querying, ensuring all components work together correctly.

Goal IDs: OBJ-01 (CMC), OBJ-02 (HHNI)
"""

from __future__ import annotations

import os
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from cmc_service.memory_store import MemoryStore
from cmc_service.models import AtomContent, AtomCreate


@pytest.fixture
def tmp_store(tmp_path: Path):
    """Create a temporary MemoryStore for testing."""
    os.environ["CMC_BACKEND"] = "sqlite"
    store = MemoryStore(tmp_path / "cmc")
    yield store
    store.close()
    if "CMC_BACKEND" in os.environ:
        del os.environ["CMC_BACKEND"]


@pytest.fixture
def mock_hhni_clients():
    """Mock DGraph and Qdrant clients for HHNI testing."""
    mock_dgraph = MagicMock()
    mock_qdrant = MagicMock()
    
    # Mock Qdrant collection info
    mock_collection = MagicMock()
    mock_collection.vectors_count = 10
    mock_qdrant.create_collection.return_value = None
    mock_qdrant.collection_exists.return_value = True
    mock_qdrant.get_collection.return_value = mock_collection
    mock_qdrant.upsert.return_value = MagicMock(status="acknowledged")
    
    # Mock DGraph upsert
    mock_dgraph.upsert_nodes.return_value = None
    
    return mock_dgraph, mock_qdrant


def test_e2e_atom_creation_and_retrieval(tmp_store: MemoryStore) -> None:
    """
    Test: Create atom → List atoms → Verify content
    Goal: OBJ-01:KR-1.1 (deterministic storage)
    """
    # Create atom
    atom = tmp_store.create_atom(
        AtomCreate(
            modality="text",
            content=AtomContent(inline="Hello from integration test", media_type="text/plain"),
            tags={"test": 1.0, "e2e": 0.9},
        ),
        correlation_id="e2e-test-001",
    )
    
    # Verify atom ID generated (UUID format)
    assert len(atom.id) == 36  # Standard UUID length
    assert atom.content.inline == "Hello from integration test"
    assert atom.tags["test"] == pytest.approx(1.0)
    
    # List atoms
    atoms = list(tmp_store.list_atoms(limit=10))
    assert len(atoms) == 1
    assert atoms[0].id == atom.id
    
    # Filter by tag
    tagged = list(tmp_store.list_atoms(tag="test", limit=10))
    assert len(tagged) == 1
    assert tagged[0].tags["test"] == pytest.approx(1.0)


def test_e2e_snapshot_determinism(tmp_store: MemoryStore) -> None:
    """
    Test: Create atoms → Snapshot → Reload → Verify same snapshot ID
    Goal: OBJ-01:KR-1.1 (snapshot determinism)
    """
    # Fixed time for determinism
    fixed_time = datetime(2025, 10, 19, 12, 0, 0, tzinfo=timezone.utc)
    
    # Create atoms
    with patch('cmc_service.models.datetime') as mock_dt:
        mock_dt.now.return_value = fixed_time
        mock_dt.side_effect = lambda *args, **kwargs: datetime(*args, **kwargs)
        
        atom1 = tmp_store.create_atom(
            AtomCreate(modality="text", content=AtomContent(inline="First", media_type="text/plain")),
        )
        atom2 = tmp_store.create_atom(
            AtomCreate(modality="text", content=AtomContent(inline="Second", media_type="text/plain")),
        )
    
    # Create snapshot
    snapshot1 = tmp_store.create_snapshot(note="e2e test snapshot")
    snap_id_1 = snapshot1.id
    
    # Close and reload
    tmp_store.close()
    store2 = MemoryStore(tmp_store.base_path)
    
    # Verify same snapshot exists
    loaded_snap = store2.get_snapshot(snap_id_1)
    assert loaded_snap is not None
    assert loaded_snap.id == snap_id_1
    assert len(loaded_snap.atom_ids) == 2
    
    store2.close()


def test_e2e_hhni_integration_with_mocks(tmp_store: MemoryStore, mock_hhni_clients) -> None:
    """
    Test: Create atom with HHNI → Verify indexing called → Check node structure
    Goal: OBJ-02:KR-2.1 (HHNI indexing success)
    """
    mock_dgraph, mock_qdrant = mock_hhni_clients
    
    # Inject mocks
    tmp_store._hhni_dgraph_client = mock_dgraph
    tmp_store._hhni_qdrant_client = mock_qdrant
    
    # Create atom with high priority to trigger HHNI
    content = "This is a test paragraph for HHNI indexing. It has multiple sentences. Each sentence should be indexed."
    atom, nodes = tmp_store.create_atom_with_hhni(
        AtomCreate(
            modality="text",
            content=AtomContent(inline=content, media_type="text/plain"),
            tags={"priority": 0.95},  # High priority triggers HHNI
        ),
        build_hhni=True,  # Force build
        correlation_id="e2e-hhni-001",
    )
    
    # Verify atom created
    assert len(atom.id) == 36  # UUID format
    assert atom.content.inline == content
    
    # Verify HHNI nodes generated
    assert len(nodes) > 0
    
    # Verify DGraph upsert called
    assert mock_dgraph.upsert_nodes.called
    call_args = mock_dgraph.upsert_nodes.call_args[0][0]
    assert len(call_args) > 0
    
    # Verify node structure (nodes are returned as dicts from to_dict())
    doc_node = next((n for n in call_args if n.get("level") == 1), None)
    assert doc_node is not None
    # Doc node ID format: doc:<atom_uuid>
    assert "atom_refs" in doc_node
    assert atom.id in doc_node["atom_refs"]


def test_e2e_hhni_lazy_indexing_threshold(tmp_store: MemoryStore, mock_hhni_clients) -> None:
    """
    Test: Low priority atom → HHNI skipped; High priority → HHNI triggered
    Goal: OBJ-02:KR-2.2 (lazy indexing performance)
    """
    mock_dgraph, mock_qdrant = mock_hhni_clients
    tmp_store._hhni_dgraph_client = mock_dgraph
    tmp_store._hhni_qdrant_client = mock_qdrant
    
    # Low priority (below 0.6 threshold)
    atom_low, nodes_low = tmp_store.create_atom_with_hhni(
        AtomCreate(
            modality="text",
            content=AtomContent(inline="Low priority content", media_type="text/plain"),
            tags={"priority": 0.3},
        ),
        correlation_id="e2e-lazy-low",
    )
    
    assert len(nodes_low) == 0  # No nodes generated
    assert not mock_dgraph.upsert_nodes.called  # DGraph not called
    
    # High priority (above 0.6 threshold)
    atom_high, nodes_high = tmp_store.create_atom_with_hhni(
        AtomCreate(
            modality="text",
            content=AtomContent(inline="High priority content for indexing", media_type="text/plain"),
            tags={"priority": 0.8},
        ),
        correlation_id="e2e-lazy-high",
    )
    
    assert len(nodes_high) > 0  # Nodes generated
    assert mock_dgraph.upsert_nodes.called  # DGraph called


def test_e2e_snapshot_replay_after_hhni(tmp_store: MemoryStore, mock_hhni_clients) -> None:
    """
    Test: Create atoms with HHNI → Snapshot → Replay → Verify integrity
    Goal: OBJ-01:KR-1.1 (replay integrity), OBJ-02:KR-2.3 (HHNI + CMC integration)
    """
    mock_dgraph, mock_qdrant = mock_hhni_clients
    tmp_store._hhni_dgraph_client = mock_dgraph
    tmp_store._hhni_qdrant_client = mock_qdrant
    
    # Create multiple atoms with HHNI
    atom1, _ = tmp_store.create_atom_with_hhni(
        AtomCreate(
            modality="text",
            content=AtomContent(inline="First document for snapshot test", media_type="text/plain"),
            tags={"priority": 0.7},
        ),
        build_hhni=True,
    )
    
    atom2, _ = tmp_store.create_atom_with_hhni(
        AtomCreate(
            modality="text",
            content=AtomContent(inline="Second document for snapshot test", media_type="text/plain"),
            tags={"priority": 0.8},
        ),
        build_hhni=True,
    )
    
    # Create snapshot
    snapshot = tmp_store.create_snapshot(note="e2e replay test")
    
    # Replay snapshot
    replayed_atoms = list(tmp_store.replay_snapshot(snapshot.id))
    
    # Verify all atoms replayed
    assert len(replayed_atoms) == 2
    replayed_ids = {a.id for a in replayed_atoms}
    assert atom1.id in replayed_ids
    assert atom2.id in replayed_ids
    
    # Verify content intact
    for atom in replayed_atoms:
        if atom.id == atom1.id:
            assert atom.content.inline == "First document for snapshot test"
        elif atom.id == atom2.id:
            assert atom.content.inline == "Second document for snapshot test"


def test_e2e_corruption_recovery(tmp_store: MemoryStore) -> None:
    """
    Test: Create atoms → Corrupt journal → Verify quarantine
    Goal: OBJ-01:KR-1.3 (corruption handling)
    """
    # SQLite backend doesn't use journals, so this test is specific to JSONL
    if tmp_store._backend != "jsonl":
        pytest.skip("Corruption test only applicable to JSONL backend")
    
    # Create atoms
    atom1 = tmp_store.create_atom(
        AtomCreate(modality="text", content=AtomContent(inline="Before corruption", media_type="text/plain")),
    )
    tmp_store.close()
    
    # Corrupt the journal
    atoms_log = tmp_store.base_path / "atoms.log"
    with atoms_log.open("a", encoding="utf-8") as f:
        f.write("CORRUPT_LINE_NO_JSON\n")
    
    # Reload and verify quarantine
    store2 = MemoryStore(tmp_store.base_path)
    integrity = store2.journal_integrity()
    assert not integrity["atoms_log_ok"]
    
    # Verify quarantine file created
    quarantine_files = list(store2.quarantine_path.glob("*.quarantine"))
    assert len(quarantine_files) > 0
    
    store2.close()


def test_e2e_performance_baseline(tmp_store: MemoryStore, mock_hhni_clients) -> None:
    """
    Test: Measure time for 100 atom creations (baseline for OBJ-02:KR-2.1)
    Goal: OBJ-02:KR-2.1 (p99 latency tracking)
    """
    import time
    
    mock_dgraph, mock_qdrant = mock_hhni_clients
    tmp_store._hhni_dgraph_client = mock_dgraph
    tmp_store._hhni_qdrant_client = mock_qdrant
    
    durations = []
    for i in range(100):
        start = time.perf_counter()
        tmp_store.create_atom(
            AtomCreate(
                modality="text",
                content=AtomContent(inline=f"Performance test atom {i}", media_type="text/plain"),
                tags={"iteration": float(i) / 100.0},  # Normalize to [0.0, 1.0]
            ),
        )
        duration = time.perf_counter() - start
        durations.append(duration * 1000)  # Convert to ms
    
    # Calculate p99
    durations.sort()
    p99 = durations[int(len(durations) * 0.99)]
    
    # Log for tracking (no hard assertion, just baseline)
    print(f"\nPerformance baseline: p99 atom creation = {p99:.2f}ms")
    assert p99 < 1000  # Sanity check: should be under 1 second


# Integration test discovery
__all__ = [
    "test_e2e_atom_creation_and_retrieval",
    "test_e2e_snapshot_determinism",
    "test_e2e_hhni_integration_with_mocks",
    "test_e2e_hhni_lazy_indexing_threshold",
    "test_e2e_snapshot_replay_after_hhni",
    "test_e2e_corruption_recovery",
    "test_e2e_performance_baseline",
]

