from __future__ import annotations

import math
from dataclasses import dataclass, field
from hashlib import sha256
from typing import Iterable, List, Mapping, Optional, Sequence, Tuple, Union
from uuid import uuid4

from packages.seg import write_witness


SeedCapsule = Union[str, Mapping[str, object]]


@dataclass
class VisionTensorResult:
    tensor: List[float]
    axes: List[str]
    summary: str
    score: float
    model: str
    correlation_id: str
    policy_pack_ids: List[str] = field(default_factory=list)


@dataclass
class GateResult:
    passed: bool
    score: float
    threshold: float
    correlation_id: str
    message: str


def _to_text(seed_capsule: SeedCapsule) -> Tuple[str, List[str]]:
    if isinstance(seed_capsule, str):
        return seed_capsule, []
    text = ""
    axes: List[str] = []
    if "vision" in seed_capsule:
        text = str(seed_capsule["vision"])
    elif "description" in seed_capsule:
        text = str(seed_capsule["description"])
    else:
        text = " ".join(str(value) for value in seed_capsule.values())
    axes_value = seed_capsule.get("axes") if isinstance(seed_capsule, Mapping) else None
    if isinstance(axes_value, (list, tuple)):
        axes = [str(item) for item in axes_value]
    return text, axes


def _hash_to_vector(text: str, dimension: int = 16) -> List[float]:
    digest = sha256(text.encode("utf-8")).digest()
    # Expand digest if needed
    repeats = (dimension * 4 + len(digest) - 1) // len(digest)
    payload = (digest * repeats)[: dimension * 4]
    values: List[float] = []
    for idx in range(dimension):
        chunk = payload[idx * 4 : (idx + 1) * 4]
        integer = int.from_bytes(chunk, "big")
        values.append(integer / 0xFFFFFFFF)
    # Normalise to unit vector
    norm = math.sqrt(sum(val * val for val in values)) or 1.0
    return [val / norm for val in values]


def _cosine_similarity(vec_a: Sequence[float], vec_b: Sequence[float]) -> float:
    dot = sum(a * b for a, b in zip(vec_a, vec_b))
    mag_a = math.sqrt(sum(a * a for a in vec_a))
    mag_b = math.sqrt(sum(b * b for b in vec_b))
    if not mag_a or not mag_b:
        return 0.0
    return max(min(dot / (mag_a * mag_b), 1.0), -1.0)


def compute_tensor(
    seed_capsule: SeedCapsule,
    *,
    model: str = "deterministic-hash-v1",
    correlation_id: Optional[str] = None,
    seg_filename: str = "vision_tensor_witness.jsonl",
    axes: Optional[Iterable[str]] = None,
    policy_pack_ids: Optional[Iterable[str]] = None,
    policy_packs: Optional[Iterable[str]] = None,
) -> VisionTensorResult:
    """Compute a deterministic pseudo-embedding for the seed vision capsule."""
    text, capsule_axes = _to_text(seed_capsule)
    effective_axes: List[str]
    if axes is not None:
        effective_axes = [str(item) for item in axes]
    else:
        effective_axes = capsule_axes
    capsule_policy_ids: List[str] = []
    if isinstance(seed_capsule, Mapping):
        raw_policy = (
            seed_capsule.get("policy_pack_ids")
            or seed_capsule.get("policy_packs")
            or seed_capsule.get("policies")
        )
        if isinstance(raw_policy, (list, tuple, set)):
            capsule_policy_ids = [str(item) for item in raw_policy if str(item).strip()]
        elif isinstance(raw_policy, str) and raw_policy.strip():
            capsule_policy_ids = [raw_policy.strip()]
    provided_policy_ids = [str(item).strip() for item in (policy_pack_ids or []) if str(item).strip()]
    alias_policy_ids = [str(item).strip() for item in (policy_packs or []) if str(item).strip()]
    policy_ids: List[str] = []
    for candidate in [*provided_policy_ids, *alias_policy_ids, *capsule_policy_ids]:
        if candidate and candidate not in policy_ids:
            policy_ids.append(candidate)
    tensor = _hash_to_vector(text)
    axes_text = " ".join(effective_axes) if effective_axes else "default axes"
    axes_vector = _hash_to_vector(axes_text)
    score = float(f"{(_cosine_similarity(tensor, axes_vector) + 1) / 2:.4f}")
    corr = correlation_id or str(uuid4())
    summary = text[:280]
    axes_list = list(effective_axes)

    result = VisionTensorResult(
        tensor=tensor,
        axes=axes_list,
        summary=summary,
        score=score,
        model=model,
        correlation_id=corr,
        policy_pack_ids=policy_ids,
    )

    write_witness(
        {
            "event": "vision_tensor.compute",
            "correlation_id": corr,
            "score": score,
            "axes": effective_axes,
            "model": model,
            "policy_pack_ids": policy_ids,
        },
        filename=seg_filename,
    )
    return result


def _ensure_tensor_result(data: Union[VisionTensorResult, Mapping[str, object]]) -> VisionTensorResult:
    if isinstance(data, VisionTensorResult):
        return data
    tensor = [float(x) for x in data.get("tensor", [])]
    axes_list = [str(a) for a in data.get("axes", [])]
    summary = str(data.get("summary", ""))
    score = float(data.get("score", 0.0))
    model = str(data.get("model", "unknown"))
    correlation_id = str(data.get("correlation_id", uuid4()))
    policy_ids = [str(pid) for pid in data.get("policy_pack_ids", [])]
    return VisionTensorResult(
        tensor=tensor,
        axes=axes_list,
        summary=summary,
        score=score,
        model=model,
        correlation_id=correlation_id,
        policy_pack_ids=policy_ids,
    )

def g_vision_fit(
    result: Union[VisionTensorResult, Mapping[str, object]],
    *,
    threshold: float = 0.9,
) -> GateResult:
    """Check whether the VisionFit score clears the configured threshold."""
    vt_result = _ensure_tensor_result(result)
    passed = vt_result.score >= threshold
    message = "VisionFit OK" if passed else f"VisionFit {vt_result.score:.3f} below threshold {threshold:.3f}"
    write_witness(
        {
            "event": "gate.g_vision_fit",
            "correlation_id": vt_result.correlation_id,
            "passed": passed,
            "score": vt_result.score,
            "threshold": threshold,
        },
        filename="gates_witness.jsonl",
    )
    return GateResult(
        passed=passed,
        score=vt_result.score,
        threshold=threshold,
        correlation_id=vt_result.correlation_id,
        message=message,
    )

__all__ = ["VisionTensorResult", "GateResult", "compute_tensor", "g_vision_fit", "_ensure_tensor_result"]
