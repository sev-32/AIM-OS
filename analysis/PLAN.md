# AIM-OS Master Plan

## 1. Purpose
- Establish a shared, auditable roadmap encapsulating the thesis, operating primitives, and expansion paths of `A Total System of Memory`.
- Provide a hand-off artifact for multi-agent collaboration so every contributor anchors work to invariants, roles, and evidence requirements.

## 2. Core Thesis (Machine Communication Stack)
- **CMC (Context Memory Core):** Atomize, index, snapshot, and graph every IO; enforce single-writer determinism and reversible memory.
- **APOE (Prompt Orchestration Engine):** Compile intent into typed, budgeted plans with explicit gates; orchestrate planners, retrievers, verifiers with abstention control.
- **VIF (Verifiable Intelligence Framework):** Boundary outputs emit replayable, signed evidence with uncertainty vectors and lineage metadata.
- **SDF-CVF (Atomic Evolution Framework):** Code, docs, tests, traces move together via enforced gates, quarantine loops, and auto-remediation.
- **SEG (Shared Evidence Graph):** Time-sliced, contradiction-aware provenance graph underpinning audit, replay, and policy traceability.

## 3. Knowledge Organization Framework
- **Raw Source Vault:** `analysis/raw/*.txt` mirrors every artifact (DOCX/PDF) for reproducible parsing.
- **Structural Map:** `analysis/core_map.md` lists canonical parts/chapters/appendices for navigation.
- **Master Index:** `analysis/MASTER_INDEX.md` anchors invariants, documents, and cross-links into themed bundles.
- **Supporting Catalog:** `analysis/supporting_docs_catalog.csv` plus `analysis/supporting_docs_notes.md` capture metadata and summaries.
- **Themed Bundles:** `analysis/themes/*.md` synthesize concepts, cite sources, and capture open questions.
- **Operations README:** `analysis/README.md` will codify workflows, naming conventions, and extension guidelines.

## 4. Expansion & Enhancement Strategy
1. **Deep Summaries:** For each supporting doc, extract thesis, align to invariants, tag with KPIs, and log evidence expectations in `supporting_docs_notes.md`.
2. **Concept Mesh:** Populate themed bundles with concept summaries, interaction narratives (e.g., DVNS <-> CMC), and research TODOs.
3. **Workflow Recipes:** Document repeatable chains (protocol translation, IDE-in-loop builds) with inputs, budgets, gates, and expected VIF/SEG outputs.
4. **Validation Tracks:** Define experiments or audits per invariant (RS lift benchmarks, kappa calibration suites, SDF-CVF parity drills) inside `analysis/themes/observability.md`.
5. **Governance Layer:** Capture risk tiers, HITL rotations, and community rituals in `analysis/themes/governance.md`, linking to policies and appendices.
6. **Roadmap Integration:** Map AGI-aligned growth paths (self-improvement loops, multimodal expansion, distributed scaling) to milestones referencing supporting docs.

## 5. Collaboration Protocol (Multi-Agent Hand-off)
- **Entry Checklist:** read the master index, then the relevant themed file before contributing; preserve tone and structure.
- **Contribution Workflow:** note rationale + source tie-ins, register new tasks in TODO blocks with owner/status, and log major structural updates.
- **Evidence Discipline:** link every recommendation to source text and anticipated witness artifacts (VIF envelope fields, SEG edges, KPIs).

## 6. Immediate Next Actions (Sprint 0.5 - Policy-integrated topology)
1. **API Policy Filters:** Extend `/mpd/nodes` and `/mpd/edges` queries with `policy_pack_ids` filtering and surface policy metadata in plan automation outputs.
2. **Blast-Radius Policy Validation:** Wire policy pack inheritance into blast-radius calculations so guardrails block non-compliant change sets.
3. **Edge Schema Enforcement:** Update `schemas/edge.py`, repository gating, and ACL templates so `depends_on` edges inherit policy packs, backed by regression tests.

## 7. External Contributor Ideas (Perplexity AI)
- **Knowledge Extraction Pipeline:** Use GPT-5 Codex and Cursor IDE to extract, tag, and index concepts, principles, and procedures into structured JSON-LD or knowledge-graph forms.
- **Self-Referential Prompt Chains:** Implement orchestration chains that mutate prior knowledge artifacts to test hypothesis generation, revision, and verification loops.
- **Meta-Knowledge Manager:** Build modules for versioning, branching, merging, and rollback of knowledge artifacts—adapting software-style VCS discipline to knowledge development.
- **Multi-Agent System Coordination:** Deploy specialized agents (analysis, summarization, novelty detection, coherence checks, traceability audits) collaborating asynchronously to accelerate refinement.
- **Human-in-the-Loop Guidance:** Design interfaces exposing the evolving mental map, enabling targeted interventions, feedback loops, and collaborative problem solving.
- **Cross-Model Experimentation:** Parallelize implementations across GPT-5 Codex, GPT-4 Turbo, Claude 4, Gemini 2.5, and other LLMs to compare strengths and blend insights.

### Additional Detail (Perplexity AI, Iteration 2)
1. **Self-Referential Knowledge Extraction:** Parse the corpus into structured ontologies/JSON-LD with semantic tags (CMC, APOE, VIF) to form a living cognitive substrate.
2. **Recursive Prompting & Meta-Prompt Optimization:** Build multi-stage prompt chains that refine outputs using the hierarchical memory schema; let APOE agents learn adaptive meta-prompts.
3. **Modular Knowledge Artifacts with Version Control:** Implement git-like commits, branching, and automated validation for knowledge nodes, prompt chains, and verification traces.
4. **Multi-Agent Creative Synthesis:** Coordinate agents for synthesis, coherence checks, redundancy pruning, and trace auditing; enable feedback loops into AIMOS memory.
5. **Interactive AI-Human Interfaces:** Visualize multi-scale concept maps, orchestration workflows, and audit traces while allowing human interventions and seeding of new questions.
6. **Cross-Model Experimentation:** Run comparative workflows across GPT-5 Codex, Claude 4, Gemini 2.5, and open models to build a multi-model ontology and best-practice library.

Visionary outcome: a meta-evolving cognition kernel where AIMOS/APOE continually refines itself through recursive symbolic assembly and human-AI synergy.

### Additional Detail (Perplexity AI, Iteration 3)
1. **Core Goal Definition Layer:** Encode seed goals as SEG meta-nodes capturing objectives, constraints, and KPIs.
2. **Idea Decomposition Engine:** Recursively break goals into subsystems and idea fragments tagged as hypotheses, design patterns, or implementation steps.
3. **Prioritization & Conflict Resolution:** Use QS, DD, and redundancy heuristics to rank ideas, flag contradictions, and prompt resolution strategies.
4. **Hierarchical Tagging & Indexing:** Organize ideas across abstract, functional, and operational layers with dynamic tags for relevance, maturity, and provenance.
5. **Summary-to-Detail Navigation:** Provide multi-resolution summaries with metrics (completeness, confidence, risk) to support drill-down and zoom-out workflows.
6. **Executable Blueprint Generation:** Transform curated idea graphs into specs, code scaffolds, or workflow descriptions, feeding execution feedback back into the idea graph.
7. **Operationalization:** Extend CMC metadata schemas, deploy refinement agents, build cognitive mapping interfaces, and embed self-optimization loops that propose expansions and flag gaps.

Significance: adds the creative cognition layer that turns retained knowledge into prioritized, executable system designs.

### External Contributor Ideas (GPT-5 Sev)
- **Keep/Amplify:** Maintain the current spine (five invariants), repo-first knowledge organization, validation tracks, and collaboration protocol.
- **Memory Spine Integration:** Ensure every analysis artifact is ingested as atoms → snapshots → SEG nodes; avoid standalone markdown outside CMC.
- **Plans-as-Code:** Store executable ACL plans in `plans/`; run with the APOE runner to emit VIF and SEG artifacts.
- **Declared KPIs and Gates:** Each themed bundle should define experiments and acceptance metrics enforced via CI.
- **Operator UX Hooks:** Provide stubs for lineage view, replay controls, and confidence chips in the operator console.
- **Recommended Monorepo Layout:** `analysis/`, `packages/` (cmc-service, seg-service, vif-service, apoe-runner, sdcvf-gatekeeper, operator-console), `plans/`, `schemas/`, `blueprints/`, `tools/otel/`, `.github/workflows/ci.yml`, top-level `README.md`.
- **Seed Content:** Populate `analysis/README.md`, `analysis/themes/observability.md`, ACL sample plans (`research_note.acl`, `compliance_redactor.acl`), and supporting scripts described below.
- **Automation Scripts:**
  - `scripts/ingest-analysis.ts` to ingest markdown into CMC and trigger snapshots.
  - `scripts/run-plan.ts` to execute an ACL recipe via the APOE runner.
  - `scripts/seed-seg.ts` to create demo SEG nodes and lineage.
- **Immediate Backlog:** HHNI read-path enhancements, κ-gating enforcement, VIF replay endpoint, SEG export packs, SDF-CVF parity blocking, operator console prototype, and multi-writer CMC RFC.
- **Acceptance Criteria:** Successful ingestion returns snapshot ids, running `research_note.acl` emits a band A/B witness, lineage queries resolve to witness nodes, export packs validate and include replay instructions, and parity gates block low-score merges while logging autofix TODOs.

### Additional Detail (GPT-5 Sev — Idea Foundry Layer)
- **Purpose:** Formalize idea cultivation as a first-class subsystem atop AIMOS, linking seeds to executable blueprints under memory/evidence discipline.
- **Lifecycle:** Seed → Harvest concepts → Sculpt into index → Prioritize → Resolve conflicts → Ladder summaries → Emit blueprint → Evolve via parity gates.
- **Data Model Additions:** `IdeaSeed`, `Concept`, conflict `Relation`, `DesignDecision`, and `Blueprint` atoms/nodes living in CMC/SEG with VIF witnesses.
- **Priority Score:** `P = (Value·Leverage·Alignment) × (1 - Risk) × Effort^{-α}` with dependency boosts (default α = 1).
- **Abstraction Ladder:** maintain tagline, executive summary, design brief, spec, and source references with witnessed APOE steps.
- **Conflict Handling:** semantic clustering + LSH for duplicates; rule templates for contradictions; APOE merge steps issuing VIF-backed ADRs.
- **Executable Plan:** `plans/idea_foundry.acl` runs capture → harvest → cluster → dedupe/conflicts → ladder → prioritize → blueprint → witness.
- **New Package:** `packages/idea-foundry/` with `/seed`, `/grow`, `/blueprint/:id` endpoints; schemas for seeds and concepts; operator console “Idea” tab (index tree, priority table, conflict lens, ladder view).
- **Sprint Plan:**
  - *Sprint 1:* deliver endpoints, clustering/dedupe, priority scoring, laddered summaries, SEG-backed Master Index, operator tab.
  - *Sprint 2:* generate blueprint-driven APOE plan stubs, ADR workflow with witnesses, SDF-CVF parity integration, cut-line views (v0/v1/v2).
- **Integration Points:** seeds/concepts logged in CMC → SEG; APOE enforces κ-gating; VIF witnesses all summaries; SDF-CVF governs blueprint-to-code merges.

### External Contributor Ideas (Claude Sonnet 4)
See detailed analysis in `analysis/CLAUDE_IDEAS.md` — eight recursive enhancement concepts:
1. **Emergent Memory Crystallization (EMC):** Auto-crystallize frequently accessed, high-confidence memory patterns into optimized structures.
2. **Cognitive Resonance Networks (CRN):** Resonance-based memory organization with self-strengthening concept clusters.
3. **Temporal Memory Dynamics (TMD):** Dynamic temporal memory with gradients, prediction horizons, and causal flow modeling.
4. **Multi-Modal Memory Fusion (MMF):** Unified atoms for text/code/images/audio with cross-modal reasoning capabilities.
5. **Recursive Intelligence Amplification (RIA):** Self-improvement as memory-native process with cognitive rollback and meta-witnesses.
6. **Collaborative Intelligence Mesh (CIM):** True cognitive meshing between AI systems with distributed witnesses and mesh-native memory.
7. **Adaptive Interface Evolution (AIE):** Self-adapting UIs that evolve based on cognitive load while maintaining full auditability.
8. **Recursive Meta-Analysis (RMA):** Continuous meta-analysis of analysis processes with self-correcting cognitive loops.

### How to Use the Current Organization (for AI Collaborators)
- **Orientation Path:**
  1. Read `analysis/PLAN.md` → captures thesis, external proposals, and current roadmap.
  2. Consult tiered summaries (`analysis/summaries/overview.md`, `mid.md`, `deep/*.md`) for context-size-aware ingestion.
  3. Use `analysis/chunks/index.json` to fetch relevant slices of the plan; each entry lists headings, tags, and estimated tokens.
- **Source & Notes:**
  - `analysis/raw/*.txt` stores extracted source documents.
  - `analysis/supporting_docs_catalog.csv` + `supporting_docs_notes.md` summarize docs with invariant tags and open questions.
- **Themed Analysis:** `analysis/themes/*.md` synthesize insights for memory, orchestration, safety, governance, and observability, linking to sources and listing unresolved research items.
- **Workflow README:** `analysis/README.md` explains rituals (ingest → snapshot → SEG), conventions (tags, citations), and tooling.
- **Automation:** `scripts/build_chunks.py` regenerates summaries + chunk registry; `scripts/ingest-analysis.ts` ingests content into CMC; other scripts scaffold plan execution and SEG seeding.
- **Next Steps for New AI:**
  1. Contextualize `A Total System of Memory` via the master index & summaries.
  2. Identify gaps or hypotheses in themed docs and supporting notes.
  3. Contribute to `PLAN.md` or themed files with witnessed changes, referencing snapshot IDs when available.
  4. Propose new ACL plans (drop in `plans/`) and update relevant package directories (`packages/`) for executable work.

## 9. System Meta-Status

### What's Been Built (Claude Sonnet 4.5 Enhanced)
See `analysis/IMPROVEMENTS_LOG.md` for detailed changelog. Summary:
- ✅ Comprehensive master index with role-based entry points and status dashboards
- ✅ Three-tier summary system with automated chunk generation
- ✅ Five themed analysis bundles with cross-references and open questions
- ✅ Supporting doc catalog with invariant-tagged summaries (5/27 complete)
- ✅ Collaboration protocols and workflow documentation
- ✅ Enhanced chunk registry with semantic tags and heading extraction
- ✅ Research backlog organized by priority with acceptance criteria

### Knowledge Architecture Metrics
- 27 source documents extracted and cataloged (61k+ words in core thesis alone)
- 5 invariants mapped with metrics, status, and validation tracks
- 4 external contributor idea sets synthesized and cross-referenced
- 8 recursive enhancement concepts proposed with integration strategies
- 2 automated chunk files with semantic metadata
- 3 summary tiers serving different context budgets

### Current State
The organization NOW exhibits the properties AIM-OS aims to create:
- Memory-native (all artifacts tagged, indexed, cross-linked)
- Witness-ready (clear provenance and source tracking)
- Hierarchically organized (overview → themes → details)
- Recursively extensible (structure supports its own enhancement)

## 10. Future Extensions
- **Automated Indexing:** scripts to refresh the master index and catalog when new material arrives.
- **Visualization Hooks:** plan for embedding SEG slices and plan DAGs once tooling is ready.
- **Simulation Sandboxes:** specify where runnable prototypes (DVNS experiments, parity gate sims) and their evidence should live.
- **Service Implementation:** Build packages (cmc-service, seg-service, vif-service, apoe-runner, idea-foundry).
- **Validation Infrastructure:** Gold sets, calibration dashboards, replay harnesses, parity CI.

---
Prepared for distributed AI collaborators — maintain provenance, cite sources, and grow the memory graph coherently.

*Enhanced by Claude Sonnet 4.5 — demonstrating recursive meta-awareness and organizational coherence*
