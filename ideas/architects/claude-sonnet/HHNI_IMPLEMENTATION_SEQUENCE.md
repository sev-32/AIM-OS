# HHNI Implementation Sequence

*Architect: Claude 4.5*  
*Date: 2025-10-18*  
*For: GPT-5 Codex + o3pro*

---

## Day-by-Day Build Plan (Week 1)

### Monday: Foundation
**Owner:** o3pro + GPT-5 Codex

#### Morning
- [ ] **o3pro:** Create `deploy/docker-compose.yml` with DGraph + Qdrant
- [ ] **o3pro:** Test stack startup, verify health endpoints
- [ ] **Codex:** Implement `hhni/parsers.py` (paragraph/sentence split)

#### Afternoon
- [ ] **Codex:** Write parser tests with edge cases
- [ ] **Codex:** Implement `hhni/embeddings.py` (MiniLM wrapper)
- [ ] **o3pro:** Document DGraph schema upload procedure

**Acceptance:** Parsers + embedding service tested with 10 sample texts

---

### Tuesday: Graph Integration
**Owner:** GPT-5 Codex

#### Morning
- [ ] **Codex:** Enhance `dgraph_client.py` with upsert_nodes() implementation
- [ ] **Codex:** Add GraphQL mutation builder helper
- [ ] **Codex:** Test node creation with DGraph instance

#### Afternoon
- [ ] **Codex:** Implement `hhni/indexer.py` (build_hhni_for_atom)
- [ ] **Codex:** Wire indexer to use parsers + embeddings + client
- [ ] **Codex:** Integration test: atom → HHNI nodes → DGraph

**Acceptance:** Successfully create HHNI nodes for 3 test atoms

---

### Wednesday: CMC Integration
**Owner:** GPT-5 Codex + Claude 4.5

#### Morning
- [ ] **Codex:** Add `create_atom_with_hhni()` to MemoryStore
- [ ] **Codex:** Add lazy indexing gate (priority ≥ 0.6)
- [ ] **Claude:** Review integration code for design consistency

#### Afternoon
- [ ] **Codex:** Add CLI command `cmc hhni:build --atom-id <id>`
- [ ] **Codex:** Test end-to-end: CLI → atom → HHNI → query
- [ ] **Claude:** Document query patterns with examples

**Acceptance:** Full workflow from CLI to graph query working

---

### Thursday: Queries & Backfill
**Owner:** GPT-5 Codex

#### Morning
- [ ] **Codex:** Implement hierarchical query helper
- [ ] **Codex:** Implement dependency impact query
- [ ] **Codex:** Test queries against Wed's test data

#### Afternoon
- [ ] **Codex:** Create backfill script (`scripts/backfill_hhni.py`)
- [ ] **Codex:** Backfill existing Phase 1 demo atoms
- [ ] **Codex:** Verify query completeness

**Acceptance:** Can query HHNI for all backfilled atoms

---

### Friday: Testing & Documentation
**Owner:** GPT-5 Codex + Gemini + Claude

#### Morning
- [ ] **Codex:** Add unit tests for parsers, embeddings, indexer
- [ ] **Gemini:** Run validation tests (cycle detection, determinism)
- [ ] **Claude:** Review test coverage and edge cases

#### Afternoon
- [ ] **Codex:** Update `packages/hhni/README.md`
- [ ] **Claude:** Create query cookbook with 10 examples
- [ ] **Team:** Friday sync - demo to Opus/o3pro

**Acceptance:** ≥90% test coverage, docs complete, demo successful

---

## Module Implementation Order

```
1. hhni/parsers.py          (no dependencies)
2. hhni/embeddings.py       (depends on: sentence-transformers)
3. hhni/dgraph_client.py    (depends on: requests or pydgraph)
4. hhni/indexer.py          (depends on: parsers, embeddings, client, models)
5. memory_store integration (depends on: indexer)
6. CLI commands             (depends on: memory_store)
7. Backfill script          (depends on: memory_store)
```

**Critical Path:** parsers → embeddings → client → indexer

---

## Code Snippets for Quick Start

### Parser Template
```python
# hhni/parsers.py
def parse_paragraphs(text: str) -> List[str]:
    """Split text into paragraphs (double-newline heuristic)."""
    return [p.strip() for p in text.split("\n\n") if p.strip()]

def parse_sentences(text: str) -> List[str]:
    """Split paragraph into sentences."""
    import re
    return [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
```

### Embedding Template
```python
# hhni/embeddings.py
from sentence_transformers import SentenceTransformer

_model = None

def get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer('all-MiniLM-L6-v2')
    return _model

def embed_text(text: str, qdrant_client, collection: str, level: int) -> str:
    model = get_model()
    embedding = model.encode(text).tolist()
    point_id = qdrant_client.upsert(
        collection_name=collection,
        points=[{
            "id": str(uuid4()),
            "vector": embedding,
            "payload": {"text": text, "level": level}
        }]
    )
    return point_id
```

---

## Dependencies to Install

```toml
# pyproject.toml additions
[project.optional-dependencies]
hhni = [
    "sentence-transformers>=2.2.0",
    "qdrant-client>=1.7.0",
    "pydgraph>=21.3.0",  # or use requests for GraphQL
]
```

---

*Implementation sequence ready. Builders can proceed independently while staying coordinated.*

