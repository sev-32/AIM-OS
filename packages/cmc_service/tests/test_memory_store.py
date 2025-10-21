from __future__ import annotations

from pathlib import Path
import os

import pytest

from cmc_service.memory_store import MemoryStore
from cmc_service.models import AtomContent, AtomCreate
from cmc_service.store_io import JournalCorruptionError


@pytest.fixture()
def sqlite_store(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> MemoryStore:
    monkeypatch.setenv("CMC_BACKEND", "sqlite")
    store_path = tmp_path / "cmc"
    store = MemoryStore(store_path)
    yield store
    store.close()
    monkeypatch.delenv("CMC_BACKEND", raising=False)


@pytest.fixture()
def jsonl_store(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> MemoryStore:
    monkeypatch.setenv("CMC_BACKEND", "jsonl")
    store_path = tmp_path / "cmc"
    store = MemoryStore(store_path)
    yield store
    store.close()
    monkeypatch.delenv("CMC_BACKEND", raising=False)


@pytest.mark.parametrize("backend_fixture", ["sqlite_store", "jsonl_store"])
def test_create_and_list_atom(request: pytest.FixtureRequest, backend_fixture: str) -> None:
    store: MemoryStore = request.getfixturevalue(backend_fixture)
    atom = store.create_atom(
        AtomCreate(
            modality="text",
            content=AtomContent(inline="Hello", media_type="text/plain"),
            tags={"example": 1.0},
        )
    )

    atoms = list(store.list_atoms())
    assert len(atoms) == 1
    assert atoms[0].id == atom.id
    assert atoms[0].tags["example"] == pytest.approx(1.0)


@pytest.mark.parametrize("backend_fixture", ["sqlite_store", "jsonl_store"])
def test_snapshot_roundtrip(request: pytest.FixtureRequest, backend_fixture: str) -> None:
    store: MemoryStore = request.getfixturevalue(backend_fixture)
    atom = store.create_atom(
        AtomCreate(
            modality="text",
            content=AtomContent(inline="World"),
        )
    )
    snapshot = store.create_snapshot()
    assert atom.id in snapshot.atom_ids

    replayed = list(store.replay_snapshot(snapshot.id))
    assert len(replayed) == 1
    assert replayed[0].id == atom.id


@pytest.mark.parametrize("backend_fixture", ["sqlite_store", "jsonl_store"])
def test_snapshot_deterministic(request: pytest.FixtureRequest, backend_fixture: str) -> None:
    store: MemoryStore = request.getfixturevalue(backend_fixture)
    for word in ["alpha", "beta", "gamma"]:
        store.create_atom(
            AtomCreate(modality="text", content=AtomContent(inline=word))
        )
    snapshot1 = store.create_snapshot()
    snapshot2 = store.create_snapshot()
    assert snapshot1.id == snapshot2.id


def test_snapshot_id_stable_after_reload(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CMC_BACKEND", "sqlite")
    store_path = tmp_path / "cmc"

    store = MemoryStore(store_path)
    for word in ["delta", "epsilon", "zeta"]:
        store.create_atom(
            AtomCreate(modality="text", content=AtomContent(inline=word))
        )
    original_snapshot = store.create_snapshot(note="baseline")
    store.close()

    reloaded_store = MemoryStore(store_path)
    reloaded_snapshot = reloaded_store.create_snapshot(note="baseline")
    assert reloaded_snapshot.id == original_snapshot.id
    reloaded_store.close()
    monkeypatch.delenv("CMC_BACKEND", raising=False)


def test_journal_corruption_triggers_quarantine(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CMC_BACKEND", "jsonl")
    store_path = tmp_path / "cmc"
    store = MemoryStore(store_path)
    atom = store.create_atom(
        AtomCreate(modality="text", content=AtomContent(inline="corrupt"))
    )
    store.create_snapshot()
    store.close()

    atoms_log = store_path / "atoms.log"
    data = atoms_log.read_bytes()
    atoms_log.write_bytes(data[:-1])

    with pytest.raises(JournalCorruptionError):
        MemoryStore(store_path)
    monkeypatch.delenv("CMC_BACKEND", raising=False)


if __name__ == "__main__":  # pragma: no cover
    pytest.main([__file__])
