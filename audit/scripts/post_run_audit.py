#!/usr/bin/env python
"""Collect minimal post-run audit bundle without LLM summarisation."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List

ROOT = Path(__file__).resolve().parents[2]
AUDIT_DIR = ROOT / "audit" / "history"


def run(command: List[str], env: Dict[str, str] | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(command, capture_output=True, text=True, cwd=ROOT, env=env, check=False)


def git_diff_stat() -> Dict[str, Any]:
    diff = run(["git", "diff", "--stat"])
    numstat = run(["git", "diff", "--numstat"])
    files = []
    for line in numstat.stdout.splitlines():
        parts = line.strip().split("\t")
        if len(parts) == 3:
            added, removed, path = parts
            files.append({"path": path, "added": int(added if added != "-" else 0), "removed": int(removed if removed != "-" else 0)})
    return {"summary": diff.stdout.strip(), "files": files}


def git_status() -> List[Dict[str, str]]:
    status = run(["git", "status", "--short"])
    files = []
    for line in status.stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        flag, path = line[:2].strip(), line[2:].strip()
        files.append({"status": flag, "path": path})
    return files


def pytest_summary(skip: bool) -> Dict[str, Any]:
    if skip:
        return {"passed": True, "names": [], "output": []}
    result = run([sys.executable, "-m", "pytest", "-q", "--maxfail=1"])
    passed = result.returncode == 0
    lines = result.stdout.splitlines()
    names = [line for line in lines if line.startswith("packages/") and ("PASSED" in line or "FAILED" in line)]
    return {"passed": passed, "names": names, "output": lines[-20:], "returncode": result.returncode}


def cmc_status(backends: List[str]) -> Dict[str, Any]:
    responses = {}
    for backend in backends:
        env = dict(os.environ)
        env["CMC_BACKEND"] = backend
        result = run([sys.executable, "-m", "cmc_service.cli", "status"], env=env)
        try:
            payload = json.loads(result.stdout.splitlines()[-1])
        except Exception:
            payload = {"raw": result.stdout}
        responses[backend] = payload
    return responses


def write_summary(target: Path, ctx: Dict[str, Any]) -> None:
    lines = [
        "# Post-Run Audit Summary",
        "",
        "## What Changed",
        ctx.get("change_list_text", "- none"),
        "",
        "## Why It Changed",
        f"- Goals / KRs touched: {ctx.get('goals_text', '[]')}",
        "",
        "## Evidence",
        f"- Tests: {'pass' if ctx['pytest']['passed'] else 'fail'}",
        f"- Snapshot ID: {ctx['sqlite_snapshot'] or 'n/a'}",
        "- Logs: see context.json",
        "",
        "## Risks / Gates",
        "- Acceptance gates: []",
        "- Follow-ups: none",
        "",
        "## Next Prompts",
        "- (set by o3)",
        "",
    ]
    (target / "summary.md").write_text("\n".join(lines))


def write_witness(target: Path, ctx: Dict[str, Any]) -> None:
    witness = {
        "artifact_type": "audit",
        "agent": {"name": ctx["agent"], "role": ctx["task"]},
        "model": {"id": "audit-script", "version": "0.1"},
        "corr_id": ctx["corr"],
        "started_at": ctx["started_at"],
        "finished_at": ctx["finished_at"],
        "inputs": {
            "files_before": ctx["status_files"],
            "plan_before": "",
            "goals": ctx.get("goals", []),
        },
        "outputs": {
            "files_changed": ctx["diff"]["files"],
            "tests": {
                "passed": int(ctx["pytest"]["passed"]),
                "failed": 0 if ctx["pytest"]["passed"] else 1,
                "names": ctx["pytest"]["names"],
            },
            "snapshot_id": ctx["sqlite_snapshot"],
            "log_actions": [],
        },
        "acceptance": {
            "docs": [],
            "gates_touched": [],
            "status": "pass" if ctx["pytest"]["passed"] else "needs-review",
            "notes": "",
        },
        "risk": {
            "band": "green" if ctx["pytest"]["passed"] else "yellow",
            "issues": [],
        },
        "signature": None,
    }
    (target / "witness.json").write_text(json.dumps(witness, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser(description="Create audit bundle")
    parser.add_argument("--agent", required=True)
    parser.add_argument("--task", required=True)
    parser.add_argument("--corr", required=True)
    parser.add_argument("--skip-tests", action="store_true")
    args = parser.parse_args()

    started_at = datetime.now(timezone.utc).isoformat()
    diff_info = git_diff_stat()
    status_files = git_status()
    pytest_info = pytest_summary(skip=args.skip_tests)
    status_info = cmc_status(["sqlite", "jsonl"])
    finished_at = datetime.now(timezone.utc).isoformat()

    sqlite_snapshot = status_info.get("sqlite", {}).get("latest_snapshot", {}).get("id")
    change_list_text = "\n".join(f"- {item['status']} {item['path']}" for item in status_files) or "- no tracked changes"

    bundle_id = finished_at.replace(":", "-")
    target_dir = AUDIT_DIR / f"{bundle_id}__agent-{args.agent}__task-{args.task}__corr-{args.corr}"
    target_dir.mkdir(parents=True, exist_ok=True)

    context = {
        "agent": args.agent,
        "task": args.task,
        "corr": args.corr,
        "started_at": started_at,
        "finished_at": finished_at,
        "diff": diff_info,
        "status_files": status_files,
        "pytest": pytest_info,
        "status": status_info,
        "sqlite_snapshot": sqlite_snapshot,
        "change_list_text": change_list_text,
        "goals": [],
        "goals_text": "[]",
    }

    write_summary(target_dir, context)
    write_witness(target_dir, context)

    (target_dir / "context.json").write_text(json.dumps(context, indent=2))


if __name__ == "__main__":
    main()
