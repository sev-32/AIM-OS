from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Generator

import pytest

from packages.cmc_service.memory_store import MemoryStore
from packages.cmc_service.models import AtomContent, AtomCreate
from packages.cmc_service.repository import AtomRepository, SQLiteConfig
from schemas.edge import BitemporalEdge
from schemas.mpd import KPIReference, MPDNode


@pytest.fixture()
def repository(tmp_path: Path) -> Generator[AtomRepository, None, None]:
    config = SQLiteConfig(path=tmp_path / "cmc.db", enable_wal=False)
    repo = AtomRepository(config)
    try:
        yield repo
    finally:
        repo.close()


def test_memory_persistence_across_sessions(tmp_path: Path) -> None:
    store_path = tmp_path / "cmc_store"
    store = MemoryStore(store_path)
    try:
        decisions = []
        for idx in range(20):
            payload = AtomCreate(
                modality="text",
                content=AtomContent(inline=f"Decision {idx}: adopt pattern {idx}", media_type="text/plain"),
                tags={"decision": 1.0, "project_apollo": 1.0},
                metadata={"topic": "project_apollo", "index": idx},
            )
            atom = store.create_atom(payload)
            decisions.append(atom.id)
        snapshot = store.create_snapshot(atom_ids=decisions, note="Project Apollo decisions")
        assert snapshot.atom_ids == decisions
    finally:
        store.close()

    restored = MemoryStore(store_path)
    try:
        recovered = list(restored.list_atoms(tag="project_apollo", limit=25))
        assert len(recovered) == 20
        recovered.sort(key=lambda atom: atom.metadata.get("index", -1))
        assert recovered[0].content.inline.startswith("Decision 0")
        assert recovered[-1].metadata["index"] == 19
    finally:
        restored.close()


def test_dependency_degree_limits(repository: AtomRepository) -> None:
    now = datetime.now(timezone.utc)
    source = MPDNode(
        mpd_id="service.a",
        type="service",
        purpose="Core orchestrator",
        capabilities=[],
        interfaces=[],
        manager_of=[],
        depends_on=[],
        policy_pack_ids=["policy.default"],
        budgets=[],
        owners=[],
        kpis=[KPIReference(name="MaxDeps", target=1.0)],
        lifecycle="active",
        witness=None,
        links=[],
        max_dependency_degree=2,
        tt_start=now,
        vt_start=now,
    )
    deps = [
        MPDNode(
            mpd_id=f"service.dep_{idx}",
            type="service",
            purpose=f"Dependency {idx}",
            capabilities=[],
            interfaces=[],
            manager_of=[],
            depends_on=[],
            policy_pack_ids=["policy.default"],
            budgets=[],
            owners=[],
            kpis=[],
            lifecycle="active",
            witness=None,
            links=[],
            max_dependency_degree=1,
            tt_start=now,
            vt_start=now,
        )
        for idx in range(3)
    ]
    repository.upsert_mpd_nodes([source, *deps])

    for idx in range(2):
        edge = BitemporalEdge(
            source_id=source.mpd_id,
            target_id=deps[idx].mpd_id,
            relation="depends_on",
            policy_pack_ids=["policy.default"],
            tt_start=now,
            vt_start=now,
        )
        repository.upsert_mpd_edges([edge])

    with pytest.raises(ValueError):
        repository.upsert_mpd_edges([
            BitemporalEdge(
                source_id=source.mpd_id,
                target_id=deps[2].mpd_id,
                relation="depends_on",
                policy_pack_ids=["policy.default"],
                tt_start=now,
                vt_start=now,
            )
        ])
