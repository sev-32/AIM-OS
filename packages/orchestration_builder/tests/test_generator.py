
from __future__ import annotations

import json
from pathlib import Path

import yaml

from packages.orchestration_builder.generator import OrchestrationBuildResult, build_orchestration


def _build_sample_seed(node_count: int = 24, fan_out: int = 4) -> dict:
    agents = []
    for idx in range(node_count):
        agent_id = f"agent_{idx:02d}"
        depends = []
        for offset in range(1, fan_out + 1):
            target = (idx + offset) % node_count
            if target != idx:
                depends.append(f"agent_{target:02d}")
        agents.append(
            {
                "id": agent_id,
                "role": "specialist" if idx % 2 else "coordinator",
                "policy_pack_ids": [f"policy.group{idx % 5}"],
                "max_dependency_degree": fan_out + 1,
                "depends_on": depends,
            }
        )
    return {"agents": agents}


def _research_orchestrator_seed() -> dict:
    return {
        "type": "prompt_orchestration_framework",
        "name": "Research Orchestrator",
        "description": "Multi-stage research pipeline with 20+ agents and 80+ flows.",
        "policies": {
            "max_research_depth": 3,
            "evidence_threshold": 0.82,
            "max_total_time": 60,
        },
        "pipeline_stages": [
            {
                "key": "search",
                "label": "Literature Search",
                "concurrency": 3,
                "retry": {"max_attempts": 2, "strategy": "exponential", "cooldown_seconds": 10},
                "agents": [
                    {"name": "Scholar Agent", "role": "retriever", "capabilities": ["academic_papers", "citations"]},
                    {"name": "Web Agent", "role": "retriever", "capabilities": ["web_articles", "blogs"]},
                    {"name": "Code Agent", "role": "retriever", "capabilities": ["repositories", "documentation"]},
                ],
            },
            {
                "key": "extraction",
                "label": "Content Extraction",
                "concurrency": 5,
                "agents": [
                    {"name": "Key Concept Extractor", "role": "parser"},
                    {"name": "Methodology Extractor", "role": "parser"},
                    {"name": "Results Extractor", "role": "parser"},
                    {"name": "Limitations Extractor", "role": "parser"},
                    {"name": "References Extractor", "role": "parser"},
                ],
            },
            {
                "key": "analysis",
                "label": "Analysis",
                "concurrency": 4,
                "agents": [
                    {"name": "Trend Analyzer", "role": "analyst"},
                    {"name": "Gap Identifier", "role": "analyst"},
                    {"name": "Contradiction Detector", "role": "analyst"},
                    {"name": "Synthesis Builder", "role": "analyst"},
                ],
            },
            {
                "key": "validation",
                "label": "Validation",
                "concurrency": 3,
                "agents": [
                    {"name": "Fact Checker", "role": "validator"},
                    {"name": "Logic Validator", "role": "validator"},
                    {"name": "Consistency Checker", "role": "validator"},
                ],
            },
            {
                "key": "reporting",
                "label": "Reporting",
                "concurrency": 2,
                "agents": [
                    {"name": "Structured Report Builder", "role": "communicator"},
                    {"name": "Executive Summary Generator", "role": "communicator"},
                ],
            },
        ],
    }


def test_build_orchestration_generates_large_graph(tmp_path: Path) -> None:
    seed = _build_sample_seed(node_count=26, fan_out=4)
    result = build_orchestration(seed, output_dir=tmp_path, filename="test_orchestration.json")
    assert isinstance(result, OrchestrationBuildResult)
    assert result.artifact_path.exists()

    node_ids = {node["id"] for node in result.nodes}
    assert len(node_ids) == 26

    edge_pairs = {(edge["source"], edge["target"]) for edge in result.edges}
    assert len(edge_pairs) >= 26 * 4  # >= 104 edges

    for edge in result.edges:
        assert edge["source"] in node_ids
        assert edge["target"] in node_ids

    assert all(node["policy_pack_ids"] for node in result.nodes)
    assert sum(result.policy_summary.values()) == len(result.nodes)


def test_research_orchestrator_structure(tmp_path: Path) -> None:
    seed = _research_orchestrator_seed()
    result = build_orchestration(seed, output_dir=tmp_path)
    summary_path = result.artifact_path
    assert summary_path.exists()

    root_dir = summary_path.parent
    summary = json.loads(summary_path.read_text(encoding="utf-8"))

    assert summary["metadata"]["agent_count"] >= 22
    assert len(summary["edges"]) >= 80
    assert {"policy.research_depth", "policy.evidence_threshold"}.issubset(summary["policy_summary"].keys())

    agents_dir = root_dir / "agents"
    assert (agents_dir / "search" / "scholar_agent.acl").exists()
    assert (agents_dir / "extraction" / "key_concept_extractor.acl").exists()
    assert (agents_dir / "analysis" / "trend_analyzer.acl").exists()
    assert (agents_dir / "validation" / "fact_checker.acl").exists()
    assert (agents_dir / "reporting" / "structured_report_builder.acl").exists()
    assert (agents_dir / "orchestration" / "orchestration_supervisor.acl").exists()

    prompt_files = list((root_dir / "prompts").rglob("*.md"))
    assert len(prompt_files) >= 50

    flows_dir = root_dir / "flows"
    main_pipeline = yaml.safe_load((flows_dir / "main_pipeline.yaml").read_text(encoding="utf-8"))
    assert len(main_pipeline["stages"]) == 5
    assert any(stage["key"] == "analysis" for stage in main_pipeline["stages"])
    assert main_pipeline["global_agents"]

    feedback_loops = yaml.safe_load((flows_dir / "feedback_loops.yaml").read_text(encoding="utf-8"))
    loop_names = {loop["name"] for loop in feedback_loops["loops"]}
    assert "analysis_validation_feedback" in loop_names

    parallel_groups = yaml.safe_load((flows_dir / "parallel_execution.yaml").read_text(encoding="utf-8"))
    assert all(group["members"] for group in parallel_groups["groups"])

    gates_dir = root_dir / "gates"
    for gate_name in [
        "g_search_complete.py",
        "g_extraction_quality.py",
        "g_analysis_depth.py",
        "g_validation_passed.py",
    ]:
        assert (gates_dir / gate_name).exists()

    policies_path = root_dir / "policies" / "research_governance.json"
    policy_data = json.loads(policies_path.read_text(encoding="utf-8"))
    assert policy_data["base"]["max_research_depth"] == 3

    tests_dir = root_dir / "tests"
    assert (tests_dir / "test_pipeline_e2e.py").exists()
    assert (tests_dir / "test_parallel_agents.py").exists()

    # The return object reflects the same policy summary written to disk
    assert result.policy_summary == summary["policy_summary"]
