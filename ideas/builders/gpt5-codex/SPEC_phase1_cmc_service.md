# Phase 1 Specification — CMC Service v0.1

*Contributor: GPT-5 Codex (Builder)*  
*Date: 2025-10-18*  
*Workspace: `ideas/builders/gpt5-codex/`*

---

## 1. Goal Statement
Build the **Minimal Viable Memory** layer of AIM-OS: a deterministic service that ingests text payloads as *atoms*, persists them with canonical metadata, and emits replayable *snapshots* suitable for downstream APOE/VIF/SEG integration.

---

## 2. Functional Requirements

### FR1. Atom Ingestion
- **FR1.1** A client can create an atom by providing: modality, content (inline text or external URI), optional tags (key → weight), metadata (free-form dict), and optional embedding vector.
- **FR1.2** The service assigns a UUIDv7 ID, computes a canonical SHA256 hash of content+metadata, and records create timestamp in RFC3339.
- **FR1.3** Ingest must be deterministic: identical payload → identical hash and stored object.
- **FR1.4** Atom write operations append to a commit log and optionally store payload in `payloads/<atom_id>.json` when inline text length > configurable threshold (default 2 KB).

### FR2. Atom Retrieval
- **FR2.1** List atoms endpoint returns atoms ordered by create time descending.
- **FR2.2** Query filters: `tag`, `since` (timestamp), `limit` (default 100), `as_of` (snapshot id for time travel).
- **FR2.3** Retrieval must be side-effect free and deterministic.

### FR3. Snapshot Management
- **FR3.1** A client can request snapshot creation referencing either explicit atom IDs or implicit “all since last snapshot”.
- **FR3.2** Snapshot ID = SHA256 of ordered atom ID list + previous snapshot ID + note.
- **FR3.3** Snapshot manifest stores: id, created_at, previous_id, atom_ids, stats (count, tag histogram), note.
- **FR3.4** Snapshot replay API returns atom records in deterministic order (creation sequence).

### FR4. Evidence Hooks
- **FR4.1** Every atom and snapshot persists a `witness_stub` containing placeholder fields for VIF integration (model/tool IDs, correlation id, uncertainty band).
- **FR4.2** Provide helper `build_seg_payload` returning dictionary for future SEG ingestion (not stored automatically).

### FR5. Observability & Health
- **FR5.1** Emit structured logs for ingest, snapshot creation, replay (JSON: ts, action, duration_ms, identifiers).
- **FR5.2** Provide metrics counters and histograms (in-process registry, optional Prometheus exposition).
- **FR5.3** Provide `cmc status` CLI command to print summary (atom count, last snapshot, log integrity check).

---

## 3. Non-Functional Requirements

### Determinism & Reliability
- **NFR1** All state changes funnel through a single writer lock (file-based). Concurrency beyond one process explicitly unsupported in v0.1.
- **NFR2** Log records use canonical JSON (sorted keys, UTF-8). Replay must produce identical atoms/snapshots bit-for-bit.
- **NFR3** Detect log corruption via length prefix + SHA256; corrupted segments moved to `quarantine/` with failure metadata.

### Performance
- **NFR4** Target throughput: ≥ 50 atoms/sec on developer laptop (text payload ≤ 5 KB).
- **NFR5** Snapshot creation: ≤ 250 ms for 10k atoms (append-only manifest computation).
- **NFR6** Retrieval latency: ≤ 50 ms for 100 atoms in memory; ≤ 150 ms hitting disk cache.

### Storage Footprint
- **NFR7** Keep log overhead minimal: store embeddings inline only if vector length ≤ 1024; otherwise write to payload file.
- **NFR8** Provide configuration for base path and log rotation (default rotate at 100 MB per file).

### Safety & Policy
- **NFR9** Reject payloads flagged with `policy_tags` requiring HITL (future) by writing to `quarantine/` and returning 409 with reason.
- **NFR10** Enforce tag cardinality ≤ 64, weight clamp to [0,1], maximum payload size 256 KB.

### Testing & CI
- **NFR11** Provide unit tests covering ingest, replay, determinism, corruption handling.
- **NFR12** Provide golden integration test ingesting sample corpus (subset of `analysis/raw`) and verifying snapshot hash matches expected fixture.

---

## 4. Interfaces & Schema

### 4.1 Python Types
```python
@dataclass
class AtomCreate:
    modality: Literal['text']
    content: AtomContent           # inline text or URI reference
    tags: Mapping[str, float] = field(default_factory=dict)
    metadata: Mapping[str, Any] = field(default_factory=dict)
    embedding: Optional[List[float]] = None

@dataclass
class Atom(AtomCreate):
    id: str
    created_at: datetime
    hash: str
    witness: WitnessStub

@dataclass
class Snapshot:
    id: str
    created_at: datetime
    previous_id: Optional[str]
    atom_ids: List[str]
    stats: SnapshotStats
    note: Optional[str]
    witness: WitnessStub
```

### 4.2 CLI Commands
- `cmc atoms:create --file path --tag source:plan`
- `cmc atoms:list --tag role:guardian --limit 20`
- `cmc snapshots:create --note "Initial import"`
- `cmc snapshots:replay --id SNAPSHOT_ID --out replay.json`
- `cmc status`

### 4.3 Config
```
[storage]
base_path = "./data/cmc"
rotate_bytes = 104857600
payload_inline_threshold = 2048

[limits]
max_payload_bytes = 262144
max_tags = 64
```

---

## 5. Implementation Plan (Iterations)

1. **Bootstrap (Day 1)**
   - Scaffold `packages/cmc_service/` structure.
   - Implement `MemoryStore` with in-memory backend (for tests).
   - Write unit tests for create/list/snapshot/replay (in-memory).

2. **Persistence Layer (Day 2)**
   - Implement append-only JSONL storage with length+hash framing.
   - Add file-locking and rotation.
   - Extend tests to disk-backed store (tmpdir fixture).

3. **CLI & Metrics (Day 3)**
   - Build CLI using `typer` or `click`.
   - Integrate metrics registry & `status` command.
   - Add logging (structlog or standard logging with JSON formatter).

4. **Integration Demo (Day 4)**
   - Script to ingest sample atoms from `analysis/raw/A Total System of Memory.txt` slices.
   - Create snapshot, replay, compare manifest hash.
   - Document results in `logs/phase1_demo.md` with witness stubs.

5. **Polish & Hand-off (Day 5)**
   - Write developer README (`packages/cmc_service/README.md`).
   - Update `ideas/REGISTRY.md` status to `[EXPLORATION]`.
   - Coordinate with Opus for review, gather feedback.

---

## 6. Acceptance Criteria Checklist
- [ ] AC1 Atom ingest deterministic: repeated run yields identical JSON record & hash.
- [ ] AC2 Snapshot creation produces stable ID across runs.
- [ ] AC3 Replay of snapshot regenerates atoms identical to original input (deep equality).
- [ ] AC4 Quarantine triggers on corrupted log entry (integration test).
- [ ] AC5 Metrics counters increment as expected (unit assertions).
- [ ] AC6 Golden demo executed; results documented.

---

## 7. Dependencies & Coordination
- Coordinate with **Opus 4.1** for policy/quarantine thresholds.
- Align with **Gemini 2.5** on determinism assumptions for future proofs.
- Provide interface notes to **o3pro** for future SEG handoff.
- Keep **Braden** informed (human) via `BRADEN_STATUS_UPDATE.md` once prototype ready.

---

## 8. Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Hash drift due to ordering inconsistencies | Replay invalidates snapshots | Canonical JSON serialisation; regression tests |
| Log corruption from abrupt termination | Data loss | Length+hash framing, on-startup integrity check |
| Performance degradation with large atom sets | Slow retrieval | LRU cache for recent atoms; future indexing enhancements |
| Scope creep into HHNI/DVNS | Delays | Enforce phase boundary—only minimal tag index |

---

*End of specification — GPT-5 Codex*
