from __future__ import annotations

import json
import os
from collections import OrderedDict
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from time import perf_counter
from typing import Any, Dict, Iterable, Iterator, List, Mapping, Optional, Tuple
from uuid import uuid4
import logging

from .models import (
    Atom,
    AtomContent,
    AtomCreate,
    Snapshot,
    SnapshotStats,
    WitnessStub,
)
from .repository import AtomRepository, SQLiteConfig
from .store_io import Journal, JournalCorruptionError
from .logging_utils import (
    ATOMS_CREATED_TOTAL,
    SNAPSHOT_DURATION,
    SNAPSHOTS_CREATED_TOTAL,
    WRITE_ERRORS_TOTAL,
)


MAX_INLINE_PAYLOAD = 1_000_000  # 1 MB
MAX_TOTAL_PAYLOAD = 100_000_000  # 100 MB
MAX_TAGS_PER_ATOM = 20
MAX_TAG_KEY_LENGTH = 50
MIN_TAG_WEIGHT = 0.0
MAX_TAG_WEIGHT = 1.0


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _log_extra(
    *,
    action: str,
    correlation_id: Optional[str],
    **kwargs: Any,
) -> Dict[str, Any]:
    payload = {
        "ts": _utc_now_iso(),
        "action": action,
        "correlation_id": correlation_id,
    }
    payload.update({k: v for k, v in kwargs.items() if v is not None})
    return {"json": payload}


def _datetime_to_iso(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


class MemoryStore:
    """Deterministic memory store with optional SQLite backend."""

    def __init__(self, base_path: str | os.PathLike[str]):
        self.logger = logging.getLogger("cmc_service.store")
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
        (self.base_path / "payloads").mkdir(exist_ok=True)
        (self.base_path / "quarantine").mkdir(exist_ok=True)
        (self.base_path / "index" / "tags").mkdir(parents=True, exist_ok=True)

        backend = os.environ.get("CMC_BACKEND", "sqlite").lower()
        if backend not in {"sqlite", "jsonl"}:
            raise ValueError("CMC_BACKEND must be 'sqlite' or 'jsonl'")
        self._backend = backend

        self._counters = {
            "atoms_created_total": {},
            "snapshots_created_total": 0,
            "write_errors_total": 0,
        }

        self._snapshot_duration_ms: List[float] = []

        # Storage backends
        self._atom_journal = Journal(self.base_path / "atoms.log") if self._backend == "jsonl" else None
        self._snapshot_journal = Journal(self.base_path / "snapshots.log") if self._backend == "jsonl" else None
        self._repo = None
        self._repo_config: Optional[SQLiteConfig] = None
        if self._backend == "sqlite":
            db_path = self.base_path / "cmc.db"
            self._repo_config = SQLiteConfig(path=db_path)
            self._repo = AtomRepository(self._repo_config)

        # in-memory cache for quick access (limited)
        self._atoms: OrderedDict[str, Atom] = OrderedDict()
        self._snapshots: Dict[str, Snapshot] = {}

        # HHNI clients (lazy)
        self._hhni_dgraph_client = None
        self._hhni_qdrant_client = None

        self._load_existing()
        self.logger.info(
            "store.init.complete",
            extra=_log_extra(
                action="store.init",
                correlation_id=None,
                path=str(self.base_path),
                atoms=len(self._atoms),
                snapshots=len(self._snapshots),
                backend=self._backend,
            ),
        )

    # ------------------------------------------------------------------
    # public API

    def create_atom(self, payload: AtomCreate, *, correlation_id: Optional[str] = None) -> Atom:
        atom_id = str(uuid4())
        normalized_tags = self._validate_tags(payload.tags)
        metadata = dict(payload.metadata)

        normalized_content = self._prepare_content(atom_id, payload.content)
        if normalized_content.inline is None and payload.content.inline is not None:
            metadata["payload_offload"] = True

        normalized_payload = AtomCreate(
            modality=payload.modality,
            content=normalized_content,
            tags=normalized_tags,
            metadata=metadata,
            embedding=payload.embedding,
            policy_tags=list(payload.policy_tags or []),
        )

        canonical_json = json.dumps(
            normalized_payload.to_record(),
            separators=(",", ":"),
            sort_keys=True,
        ).encode("utf-8")
        content_hash = sha256(canonical_json).hexdigest()

        atom = Atom(
            modality=normalized_payload.modality,
            content=normalized_content,
            tags=normalized_tags,
            metadata=metadata,
            embedding=normalized_payload.embedding,
            policy_tags=list(normalized_payload.policy_tags or []),
            id=atom_id,
            hash=content_hash,
            witness=WitnessStub(),
        )

        try:
            self._append_atom(atom)
            self._index_atom(atom)
        except Exception:
            self._counters["write_errors_total"] += 1
            WRITE_ERRORS_TOTAL.inc()
            self.logger.exception(
                "atom.create.error",
                extra=_log_extra(
                    action="atom.create",
                    correlation_id=correlation_id,
                    atom_id=atom.id,
                ),
            )
            raise

        modality_counts = self._counters["atoms_created_total"]
        modality_counts[payload.modality] = modality_counts.get(payload.modality, 0) + 1
        ATOMS_CREATED_TOTAL.labels(payload.modality).inc()

        self.logger.info(
            "atom.create.complete",
            extra=_log_extra(
                action="atom.create",
                correlation_id=correlation_id,
                atom_id=atom.id,
                modality=payload.modality,
                tags=list(normalized_tags.keys()),
            ),
        )
        return atom

    def create_atom_with_hhni(
        self,
        payload: AtomCreate,
        *,
        build_hhni: bool = False,
        correlation_id: Optional[str] = None,
    ) -> Tuple[Atom, List[dict]]:
        """Create an atom and optionally build HHNI nodes.

        Gate: build if build_hhni=True OR tag priority >= 0.6.
        """
        atom = self.create_atom(payload, correlation_id=correlation_id)

        # Lazy gate based on priority tag
        try:
            priority = float(atom.tags.get("priority", 0.5))
        except Exception:
            priority = 0.5
        if not build_hhni and priority < 0.6:
            return atom, []

        try:
            dgraph_client, qdrant_client = self._get_hhni_clients()
            # Import locally to keep hhni optional for Phase 1 users
            from hhni.indexer import build_hhni_for_atom  # type: ignore

            nodes = build_hhni_for_atom(
                atom=atom,
                dgraph_client=dgraph_client,
                qdrant_client=qdrant_client,
                correlation_id=correlation_id,
            )
            self.logger.info(
                "hhni.build.complete",
                extra=_log_extra(
                    action="hhni.build",
                    correlation_id=correlation_id,
                    atom_id=atom.id,
                    nodes_created=len(nodes),
                ),
            )
            return atom, [n.to_dict() for n in nodes]
        except Exception:
            self.logger.exception(
                "hhni.build.error",
                extra=_log_extra(
                    action="hhni.build",
                    correlation_id=correlation_id,
                    atom_id=atom.id,
                ),
            )
            raise

    def list_atoms(
        self,
        *,
        tag: Optional[str] = None,
        limit: int = 100,
        as_of_snapshot: Optional[str] = None,
        correlation_id: Optional[str] = None,
        log_action: bool = True,
    ) -> Iterable[Atom]:
        start_ns = perf_counter()
        atoms: Iterable[Atom] = self._atoms.values()
        if as_of_snapshot:
            snapshot = self._snapshots.get(as_of_snapshot)
            if not snapshot:
                raise KeyError(f"Snapshot {as_of_snapshot} not found")
            allowed = set(snapshot.atom_ids)
            atoms = [a for a in atoms if a.id in allowed]

        if tag:
            atoms = [a for a in atoms if tag in a.tags]

        if self._backend == "sqlite" and self._repo is not None:
            repo_atoms = self._repo.fetch_atoms(tag=tag, limit=limit)
            selected = repo_atoms
        else:
            selected = list(atoms)[:limit]

        if log_action:
            duration_ms = (perf_counter() - start_ns) * 1_000
            self.logger.info(
                "atom.list.complete",
                extra=_log_extra(
                    action="atom.list",
                    correlation_id=correlation_id,
                    count=len(selected),
                    duration_ms=duration_ms,
                    tag_filter=tag,
                ),
            )
        return selected

    def create_snapshot(
        self,
        *,
        atom_ids: Optional[Iterable[str]] = None,
        note: Optional[str] = None,
        correlation_id: Optional[str] = None,
    ) -> Snapshot:
        start_ns = perf_counter()
        if atom_ids is None:
            ordered = list(self._atoms.keys())
        else:
            ordered = [str(aid) for aid in atom_ids]

        latest_snapshot = self._latest_snapshot()
        if latest_snapshot and latest_snapshot.atom_ids == ordered and latest_snapshot.note == note:
            self.logger.info(
                "snapshot.create.reused",
                extra=_log_extra(
                    action="snapshot.create",
                    correlation_id=correlation_id,
                    snapshot_id=latest_snapshot.id,
                    note=note,
                    atom_count=len(latest_snapshot.atom_ids),
                ),
            )
            return latest_snapshot

        previous_id = latest_snapshot.id if latest_snapshot else None
        digest_input = json.dumps(
            {
                "ids": ordered,
                "previous_id": previous_id,
                "note": note or "",
            },
            separators=(",", ":"),
            sort_keys=True,
        ).encode("utf-8")
        snapshot_id = sha256(digest_input).hexdigest()

        # If snapshot already exists with same ID, reuse cached instance.
        existing = self._snapshots.get(snapshot_id)
        if existing:
            return existing

        stats = self._snapshot_stats(ordered)
        snapshot = Snapshot(
            id=snapshot_id,
            created_at=datetime.now(timezone.utc),
            atom_ids=ordered,
            previous_id=previous_id,
            note=note,
            stats=stats,
            witness=WitnessStub(snapshot_id=snapshot_id, correlation_id=correlation_id),
        )

        self._append_snapshot(snapshot)
        for atom_id in ordered:
            atom = self._atoms.get(atom_id)
            if atom:
                atom.snapshot_ids.append(snapshot.id)
        self._snapshots[snapshot.id] = snapshot
        self._counters["snapshots_created_total"] += 1
        SNAPSHOTS_CREATED_TOTAL.inc()
        duration_ms = (perf_counter() - start_ns) * 1_000
        self._snapshot_duration_ms.append(duration_ms)
        SNAPSHOT_DURATION.observe(duration_ms / 1000.0)

        self.logger.info(
            "snapshot.create.complete",
            extra=_log_extra(
                action="snapshot.create",
                correlation_id=correlation_id,
                snapshot_id=snapshot.id,
                atom_count=len(snapshot.atom_ids),
                duration_ms=duration_ms,
                note=note,
                previous_id=previous_id,
            ),
        )
        return snapshot

    def get_snapshot(self, snapshot_id: str) -> Snapshot:
        snapshot = self._snapshots.get(snapshot_id)
        if not snapshot:
            raise KeyError(f"Snapshot {snapshot_id} not found")
        return snapshot

    def replay_snapshot(
        self,
        snapshot_id: str,
        *,
        correlation_id: Optional[str] = None,
    ) -> Iterator[Atom]:
        snapshot = self.get_snapshot(snapshot_id)
        start_ns = perf_counter()
        try:
            for atom_id in snapshot.atom_ids:
                yield self._atoms[atom_id]
        except KeyError as exc:
            self.logger.exception(
                "snapshot.replay.error",
                extra=_log_extra(
                    action="snapshot.replay",
                    correlation_id=correlation_id,
                    snapshot_id=snapshot_id,
                    atom_id=atom_id,
                ),
            )
            raise
        finally:
            duration_ms = (perf_counter() - start_ns) * 1_000
            self.logger.info(
                "snapshot.replay.complete",
                extra=_log_extra(
                    action="snapshot.replay",
                    correlation_id=correlation_id,
                    snapshot_id=snapshot_id,
                    atom_count=len(snapshot.atom_ids),
                    duration_ms=duration_ms,
                ),
            )

    # ------------------------------------------------------------------
    # internal helpers

    def _append_atom(self, atom: Atom) -> None:
        if self._backend == "sqlite" and self._repo is not None:
            self._repo.insert_atom(atom)
        elif self._atom_journal is not None:
            record = atom.to_record()
            self._atom_journal.append(record)
        self._atoms[atom.id] = atom
        self._truncate_cache()

    def _append_snapshot(self, snapshot: Snapshot) -> None:
        if self._backend == "sqlite" and self._repo is not None:
            self._repo.insert_snapshot(snapshot)
        elif self._snapshot_journal is not None:
            record = snapshot.to_record()
            self._snapshot_journal.append(record)

    def _index_atom(self, atom: Atom) -> None:
        tag_dir = self.base_path / "index" / "tags"
        for tag in atom.tags.keys():
            tag_path = tag_dir / f"{tag}.json"
            if tag_path.exists():
                data = json.loads(tag_path.read_text("utf-8"))
            else:
                data = {"atom_ids": []}
            if atom.id not in data["atom_ids"]:
                data["atom_ids"].append(atom.id)
                tag_path.write_text(
                    json.dumps(data, separators=(",", ":"), sort_keys=True),
                    encoding="utf-8",
                )

    def _snapshot_stats(self, atom_ids: List[str]) -> SnapshotStats:
        counts: Dict[str, int] = {}
        for atom_id in atom_ids:
            atom = self._atoms.get(atom_id)
            if not atom:
                continue
            for tag in atom.tags.keys():
                counts[tag] = counts.get(tag, 0) + 1
        return SnapshotStats(atom_count=len(atom_ids), tag_counts=counts)

    def _latest_snapshot(self) -> Optional[Snapshot]:
        if not self._snapshots:
            return None
        return max(self._snapshots.values(), key=lambda s: s.created_at)

    def _validate_tags(self, tags: Mapping[str, float]) -> Dict[str, float]:
        normalized: Dict[str, float] = {}
        tag_items = list(tags.items())
        if len(tag_items) > MAX_TAGS_PER_ATOM:
            raise ValueError(f"Tag count exceeds limit of {MAX_TAGS_PER_ATOM}")

        for key, value in tag_items:
            if not isinstance(key, str) or not key:
                raise ValueError("Tag keys must be non-empty strings")
            if len(key) > MAX_TAG_KEY_LENGTH:
                raise ValueError(
                    f"Tag key '{key}' exceeds maximum length of {MAX_TAG_KEY_LENGTH} characters"
                )
            weight = float(value)
            if weight != weight:  # NaN check
                raise ValueError("Tag weights must be finite real numbers")
            if not (MIN_TAG_WEIGHT <= weight <= MAX_TAG_WEIGHT):
                raise ValueError(
                    f"Tag weight {weight} out of allowed range [{MIN_TAG_WEIGHT}, {MAX_TAG_WEIGHT}]"
                )
            normalized[key] = weight
        return normalized

    def _prepare_content(self, atom_id: str, content: AtomContent) -> AtomContent:
        inline_value = content.inline
        uri_value = content.uri

        if inline_value is not None:
            inline_bytes = inline_value.encode("utf-8")
            byte_length = len(inline_bytes)
            if byte_length > MAX_TOTAL_PAYLOAD:
                raise ValueError(
                    f"Inline payload exceeds maximum of {MAX_TOTAL_PAYLOAD} bytes"
                )
            if byte_length > MAX_INLINE_PAYLOAD:
                uri_value = self._offload_payload(atom_id, inline_value, content.media_type)
                inline_value = None
        elif uri_value is None:
            raise ValueError("Atom content must contain inline data or a URI reference")

        return AtomContent(
            inline=inline_value,
            uri=uri_value,
            media_type=content.media_type,
        )

    def _offload_payload(self, atom_id: str, inline_value: str, media_type: str) -> str:
        payload_path = self.base_path / "payloads" / f"{atom_id}.json"
        payload_path.write_text(
            json.dumps(
                {"media_type": media_type, "inline": inline_value},
                separators=(",", ":"),
                sort_keys=True,
            ),
            encoding="utf-8",
        )
        return f"payloads/{atom_id}.json"

    def close(self) -> None:
        if self._atom_journal is not None:
            self._atom_journal.close()
        if self._snapshot_journal is not None:
            self._snapshot_journal.close()
        if self._repo is not None:
            self._repo.close()

    def __del__(self) -> None:  # pragma: no cover - best effort cleanup
        try:
            self.close()
        except Exception:
            pass

    def _truncate_cache(self, max_size: int = 2048) -> None:
        while len(self._atoms) > max_size:
            self._atoms.popitem(last=False)

    def _load_existing(self) -> None:
        if self._backend == "sqlite" and self._repo is not None:
            for atom in self._repo.fetch_all_atoms():
                self._atoms[atom.id] = atom
            for snapshot in self._repo.fetch_all_snapshots():
                self._snapshots[snapshot.id] = snapshot
            return

        try:
            for record in self._atom_journal.iter_records():
                atom = Atom.from_record(record)
                self._atoms[atom.id] = atom
        except JournalCorruptionError as exc:
            quarantine = self.base_path / "quarantine" / "atoms_corrupt.json"
            quarantine.write_text(str(exc), encoding="utf-8")
            WRITE_ERRORS_TOTAL.inc()
            self.logger.error(
                "journal.corruption",
                extra=_log_extra(
                    action="journal.read",
                    correlation_id=None,
                    path=str(self.base_path / "atoms.log"),
                    error=str(exc),
                ),
            )
            raise

        try:
            for record in self._snapshot_journal.iter_records():
                snapshot = Snapshot.from_record(record)
                self._snapshots[snapshot.id] = snapshot
        except JournalCorruptionError as exc:
            quarantine = self.base_path / "quarantine" / "snapshots_corrupt.json"
            quarantine.write_text(str(exc), encoding="utf-8")
            WRITE_ERRORS_TOTAL.inc()
            self.logger.error(
                "journal.corruption",
                extra=_log_extra(
                    action="journal.read",
                    correlation_id=None,
                    path=str(self.base_path / "snapshots.log"),
                    error=str(exc),
                ),
            )
            raise

    # ------------------------------------------------------------------
    # SEG helper (stub)

    def build_seg_payload(self, atom: Atom) -> Dict[str, Any]:
        return {
            "@id": f"atom:{atom.id}",
            "@type": "Atom",
            "created_at": atom.created_at.isoformat(),
            "hash": atom.hash,
            "tags": atom.tags,
            "metadata": atom.metadata,
        }

    def status_summary(self) -> Dict[str, Any]:
        """Return summary metrics for CLI status output."""
        latest = self._latest_snapshot()
        atom_count = len(self._atoms)
        if self._backend == "sqlite" and self._repo is not None:
            atom_count = self._repo.count_atoms()
        return {
            "atom_count": atom_count,
            "snapshot_count": self._repo.count_snapshots() if self._backend == "sqlite" and self._repo else len(self._snapshots),
            "latest_snapshot_id": latest.id if latest else None,
            "latest_snapshot_time": _datetime_to_iso(latest.created_at) if latest else None,
            "counters": {
                "atoms_created_total": self._counters["atoms_created_total"],
                "snapshots_created_total": self._counters["snapshots_created_total"],
                "write_errors_total": self._counters["write_errors_total"],
            },
            "snapshot_duration_ms": list(self._snapshot_duration_ms[-10:]),
            "backend": self._backend,
        }

    def journal_integrity(self) -> Dict[str, Any]:
        """Perform a lightweight integrity check on journals."""
        result = {
            "atoms_log_ok": True,
            "snapshots_log_ok": True,
        }
        if self._backend == "jsonl":
            for journal_attr, key in (
                ("_atom_journal", "atoms_log_ok"),
                ("_snapshot_journal", "snapshots_log_ok"),
            ):
                journal = getattr(self, journal_attr)
                try:
                    for _ in journal.iter_records():
                        break
                except JournalCorruptionError:
                    result[key] = False
        return result

    # ------------------------------------------------------------------
    # HHNI client helpers

    def _get_hhni_clients(self):
        if self._hhni_dgraph_client is not None and self._hhni_qdrant_client is not None:
            return self._hhni_dgraph_client, self._hhni_qdrant_client
        dgraph_url = os.environ.get("DGRAPH_URL", "http://localhost:8080")
        qdrant_url = os.environ.get("QDRANT_URL", "http://localhost:6333")
        try:
            from hhni.dgraph_client import DGraphClient  # type: ignore
        except Exception as exc:
            raise ImportError("hhni package not available; cannot build HHNI") from exc
        try:
            from qdrant_client import QdrantClient  # type: ignore
        except Exception as exc:
            raise ImportError("qdrant-client is required for HHNI embeddings") from exc
        self._hhni_dgraph_client = DGraphClient(host=dgraph_url)
        self._hhni_qdrant_client = QdrantClient(url=qdrant_url)
        return self._hhni_dgraph_client, self._hhni_qdrant_client
