
from __future__ import annotations

import json
import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence

import yaml


@dataclass
class OrchestrationBuildResult:
    nodes: List[Dict[str, Any]]
    edges: List[Dict[str, str]]
    policy_summary: Dict[str, int]
    artifact_path: Path


@dataclass
class AgentBlueprint:
    identifier: str
    name: str
    stage: str
    stage_label: str
    role: str
    description: str
    policies: List[str]
    depends_on: List[str]
    max_dependency_degree: int
    prompt_variants: List[str]
    concurrency: int
    retry: Mapping[str, Any]
    capabilities: List[str]
    inputs: List[str]
    outputs: List[str]
    category: str = "stage"

    def acl_payload(self) -> Dict[str, Any]:
        return {
            "agent": {
                "id": self.identifier,
                "name": self.name,
                "stage": self.stage,
                "stage_label": self.stage_label,
                "role": self.role,
                "description": self.description,
                "capabilities": self.capabilities,
                "policies": self.policies,
                "depends_on": self.depends_on,
                "inputs": self.inputs,
                "outputs": self.outputs,
                "prompts": [
                    f"prompts/{self.stage}/{variant}.md" for variant in self.prompt_variants
                ],
                "concurrency": self.concurrency,
                "retry": dict(self.retry),
                "category": self.category,
            }
        }


@dataclass
class StageSpec:
    key: str
    label: str
    agents: List[AgentBlueprint]
    coordinator: AgentBlueprint
    concurrency: int
    retry: Mapping[str, Any]


def _ensure_path(value: Path | str) -> Path:
    return Path(value).expanduser().resolve()


def _load_seed(seed: Dict[str, Any] | Path | str) -> Mapping[str, Any]:
    if isinstance(seed, (str, Path)):
        path = _ensure_path(seed)
        text = path.read_text(encoding="utf-8")
        if path.suffix.lower() in {".yml", ".yaml"}:
            return yaml.safe_load(text)
        return json.loads(text)
    return seed


def _slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")
    return slug or "orchestration"


def _dedupe(items: Sequence[str]) -> List[str]:
    seen: set[str] = set()
    result: List[str] = []
    for item in items:
        key = item.strip()
        if key and key not in seen:
            seen.add(key)
            result.append(key)
    return result


def build_orchestration(
    seed: Dict[str, Any] | Path | str,
    *,
    output_dir: Path | str | None = None,
    filename: Optional[str] = None,
) -> OrchestrationBuildResult:
    payload = _load_seed(seed)
    if "pipeline_stages" in payload:
        return _build_complex_orchestration(payload, output_dir, filename)
    return _build_simple_graph(payload, output_dir, filename)


def _build_simple_graph(
    payload: Mapping[str, Any],
    output_dir: Path | str | None,
    filename: Optional[str],
) -> OrchestrationBuildResult:
    agents: Iterable[Mapping[str, Any]] = payload.get("agents", []) or []

    agent_index: Dict[str, Mapping[str, Any]] = {}
    nodes: List[Dict[str, Any]] = []
    for agent in agents:
        agent_id = str(agent.get("id", "")).strip()
        if not agent_id:
            raise ValueError("Agent entry missing 'id'")
        if agent_id in agent_index:
            raise ValueError(f"Duplicate agent id: {agent_id}")
        policies = [str(p).strip() for p in (agent.get("policy_pack_ids") or []) if str(p).strip()]
        nodes.append(
            {
                "id": agent_id,
                "role": agent.get("role", "agent"),
                "policy_pack_ids": policies,
                "max_dependency_degree": agent.get("max_dependency_degree"),
            }
        )
        agent_index[agent_id] = agent

    edges: List[Dict[str, str]] = []
    policy_summary: Dict[str, int] = {}
    for node in nodes:
        for policy in node["policy_pack_ids"]:
            policy_summary[policy] = policy_summary.get(policy, 0) + 1

    for node in nodes:
        agent = agent_index[node["id"]]
        depends = agent.get("depends_on") or []
        relation = agent.get("relation", "depends_on")
        for target in depends:
            target_id = str(target).strip()
            if target_id not in agent_index:
                raise ValueError(f"Agent {node['id']} depends on unknown agent {target_id}")
            edges.append(
                {
                    "source": node["id"],
                    "target": target_id,
                    "relation": relation,
                }
            )

    out_dir = _ensure_path(output_dir) if output_dir else Path.cwd()
    out_dir.mkdir(parents=True, exist_ok=True)
    artifact_path = out_dir / (filename or "orchestration_build.json")
    artifact_payload = {
        "nodes": nodes,
        "edges": edges,
        "policy_summary": policy_summary,
    }
    artifact_text = json.dumps(artifact_payload, indent=2)
    artifact_path.write_text(artifact_text, encoding="utf-8")

    return OrchestrationBuildResult(
        nodes=nodes,
        edges=edges,
        policy_summary=policy_summary,
        artifact_path=artifact_path,
    )


def _build_complex_orchestration(
    payload: Mapping[str, Any],
    output_dir: Path | str | None,
    filename: Optional[str],
) -> OrchestrationBuildResult:
    name = payload.get("name") or "ResearchOrchestrator"
    base_dir = _ensure_path(output_dir) if output_dir else Path.cwd()
    root_dir = base_dir / _slugify(name)
    root_dir.mkdir(parents=True, exist_ok=True)

    base_policies = _base_policies(payload.get("policies"))
    stage_specs = _normalise_pipeline(payload.get("pipeline_stages") or [], base_policies)
    global_agents = _build_global_agents(base_policies, stage_specs, payload.get("global_agents") or [])

    global_ids = [agent.identifier for agent in global_agents]

    for stage in stage_specs:
        stage.coordinator.depends_on = _dedupe(global_ids)
        for agent in stage.agents:
            agent.depends_on = _dedupe(
                [stage.coordinator.identifier, *global_ids]
            )

    retry_manager_id = "orchestration.retry_manager"

    all_agents: List[AgentBlueprint] = []
    for stage in stage_specs:
        all_agents.extend(stage.agents)
        all_agents.append(stage.coordinator)
    all_agents.extend(global_agents)

    _write_agents(root_dir, stage_specs, global_agents)
    edge_list = _build_edges(stage_specs, global_agents, retry_manager_id)
    policy_summary = _summarise_policies(all_agents)
    nodes_payload = [
        {
            "id": agent.identifier,
            "name": agent.name,
            "stage": agent.stage,
            "role": agent.role,
            "policy_pack_ids": agent.policies,
            "max_dependency_degree": agent.max_dependency_degree,
            "depends_on": agent.depends_on,
            "category": agent.category,
        }
        for agent in all_agents
    ]

    summary_payload = {
        "name": name,
        "description": payload.get("description", ""),
        "nodes": nodes_payload,
        "edges": edge_list,
        "policy_summary": policy_summary,
        "metadata": {
            "stage_count": len(stage_specs),
            "agent_count": len(nodes_payload),
            "policy_keys": sorted(policy_summary.keys()),
        },
    }

    summary_path = root_dir / (filename or "orchestration_summary.json")
    summary_path.write_text(json.dumps(summary_payload, indent=2), encoding="utf-8")

    _write_flows(root_dir, stage_specs, global_agents, edge_list)
    _write_prompts(root_dir, stage_specs, global_agents)
    _write_gates(root_dir)
    _write_policies(root_dir, payload.get("policies") or {})
    _write_generated_tests(root_dir, summary_path)
    _write_readme(root_dir, name, payload.get("description", ""))

    return OrchestrationBuildResult(
        nodes=nodes_payload,
        edges=edge_list,
        policy_summary=policy_summary,
        artifact_path=summary_path,
    )


def _base_policies(seed_policies: Mapping[str, Any] | None) -> List[str]:
    policies = {
        "policy.research_depth": "max_research_depth",
        "policy.evidence_threshold": "evidence_threshold",
        "policy.latency_budget": "max_total_time",
    }
    if isinstance(seed_policies, Mapping):
        for key in seed_policies:
            slug = _slugify(str(key))
            policies[f"policy.seed.{slug}"] = str(key)
    return sorted(policies.keys())


def _normalise_pipeline(pipeline: Iterable[Any], base_policies: Sequence[str]) -> List[StageSpec]:
    stage_specs: List[StageSpec] = []
    for entry in pipeline:
        if not isinstance(entry, Mapping):
            raise TypeError("Each pipeline stage must be a mapping with 'name'/'label' and 'agents'.")

        label = str(entry.get("label") or entry.get("name") or "Stage")
        key = str(entry.get("key") or _slugify(label))
        agents_iterable = entry.get("agents") or []
        if not isinstance(agents_iterable, Iterable):
            raise TypeError(f"Stage '{label}' must contain an iterable of agents.")

        agent_entries = list(agents_iterable)
        retry_cfg = entry.get("retry") or {"max_attempts": 3, "strategy": "exponential", "cooldown_seconds": 15}
        concurrency = int(entry.get("concurrency") or max(len(agent_entries), 1))

        stage_agents: List[AgentBlueprint] = []
        for raw_agent in agent_entries:
            if isinstance(raw_agent, Mapping):
                agent_label = str(raw_agent.get("label") or raw_agent.get("name") or raw_agent.get("id") or "agent")
                agent_role = str(raw_agent.get("role") or "specialist")
                description = str(
                    raw_agent.get("description")
                    or f"Executes {agent_label} responsibilities within the {label} stage."
                )
                capabilities = [str(cap) for cap in raw_agent.get("capabilities", []) if str(cap).strip()]
                extra_policies = [str(pol) for pol in raw_agent.get("policies", []) if str(pol).strip()]
                concurrency_override = raw_agent.get("concurrency")
                agent_retry = raw_agent.get("retry")
            else:
                agent_label = str(raw_agent)
                agent_role = "specialist"
                description = f"Executes {agent_label} responsibilities within the {label} stage."
                capabilities = []
                extra_policies = []
                concurrency_override = None
                agent_retry = None

            agent_slug = _slugify(agent_label)
            identifier = f"{key}.{agent_slug}"
            prompt_variants = [f"{agent_slug}_primary", f"{agent_slug}_fallback", f"{agent_slug}_summary"]
            policies = _dedupe([*base_policies, *extra_policies])
            concurrency_value = int(concurrency_override or 1)
            retry_value = agent_retry or retry_cfg

            stage_agents.append(
                AgentBlueprint(
                    identifier=identifier,
                    name=agent_label,
                    stage=key,
                    stage_label=label,
                    role=agent_role,
                    description=description,
                    policies=policies,
                    depends_on=[],
                    max_dependency_degree=max(len(prompt_variants) * 4, 16),
                    prompt_variants=prompt_variants,
                    concurrency=concurrency_value,
                    retry=retry_value,
                    capabilities=capabilities,
                    inputs=[f"{key}.input"],
                    outputs=[f"{key}.output"],
                )
            )

        coordinator_id = f"{key}.coordinator"
        coordinator_blueprint = AgentBlueprint(
            identifier=coordinator_id,
            name=f"{label} Coordinator",
            stage=key,
            stage_label=label,
            role="coordinator",
            description=f"Coordinates all {label} agents and manages hand-offs to subsequent stages.",
            policies=_dedupe([*base_policies, "policy.stage_alignment"]),
            depends_on=[],
            max_dependency_degree=max(len(stage_agents) * 4, 32),
            prompt_variants=[f"{key}_coordination"],
            concurrency=concurrency,
            retry=retry_cfg,
            capabilities=["schedule", "governance", "quality_assurance"],
            inputs=[f"{key}.input"],
            outputs=[f"{key}.handoff"],
            category="coordinator",
        )

        stage_specs.append(
            StageSpec(
                key=key,
                label=label,
                agents=stage_agents,
                coordinator=coordinator_blueprint,
                concurrency=concurrency,
                retry=retry_cfg,
            )
        )

    return stage_specs


def _build_global_agents(
    base_policies: Sequence[str],
    stage_specs: Sequence[StageSpec],
    seed_global: Iterable[Any],
) -> List[AgentBlueprint]:
    coordinator_ids = [stage.coordinator.identifier for stage in stage_specs]
    derived_policies = _dedupe([*base_policies, "policy.stage_alignment", "policy.system_observability"])

    defaults: List[Dict[str, Any]] = [
        {
            "identifier": "orchestration.supervisor",
            "name": "Orchestration Supervisor",
            "role": "executive",
            "description": "Directs the full orchestration lifecycle and resolves contention across stages.",
            "category": "supervisor",
        },
        {
            "identifier": "orchestration.observability_hub",
            "name": "Observability Hub",
            "role": "telemetry",
            "description": "Aggregates metrics, traces, and structured logs for every stage transition.",
            "category": "observer",
        },
        {
            "identifier": "orchestration.policy_enforcer",
            "name": "Policy Enforcer",
            "role": "governance",
            "description": "Ensures every agent complies with governance packs before execution proceeds.",
            "category": "governance",
        },
        {
            "identifier": "orchestration.audit_trail",
            "name": "Audit Trail Emitter",
            "role": "provenance",
            "description": "Emits immutable VIF evidence for each agent execution.",
            "category": "observer",
        },
        {
            "identifier": "orchestration.retry_manager",
            "name": "Retry Manager",
            "role": "resilience",
            "description": "Coordinates retries, exponential backoff, and safe restarts across stages.",
            "category": "resilience",
        },
        {
            "identifier": "orchestration.quality_board",
            "name": "Quality Board",
            "role": "analysis",
            "description": "Evaluates outputs against evidence thresholds and signals corrective actions.",
            "category": "analysis",
        },
    ]

    extras: List[Dict[str, Any]] = []
    for raw in seed_global:
        if isinstance(raw, Mapping):
            extras.append(raw)

    blueprints: List[AgentBlueprint] = []
    for spec in [*defaults, *extras]:
        identifier = str(spec.get("identifier") or spec.get("id") or spec.get("name") or "global.agent")
        name = str(spec.get("name") or identifier.title())
        role = str(spec.get("role") or "support")
        description = str(spec.get("description") or "Global orchestration support agent")
        category = str(spec.get("category") or "support")
        slug_stage = "orchestration"
        stage_label = "Global Orchestration"
        prompt_slug = _slugify(identifier.split(".")[-1])
        prompt_variants = [f"{prompt_slug}_primary", f"{prompt_slug}_monitor", f"{prompt_slug}_summary"]

        blueprint = AgentBlueprint(
            identifier=identifier,
            name=name,
            stage=slug_stage,
            stage_label=stage_label,
            role=role,
            description=description,
            policies=_dedupe([*derived_policies, "policy.system_fallbacks"]),
            depends_on=list(coordinator_ids),
            max_dependency_degree=max(len(coordinator_ids) * 2, 24),
            prompt_variants=prompt_variants,
            concurrency=1,
            retry={"max_attempts": 5, "strategy": "exponential", "cooldown_seconds": 30},
            capabilities=["monitor", "govern", "recover"],
            inputs=["orchestration.signal"],
            outputs=["orchestration.report"],
            category=category,
        )
        blueprints.append(blueprint)

    return blueprints


def _write_agents(root_dir: Path, stages: Sequence[StageSpec], global_agents: Sequence[AgentBlueprint]) -> None:
    agents_dir = root_dir / "agents"
    for stage in stages:
        stage_dir = agents_dir / stage.key
        stage_dir.mkdir(parents=True, exist_ok=True)
        for agent in [*stage.agents, stage.coordinator]:
            acl_path = stage_dir / f"{_slugify(agent.name)}.acl"
            acl_path.write_text(
                yaml.safe_dump(agent.acl_payload(), sort_keys=False, indent=2),
                encoding="utf-8",
            )

    orchestration_dir = agents_dir / "orchestration"
    orchestration_dir.mkdir(parents=True, exist_ok=True)
    for agent in global_agents:
        acl_path = orchestration_dir / f"{_slugify(agent.name)}.acl"
        acl_path.write_text(
            yaml.safe_dump(agent.acl_payload(), sort_keys=False, indent=2),
            encoding="utf-8",
        )


def _build_edges(
    stages: Sequence[StageSpec],
    global_agents: Sequence[AgentBlueprint],
    retry_manager_id: str,
) -> List[Dict[str, str]]:
    edges: List[Dict[str, str]] = []
    seen: set[tuple[str, str, str]] = set()

    def add_edge(source: str, target: str, relation: str) -> None:
        if source == target:
            return
        key = (source, target, relation)
        if key not in seen:
            edges.append({"source": source, "target": target, "relation": relation})
            seen.add(key)

    for stage in stages:
        for agent in [*stage.agents, stage.coordinator]:
            for dependency in agent.depends_on:
                add_edge(agent.identifier, dependency, "depends_on")

    for global_agent in global_agents:
        for dependency in global_agent.depends_on:
            add_edge(global_agent.identifier, dependency, "monitors")

    for idx, stage in enumerate(stages[:-1]):
        next_stage = stages[idx + 1]
        for source_agent in stage.agents:
            for target_agent in next_stage.agents:
                add_edge(source_agent.identifier, target_agent.identifier, "feeds")
        add_edge(stage.coordinator.identifier, next_stage.coordinator.identifier, "handoff")

    stage_map = {stage.key: stage for stage in stages}
    if "analysis" in stage_map and "validation" in stage_map:
        for analysis_agent in stage_map["analysis"].agents:
            for validation_agent in stage_map["validation"].agents:
                add_edge(analysis_agent.identifier, validation_agent.identifier, "feedback")
                add_edge(validation_agent.identifier, analysis_agent.identifier, "feedback")

    for stage in stages:
        for agent in stage.agents:
            add_edge(stage.coordinator.identifier, agent.identifier, "controls")
            add_edge(agent.identifier, stage.coordinator.identifier, "reports")
            add_edge(agent.identifier, retry_manager_id, "retry_signal")
            add_edge(retry_manager_id, agent.identifier, "retry_dispatch")
        for global_agent in global_agents:
            add_edge(stage.coordinator.identifier, global_agent.identifier, "reports")
            add_edge(global_agent.identifier, stage.coordinator.identifier, "oversees")

    return edges


def _summarise_policies(agents: Sequence[AgentBlueprint]) -> Dict[str, int]:
    counter: Counter[str] = Counter()
    for agent in agents:
        counter.update(agent.policies)
    return dict(sorted(counter.items()))


def _write_prompts(root_dir: Path, stages: Sequence[StageSpec], global_agents: Sequence[AgentBlueprint]) -> None:
    prompts_dir = root_dir / "prompts"
    for stage in stages:
        stage_dir = prompts_dir / stage.key
        stage_dir.mkdir(parents=True, exist_ok=True)
        for agent in stage.agents:
            for variant in agent.prompt_variants:
                prompt_path = stage_dir / f"{variant}.md"
                prompt_path.write_text(
                    _prompt_template(
                        agent_name=agent.name,
                        stage_label=stage.label,
                        variant=variant,
                        policies=agent.policies,
                    ),
                    encoding="utf-8",
                )
        coordinator_variant = stage.coordinator.prompt_variants[0]
        prompt_path = stage_dir / f"{coordinator_variant}.md"
        prompt_path.write_text(
            _prompt_template(
                agent_name=stage.coordinator.name,
                stage_label=stage.label,
                variant=coordinator_variant,
                policies=stage.coordinator.policies,
            ),
            encoding="utf-8",
        )

    orchestration_dir = prompts_dir / "orchestration"
    orchestration_dir.mkdir(parents=True, exist_ok=True)
    for agent in global_agents:
        for variant in agent.prompt_variants:
            prompt_path = orchestration_dir / f"{variant}.md"
            prompt_path.write_text(
                _prompt_template(
                    agent_name=agent.name,
                    stage_label=agent.stage_label,
                    variant=variant,
                    policies=agent.policies,
                ),
                encoding="utf-8",
            )




def _prompt_template(agent_name: str, stage_label: str, variant: str, policies: Sequence[str]) -> str:
    variant_title = variant.replace("_", " ").title()
    policy_text = "\n".join(f"- {policy}" for policy in policies)
    return (
        f"# {agent_name} :: {variant_title}\n"
        f"Stage: {stage_label}\n\n"
        "## Objectives\n"
        "- Maintain evidence alignment and governance compliance.\n"
        "- Respect orchestration policies while completing assigned actions.\n"
        "\n## Policy Context\n"
        f"{policy_text if policy_text else '- (no explicit policies)'}\n\n"
        "## Required Outputs\n"
        "- Structured summary of findings.\n"
        "- Confidence score with supporting evidence identifiers.\n"
        "- Next-step recommendation or escalation flag.\n"
    )

def _write_flows(
    root_dir: Path,
    stages: Sequence[StageSpec],
    global_agents: Sequence[AgentBlueprint],
    edges: Sequence[Dict[str, str]],
) -> None:
    flows_dir = root_dir / "flows"
    flows_dir.mkdir(parents=True, exist_ok=True)

    pipeline = {
        "stages": [
            {
                "key": stage.key,
                "label": stage.label,
                "agents": [agent.identifier for agent in stage.agents],
                "coordinator": stage.coordinator.identifier,
            }
            for stage in stages
        ],
        "global_agents": [agent.identifier for agent in global_agents],
        "edges": edges,
    }

    (flows_dir / "main_pipeline.yaml").write_text(
        yaml.safe_dump(pipeline, sort_keys=False, indent=2),
        encoding="utf-8",
    )

    feedback_loops = {
        "loops": [
            {
                "name": "analysis_validation_feedback",
                "sources": [agent.identifier for agent in _stage_by_key(stages, "analysis").agents]
                if _stage_by_key(stages, "analysis")
                else [],
                "targets": [agent.identifier for agent in _stage_by_key(stages, "validation").agents]
                if _stage_by_key(stages, "validation")
                else [],
                "mode": "bidirectional",
                "criteria": ["evidence_threshold >= 0.8", "no_conflicts_detected"],
            },
            *[
                {
                    "name": f"{stage.key}_retry_loop",
                    "stage": stage.key,
                    "manager": "orchestration.retry_manager",
                    "trigger": "quality_board",
                    "max_attempts": stage.retry.get("max_attempts", 3),
                }
                for stage in stages
            ],
        ]
    }

    (flows_dir / "feedback_loops.yaml").write_text(
        yaml.safe_dump(feedback_loops, sort_keys=False, indent=2),
        encoding="utf-8",
    )

    parallel_groups = {
        "groups": [
            {
                "name": f"{stage.key}_parallel",
                "members": [agent.identifier for agent in stage.agents],
                "concurrency": stage.concurrency,
            }
            for stage in stages
        ],
        "supervisors": [agent.identifier for agent in global_agents],
    }

    (flows_dir / "parallel_execution.yaml").write_text(
        yaml.safe_dump(parallel_groups, sort_keys=False, indent=2),
        encoding="utf-8",
    )


def _stage_by_key(stages: Sequence[StageSpec], key: str) -> Optional[StageSpec]:
    for stage in stages:
        if stage.key == key:
            return stage
    return None


def _write_gates(root_dir: Path) -> None:
    gates_dir = root_dir / "gates"
    gates_dir.mkdir(parents=True, exist_ok=True)
    gate_specs = {
        "g_search_complete.py": "Search stage must deliver the required corpus before extraction begins.",
        "g_extraction_quality.py": "Extraction outputs must contain traceable evidence identifiers.",
        "g_analysis_depth.py": "Analysis stage must reach depth scores within the acceptable threshold.",
        "g_validation_passed.py": "Validation stage verifies logic, consistency, and fact checks before reporting.",
    }
    template = (
        '"""Autogenerated orchestration gate."""\n\n'
        'from typing import Mapping\n\n\n'
        'def evaluate(context: Mapping[str, object]) -> bool:\n'
        '    """Return True when gate conditions are satisfied."""\n'
        '    required = context.get("required", 0)\n'
        '    achieved = context.get("achieved", 0)\n'
        '    return bool(achieved >= required and context.get("status") == "ready")\n\n\n'
        'DESCRIPTION = {description!r}\n'
    )
    for filename, description in gate_specs.items():
        (gates_dir / filename).write_text(
            template.format(description=description),
            encoding="utf-8",
        )


def _write_policies(root_dir: Path, seed_policies: Mapping[str, Any]) -> None:
    policies_dir = root_dir / "policies"
    policies_dir.mkdir(parents=True, exist_ok=True)
    derived = {
        "base": {
            "max_research_depth": seed_policies.get("max_research_depth", 3),
            "evidence_threshold": seed_policies.get("evidence_threshold", 0.8),
            "max_total_time_minutes": seed_policies.get("max_total_time", 60),
        },
        "stage_overrides": {
            key: value
            for key, value in seed_policies.items()
            if key not in {"max_research_depth", "evidence_threshold", "max_total_time"}
        },
    }
    (policies_dir / "research_governance.json").write_text(
        json.dumps(derived, indent=2),
        encoding="utf-8",
    )




def _write_generated_tests(root_dir: Path, summary_path: Path) -> None:
    tests_dir = root_dir / "tests"
    tests_dir.mkdir(parents=True, exist_ok=True)

    summary_literal = repr(str(summary_path.relative_to(root_dir)))
    flows_literal = repr("flows")

    test_e2e = (
        "from pathlib import Path\n"
        "import json\n"
        "import yaml\n\n\n"
        "BASE_DIR = Path(__file__).resolve().parent.parent\n\n"
        "def test_pipeline_summary_counts() -> None:\n"
        "    summary_path = BASE_DIR / {summary}\n"
        "    data = json.loads(summary_path.read_text(encoding='utf-8'))\n"
        "    assert data['metadata']['agent_count'] >= 20\n"
        "    assert len(data['edges']) >= 80\n"
        "    assert sorted(data['policy_summary'])\n\n"
        "def test_pipeline_flow_files() -> None:\n"
        "    flows_dir = BASE_DIR / {flows}\n"
        "    main_pipeline = yaml.safe_load((flows_dir / 'main_pipeline.yaml').read_text(encoding='utf-8'))\n"
        "    assert main_pipeline['stages']\n"
        "    parallel = yaml.safe_load((flows_dir / 'parallel_execution.yaml').read_text(encoding='utf-8'))\n"
        "    assert parallel['groups']\n"
    ).format(summary=summary_literal, flows=flows_literal)

    (tests_dir / "test_pipeline_e2e.py").write_text(test_e2e, encoding="utf-8")

    test_parallel = (
        "from pathlib import Path\n"
        "import yaml\n\n\n"
        "BASE_DIR = Path(__file__).resolve().parent.parent\n\n"
        "def test_parallel_groups_have_members() -> None:\n"
        "    flows_dir = BASE_DIR / {flows}\n"
        "    parallel = yaml.safe_load((flows_dir / 'parallel_execution.yaml').read_text(encoding='utf-8'))\n"
        "    for group in parallel['groups']:\n"
        "        assert len(group['members']) >= 3\n"
    ).format(flows=flows_literal)

    (tests_dir / "test_parallel_agents.py").write_text(test_parallel, encoding="utf-8")

def _write_readme(root_dir: Path, name: str, description: str) -> None:
    readme = root_dir / "README.md"
    readme.write_text(
        (
            f"# {name}\n\n"
            f"{description or 'Autogenerated orchestration harness for Test 8.1.'}\n\n"
            "## Contents\n"
            "- agents/: ACL specifications for every orchestration agent.\n"
            "- prompts/: Prompt templates grouped by stage.\n"
            "- flows/: Pipeline, feedback, and parallel execution blueprints.\n"
            "- gates/: Execution gates guarding stage transitions.\n"
            "- policies/: Governance snapshot applied during orchestration.\n"
            "- tests/: Lightweight regression scaffolding.\n"
            "- orchestration_summary.json: Node, edge, and policy overview.\n"
        ),
        encoding="utf-8",
    )
