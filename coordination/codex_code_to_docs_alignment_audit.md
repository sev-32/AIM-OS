# Codex Alignment Audit – Code-to-Documentation View  
**Date:** 2025-10-21  
**Author:** Codex (code-first sweep)  

## Scope & Method
- Reviewed implementation packages across the active codebase (`packages/*`) with emphasis on CMC, HHNI, SEG, APOE/orchestration, meta reasoning, document builders, and supporting tooling.  
- Cross-referenced each component against design sources (`analysis/themes/*.md`, `analysis/PLAN.md`, documentation under `Documentation/`, and coordination logs) to identify mismatches.  
- Sampled representative tests in `packages/*/tests` plus higher-level scenarios in `Testing/` to catalogue proven behaviours versus aspirational promises.  
- Catalogued recurring implementation patterns suitable for extraction into design templates/pattern libraries.  

## Component Findings

### 1. Context Memory Core (`packages/cmc_service`)
- **Implementation snapshot**
  - `memory_store.py` implements atom journaling, snapshot chaining, and metrics emission (`packages/cmc_service/memory_store.py:63`).  
  - `btsm.py` derives Bitemporal Total System Map nodes from vision tensor outputs and depends on `schemas` objects (`packages/cmc_service/btsm.py:27`).  
  - FastAPI surface (`packages/cmc_service/api.py:34`) exposes CRUD, policy hooks, and HHNI toggles; CLI + migrations (SQLite, JSONL) persist memory.  
- **Documentation coverage**
  - `packages/cmc_service/README.md:1` documents Phase‑1 MVP, but still references DGraph/Qdrant coupling and HHNI extras that are not present in current code paths.  
  - `analysis/themes/memory.md:4` references CMC + DVNS holistically but lacks detail on current journaling limits, SEG witness hooks, or BTSM trunk generation.  
  - `analysis/PLAN.md:28` sets policy pack expectations (policy-filtered `/mpd`) that are not implemented in the code.  
- **Implementation → documentation gaps**
  - BTSM utilities depend on `schemas.MPDNode`/`BitemporalEdge` yet no public README or design doc explains BTSM trunk creation or storage locations.  
  - `logging_utils.py` introduces Prometheus counters (`packages/cmc_service/logging_utils.py:12`) but docs never state what metrics exist or how they map to observability plans.  
  - Witness hooks (`packages/seg/witness.py:12`) default to `packages/cmc_service/data/seg` but CMC docs omit SEG directory expectations.  
- **Documentation → implementation gaps**
  - README promises HHNI integration via DGraph/Qdrant and a `--force` tag path; current HHNI package has pivoted to local in-memory indexing, DVNS physics, and no DGraph client wiring.  
  - `analysis/PLAN.md:36` references ACL plan APIs (`/mpd/nodes`) and policy pack inheritance. API module lacks those endpoints.  
  - Governance theme expects blast-radius policy validation; there is no enforcement in repository or API layers.  
- **Patterns surfaced**
  - Deterministic journaling + metrics instrumentation pattern (write-through journal + Prometheus counters) is reusable; should be formalized as “deterministic append-store” template.  
  - BTSM builder pattern (derive trunk nodes from high-level tensor summaries) could seed a “vision → MPD translation” pattern doc.  
- **Tests / evidence**
  - Unit tests cover repository/bitemporal behaviour (`packages/cmc_service/tests/test_repository.py:1`, `test_bitemporal.py:1`) and API smoke flows (`test_api.py:1`).  
  - Integration tests depend on `schemas` module that is currently missing from the repo (git status shows `schemas/` untracked), causing suite instability—documented as a blocking dependency gap.  

### 2. HHNI & Retrieval (`packages/hhni`)
- **Implementation snapshot**
  - Hierarchical fractal index (`packages/hhni/hierarchical_index.py:54`), semantic search (`packages/hhni/semantic_search.py:44`), token budgeting (`packages/hhni/budget_manager.py:57`), DVNS physics (`packages/hhni/dvns_physics.py:139`), and new two-stage retriever (`packages/hhni/retrieval.py:56`).  
  - Package `__init__` still exports legacy DGraph classes (`packages/hhni/__init__.py:1`), not the new core modules.  
- **Documentation coverage**
  - `analysis/themes/memory.md:9` mentions DVNS conceptually but omits concrete force coefficients, token budgeting, RS-lift goals, or retrieval stages.  
  - No README or design ADR captures the Week‑2 additions. Coordination logs (`coordination/daily/2025-10-21_phase_2_kickoff.md:332-342`) are the only record.  
- **Implementation → documentation gaps**
  - Budget manager strategies, audit trails, and `create_budget_items_from_search()` have no doc trail; success criteria in kickoff doc promised integration with VIF but no spec update explains audit schema.  
  - DVNS configuration (velocity clamps, convergence metrics) and RetrievalConfig (RS-lift instrumentation) need to be reflected in design docs and Ops guides.  
  - `TwoStageRetriever` is the canonical HHNI entry point but package-level exports/docs still point to absent DGraph integration.  
- **Documentation → implementation gaps**
  - Design references still expect external vector stores/Qdrant; current implementation is deterministic fallback only.  
  - Observability theme lists DVNS telemetry requirements (`analysis/themes/observability.md:9`) but no telemetry hooks exist.  
- **Patterns surfaced**
  - “Config + Result dataclass + audit trail” pattern repeated across DVNS, budget manager, retrieval—candidate for shared documentation/pattern library.  
  - Force computation modules share normalized vector utilities; could be consolidated/extracted.  
- **Tests / evidence**
  - Unit coverage exists for index, semantic search, budget manager, DVNS physics, and retrieval (all in `packages/hhni/tests`).  
  - RS-lift is instrumented but not benchmarked; tests assert non-zero results but do not measure ≥15% lift target.  

### 3. SEG & Witnessing (`packages/seg`)
- **Implementation snapshot**
  - Minimal witness writer (`packages/seg/witness.py:12`) appends JSONL entries and auto-fills metadata.  
  - No schema validation or partitioning; relies on default path under CMC `data/seg`.  
- **Documentation coverage**
  - SEG is prominent in design docs (`analysis/PLAN.md:16`, `analysis/themes/governance.md:4`) but there is no interface doc describing witness payload structure or storage conventions.  
  - `Testing/TEST_SCENARIOS.md:11` calls for contradiction audits and provenance validation; no automated tests exercise `write_witness`.  
- **Gaps**
  - Need documented schema for witness payloads (fields, provenance requirements).  
  - No example linking CMC/HHNI outputs to witness creation; high risk of drift if future code writes incompatible payloads.  

### 4. Orchestration & Policy (`packages/apoe_runner`, `packages/orchestration_builder`, `packages/doc_builder`)
- **Implementation snapshot**
  - APOE runner executes ACL plans, manages parameters, and writes SEG witnesses (`packages/apoe_runner/executor.py:256`).  
  - Policy gates implement behavioural enforcement decisions (`packages/orchestration_builder/policy_gates.py:52`) with evidence scoring and runtime state tracking.  
  - `doc_builder/generator.py:22` renders markdown from structured seeds; orchestration builder has executor/generator/test scaffolding.  
- **Documentation coverage**
  - `analysis/themes/orchestration.md:4` describes ACL, Iι-gating, DEPP but still references scripts (`scripts/run-plan.ts`) not present; no update ties to `apoe_runner`.  
  - Governance theme references policy packs but lacks mapping to `policy_gates.py` decisions or runtime telemetry.  
  - No README explains APOE runner CLI, plan schema, or witness integration; documentation for doc builder is absent.  
- **Implementation → documentation gaps**
  - Policy gate metrics (latency, depth, uncertainty) and decision enum are new but not captured in governance documentation or policy pack definitions.  
  - Plan execution error handling, workspace preparation, and witness emission pipelines lack ADRs or ops runbooks.  
  - Doc builder’s JSON→Markdown transformation and metadata instrumentation remain undocumented.  
- **Documentation → implementation gaps**
  - Orchestration theme promises ACL plans with typed budgets and capability tokens; repository does not include actual plan templates or generator for ACL.  
  - Governance docs require policy version propagation and VIF envelopes; code lacks these hooks.  
- **Patterns surfaced**
  - “Policy gating via dataclasses + decision enums” repeated; should evolve into a governance pattern doc.  
  - Witness emission reused across APOE, meta optimizer, doc builder; needs centralized guidance.  
- **Tests / evidence**
  - Tests exist for doc/orchestration generators but not for full ACL execution or policy gate boundary cases.  

### 5. Meta Reasoning & Optimization (`packages/meta_reasoning`, `packages/meta_optimizer`)
- **Implementation snapshot**
  - Thought articulator integrates LLM meta-reflection with optional CMC persistence (`packages/meta_reasoning/thought_articulator.py:51`).  
  - Vision tensor builder generates metric-rich tensors and writes witnesses (`packages/meta_optimizer/vision_tensor.py:16`).  
- **Documentation coverage**
  - Lucid Empire / vision tensor ideas live in DOCX/Markdown (`Documentation/LUCID_EMPIRE_ARCHITECTURE.md`, `analysis/themes/memory.md`) but lack explicit link to the current Python modules.  
  - No documentation explains dependencies (Google GenAI, environment variables) or expected outputs for articulated reasoning.  
- **Gaps**
  - Need pattern docs for “LLM articulation pipeline” and “vision tensor witness emission”.  
  - Clarify how outputs feed BTSM/HHNI (currently implicit via shared metadata).  
- **Tests / evidence**
  - Minimal tests exist (`packages/meta_optimizer/tests/test_vision_tensor.py:1`); meta_reasoning lacks tests entirely.  

### 6. Testing & Evidence
- **Implementation snapshot**
  - Unit suites exist for CMC, HHNI, doc/orchestration builder, vision tensor.  
  - `Testing/TEST_SCENARIOS.md:11` enumerates seven core promises with detailed scenarios spanning hundreds of steps.  
- **Gaps**
  - Scenario doc promises integration/acceptance tests (e.g., cross-session memory, blast-radius previews) that are not automated anywhere in repo.  
  - No linkage between scenario IDs and actual test files; missing status tracking (planned/in-progress/completed).  
  - External AI feedback in `Testing/artifacts/` is not catalogued against code outcomes.  

## Cross-Cutting Patterns & Opportunities
| Pattern | Observed Implementation | Documentation Status | Recommended Action |
| --- | --- | --- | --- |
| Deterministic append-store with metrics | `memory_store.py:63`, `store_io.py:1`, Prometheus counters | Not described outside README | Publish pattern doc + integrate into observability theme |
| Config + Result dataclass pairs w/ audit trail | DVNS (`dvns_physics.py:96`), budget manager (`budget_manager.py:32`), retrieval (`retrieval.py:24`) | No formal pattern reference | Document as “Audited computation modules” and standardize field naming |
| Witness emission helpers | `seg/witness.py:12`, used by APOE & vision tensor | Governance docs mention VIF but not JSONL schema | Produce witness schema doc + ADR linking components |
| Policy gate evaluations | `policy_gates.py:52` | Governance theme lacks runtime mapping | Capture policy enforcement template + metrics |
| Vision tensor → BTSM pipeline | `vision_tensor.py:16` feeds `btsm.py:27` | Design docs cite concept but not actual API | Add architecture note on data flow |

## Testing Evidence vs Promises
- **Covered by automated tests**
  - CMC storage, snapshot chaining, repository migrations (`packages/cmc_service/tests/*`).  
  - HHNI indexing/search/budget/DVNS/retrieval suites (`packages/hhni/tests/*`).  
  - Vision tensor generation (`packages/meta_optimizer/tests/test_vision_tensor.py`).  
  - Doc/orchestration basic generators (`packages/orchestration_builder/tests/*`, `packages/doc_builder/tests/test_generator.py`).  
- **Not yet automated (doc promises only)**
  - Core AIM-OS promises enumerated in `Testing/TEST_SCENARIOS.md` (e.g., “It never forgets,” “It shows impact before changes,” “Every decision has provenance”).  
  - RS-lift ≥ 15% bench is measured by instrumentation but has no regression harness.  
  - Policy gate escalation paths, SEG contradiction detection, and MIGE pipeline validations lack executable tests.  

## Priority Gap Backlog
1. **Document modern HHNI stack** – Update `analysis/themes/memory.md` and create HHNI README covering budget manager, DVNS physics, retrieval, and current dependency model (no DGraph).  
2. **Resolve CMC `schemas` dependency** – Track missing `schemas/` package (tests currently blocked) and align README/API docs with actual storage architecture.  
3. **Publish witness schema & policy enforcement ADR** – Define JSONL structure, retention policy, and map policy gate metrics to governance docs.  
4. **Backfill orchestration documentation** – Replace references to `scripts/run-plan.ts` with `apoe_runner` usage, document plan execution flow, and capture plan templates.  
5. **Meta reasoning/vision documentation & tests** – Document required credentials, outputs, and provide unit/integration coverage for `thought_articulator`.  
6. **Scenario-to-test mapping** – Add status table mapping `Testing/TEST_SCENARIOS.md` promises to actual automated suites, with owners and gaps.  

## Recommended Next Actions
1. **Author documentation updates** (HHNI, CMC, governance) as follow-on tasks; include ADRs where evolution diverged from the original plan.  
2. **Stabilize test harness** by committing or vendoring the `schemas` package and wiring HHNI retrieval tests into CI.  
3. **Create pattern library** (e.g., `docs/patterns/*.md`) capturing deterministic store, audited computation modules, witness emission, and policy gates.  
4. **Establish scenario tracking matrix** linking `Testing/TEST_SCENARIOS.md` IDs to automated suites and backlog entries.  
5. **Coordinate with Cursor-AI** to merge code-first findings with doc-first audit, prioritizing updates for Week‑3 roadmap.  
