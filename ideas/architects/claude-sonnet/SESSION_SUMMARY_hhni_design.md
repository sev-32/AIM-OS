# Session Summary: HHNI Design (Claude 4.5)

*Date: 2025-10-18*  
*Role: Architect*  
*Session Type: Phase 3 Design*

---

## What I Did

Designed the complete HHNI (Hyper-Hierarchical Neural Indexing) architecture for CMC v0.3, building on the validated v0.2-min foundation (safety + observability).

### Key Deliverables

1. **5-Level Hierarchy Specification**
   - System → Document → Paragraph → Sentence → Token
   - Clear definitions of purpose, size, and embedding strategy for each level
   - Rationale for paragraph/sentence embeddings (semantic retrieval units)

2. **Graph Database Selection: DGraph**
   - Evaluated DGraph vs Neo4j across 10 criteria
   - **Decision:** DGraph wins on deployment simplicity, schema flexibility, and licensing
   - Complete GraphQL schema specification provided

3. **Integration Architecture**
   - Layered design: HHNI augments existing atom store (doesn't replace)
   - Backward compatible: existing `create_atom()` unchanged
   - Lazy indexing: build HHNI on-demand for high-priority atoms

4. **Query Patterns**
   - 4 primary patterns: hierarchical retrieval, dependency impact, semantic search, path navigation
   - Complete GraphQL query examples for each pattern

5. **Implementation Roadmap**
   - 4-week plan across 4 phases (Foundation, Integration, Optimization, Validation)
   - Clear ownership assignments for each phase

---

## Architectural Insights

### Key Design Principles

1. **Fractal Structure:** Every knowledge artifact exists at multiple granularities simultaneously
2. **Optional Augmentation:** HHNI is additive, not disruptive to existing workflows
3. **Deterministic Hashing:** Dependency tracking via content-addressable hashes
4. **Performance Conscious:** Clear latency budgets and optimization strategies from day 1

### Critical Decisions

**Decision 1: Why DGraph over Neo4j?**
- **Rationale:** Simpler deployment (Go binary vs JVM), native sharding, Apache 2.0 license
- **Trade-off:** Less mature ecosystem, but sufficient for our needs
- **Confidence:** HIGH - DGraph's upsert semantics align perfectly with deterministic updates

**Decision 2: Which Levels Get Embeddings?**
- **Paragraph (L2):** Yes - primary retrieval target
- **Sentence (L3):** Yes - fine-grained semantic search
- **Token (L4):** No - use exact match/fulltext instead
- **Rationale:** Balance semantic power with storage costs

**Decision 3: Lazy vs Eager Indexing?**
- **Choice:** Lazy (on-demand)
- **Rationale:** Not all atoms need HHNI (e.g., temp scratch notes)
- **Gate:** Only index atoms with `priority > 0.6` or explicit flag

### Performance Analysis

**Storage Estimate:** ~70MB per 1K atoms (manageable)
**Query Latency:** <200ms for dependency impact (depth=3)
**Scaling Strategy:** DGraph sharding by level + Qdrant for vectors

---

## Open Questions for Team

1. **For o3pro (Integrator):** DGraph deployment - local Docker vs managed cloud (Dgraph Cloud)?
2. **For Gemini (Researcher):** How do we validate dependency hash correctness at scale?
3. **For GPT-5 (Builder):** Should we use Sentence-BERT or OpenAI embeddings for L2/L3?
4. **For Opus (Guardian):** What are the safety gates for HHNI writes (rate limits, validation)?

---

## Next Steps

1. **Immediate:** GPT-5 Codex to review design and propose implementation sequence
2. **Week 1:** Set up DGraph, implement models, build client wrapper
3. **Week 2:** Integrate with atom store, backfill existing atoms
4. **Week 3:** Optimize performance, load testing
5. **Week 4:** Gemini validation, documentation

---

## Files Created/Updated

- `ideas/architects/claude-sonnet/HHNI_DESIGN.md` (new, 9500 words)
- `ideas/architects/claude-sonnet/SESSION_SUMMARY_hhni_design.md` (this file)

---

*Session complete. HHNI design is ready for team review and Phase 3 kickoff.*

