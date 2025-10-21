# goals: [KR-2.2, KR-3.1]
from __future__ import annotations

import pytest

from hhni.safety import HHNISafetyGates, HHNIQueryGates


class DummyAtom:
    def __init__(self, inline: str | None = "hello", uri: str | None = None):
        self.content = type("Content", (), {"inline": inline, "uri": uri, "media_type": "text/plain"})


def test_validate_atom_pre_build_allows_small_inline() -> None:
    atom = DummyAtom(inline="x" * 10)
    HHNISafetyGates.validate_atom_pre_build(atom)


def test_validate_atom_pre_build_rejects_large_inline() -> None:
    atom = DummyAtom(inline="x" * (HHNISafetyGates.MAX_ATOM_SIZE + 1))
    with pytest.raises(ValueError):
        HHNISafetyGates.validate_atom_pre_build(atom)


def test_validate_atom_pre_build_disallows_uri() -> None:
    atom = DummyAtom(inline=None, uri="s3://bucket/file")
    with pytest.raises(ValueError):
        HHNISafetyGates.validate_atom_pre_build(atom)


def test_validate_node_count_ok() -> None:
    HHNISafetyGates.validate_node_count([object()] * HHNISafetyGates.MAX_NODES_PER_ATOM)


def test_validate_node_count_exceeds_limit() -> None:
    with pytest.raises(RuntimeError):
        HHNISafetyGates.validate_node_count([object()] * (HHNISafetyGates.MAX_NODES_PER_ATOM + 1))


def test_validate_text_length_paragraph_limit() -> None:
    HHNISafetyGates.validate_text_length("a" * HHNISafetyGates.MAX_PARAGRAPH_LENGTH, "paragraph")
    with pytest.raises(ValueError):
        HHNISafetyGates.validate_text_length("a" * (HHNISafetyGates.MAX_PARAGRAPH_LENGTH + 1), "paragraph")


def test_query_limits_add_first() -> None:
    query = "queryHHNINode(filter: { level: { eq: 2 } }) { id }"
    limited = HHNIQueryGates.apply_limits(query)
    assert "first:" in limited


def test_query_limits_respect_existing_first() -> None:
    query = "queryHHNINode(first: 20, filter: { level: { eq: 2 } }) { id }"
    limited = HHNIQueryGates.apply_limits(query, first=500)
    assert limited.count("first:") == 1
    assert "first: 20" in limited


def test_query_depth_validation() -> None:
    HHNIQueryGates.validate_depth(HHNIQueryGates.MAX_TRAVERSAL_DEPTH)
    with pytest.raises(ValueError):
        HHNIQueryGates.validate_depth(HHNIQueryGates.MAX_TRAVERSAL_DEPTH + 1)
