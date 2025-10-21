from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import pytest

from schemas.mpd import MPDNode, KPIReference
from schemas.edge import BitemporalEdge

from cmc_service.repository import AtomRepository, SQLiteConfig


@pytest.fixture()
def repo(tmp_path: Path) -> AtomRepository:
    config = SQLiteConfig(path=tmp_path / "cmc.db", enable_wal=False)
    repository = AtomRepository(config)
    yield repository
    repository.close()


def test_upsert_mpd_nodes_and_edges(repo: AtomRepository) -> None:
    now = datetime.now(timezone.utc)
    node = MPDNode(
        mpd_id="test.node",
        type="service",
        purpose="Test node",
        capabilities=[],
        interfaces=[],
        manager_of=[],
        depends_on=[],
        policy_pack_ids=[],
        budgets=[],
        owners=[],
        kpis=[KPIReference(name="VisionFit", target=0.9)],
        lifecycle="active",
        witness=None,
        links=[],
        max_dependency_degree=1,
        tt_start=now,
        vt_start=now,
    )
    repo.upsert_mpd_nodes([node])

    edge = BitemporalEdge(
        source_id="test.node",
        target_id="test.node",
        relation="self",
        policy_pack_ids=[],
        tt_start=now,
        vt_start=now,
    )
    repo.upsert_mpd_edges([edge])

    stored = repo.fetch_mpd_nodes()
    found = next((item for item in stored if item.mpd_id == "test.node"), None)
    assert found is not None
    assert found.max_dependency_degree == 1
