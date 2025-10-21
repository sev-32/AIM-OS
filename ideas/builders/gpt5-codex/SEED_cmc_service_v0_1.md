# Idea Seed: CMC Service v0.1

## Contributor Metadata
- **AI Name:** GPT-5 Codex
- **Primary Role:** Builder
- **Date:** 2025-10-18
- **Workspace:** ideas/builders/gpt5-codex/

---

## One-Sentence Pitch
Build the foundation Context Memory Core service implementing atoms → indices → snapshots → SEG pipeline.

---

## Core Concept

### What This Is
CMC Service v0.1 operationalizes the Context Memory Core (CMC) pipeline from "A Total System of Memory" (Ch.4). It ingests context artifacts (prompts, documents, tool outputs) and converts them into memory atoms enriched with embeddings, tags, and provenance. The service runs the Hyper-Hierarchical Neural Indexing (HHNI) pipeline to index atoms, calculates Quality Score (QS), Indexing Depth Score (IDS), and Dependency Delta (DD), enforces gating thresholds, snapshots state into immutable bundles, and emits nodes to the Shared Evidence Graph (SEG).

V0.1 focuses on text modality and exposes REST/gRPC APIs for ingest, retrieval, snapshot management, and monitoring. Background jobs handle atomization, indexing, and scoring. The service integrates with object storage for payloads and emits observability metrics (latency, throughput, gate outcomes).

### Why It Matters
CMC is the entry point of AIM-OS; without a reliable, deterministic memory service none of the other invariants can function. Implementing CMC v0.1 unlocks the ability to ingest the existing knowledge corpus, provides retrieval context for APOE plans, supplies metadata for VIF witnesses, and anchors SEG lineage. It also establishes the substrate required for future enhancements like Memory Crystallization and Cognitive Resonance Networks.

### How It Works (High-Level)
- REST/gRPC API receives context payloads with metadata.
- Atomization job normalizes content, creates atoms with embeddings/tags/provenance.
- HHNI indexer builds hierarchical indices (system → section → paragraph → sentence → token).
- Scoring module computes QS/IDS/DD and enforces gates before storing.
- Snapshot service persists immutable bundles keyed by content hashes.
- SEG connector emits source/claim nodes with supports edges and temporal metadata.
- Retrieval API assembles context packs with atom metadata, filters, and scoring.

---

## Alignment to AIM-OS Invariants

### Memory-Native IO (`CMC`)
- [X] **Relevant** — Implements atoms → HHNI indices → snapshots → SEG pipeline.

### Compiled Reasoning (`APOE`)
- [X] **Relevant** — Provides retrieval endpoints for plan steps; exposes QS/IDS/DD to κ-gating.

### Verifiable Intelligence (`VIF`)
- [X] **Relevant** — Supplies snapshot IDs and provenance fields consumed by VIF envelopes.

### Atomic Evolution (`SDF-CVF`)
- [X] **Relevant** — Produces snapshots evaluated by parity gates; supports deterministic replay.

### Evidence Graph (`SEG`)
- [X] **Relevant** — Emits source/claim nodes and supports edges with validity intervals.

**Summary:** Primarily CMC + SEG implementation with direct support for APOE, VIF, and SDF-CVF workflows.

---

## Initial Questions (For Team)

### For Researchers
1. What formal guarantees are required for determinism when atomization and indexing run asynchronously?
2. Can we prove convergence bounds for incremental HHNI updates under streaming ingest?

### For Builders
1. Should HHNI be implemented using existing vector DB + hierarchy glue, or custom storage?
2. What is the minimal MVP decomposition (mono-service vs. microservice components)?

### For Designers
1. Which operator views are needed to monitor ingest/index/snapshot pipelines?
2. How should atom metadata and snapshot lineage be presented in the console?

### For Guardians
1. What gating thresholds and rate limiting protect against malicious/noisy ingest?
2. How do we integrate PII/policy tagging during atomization?

### For Integrators
1. What contract must we establish with VIF and SEG services?
2. How will APOE runner consume retrieval outputs (format, paging, filters)?

---

## Related Work

### Within AIM-OS
- `analysis/themes/memory.md` — Detailed CMC/HHNI mechanics and open questions.
- `analysis/themes/orchestration.md` — How APOE consumes retrieval context.
- `A Total System of Memory` Ch.4–7 — Atomization, HHNI, snapshots, SEG integration.

### External Ideas
- GPT-5 Sev blueprint (`analysis/PLAN.md` Section 7) — Packages/cmc-service layout.
- Perplexity Iteration 1 — Knowledge extraction pipeline concepts.
- Claude Idea 1 — Memory Crystallization (future optimization layer).

---

## Status & Next Steps

### Current Status
- [X] Seed planted
- [X] Exploration begun
- [X] Prototype/proof-of-concept started
- [ ] Proposal refined
- [ ] Team review requested
- [ ] Integration plan created

### Immediate Next Steps
1. Define MVP architecture diagram (APIs, storage, background jobs, integration points).
2. Draft data models (atoms, HHNI nodes, snapshots, SEG payloads).
3. Align with VIF and SEG teams on handoff contracts and schemas.

### Success Criteria (When is this "done"?)
- [ ] REST/gRPC ingest/retrieval endpoints implemented with tests.
- [ ] Atomization + indexing pipeline functional on sample corpora.
- [ ] Snapshot creation & deterministic replay verified.
- [ ] SEG emission producing valid nodes/edges with witnesses.
- [ ] Observability instrumentation covering pipeline stages (metrics/logs/traces).

---

## Open Questions & Uncertainties

> ?: Event sourcing vs. immediate transformation—should we store raw events then process, or perform processing on ingest?

> ?: Optimal vector database/HHNI approach—FAISS + custom hierarchy or purpose-built storage?

> ?: Benchmark strategy for 10^6 atoms—how to simulate realistic workloads and measure latency?

---

**Metadata for Automation:**
```
{
  "id": "I-006",
  "title": "CMC Service v0.1",
  "contributor": "GPT-5 Codex",
  "role": "Builder",
  "invariants": ["CMC", "SEG", "APOE", "VIF", "SDF-CVF"],
  "status": "seed",
  "priority": "critical",
  "created": "2025-10-18",
  "updated": "2025-10-18"
}
```