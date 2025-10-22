# Embedding Field - Vector Representation

**Field of:** Atom  
**Type:** Pydantic Model  
**Purpose:** Semantic vector for similarity search  
**Status:** ✅ Fully Implemented

---

## 🎯 **Quick Context (50 words)**

Embedding stores vector representation for semantic search. Includes model ID, dimension, vector array, and generation timestamp. Enables finding similar content via cosine similarity. Models: sentence-transformers (local, 384d), OpenAI (cloud, 1536d). Optional but critical for HHNI retrieval. Generated once, cached.

---

## 📦 **Fields**

| Field | Type | Purpose |
|-------|------|---------|
| `model_id` | str | Model identifier |
| `dim` | int | Vector dimension (384, 1536) |
| `vector` | List[float] | Embedding array |
| `generated_at` | datetime | Creation timestamp |

---

## 🔧 **Models Supported**

**Local (Fast, Free):**
- `sentence-transformers/all-MiniLM-L6-v2` (384d)
- `sentence-transformers/all-mpnet-base-v2` (768d)

**Cloud (Higher Quality):**
- `text-embedding-3-small` (1536d) - OpenAI
- `text-embedding-3-large` (3072d) - OpenAI

---

## 📊 **Usage**

```python
# Generate embedding
embedding = embedding_service.embed("Hello world")

# Search by similarity
results = vector_store.search(
    query_embedding.vector,
    k=10
)
```

---

**Parent:** [../../README.md](../../README.md)  
**Sibling:** [../modality/](../modality/)

