from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from packages.orchestration_builder import OrchestrationExecutor, build_orchestration


class FakeLLM:
    def __init__(self) -> None:
        self.calls: list[dict[str, Optional[str]]] = []

    def generate(self, prompt: str, *, context: Optional[str] = None) -> str:
        self.calls.append({"prompt": prompt, "context": context})
        return f"fake-response-{len(self.calls)}"


def _research_seed() -> dict:
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
                    {"name": "Scholar Agent", "role": "retriever"},
                    {"name": "Web Agent", "role": "retriever"},
                    {"name": "Code Agent", "role": "retriever"},
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
        ],
    }


def test_executor_creates_outputs_and_audit(tmp_path: Path) -> None:
    seed = _research_seed()
    result = build_orchestration(seed, output_dir=tmp_path)
    root = result.artifact_path.parent

    fake_llm = FakeLLM()
    executor = OrchestrationExecutor(root, llm_client=fake_llm, model_name="fake-model")
    audit_path = executor.run(max_agents=4, include_coordinators=False)

    assert audit_path.exists()
    assert len(fake_llm.calls) == 4

    outputs_dir = root / "outputs"
    created_outputs = list(outputs_dir.glob("*.md"))
    assert len(created_outputs) == 4

    audit_payload = json.loads(audit_path.read_text(encoding="utf-8"))
    assert audit_payload["output_count"] == 4
    assert len(audit_payload["entries"]) == 4


def test_executor_runs_full_pipeline(tmp_path: Path) -> None:
    seed = _research_seed()
    result = build_orchestration(seed, output_dir=tmp_path)
    root = result.artifact_path.parent

    fake_llm = FakeLLM()
    executor = OrchestrationExecutor(root, llm_client=fake_llm, model_name="fake-model")
    audit_path = executor.run(include_coordinators=True)

    audit_payload = json.loads(audit_path.read_text(encoding="utf-8"))
    assert audit_payload["output_count"] == len(audit_payload["entries"])
    assert audit_payload["output_count"] >= 10
    # Ensure global audit file references outputs directory
    for entry in audit_payload["entries"]:
        output_reference = entry["output_file"].replace("\\", "/")
        assert output_reference.startswith("outputs/")
