# SEG L1: System Overview

**Detail Level:** 1 of 5 (500 words)  
**Context Budget:** ~8k tokens  
**Purpose:** Understand SEG architecture

---

## What Is SEG?

SEG (Shared Evidence Graph) transforms evidence from scattered facts into a queryable knowledge graph with complete temporal provenance. Every claim, source, derivation, and contradiction becomes a node. Every relationship ("supports," "contradicts," "derives," "witnesses") becomes an edge. Bitemporal storage (transaction time + valid time) enables "what was known at time T?" queries. Combined with automatic contradiction detection, JSON-LD export, and SHACL validation, SEG provides the foundation for auditable, traceable, contradiction-aware AI systems.

## The Core Innovation: Evidence as Temporal Knowledge Graph

**Traditional Approach (Scattered Evidence):**
```
File 1: "OAuth2 uses JWT tokens"
File 2: "Our system uses session cookies"
Conflict?: Unknown (no detection)
Provenance?: Unknown (manual search)
Temporal?: Unknown (when was this true?)
```

**SEG Approach (Unified Graph):**
```
Nodes:
- N1: Claim("OAuth2 uses JWT tokens") [created: 2025-01-15, valid: 2025-01-15 → ∞]
- N2: Claim("System uses session cookies") [created: 2025-03-20, valid: 2025-03-20 → ∞]
- N3: Source(VIF_witness_abc123)
- N4: Derivation(APOE_plan_xyz789)

Edges:
- N3 --[witnesses]--> N1 (provenance!)
- N4 --[derives]--> N2 (lineage!)
- N1 <--[contradicts]--> N2 (conflict detected automatically!)

Queries:
- "What authentication methods exist?" → N1, N2
- "Where did N1 come from?" → N3 (VIF witness)
- "What conflicts with N2?" → N1 (contradiction!)
- "What was true on 2025-02-01?" → Only N1 (temporal query!)
```

**This is verifiable, traceable, contradiction-aware knowledge!** ✨

---

## The Five Core Components

### 1. Graph Schema

**Nodes and Edges:**

**Node Types:**
- **Claim:** Factual assertion (evidence)
- **Source:** Where it came from (VIF witness, document, user input)
- **Derivation:** How it was derived (APOE execution, inference chain)
- **Agent:** Who/what created it (human, AI model, system)

**Edge Types:**
- **supports:** Evidence backs up claim
- **contradicts:** Evidence conflicts with claim  
**derives:** Claim produced from other claims
- **witnesses:** VIF witness records claim
- **cites:** Source reference

**Schema:**
```python
@dataclass
class SEGNode:
    id: str                       # Unique node ID
    type: str                     # "claim" | "source" | "derivation" | "agent"
    content: Any                  # Node payload
    created_at: datetime          # Transaction time
    valid_from: datetime          # Valid time start
    valid_to: Optional[datetime]  # Valid time end (None = still valid)

@dataclass
class SEGEdge:
    id: str
    type: str                     # "supports" | "contradicts" | "derives" | etc.
    source_node_id: str
    target_node_id: str
    weight: float = 1.0           # Edge strength
    created_at: datetime
```

---

### 2. Bitemporal Storage

**Two timelines:**

**Transaction Time (TT):** When fact was recorded in system  
**Valid Time (VT):** When fact was true in real world  

**Example:**
```
Fact: "User John has role Admin"
TT: 2025-10-21 (when recorded in SEG)
VT: 2025-10-15 → 2025-10-18 (when it was actually true)

Query: "What was John's role on 2025-10-17?"
Answer: Admin (VT contains 2025-10-17)

Query: "What did we know about John on 2025-10-14?"
Answer: Nothing (TT is after 2025-10-14, fact not yet recorded)
```

**Enables:**
- Temporal queries ("what was known when?")
- Correction without deletion (update VT, preserve TT)
- Full audit trail (every change tracked)

---

### 3. Contradiction Detection

**Automatic conflict finding:**

**Algorithm:**
```python
def detect_contradictions(graph: SEG) -> List[Conflict]:
    """Find conflicting claims"""
    conflicts = []
    
    # Get all claims
    claims = graph.get_nodes_by_type("claim")
    
    # Check pairwise
    for c1, c2 in combinations(claims, 2):
        # High semantic similarity (same topic)
        if similarity(c1.content, c2.content) > 0.7:
            # Opposite stances (contradiction!)
            if are_contradictory(c1.content, c2.content):
                conflicts.append(Conflict(
                    claim_a=c1,
                    claim_b=c2,
                    detected_at=datetime.utcnow()
                ))
                
                # Add edge
                graph.add_edge(SEGEdge(
                    type="contradicts",
                    source=c1.id,
                    target=c2.id
                ))
    
    return conflicts
```

**Prevents drift!** Conflicting information automatically flagged.

---

### 4. Export System

**Standards compliance:**

**JSON-LD:** W3C-standard linked data format  
**SHACL:** Shape validation (ensure graph integrity)  
**RDF:** Triple store compatibility  

**Example JSON-LD:**
```json
{
  "@context": "https://aimos.org/seg/context",
  "@type": "Claim",
  "@id": "claim:auth_jwt",
  "content": "OAuth2 uses JWT tokens",
  "created": "2025-01-15T10:00:00Z",
  "validFrom": "2025-01-15T10:00:00Z",
  "witnesses": [
    {"@id": "vif:witness_abc123"}
  ]
}
```

---

### 5. Query Engine

**Powerful graph queries:**

**Lineage:** "Where did this come from?"  
**Temporal:** "What was true at time T?"  
**Contradiction:** "What conflicts with this?"  
**Provenance:** "Who created this?"  

**Examples:**
```python
# Lineage query
ancestors = seg.trace_lineage(claim_id="c123", direction="backward")

# Temporal query
snapshot = seg.snapshot_at_time(timestamp="2025-10-15T12:00:00Z")

# Contradiction query
conflicts = seg.find_contradictions(claim_id="c123")

# Provenance query
chain = seg.get_provenance_chain(claim_id="c123")
```

---

## Integration Points

**SEG Stores:**
- VIF witnesses (as source nodes)
- APOE executions (as derivation nodes)
- CMC changes (as events)

**SEG Enables:**
- SDF-CVF (parity requires provenance)
- Audit compliance (full trails)
- Knowledge coherence (contradiction detection)

---

## Current Status

**Implementation:** 35% complete (Week 5 priority)  
**Tests:** Basic JSONL storage working  
**Code:** `packages/seg/`, `packages/cmc_service/data/seg/`

**Week 5 Targets:**
- ✅ Bitemporal queries
- ✅ Contradiction detection (automated)
- ✅ JSON-LD export
- ✅ Graph database (Neo4j integration)

---

**Parent:** [../../README.md](../../README.md)  
**Status:** 35% implemented, Week 5 priority

**PATTERN CONTINUES - SEG DOCUMENTED!** ✅

