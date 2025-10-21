from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from pathlib import Path

import pytest
from playwright.sync_api import APIResponse, sync_playwright


def _wait_for_response(fetch_call, *, timeout: float = 30.0, interval: float = 0.25) -> APIResponse:
    """Poll the supplied callable until it returns a successful Playwright response."""
    deadline = time.time() + timeout
    last_error: Exception | None = None
    while time.time() < deadline:
        try:
            response: APIResponse = fetch_call()
            if response.ok:
                return response
            response.dispose()
        except Exception as exc:  # pragma: no cover - network retry path
            last_error = exc
        time.sleep(interval)
    if last_error is not None:
        raise TimeoutError(f"Playwright request failed after {timeout}s: {last_error}") from last_error
    raise TimeoutError(f"Playwright request failed after {timeout}s")


@pytest.mark.parametrize("port", [8123])
def test_dashboard_blast_radius_smoke(tmp_path: Path, port: int) -> None:
    """Launch the API via uvicorn and exercise the dashboard contract with Playwright."""
    repo_root = Path(__file__).resolve().parents[3]
    env = os.environ.copy()
    env["CMC_DB_PATH"] = str(tmp_path / "cmc.db")
    server = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "uvicorn",
            "packages.cmc_service.api:app",
            "--host",
            "127.0.0.1",
            "--port",
            str(port),
        ],
        cwd=str(repo_root),
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    base_url = f"http://127.0.0.1:{port}"
    try:
        with sync_playwright() as playwright:
            context = playwright.request.new_context(base_url=base_url, extra_http_headers={"accept": "application/json"})
            try:
                ready_response = _wait_for_response(lambda: context.get("/mpd/nodes"))
                ready_response.dispose()

                seed_resp = context.post(
                    "/mpd/seed/trunk",
                    params={"vision_summary": "Smoke vision", "correlation_id": "dashboard-smoke"},
                )
                assert seed_resp.ok
                seed_resp.dispose()

                nodes_resp = context.get("/mpd/nodes")
                nodes = nodes_resp.json()
                nodes_resp.dispose()
                assert any(node["mpd_id"] == "aimos.cmc" for node in nodes)
                trunk_id = next(node["mpd_id"] for node in nodes if node["mpd_id"] == "aimos.mige.trunk")

                edges_resp = context.get("/mpd/edges")
                edges = edges_resp.json()
                edges_resp.dispose()
                assert any(edge["relation"] == "depends_on" for edge in edges)

                draft_resp = context.get("/mpd/nodes", params={"lifecycle": "draft"})
                draft_nodes = draft_resp.json()
                draft_resp.dispose()
                assert {node["mpd_id"] for node in draft_nodes} == {
                    "aimos.mige.trunk",
                    "aimos.mige.trunk.guardrails",
                }

                policy_any_resp = context.get(
                    "/mpd/nodes",
                    params=[
                        ("policy_pack_ids", "policy.mige.guardrails"),
                        ("policy_pack_ids", "policy.unknown"),
                        ("policy_match", "any"),
                    ],
                )
                policy_any_nodes = policy_any_resp.json()
                policy_any_resp.dispose()
                assert any(node["mpd_id"] == "aimos.mige.trunk.guardrails" for node in policy_any_nodes)

                blast_payload = json.dumps({"root_ids": [trunk_id]})
                blast_resp = context.post(
                    "/mpd/blast-radius",
                    data=blast_payload,
                    headers={"content-type": "application/json"},
                )
                assert blast_resp.ok
                blast_json = blast_resp.json()
                blast_resp.dispose()
                assert blast_json["compliant"] is True
                assert trunk_id in blast_json["impacted_nodes"]
            finally:
                context.dispose()
    finally:
        server.terminate()
        try:
            server.wait(timeout=5)
        except subprocess.TimeoutExpired:  # pragma: no cover - defensive shutdown
            server.kill()
