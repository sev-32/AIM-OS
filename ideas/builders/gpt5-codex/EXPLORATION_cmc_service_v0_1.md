# Exploration Log: CMC Service v0.1

*Contributor: GPT-5 Codex (Builder)*  
*Date: 2025-10-18*  
*Workspace: `ideas/builders/gpt5-codex/`*

---

## 1. Mission & Scope (Phase 1 – Minimal Viable Memory)

**Objective:** Deliver a deterministic, file-backed prototype that ingests context payloads as *atoms*, maintains an append-only commit log, and materialises *snapshots* that can be replayed bit-for-bit. This unlocks ingestion of the existing knowledge corpus and produces the substrate required by APOE, VIF, and SEG.

**Out of scope for v0.1 (explicitly deferred):** HHNI multi-level indexing beyond paragraph granularity, DVNS refinement, distributed writers, policy-aware geometry, full SEG API, encryption/PII redaction, multi-modal payloads.

---

## 2. Architectural Slice (Component View)

```
┌──────────────────────────────┐
│  Ingest API (Sync)           │
│  - /atoms (POST)             │
│  - /atoms (GET, filters)     │
│  - /snapshots (POST, GET)    │
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│  Write Pipeline (Deterministic) │
│  1. Normalise input             │
│  2. Enrich metadata             │
│  3. Compute hashes & QS stub    │
│  4. Persist to append log       │
│  5. Emit event to observers     │
└──────────────┬────────────────┘
               │
               ▼
┌──────────────────────────────┐
│  Storage Substrate           │
│  - atoms.jsonl (append-only) │
│  - snapshots.jsonl           │
│  - payloads/ (content blobs) │
│  - index/ (tag lookup cache) │
└──────────────┬────────────────┘
               │
               ▼
┌──────────────────────────────┐
│  Snapshot Engine             │
│  - Deterministic digest      │
│  - Previous pointer          │
│  - Atom membership vector    │
└──────────────┬────────────────┘
               │
               ▼
┌──────────────────────────────┐
│  Evidence Hooks (Stubs)      │
│  - Witness payload builder   │
│  - SEG node template         │
│  - Observability signals     │
└──────────────────────────────┘
```

All writes flow through the pipeline, guaranteeing single-writer semantics. The prototype runs in-process (library + optional CLI) to minimise moving parts while maintaining deterministic behaviour.

---

## 3. Data Model (v0.1)

### 3.1 Atom
```
Atom {
  id: UUIDv7,
  created_at: RFC3339,
  modality: Literal["text"],
  content_ref: {
    inline?: str,
    uri?: str,
    media_type: str
  },
  tags: Dict[str, float],        # tag → weight (0..1)
  metadata: Dict[str, Any],      # e.g. source path, contributor
  embedding: Optional[List[float]],
  hash: str,                     # sha256(content+metadata)
  witness: WitnessStub,          # minimal fields for VIF
  snapshot_ids: List[str]        # populated lazily
}
```

### 3.2 Snapshot
```
Snapshot {
  id: str,                       # hash of ordered atom ids + previous snapshot id
  created_at: RFC3339,
  note: Optional[str],
  atom_ids: List[str],           # deterministic ordering (commit order)
  previous_id: Optional[str],
  stats: {
    atom_count: int,
    tag_counts: Dict[str, int]
  },
  hash: str,                     # digest of manifest to support replay
  witness: WitnessStub
}
```

### 3.3 Witness (Stub)
```
WitnessStub {
  model_id: str?,
  tool_ids: List[str],
  snapshot_id: str,
  correlation_id: str,
  uncertainty: {
    band: Literal["green", "yellow", "red"],
    ece: float?
  }
}
```

> **Determinism note:** hashes are computed with canonical JSON serialisation (sorted keys, UTF-8) to guarantee reproducibility.

---

## 4. Interfaces (Library + Optional HTTP facade)

### 4.1 Python Library (`cmc_service`) – canonical API

```python
class MemoryStore:
    def create_atom(self, payload: AtomCreate) -> Atom: ...
    def list_atoms(self, *, tag=None, limit=100, as_of=None) -> Iterable[Atom]: ...
    def create_snapshot(self, note: str | None = None,
                        atom_ids: Sequence[str] | None = None) -> Snapshot: ...
    def get_snapshot(self, snapshot_id: str) -> Snapshot: ...
    def replay_snapshot(self, snapshot_id: str) -> Iterable[Atom]: ...
```

### 4.2 CLI (optional, built atop library)

```
$ cmc atoms:create --modality text --file docs/example.md --tag source:plan
$ cmc snapshots:create --note "Plan import"
$ cmc snapshots:replay SNAPSHOT_ID
```

### 4.3 REST Facade (stretch goal if time permits)
- Implemented with FastAPI or Flask wrapper.
- Mirrors library methods.
- Emits JSON with deterministic key ordering.

---

## 5. Storage Strategy

- **Base directory:** configurable (default `./data/cmc_store`).
- **atoms.jsonl:** append-only log (one canonical JSON per atom).
- **snapshots.jsonl:** append-only log capturing manifest.
- **payloads/<atom_id>.json:** optional full payload dump for large bodies.
- **index/tags/<tag>.idx:** lightweight cache enabling tag-based lookups (JSON list of atom ids).
- **Checksums:** each log entry preceded by 32-bit length + SHA256 for corruption detection.

> Rationale: line-delimited JSON keeps the prototype tooling-friendly while offering deterministic playback. Future versions can migrate to SQLite or columnar storage without breaking the interface.

---

## 6. Determinism & Gates

- **Single writer:** all mutations funnel through `MemoryStore` instance; multi-process locking (file lock) enforced via `fcntl`/`msvcrt` wrappers.
- **Size gates:** reject payloads > 256kB (configurable) and tag counts > 64.
- **Tag hygiene:** normalise tags to lowercase, strip whitespace, clamp weights to [0,1].
- **Replay gate:** snapshot creation recomputes manifest hash and compares with stored value; mismatch triggers quarantine directory.

---

## 7. Observability & Evidence (Phase 1)

- **Metrics (printed / optional Prometheus stub):**
  - `cmc_atoms_total`
  - `cmc_snapshot_total`
  - `cmc_write_latency_ms`
- **Logs:** structured JSON (timestamp, action, atom_id, snapshot_id, duration_ms).
- **Witness:** minimal stub reused by VIF when upstream services mature. Stored alongside atoms/snapshots.
- **SEG Stub:** helper `build_seg_payload(atom | snapshot)` returning dictionary for future ingestion.

---

## 8. Safety & Policy Hooks

- Intake supports optional `policy_tags` (e.g., `pii:suspect`) flagged for Guardian review.
- File-locking prevents concurrent writers from corrupting the append log.
- Quarantine folder collects failed writes along with failure metadata for manual inspection.
- TODO (future): integrate configurable redaction hooks before persisting content.

---

## 9. Validation Strategy

1. **Unit tests** (`tests/test_memory_store.py`):
   - Create atom → list atoms → snapshot → replay.
   - Deterministic snapshot hash given identical inputs.
   - Tag filters return expected subset.
2. **Golden run** (`examples/phase1_demo.py`):
   - Ingest selection from `analysis/raw/`.
   - Generate snapshot.
   - Replay snapshot and diff vs. input manifest.
3. **Hash reproducibility:** run golden twice, compare snapshot IDs.
4. **Failure handling:** simulate corrupted log entry → ensure quarantine triggers.

---

## 10. Open Questions

- How aggressively should we cache atoms in memory vs. reading from disk per request? (v0.1: load-on-demand with small LRU cache.)
- Should embeddings be stored inline or as separate payload files to keep logs lean? (v0.1: inline optional list, caution for large vectors.)
- How soon do we introduce HHNI hierarchy beyond simple tag index? (v0.1: keep simple; design interface so future indices plug in.)
- Should snapshot manifest include derived stats (e.g., unique sources, size) or compute lazily? (v0.1: store counts for quick UI display.)

---

## 11. Next Actions (tracked in TODOs)

1. ✅ Draft exploration log (this document).
2. ✅ Generate formal requirements & acceptance criteria (`SPEC_phase1_cmc_service.md`).
3. ✅ Scaffold `packages/cmc_service/` with library, CLI, tests.
4. ✅ Run golden demo ingesting a handful of atoms (analysis excerpts).
5. ✅ Publish results + witness stub back into workspace; validation plan documented (`VALIDATION_phase1_cmc_service.md`).

---

*End of exploration log — GPT-5 Codex*
