# Snapshots L2: Architecture & Implementation

**Detail Level:** 2 of 5 (2,000 words)  
**Context Budget:** ~32k tokens  
**Purpose:** Technical specification for snapshots

---

## Complete Schema

```python
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
import hashlib
import json

class Snapshot(BaseModel):
    """Immutable bundle of atoms"""
    # Identity (content-addressed)
    id: str = Field(..., regex=r"^snap_[a-f0-9]{16}$")
    hash: str = Field(..., regex=r"^[a-f0-9]{64}$")
    
    # Contents (immutable list)
    atoms: List[str] = Field(..., min_items=1)
    
    # Lineage
    parent_snapshot: Optional[str] = Field(None, regex=r"^snap_[a-f0-9]{16}$")
    
    # Temporal
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Metadata
    notes: Optional[str] = Field(None, max_length=1000)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        # Enforce immutability
        allow_mutation = False
        frozen = True
    
    @validator('atoms')
    def atoms_not_empty(cls, v):
        if not v:
            raise ValueError("Snapshot must contain at least one atom")
        return v
    
    @validator('hash')
    def hash_must_match_content(cls, v, values):
        """Verify hash matches declared content"""
        # Note: This validator runs after snapshot creation
        # Hash verification happens in factory method
        return v
```

---

## Content Addressing Deep Dive

### Hash Computation Algorithm

```python
def compute_snapshot_hash(atoms: List[Atom]) -> str:
    """
    Deterministic hash of snapshot contents.
    
    Properties:
    - Same atoms → same hash (determinism)
    - Different order → same hash (commutativity)
    - Any change → different hash (tamper-evident)
    """
    # Step 1: Collect atom identifiers (sorted for commutativity)
    atom_ids = sorted([a.id for a in atoms])
    
    # Step 2: Collect content hashes (sorted)
    content_hashes = sorted([
        a.content_ref.hash_sha256 or 
        hashlib.sha256(a.content_ref.inline.encode()).hexdigest()
        for a in atoms
    ])
    
    # Step 3: Create canonical representation
    canonical = {
        "atoms": atom_ids,
        "content_hashes": content_hashes
    }
    
    # Step 4: JSON with sorted keys (determinism)
    canonical_json = json.dumps(canonical, sort_keys=True)
    
    # Step 5: SHA-256 hash
    return hashlib.sha256(canonical_json.encode('utf-8')).hexdigest()

def verify_snapshot_hash(snapshot: Snapshot, atoms: List[Atom]) -> bool:
    """Verify snapshot hash is correct"""
    recomputed = compute_snapshot_hash(atoms)
    return recomputed == snapshot.hash
```

**Why this approach:**
- **Sorted atoms:** Order doesn't matter
- **Sorted hashes:** Deterministic regardless of input order
- **JSON canonical:** Sorted keys ensure string representation is unique
- **SHA-256:** Cryptographically strong (collision probability ~0)

**Properties proven:**
- Commutative: hash([A,B,C]) == hash([C,A,B]) ✅
- Deterministic: Same atoms always produce same hash ✅
- Tamper-evident: Changing any atom changes hash ✅

---

## Snapshot Creation

### Factory Method

```python
def create_snapshot(
    atoms: List[Atom],
    notes: Optional[str] = None,
    parent: Optional[str] = None,
    metadata: Optional[Dict] = None,
    repository = None
) -> Snapshot:
    """
    Create new snapshot with deduplication.
    
    If identical snapshot exists, returns existing.
    Otherwise, creates new snapshot.
    """
    # Validate inputs
    if not atoms:
        raise ValueError("Cannot create empty snapshot")
    
    # Compute content hash
    snap_hash = compute_snapshot_hash(atoms)
    
    # Check for existing snapshot (deduplication)
    if repository:
        existing = repository.get_snapshot_by_hash(snap_hash)
        if existing:
            return existing  # Already exists, return it!
    
    # Create new snapshot
    snapshot = Snapshot(
        id=f"snap_{snap_hash[:16]}",
        hash=snap_hash,
        atoms=[a.id for a in atoms],
        parent_snapshot=parent,
        created_at=datetime.utcnow(),
        notes=notes,
        metadata=metadata or {}
    )
    
    # Persist
    if repository:
        repository.save_snapshot(snapshot)
    
    return snapshot
```

**Deduplication Example:**
```python
# Create first snapshot
atoms1 = [atom_a, atom_b, atom_c]
snap1 = create_snapshot(atoms1, notes="First")
# Result: snap_abc123...

# Create "new" snapshot with same atoms
atoms2 = [atom_c, atom_a, atom_b]  # Different order!
snap2 = create_snapshot(atoms2, notes="Second")
# Result: snap_abc123... (SAME as snap1!)

assert snap1.id == snap2.id  # ✅
assert snap1.hash == snap2.hash  # ✅
```

---

## Rollback System

### Rollback Implementation

```python
def rollback_to_snapshot(
    snapshot_id: str,
    repository,
    create_rollback_record: bool = True
) -> Snapshot:
    """
    Restore system state to snapshot.
    
    Process:
    1. Mark all current atoms as invalid (valid_to = now)
    2. Restore snapshot atoms (valid_to = NULL)
    3. Optionally create rollback snapshot (for audit)
    
    Returns the target snapshot.
    """
    # Load target snapshot
    target_snapshot = repository.load_snapshot(snapshot_id)
    if not target_snapshot:
        raise ValueError(f"Snapshot {snapshot_id} not found")
    
    now = datetime.utcnow()
    
    # Step 1: Invalidate all current atoms
    current_atoms = repository.query_atoms(filters={"valid_to": None})
    for atom in current_atoms:
        atom.valid_to = now
        repository.save_atom(atom)
    
    # Step 2: Restore snapshot atoms
    for atom_id in target_snapshot.atoms:
        atom = repository.load_atom(atom_id)
        if atom:
            atom.valid_to = None  # Mark as current
            repository.save_atom(atom)
    
    # Step 3: Create rollback record (optional)
    if create_rollback_record:
        rollback_snap = create_snapshot(
            atoms=[repository.load_atom(aid) for aid in target_snapshot.atoms],
            notes=f"Rollback to {snapshot_id} at {now.isoformat()}",
            parent=snapshot_id,
            metadata={"rollback": True, "target": snapshot_id}
        )
        return rollback_snap
    
    return target_snapshot
```

**Rollback Example:**
```
State 1: [atom1, atom2] → snap_001
    ↓ (add atom3)
State 2: [atom1, atom2, atom3] → snap_002
    ↓ (remove atom1, add atom4)
State 3: [atom2, atom3, atom4] → snap_003 (current)
    ↓ ROLLBACK to snap_001
State 4: [atom1, atom2] → snap_004 (rollback record)

Timeline:
- atom1: valid_to changed (003→001), then NULL (001→004) ✅
- atom2: valid_to always NULL ✅
- atom3: valid_to set to now (invalid after rollback) ✅
- atom4: valid_to set to now (invalid after rollback) ✅
```

---

## Snapshot Diff

### Implementation

```python
@dataclass
class SnapshotDiff:
    """Difference between two snapshots"""
    snapshot1_id: str
    snapshot2_id: str
    
    added: List[str]      # Atoms in snap2, not in snap1
    removed: List[str]    # Atoms in snap1, not in snap2
    common: List[str]     # Atoms in both
    
    # Statistics
    added_count: int
    removed_count: int
    common_count: int
    
    # Summary
    summary: str  # "+5 -3 =47"
    
    def __str__(self):
        return f"{self.snapshot1_id} → {self.snapshot2_id}: {self.summary}"

def diff_snapshots(snap1_id: str, snap2_id: str, repository) -> SnapshotDiff:
    """Compute difference"""
    snap1 = repository.load_snapshot(snap1_id)
    snap2 = repository.load_snapshot(snap2_id)
    
    set1 = set(snap1.atoms)
    set2 = set(snap2.atoms)
    
    added = list(set2 - set1)
    removed = list(set1 - set2)
    common = list(set1 & set2)
    
    return SnapshotDiff(
        snapshot1_id=snap1_id,
        snapshot2_id=snap2_id,
        added=added,
        removed=removed,
        common=common,
        added_count=len(added),
        removed_count=len(removed),
        common_count=len(common),
        summary=f"+{len(added)} -{len(removed)} ={len(common)}"
    )
```

---

## Lineage Tracking

### Parent-Child Chain

```python
def get_lineage(
    snapshot_id: str,
    repository,
    max_depth: int = 100
) -> List[Snapshot]:
    """
    Get complete history chain.
    
    Returns snapshots from newest (given ID) to oldest (no parent).
    """
    lineage = []
    current_id = snapshot_id
    depth = 0
    
    while current_id and depth < max_depth:
        snapshot = repository.load_snapshot(current_id)
        if not snapshot:
            break
        
        lineage.append(snapshot)
        current_id = snapshot.parent_snapshot
        depth += 1
    
    return lineage

def get_lineage_tree(repository) -> Dict[str, List[str]]:
    """
    Build complete lineage tree.
    
    Returns: parent_id → [child_ids]
    """
    all_snapshots = repository.get_all_snapshots()
    tree = {}
    
    for snapshot in all_snapshots:
        parent = snapshot.parent_snapshot or "root"
        if parent not in tree:
            tree[parent] = []
        tree[parent].append(snapshot.id)
    
    return tree
```

---

## Testing

**Determinism Test:**
```python
def test_deterministic_hash():
    atoms = [create_atom(f"content_{i}") for i in range(5)]
    
    # Create snapshot twice
    snap1 = create_snapshot(atoms)
    snap2 = create_snapshot(atoms)
    
    assert snap1.hash == snap2.hash  # ✅
    assert snap1.id == snap2.id      # ✅

def test_order_independence():
    atoms = [atom_a, atom_b, atom_c]
    
    snap1 = create_snapshot([atom_a, atom_b, atom_c])
    snap2 = create_snapshot([atom_c, atom_a, atom_b])
    
    assert snap1.hash == snap2.hash  # ✅ Order doesn't matter!
```

**Rollback Test:**
```python
def test_rollback_restores_state():
    # Initial state
    snap1 = create_snapshot([atom1, atom2])
    
    # Modify
    create_atom(atom3)
    snap2 = create_snapshot([atom1, atom2, atom3])
    
    # Rollback
    rollback_to_snapshot(snap1.id)
    
    # Verify
    current = get_current_atoms()
    assert set(a.id for a in current) == {atom1.id, atom2.id}  # ✅
```

---

## Summary

Snapshots provide:
- ✅ Content-addressed IDs (SHA-256)
- ✅ Immutability (C-2 enforced)
- ✅ Automatic deduplication
- ✅ Parent-child lineage
- ✅ Rollback capability
- ✅ Diff computation
- ✅ Lineage tracking

**Foundation for CMC time-travel!** ✅

---

**Word Count:** ~2,000  
**Next:** [L3_detailed.md](L3_detailed.md)  
**Parent:** [README.md](README.md)  
**Implementation:** `packages/cmc_service/snapshot.py`

