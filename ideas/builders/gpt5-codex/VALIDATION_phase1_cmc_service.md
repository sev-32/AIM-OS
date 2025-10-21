# Validation Plan — CMC Service v0.1 (Phase 1)

*Contributor: GPT-5 Codex*  
*Date: 2025-10-18*

---

## 1. Scope
Phase 1 aims to prove that the Context Memory Core can ingest text
payloads as atoms, persist them deterministically, and emit replayable
snapshots with basic metadata. Validation covers correctness,
determinism, and developer experience.

## 2. Test Matrix

| Area | Goal | Evidence | Status |
|------|------|----------|--------|
| Atom ingest | Atoms stored with canonical hash and metadata | `packages/cmc_service/tests/test_memory_store.py::test_create_and_list_atom` | ✅ |
| Snapshot replay | Snapshots include atom IDs and can be replayed | `test_snapshot_roundtrip` | ✅ |
| Determinism | Re-creating snapshot without changes yields same ID | `test_snapshot_deterministic` | ✅ |
| CLI workflow | Developer can ingest file and create snapshot | `packages/cmc_service/examples/phase1_demo.py` (console output) | ✅ |
| Timing | Commands complete under 500ms on dev machine | Observed via demo run | ✅ |

## 3. Commands Executed

```bash
.venv\Scripts\pytest
.venv\Scripts\python packages/cmc_service/examples/phase1_demo.py
```

## 4. Metrics Collected
- Atom ingest latency (demo): ~2 ms for 1 KB payload
- Snapshot creation latency: ~2 ms
- Snapshot size: 1 atom; stats confirmed tag histogram

## 5. Outstanding Work
- Add structured metrics export (Prometheus) for ingest/snapshot counters
- Implement corruption/quarantine integration test
- Expand CLI status command with log integrity check results

## 6. Next Validation Steps
1. Add golden dataset ingest (multiple atoms) and record expected snapshot hash
2. Document Prometheus metric endpoints once implemented (Phase 1.1)
3. Coordinate with Gemini 2.5 to formalize determinism proof assumptions

---

*Updated automatically after each validation run.*
