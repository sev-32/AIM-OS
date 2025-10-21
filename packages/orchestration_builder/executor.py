from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Mapping, Optional, Protocol, Sequence

import google.generativeai as genai
import yaml


class LLMClient(Protocol):
    """Minimal interface for LLM generation."""

    def generate(self, prompt: str, *, context: Optional[str] = None) -> str:  # pragma: no cover - protocol
        ...


class GeminiClient:
    """Thin wrapper around the Gemini SDK used for orchestration execution."""

    def __init__(
        self,
        *,
        model: str = "gemini-2.0-flash-exp",
        api_key: Optional[str] = None,
        safety_settings: Optional[Sequence[Mapping[str, str]]] = None,
    ) -> None:
        key = api_key or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if not key:
            raise RuntimeError(
                "Gemini API key not configured. "
                "Set GEMINI_API_KEY (preferred) or GOOGLE_API_KEY before executing orchestrations."
            )
        genai.configure(api_key=key)
        self._model = genai.GenerativeModel(model)
        self._safety_settings = safety_settings

    def generate(self, prompt: str, *, context: Optional[str] = None) -> str:
        message = prompt if not context else f"{prompt}\n\n# Context\n{context}"
        response = self._model.generate_content(
            message,
            safety_settings=self._safety_settings,
        )
        if response is None:
            raise RuntimeError("Gemini returned no response.")
        if getattr(response, "prompt_feedback", None) and getattr(
            response.prompt_feedback, "block_reason", None
        ):
            reason = response.prompt_feedback.block_reason
            raise RuntimeError(f"Gemini blocked the prompt: {reason}")
        text = getattr(response, "text", None)
        if not text and getattr(response, "candidates", None):
            parts = response.candidates[0].content.parts
            text = "".join(getattr(part, "text", "") for part in parts)
        if not text:
            raise RuntimeError("Gemini returned an empty response.")
        return text.strip()


@dataclass
class AuditEntry:
    agent_id: str
    stage: str
    prompt_file: str
    dependencies: Sequence[str]
    output_file: str
    started_at: str
    duration_ms: float
    model: str

    def as_dict(self) -> Dict[str, object]:
        return {
            "agent_id": self.agent_id,
            "stage": self.stage,
            "prompt_file": self.prompt_file,
            "dependencies": list(self.dependencies),
            "output_file": self.output_file,
            "started_at": self.started_at,
            "duration_ms": self.duration_ms,
            "model": self.model,
        }


class OrchestrationExecutor:
    """Executes generated orchestration agents with an LLM client and records an audit trail."""

    def __init__(
        self,
        root: Path | str,
        *,
        llm_client: Optional[LLMClient] = None,
        model_name: str = "gemini-2.0-flash-exp",
    ) -> None:
        self.root = Path(root).resolve()
        if not self.root.exists():
            raise FileNotFoundError(f"Orchestration path does not exist: {self.root}")

        self.summary = json.loads(
            (self.root / "orchestration_summary.json").read_text(encoding="utf-8")
        )
        self.pipeline = yaml.safe_load(
            (self.root / "flows" / "main_pipeline.yaml").read_text(encoding="utf-8")
        )

        self.agent_specs = self._load_agent_specs()
        self.outputs: Dict[str, Dict[str, object]] = {}
        self.audit_entries: List[AuditEntry] = []
        self.model_name = model_name

        self.llm = llm_client or GeminiClient(model=model_name)

        self.outputs_dir = self.root / "outputs"
        self.outputs_dir.mkdir(parents=True, exist_ok=True)
        self.audit_dir = self.root / "audit"
        self.audit_dir.mkdir(parents=True, exist_ok=True)

    def _load_agent_specs(self) -> Dict[str, Dict[str, object]]:
        specs: Dict[str, Dict[str, object]] = {}
        for path in (self.root / "agents").rglob("*.acl"):
            data = yaml.safe_load(path.read_text(encoding="utf-8"))
            agent = data.get("agent", {})
            agent_id = agent.get("id")
            if not agent_id:
                continue
            specs[agent_id] = {
                "path": path,
                "stage": agent.get("stage"),
                "prompts": [str(p) for p in (agent.get("prompts") or [])],
                "depends_on": agent.get("depends_on") or [],
            }
        return specs

    def run(self, *, max_agents: Optional[int] = None, include_coordinators: bool = True) -> Path:
        executed = 0
        processed: set[str] = set()
        for stage in self.pipeline.get("stages", []):
            for agent_id in stage.get("agents", []):
                self._execute_agent(agent_id)
                processed.add(agent_id)
                executed += 1
                if max_agents is not None and executed >= max_agents:
                    return self._write_audit()
            if include_coordinators:
                coordinator = stage.get("coordinator")
                if coordinator:
                    self._execute_agent(coordinator)
                    processed.add(coordinator)
                    executed += 1
                    if max_agents is not None and executed >= max_agents:
                        return self._write_audit()

        for node in self.summary.get("nodes", []):
            agent_id = node.get("id")
            if not agent_id or agent_id in processed:
                continue
            if agent_id not in self.agent_specs:
                continue
            self._execute_agent(agent_id)
            processed.add(agent_id)
            executed += 1
            if max_agents is not None and executed >= max_agents:
                break
        return self._write_audit()

    def _execute_agent(self, agent_id: str) -> None:
        if agent_id in self.outputs:
            return
        spec = self.agent_specs.get(agent_id)
        if not spec:
            return

        prompt_file = self._select_prompt_file(spec)
        if prompt_file is None or not prompt_file.exists():
            raise FileNotFoundError(f"Prompt file not found for agent {agent_id}")
        prompt_text = prompt_file.read_text(encoding="utf-8")

        dependencies: Sequence[str] = spec.get("depends_on", [])
        context_chunks: List[str] = []
        for dependency in dependencies:
            output = self.outputs.get(dependency)
            if output:
                context_chunks.append(
                    f"## Output from {dependency}\n{output['text']}\n"
                )
        context = "\n".join(context_chunks) if context_chunks else None

        started_at = datetime.now(timezone.utc)
        start_time = time.perf_counter()
        result_text = self.llm.generate(prompt_text, context=context)
        duration_ms = (time.perf_counter() - start_time) * 1000

        output_path = self.outputs_dir / f"{agent_id.replace('.', '_')}.md"
        output_path.write_text(result_text, encoding="utf-8")

        self.outputs[agent_id] = {
            "text": result_text,
            "path": output_path,
            "stage": spec.get("stage"),
        }

        self.audit_entries.append(
            AuditEntry(
                agent_id=agent_id,
                stage=str(spec.get("stage")),
                prompt_file=str(prompt_file.relative_to(self.root)),
                dependencies=dependencies,
                output_file=str(output_path.relative_to(self.root)),
                started_at=started_at.isoformat(),
                duration_ms=duration_ms,
                model=self.model_name,
            )
        )

    def _select_prompt_file(self, spec: Mapping[str, object]) -> Optional[Path]:
        prompts = spec.get("prompts") or []
        if not prompts:
            return None
        relative = Path(str(prompts[0]))
        return (self.root / relative).resolve()

    def _write_audit(self) -> Path:
        audit_path = self.audit_dir / "orchestration_run.json"
        payload = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "output_count": len(self.outputs),
            "entries": [entry.as_dict() for entry in self.audit_entries],
        }
        audit_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return audit_path
