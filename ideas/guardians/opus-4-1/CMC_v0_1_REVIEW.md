# Guardian Review: CMC v0.1 Prototype

*Reviewer: Opus 4.1 (Guardian)*  
*Date: 2025-10-18*  
*Status: REQUIRES FIXES*

---

## Executive Summary

The CMC v0.1 prototype successfully demonstrates core deterministic memory functionality. However, **critical safety and production-readiness issues must be addressed** before v0.2 deployment. This review identifies 5 HIGH-priority and 3 MEDIUM-priority issues requiring immediate remediation.

**Verdict: CONDITIONAL PASS** - Proceed to v0.2 only after implementing required fixes.

---

## 1. Critical Safety Issues (HIGH Priority)

### 1.1 Missing Single-Writer Lock ⚠️

**Finding:** `Journal` class has no file locking mechanism.

**Location:** `packages/cmc_service/store_io.py:15-22`

**Risk:** Concurrent writes could corrupt journal, violating determinism invariant.

**Required Fix:**
```python
import fcntl  # Unix/Linux
import msvcrt  # Windows

class Journal:
    def __init__(self, path):
        # ... existing code ...
        self._acquire_exclusive_lock()
    
    def _acquire_exclusive_lock(self):
        if sys.platform == 'win32':
            msvcrt.locking(self._fh.fileno(), msvcrt.LK_NBLCK, 1)
        else:
            fcntl.flock(self._fh.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
```

**Acceptance Criteria:** Demonstrate that second process attempting to write receives `IOError` or blocks.

### 1.2 Incomplete Snapshot ID Determinism ⚠️

**Finding:** Snapshot ID only hashes atom IDs, ignoring `previous_id` and `note`.

**Location:** `packages/cmc_service/memory_store.py:98-105`

**Risk:** Different snapshot chains could produce identical IDs, breaking time-travel guarantees.

**Required Fix:**
```python
digest_input = json.dumps(
    {
        "ids": ordered,
        "previous_id": previous_id,  # Chain snapshots
        "note": note or "",          # Include semantic context
        "created_at": created_at.isoformat() if created_at else None
    },
    separators=(",", ":"),
    sort_keys=True,
).encode("utf-8")
```

**Decision:** Include `previous_id` for chaining, exclude `created_at` for pure determinism.

### 1.3 Missing Payload Size Limits ⚠️

**Finding:** No validation on atom content size.

**Location:** `packages/cmc_service/memory_store.py:45`

**Risk:** OOM attacks via multi-GB payloads.

**Required Fix:**
```python
MAX_INLINE_PAYLOAD = 1_000_000  # 1MB inline
MAX_TOTAL_PAYLOAD = 100_000_000  # 100MB with offload

def create_atom(self, atom_create: AtomCreate) -> Atom:
    content_size = len(atom_create.content.inline or "")
    if content_size > MAX_TOTAL_PAYLOAD:
        raise ValueError(f"Payload exceeds {MAX_TOTAL_PAYLOAD} bytes")
    
    if content_size > MAX_INLINE_PAYLOAD:
        # Offload to payloads/<atom_id>.json
        self._offload_payload(atom_id, atom_create.content)
```

### 1.4 No Tag Hygiene Enforcement ⚠️

**Finding:** Unlimited tags with unbounded weights.

**Location:** `packages/cmc_service/models.py`

**Risk:** Tag explosion could degrade retrieval performance.

**Required Fix:**
```python
MAX_TAGS_PER_ATOM = 20
MAX_TAG_KEY_LENGTH = 50
MIN_TAG_WEIGHT = 0.0
MAX_TAG_WEIGHT = 1.0

def validate_tags(tags: Dict[str, float]):
    if len(tags) > MAX_TAGS_PER_ATOM:
        raise ValueError(f"Exceeds {MAX_TAGS_PER_ATOM} tags")
    for key, weight in tags.items():
        if len(key) > MAX_TAG_KEY_LENGTH:
            raise ValueError(f"Tag key exceeds {MAX_TAG_KEY_LENGTH} chars")
        if not (MIN_TAG_WEIGHT <= weight <= MAX_TAG_WEIGHT):
            raise ValueError(f"Tag weight out of range [{MIN_TAG_WEIGHT}, {MAX_TAG_WEIGHT}]")
```

### 1.5 Insufficient Observability ⚠️

**Finding:** No structured logging or metrics.

**Location:** Throughout codebase

**Risk:** Cannot debug production issues or monitor health.

**Required Fix:**
```python
import structlog
from prometheus_client import Counter, Histogram

logger = structlog.get_logger()
atom_create_counter = Counter('cmc_atoms_created', 'Atoms created', ['modality'])
snapshot_duration = Histogram('cmc_snapshot_duration_seconds', 'Snapshot creation time')

@snapshot_duration.time()
def create_snapshot(self, ...):
    logger.info("snapshot.create.start", atom_count=len(atom_ids))
    # ... existing code ...
    logger.info("snapshot.create.complete", snapshot_id=snapshot.id)
```

---

## 2. Medium Priority Issues

### 2.1 Integrity Algorithm Choice

**Current:** CRC32 for frame checksums.

**Recommendation:** Keep CRC32 for speed, add optional SHA256 for snapshot integrity.

```python
class Snapshot:
    integrity_hash: Optional[str]  # SHA256 of all atom hashes
```

### 2.2 UTC Handling Inconsistency

**Finding:** Mix of `datetime.utcnow()` (deprecated) and timezone-aware datetimes.

**Fix:** Standardize on `datetime.now(timezone.utc)`.

### 2.3 Missing Corruption Quarantine

**Finding:** Corrupted journals cause hard failures.

**Fix:** Add quarantine mode:
```python
def iter_records(self, quarantine_on_error=True):
    try:
        # ... existing code ...
    except JournalCorruptionError as e:
        if quarantine_on_error:
            self._quarantine_corrupted_segment()
            logger.error("journal.corruption.quarantined", error=str(e))
        else:
            raise
```

---

## 3. Acceptance Criteria for v0.2

### Required (Blocking)

- [ ] AC1: Single-writer lock prevents concurrent corruption
- [ ] AC2: Snapshot ID includes `previous_id` for chaining
- [ ] AC3: Payload size limits enforced (1MB inline, 100MB total)
- [ ] AC4: Tag hygiene validated (count, key length, weight range)
- [ ] AC5: Structured JSON logging with correlation IDs
- [ ] AC6: Golden test: identical snapshot IDs across clean runs
- [ ] AC7: Corruption test: quarantine behavior on bad frames

### Recommended (Non-Blocking)

- [ ] RC1: Prometheus metrics for atoms/snapshots/errors
- [ ] RC2: SHA256 integrity hash for snapshots
- [ ] RC3: TypeScript CMC client with type generation
- [ ] RC4: Docker health check endpoint

---

## 4. Implementation Sequence

### Day 1: Safety Critical
1. Implement file locking (1.1)
2. Fix snapshot ID determinism (1.2)
3. Add payload/tag limits (1.3, 1.4)
4. Write golden + corruption tests

### Day 2: Observability & Hygiene
1. Add structured logging (1.5)
2. Implement metrics collection
3. Standardize UTC handling
4. Add payload offload for large content

### Day 3: Integration & Documentation
1. TypeScript client scaffold
2. Update README with limits/policies
3. Run acceptance criteria suite
4. Performance baseline (10K atoms)

---

## 5. Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Journal corruption from concurrent writes | HIGH | CRITICAL | File locking (Day 1) |
| OOM from unbounded payloads | MEDIUM | HIGH | Size limits (Day 1) |
| Non-deterministic snapshot IDs | LOW | HIGH | Include previous_id (Day 1) |
| Tag explosion degrading performance | MEDIUM | MEDIUM | Tag limits (Day 1) |
| Undiagnosable production issues | HIGH | MEDIUM | Structured logging (Day 2) |

---

## 6. Guardian Recommendations

1. **Prioritize Determinism:** The single-writer lock and snapshot ID fix are non-negotiable for v0.2.
2. **Defense in Depth:** Implement both size limits AND rate limiting to prevent resource exhaustion.
3. **Observability First:** Without proper logging/metrics, we're flying blind in production.
4. **Test Coverage Target:** Achieve 90% coverage with emphasis on error paths.
5. **Migration Safety:** Create backup of Phase 1 data before any v0.2 migrations.

---

## 7. Sign-Off Decision

**Guardian Verdict:** **PROCEED WITH CAUTION**

The v0.1 prototype proves the core concept. With the Day 1 safety fixes implemented and verified, we can proceed to v0.2 development. However:

- **Hard Gate:** No v0.2 deployment until ALL required acceptance criteria pass.
- **Soft Gate:** Recommended criteria should be completed within Sprint 1.
- **Review Gate:** Guardian re-review required after fixes before v0.2 blueprint implementation.

---

*Signed: Opus 4.1, Guardian*  
*Authority: Safety & Determinism Oversight*
