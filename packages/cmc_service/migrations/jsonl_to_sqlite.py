#!/usr/bin/env python
"""
Migration utility: JSONL → SQLite

Converts Phase 1 JSONL-backed atoms and snapshots to SQLite schema.
Verifies deterministic hash integrity during migration.
"""

from __future__ import annotations

import argparse
import json
import logging
import shutil
from pathlib import Path
from typing import Iterator

from ..models import Atom, Snapshot
from ..repository import AtomRepository, SQLiteConfig
from ..store_io import Journal

logger = logging.getLogger(__name__)


def iter_jsonl_atoms(journal_path: Path) -> Iterator[Atom]:
    """Iterate atoms from JSONL journal."""
    journal = Journal(journal_path)
    try:
        for record in journal.iter_records():
            yield Atom.from_record(record)
    finally:
        journal.close()


def iter_jsonl_snapshots(journal_path: Path) -> Iterator[Snapshot]:
    """Iterate snapshots from JSONL journal."""
    journal = Journal(journal_path)
    try:
        for record in journal.iter_records():
            yield Snapshot.from_record(record)
    finally:
        journal.close()


def migrate(
    *,
    jsonl_base: Path,
    sqlite_path: Path,
    backup: bool = True,
    verify: bool = True,
) -> None:
    """
    Migrate JSONL data to SQLite.

    Args:
        jsonl_base: Directory containing atoms.log and snapshots.log
        sqlite_path: Target SQLite database file
        backup: Create timestamped backup of source JSONL files
        verify: Verify all hashes match after migration
    """
    atoms_log = jsonl_base / "atoms.log"
    snapshots_log = jsonl_base / "snapshots.log"

    if not atoms_log.exists():
        raise FileNotFoundError(f"Atoms journal not found: {atoms_log}")
    if not snapshots_log.exists():
        raise FileNotFoundError(f"Snapshots journal not found: {snapshots_log}")

    # Backup if requested
    if backup:
        backup_dir = jsonl_base / f"backup_{int(__import__('time').time())}"
        backup_dir.mkdir(exist_ok=True)
        shutil.copy2(atoms_log, backup_dir / "atoms.log")
        shutil.copy2(snapshots_log, backup_dir / "snapshots.log")
        logger.info(f"Backed up JSONL files to {backup_dir}")

    # Initialize SQLite repository
    config = SQLiteConfig(path=sqlite_path, enable_wal=True)
    repo = AtomRepository(config)

    # Migrate atoms
    atom_count = 0
    atom_hashes = {}
    logger.info("Migrating atoms...")
    for atom in iter_jsonl_atoms(atoms_log):
        repo.insert_atom(atom)
        atom_hashes[atom.id] = atom.hash
        atom_count += 1
        if atom_count % 100 == 0:
            logger.info(f"Migrated {atom_count} atoms...")

    logger.info(f"Migrated {atom_count} atoms total")

    # Migrate snapshots
    snapshot_count = 0
    logger.info("Migrating snapshots...")
    for snapshot in iter_jsonl_snapshots(snapshots_log):
        repo.insert_snapshot(snapshot)
        snapshot_count += 1
        if snapshot_count % 10 == 0:
            logger.info(f"Migrated {snapshot_count} snapshots...")

    logger.info(f"Migrated {snapshot_count} snapshots total")

    # Verify
    if verify:
        logger.info("Verifying hash integrity...")
        fetched = repo.fetch_atoms(limit=10000)
        for atom in fetched:
            expected_hash = atom_hashes.get(atom.id)
            if expected_hash and atom.hash != expected_hash:
                raise ValueError(
                    f"Hash mismatch for atom {atom.id}: "
                    f"expected {expected_hash}, got {atom.hash}"
                )
        logger.info(f"Verified {len(fetched)} atoms - all hashes match ✓")

    repo.close()
    logger.info("Migration complete!")


def main() -> None:
    parser = argparse.ArgumentParser(description="Migrate JSONL to SQLite")
    parser.add_argument(
        "--base-path",
        type=Path,
        default=Path("./packages/cmc_service/data"),
        help="Directory containing atoms.log and snapshots.log",
    )
    parser.add_argument(
        "--sqlite-path",
        type=Path,
        default=None,
        help="Target SQLite database (default: BASE_PATH/cmc.db)",
    )
    parser.add_argument(
        "--no-backup",
        action="store_true",
        help="Skip backing up source JSONL files",
    )
    parser.add_argument(
        "--no-verify",
        action="store_true",
        help="Skip hash verification after migration",
    )

    args = parser.parse_args()
    
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
    )

    jsonl_base = args.base_path
    sqlite_path = args.sqlite_path or (jsonl_base / "cmc.db")

    migrate(
        jsonl_base=jsonl_base,
        sqlite_path=sqlite_path,
        backup=not args.no_backup,
        verify=not args.no_verify,
    )


if __name__ == "__main__":
    main()

