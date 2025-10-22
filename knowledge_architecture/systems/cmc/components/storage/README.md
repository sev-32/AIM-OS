# Storage - Multi-Tier Persistence

**Component of:** CMC  
**Type:** Infrastructure Component  
**Purpose:** Persist atoms across vector, object, metadata, and graph stores  
**Status:** ✅ 75% Implemented (SQLite + JSONL + basic vector)

---

## 🎯 **Quick Context (100 words)**

Storage provides four-tier persistence: Vector Store (embeddings for semantic search), Object Store (large payloads, S3-compatible), Metadata Store (atoms/snapshots, SQLite/Postgres), Graph Store (SEG edges, RDF). Each tier optimized for its data type. Vector: fast KNN. Object: content-addressed, deduped. Metadata: ACID transactions, indexed queries. Graph: temporal, contradiction-aware. Abstracts implementation (local vs cloud). Enables scaling: local dev → production distributed. Critical for CMC durability, queryability, and performance.

**[More detail below ↓]**

---

## 📊 **Context Budget Guide**

**4k:** This README  
**8k:** [L1_overview.md](L1_overview.md)  
**32k:** [L2_architecture.md](L2_architecture.md)  
**200k+:** L3-L5 + layer-specific docs

---

## 📦 **The Four Storage Layers**

### **1. Vector Store** (Embeddings)
**Purpose:** Semantic search via KNN  
**Data:** Embedding vectors (384-3072 dim)  
**Operations:** Add, search, delete  
**Implementations:**
- Faiss (local, fast)
- Chroma (local, persistent)
- Qdrant (cloud, scalable)

**Location:** [layers/vector_store/](layers/vector_store/)

---

### **2. Object Store** (Large Payloads)
**Purpose:** Store content >1KB  
**Data:** Atom content, file attachments  
**Operations:** Put, get, delete, exists  
**Implementations:**
- Filesystem (local dev)
- S3 (production)
- MinIO (self-hosted S3-compatible)

**Location:** [layers/object_store/](layers/object_store/)

---

### **3. Metadata Store** (Atoms/Snapshots)
**Purpose:** Structured queries, ACID transactions  
**Data:** Atoms, snapshots, tags  
**Operations:** SQL queries, indexes  
**Implementations:**
- SQLite (local, embedded)
- PostgreSQL (production, distributed)

**Schema:** [layers/metadata_store/schema/](layers/metadata_store/schema/)  
**Location:** [layers/metadata_store/](layers/metadata_store/)

---

### **4. Graph Store** (SEG Edges)
**Purpose:** Provenance relationships  
**Data:** Nodes (claims), edges (supports/contradicts)  
**Operations:** Graph queries, time-slicing  
**Implementations:**
- JSONL (current, basic)
- Neo4j (planned)
- TypeDB (future)

**Location:** [layers/graph_store/](layers/graph_store/)

---

## 🔧 **Storage Abstraction**

```python
# Abstract interfaces (implementation-agnostic)
class VectorStore(ABC):
    def add(ids, embeddings, metadata): pass
    def search(query_vector, k, filters): pass

class ObjectStore(ABC):
    def put(uri, content): pass
    def get(uri): pass

class MetadataStore(ABC):
    def save_atom(atom): pass
    def load_atom(atom_id): pass
    def query(filters): pass

class GraphStore(ABC):
    def add_node(node): pass
    def add_edge(from_id, to_id, type): pass
    def query_lineage(node_id): pass
```

---

## 🔗 **Data Flow**

**Write (Atom Creation):**
```
Atom Created
    ├──→ Metadata Store (atom record)
    ├──→ Vector Store (embedding)
    ├──→ Object Store (if content >1KB)
    └──→ Graph Store (SEG edges)
```

**Read (Query):**
```
Query
    ├──→ Vector Store (semantic search)
    ├──→ Metadata Store (load full atoms)
    └──→ Object Store (lazy-load content if needed)
```

---

## 📊 **Current Implementation**

**Working:**
- ✅ SQLite metadata store (atoms, snapshots, tags)
- ✅ Filesystem object store (local dev)
- ✅ Faiss vector store (basic)
- ✅ JSONL graph store (basic provenance)

**Planned:**
- ⏸️ PostgreSQL (production metadata)
- ⏸️ S3 object store (production)
- ⏸️ Qdrant/Chroma (production vector)
- ⏸️ Neo4j/TypeDB (production graph)

---

## 🔗 **Relationships**

**Storage used by:**
- Write Pipeline (persists atoms)
- Read Pipeline (queries atoms)
- Snapshot System (stores bundles)
- HHNI (indexes atoms)

**Storage abstracts:**
- Local vs. cloud deployment
- Development vs. production
- Scaling strategies

---

## 📚 **Detail Levels**

**L0:** This README  
**L1-L5:** Architecture docs (to be created)

**Sub-components:**
- [layers/vector_store/](layers/vector_store/) - Embedding storage
- [layers/object_store/](layers/object_store/) - Payload storage
- [layers/metadata_store/](layers/metadata_store/) - ACID storage
- [layers/graph_store/](layers/graph_store/) - Graph storage

---

**Parent:** [../../README.md](../../README.md)  
**Implementation:** `packages/cmc_service/repository.py`, `storage.py`  
**Status:** Core infrastructure, 75% complete

