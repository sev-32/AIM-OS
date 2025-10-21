# HHNI Validation Plan & Test Strategy

*Researcher: Gemini 2.5 Pro*  
*Date: 2025-10-18*  
*Target: HHNI v0.3*

---

## 1. Executive Summary

**Verdict: HIGHLY TESTABLE ✅**

The HHNI implementation is robust and well-structured, but requires rigorous testing beyond standard unit/integration tests to be considered production-grade.

This plan outlines a **three-tiered validation strategy** to ensure correctness, resilience, and performance.

---

## 2. Tier 1: Foundational Correctness (Unit Tests)

**Objective:** Verify each component in isolation.

### `packages/hhni/safety.py`
- [ ] **Test Case:** `test_atom_size_gate_ok` (99KB)
- [ ] **Test Case:** `test_atom_size_gate_fail` (101KB) → `ValueError`
- [ ] **Test Case:** `test_node_explosion_gate_ok` (999 nodes)
- [ ] **Test Case:** `test_node_explosion_gate_fail` (1001 nodes) → `RuntimeError`
- [ ] **Test Case:** `test_text_length_gates` (paragraph, sentence ok/fail)
- [ ] **Test Case:** `test_query_limiter` (adds `first: 1000`)
- [ ] **Test Case:** `test_query_limiter_noop` (with existing `first:`)
- [ ] **Test Case:** `test_depth_validation` (depth=5 ok, depth=6 fail)

### `packages/hhni/parsers.py`
- [ ] **Test Case:** `test_paragraph_parsing_mixed_newlines` (`\n`, `\r\n`)
- [ ] **Test Case:** `test_paragraph_parsing_extra_whitespace`
- [ ] **Test Case:** `test_sentence_parsing_common_delimiters` (`.`, `!`, `?`)
- [ ] **Test Case:** `test_sentence_parsing_no_final_delimiter`
- [ ] **Test Case:** `test_parsing_empty_and_whitespace_input`

### `packages/hhni/embeddings.py`
- [ ] **Test Case:** `test_get_model_cached` (proves singleton)
- [ ] **Test Case:** `test_encode_text_mocked` (verify correct shape 384)
- [ ] **Test Case:** `test_embed_batch_size_gate` (101 texts → `ValueError`)
- [ ] **Test Case:** `test_store_embedding_mocked` (verify Qdrant client called)
- [ ] **Test Case:** `test_store_embedding_qdrant_fails` → `Exception` raised

---

## 3. Tier 2: Resilience & Failure Modes (Integration Tests)

**Objective:** Verify system behavior under adverse conditions.

### `packages/hhni/dgraph_client.py`
- [ ] **Test Case:** `test_upsert_nodes_success` (mock `requests.post`)
- [ ] **Test Case:** `test_upsert_transient_failure` (fails twice, succeeds on 3rd retry)
- [ ] **Test Case:** `test_upsert_permanent_failure` (fails 3 times, raises `RuntimeError`)
- [ ] **Test Case:** `test_query_graphql_error_response` (raises `RuntimeError`)
- [ ] **Test Case:** `test_health_check_unhealthy`

### `packages/hhni/indexer.py`
- [ ] **Test Case:** `test_build_hhni_end_to_end` (mock DGraph/Qdrant)
- [ ] **Test Case:** `test_build_hhni_qdrant_fails` (verify retry logic and final exception)
- [ ] **Test Case:** `test_build_hhni_dgraph_fails` (verify exception propagates)
- [ ] **Test Case:** `test_build_hhni_empty_content` (creates doc node only)
- [ ] **Test Case:** `test_build_hhni_atom_too_large` (fails at pre-build gate)
- [ ] **Test Case:** `test_build_hhni_node_explosion` (fails at post-build gate)

---

## 4. Tier 3: Advanced Validation (Formal & Chaos)

**Objective:** Prove system invariants and discover unknown weaknesses.

### Formal Correctness Proofs
- [ ] **Determinism:** Prove `HHNINode` ID generation (`f"para:{atom.id}#p{p_idx}"`) is deterministic and collision-free for a given atom.
- [ ] **Idempotency:** Prove that running `build_hhni_for_atom()` twice on the same atom results in the same graph state (DGraph upsert behavior).
- [ ] **Invariant:** Prove that `len(node.children)` matches `count(children)` in the graph.

### Chaos Engineering Tests (`pytest-docker-tools`)
- [ ] **Test Case:** `test_indexing_while_dgraph_restarts`
  - Start DGraph container
  - Begin indexing 10 atoms
  - Kill DGraph container mid-way
  - Verify indexing fails gracefully with logged errors
  - Restart DGraph
  - Verify subsequent indexing succeeds

- [ ] **Test Case:** `test_indexing_while_qdrant_flaky`
  - Use `requests-mock` to make Qdrant fail 50% of the time
  - Verify retry logic handles transient errors
  - Verify final state is consistent

### Security & Vulnerability Analysis
- [ ] **Injection:** Can GraphQL queries be injected via atom content?
  - **Test:** Create atom with `content = 'text"}], "variables": { ... }'}`
  - **Expected:** `dgraph_client` should correctly escape this.
- [ ] **Resource Exhaustion:** Can a maliciously crafted atom (e.g., thousands of single-character paragraphs) bypass size limits but still cause performance issues?
  - **Test:** Atom with 99KB of `a\n\na\n\na...`
  - **Expected:** `validate_node_count` should catch this.

### Performance Regression Suite
- [ ] **Benchmark:** Create `benchmarks/test_hhni_perf.py`
- [ ] **Test Case:** `benchmark_indexing_100_atoms` (target: <5s)
- [ ] **Test Case:** `benchmark_query_cookbook` (run all 10 patterns, assert p99 < 200ms)
- [ ] **Action:** Run this suite on every PR to `packages/hhni/`

---

## 5. Implementation Plan

### For GPT-5 Codex & Claude 4.5
1. Create `tests/` directory inside `packages/hhni/`
2. Implement all Tier 1 and Tier 2 tests using `pytest` and `unittest.mock`.
3. Add `pytest-mock` and `requests-mock` to `requirements.txt`.

### For Gemini 2.5 Pro (Self-Assigned)
1. Write formal proofs for determinism and idempotency.
2. Implement Tier 3 Chaos Engineering tests.
3. Perform security vulnerability analysis.
4. Set up performance regression suite.

---

## 6. Required Tooling

- `pytest`
- `pytest-mock`
- `requests-mock`
- `pytest-docker-tools` (for chaos tests)
- `pytest-benchmark` (for performance suite)

---

## 7. Success Criteria

- 95%+ unit test coverage on `safety.py`, `parsers.py`, `embeddings.py`
- All Tier 2 integration tests passing
- At least one chaos test implemented and passing
- Performance benchmarks established and automated
- Formal proofs documented and peer-reviewed

---

*Validation plan ready. Awaiting team review before implementation.*
