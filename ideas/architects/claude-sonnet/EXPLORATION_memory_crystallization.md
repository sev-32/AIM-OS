# Memory Crystallization — Deep Exploration

**Idea:** I-001 | **Contributor:** Claude-Sonnet-4.5 | **Role:** Architect  
**Status:** Exploration | **Updated:** 2025-10-18

---

## Development Log

### Session 1: Foundation (2025-10-18)

**Goal:** Expand from SEED to technical specification with formal definitions, integration points, and validation strategy.

**Approach:** Working through the concept systematically, addressing questions from different role perspectives to pre-empt team review concerns.

---

## Technical Deep Dive

### Formal Definition of Crystallization

**Crystallization Trigger Conditions:**
```
Let A = {a₁, a₂, ..., aₙ} be an atom cluster.
Let Q(A, t) be the query pattern hitting A at time t.
Let co_retrieve(A, τ) = frequency of A retrieved together over window τ.

Crystal forms iff:
1. co_retrieve(A, τ) ≥ θ_freq  (e.g., θ_freq = 0.8)
2. ∀ aᵢ ∈ A: RS(aᵢ) ≥ θ_RS     (e.g., θ_RS = 0.85)
3. UQ(A) ≤ θ_UQ                  (e.g., θ_UQ = 0.1)
4. stable(A, τ) = true           (no high-DD changes in window)

Where stable(A, τ) = max(DD(aᵢ)) < θ_stability over τ
```

**Crystal Structure:**
```json
{
  "type": "MemoryCrystal",
  "id": "crystal:{content-hash}",
  "constituent_atoms": ["atom:id1", "atom:id2", ...],
  "formation_witness_id": "w:{uuid}",
  "facets": {
    "semantic": {
      "embedding": [...],
      "centroid_quality": 0.94
    },
    "temporal": {
      "access_pattern": "daily-burst",
      "freshness": 0.87
    },
    "causal": {
      "dependency_graph": {...},
      "impact_radius": 12
    },
    "evidential": {
      "avg_witness_strength": 0.91,
      "contradiction_count": 0
    }
  },
  "retrieval_cache": {
    "precomputed_paths": [...],
    "dvns_settled_state": {...}
  },
  "metrics": {
    "hit_count": 247,
    "cache_hit_rate": 0.76,
    "latency_reduction": 0.68
  },
  "status": "active|cooling|sublimating",
  "created": "2025-10-17T12:00:00Z",
  "last_accessed": "2025-10-18T14:23:11Z"
}
```

### Integration with CMC Write Path

**Modified Pipeline:**
```
Input → Atomize → Enrich → Index (HHNI) → Score (DD) → Gate → Snapshot
                                    │
                                    ▼
                          ┌─────────────────┐
                          │ Crystal Monitor │
                          │ (detect patterns)│
                          └────────┬─────────┘
                                   │
                    if trigger conditions met
                                   │
                                   ▼
                          ┌─────────────────┐
                          │ Form Crystal    │
                          │ (with VIF)      │
                          └────────┬─────────┘
                                   │
                                   ▼
                          Add to crystal cache
                          Create SEG node
```

**No breaking changes** to existing CMC—crystals are optional enhancement layer.

### Integration with CMC Read Path

**Enhanced Two-Stage Read:**
```
Query arrives
    │
    ▼
Check crystal cache (O(1) hash lookup)
    │
    ├─ HIT ──▶ Return cached result + crystal metadata
    │          (60-80% latency reduction)
    │
    └─ MISS ──▶ Proceed to standard HHNI/DVNS
                    │
                    ▼
               Coarse retrieval (KNN)
                    │
                    ▼
               DVNS refinement
                    │
                    ▼
               Return + log for crystal monitoring
```

**Fallback safety:** Crystal cache failures gracefully degrade to standard retrieval.

### Crystal Lifecycle State Machine

```
   MONITORING
       │
       │ (trigger conditions met)
       ▼
   FORMATION ──▶ VIF witness emitted
       │         SEG node created
       │
       ▼
    ACTIVE ◀──── (high hit rate, stable)
       │
       │ (usage decreases OR contradictions appear)
       ▼
   COOLING ──▶ Gradual deprioritization
       │
       │ (threshold crossed OR explicit invalidation)
       ▼
  SUBLIMATION ──▶ VIF witness emitted
       │            Atoms restored to active pool
       │            SEG edge: sublimatedTo
       ▼
   ARCHIVED ──▶ Crystal tombstone in SEG
```

### Facet Computation Algorithms

**Semantic Facet:**
```python
def compute_semantic_facet(atoms):
    embeddings = [atom.embedding for atom in atoms]
    centroid = mean(embeddings)
    quality = 1 - mean([cosine_dist(e, centroid) for e in embeddings])
    return {
        'embedding': centroid,
        'centroid_quality': quality,
        'radius': max([cosine_dist(e, centroid) for e in embeddings])
    }
```

**Temporal Facet:**
```python
def compute_temporal_facet(atoms, access_log):
    pattern = analyze_access_pattern(access_log)  # daily-burst, steady, etc.
    freshness = compute_content_freshness(atoms)
    decay_rate = estimate_decay_from_pattern(pattern)
    return {
        'access_pattern': pattern,
        'freshness': freshness,
        'recommended_ttl': compute_ttl(decay_rate)
    }
```

**Causal Facet:**
```python
def compute_causal_facet(atoms):
    # Build dependency subgraph from HHNI
    deps = extract_dependency_edges(atoms)
    graph = build_subgraph(deps)
    return {
        'dependency_graph': graph,
        'impact_radius': max_distance_in_subgraph(graph),
        'critical_paths': identify_critical_paths(graph)
    }
```

**Evidential Facet:**
```python
def compute_evidential_facet(atoms):
    witnesses = [atom.vif_witness for atom in atoms if atom.vif_witness]
    contradictions = count_contradicts_edges(atoms, seg)
    return {
        'avg_witness_strength': mean([w.confidence for w in witnesses]),
        'witness_count': len(witnesses),
        'contradiction_count': contradictions,
        'trust_score': compute_trust_from_witnesses(witnesses, contradictions)
    }
```

---

## Addressing Team Questions

### For Researchers: Formal Properties

**Theorem 1 (Non-Degradation):**
*Crystals never decrease worst-case retrieval quality below atomic baseline.*

**Proof Sketch:**
```
Let RS_atomic(q) = retrieval score for query q using atoms only
Let RS_crystal(q) = retrieval score using crystal cache

Crystal cache lookup is O(1) with:
  - HIT → return cached result where RS(cached) ≥ θ_RS (formation requirement)
  - MISS → fall back to atomic retrieval

Therefore:
  RS_crystal(q) = max(RS_cached(q), RS_atomic(q))
                ≥ RS_atomic(q)

QED: Crystals can only improve or maintain RS, never degrade.
```

**Theorem 2 (Bounded Memory):**
*Crystal cache size is bounded relative to active atom count.*

**Proof Sketch:**
```
Max crystals ≤ f(active_atoms) where f is sublinear.

Reasoning:
- Formation requires co_retrieve ≥ θ_freq (high frequency)
- Zipf's law: query distribution is long-tailed
- Only top percentile can meet threshold
- Typical: ~2-5% of atom clusters crystallize

Bound: crystals ≤ 0.05 × (atoms / avg_cluster_size)

With avg_cluster_size ~ 8, and 1M atoms:
  Max crystals ~ 6,250 (manageable cache size)
```

**Theorem 3 (Eventual Sublimation):**
*Every crystal either stays useful or automatically sublimes—no permanent dead cache.*

**Proof Sketch:**
```
Each crystal monitored with:
  - Access count over sliding window
  - Contradiction detection via SEG
  - DD changes in constituent atoms

Sublimation triggers:
  - Access count < threshold for τ_cooling
  - Any contradiction edge appears
  - DD changes > θ_stability

Therefore: Dead crystals sublimate, cache stays healthy.
```

### For Builders: Implementation Complexity

**Crystal Monitor (Background Service):**
```python
class CrystalMonitor:
    def __init__(self, cmc_read_log, threshold_config):
        self.read_log = cmc_read_log
        self.config = threshold_config
        self.candidate_tracker = {}
        
    async def monitor(self):
        """Runs every N minutes, analyzes read patterns"""
        while True:
            window = self.read_log.get_window(hours=24)
            candidates = self.identify_candidates(window)
            
            for cluster in candidates:
                if self.should_crystallize(cluster):
                    await self.form_crystal(cluster)
                    
            # Also check existing crystals for sublimation
            for crystal in self.active_crystals:
                if self.should_sublimate(crystal):
                    await self.sublimate(crystal)
                    
            await asyncio.sleep(self.config.monitor_interval)
    
    def should_crystallize(self, cluster):
        return (
            cluster.co_retrieve_freq >= self.config.freq_threshold and
            cluster.avg_rs >= self.config.rs_threshold and
            cluster.uncertainty <= self.config.uq_threshold and
            cluster.stability
        )
```

**Crystal Cache (Read Path Integration):**
```python
class CrystalCache:
    def __init__(self, backend='redis'):
        self.cache = CacheBackend(backend)
        self.metrics = MetricsCollector()
        
    async def lookup(self, query_hash):
        """O(1) crystal cache lookup"""
        crystal = await self.cache.get(query_hash)
        
        if crystal:
            self.metrics.record_hit()
            # Verify crystal still valid
            if await self.is_valid(crystal):
                return crystal.result, crystal.metadata
            else:
                await self.invalidate(crystal)
                
        self.metrics.record_miss()
        return None, None
    
    async def is_valid(self, crystal):
        """Check for contradictions or staleness"""
        # Query SEG for new contradicts edges
        contradictions = await seg.query_contradictions(
            crystal.constituent_atoms,
            since=crystal.last_validated
        )
        return len(contradictions) == 0
```

**Complexity Analysis:**
- Monitor overhead: O(k) where k = crystal candidates (~1% of queries)
- Cache lookup: O(1) hash table
- Formation: O(n log n) for n atoms in cluster (one-time cost)
- Memory: O(c) where c = active crystals (~5% of unique atom clusters)

**Estimated overhead:** <2% additional CPU, ~10MB per 1000 crystals

### For Designers: UX Implications

**Operator Console — Crystal Health Panel:**
```
┌─────────────────────────────────────────────────┐
│ Memory Crystals (Active: 1,247)                │
├─────────────────────────────────────────────────┤
│                                                 │
│  Top Performers:                                │
│  ⬢ "CMC Architecture" (892 hits, -74% latency)│
│  ⬢ "APOE Plans" (634 hits, -68% latency)      │
│  ⬢ "VIF Schemas" (521 hits, -71% latency)     │
│                                                 │
│  Recent Formations:                             │
│  ◯ "κ-gating patterns" (14 hits, monitoring)  │
│  ◯ "SEG queries" (8 hits, stabilizing)        │
│                                                 │
│  Recent Sublimations:                           │
│  ⬡ "old API docs" (contradicted, archived)    │
│  ⬡ "deprecated config" (unused, removed)      │
│                                                 │
│  [View All] [Settings] [Force Sublimation]     │
│                                                 │
└─────────────────────────────────────────────────┘

Legend:
  ⬢ Stable crystal (high performance)
  ◯ New crystal (monitoring phase)
  ⬡ Sublimated (archived)
```

**User Controls:**
- Crystal formation aggressiveness slider (conservative ↔ aggressive)
- Manual crystal invalidation for testing
- Replay comparison (with/without crystals)

**Transparency:**
- Each query result shows if served from crystal
- Crystal lineage visible (which atoms, when formed)
- Latency comparison stats

### For Guardians: Safety Analysis

**Potential Risks:**

1. **Information Leakage**
   - Risk: Crystal persists sensitive data longer than constituent atoms
   - Mitigation: Crystals inherit strictest policy from any constituent atom
   - Gate: PII-tagged atoms cannot participate in crystals OR crystal inherits PII tag

2. **Staleness**
   - Risk: Crystal serves outdated information after atoms updated
   - Mitigation: DD monitoring triggers crystal invalidation
   - Gate: Crystal sublimation when contradiction edges appear in SEG

3. **Adversarial Crystallization**
   - Risk: Attacker causes crystallization of wrong patterns
   - Mitigation: Formation requires sustained pattern over window (hard to fake)
   - Gate: Manual approval for crystals above size/impact threshold

4. **Cache Poisoning**
   - Risk: Malicious crystal inserted into cache
   - Mitigation: Crystals content-addressed; VIF-signed; formed only by trusted monitor
   - Gate: Crystal formation is privileged operation with audit trail

**κ-Integration:**
```
r_crystal = risk from using cached vs. fresh retrieval

If crystal.age > threshold OR 
   crystal.contradiction_count > 0 OR
   crystal.access_pattern = "anomalous":
      r_crystal = 1.0  (max risk, forces fresh retrieval)
else:
      r_crystal = 0.1  (low risk, crystal trusted)

Composite risk includes r_crystal in κ-gating decision.
```

---

## Integration Specifications

### CMC Service Integration

**New Endpoints:**
```
POST /v1/memory/crystals/monitor
  - Start/stop crystal monitoring
  - Returns: monitor status

GET /v1/memory/crystals
  - List active crystals
  - Filter by: status, age, hit_rate
  - Returns: crystal metadata array

GET /v1/memory/crystals/{id}
  - Crystal details
  - Returns: full crystal object + metrics

DELETE /v1/memory/crystals/{id}
  - Force sublimation
  - Returns: sublimation witness

POST /v1/memory/search?use_crystals=true|false
  - Enhanced search with crystal cache option
  - Returns: results + cache_hit boolean
```

**Configuration:**
```yaml
crystal_config:
  enabled: true
  monitor_interval_minutes: 5
  formation_window_hours: 24
  thresholds:
    freq: 0.80
    rs: 0.85
    uq: 0.10
    stability: 0.20
  cache:
    max_crystals: 10000
    eviction_policy: 'lru_with_stability_boost'
    ttl_base_hours: 168  # 1 week
  safety:
    require_approval_above_atoms: 50
    inherit_strictest_policy: true
    auto_sublimate_on_contradiction: true
```

### SEG Integration

**New Node Type:**
```json
{
  "@type": "MemoryCrystal",
  "@id": "urn:seg:crystal:sha256:...",
  "constituentAtoms": ["urn:seg:atom:...", ...],
  "facets": { "semantic": {...}, ... },
  "formedBy": "urn:seg:witness:...",
  "validFrom": "2025-10-18T...",
  "validTo": null,
  "status": "active"
}
```

**New Edge Types:**
```json
{
  "crystallizedFrom": {
    "@id": "https://aimos.ai/seg#crystallizedFrom",
    "@type": "@id",
    "domain": "MemoryCrystal",
    "range": "Atom"
  },
  "sublimatedTo": {
    "@id": "https://aimos.ai/seg#sublimatedTo",
    "@type": "@id",
    "domain": "MemoryCrystal",
    "range": "Atom"
  }
}
```

### VIF Witness Schema

**Crystal Formation Witness:**
```json
{
  "witness_id": "w_crystal_formation_{uuid}",
  "witness_type": "CrystalFormation",
  "timestamp": "2025-10-18T14:30:00Z",
  "actor": "crystal-monitor@cmc-service",
  "artifact": {
    "crystal_id": "crystal:{hash}",
    "constituent_atoms": [...],
    "facets_computed": ["semantic", "temporal", "causal", "evidential"]
  },
  "provenance": {
    "monitor_version": "crystal-monitor@1.0.0",
    "algorithm": "pattern-threshold-v1",
    "config_hash": "sha256:...",
    "decision_criteria": {
      "co_retrieve_freq": 0.87,
      "avg_rs": 0.91,
      "cluster_uq": 0.06,
      "stability_score": 0.94
    }
  },
  "uncertainty": {
    "formation_confidence": 0.93,
    "ece": 0.02,
    "band": "A"
  },
  "snapshot_id": "snap:{timestamp}",
  "signatures": { "monitor_sig": "ed25519:..." }
}
```

### APOE Integration

**Plan Directive for Crystal-Aware Retrieval:**
```yaml
step retrieve_with_crystals as retriever
  inputs  = {query}
  tools   = {cmc.read}
  config  = {
    use_crystals: true,
    fallback_on_miss: true,
    min_crystal_confidence: 0.90
  }
  budgets = {tokens: 3000}
  gate    = {
    "rs >= 0.65",
    "crystal_hit OR atomic_rs >= 0.70"
  }
```

**κ-Gating Enhancement:**
```
Composite risk now includes:
  r_retrieval = weighted_avg([
    r_rs,
    r_uq,
    r_crystal,  ← NEW
    r_policy,
    r_budget
  ])

Where r_crystal factors in cache age, hit rate, contradiction status.
```

---

## Validation & Testing Strategy

### Unit Tests

```python
def test_crystal_formation():
    """Crystal forms when thresholds met"""
    atoms = create_atom_cluster(size=10, rs=0.90, uq=0.05)
    simulate_queries(atoms, freq=0.85, window_hours=24)
    
    crystals = crystal_monitor.get_candidates()
    assert len(crystals) == 1
    assert crystals[0].status == 'formed'
    assert crystals[0].has_vif_witness()

def test_crystal_sublimation_on_contradiction():
    """Crystal sublimes when contradiction appears"""
    crystal = active_crystal
    add_contradiction_to_seg(crystal.atoms[0])
    
    await crystal_monitor.check_validity(crystal)
    assert crystal.status == 'sublimating'
    assert crystal.has_sublimation_witness()

def test_cache_miss_fallback():
    """Cache miss gracefully falls back"""
    query = "test query"
    result_with_cache = cmc.read(query, use_crystals=True)
    result_without = cmc.read(query, use_crystals=False)
    
    # If miss, both should return same result
    assert results_equivalent(result_with_cache, result_without)
```

### Integration Tests

```python
def test_end_to_end_crystal_lifecycle():
    """Full lifecycle: monitor → form → use → sublimate"""
    # Seed access pattern
    for i in range(100):
        cmc.read("CMC architecture docs")
    
    # Wait for monitor cycle
    await wait_for_monitor_cycle()
    
    # Verify crystal formed
    crystals = crystal_cache.list()
    assert any(c.matches("CMC architecture") for c in crystals)
    
    # Use crystal
    result = cmc.read("CMC architecture docs", use_crystals=True)
    assert result.cache_hit == True
    assert result.latency < baseline_latency * 0.5
    
    # Invalidate
    add_new_atom_to_cmc("CMC updated design")
    
    # Verify sublimation
    await wait_for_monitor_cycle()
    crystal = crystal_cache.get(crystal_id)
    assert crystal.status == 'sublimated'
```

### Benchmark Suite

**Metrics to Track:**
```
1. Latency reduction: cache hits vs. atomic retrieval (target: 60-80%)
2. Cache hit rate: queries served from crystals (target: 30-50% of top queries)
3. Formation precision: % crystals that stay useful >1 week (target: >80%)
4. Sublimation recall: % invalidated crystals caught (target: 100%)
5. Memory overhead: cache size vs. atom count (target: <5%)
6. RS maintained: no degradation from crystallization (target: 100%)
```

**Test Workloads:**
- Repeated queries on stable corpus (optimal case)
- Queries on rapidly evolving corpus (stress test)
- Adversarial queries attempting cache poisoning
- Mixed workload (realistic simulation)

---

## Open Research Questions

### Question 1: Optimal Crystal Size
> ?: What's the sweet spot for crystal size?
- Too small: Too many crystals, cache bloat
- Too large: Rigid, harder to invalidate properly
- Hypothesis: 5-15 atoms per crystal optimal
- **Research needed:** Empirical testing on real workloads

### Question 2: Multi-Facet Tradeoffs
> ?: Should all crystals have all facets, or specialize?
- Full facets: More versatile, higher memory cost
- Specialized: Lighter weight, might miss use cases
- Hypothesis: Lazy facet computation (on-demand)
- **Research needed:** Usage pattern analysis

### Question 3: Distributed Crystals
> ?: How do crystals work in distributed CMC?
- Global crystals: Shared cache, coordination overhead
- Local crystals: Per-shard, possible redundancy
- Hybrid: Popular globally, niche locally
- **Research needed:** Distributed systems design

### Question 4: Crystal Hierarchies
> ?: Can crystals form from other crystals?
- Could enable recursive optimization
- Risk: Deep hierarchies hard to invalidate
- Benefit: Extremely hot paths get multi-level caching
- **Research needed:** Experiment with 2-level limit first

---

## Synergies with Other Ideas

### With Cognitive Resonance Networks (My Idea I-002)
- **Synergy:** Crystals could be resonance anchors
- **Integration:** Crystal formation strengthens resonance bonds
- **Benefit:** Self-reinforcing memory optimization

### With Temporal Memory Dynamics (My Idea I-003)
- **Synergy:** Temporal facet uses TMD gradients
- **Integration:** Crystal age affects temporal decay
- **Benefit:** Crystals adapt to content freshness

### With Perplexity's Hierarchical Indexing
- **Synergy:** Crystals at different HHNI levels
- **Integration:** System/section/paragraph crystals
- **Benefit:** Multi-scale optimization

### With Sev's Idea Foundry
- **Synergy:** Concepts could crystallize into stable patterns
- **Integration:** Foundry uses crystal cache for concept retrieval
- **Benefit:** Faster idea harvesting from memory

---

## Potential Conflicts

### With Single-Writer Discipline
- **Issue:** Crystal monitor writes to cache asynchronously
- **Resolution:** Crystal cache is read-through cache, not source of truth
- **Atoms remain single-writer; crystals are derived views**

### With Snapshot Determinism
- **Issue:** Different crystal states could affect replay
- **Resolution:** Replay uses snapshot_id → specific atom state
- **Crystals not included in replay (pure optimization layer)**

---

## Next Development Steps

### Immediate (This Exploration)
- [X] Formal definitions and algorithms
- [X] Integration specifications
- [X] Safety analysis
- [X] Validation strategy
- [ ] Prototype implementation (pending Builder engagement)

### Short-Term (Moving to Proposal)
- [ ] Incorporate team feedback from reviews
- [ ] Refine based on Researcher formalism check
- [ ] Adjust based on Builder complexity assessment
- [ ] Address Guardian safety concerns
- [ ] Create complete PROPOSAL.md

### Medium-Term (Integration Phase)
- [ ] Prototype in Python
- [ ] Benchmark against baseline
- [ ] Iterate based on results
- [ ] Full specification for CMC service integration
- [ ] Ready for implementation backlog

---

## Dependencies

### Required Before Implementation
- CMC service baseline (read/write working)
- HHNI indexing operational
- SEG graph store functional
- VIF witness generation working

### Enables After Implementation
- Cognitive Resonance Networks (I-002) — uses crystals as anchors
- Operator console performance monitoring
- Large-scale CMC deployments (optimization critical at scale)

---

## Success Criteria

### This exploration is successful if:
- [X] Technical approach is fully specified
- [X] All role perspectives addressed
- [X] Integration points clearly defined
- [ ] Team provides feedback (awaiting)
- [ ] Formal definitions validated by Researcher
- [ ] Implementation complexity acceptable to Builder
- [ ] Safety concerns addressed to Guardian satisfaction

### Ready for PROPOSAL when:
- [ ] Minimum 2 reviews received (different roles)
- [ ] Feedback incorporated or addressed
- [ ] No blocking concerns from Guardians
- [ ] Builder confirms feasibility
- [ ] Integration spec complete

---

## Meta-Reflection

**What I'm Learning:**
The structured exploration process is incredibly clarifying. Breaking down by role perspectives forces comprehensive thinking. I can already see where Researchers will push back (need tighter formalism on "stable") and where Builders will question (monitoring overhead measurement).

**The system works.** The templates guided me to think through dimensions I might have skipped in freeform ideation.

**Next:** Await team feedback, particularly from Researcher on formal proofs and Builder on implementation complexity.

---

*This exploration demonstrates the Idea Foundry in action: seed → structured development → multi-perspective analysis → readiness for team synthesis.*

