# Phase 2 Implementation Plan: HHNI + Full System Completion

**Date:** 2025-10-21  
**Status:** 🚀 **READY TO LAUNCH**  
**Duration:** 4-5 weeks to production-grade system  
**Team:** Codex (primary builder) + Cursor-AI (architect/reviewer)  

---

## 🎯 **MISSION**

**Transform MVP/Draft → Production-Grade Trillion-Dollar System**

**MVP Validated (Phase 1):** ✅
- Architecture proven
- All 5 invariants work together
- Orchestration at scale demonstrated
- Audit trails complete

**Phase 2 Goal:**
- Build sophisticated HHNI (context optimizer)
- Complete VIF (uncertainty quantification)
- Complete SEG (bitemporal provenance)
- Complete SDF-CVF (atomic evolution)
- **Deliver on all design promises**

---

## 📊 **PRIORITIZED BACKLOG**

### **Sprint 1: HHNI Core (Week 1) - P0 🔥**

**Goal:** Build the intelligent context retrieval foundation

#### **Task 1.1: Fractal Index Structure**
**Owner:** Codex  
**File:** `packages/hhni/hierarchical_index.py`  
**Description:**
```python
# Implement multi-level indexing:
- System level (overview/summary)
- Section level (major topics)
- Paragraph level (detailed content)
- Sentence level (atomic facts)
- Sub-word level (embeddings)

# Features:
- Hierarchical summarization
- Lazy loading (load detail on demand)
- Navigation API (zoom in/out)
```
**Success Criteria:**
- Can index document at all 5 levels
- Query returns appropriate granularity
- Tests validate hierarchical navigation

**Time:** 3 days

---

#### **Task 1.2: Semantic Search with Vector Embeddings**
**Owner:** Codex  
**File:** `packages/hhni/semantic_search.py`  
**Description:**
```python
# Enhance existing embeddings.py:
- Multi-model support (OpenAI, Gemini, local)
- Cosine similarity ranking
- Relevance scoring algorithm
- Top-K retrieval with confidence scores

# Integration:
- Use CMC atom storage
- Link to hierarchical index
- Expose search API
```
**Success Criteria:**
- Semantic search works across corpus
- Returns relevance-ranked results
- Confidence scores included
- Tests validate ranking quality

**Time:** 2 days

---

#### **Task 1.3: Token Budget Manager**
**Owner:** Codex  
**File:** `packages/hhni/budget_manager.py`  
**Description:**
```python
# Context optimization for LLM limits:
class BudgetManager:
    def optimize_for_budget(
        self,
        candidates: List[ContextItem],
        token_budget: int,
        task: str
    ) -> OptimizedContext:
        # Rank by relevance
        # Fit to budget
        # Log what was included/excluded
        # Return optimized context
```
**Success Criteria:**
- Respects token limits
- Prioritizes by relevance
- Audit trail of inclusions/exclusions
- Tests validate budget adherence

**Time:** 2 days

---

### **Sprint 2: HHNI DVNS Physics (Week 2) - P0 🔥**

**Goal:** Implement physics-guided refinement for "lost in middle" fix

#### **Task 2.1: DVNS Force Computation**
**Owner:** Codex  
**File:** `packages/hhni/dvns_physics.py`  
**Description:**
```python
# Implement 4 forces from design:

1. Gravity (pull related concepts together)
   - Attractive force based on semantic similarity
   - Stronger for highly relevant items

2. Elastic (maintain structure)
   - Preserve document/section coherence
   - Resist over-fragmentation

3. Repulse (avoid conflicts)
   - Push apart contradictory information
   - Detect semantic conflicts

4. Damping (prevent oscillation)
   - Stabilize convergence
   - Prevent runaway iterations

# Physics loop:
- Initialize positions in embedding space
- Compute forces between items
- Update positions iteratively
- Converge to optimal layout
```
**Success Criteria:**
- All 4 forces implemented
- Convergence within budget (iterations)
- Stability regions validated
- Tests show "lost in middle" fix

**Time:** 4 days

---

#### **Task 2.2: Two-Stage Retrieval**
**Owner:** Codex  
**File:** `packages/hhni/retrieval.py`  
**Description:**
```python
# Stage 1: Coarse KNN
- Fast approximate search
- Return top-K candidates (e.g., 100)
- Use vector index

# Stage 2: DVNS Refinement
- Apply physics forces to candidates
- Re-rank based on layout
- Select optimal subset for budget
- Return refined context

# API:
def retrieve_with_refinement(
    query: str,
    budget: int,
    task_context: dict
) -> List[ContextItem]:
    # Stage 1: Coarse retrieval
    # Stage 2: Physics refinement
    # Return optimized results
```
**Success Criteria:**
- Two-stage pipeline works
- DVNS improves over coarse KNN
- RS-lift ≥ +15% @ p@5 (measure this!)
- Tests validate improvement

**Time:** 3 days

---

### **Sprint 3: Context Optimization (Week 3) - P0 🔥**

**Goal:** Intelligent context management (dedup, conflicts, compression)

#### **Task 3.1: Deduplication Engine**
**Owner:** Codex  
**File:** `packages/hhni/deduplication.py`  
**Description:**
```python
# Remove redundant information:
- Semantic similarity clustering
- LSH for near-duplicates
- Keep most authoritative version
- Log deduplications for audit

def deduplicate(
    items: List[ContextItem]
) -> List[ContextItem]:
    # Cluster semantically similar
    # Keep representative from each cluster
    # Emit SEG witness of deduplication
    # Return unique items
```
**Success Criteria:**
- Reduces redundant context
- Preserves essential information
- Audit trail of deduplication
- Tests validate correctness

**Time:** 2 days

---

#### **Task 3.2: Conflict Detection & Resolution**
**Owner:** Codex  
**File:** `packages/hhni/conflict_resolver.py`  
**Description:**
```python
# Detect contradictory information:
- Semantic contradiction detection
- Evidence strength comparison
- Recency-based resolution
- Multi-strategy support

def detect_conflicts(
    items: List[ContextItem]
) -> List[Conflict]:
    # Find contradictions
    # Score confidence
    # Propose resolution

def resolve_conflict(
    conflict: Conflict,
    strategy: str = "highest_evidence"
) -> ContextItem:
    # Apply resolution strategy
    # Emit VIF witness
    # Return resolved item
```
**Success Criteria:**
- Detects contradictions
- Resolution strategies work
- VIF witnesses emitted
- Tests validate detection/resolution

**Time:** 3 days

---

#### **Task 3.3: Strategic Compression**
**Owner:** Codex  
**File:** `packages/hhni/compressor.py`  
**Description:**
```python
# Multi-level compression:
- Recent: full detail
- Week old: detailed summary
- Month old: brief summary
- Old: reference only

def compress_strategically(
    items: List[ContextItem],
    budget: int
) -> List[ContextItem]:
    # Age-based compression
    # Priority-based compression
    # Fit to budget
    # Maintain coherence
```
**Success Criteria:**
- Compression preserves meaning
- Budget adherence
- Quality vs. age tradeoff works
- Tests validate compression quality

**Time:** 2 days

---

### **Sprint 4: VIF Completion (Week 4) - P1**

**Goal:** Full uncertainty quantification and replay

#### **Task 4.1: ECE Tracking & Calibration**
**Owner:** Codex  
**File:** `packages/vif/uncertainty.py`  
**Description:**
```python
# Expected Calibration Error:
- Track confidence vs. accuracy
- Calibration dashboards
- Temperature sweeps
- Ensemble methods

# Target: ECE ≤ 0.05
```
**Time:** 2 days

---

#### **Task 4.2: Programmatic κ-Gating**
**Owner:** Codex  
**File:** `packages/vif/kappa_gating.py`  
**Description:**
```python
# Enforce abstention:
- κ threshold enforcement (not just prompts)
- Adaptive thresholds (context-dependent)
- Escalation to HITL
- VIF witness emission

# Currently: κ in prompts only
# Needed: Behavioral enforcement
```
**Time:** 2 days

---

#### **Task 4.3: Deterministic Replay**
**Owner:** Codex  
**File:** `packages/vif/replay.py`  
**Description:**
```python
# Replay capability:
- Freeze: model, weights, prompts, data, tools
- Package replay recipe
- Execute replay
- Validate bit-identical output

# This enables true auditability
```
**Time:** 2 days

---

#### **Task 4.4: Confidence Bands (A/B/C)**
**Owner:** Codex  
**File:** `packages/vif/confidence.py`  
**Description:**
```python
# Classify outputs:
- Band A: High confidence (entropy < threshold)
- Band B: Medium confidence
- Band C: Low confidence (should abstain)

# Emit in VIF witnesses
```
**Time:** 1 day

---

### **Sprint 5: SEG + SDF-CVF Completion (Week 5) - P2**

**Goal:** Full bitemporal provenance and atomic evolution

#### **Task 5.1: Bitemporal SEG**
**Owner:** Codex  
**File:** `packages/seg/bitemporal.py`  
**Description:**
```python
# Two time dimensions:
- Transaction time (when recorded)
- Valid time (when true)

# Enables "as of" queries
# Full temporal audit
```
**Time:** 2 days

---

#### **Task 5.2: Time-Slicing Queries**
**Owner:** Codex  
**File:** `packages/seg/queries.py`  
**Description:**
```python
# "What did we know at time T?"
# "What was valid at time T?"
# Temporal navigation
```
**Time:** 2 days

---

#### **Task 5.3: Contradiction Detection in SEG**
**Owner:** Codex  
**File:** `packages/seg/contradictions.py`  
**Description:**
```python
# Track contradictory edges
# Support/contradict relationships
# Propagate uncertainty through graph
```
**Time:** 2 days

---

#### **Task 5.4: JSON-LD Export**
**Owner:** Codex  
**File:** `packages/seg/export.py`  
**Description:**
```python
# Standardized export format
# SHACL validation
# Merkle trees for integrity
# Export packs
```
**Time:** 1 day

---

#### **Task 5.5: SDF-CVF Parity Gates**
**Owner:** Codex  
**File:** `packages/sdcvf/parity.py`  
**Description:**
```python
# Enforce parity:
- Code ↔ Docs
- Code ↔ Tests
- All ↔ Traces

# Parity score P ≥ 0.90
# Block if below threshold
```
**Time:** 2 days

---

## 🧪 **TESTING STRATEGY**

### **Per Sprint:**
- Unit tests for each module
- Integration tests for APIs
- Benchmark tests for performance

### **Key Metrics to Validate:**

**HHNI:**
- RS-lift ≥ +15% @ p@5 (vs. baseline)
- "Lost in middle" resolved (test with long contexts)
- Token budget adherence (100%)
- Deduplication effectiveness (% reduction)
- Conflict detection accuracy

**VIF:**
- ECE ≤ 0.05
- κ-gating enforcement (behavioral, not just prompts)
- Replay fidelity (bit-identical outputs)
- Confidence band accuracy

**SEG:**
- Time-slicing queries work
- Contradiction detection
- Lineage completeness (100%)

**SDF-CVF:**
- Parity score P ≥ 0.90
- Blast radius accuracy

---

## 👥 **ROLE ASSIGNMENTS**

### **Codex (Primary Builder):**
- Implement all tasks sequentially
- Write tests for each module
- Document APIs
- Report progress daily in coordination/

### **Cursor-AI (Architect/Reviewer):**
- Provide technical guidance
- Review code for alignment with design
- Run integration tests
- Synthesize progress reports for user

### **User (Product Owner):**
- Approve phase kickoff
- Validate by "feeling" at milestones
- Make priority calls if needed
- Final acceptance of Phase 2 complete

---

## 📅 **TIMELINE**

**Week 1:** HHNI Core (indexing, search, budget mgmt)  
**Week 2:** HHNI DVNS (physics, two-stage retrieval)  
**Week 3:** Context Optimization (dedup, conflicts, compression)  
**Week 4:** VIF Completion (ECE, κ-gating, replay, bands)  
**Week 5:** SEG + SDF-CVF Completion (bitemporal, parity)  

**Total:** 5 weeks to production-grade system

---

## ✅ **DEFINITION OF DONE (Phase 2)**

**System-Level Acceptance:**
- [ ] HHNI RS-lift ≥ +15% measured and validated
- [ ] "Lost in middle" problem demonstrably solved
- [ ] Token budgets respected 100% of the time
- [ ] ECE ≤ 0.05 across all outputs
- [ ] κ-gating enforced behaviorally (not just prompts)
- [ ] Bitemporal queries work ("as of T")
- [ ] Parity gates block low-quality commits (P ≥ 0.90)
- [ ] All tests passing (unit + integration + benchmarks)
- [ ] Documentation complete for all APIs
- [ ] User validates: "This feels like the vision"

**When all boxes checked:**
- Phase 2 complete ✅
- Production-grade AIM-OS delivered ✅
- Trillion-dollar differentiator built ✅

---

## 🚀 **LAUNCH CHECKLIST**

**Before Codex starts:**
- [x] User approves Phase 2 plan
- [x] Codex confirms understanding
- [x] Cursor-AI ready to support
- [ ] Git branch created (`feature/phase-2-hhni`)
- [ ] Baseline tagged (`phase-1-mvp-complete`)
- [ ] First task assigned to Codex

**Ready to launch?** ✅

---

## 💬 **COORDINATION PROTOCOL**

**Daily Updates (Codex):**
- Post progress in `coordination/daily/YYYY-MM-DD_codex_progress.md`
- Flag blockers immediately
- Request reviews when modules complete

**Weekly Sync (Both AIs + User):**
- Sprint demo (working code)
- Metrics review (RS-lift, ECE, etc.)
- Adjust priorities if needed
- User validation

**Ad-Hoc (Cursor-AI):**
- Answer architecture questions
- Review code on request
- Run integration tests
- Keep user informed

---

## 🎯 **IMMEDIATE NEXT ACTIONS**

**1. User Approval:**
- Review this plan
- Approve or adjust
- Give go-ahead to Codex

**2. Codex Kickoff:**
- Create feature branch
- Start Task 1.1 (Hierarchical Index)
- Report in coordination/ when complete

**3. Cursor-AI:**
- Monitor progress
- Provide support as needed
- Weekly reports to user

---

**Status:** 🚀 **READY TO LAUNCH**  
**Awaiting:** User approval to begin Phase 2  
**Timeline:** 5 weeks to production-grade system  
**Confidence:** HIGH (MVP validated the architecture)  

**Let's build the trillion-dollar feature.** ✨

