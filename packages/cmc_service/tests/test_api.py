from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path

from fastapi.testclient import TestClient

from packages.cmc_service.api import app


def test_seed_and_filter_edges(tmp_path) -> None:
    db_path = tmp_path / "cmc.db"
    os.environ["CMC_DB_PATH"] = str(db_path)
    client = TestClient(app)

    resp = client.post(
        "/mpd/seed/trunk",
        params={
            "vision_summary": "Seed vision",
            "correlation_id": "test",
        },
    )
    assert resp.status_code == 200
    nodes = client.get("/mpd/nodes").json()
    assert any(node["mpd_id"] == "aimos.cmc" for node in nodes)
    source_id = next(node["mpd_id"] for node in nodes if node["mpd_id"] == "aimos.mige.trunk")
    target_id = next(node["mpd_id"] for node in nodes if node["mpd_id"] == "aimos.mige.trunk.guardrails")

    guardrail_nodes = client.get("/mpd/nodes", params=[("policy_pack_ids", "policy.mige.guardrails")]).json()
    assert guardrail_nodes
    assert all("policy.mige.guardrails" in node["policy_pack_ids"] for node in guardrail_nodes)
    both_filtered = client.get(
        "/mpd/nodes",
        params=[("policy_pack_ids", "policy.mige.default"), ("policy_pack_ids", "policy.mige.guardrails")],
    ).json()
    assert both_filtered and all(
        {"policy.mige.default", "policy.mige.guardrails"}.issubset(set(node["policy_pack_ids"])) for node in both_filtered
    )
    draft_nodes = client.get("/mpd/nodes", params=[("lifecycle", "draft")]).json()
    assert {node["mpd_id"] for node in draft_nodes} == {"aimos.mige.trunk", "aimos.mige.trunk.guardrails"}
    active_nodes = client.get("/mpd/nodes", params=[("lifecycle", "active")]).json()
    assert any(node["mpd_id"] == "aimos.cmc" for node in active_nodes)
    policy_any = client.get(
        "/mpd/nodes",
        params=[
            ("policy_pack_ids", "policy.mige.guardrails"),
            ("policy_pack_ids", "policy.missing"),
            ("policy_match", "any"),
        ],
    ).json()
    assert any(node["mpd_id"] == "aimos.mige.trunk.guardrails" for node in policy_any)

    dep_resp = client.post(
        "/mpd/edges/depends-on",
        json={
            "source_id": source_id,
            "targets": [target_id],
            "policy_pack_ids": ["policy.custom"],
            "tt_start": datetime.now(timezone.utc).isoformat(),
        },
    )
    assert dep_resp.status_code == 200

    edges = client.get("/mpd/edges", params={"relation": "depends_on"}).json()
    assert any(edge["relation"] == "depends_on" for edge in edges)
    filtered = client.get(
        "/mpd/edges", params={"relation": "depends_on", "source_id": source_id, "target_id": target_id}
    ).json()
    assert any(edge["target_id"] == target_id for edge in filtered)
    policy_filtered = client.get("/mpd/edges", params=[("policy_pack_ids", "policy.custom")]).json()
    assert policy_filtered and all("policy.custom" in edge["policy_pack_ids"] for edge in policy_filtered)
    combined_policy_edge = next(
        edge for edge in policy_filtered if edge["source_id"] == source_id and edge["target_id"] == target_id
    )
    assert "policy.mige.default" in combined_policy_edge["policy_pack_ids"]
    any_policy_edges = client.get(
        "/mpd/edges",
        params=[
            ("policy_pack_ids", "policy.custom"),
            ("policy_pack_ids", "policy.nonexistent"),
            ("policy_match", "any"),
        ],
    ).json()
    assert any(
        edge["source_id"] == source_id and edge["target_id"] == target_id for edge in any_policy_edges
    )

    blast_ok = client.post("/mpd/blast-radius", json={"root_ids": [source_id]}).json()
    assert blast_ok["compliant"] is True
    assert source_id in blast_ok["impacted_nodes"]
    assert blast_ok["required_policy_pack_ids"]

    blast_block = client.post(
        "/mpd/blast-radius",
        json={
            "root_ids": [source_id],
            "required_policy_pack_ids": ["policy.noncompliant"],
        },
    ).json()
    assert blast_block["compliant"] is False
    assert any(v["kind"] in {"node_policy", "edge_policy"} for v in blast_block["violations"])


def test_kpi_endpoint(tmp_path, monkeypatch):
    db_path = tmp_path / "cmc.db"
    os.environ["CMC_DB_PATH"] = str(db_path)
    client = TestClient(app)

    goals_dir = tmp_path / "goals"
    goals_dir.mkdir()
    kpi_file = goals_dir / "KPI_METRICS.json"
    kpi_file.write_text(json.dumps({"metric": 1}), encoding="utf-8")

    monkeypatch.chdir(tmp_path)
    data = client.get("/kpis").json()
    assert data["metric"] == 1
