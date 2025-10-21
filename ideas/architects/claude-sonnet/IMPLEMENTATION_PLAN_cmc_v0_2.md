# Implementation Plan: CMC Service v0.2

*Author: GPT-5 Codex (Builder)*  
*Date: 2025-10-18*  
*Status: Draft*

---

## Scope & Invariants
- **SQLite primary store** replaces JSONL for atoms/snapshots (Invariant: CMC determinism)
- **HHNI Levels 0-2** (corpus → section → paragraph) populated on ingest with lazy gates (Invariant: HHNI)
- **Witness/VIF stubs** enriched to capture SQLite row IDs and HHNI node references (Invariant: VIF/SEG)
- **Observability** retains Prometheus counters with fine-grained buckets; CI smoke ingest exercises metrics

Out of scope: token-level HHNI, APOE orchestration, full SEG graph emission.

---

## Phase Breakdown

### Phase 0 – Foundations (1 day)
- Refactor existing file I/O into repository abstraction (`packages/cmc_service/repo.py`).
- Scaffold SQLite schema (`atoms`, `snapshots`, `tags`, `witnesses`).
- Implement migration utility: `python -m cmc_service.migrations.jsonl_to_sqlite --base-path ...`.
- Update tests to run against temporary SQLite database (pytest fixture).

### Phase 1 – Atom Pipeline (2 days)
- Modify `MemoryStore` to write atoms to SQLite within transactions.
- Maintain append-only JSONL as audit trail (optional, behind feature flag `CMC_KEEP_JOURNAL`).
- Update tag index logic to query SQLite.
- Ensure `create_atom` writes to SQLite first, then journal/quarantine for fallback.
- Extend tests: atom creation, querying, tag filtering in SQLite context.

### Phase 2 – Snapshot Layer (1 day)
- Persist snapshots in SQLite with deterministic hash and `previous_id` chain.
- Store `atom_snapshot` mapping table for quick replay queries.
- Update `status_summary` to pull counts from SQLite.
- Adjust metrics to reflect SQLite transactions (latency measurement).

### Phase 3 – HHNI L0–L2 Integration (2 days)
- Create `hhni/pipeline.py` orchestrator that:
  1. Derives sections from file path or metadata.
  2. Splits content into paragraphs (reuse existing parsers).
  3. Writes nodes to DGraph and vectors to Qdrant using existing clients.
- Persist HHNI node references in SQLite table `hhni_nodes` (atom_id, level, node_id).
- Add gating logic: enforce priority threshold, add manual override flag (`force=True`).
- Tests: integration tests mocking DGraph/Qdrant verifying nodes stored, gating respected.

### Phase 4 – VIF/SEG Shims (1 day)
- Extend `WitnessStub` to include SQLite snapshot row ID and HHNI node count.
- Provide `MemoryStore.emit_witness()` returning JSON structure ready for SEG ingestion.
- Add CLI command `cmc witness:emit SNAPSHOT_ID` to dump witness payload.
- Tests: ensure witness output references stored artifacts.

### Phase 5 – Observability & CI (0.5 day)
- Add `scripts/ci_smoke_ingest.py` to ingest sample atoms, create snapshot, and dump metrics.
- Integrate script into CI (GitHub Actions placeholder) to assert counters > 0.
- Document metrics bucket ranges, update README.

### Phase 6 – Documentation & Handoff (0.5 day)
- Update `README.md` with SQLite deployment notes, migration instructions.
- Add ADR summarizing migration decision and fallback plan.
- Prepare handoff brief for Opus + Gemini.

---

## Dependencies & Risks
- Requires `sqlite3` availability (Python stdlib) and ensures thread-safe access via `check_same_thread=False` only when necessary.
- DGraph/Qdrant containers must be running for HHNI tests; use pytest markers to skip when not available.
- Migration must be idempotent; provide backup instructions before running on real data.

---

## Success Criteria
- `pytest` suite passes with SQLite-backed store.
- `cmc status` reflects SQLite counts; `cmc metrics:dump` shows non-zero counters post smoke ingest.
- HHNI L0–L2 nodes stored with deterministic IDs and accessible via CLI.
- Witness export consumed by Opus for guard review.
- Gate review (Opus) and validation (Gemini) sign off.
