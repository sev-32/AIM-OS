from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import json
from typing import Iterable, List, Mapping, Optional

from schemas import BitemporalEdge, MPDNode, KPIReference

from .repository import AtomRepository, SQLiteConfig


def _normalize_owners(owners: Optional[Iterable[str]]) -> List[str]:
    if owners is None:
        return ["GPT-5 Codex", "o3pro-ai"]
    if isinstance(owners, str):
        try:
            decoded = json.loads(owners)
            if isinstance(decoded, list):
                return [str(item) for item in decoded]
        except json.JSONDecodeError:
            pass
        return [owners]
    return [str(item) for item in owners]


def draft_trunk_nodes(
    vision_tensor: Mapping[str, object],
    *,
    owners: Optional[Iterable[str]] = None,
    max_dependency_degree: int = 8,
) -> List[MPDNode]:
    """Create BTSM trunk nodes derived from a vision tensor summary."""
    summary = str(vision_tensor.get("summary", ""))
    correlation_id = vision_tensor.get("correlation_id")
    now = datetime.now(timezone.utc)
    owner_list = _normalize_owners(owners)

    tensor_policies_raw = vision_tensor.get("policy_pack_ids") or []
    tensor_policy_ids: List[str] = []
    if isinstance(tensor_policies_raw, (list, tuple, set)):
        tensor_policy_ids = [str(item).strip() for item in tensor_policies_raw if str(item).strip()]
    elif isinstance(tensor_policies_raw, str) and tensor_policies_raw.strip():
        tensor_policy_ids = [tensor_policies_raw.strip()]

    def _unique_policies(initial: Iterable[str]) -> List[str]:
        seen: List[str] = []
        for candidate in initial:
            if candidate and candidate not in seen:
                seen.append(candidate)
        return seen

    root_policy_ids = _unique_policies(["policy.mige.default", *tensor_policy_ids])
    guardrail_policy_ids = _unique_policies([*root_policy_ids, "policy.mige.guardrails"])

    root_node = MPDNode(
        mpd_id="aimos.mige.trunk",
        type="program",
        purpose="Seed vision trunk derived from Vision Tensor.",
        capabilities=["vision-tracing", "mpd-draft"],
        interfaces=["plans/seed_to_tensor.acl"],
        manager_of=["aimos.mige.trunk.guardrails"],
        depends_on=["aimos.cmc"],
        policy_pack_ids=root_policy_ids,
        budgets=["analysis:medium"],
        owners=owner_list,
        kpis=[
            KPIReference(name="MIGE_VisionFit_target", target=0.9),
        ],
        lifecycle="draft",
        witness=f"seg://plan/seed_to_tensor/{correlation_id}" if correlation_id else None,
        links=["plans/seed_to_tensor.acl"],
        max_dependency_degree=max_dependency_degree,
        tt_start=now,
        vt_start=now,
    )

    guardrail_node = MPDNode(
        mpd_id="aimos.mige.trunk.guardrails",
        type="control",
        purpose="Tracks MIGE governance guardrails for trunk evolution.",
        capabilities=["gate-validation", "seg-export"],
        interfaces=["plans/tensor_to_trunk.acl"],
        manager_of=[],
        depends_on=["aimos.mige.trunk"],
        policy_pack_ids=guardrail_policy_ids,
        budgets=["governance:low"],
        owners=owner_list,
        kpis=[KPIReference(name="MIGE_BlastRadiusFalseNegatives_target", target=0.0)],
        lifecycle="draft",
        witness=f"seg://plan/tensor_to_trunk/{correlation_id}" if correlation_id else None,
        links=["plans/tensor_to_trunk.acl"],
        max_dependency_degree=4,
        tt_start=now,
        vt_start=now,
    )

    root_node.purpose = (summary[:350] or root_node.purpose)
    return [root_node, guardrail_node]


def persist_nodes(db_path: str | Path, nodes: Iterable[MPDNode]) -> List[str]:
    """Persist MPD nodes into the repository."""
    config = SQLiteConfig(path=Path(db_path))
    repo = AtomRepository(config)
    repo.upsert_mpd_nodes(list(nodes))
    repo.close()
    return [node.mpd_id for node in nodes]


def persist_depends_on_edges(db_path: str | Path, nodes: Iterable[MPDNode]) -> int:
    """Persist depends_on edges derived from the supplied nodes."""
    config = SQLiteConfig(path=Path(db_path))
    repo = AtomRepository(config)
    now = datetime.now(timezone.utc)
    edges: List[BitemporalEdge] = []
    for node in nodes:
        for target in node.depends_on:
            edges.append(
                BitemporalEdge(
                    source_id=node.mpd_id,
                    target_id=target,
                    relation="depends_on",
                    policy_pack_ids=list(node.policy_pack_ids),
                    tt_start=node.tt_start if isinstance(node.tt_start, datetime) else now,
                    tt_end=node.tt_end if isinstance(node.tt_end, datetime) else None,
                    vt_start=node.vt_start if isinstance(node.vt_start, datetime) else now,
                    vt_end=node.vt_end if isinstance(node.vt_end, datetime) else None,
                )
            )
    if edges:
        repo.upsert_mpd_edges(edges)
    repo.close()
    return len(edges)


__all__ = ["draft_trunk_nodes", "persist_nodes", "persist_depends_on_edges"]
