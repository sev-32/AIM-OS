# goals: [KR-2.3, KR-3.1]
from __future__ import annotations

from typing import List

import pytest

from hhni.indexer import build_hhni_for_atom
from hhni.models import HHNINode
from hhni.safety import HHNISafetyGates


class DummyAtom:
    def __init__(self, atom_id: str, inline: str, tags=None):
        self.id = atom_id
        self.content = type("Content", (), {"inline": inline, "uri": None, "media_type": "text/plain"})
        self.tags = tags or {}
        self.created_at = HHNINode.__dataclass_fields__["created_at"].default_factory()  # type: ignore
        self.hash = "hash123"
        self.witness = type("Witness", (), {"snapshot_id": None})


class DummyDGraphClient:
    def __init__(self):
        self.upsert_payloads: List[dict] = []

    def upsert_nodes(self, nodes):
        self.upsert_payloads.append({"input": list(nodes)})


class DummyQdrantClient:
    def __init__(self, fail=False):
        self.fail = fail
        self.points = []

    def upsert(self, collection_name, points):
        if self.fail:
            raise RuntimeError("qdrant down")
        self.points.extend(points)
        return points[0]["id"]


@pytest.fixture()
def atom_text() -> str:
    return "Paragraph one.\n\nParagraph two."


def test_build_hhni_for_atom_success(atom_text) -> None:
    # goals: [KR-2.3]
    atom = DummyAtom("atom1", atom_text)
    dgraph = DummyDGraphClient()
    qdrant = DummyQdrantClient()

    nodes = build_hhni_for_atom(atom=atom, dgraph_client=dgraph, qdrant_client=qdrant, correlation_id="123")

    assert len(nodes) == 1 + 2 + 2  # doc + paragraphs + sentences
    assert dgraph.upsert_payloads
    assert all("vector_id" in node.to_dict() for node in nodes if node.level > 1)


def test_build_hhni_for_atom_qdrant_failure(atom_text) -> None:
    # goals: [KR-1.2]
    atom = DummyAtom("atom2", atom_text)
    dgraph = DummyDGraphClient()
    qdrant = DummyQdrantClient(fail=True)

    with pytest.raises(RuntimeError):
        build_hhni_for_atom(atom=atom, dgraph_client=dgraph, qdrant_client=qdrant, correlation_id="xyz")
