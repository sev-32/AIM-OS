from __future__ import annotations

import json
import sqlite3
from collections import deque
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Set, Tuple

from schemas.mpd import KPIReference, MPDNode  # type: ignore
from schemas.edge import BitemporalEdge  # type: ignore

from .models import Atom, AtomContent, Snapshot, SnapshotStats, WitnessStub


@dataclass
class SQLiteConfig:
    path: Path
    enable_wal: bool = True


class AtomRepository:
    """SQLite-backed repository for atoms and snapshots with ACID guarantees."""

    def __init__(self, config: SQLiteConfig):
        self._config = config
        self._conn = sqlite3.connect(str(config.path), check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        if config.enable_wal:
            self._conn.execute("PRAGMA journal_mode=WAL")
        self._ensure_schema()

    def _ensure_schema(self) -> None:
        cur = self._conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS atoms (
                id TEXT PRIMARY KEY,
                modality TEXT NOT NULL,
                inline TEXT,
                uri TEXT,
                media_type TEXT NOT NULL,
                hash TEXT NOT NULL,
                created_at TEXT NOT NULL,
                metadata TEXT,
                witness TEXT,
                embedding BLOB
            )
            """
        )
        cur.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_atoms_modality ON atoms(modality)
            """
        )
        cur.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_atoms_created ON atoms(created_at)
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS tags (
                atom_id TEXT NOT NULL,
                tag_key TEXT NOT NULL,
                weight REAL NOT NULL,
                PRIMARY KEY(atom_id, tag_key),
                FOREIGN KEY(atom_id) REFERENCES atoms(id)
            )
            """
        )
        cur.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_tags_key ON tags(tag_key)
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS snapshots (
                id TEXT PRIMARY KEY,
                created_at TEXT NOT NULL,
                previous_id TEXT,
                note TEXT,
                stats TEXT,
                witness TEXT
            )
            """
        )
        cur.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_snapshots_created ON snapshots(created_at)
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS snapshot_atoms (
                snapshot_id TEXT NOT NULL,
                atom_id TEXT NOT NULL,
                position INTEGER NOT NULL,
                PRIMARY KEY(snapshot_id, position),
                FOREIGN KEY(snapshot_id) REFERENCES snapshots(id),
                FOREIGN KEY(atom_id) REFERENCES atoms(id)
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS mpd_nodes (
                mpd_id TEXT PRIMARY KEY,
                type TEXT NOT NULL,
                purpose TEXT NOT NULL,
                capabilities TEXT,
                interfaces TEXT,
                manager_of TEXT,
                depends_on TEXT,
                policy_pack_ids TEXT,
                budgets TEXT,
                owners TEXT,
                kpis TEXT,
                lifecycle TEXT,
                witness TEXT,
                links TEXT,
                max_dependency_degree INTEGER NOT NULL DEFAULT 0,
                tt_start TEXT NOT NULL,
                tt_end TEXT,
                vt_start TEXT NOT NULL,
                vt_end TEXT
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS mpd_edges (
                edge_id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_id TEXT NOT NULL,
                target_id TEXT NOT NULL,
                relation TEXT NOT NULL,
                policy_pack_ids TEXT,
                tt_start TEXT NOT NULL,
                tt_end TEXT,
                vt_start TEXT NOT NULL,
                vt_end TEXT,
                UNIQUE(source_id, target_id, relation, tt_start),
                FOREIGN KEY(source_id) REFERENCES mpd_nodes(mpd_id),
                FOREIGN KEY(target_id) REFERENCES mpd_nodes(mpd_id)
            )
            """
        )
        cur.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_mpd_nodes_tt_start ON mpd_nodes(tt_start)
            """
        )
        cur.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_mpd_edges_tt_start ON mpd_edges(tt_start)
            """
        )
        self._conn.commit()
        self._seed_core_btsm()

    def insert_atom(self, atom: Atom) -> None:
        """Insert an atom with all metadata, tags, and witness information."""
        cur = self._conn.cursor()
        cur.execute(
            """
            INSERT INTO atoms (
                id, modality, inline, uri, media_type, hash, created_at,
                metadata, witness, embedding
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                atom.id,
                atom.modality,
                atom.content.inline,
                atom.content.uri,
                atom.content.media_type,
                atom.hash,
                atom.created_at.isoformat(),
                json.dumps(atom.metadata) if atom.metadata else None,
                json.dumps(atom.witness.to_dict()),
                json.dumps(atom.embedding) if atom.embedding else None,
            ),
        )
        for tag, weight in atom.tags.items():
            cur.execute(
                """
                INSERT INTO tags (atom_id, tag_key, weight)
                VALUES (?, ?, ?)
                """,
                (atom.id, tag, weight),
            )
        self._conn.commit()

    def insert_snapshot(self, snapshot: Snapshot) -> None:
        """Insert a snapshot with stats, witness, and atom ordering."""
        cur = self._conn.cursor()
        cur.execute(
            """
            INSERT INTO snapshots (id, created_at, previous_id, note, stats, witness)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                snapshot.id,
                snapshot.created_at.isoformat(),
                snapshot.previous_id,
                snapshot.note,
                json.dumps(snapshot.stats.to_dict()),
                json.dumps(snapshot.witness.to_dict()),
            ),
        )
        for position, atom_id in enumerate(snapshot.atom_ids):
            cur.execute(
                """
                INSERT INTO snapshot_atoms (snapshot_id, atom_id, position)
                VALUES (?, ?, ?)
                """,
                (snapshot.id, atom_id, position),
            )
        self._conn.commit()

    def fetch_atoms(
        self, *, tag: Optional[str] = None, limit: int = 100, offset: int = 0
    ) -> List[Atom]:
        """Fetch atoms with optional tag filtering and pagination."""
        if tag:
            query = """
                SELECT DISTINCT a.*
                FROM atoms a
                JOIN tags t ON a.id = t.atom_id
                WHERE t.tag_key = ?
                ORDER BY a.created_at DESC
                LIMIT ? OFFSET ?
            """
            params = (tag, limit, offset)
        else:
            query = """
                SELECT * FROM atoms
                ORDER BY created_at DESC
                LIMIT ? OFFSET ?
            """
            params = (limit, offset)

        cur = self._conn.cursor()
        rows = cur.execute(query, params).fetchall()
        return [self._row_to_atom(row) for row in rows]

    def fetch_atom_tags(self, atom_id: str) -> Dict[str, float]:
        """Fetch all tags for a given atom."""
        cur = self._conn.cursor()
        rows = cur.execute(
            "SELECT tag_key, weight FROM tags WHERE atom_id = ?", (atom_id,)
        ).fetchall()
        return {row["tag_key"]: row["weight"] for row in rows}

    def fetch_snapshot(self, snapshot_id: str) -> Optional[Snapshot]:
        """Fetch a snapshot by ID with all associated atoms."""
        cur = self._conn.cursor()
        row = cur.execute(
            "SELECT * FROM snapshots WHERE id = ?", (snapshot_id,)
        ).fetchone()
        if not row:
            return None

        atom_rows = cur.execute(
            """
            SELECT atom_id FROM snapshot_atoms
            WHERE snapshot_id = ?
            ORDER BY position
            """,
            (snapshot_id,),
        ).fetchall()
        atom_ids = [r["atom_id"] for r in atom_rows]

        return Snapshot(
            id=row["id"],
            created_at=datetime.fromisoformat(row["created_at"]),
            atom_ids=atom_ids,
            previous_id=row["previous_id"],
            note=row["note"],
            stats=SnapshotStats.from_dict(json.loads(row["stats"])) if row["stats"] else SnapshotStats(atom_count=len(atom_ids)),
            witness=WitnessStub.from_dict(json.loads(row["witness"])) if row["witness"] else WitnessStub(),
        )

    def fetch_all_atoms(self) -> List[Atom]:
        cur = self._conn.cursor()
        rows = cur.execute("SELECT * FROM atoms ORDER BY created_at ASC").fetchall()
        return [self._row_to_atom(row) for row in rows]

    def fetch_all_snapshots(self) -> List[Snapshot]:
        cur = self._conn.cursor()
        rows = cur.execute("SELECT * FROM snapshots ORDER BY created_at ASC").fetchall()
        snapshots: List[Snapshot] = []
        for row in rows:
            atom_rows = cur.execute(
                """
                SELECT atom_id FROM snapshot_atoms
                WHERE snapshot_id = ?
                ORDER BY position
                """,
                (row["id"],),
            ).fetchall()
            atom_ids = [r["atom_id"] for r in atom_rows]
            snapshots.append(
                Snapshot(
                    id=row["id"],
                    created_at=datetime.fromisoformat(row["created_at"]),
                    atom_ids=atom_ids,
                    previous_id=row["previous_id"],
                    note=row["note"],
                    stats=SnapshotStats.from_dict(json.loads(row["stats"])) if row["stats"] else SnapshotStats(atom_count=len(atom_ids)),
                    witness=WitnessStub.from_dict(json.loads(row["witness"])) if row["witness"] else WitnessStub(),
                )
            )
        return snapshots

    def count_atoms(self) -> int:
        """Return total atom count."""
        cur = self._conn.cursor()
        return cur.execute("SELECT COUNT(*) FROM atoms").fetchone()[0]

    def count_snapshots(self) -> int:
        cur = self._conn.cursor()
        return cur.execute("SELECT COUNT(*) FROM snapshots").fetchone()[0]

    # ------------------------------------------------------------------
    # BTSM helpers

    def upsert_mpd_nodes(self, nodes: Iterable[MPDNode]) -> None:
        cur = self._conn.cursor()
        for node in nodes:
            cur.execute(
                """
                INSERT INTO mpd_nodes (
                    mpd_id, type, purpose, capabilities, interfaces, manager_of,
                    depends_on, policy_pack_ids, budgets, owners, kpis, lifecycle,
                    witness, links, max_dependency_degree, tt_start, tt_end,
                    vt_start, vt_end
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(mpd_id) DO UPDATE SET
                    type=excluded.type,
                    purpose=excluded.purpose,
                    capabilities=excluded.capabilities,
                    interfaces=excluded.interfaces,
                    manager_of=excluded.manager_of,
                    depends_on=excluded.depends_on,
                    policy_pack_ids=excluded.policy_pack_ids,
                    budgets=excluded.budgets,
                    owners=excluded.owners,
                    kpis=excluded.kpis,
                    lifecycle=excluded.lifecycle,
                    witness=excluded.witness,
                    links=excluded.links,
                    max_dependency_degree=excluded.max_dependency_degree,
                    tt_start=excluded.tt_start,
                    tt_end=excluded.tt_end,
                    vt_start=excluded.vt_start,
                    vt_end=excluded.vt_end
                """,
                (
                    node.mpd_id,
                    node.type,
                    node.purpose,
                    json.dumps(node.capabilities),
                    json.dumps(node.interfaces),
                    json.dumps(node.manager_of),
                    json.dumps(node.depends_on),
                    json.dumps(node.policy_pack_ids),
                    json.dumps(node.budgets),
                    json.dumps(node.owners),
                    json.dumps([kpi.model_dump() for kpi in node.kpis]),
                    node.lifecycle,
                    node.witness,
                    json.dumps(node.links),
                    node.max_dependency_degree,
                    node.tt_start.isoformat(),
                    node.tt_end.isoformat() if node.tt_end else None,
                    node.vt_start.isoformat(),
                    node.vt_end.isoformat() if node.vt_end else None,
                ),
            )
        self._conn.commit()

    def upsert_mpd_edges(self, edges: Iterable[BitemporalEdge]) -> None:
        cur = self._conn.cursor()
        for edge in edges:
            policies, max_degree = self._normalize_edge_policies(cur, edge)
            edge.policy_pack_ids = policies
            self._enforce_dependency_degree(cur, edge, max_degree)
            cur.execute(
                """
                INSERT INTO mpd_edges (
                    source_id, target_id, relation, policy_pack_ids,
                    tt_start, tt_end, vt_start, vt_end
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(source_id, target_id, relation, tt_start) DO UPDATE SET
                    policy_pack_ids=excluded.policy_pack_ids,
                    tt_end=excluded.tt_end,
                    vt_start=excluded.vt_start,
                    vt_end=excluded.vt_end
                """,
                (
                    edge.source_id,
                    edge.target_id,
                    edge.relation,
                    json.dumps(policies),
                    edge.tt_start.isoformat(),
                    edge.tt_end.isoformat() if edge.tt_end else None,
                    edge.vt_start.isoformat(),
                    edge.vt_end.isoformat() if edge.vt_end else None,
                ),
            )
        self._conn.commit()

    def _row_to_mpd_node(self, row) -> MPDNode:
        """Convert SQLite row to MPDNode (helper for bitemporal queries)."""
        kpi_payload = json.loads(row["kpis"]) if row["kpis"] else []
        return MPDNode(
            mpd_id=row["mpd_id"],
            type=row["type"],
            purpose=row["purpose"],
            capabilities=json.loads(row["capabilities"]) if row["capabilities"] else [],
            interfaces=json.loads(row["interfaces"]) if row["interfaces"] else [],
            manager_of=json.loads(row["manager_of"]) if row["manager_of"] else [],
            depends_on=json.loads(row["depends_on"]) if row["depends_on"] else [],
            policy_pack_ids=json.loads(row["policy_pack_ids"]) if row["policy_pack_ids"] else [],
            budgets=json.loads(row["budgets"]) if row["budgets"] else [],
            owners=json.loads(row["owners"]) if row["owners"] else [],
            kpis=[KPIReference(**item) for item in kpi_payload],
            lifecycle=row["lifecycle"],
            witness=row["witness"],
            links=json.loads(row["links"]) if row["links"] else [],
            max_dependency_degree=row["max_dependency_degree"],
            tt_start=datetime.fromisoformat(row["tt_start"]),
            tt_end=datetime.fromisoformat(row["tt_end"]) if row["tt_end"] else None,
            vt_start=datetime.fromisoformat(row["vt_start"]),
            vt_end=datetime.fromisoformat(row["vt_end"]) if row["vt_end"] else None,
        )
    
    def _row_to_mpd_edge(self, row) -> BitemporalEdge:
        """Convert SQLite row to BitemporalEdge (helper for bitemporal queries)."""
        return BitemporalEdge(
            source_id=row["source_id"],
            target_id=row["target_id"],
            relation=row["relation"],
            policy_pack_ids=json.loads(row["policy_pack_ids"]) if row["policy_pack_ids"] else [],
            tt_start=datetime.fromisoformat(row["tt_start"]),
            tt_end=datetime.fromisoformat(row["tt_end"]) if row["tt_end"] else None,
            vt_start=datetime.fromisoformat(row["vt_start"]),
            vt_end=datetime.fromisoformat(row["vt_end"]) if row["vt_end"] else None,
        )
    
    def _insert_mpd_node_raw(self, cur, node: MPDNode) -> None:
        """Insert MPD node without upsert logic (for testing historical versions)."""
        import json
        cur.execute(
            """
            INSERT INTO mpd_nodes (
                mpd_id, type, purpose, capabilities, interfaces,
                manager_of, depends_on, policy_pack_ids, budgets, owners,
                kpis, lifecycle, witness, links, max_dependency_degree,
                tt_start, tt_end, vt_start, vt_end
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                node.mpd_id,
                node.type,
                node.purpose,
                json.dumps(node.capabilities),
                json.dumps(node.interfaces),
                json.dumps(node.manager_of),
                json.dumps(node.depends_on),
                json.dumps(node.policy_pack_ids),
                json.dumps(node.budgets),
                json.dumps(node.owners),
                json.dumps([kpi.model_dump() for kpi in node.kpis]),
                node.lifecycle,
                node.witness,
                json.dumps(node.links),
                node.max_dependency_degree,
                node.tt_start.isoformat(),
                node.tt_end.isoformat() if node.tt_end else None,
                node.vt_start.isoformat(),
                node.vt_end.isoformat() if node.vt_end else None,
            ),
        )
    
    def fetch_mpd_nodes(
        self,
        *,
        policy_pack_ids: Optional[Iterable[str]] = None,
        policy_match: str = "all",
        lifecycle: Optional[Iterable[str]] = None,
    ) -> List[MPDNode]:
        cur = self._conn.cursor()
        rows = cur.execute("SELECT * FROM mpd_nodes ORDER BY mpd_id ASC").fetchall()
        nodes: List[MPDNode] = []
        policy_filter = {str(value) for value in (policy_pack_ids or []) if str(value).strip()}
        lifecycle_filter = {str(value) for value in (lifecycle or []) if str(value).strip()}
        for row in rows:
            if lifecycle_filter and (row["lifecycle"] or "") not in lifecycle_filter:
                continue
            node_policy_ids = json.loads(row["policy_pack_ids"]) if row["policy_pack_ids"] else []
            if policy_filter and not self._policy_filter_matches(node_policy_ids, policy_filter, policy_match):
                continue
            nodes.append(self._row_to_mpd_node(row))
        return nodes

    def fetch_mpd_edges(
        self,
        *,
        relation: Optional[str] = None,
        source_id: Optional[str] = None,
        target_id: Optional[str] = None,
        policy_pack_ids: Optional[Iterable[str]] = None,
        policy_match: str = "all",
    ) -> List[BitemporalEdge]:
        cur = self._conn.cursor()
        query = (
            "SELECT source_id, target_id, relation, policy_pack_ids, tt_start, tt_end, vt_start, vt_end "
            "FROM mpd_edges"
        )
        clauses = []
        params: List[object] = []
        if relation:
            clauses.append("relation = ?")
            params.append(relation)
        if source_id:
            clauses.append("source_id = ?")
            params.append(source_id)
        if target_id:
            clauses.append("target_id = ?")
            params.append(target_id)
        if clauses:
            query += " WHERE " + " AND ".join(clauses)
        query += " ORDER BY source_id, target_id, relation"
        rows = cur.execute(query, params).fetchall()
        edges: List[BitemporalEdge] = []
        policy_filter = {str(value) for value in (policy_pack_ids or []) if str(value).strip()}
        for row in rows:
            row_policy_ids = json.loads(row["policy_pack_ids"]) if row["policy_pack_ids"] else []
            if policy_filter and not self._policy_filter_matches(row_policy_ids, policy_filter, policy_match):
                continue
            edges.append(self._row_to_mpd_edge(row))
        return edges

    def _policy_filter_matches(self, policies: Iterable[str], required: Set[str], mode: str) -> bool:
        if not required:
            return True
        policy_set = {str(item) for item in policies if str(item).strip()}
        match_mode = mode if mode in {"all", "any"} else "all"
        if match_mode == "any":
            return any(pid in policy_set for pid in required)
        return required.issubset(policy_set)


    def calculate_blast_radius(
        self,
        root_ids: Iterable[str],
        *,
        relation_types: Optional[Iterable[str]] = None,
        required_policy_pack_ids: Optional[Iterable[str]] = None,
    ) -> Dict[str, object]:
        roots = [str(root).strip() for root in root_ids if str(root).strip()]
        if not roots:
            raise ValueError("At least one root_id is required to compute blast radius.")
    
        nodes = self.fetch_mpd_nodes()
        edges = self.fetch_mpd_edges()
        node_index: Dict[str, MPDNode] = {node.mpd_id: node for node in nodes}
    
        allowed_relations = {str(rel).strip() for rel in (relation_types or []) if str(rel).strip()}
        adjacency: Dict[str, List[BitemporalEdge]] = {}
        for edge in edges:
            if allowed_relations and edge.relation not in allowed_relations:
                continue
            adjacency.setdefault(edge.source_id, []).append(edge)
    
        required_policies: List[str] = []
        for policy in required_policy_pack_ids or []:
            normalized = str(policy).strip()
            if normalized and normalized not in required_policies:
                required_policies.append(normalized)
        if not required_policies:
            for root_id in roots:
                node = node_index.get(root_id)
                if not node:
                    continue
                for policy in node.policy_pack_ids:
                    if policy not in required_policies:
                        required_policies.append(policy)
    
        violations: List[Dict[str, object]] = []
        impacted_nodes: Set[str] = set()
        traversed_edges: List[Dict[str, object]] = []
    
        checked_roots: List[str] = []
        required_policy_set = set(required_policies)
        for root_id in roots:
            node = node_index.get(root_id)
            if node is None:
                violations.append(
                    {
                        "kind": "missing_node",
                        "subject_id": root_id,
                        "message": f"Root node {root_id} not found.",
                        "policy_pack_ids": [],
                    }
                )
                continue
            checked_roots.append(root_id)
            impacted_nodes.add(root_id)
            if required_policy_set and not required_policy_set.issubset(set(node.policy_pack_ids)):
                violations.append(
                    {
                        "kind": "node_policy",
                        "subject_id": root_id,
                        "message": "Root node missing required policy packs.",
                        "policy_pack_ids": list(node.policy_pack_ids),
                    }
                )
    
        queue: deque[str] = deque(checked_roots)
        visited: Set[str] = set()
        while queue:
            current = queue.popleft()
            if current in visited:
                continue
            visited.add(current)
            for edge in adjacency.get(current, []):
                traversed_edges.append(
                    {
                        "source_id": edge.source_id,
                        "target_id": edge.target_id,
                        "relation": edge.relation,
                        "policy_pack_ids": list(edge.policy_pack_ids),
                    }
                )
                if required_policy_set and not required_policy_set.issubset(set(edge.policy_pack_ids)):
                    violations.append(
                        {
                            "kind": "edge_policy",
                            "subject_id": f"{edge.source_id}->{edge.target_id}",
                            "message": "Edge missing required policy packs.",
                            "policy_pack_ids": list(edge.policy_pack_ids),
                        }
                    )
                target_node = node_index.get(edge.target_id)
                if target_node is None:
                    violations.append(
                        {
                            "kind": "missing_node",
                            "subject_id": edge.target_id,
                            "message": f"Target node {edge.target_id} not found.",
                            "policy_pack_ids": [],
                        }
                    )
                    continue
                impacted_nodes.add(target_node.mpd_id)
                if required_policy_set and not required_policy_set.issubset(set(target_node.policy_pack_ids)):
                    violations.append(
                        {
                            "kind": "node_policy",
                            "subject_id": target_node.mpd_id,
                            "message": "Target node missing required policy packs.",
                            "policy_pack_ids": list(target_node.policy_pack_ids),
                        }
                    )
                if target_node.mpd_id not in visited:
                    queue.append(target_node.mpd_id)
    
        return {
            "root_ids": roots,
            "required_policy_pack_ids": required_policies,
            "impacted_nodes": sorted(impacted_nodes),
            "traversed_edges": traversed_edges,
            "violations": violations,
            "compliant": not violations,
        }
    
    def _normalize_edge_policies(self, cursor: sqlite3.Cursor, edge: BitemporalEdge) -> Tuple[List[str], Optional[int]]:
        policies = [str(pid).strip() for pid in edge.policy_pack_ids if str(pid).strip()]
        if edge.relation != "depends_on":
            return policies, None
        row = cursor.execute(
            "SELECT policy_pack_ids, max_dependency_degree FROM mpd_nodes WHERE mpd_id = ?", (edge.source_id,)
        ).fetchone()
        inherited: List[str] = []
        max_degree: Optional[int] = None
        if row:
            if row["policy_pack_ids"]:
                inherited_payload = json.loads(row["policy_pack_ids"])
                if isinstance(inherited_payload, list):
                    inherited = [str(pid).strip() for pid in inherited_payload if str(pid).strip()]
            max_degree = row["max_dependency_degree"] if row["max_dependency_degree"] is not None else None
        for policy_id in inherited:
            if policy_id not in policies:
                policies.append(policy_id)
        if not policies:
            raise ValueError(f"depends_on edge {edge.source_id}->{edge.target_id} missing policy inheritance")
        return policies, max_degree

    def _enforce_dependency_degree(self, cursor: sqlite3.Cursor, edge: BitemporalEdge, max_degree: Optional[int]) -> None:
        if edge.relation != "depends_on" or max_degree is None:
            return
        try:
            limit = int(max_degree)
        except (TypeError, ValueError):
            return
        if limit <= 0:
            return
        exists = cursor.execute(
            """
            SELECT 1 FROM mpd_edges
            WHERE source_id = ? AND target_id = ? AND relation = ? AND (vt_end IS NULL)
            """,
            (edge.source_id, edge.target_id, edge.relation),
        ).fetchone()
        if exists:
            return
        current = cursor.execute(
            """
            SELECT COUNT(*) FROM mpd_edges
            WHERE source_id = ? AND relation = ? AND (vt_end IS NULL)
            """,
            (edge.source_id, "depends_on"),
        ).fetchone()[0]
        if current >= limit:
            raise ValueError(
                f"depends_on edge {edge.source_id}->{edge.target_id} exceeds max_dependency_degree {limit}"
            )

    def _row_to_atom(self, row: sqlite3.Row) -> Atom:
        """Convert a SQLite row to an Atom instance."""
        tags = self.fetch_atom_tags(row["id"])
        return Atom(
            id=row["id"],
            modality=row["modality"],
            content=AtomContent(
                inline=row["inline"],
                uri=row["uri"],
                media_type=row["media_type"],
            ),
            hash=row["hash"],
            created_at=datetime.fromisoformat(row["created_at"]),
            tags=tags,
            metadata=json.loads(row["metadata"]) if row["metadata"] else {},
            witness=WitnessStub.from_dict(json.loads(row["witness"])) if row["witness"] else WitnessStub(),
            embedding=json.loads(row["embedding"]) if row["embedding"] else None,
        )

    def close(self) -> None:
        """Close database connection."""
        self._conn.close()

    def _seed_core_btsm(self) -> None:
        """Ensure core AIMOS BTSM nodes and edges exist for blast-radius defaults."""
        baseline = datetime(2025, 1, 1, tzinfo=timezone.utc)
        iso_start = baseline.isoformat()
        cur = self._conn.cursor()
        existing_nodes = {
            row["mpd_id"]
            for row in cur.execute(
                "SELECT mpd_id FROM mpd_nodes WHERE mpd_id IN (?, ?, ?)",
                ("aimos.cmc", "aimos.cmc.sqlite", "aimos.cmc.seg"),
            )
        }
        node_payloads = []
        if "aimos.cmc" not in existing_nodes:
            node_payloads.append(
                (
                    "aimos.cmc",
                    "platform",
                    "Context Memory Core orchestrates atomic knowledge ingestion and replay.",
                    json.dumps(["memory-ingest", "snapshot-index"]),
                    json.dumps(["plans/cmc_ingest.acl", "plans/cmc_snapshot.acl"]),
                    json.dumps(["aimos.cmc.sqlite", "aimos.cmc.seg"]),
                    json.dumps([]),
                    json.dumps(["policy.cmc.default", "policy.mige.default"]),
                    json.dumps(["operations:core"]),
                    json.dumps(["GPT-5 Codex", "o3pro-ai"]),
                    json.dumps([KPIReference(name="CMC_Snapshot_SLA_target", target=0.99).model_dump()]),
                    "active",
                    None,
                    json.dumps(["docs/cmc.md"]),
                    6,
                    iso_start,
                    None,
                    iso_start,
                    None,
                )
            )
        if "aimos.cmc.sqlite" not in existing_nodes:
            node_payloads.append(
                (
                    "aimos.cmc.sqlite",
                    "service",
                    "Durable SQLite persistence for Context Memory Core.",
                    json.dumps(["bitemporal-storage", "wal-checkpoint"]),
                    json.dumps(["plans/cmc_backup.acl"]),
                    json.dumps([]),
                    json.dumps(["aimos.cmc"]),
                    json.dumps(["policy.cmc.default", "policy.mige.default", "policy.db.backup"]),
                    json.dumps(["operations:core"]),
                    json.dumps(["GPT-5 Codex", "o3pro-ai"]),
                    json.dumps([]),
                    "active",
                    None,
                    json.dumps(["docs/cmc_storage.md"]),
                    3,
                    iso_start,
                    None,
                    iso_start,
                    None,
                )
            )
        if "aimos.cmc.seg" not in existing_nodes:
            node_payloads.append(
                (
                    "aimos.cmc.seg",
                    "service",
                    "Shared Evidence Graph interface for provenance and replay.",
                    json.dumps(["seg-witness", "lineage-api"]),
                    json.dumps(["plans/seg_export.acl"]),
                    json.dumps([]),
                    json.dumps(["aimos.cmc"]),
                    json.dumps(["policy.cmc.default", "policy.mige.default", "policy.seg.default"]),
                    json.dumps(["governance:medium"]),
                    json.dumps(["GPT-5 Codex", "o3pro-ai"]),
                    json.dumps([]),
                    "active",
                    None,
                    json.dumps(["docs/seg.md"]),
                    4,
                    iso_start,
                    None,
                    iso_start,
                    None,
                )
            )
        if node_payloads:
            cur.executemany(
                """
                INSERT INTO mpd_nodes (
                    mpd_id, type, purpose, capabilities, interfaces, manager_of,
                    depends_on, policy_pack_ids, budgets, owners, kpis, lifecycle,
                    witness, links, max_dependency_degree, tt_start, tt_end, vt_start, vt_end
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                node_payloads,
            )
        edge_payloads = [
            (
                "aimos.cmc",
                "aimos.cmc.sqlite",
                "manager_of",
                json.dumps(["policy.cmc.default", "policy.mige.default"]),
                iso_start,
                None,
                iso_start,
                None,
            ),
            (
                "aimos.cmc",
                "aimos.cmc.seg",
                "manager_of",
                json.dumps(["policy.cmc.default", "policy.mige.default"]),
                iso_start,
                None,
                iso_start,
                None,
            ),
            (
                "aimos.cmc.sqlite",
                "aimos.cmc",
                "depends_on",
                json.dumps(["policy.cmc.default", "policy.mige.default", "policy.db.backup"]),
                iso_start,
                None,
                iso_start,
                None,
            ),
            (
                "aimos.cmc.seg",
                "aimos.cmc",
                "depends_on",
                json.dumps(["policy.cmc.default", "policy.mige.default", "policy.seg.default"]),
                iso_start,
                None,
                iso_start,
                None,
            ),
        ]
        for payload in edge_payloads:
            cur.execute(
                """
                INSERT OR IGNORE INTO mpd_edges (
                    source_id, target_id, relation, policy_pack_ids,
                    tt_start, tt_end, vt_start, vt_end
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                payload,
            )
        self._conn.commit()
