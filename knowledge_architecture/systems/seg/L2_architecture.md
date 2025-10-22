# SEG L2: Technical Architecture

**Detail Level:** 2 of 5 (2,000 words)  
**Context Budget:** ~32k tokens  
**Purpose:** Complete technical specification of SEG

---

## SYSTEM OVERVIEW

SEG (Shared Evidence Graph) transforms scattered evidence into a unified, temporal, contradiction-aware knowledge graph. Instead of facts living in isolated documents, SEG treats evidence as a graph where every claim, source, derivation, and agent becomes a node, and every relationship (supports, contradicts, derives, witnesses) becomes an edge. Bitemporal storage (Transaction Time + Valid Time) enables "what was known when?" queries, and automatic contradiction detection surfaces conflicts before they cause problems.

---

## ARCHITECTURE DIAGRAM

```
┌─────────────────────────────────────────────────────────────┐
│              SHARED EVIDENCE GRAPH (SEG)                     │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌─────────────────────────────────────────────────────┐    │
│  │              GRAPH LAYER                             │    │
│  ├─────────────────────────────────────────────────────┤    │
│  │  Nodes: [Claim, Source, Derivation, Agent]          │    │
│  │  Edges: [supports, contradicts, derives, witnesses] │    │
│  └──────────────────────┬──────────────────────────────┘    │
│                         ↓                                     │
│  ┌─────────────────────────────────────────────────────┐    │
│  │           BITEMPORAL STORAGE                         │    │
│  ├─────────────────────────────────────────────────────┤    │
│  │  Transaction Time (TT): When recorded in SEG         │    │
│  │  Valid Time (VT): When true in reality               │    │
│  │  → Enables: "What was known at time T?"             │    │
│  └──────────────────────┬──────────────────────────────┘    │
│                         ↓                                     │
│  ┌─────────────────────────────────────────────────────┐    │
│  │        CONTRADICTION DETECTION                       │    │
│  ├─────────────────────────────────────────────────────┤    │
│  │  • Find semantically similar claims                  │    │
│  │  • Check for opposite stances                        │    │
│  │  • Create "contradicts" edges automatically          │    │
│  │  • Flag for resolution                               │    │
│  └──────────────────────┬──────────────────────────────┘    │
│                         ↓                                     │
│  ┌─────────────────────────────────────────────────────┐    │
│  │            QUERY ENGINE                              │    │
│  ├─────────────────────────────────────────────────────┤    │
│  │  • Lineage: Trace origins                            │    │
│  │  • Temporal: What was true at time T?               │    │
│  │  • Provenance: Who created this?                    │    │
│  │  • Contradiction: What conflicts?                   │    │
│  └──────────────────────┬──────────────────────────────┘    │
│                         ↓                                     │
│  ┌─────────────────────────────────────────────────────┐    │
│  │           EXPORT SYSTEM                              │    │
│  ├─────────────────────────────────────────────────────┤    │
│  │  • JSON-LD (W3C standard)                            │    │
│  │  • RDF (triple store compatible)                    │    │
│  │  • SHACL (shape validation)                         │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

---

## CORE COMPONENTS

### 1. Graph Schema - Nodes and Edges

**Node Types (4):**

**Claim Node:**
```python
@dataclass
class ClaimNode:
    """Factual assertion (evidence)"""
    id: str                           # "claim:auth_jwt_001"
    type: str = "claim"
    content: str                      # "OAuth2 uses JWT tokens"
    embedding: Optional[np.ndarray]   # For semantic similarity
    confidence: float = 1.0           # How confident (0-1)
    stance: str = "positive"          # "positive" | "negative" | "neutral"
    
    # Bitemporal
    created_at: datetime              # Transaction time
    valid_from: datetime              # Valid time start
    valid_to: Optional[datetime]      # Valid time end (None = still valid)
    
    # Provenance
    source_ids: List[str]             # Where it came from
    vif_witness_id: Optional[str]     # VIF witness that recorded it
```

**Source Node:**
```python
@dataclass
class SourceNode:
    """Origin of evidence"""
    id: str                           # "source:vif_abc123"
    type: str = "source"
    source_type: str                  # "vif_witness" | "document" | "user_input" | "external_api"
    reference: str                    # VIF ID, document path, user ID, API endpoint
    authority_score: float = 0.5      # How trustworthy (0-1)
    verified: bool = False            # Has this been verified?
    
    # Bitemporal
    created_at: datetime
    valid_from: datetime
    valid_to: Optional[datetime] = None
```

**Derivation Node:**
```python
@dataclass
class DerivationNode:
    """How claim was derived"""
    id: str                           # "derivation:apoe_plan_xyz"
    type: str = "derivation"
    method: str                       # "apoe_execution" | "inference_chain" | "computation"
    inputs: List[str]                 # Input claim/source IDs
    outputs: List[str]                # Output claim IDs
    reasoning: str                    # Human-readable explanation
    confidence: float                 # How confident in derivation
    
    # APOE-specific
    apoe_plan_id: Optional[str]       # Reference to APOE execution
    vif_trace: List[str]              # VIF witnesses for each step
    
    # Bitemporal
    created_at: datetime
```

**Agent Node:**
```python
@dataclass
class AgentNode:
    """Who/what created evidence"""
    id: str                           # "agent:user_john" | "agent:gpt4_turbo"
    type: str = "agent"
    agent_type: str                   # "human" | "ai_model" | "system"
    model_id: Optional[str]           # If AI: "gpt-4-turbo"
    user_id: Optional[str]            # If human: "john@example.com"
    authority_score: float = 0.5      # Trustworthiness
    
    created_at: datetime
```

**Edge Types (5):**

**supports:**
```python
@dataclass
class SupportsEdge:
    """Evidence backs up claim"""
    id: str
    type: str = "supports"
    source_node_id: str               # Source or claim that supports
    target_node_id: str               # Claim being supported
    weight: float = 1.0               # Strength of support (0-1)
    created_at: datetime
```

**contradicts:**
```python
@dataclass
class ContractsEdge:
    """Evidence conflicts with claim"""
    id: str
    type: str = "contradicts"
    source_node_id: str               # Claim A
    target_node_id: str               # Claim B (conflicts with A)
    similarity: float                 # How semantically similar (0-1)
    contradiction_score: float        # How contradictory (0-1)
    detected_at: datetime
```

**derives:**
```python
@dataclass
class DerivesEdge:
    """Claim produced from others"""
    id: str
    type: str = "derives"
    source_node_id: str               # Derivation node
    target_node_id: str               # Resulting claim
    confidence: float                 # Confidence in derivation
    created_at: datetime
```

**witnesses:**
```python
@dataclass
class WitnessesEdge:
    """VIF records claim"""
    id: str
    type: str = "witnesses"
    source_node_id: str               # Source (VIF witness)
    target_node_id: str               # Claim being witnessed
    vif_id: str                       # Reference to full VIF
    created_at: datetime
```

**cites:**
```python
@dataclass
class CitesEdge:
    """Reference to source"""
    id: str
    type: str = "cites"
    source_node_id: str               # Claim
    target_node_id: str               # Source
    created_at: datetime
```

---

### 2. Bitemporal Storage

**Two Independent Timelines:**

**Transaction Time (TT):** When fact was recorded in SEG  
**Valid Time (VT):** When fact was true in reality  

**Schema Addition:**
```python
# Every node has:
created_at: datetime      # TT: when added to SEG
valid_from: datetime      # VT: when became true
valid_to: Optional[datetime]  # VT: when ceased to be true (None = still valid)
```

**Example Scenario:**
```python
# Real events:
# 2025-10-15: User John promoted to Admin
# 2025-10-18: User John demoted to User

# SEG records (as we learn about them):
# 2025-10-21 10:00: We record the promotion
claim_promotion = ClaimNode(
    content="John has role Admin",
    created_at=datetime(2025, 10, 21, 10, 0),   # TT: when we recorded it
    valid_from=datetime(2025, 10, 15),           # VT: when it became true
    valid_to=datetime(2025, 10, 18)              # VT: when it ceased to be true
)

# 2025-10-25 12:00: We discover it ended on 10-18
# (Update VT, TT stays the same for this record)
```

**Temporal Queries:**
```python
def query_valid_time(claim_type: str, at_time: datetime) -> List[ClaimNode]:
    """What was true at specific time?"""
    return [
        claim for claim in seg.get_claims(claim_type)
        if claim.valid_from <= at_time and (
            claim.valid_to is None or claim.valid_to > at_time
        )
    ]

def query_transaction_time(at_time: datetime) -> List[Node]:
    """What did we know at specific time?"""
    return [
        node for node in seg.get_all_nodes()
        if node.created_at <= at_time
    ]

# Example: "What was John's role on 2025-10-17?"
roles = query_valid_time("user_role", datetime(2025, 10, 17))
# Returns: [ClaimNode(content="John has role Admin", ...)]

# Example: "What did we know about John on 2025-10-20?"
knowledge = query_transaction_time(datetime(2025, 10, 20))
# Returns: [] (we hadn't recorded anything yet, TT = 2025-10-21)
```

**Benefits:**
- **Corrections without deletion:** Update VT, preserve TT
- **Audit trails:** Know when we learned things (TT)
- **Historical reasoning:** Reason about past states (VT)
- **Time travel:** Query as-of any point in time

**Current Status:** 20% implemented (schema designed, queries not yet working)

---

### 3. Contradiction Detection

**Algorithm:**
```python
def detect_contradictions(seg: SEG) -> List[ContradictionRecord]:
    """Find conflicting claims in graph"""
    conflicts = []
    claims = seg.get_nodes_by_type("claim")
    
    # Check all pairs
    for i, claim_a in enumerate(claims):
        for claim_b in claims[i+1:]:
            # Step 1: Check semantic similarity (same topic?)
            if claim_a.embedding is None or claim_b.embedding is None:
                continue
            
            similarity = cosine_similarity(
                [claim_a.embedding],
                [claim_b.embedding]
            )[0, 0]
            
            if similarity < 0.6:
                continue  # Different topics, skip
            
            # Step 2: Check stances (opposite?)
            if are_opposite_stances(claim_a.stance, claim_b.stance):
                # Step 3: Verify contradiction (not just different stances)
                contradiction_score = analyze_contradiction(
                    claim_a.content,
                    claim_b.content
                )
                
                if contradiction_score > 0.5:
                    # Contradiction detected!
                    conflicts.append(ContradictionRecord(
                        claim_a=claim_a,
                        claim_b=claim_b,
                        similarity=similarity,
                        contradiction_score=contradiction_score,
                        detected_at=datetime.utcnow()
                    ))
                    
                    # Add "contradicts" edge to graph
                    seg.add_edge(ContractsEdge(
                        id=f"contradicts_{claim_a.id}_{claim_b.id}",
                        source_node_id=claim_a.id,
                        target_node_id=claim_b.id,
                        similarity=similarity,
                        contradiction_score=contradiction_score,
                        detected_at=datetime.utcnow()
                    ))
    
    return conflicts

def analyze_contradiction(content_a: str, content_b: str) -> float:
    """Determine contradiction strength (0-1)"""
    # Simplified: keyword-based stance detection
    # Real implementation: NLP or LLM-based analysis
    
    # Extract stances
    stance_a = extract_stance(content_a)  # "positive" | "negative" | "neutral"
    stance_b = extract_stance(content_b)
    
    # Opposite stances = high contradiction
    if (stance_a == "positive" and stance_b == "negative") or \
       (stance_a == "negative" and stance_b == "positive"):
        return 1.0
    elif stance_a != stance_b:
        return 0.5
    else:
        return 0.0
```

**Automatic Flagging:**
```python
def on_new_claim(claim: ClaimNode):
    """Check for contradictions when new claim added"""
    existing_claims = seg.get_claims()
    
    for existing in existing_claims:
        similarity = cosine_similarity([claim.embedding], [existing.embedding])[0, 0]
        
        if similarity > 0.6:  # Same topic
            contradiction = analyze_contradiction(claim.content, existing.content)
            
            if contradiction > 0.5:
                # Alert!
                log.warning(f"Contradiction detected: {claim.id} vs {existing.id}")
                
                # Add edge
                seg.add_edge(ContractsEdge(...))
                
                # Notify for resolution
                notify_contradiction(claim, existing, contradiction)
```

**Current Status:** 25% implemented (algorithm designed, not automated)

---

### 4. Query Engine

**Four Query Types:**

**Lineage Query (Backward Tracing):**
```python
def trace_lineage(seg: SEG, claim_id: str, max_depth: int = 10) -> LineageTree:
    """Trace where claim came from"""
    visited = set()
    
    def traverse(node_id: str, depth: int) -> Dict:
        if depth > max_depth or node_id in visited:
            return None
        
        visited.add(node_id)
        node = seg.get_node(node_id)
        
        # Find incoming edges (what led to this?)
        incoming = seg.get_incoming_edges(node_id)
        
        ancestors = []
        for edge in incoming:
            ancestor = traverse(edge.source_node_id, depth + 1)
            if ancestor:
                ancestors.append(ancestor)
        
        return {
            "node": node,
            "ancestors": ancestors,
            "depth": depth
        }
    
    return traverse(claim_id, 0)

# Example: "Where did 'OAuth2 uses JWT' come from?"
lineage = trace_lineage(seg, "claim:auth_jwt_001")
# Returns tree: Claim <- Derivation <- [Input Claims] <- Sources (VIF witnesses)
```

**Temporal Query:**
```python
def snapshot_at_time(seg: SEG, timestamp: datetime) -> SEGSnapshot:
    """Get graph state at specific time"""
    # Transaction time: what was in SEG at that time?
    nodes_tt = [n for n in seg.nodes if n.created_at <= timestamp]
    
    # Valid time: which claims were true at that time?
    nodes_vt = [
        n for n in nodes_tt
        if n.valid_from <= timestamp and (n.valid_to is None or n.valid_to > timestamp)
    ]
    
    return SEGSnapshot(
        transaction_time_nodes=nodes_tt,
        valid_time_nodes=nodes_vt,
        as_of=timestamp
    )
```

**Provenance Query:**
```python
def get_provenance_chain(seg: SEG, claim_id: str) -> ProvenanceChain:
    """Get full provenance for claim"""
    claim = seg.get_node(claim_id)
    
    # Find VIF witness
    witness_edges = seg.get_edges_by_type("witnesses", target_id=claim_id)
    vif_witnesses = [seg.get_node(e.source_node_id) for e in witness_edges]
    
    # Find APOE execution (if applicable)
    derivation_edges = seg.get_edges_by_type("derives", target_id=claim_id)
    derivations = [seg.get_node(e.source_node_id) for e in derivation_edges]
    
    # Find original sources
    cite_edges = seg.get_edges_by_type("cites", source_id=claim_id)
    sources = [seg.get_node(e.target_node_id) for e in cite_edges]
    
    return ProvenanceChain(
        claim=claim,
        vif_witnesses=vif_witnesses,
        derivations=derivations,
        sources=sources
    )
```

**Contradiction Query:**
```python
def find_contradictions(seg: SEG, claim_id: str) -> List[ClaimNode]:
    """Find claims that conflict with this one"""
    contradicts_edges = seg.get_edges_by_type("contradicts", source_id=claim_id)
    contradicts_edges += seg.get_edges_by_type("contradicts", target_id=claim_id)
    
    conflicting_claim_ids = set()
    for edge in contradicts_edges:
        if edge.source_node_id == claim_id:
            conflicting_claim_ids.add(edge.target_node_id)
        else:
            conflicting_claim_ids.add(edge.source_node_id)
    
    return [seg.get_node(cid) for cid in conflicting_claim_ids]
```

**Current Status:** 35% implemented (basic queries work, temporal/lineage partial)

---

### 5. Export System

**JSON-LD Export:**
```json
{
  "@context": {
    "@vocab": "https://aimos.org/seg/",
    "xsd": "http://www.w3.org/2001/XMLSchema#",
    "claim": "https://aimos.org/seg/Claim",
    "source": "https://aimos.org/seg/Source"
  },
  "@graph": [
    {
      "@id": "claim:auth_jwt_001",
      "@type": "Claim",
      "content": "OAuth2 uses JWT tokens",
      "confidence": 0.95,
      "createdAt": "2025-10-21T10:00:00Z",
      "validFrom": "2025-10-21T10:00:00Z",
      "witnesses": [
        {"@id": "source:vif_abc123"}
      ],
      "contradicts": []
    },
    {
      "@id": "source:vif_abc123",
      "@type": "Source",
      "sourceType": "vif_witness",
      "reference": "vif_abc123",
      "authorityScore": 0.9,
      "verified": true
    }
  ]
}
```

**SHACL Validation:**
```turtle
:ClaimShape a sh:NodeShape ;
  sh:targetClass :Claim ;
  sh:property [
    sh:path :content ;
    sh:minCount 1 ;
    sh:datatype xsd:string
  ] ;
  sh:property [
    sh:path :confidence ;
    sh:minCount 1 ;
    sh:datatype xsd:float ;
    sh:minInclusive 0.0 ;
    sh:maxInclusive 1.0
  ] .
```

**Current Status:** 30% implemented (basic JSONL, no JSON-LD yet)

---

## INTEGRATION POINTS

**SEG ← VIF:**
- VIF witnesses become source nodes
- Provenance chains tracked

**SEG ← APOE:**
- Execution traces become derivation nodes
- Plan steps linked as graph

**SEG ← CMC:**
- CMC changes become event nodes
- Memory evolution tracked

**SEG → SDF-CVF:**
- Provenance enables parity checking
- Traces validate quartet alignment

---

## CURRENT IMPLEMENTATION STATUS

**Overall:** 35% complete

**Components:**
- Graph Schema: 30%
- Bitemporal Storage: 20%
- Contradiction Detection: 25%
- Query Engine: 35% ✅
- Export System: 30%

**Week 5 Priorities:**
- Bitemporal query engine (temporal/lineage queries)
- Contradiction detection (automated)
- JSON-LD export (W3C compliance)
- Graph database integration (Neo4j)

---

## SUMMARY

SEG enables complete provenance through:
1. **Graph Schema:** 4 node types, 5 edge types
2. **Bitemporal Storage:** TT + VT for temporal queries
3. **Contradiction Detection:** Automatic conflict finding
4. **Query Engine:** Lineage, temporal, provenance, contradiction queries
5. **Export System:** JSON-LD, RDF, SHACL compliance

**Result:** Contradiction-aware, temporal, traceable knowledge graph! ✨

---

**Word Count:** ~2,000  
**Next:** [L3_detailed.md](L3_detailed.md) (10,000 words, implementation guide)  
**Parent:** [README.md](README.md)  
**Implementation:** `packages/seg/`, `packages/cmc_service/data/seg/`  
**Status:** 35% implemented, Week 5 priority

