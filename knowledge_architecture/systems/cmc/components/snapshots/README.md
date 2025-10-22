# Snapshots - Immutable Memory Bundles

**Component of:** CMC  
**Type:** Core Component  
**Purpose:** Content-addressed, immutable atom bundles for time-travel  
**Status:** ✅ Fully Implemented (75% of CMC)

---

## 🎯 **Quick Context (100 words)**

Snapshots are immutable bundles of atoms - like Git commits for memory. Each snapshot has content-addressed ID (SHA-256 hash of contents), creation timestamp, parent reference, and atom list. Once created, never modified. Enables rollback, replay, audit. Deduplication automatic (same atoms = same hash). Snapshots form lineage chain (parent→child). Every atom belongs to exactly one snapshot. Critical for determinism, time-travel queries, and verifiable replay. Think: database transaction + Git commit + Merkle tree.

**[More detail below ↓]**

---

## 📊 **Context Budget Guide**

**4k Context:** Read this README  
**8k Context:** Read [L1_overview.md](L1_overview.md) (500w)  
**32k Context:** Read [L2_architecture.md](L2_architecture.md) (2kw)  
**200k+ Context:** Read L3-L5 + operations/

---

## 📦 **Snapshot Structure**

**Identity:**
- `id` - Content-addressed (snap_{hash[:16]})
- `hash` - SHA-256 of canonical representation

**Contents:**
- `atoms` - List of atom IDs in this bundle

**Lineage:**
- `parent_snapshot` - Previous snapshot (Git-like chain)

**Metadata:**
- `created_at` - Transaction timestamp
- `notes` - Human description
- `metadata` - Extensible dict

---

## 🔧 **Key Operations**

**Create:**
```python
snapshot = create_snapshot(
    atoms=[atom1, atom2, atom3],
    notes="Ingested user conversation",
    parent=current_snapshot_id
)
```

**Rollback:**
```python
rollback_to_snapshot(snapshot_id)
# Marks current atoms invalid
# Restores snapshot atoms as current
```

**Diff:**
```python
diff = diff_snapshots(snap1_id, snap2_id)
# Returns: added, removed, common atoms
```

---

## 🔗 **Relationships**

**Snapshots used by:**
- Atoms (every atom has snapshot_id)
- VIF (replay requires snapshot)
- CMC Write Pipeline (creates snapshots)
- Rollback operations (restore state)

**Snapshots enable:**
- Time-travel (rollback to any point)
- Audit (full history preserved)
- Replay (deterministic reproduction)
- Deduplication (content addressing)

**Governed by:**
- Design Constraint C-2 (immutability)
- Memory Invariant (reversible mapping)

---

## 📚 **Detail Levels**

**L0 (This File):** Navigation + 100w summary  
**L1:** [L1_overview.md](L1_overview.md) - 500w architecture  
**L2:** [L2_architecture.md](L2_architecture.md) - 2kw implementation  
**L3-L5:** Deep dives (to be created)

**Sub-components:**
- [operations/create/](operations/create/) - Creation logic
- [operations/rollback/](operations/rollback/) - Rollback system
- [operations/diff/](operations/diff/) - Comparison
- [content_addressing/](content_addressing/) - Hash computation
- [lineage/](lineage/) - Parent-child chains

---

## 🎯 **Key Concepts**

**Immutability:** Never modified after creation (C-2)  
**Content Addressing:** Same atoms → same hash  
**Lineage Chain:** Parent→child relationships (Git-like)  
**Determinism:** Reproducible, verifiable  
**Deduplication:** Automatic via hashing

---

**Parent:** [../../README.md](../../README.md) (CMC System)  
**Siblings:** [../atoms/](../atoms/), [../storage/](../storage/)  
**Implementation:** `packages/cmc_service/snapshot.py`  
**Tests:** Passing (determinism validated)

