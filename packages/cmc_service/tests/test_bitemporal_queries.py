"""Tests for bitemporal query engine."""

from __future__ import annotations

from datetime import datetime, timezone, timedelta
from pathlib import Path

import pytest

from schemas.mpd import MPDNode, KPIReference
from schemas.edge import BitemporalEdge

from cmc_service.repository import AtomRepository, SQLiteConfig
from cmc_service.bitemporal_queries import BitemporalQueryEngine


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


def test_query_nodes_as_of_transaction_time(repo: AtomRepository, engine: BitemporalQueryEngine):
    """Test as-of query using transaction time."""
    # Create nodes at different transaction times
    t1 = datetime(2025, 10, 1, tzinfo=timezone.utc)
    t2 = datetime(2025, 10, 15, tzinfo=timezone.utc)
    t3 = datetime(2025, 10, 30, tzinfo=timezone.utc)
    
    node1 = MPDNode(
        mpd_id="test.node1",
        type="service",
        purpose="First version",
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
    
    node2 = MPDNode(
        mpd_id="test.node2",
        type="service",
        purpose="Second version",
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
        tt_start=t2,
        vt_start=t2,
    )
    
    repo.upsert_mpd_nodes([node1, node2])
    
    # Query as of Oct 10 (should see node1 + seed data)
    result = engine.query_nodes_as_of(
        datetime(2025, 10, 10, tzinfo=timezone.utc),
        use_transaction_time=True
    )
    test_nodes = [n for n in result if n.mpd_id.startswith("test.")]
    assert len(test_nodes) == 1
    assert test_nodes[0].mpd_id == "test.node1"
    
    # Query as of Oct 20 (should see both test nodes)
    result = engine.query_nodes_as_of(
        datetime(2025, 10, 20, tzinfo=timezone.utc),
        use_transaction_time=True
    )
    test_nodes = [n for n in result if n.mpd_id.startswith("test.")]
    assert len(test_nodes) == 2
    
    # Query as of Sep 30 (should see seed data but no test nodes)
    result = engine.query_nodes_as_of(
        datetime(2025, 9, 30, tzinfo=timezone.utc),
        use_transaction_time=True
    )
    test_nodes = [n for n in result if n.mpd_id.startswith("test.")]
    assert len(test_nodes) == 0


def test_query_nodes_as_of_valid_time(repo: AtomRepository, engine: BitemporalQueryEngine):
    """Test as-of query using valid time."""
    now = datetime(2025, 10, 15, tzinfo=timezone.utc)
    
    # Node valid from Oct 1 to Oct 20
    node = MPDNode(
        mpd_id="test.node",
        type="service",
        purpose="Test",
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
        tt_start=now,  # Recorded on Oct 15
        vt_start=datetime(2025, 10, 1, tzinfo=timezone.utc),  # Valid from Oct 1
        vt_end=datetime(2025, 10, 20, tzinfo=timezone.utc),  # Valid until Oct 20
    )
    
    repo.upsert_mpd_nodes([node])
    
    # Query valid time Oct 10 (should find it)
    result = engine.query_nodes_as_of(
        datetime(2025, 10, 10, tzinfo=timezone.utc),
        use_transaction_time=False
    )
    test_nodes = [n for n in result if n.mpd_id == "test.node"]
    assert len(test_nodes) == 1
    
    # Query valid time Oct 25 (should not find test node - expired)
    result = engine.query_nodes_as_of(
        datetime(2025, 10, 25, tzinfo=timezone.utc),
        use_transaction_time=False
    )
    test_nodes = [n for n in result if n.mpd_id == "test.node"]
    assert len(test_nodes) == 0
    
    # Query valid time Sep 30 (should not find test node - not yet valid)
    result = engine.query_nodes_as_of(
        datetime(2025, 9, 30, tzinfo=timezone.utc),
        use_transaction_time=False
    )
    test_nodes = [n for n in result if n.mpd_id == "test.node"]
    assert len(test_nodes) == 0


def test_query_edges_as_of(repo: AtomRepository, engine: BitemporalQueryEngine):
    """Test as-of query for edges."""
    t1 = datetime(2025, 10, 1, tzinfo=timezone.utc)
    t2 = datetime(2025, 10, 15, tzinfo=timezone.utc)
    
    # Create test nodes
    node1 = MPDNode(
        mpd_id="test.source",
        type="service",
        purpose="Source",
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
        max_dependency_degree=1,
        tt_start=t1,
        vt_start=t1,
    )
    
    node2 = MPDNode(
        mpd_id="test.target",
        type="service",
        purpose="Target",
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
        max_dependency_degree=1,
        tt_start=t1,
        vt_start=t1,
    )
    
    edge = BitemporalEdge(
        source_id="test.source",
        target_id="test.target",
        relation="depends_on",
        policy_pack_ids=["policy.test.default"],  # Required for depends_on
        tt_start=t2,
        vt_start=t2,
    )
    
    repo.upsert_mpd_nodes([node1, node2])
    repo.upsert_mpd_edges([edge])
    
    # Query before edge created (filter test edges only)
    result = engine.query_edges_as_of(
        datetime(2025, 10, 10, tzinfo=timezone.utc),
        use_transaction_time=True,
        source_id="test.source"
    )
    assert len(result) == 0
    
    # Query after edge created
    result = engine.query_edges_as_of(
        datetime(2025, 10, 20, tzinfo=timezone.utc),
        use_transaction_time=True,
        source_id="test.source"
    )
    assert len(result) == 1
    assert result[0].source_id == "test.source"
    assert result[0].target_id == "test.target"


def test_query_nodes_in_range(repo: AtomRepository, engine: BitemporalQueryEngine):
    """Test range queries."""
    t1 = datetime(2025, 10, 1, tzinfo=timezone.utc)
    t2 = datetime(2025, 10, 15, tzinfo=timezone.utc)
    t3 = datetime(2025, 11, 1, tzinfo=timezone.utc)
    
    # Create nodes at different times
    node1 = MPDNode(
        mpd_id="test.oct",
        type="service",
        purpose="October node",
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
    
    node2 = MPDNode(
        mpd_id="test.nov",
        type="service",
        purpose="November node",
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
        tt_start=t3,
        vt_start=t3,
    )
    
    repo.upsert_mpd_nodes([node1, node2])
    
    # Query October range (should see oct node + seed data)
    result = engine.query_nodes_in_range(
        datetime(2025, 10, 1, tzinfo=timezone.utc),
        datetime(2025, 10, 31, tzinfo=timezone.utc),
        use_transaction_time=True
    )
    test_nodes = [n for n in result if n.mpd_id.startswith("test.")]
    assert len(test_nodes) == 1
    assert test_nodes[0].mpd_id == "test.oct"
    
    # Query November range (range queries are inclusive, so might see oct node too if tt_end is NULL)
    result = engine.query_nodes_in_range(
        datetime(2025, 11, 1, tzinfo=timezone.utc),
        datetime(2025, 11, 30, tzinfo=timezone.utc),
        use_transaction_time=True
    )
    test_nodes = [n for n in result if n.mpd_id.startswith("test.")]
    # Should at least see nov node
    nov_nodes = [n for n in test_nodes if n.mpd_id == "test.nov"]
    assert len(nov_nodes) == 1
    
    # Query spanning both (should see both test nodes)
    result = engine.query_nodes_in_range(
        datetime(2025, 10, 1, tzinfo=timezone.utc),
        datetime(2025, 11, 30, tzinfo=timezone.utc),
        use_transaction_time=True
    )
    test_nodes = [n for n in result if n.mpd_id.startswith("test.")]
    assert len(test_nodes) == 2


def test_get_node_history(repo: AtomRepository, engine: BitemporalQueryEngine):
    """Test retrieving node history."""
    # Note: Current schema has UNIQUE constraint on mpd_id
    # Testing with seed data which has existing history
    
    # Get history of a seed node
    history = engine.get_node_history("aimos.cmc")
    
    # Should have at least one version
    assert len(history) >= 1
    assert history[0].mpd_id == "aimos.cmc"
    
    # Test with new node
    t1 = datetime(2025, 10, 1, tzinfo=timezone.utc)
    node = MPDNode(
        mpd_id="test.evolving",
        type="service",
        purpose="Version 1",
        capabilities=["v1"],
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
    
    # Get history of new node
    history = engine.get_node_history("test.evolving")
    assert len(history) >= 1
    assert history[0].mpd_id == "test.evolving"


def test_query_changes_between(repo: AtomRepository, engine: BitemporalQueryEngine):
    """Test querying changes in a time period."""
    t1 = datetime(2025, 10, 1, tzinfo=timezone.utc)
    t2 = datetime(2025, 10, 15, tzinfo=timezone.utc)
    t3 = datetime(2025, 10, 20, tzinfo=timezone.utc)
    t4 = datetime(2025, 11, 1, tzinfo=timezone.utc)
    
    # Create nodes at different times
    node1 = MPDNode(
        mpd_id="test.added_oct1",
        type="service",
        purpose="Added Oct 1",
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
    
    node2 = MPDNode(
        mpd_id="test.added_oct15",
        type="service",
        purpose="Added Oct 15",
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
        tt_start=t2,
        vt_start=t2,
    )
    
    node3 = MPDNode(
        mpd_id="test.added_nov1",
        type="service",
        purpose="Added Nov 1",
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
        tt_start=t4,
        vt_start=t4,
    )
    
    repo.upsert_mpd_nodes([node1, node2, node3])
    
    # Query changes in October
    changes = engine.query_changes_between(
        datetime(2025, 10, 1, tzinfo=timezone.utc),
        datetime(2025, 10, 31, tzinfo=timezone.utc),
        use_transaction_time=True
    )
    
    assert len(changes['nodes_added']) == 2  # node1 and node2
    assert changes['nodes_added'][0].mpd_id == "test.added_oct1"
    assert changes['nodes_added'][1].mpd_id == "test.added_oct15"
    
    # Query changes in November
    changes = engine.query_changes_between(
        datetime(2025, 11, 1, tzinfo=timezone.utc),
        datetime(2025, 11, 30, tzinfo=timezone.utc),
        use_transaction_time=True
    )
    
    assert len(changes['nodes_added']) == 1  # node3 only
    assert changes['nodes_added'][0].mpd_id == "test.added_nov1"


def test_audit_trail(repo: AtomRepository, engine: BitemporalQueryEngine):
    """Test complete audit trail for a node."""
    # Note: Testing with single version due to schema constraints
    # Full versioning requires composite key (mpd_id, tt_start)
    
    t1 = datetime(2025, 10, 1, tzinfo=timezone.utc)
    
    node = MPDNode(
        mpd_id="test.audited",
        type="service",
        purpose="Version 1",
        capabilities=["basic"],
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
    
    # Get audit trail
    trail = engine.audit_trail("test.audited", include_edges=False)
    
    assert trail['node_id'] == "test.audited"
    assert trail['version_count'] >= 1
    assert trail['first_recorded'] == t1
    assert trail['currently_valid'].purpose == "Version 1"


def test_time_travel(repo: AtomRepository, engine: BitemporalQueryEngine):
    """Test complete system snapshot at a point in time."""
    t1 = datetime(2025, 10, 1, tzinfo=timezone.utc)
    t2 = datetime(2025, 10, 15, tzinfo=timezone.utc)
    
    # Create initial state
    node1 = MPDNode(
        mpd_id="test.node1",
        type="service",
        purpose="Node 1",
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
        max_dependency_degree=1,
        tt_start=t1,
        vt_start=t1,
    )
    
    node2 = MPDNode(
        mpd_id="test.node2",
        type="service",
        purpose="Node 2",
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
        max_dependency_degree=1,
        tt_start=t1,
        vt_start=t1,
    )
    
    edge = BitemporalEdge(
        source_id="test.node1",
        target_id="test.node2",
        relation="depends_on",
        policy_pack_ids=["policy.test.default"],  # Required for depends_on
        tt_start=t1,
        vt_start=t1,
    )
    
    repo.upsert_mpd_nodes([node1, node2])
    repo.upsert_mpd_edges([edge])
    
    # Time travel to Oct 10
    snapshot = engine.time_travel(
        datetime(2025, 10, 10, tzinfo=timezone.utc),
        use_transaction_time=True
    )
    
    assert snapshot['time_dimension'] == 'transaction'
    # Should include test nodes + seed data
    test_nodes = [n for n in snapshot['nodes'] if n.mpd_id.startswith("test.")]
    test_edges = [e for e in snapshot['edges'] if e.source_id.startswith("test.")]
    assert len(test_nodes) == 2
    assert len(test_edges) == 1


def test_bitemporal_supersession(repo: AtomRepository, engine: BitemporalQueryEngine):
    """Test bitemporal query with valid time ranges."""
    # Note: Testing supersession concept with valid_time ranges
    # Full versioning requires schema change
    
    t1 = datetime(2025, 10, 1, tzinfo=timezone.utc)
    
    # Node with limited validity period
    node = MPDNode(
        mpd_id="test.superseded",
        type="service",
        purpose="Limited validity",
        capabilities=["v1"],
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
        vt_end=datetime(2025, 10, 15, tzinfo=timezone.utc),  # Expires Oct 15
    )
    
    repo.upsert_mpd_nodes([node])
    
    # Query when valid (Oct 10)
    result = engine.query_nodes_as_of(
        datetime(2025, 10, 10, tzinfo=timezone.utc),
        use_transaction_time=False  # Use valid time
    )
    matching = [n for n in result if n.mpd_id == "test.superseded"]
    assert len(matching) == 1
    
    # Query after expiration (Oct 20)
    result = engine.query_nodes_as_of(
        datetime(2025, 10, 20, tzinfo=timezone.utc),
        use_transaction_time=False
    )
    matching = [n for n in result if n.mpd_id == "test.superseded"]
    assert len(matching) == 0  # Expired


def test_edge_filtering_in_as_of_query(repo: AtomRepository, engine: BitemporalQueryEngine):
    """Test that as-of edge queries support filtering."""
    t1 = datetime(2025, 10, 1, tzinfo=timezone.utc)
    
    # Create nodes
    nodes = [
        MPDNode(
            mpd_id=f"test.node{i}",
            type="service",
            purpose=f"Node {i}",
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
            max_dependency_degree=2,
            tt_start=t1,
            vt_start=t1,
        )
        for i in range(3)
    ]
    
    # Create edges
    edges = [
        BitemporalEdge(
            source_id="test.node0",
            target_id="test.node1",
            relation="depends_on",
            policy_pack_ids=["policy.test.default"],  # Required for depends_on
            tt_start=t1,
            vt_start=t1,
        ),
        BitemporalEdge(
            source_id="test.node0",
            target_id="test.node2",
            relation="manager_of",
            policy_pack_ids=["policy.test.default"],
            tt_start=t1,
            vt_start=t1,
        ),
    ]
    
    repo.upsert_mpd_nodes(nodes)
    repo.upsert_mpd_edges(edges)
    
    # Query all edges from node0
    result = engine.query_edges_as_of(
        datetime(2025, 10, 10, tzinfo=timezone.utc),
        use_transaction_time=True,
        source_id="test.node0"
    )
    assert len(result) == 2
    
    # Query only depends_on edges from test.node0
    result = engine.query_edges_as_of(
        datetime(2025, 10, 10, tzinfo=timezone.utc),
        use_transaction_time=True,
        relation="depends_on",
        source_id="test.node0"
    )
    assert len(result) == 1
    assert result[0].relation == "depends_on"
    assert result[0].source_id == "test.node0"

