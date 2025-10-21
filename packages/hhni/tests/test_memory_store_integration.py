# goals: [KR-2.2, KR-2.3, KR-3.1]
from __future__ import annotations

import os
from unittest import mock

import pytest

from cmc_service.memory_store import MemoryStore
from cmc_service.models import AtomContent, AtomCreate


@pytest.fixture()
def tmp_store(tmp_path):
    store = MemoryStore(tmp_path)
    yield store
    store.close()


def test_create_atom_with_hhni_skips_when_priority_low(tmp_store, monkeypatch):
    # goals: [KR-2.2]
    monkeypatch.setenv("DGRAPH_URL", "http://fake")
    monkeypatch.setenv("QDRANT_URL", "http://fake")

    # Mock HHNI import to avoid requirement when gate not triggered
    with mock.patch.dict("sys.modules", {"hhni.indexer": mock.Mock(), "hhni.dgraph_client": mock.Mock(), "qdrant_client": mock.Mock()}):
        atom, nodes = tmp_store.create_atom_with_hhni(
            AtomCreate(
                modality="text",
                content=AtomContent(inline="hello"),
                tags={"priority": 0.5},
            ),
            correlation_id="cid",
        )
    assert nodes == []
    assert atom.id


def test_create_atom_with_hhni_forced_build(monkeypatch, tmp_store):
    # goals: [KR-2.3]
    monkeypatch.setenv("DGRAPH_URL", "http://fake")
    monkeypatch.setenv("QDRANT_URL", "http://fake")

    dummy_node = mock.Mock()
    dummy_node.to_dict.return_value = {"id": "node1"}

    with mock.patch("hhni.dgraph_client.DGraphClient") as dgraph_cls, mock.patch("qdrant_client.QdrantClient") as qdrant_cls, mock.patch("hhni.indexer.build_hhni_for_atom", return_value=[dummy_node]):
        atom, nodes = tmp_store.create_atom_with_hhni(
            AtomCreate(
                modality="text",
                content=AtomContent(inline="Paragraph one.\n\nParagraph two."),
                tags={"priority": 0.5},
            ),
            build_hhni=True,
            correlation_id="cid",
        )
    assert nodes == [{"id": "node1"}]
    assert atom.id
    dgraph_cls.assert_called_once()
    qdrant_cls.assert_called_once()


def test_create_atom_with_hhni_handles_exception(monkeypatch, tmp_store):
    # goals: [KR-1.2]
    monkeypatch.setenv("DGRAPH_URL", "http://fake")
    monkeypatch.setenv("QDRANT_URL", "http://fake")

    with mock.patch("hhni.dgraph_client.DGraphClient"), mock.patch("qdrant_client.QdrantClient"), mock.patch("hhni.indexer.build_hhni_for_atom", side_effect=RuntimeError("fail")):
        with pytest.raises(RuntimeError):
            tmp_store.create_atom_with_hhni(
                AtomCreate(
                    modality="text",
                    content=AtomContent(inline="Paragraph one.")
                ),
                build_hhni=True,
                correlation_id="cid",
            )
