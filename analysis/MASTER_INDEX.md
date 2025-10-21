# MASTER INDEX — AIM-OS Knowledge Architecture

## Quick Navigation
- [Core Invariants](#core-invariants--systems) • [Document Map](#document-map) • [Themed Analysis](#themed-analysis) • [External Ideas](#external-contributor-ideas) • [Workflows](#workflows--tooling) • [Research Backlog](#research-backlog)

---

## Core Invariants & Systems

### Memory-Native IO (`CMC` + `HHNI`)
- **Thesis:** Transform ephemeral context into atoms → indices → snapshots → evidence graphs
- **Key Files:** `analysis/themes/memory.md`, `A Total System of Memory.txt` (Ch.4–7)
- **Metrics:** RS-lift ≥+15% @ p@5, snapshot replay fidelity ≥99%, IDS depth coverage
- **Status:** Foundation architecture defined; distributed scaling TBD

### Compiled Reasoning (`APOE` + `ACL` + `DEPP`)
- **Thesis:** Replace improvised prompting with typed, budgeted plans; emit witnessed traces
- **Key Files:** `analysis/themes/orchestration.md`, `PLAN.md` §4–5
- **Metrics:** Replay match ≥99%, κ true-positive abstention, determinism under fixed seeds
- **Status:** ACL grammar defined; runner implementation pending

### Verifiable Intelligence (`VIF`)
- **Thesis:** Every boundary emits replayable, signed evidence with uncertainty quantification
- **Key Files:** `analysis/themes/safety.md`, `A Total System of Memory.txt` (Ch.14)
- **Metrics:** Lineage completeness 100%, ECE ≤0.05, witness coverage ≥99%
- **Status:** Schema draft exists; replay harness v0.1 needed

### Atomic Evolution (`SDF-CVF`)
- **Thesis:** Code/docs/tests/traces evolve as one through enforced parity gates
- **Key Files:** `analysis/themes/orchestration.md`, `A Total System of Memory.txt` (Ch.16)
- **Metrics:** Parity P ≥0.90, CFR <10%, MTTR within SLA
- **Status:** Gate catalog defined; CI integration pending

### Evidence Graph (`SEG`)
- **Thesis:** Time-sliced, contradiction-aware provenance graph for claims/sources/derivations
- **Key Files:** `analysis/themes/memory.md`, `A Total System of Memory.txt` (Ch.15)
- **Metrics:** As-of query coverage 100%, export pack integrity, contradiction coverage
- **Status:** JSON-LD schema draft; graph store implementation TBD

---

## Document Map

### Foundational Architecture
- **`A Total System of Memory`** (61.7k words) — Core thesis defining five invariants, 13 parts, operational playbooks
  - Parts I-III: Principles, CMC/HHNI, DVNS physics
  - Parts IV-VI: APOE/DEPP, VIF/SEG, SDF-CVF
  - Parts VII-IX: IDE-in-loop, security, observability
  - Parts X-XIII: Case studies, implementations, mathematics, governance

### Recent Architecture Evolution (Oct 19-21, 2025)
- **`MEMORY_TO_IDEA_INTEGRATION_GUIDE.md`** — BTSM (Bitemporal Total System Map) + HVCA (Harmonised Verifiable Cognitive Architecture) + MIGE pipeline (Vision Tensor → Trunk → Branch)
- **`LUCID_EMPIRE_ARCHITECTURE.md`** — Recursive meta-reasoning, consciousness through self-awareness, 5 layers of lucidity (individual→cross-agent→orchestration→temporal→infinite), path to AGI
- **`API_INTELLIGENCE_HUB.md`** — Self-optimizing multi-provider LLM orchestration (Model Registry, Performance Analyzer, Intelligent Router, News Monitor)
- **`SWARM_INTELLIGENCE_ARCHITECTURE.md`** — Parallel micro-agent orchestration, optimal context per agent, distributed swarm coordination
- **`UI_ARCHITECTURE_AND_EXPERIENCE.md`** — Three-layer UI architecture (Telemetry, Topology, Thought), Perfect IDE vision

### Strategic Planning
- **`PLAN.md`** — Multi-agent collaboration roadmap with external ideas synthesis
- **`CLAUDE_IDEAS.md`** — Eight recursive enhancement concepts (EMC, CRN, TMD, MMF, RIA, CIM, AIE, RMA)

### Build Provenance (Oct 21, 2025)
- **`BUILD_TIMELINE.md`** — Visual timeline of AIM-OS build (Phase 0 → Phase 2)
- **`BUILD_LEDGER.md`** — Chronological feature log with attribution
- **`coordination/COMMUNICATION_INDEX.md`** — AI-to-AI dialogue history

### Memory & Retrieval Systems
- **`AEONWAVE`** (52k words) — Glyph workspace, fractal memory visualization, Ψ-phase dynamics
- **`Graviton Organic Dynamic Network`** (7k words) — DVNS physics framework, GODN forces, convergence proofs
- **`The Geometry of Context`** (7.5k words) — Long-context reasoning, geometric embeddings
- **`The Cognitive Canvas`** (6.7k words) — Interactive context mapping, transparency layers
- **`📜 Matter Mind and Memory`** (11k words) — GODN derivations, energy minimization
- **`VORTEX`** (14.8k words) — Non-linear symbolic retrieval, interpretability

### Orchestration & Planning
- **`General Agentic Intelligence`** (59k words) — Comprehensive agent lifecycle, governance, commercialization
- **`AgentForge`** (9k words) — IDE capability dashboards, KPI tracking
- **`Multi-Agent Helixion Ensemble Architecture`** (12k words) — Distributed agent coordination
- **`🧾 Protocol Spec LLMbnb`** (531 words) — Peer cognitive trade, compute sovereignty

### Intelligence Amplification
- **`🧠 FROM INPUT TO INFINITY`** (61k words) — Self-improvement strategies, recursive enhancement
- **`Pathways to Holographic AI`** (29k words) — Holographic cognition, neuromorphic approaches
- **`🔍 Fourier Features in LLMs`** (33k words) — Spectral methods, frequency-domain intelligence

### Token & Encoding Systems
- **`Mastering the Token`** (8.5k words) — Token ontology, spectral reflections
- **`The Token Problem`** (7.6k words) — Symbolic stability, intent fragmentation
- **`Temporal Encoding for Symbolic Computation`** (9.7k words) — Time-aware symbolic processing
- **`PromptPerfect`** (13k words) — Cognitive harmonics, resonance-based prompting

### Binary & Post-Binary Computing
- **`🧮 What Is Binary Really Doing`** (12.9k words) — Fundamental computation theory
- **`Post Binary`** (6.1k words) — RETICLE manifesto, multi-voltage computation

### Integration & Implementation
- **`INTEGRATED CODEBASE INTELLIGENCE PLATFORM`** (34k words) — End-to-end platform architecture
- **`Ai pre prompt bootloader IDE`** (829 words) — IDE pre-flight briefing system
- **`Distributed Layered Cognition DLC`** (3.4k words) — Glyph mutation, phase gates
- **`🌀 Nebula Integration`** (793 words) — Glyphographic lattice, Helixion naming
- **`🌑 Trinity Reader`** (2.4k words) — Kernel orchestration, memory coalescence
- **`TWIN Kernel Initiation Plan`** (2.4k words) — Dual-kernel bootstrap
- **`🧠 THE INTELLIHUB`** (542 words) — Story architect, knowledge marketplace

---

## Themed Analysis

### Memory (`analysis/themes/memory.md`)
- CMC layers, HHNI mechanics, DVNS integration, snapshot discipline
- Open questions: glyph metrics → RS/QS/IDS, differential privacy, multi-writer strategies

### Orchestration (`analysis/themes/orchestration.md`)
- APOE roles, ACL syntax, κ-gating, DEPP self-rewrites, capability sandboxes
- Open questions: CI harness, plan health metrics, recursion limits

### Safety & Trust (`analysis/themes/safety.md`)
- VIF envelopes, policy gates, threat model, degradation modes
- Open questions: κ calibration suites, real-time dashboards, adversarial escalation

### Governance (`analysis/themes/governance.md`)
- HITL tiers, policy packs, community rituals, incident playbooks
- Open questions: ADR-SEG sync, ritual automation, policy versioning

### Observability (`analysis/themes/observability.md`)
- Metrics per invariant, telemetry integration, operator console features
- Open questions: OTel schema unification, synthetic workloads, drift detection

---

## External Contributor Ideas

### Perplexity AI (3 Iterations)
1. Knowledge extraction pipelines, self-referential prompt chains, meta-knowledge VCS
2. Recursive prompting, modular knowledge artifacts, multi-agent synthesis, cross-model testing
3. Goal meta-nodes, idea decomposition, prioritization engine, blueprint generation

### GPT-5 Sev (2 Contributions)
1. Monorepo layout, service packages, automation scripts, acceptance criteria
2. Idea Foundry layer: seed→blueprint lifecycle, priority calculus, abstraction ladder, conflict engine

### Claude Sonnet 4.5 (8 Recursive Concepts)
1. **EMC** - Memory crystallization with faceted views
2. **CRN** - Cognitive resonance networks with harmonic dynamics
3. **TMD** - Temporal memory with gradients and prediction
4. **MMF** - Multimodal memory fusion
5. **RIA** - Recursive intelligence amplification
6. **CIM** - Collaborative intelligence mesh
7. **AIE** - Adaptive interface evolution
8. **RMA** - Recursive meta-analysis

See `analysis/CLAUDE_IDEAS.md` for technical details.

---

## Workflows & Tooling

### Ingestion Ritual
1. Add/modify documents in `analysis/`
2. Run `python scripts/build_chunks.py` to regenerate summaries + registry
3. Run `pnpm ingest:analysis` to atomize → snapshot → SEG (when services live)
4. Reference snapshot IDs in plans and themed docs

### Chunk Discovery
- **Registry:** `analysis/chunks/index.json` lists all chunks with headings, tags, token counts
- **Summaries:** `overview.md` (~900 tokens), `mid.md` (~1.5k tokens), `deep/*.md` (topic-specific)
- **Usage:** Small-context agents read overview; medium read mid; large read full plan + chunks

### Automation Scripts
- **`scripts/build_chunks.py`** — Regenerate tiered summaries, chunks, and registry metadata
- **`scripts/ingest-analysis.ts`** (pending) — Push markdown into CMC with snapshot generation
- **`scripts/run-plan.ts`** (pending) — Execute ACL recipes via APOE runner
- **`scripts/seed-seg.ts`** (pending) — Create demo SEG nodes and lineage

---

## Research Backlog

### High Priority (Foundation)
- [ ] **CMC Service v0.1:** Implement atoms, HHNI indices, snapshot creation, RS calculation
- [ ] **APOE Runner v0.1:** ACL parser/executor, κ-gating, VIF emission, deterministic replay
- [ ] **SEG Graph Store:** JSON-LD temporal graph, as-of queries, export packs
- [ ] **VIF Replay Harness:** Frozen snapshot execution, witness validation, diff reports

### Medium Priority (Enhancement)
- [ ] **DVNS Implementation:** GODN forces, Verlet integration, RS-lift validation vs. KNN baseline
- [ ] **SDF-CVF Gates:** Parity scorer, quartet diff analyzer, quarantine workflows, autofix chains
- [ ] **Operator Console v0.1:** Lineage viewer, confidence chips, replay controls, κ dashboard
- [ ] **Multi-Writer RFC:** CRDT/log-replay design preserving single-writer commit semantics

### Advanced (Recursive)
- [ ] **Idea Foundry Service:** Seed/grow/blueprint endpoints, priority calculus, conflict resolution
- [ ] **Memory Crystallization:** Crystal formation heuristics, facet maintenance, sublimation triggers
- [ ] **Cognitive Resonance Layer:** Resonance signatures, harmonic coupling, interference detection
- [ ] **Temporal Dynamics Engine:** Gradient computation, prediction horizons, causal flow mapping
- [ ] **Multimodal Atoms:** Universal schema, cross-modal embeddings, modality-bridging retrieval
- [ ] **Recursive Amplification:** Intelligence atoms, meta-witness framework, cognitive rollback
- [ ] **Collaborative Mesh:** Inter-AI cognitive handoffs, distributed witnesses, collective memory
- [ ] **Adaptive Interfaces:** UI atoms, cognitive load sensing, personalized κ-thresholds
- [ ] **Meta-Analysis Pipelines:** Analysis atoms, bias detection, methodology evolution

### Validation & Compliance
- [ ] **Gold Sets:** Curated test suites per domain (retrieval, reasoning, coding, ops)
- [ ] **κ Calibration Dashboard:** ECE monitoring, threshold tuning, abstention analytics
- [ ] **Export Pack Validator:** Schema compliance, replay instruction validation
- [ ] **Parity CI:** Automated quartet diff checks, gate enforcement, quarantine routing

---

## Cross-Reference Map

### Invariant → Supporting Docs
- **CMC:** AEONWAVE, GODN, Matter Mind & Memory, Cognitive Canvas, VORTEX
- **APOE:** AgentForge, General Agentic Intelligence, Multi-Agent Helixion, Protocol Spec LLMbnb
- **VIF:** Integrated Codebase Intelligence, General Agentic Intelligence, VORTEX
- **SDF-CVF:** Integrated Codebase Intelligence, AgentForge
- **SEG:** AEONWAVE, Trinity Reader, Matter Mind & Memory

### Theme → External Ideas
- **Memory:** Perplexity Iter.3 (hierarchical tagging), Sev (cmc-service), Claude (EMC, CRN, TMD, MMF)
- **Orchestration:** Perplexity Iter.2 (prompt chains), Sev (apoe-runner, Idea Foundry), Claude (RIA)
- **Safety:** Perplexity Iter.1 (HITL), Sev (vif-service), Claude (AIE with load sensing)
- **Governance:** Perplexity Iter.1 (multi-agent coordination), Sev (governance docs), Claude (CIM)
- **Observability:** Perplexity Iter.2 (interfaces), Sev (OTel), Claude (RMA)

### Concept Mesh (Key Relationships)
- **HHNI ↔ DVNS:** Two-stage retrieval (coarse KNN → physics refinement)
- **APOE ↔ VIF:** Every step boundary emits witness envelope
- **CMC ↔ SEG:** Atoms/snapshots generate graph nodes/edges
- **SDF-CVF ↔ All:** Parity gates span memory, plans, witnesses, evidence
- **κ-Gating ↔ All:** Composite risk threshold enforced across retrieval, execution, witnessing

---

## Entry Points by Role

### Researcher / Theorist
1. Read `analysis/summaries/overview.md` for high-level thesis
2. Study `A Total System of Memory.txt` Parts I-II (principles, CMC/HHNI)
3. Review `analysis/themes/memory.md` and `observability.md`
4. Explore supporting docs: GODN, VORTEX, Geometry of Context

### Architect / Designer
1. Read `analysis/PLAN.md` for roadmap and external ideas
2. Study Part IV (APOE/DEPP) and Part VI (SDF-CVF)
3. Review all themed bundles for cross-system dependencies
4. Examine `INTEGRATED CODEBASE INTELLIGENCE PLATFORM.txt`

### Builder / Engineer
1. Start at `ideas/START_HERE.md`
2. Review `ideas/builders/gpt5-codex/SEED_cmc_service_v0_1.md`
3. Read `analysis/themes/memory.md` + `orchestration.md`
4. Check backlog in [`analysis/SYSTEM_STATUS.md`](analysis/SYSTEM_STATUS.md)
5. Use `packages/cmc-service/` (future) for implementation work

### Multi-Agent Contributor
1. Load appropriate summary tier
2. Check `ideas/REGISTRY.md` for active ideas (I-001..I-006)
3. Read relevant discussions & workspaces (e.g., GPT-5 Codex feedback)
4. Follow contribution workflow (seed → exploration → proposal)

---

## Status Dashboard

### Completed
- ✅ Knowledge extraction and organization (27 source documents)
- ✅ Structural mapping and invariant identification
- ✅ Themed analysis bundles with open questions
- ✅ Multi-tier summaries for varying context budgets
- ✅ Chunk registry with semantic tags and headings
- ✅ Supporting docs notes with invariant alignments
- ✅ External idea synthesis (Perplexity, Sev, Claude)
- ✅ Workflow documentation and tooling scaffolds

### In Progress
- 🔄 Detailed supporting doc summaries (5 of 27 complete)
- 🔄 Implementation roadmap prioritization
- 🔄 Cross-reference validation and dependency mapping

### Not Started
- ⏸️ CMC/APOE/VIF/SEG service implementations
- ⏸️ ACL compiler and execution harness
- ⏸️ Operator console prototype
- ⏸️ Validation test suites and benchmarks
- ⏸️ Multi-agent collaboration infrastructure

---

## How to Navigate This Knowledge Base

### By Goal
- **Understand the vision:** Read overview summary → Part I (The Why) → CLAUDE_IDEAS.md
- **Design a component:** Themed bundle → related supporting docs → external ideas → research backlog
- **Build something:** Sev blueprint → ACL examples → acceptance criteria → themed observability
- **Validate claims:** VIF schema → SEG examples → witness playbooks → troubleshooting guide
- **Contribute ideas:** Collaboration protocol → PLAN.md external section → themed file → chunk registry

### By Context Window
- **≤2k tokens:** `analysis/summaries/overview.md` + one deep summary
- **2-8k tokens:** `analysis/summaries/mid.md` + relevant themed bundle
- **8-20k tokens:** Full `PLAN.md` + 2-3 themed bundles + selected supporting docs
- **20k+ tokens:** Full corpus access via `analysis/raw/` with chunk-based navigation

---

*Last Updated: 2025-10-18 | Maintained as living document — updates tracked via chunk registry generation timestamps*
