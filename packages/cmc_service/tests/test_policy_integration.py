from __future__ import annotations

import os
import json
from datetime import datetime, timezone
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from packages.cmc_service.api import app
from packages.cmc_service.repository import AtomRepository, SQLiteConfig
from packages.meta_optimizer.vision_tensor import compute_tensor
from schemas.edge import BitemporalEdge
from schemas.mpd import KPIReference, MPDNode
from scripts.kpi_refresh import refresh_kpis


@pytest.fixture()
def repository(tmp_path: Path) -> AtomRepository:
    config = SQLiteConfig(path=tmp_path / "cmc.db", enable_wal=False)
    repo = AtomRepository(config)
    try:
        yield repo
    finally:
        repo.close()


@pytest.fixture()
def api_client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> TestClient:
    db_path = tmp_path / "cmc.db"
    monkeypatch.setenv("CMC_DB_PATH", str(db_path))
    client = TestClient(app)
    try:
        yield client
    finally:
        client.close()


def test_vision_tensor_policy_alias_propagation() -> None:
    result = compute_tensor(
        "Policy seed",
        policy_pack_ids=["policy.alpha"],
        policy_packs=["policy.beta", "policy.alpha"],
    )
    assert result.policy_pack_ids == ["policy.alpha", "policy.beta"]


def test_repository_depends_on_inherits_policy(repository: AtomRepository) -> None:
    now = datetime.now(timezone.utc)
    upstream = MPDNode(
        mpd_id="policy.source",
        type="service",
        purpose="Upstream with guardrail policy",
        capabilities=[],
        interfaces=[],
        manager_of=[],
        depends_on=[],
        policy_pack_ids=["policy.alpha", "policy.shared"],
        budgets=[],
        owners=[],
        kpis=[KPIReference(name="PolicyInheritance", target=1.0)],
        lifecycle="active",
        witness=None,
        links=[],
        max_dependency_degree=1,
        tt_start=now,
        vt_start=now,
    )
    downstream = MPDNode(
        mpd_id="policy.target",
        type="service",
        purpose="Downstream dependency",
        capabilities=[],
        interfaces=[],
        manager_of=[],
        depends_on=[],
        policy_pack_ids=["policy.existing"],
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
    repository.upsert_mpd_nodes([upstream, downstream])
    edge = BitemporalEdge(
        source_id=upstream.mpd_id,
        target_id=downstream.mpd_id,
        relation="depends_on",
        policy_pack_ids=["policy.custom"],
        tt_start=now,
        vt_start=now,
    )
    repository.upsert_mpd_edges([edge])

    stored_edges = repository.fetch_mpd_edges(source_id=upstream.mpd_id, target_id=downstream.mpd_id)
    assert stored_edges, "Expected depends_on edge to be stored."
    policies = stored_edges[0].policy_pack_ids
    assert set(policies) == {"policy.alpha", "policy.shared", "policy.custom"}


def test_repository_blast_radius_blocks_policy_violation(repository: AtomRepository) -> None:
    now = datetime.now(timezone.utc)
    root = MPDNode(
        mpd_id="policy.root",
        type="service",
        purpose="Root service enforcing alpha policy",
        capabilities=[],
        interfaces=[],
        manager_of=[],
        depends_on=["policy.dependent"],
        policy_pack_ids=["policy.alpha"],
        budgets=[],
        owners=[],
        kpis=[],
        lifecycle="active",
        witness=None,
        links=[],
        max_dependency_degree=2,
        tt_start=now,
        vt_start=now,
    )
    dependent = MPDNode(
        mpd_id="policy.dependent",
        type="service",
        purpose="Downstream service missing alpha policy",
        capabilities=[],
        interfaces=[],
        manager_of=[],
        depends_on=[],
        policy_pack_ids=["policy.beta"],
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
    repository.upsert_mpd_nodes([root, dependent])
    repository.upsert_mpd_edges(
        [
            BitemporalEdge(
                source_id=root.mpd_id,
                target_id=dependent.mpd_id,
                relation="depends_on",
                policy_pack_ids=["policy.edge-placeholder"],
                tt_start=now,
                vt_start=now,
            )
        ]
    )

    result = repository.calculate_blast_radius(
        [root.mpd_id],
        relation_types=["depends_on"],
        required_policy_pack_ids=["policy.alpha"],
    )

    assert result["compliant"] is False
    assert any(v["kind"] == "node_policy" and v["subject_id"] == dependent.mpd_id for v in result["violations"])


def test_policy_flow_end_to_end(api_client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    resp = api_client.post(
        "/mpd/seed/trunk",
        params={
            "vision_summary": "Seed vision with default guardrails",
            "correlation_id": "integration-test",
        },
    )
    assert resp.status_code == 200
    trunk_ids = resp.json()["mpd_ids"]
    assert trunk_ids

    root_id = trunk_ids[0]
    blast_ok = api_client.post("/mpd/blast-radius", json={"root_ids": [root_id]}).json()
    assert blast_ok["compliant"] is True

    blast_block = api_client.post(
        "/mpd/blast-radius",
        json={
            "root_ids": [root_id],
            "required_policy_pack_ids": ["policy.nonexistent"],
        },
    ).json()
    assert blast_block["compliant"] is False


def test_kpi_refresh_appends_history_and_csv(tmp_path: Path) -> None:
    metrics_path = tmp_path / "goals" / "KPI_METRICS.json"
    metrics_path.parent.mkdir(parents=True, exist_ok=True)
    metrics_path.write_text(
        json.dumps(
            {
                "metric.alpha": 1,
                "history": {
                    "metric.alpha": [
                        {"timestamp": "2025-10-20T00:00:00Z", "value": 1},
                    ]
                },
                "history_metadata": {"generated_at": "2025-10-20T00:00:00Z"},
            }
        ),
        encoding="utf-8",
    )

    refresh_kpis(metrics_path=metrics_path, output_dir=tmp_path / "trends")

    payload = json.loads(metrics_path.read_text(encoding="utf-8"))
    history_entries = payload["history"]["metric.alpha"]
    assert len(history_entries) == 2
    assert (tmp_path / "trends" / "metric.alpha.csv").exists()
    assert payload["history_metadata"]["notes"] == "Updated via kpi_refresh script."


def test_kpi_history_endpoint(api_client: TestClient, monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    goals_dir = tmp_path / "goals"
    goals_dir.mkdir()
    metrics_path = goals_dir / "KPI_METRICS.json"
    metrics_path.write_text(
        json.dumps(
            {
                "metric.alpha": 1,
                "metric.beta": 2,
                "history": {
                    "metric.alpha": [
                        {"timestamp": "2025-10-20T00:00:00Z", "value": 1},
                        {"timestamp": "2025-10-22T00:00:00Z", "value": 2},
                    ],
                    "metric.beta": [
                        {"timestamp": "2025-10-21T00:00:00Z", "value": 5},
                    ],
                },
                "history_metadata": {"generated_at": "2025-10-22T00:00:00Z"},
            }
        ),
        encoding="utf-8",
    )

    monkeypatch.chdir(tmp_path)

    resp = api_client.get("/kpi/history")
    assert resp.status_code == 200
    payload = resp.json()
    metrics = {item["metric"] for item in payload}
    assert metrics == {"metric.alpha", "metric.beta"}

    filtered = api_client.get(
        "/kpi/history",
        params=[("metrics", "metric.alpha"), ("start_time", "2025-10-21T00:00:00Z")],
    ).json()
    assert filtered == [
        {
            "metric": "metric.alpha",
            "history": [
                {"timestamp": "2025-10-22T00:00:00Z", "value": 2},
            ],
        }
    ]
