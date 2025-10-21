#!/usr/bin/env python3
"""Bitemporal migration utility for BTSM nodes and edges."""

from __future__ import annotations

import argparse
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import List

from schemas.mpd import KPIReference, MPDNode
from schemas.edge import BitemporalEdge

from ..repository import AtomRepository, SQLiteConfig
from ...seg import write_witness  # type: ignore

logger = logging.getLogger(__name__)


def _seed_nodes(now: datetime) -> List[MPDNode]:
    return [
        MPDNode(
            mpd_id="aimos.cmc",
            type="service",
            purpose="Context Memory Core: deterministic atom and snapshot storage.",
            capabilities=[
                "atom-ingest",
                "snapshot-commit",
                "seg-witness",
            ],
            interfaces=[
                "python:packages.cmc_service.memory_store.MemoryStore",
                "cli:packages.cmc_service.cli",
            ],
            manager_of=["aimos.cmc.sqlite", "aimos.cmc.seg"],
            depends_on=["aimos.seg"],
            policy_pack_ids=["policy.cmc.default"],
            budgets=["cpu:medium", "storage:managed"],
            owners=["GPT-5 Codex", "o3pro-ai"],
            kpis=[
                KPIReference(name="MIGE_VisionFit_target", target=0.9),
                KPIReference(name="MIGE_LineageCompleteness_target", target=0.95),
            ],
            lifecycle="active",
            witness="seg://mige/migration_v1",
            links=[
                "analysis/PLAN.md#4.1",
                "Documentation/MEMORY_TO_IDEA_INTEGRATION_GUIDE.md",
            ],
            max_dependency_degree=8,
            tt_start=now,
            vt_start=now,
        ),
        MPDNode(
            mpd_id="aimos.cmc.sqlite",
            type="storage",
            purpose="SQLite persistence for atoms, snapshots, and BTSM nodes.",
            capabilities=["sqlite", "migration"],
            interfaces=[
                "sqlite:packages/cmc_service/repository.py",
            ],
            manager_of=[],
            depends_on=["aimos.cmc"],
            policy_pack_ids=["policy.db.backup"],
            budgets=["storage:ssd"],
            owners=["GPT-5 Codex"],
            kpis=[
                KPIReference(name="MIGE_ReplaySuccess_target", target=0.99),
            ],
            lifecycle="active",
            witness="seg://mige/migration_v1",
            links=[
                "packages/cmc_service/migrations/bitemporal_upgrade.py",
            ],
            max_dependency_degree=4,
            tt_start=now,
            vt_start=now,
        ),
        MPDNode(
            mpd_id="aimos.cmc.seg",
            type="evidence",
            purpose="SEG witness export for CMC mutations and migrations.",
            capabilities=["jsonl-export", "witness-emission"],
            interfaces=[
                "python:packages.seg.witness.write_witness",
            ],
            manager_of=[],
            depends_on=["aimos.cmc"],
            policy_pack_ids=["policy.seg.default"],
            budgets=["storage:log"],
            owners=["Opus 4.1"],
            kpis=[
                KPIReference(name="MIGE_BlastRadiusFalseNegatives_target", target=0.0),
            ],
            lifecycle="active",
            witness="seg://mige/migration_v1",
            links=[
                "SYSTEM_MAP_TOTAL.md",
            ],
            max_dependency_degree=2,
            tt_start=now,
            vt_start=now,
        ),
    ]


def _seed_edges(now: datetime) -> List[BitemporalEdge]:
    return [
        BitemporalEdge(
            source_id="aimos.cmc",
            target_id="aimos.cmc.sqlite",
            relation="manager_of",
            policy_pack_ids=["policy.cmc.default"],
            tt_start=now,
            vt_start=now,
        ),
        BitemporalEdge(
            source_id="aimos.cmc",
            target_id="aimos.cmc.seg",
            relation="manager_of",
            policy_pack_ids=["policy.cmc.default"],
            tt_start=now,
            vt_start=now,
        ),
        BitemporalEdge(
            source_id="aimos.cmc.sqlite",
            target_id="aimos.cmc",
            relation="depends_on",
            policy_pack_ids=["policy.db.backup"],
            tt_start=now,
            vt_start=now,
        ),
        BitemporalEdge(
            source_id="aimos.cmc.seg",
            target_id="aimos.cmc",
            relation="depends_on",
            policy_pack_ids=["policy.seg.default"],
            tt_start=now,
            vt_start=now,
        ),
    ]


def migrate(*, base_path: Path, seg_dir: Path | None = None) -> None:
    db_path = base_path / "cmc.db"
    config = SQLiteConfig(path=db_path)
    repo = AtomRepository(config)
    now = datetime.now(timezone.utc)

    nodes = _seed_nodes(now)
    edges = _seed_edges(now)
    repo.upsert_mpd_nodes(nodes)
    repo.upsert_mpd_edges(edges)
    repo.close()

    witness_payload = {
        "event": "bitemporal_upgrade",
        "version": 1,
        "database": str(db_path),
        "node_ids": [node.mpd_id for node in nodes],
        "edge_count": len(edges),
        "tt_start": now.isoformat(),
    }
    write_witness(witness_payload, seg_dir=seg_dir)
    logger.info("Bitemporal migration complete for %s", db_path)


def main() -> None:
    parser = argparse.ArgumentParser(description="Apply BTSM bitemporal migration.")
    parser.add_argument(
        "--base-path",
        type=Path,
        default=Path("./packages/cmc_service/data"),
        help="Path to the CMC data directory containing cmc.db.",
    )
    parser.add_argument(
        "--seg-dir",
        type=Path,
        default=None,
        help="Optional override directory for SEG witness output.",
    )
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    migrate(base_path=args.base_path, seg_dir=args.seg_dir)


if __name__ == "__main__":
    main()
