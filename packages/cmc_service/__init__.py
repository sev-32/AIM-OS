"""CMC Service prototype package (Phase 1).

This package provides the minimal viable memory implementation used during
Phase 1 of AIM-OS development. It currently targets file-backed, deterministic
storage of memory atoms and replayable snapshots.
"""

from .memory_store import MemoryStore
from .models import Atom, AtomCreate, Snapshot, WitnessStub
from .logging_utils import configure_logging
from .bitemporal_queries import BitemporalQueryEngine
from .repository import AtomRepository, SQLiteConfig

configure_logging()

__all__ = [
    "MemoryStore",
    "Atom",
    "AtomCreate",
    "Snapshot",
    "WitnessStub",
    "configure_logging",
    "BitemporalQueryEngine",
    "AtomRepository",
    "SQLiteConfig",
]
