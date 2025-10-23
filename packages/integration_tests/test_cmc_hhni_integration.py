"""Integration Tests: CMC + HHNI

Tests that CMC bitemporal queries integrate with HHNI retrieval.
"""

from __future__ import annotations

from datetime import datetime, timezone, timedelta
from pathlib import Path

import pytest

from cmc_service import BitemporalQueryEngine, AtomRepository, SQLiteConfig
from schemas.mpd import MPDNode, KPIReference
from schemas.edge import BitemporalEdge


@pytest.fixture
def repo(tmp_path: Path) -> AtomRepository:
    """Create test repository."""
    config = SQLiteConfig(path=tmp_path / "test.db", enable_wal=False)
    repository = AtomRepository(config)
    yield repository
    repository.close()


@pytest.fixture
def engine(repo: AtomRepository) -> BitemporalQueryEngine:
    """Create query engine."""
    return BitemporalQueryEngine(repo)


def test_bitemporal_queries_support_hhni_metadata(engine: BitemporalQueryEngine, repo: AtomRepository):
    """Test that bitemporal queries work on nodes with HHNI metadata."""
    now = datetime.now(timezone.utc)
    
    # Create node with HHNI-like metadata
    node = MPDNode(
        mpd_id="test.hhni_indexed",
        type="service",
        purpose="HHNI indexed content",
        capabilities=["search", "retrieval"],
        interfaces=[],
        manager_of=[],
        depends_on=[],
        policy_pack_ids=[],
        budgets=[],
        owners=[],
        kpis=[KPIReference(name="retrieval_speed", target=0.95)],
        lifecycle="active",
        witness=None,
        links=[],
        max_dependency_degree=0,
        tt_start=now,
        vt_start=now,
    )
    
    repo.upsert_mpd_nodes([node])
    
    # Query using bitemporal engine
    result = engine.query_nodes_as_of(now + timedelta(minutes=1), use_transaction_time=True)
    
    # Should find the HHNI-indexed node
    matching = [n for n in result if n.mpd_id == "test.hhni_indexed"]
    assert len(matching) == 1
    assert matching[0].capabilities == ["search", "retrieval"]


def test_time_travel_enables_hhni_historical_context(engine: BitemporalQueryEngine, repo: AtomRepository):
    """Test that time-travel queries can retrieve historical HHNI context."""
    t1 = datetime(2025, 10, 1, tzinfo=timezone.utc)
    t2 = datetime(2025, 10, 15, tzinfo=timezone.utc)
    
    # Create historical context node
    node = MPDNode(
        mpd_id="test.historical_context",
        type="knowledge",
        purpose="Historical authentication design",
        capabilities=[],
        interfaces=[],
        manager_of=[],
        depends_on=[],
        policy_pack_ids=[],
        budgets=[],
        owners=[],
        kpis=[],
        lifecycle="active",
        witness=None,
        links=[],
        max_dependency_degree=0,
        tt_start=t1,
        vt_start=t1,
        vt_end=t2,  # Was valid until Oct 15
    )
    
    repo.upsert_mpd_nodes([node])
    
    # Time travel to Oct 10 (should find it)
    snapshot = engine.time_travel(
        datetime(2025, 10, 10, tzinfo=timezone.utc),
        use_transaction_time=False  # Use valid time
    )
    
    matching = [n for n in snapshot['nodes'] if n.mpd_id == "test.historical_context"]
    assert len(matching) == 1
    
    # Time travel to Oct 20 (should not find it - expired)
    snapshot = engine.time_travel(
        datetime(2025, 10, 20, tzinfo=timezone.utc),
        use_transaction_time=False
    )
    
    matching = [n for n in snapshot['nodes'] if n.mpd_id == "test.historical_context"]
    assert len(matching) == 0


def test_audit_trail_for_hhni_indexed_content(engine: BitemporalQueryEngine, repo: AtomRepository):
    """Test that audit trails work for HHNI-indexed content."""
    now = datetime.now(timezone.utc)
    
    # Create node representing indexed content
    node = MPDNode(
        mpd_id="test.indexed_doc",
        type="document",
        purpose="Authentication guide v1",
        capabilities=["hhni_indexed"],
        interfaces=[],
        manager_of=[],
        depends_on=[],
        policy_pack_ids=[],
        budgets=[],
        owners=["documentation_team"],
        kpis=[],
        lifecycle="active",
        witness="hhni_index_witness_001",
        links=["docs/auth.md"],
        max_dependency_degree=0,
        tt_start=now,
        vt_start=now,
    )
    
    repo.upsert_mpd_nodes([node])
    
    # Get audit trail
    trail = engine.audit_trail("test.indexed_doc", include_edges=True)
    
    assert trail['node_id'] == "test.indexed_doc"
    assert trail['version_count'] >= 1
    assert trail['currently_valid'].witness == "hhni_index_witness_001"


def test_query_changes_detects_hhni_index_updates(engine: BitemporalQueryEngine, repo: AtomRepository):
    """Test that change detection works for HHNI index updates."""
    t_start = datetime(2025, 10, 1, tzinfo=timezone.utc)
    t_mid = datetime(2025, 10, 15, tzinfo=timezone.utc)
    t_end = datetime(2025, 10, 31, tzinfo=timezone.utc)
    
    # Create node in October
    node = MPDNode(
        mpd_id="test.index_updated",
        type="index",
        purpose="HHNI index node",
        capabilities=["indexed"],
        interfaces=[],
        manager_of=[],
        depends_on=[],
        policy_pack_ids=[],
        budgets=[],
        owners=[],
        kpis=[],
        lifecycle="active",
        witness=None,
        links=[],
        max_dependency_degree=0,
        tt_start=t_mid,
        vt_start=t_mid,
    )
    
    repo.upsert_mpd_nodes([node])
    
    # Query changes in October
    changes = engine.query_changes_between(t_start, t_end, use_transaction_time=True)
    
    # Should detect the node addition
    added_ids = [n.mpd_id for n in changes['nodes_added']]
    assert "test.index_updated" in added_ids


def test_cmc_hhni_integration_validates_timestamps(engine: BitemporalQueryEngine):
    """Test that all queried nodes have valid timestamps."""
    now = datetime.now(timezone.utc)
    
    # Query current state
    nodes = engine.query_nodes_as_of(now, use_transaction_time=True)
    
    # All nodes should have valid timestamps
    for node in nodes:
        assert node.tt_start is not None
        assert node.vt_start is not None
        assert isinstance(node.tt_start, datetime)
        assert isinstance(node.vt_start, datetime)


def test_bitemporal_range_queries_for_hhni_context(engine: BitemporalQueryEngine, repo: AtomRepository):
    """Test that range queries work for retrieving HHNI context windows."""
    t1 = datetime(2025, 10, 1, tzinfo=timezone.utc)
    t2 = datetime(2025, 10, 31, tzinfo=timezone.utc)
    
    # Create context node
    node = MPDNode(
        mpd_id="test.context_window",
        type="context",
        purpose="October authentication context",
        capabilities=[],
        interfaces=[],
        manager_of=[],
        depends_on=[],
        policy_pack_ids=[],
        budgets=[],
        owners=[],
        kpis=[],
        lifecycle="active",
        witness=None,
        links=[],
        max_dependency_degree=0,
        tt_start=t1,
        vt_start=t1,
    )
    
    repo.upsert_mpd_nodes([node])
    
    # Query October range
    nodes = engine.query_nodes_in_range(t1, t2, use_transaction_time=True)
    
    # Should find the context node
    matching = [n for n in nodes if n.mpd_id == "test.context_window"]
    assert len(matching) == 1
