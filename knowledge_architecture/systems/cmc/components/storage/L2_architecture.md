# Storage L2: Four-Tier Architecture

**Detail Level:** 2 of 5 (2,000 words)  
**Context Budget:** ~32k tokens  
**Purpose:** Technical specification for storage layers

---

## Architecture Overview

Storage implements four specialized tiers, each optimized for its data type. This separation enables: (1) Performance optimization per tier, (2) Technology choices per use case, (3) Independent scaling, (4) Clear separation of concerns. All tiers use abstract interfaces for swappable implementations.

## Tier 1: Vector Store (Embedding Search)

### Purpose
Fast K-Nearest Neighbor search in high-dimensional embedding space for semantic similarity queries.

### Interface

```python
from abc import ABC, abstractmethod
from typing import List, Optional, Dict
import numpy as np

@dataclass
class SearchResult:
    id: str
    score: float  # Distance or similarity
    metadata: Dict[str, Any]

class VectorStore(ABC):
    """Abstract interface for vector storage"""
    
    @abstractmethod
    def add(
        self,
        ids: List[str],
        embeddings: List[List[float]],
        metadata: List[Dict[str, Any]]
    ) -> None:
        """Index vectors"""
        pass
    
    @abstractmethod
    def search(
        self,
        query_vector: List[float],
        k: int,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[SearchResult]:
        """Find k nearest neighbors"""
        pass
    
    @abstractmethod
    def delete(self, ids: List[str]) -> None:
        """Remove vectors"""
        pass
    
    @abstractmethod
    def count(self) -> int:
        """Total indexed vectors"""
        pass
```

### Faiss Implementation (Current - Local)

```python
import faiss
import numpy as np

class FaissVectorStore(VectorStore):
    """Local vector store using Faiss"""
    
    def __init__(self, dim: int = 384):
        self.dim = dim
        # Flat index (brute force, exact results)
        self.index = faiss.IndexFlatL2(dim)
        # ID mapping (Faiss uses ints, we use strings)
        self.id_map: Dict[int, str] = {}
        self.reverse_map: Dict[str, int] = {}
        self.metadata_map: Dict[str, Dict] = {}
        self.next_idx = 0
    
    def add(
        self,
        ids: List[str],
        embeddings: List[List[float]],
        metadata: List[Dict[str, Any]]
    ) -> None:
        """Add vectors to index"""
        vectors = np.array(embeddings, dtype='float32')
        
        # Add to Faiss index
        self.index.add(vectors)
        
        # Update mappings
        for i, atom_id in enumerate(ids):
            idx = self.next_idx + i
            self.id_map[idx] = atom_id
            self.reverse_map[atom_id] = idx
            self.metadata_map[atom_id] = metadata[i]
        
        self.next_idx += len(ids)
    
    def search(
        self,
        query_vector: List[float],
        k: int,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[SearchResult]:
        """KNN search"""
        query = np.array([query_vector], dtype='float32')
        
        # Search Faiss
        distances, indices = self.index.search(query, k)
        
        results = []
        for dist, idx in zip(distances[0], indices[0]):
            # Map back to atom ID
            atom_id = self.id_map.get(int(idx))
            if not atom_id:
                continue
            
            metadata = self.metadata_map.get(atom_id, {})
            
            # Apply filters if provided
            if filters:
                if not all(metadata.get(k) == v for k, v in filters.items()):
                    continue
            
            results.append(SearchResult(
                id=atom_id,
                score=float(dist),
                metadata=metadata
            ))
        
        return results
    
    def delete(self, ids: List[str]) -> None:
        """Remove vectors (not supported in IndexFlatL2)"""
        # Faiss Flat index doesn't support deletion
        # Would need to rebuild index or use IndexIDMap wrapper
        raise NotImplementedError("Faiss Flat index doesn't support deletion")
    
    def count(self) -> int:
        return self.index.ntotal
```

**Limitations:**
- No deletion support (Flat index)
- All in-memory (not persistent)
- Linear search (O(N), fine for <1M vectors)

**Advantages:**
- Exact results (no approximation)
- Simple to implement
- Fast enough for dev/testing

### Qdrant Implementation (Future - Production)

```python
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct

class QdrantVectorStore(VectorStore):
    """Production vector store using Qdrant"""
    
    def __init__(self, url: str, collection: str = "cmc_atoms"):
        self.client = QdrantClient(url=url)
        self.collection = collection
        
        # Create collection if doesn't exist
        try:
            self.client.get_collection(collection)
        except:
            self.client.create_collection(
                collection_name=collection,
                vectors_config=VectorParams(size=384, distance=Distance.COSINE)
            )
    
    def add(self, ids, embeddings, metadata) -> None:
        """Add vectors"""
        points = [
            PointStruct(
                id=hash(atom_id),  # Qdrant needs int/str ID
                vector=embedding,
                payload={"atom_id": atom_id, **meta}
            )
            for atom_id, embedding, meta in zip(ids, embeddings, metadata)
        ]
        
        self.client.upsert(collection_name=self.collection, points=points)
    
    def search(self, query_vector, k, filters=None) -> List[SearchResult]:
        """Search with optional filters"""
        hits = self.client.search(
            collection_name=self.collection,
            query_vector=query_vector,
            limit=k,
            query_filter=filters  # Qdrant filter format
        )
        
        return [
            SearchResult(
                id=hit.payload["atom_id"],
                score=hit.score,
                metadata=hit.payload
            )
            for hit in hits
        ]
```

**Advantages:**
- Persistent storage
- Deletion support
- Fast approximate search (HNSW)
- Filtering support
- Distributed/scalable

---

## Tier 2: Object Store (Large Payloads)

### Interface

```python
class ObjectStore(ABC):
    """Abstract interface for object storage"""
    
    @abstractmethod
    def put(self, uri: str, content: str) -> None:
        """Store content at URI"""
        pass
    
    @abstractmethod
    def get(self, uri: str) -> str:
        """Retrieve content from URI"""
        pass
    
    @abstractmethod
    def delete(self, uri: str) -> None:
        """Remove content"""
        pass
    
    @abstractmethod
    def exists(self, uri: str) -> bool:
        """Check if content exists"""
        pass
```

### S3 Implementation (Production)

```python
import boto3

class S3ObjectStore(ObjectStore):
    """Cloud object store using AWS S3"""
    
    def __init__(self, bucket: str, region: str = "us-east-1"):
        self.bucket = bucket
        self.region = region
        self.s3 = boto3.client('s3', region_name=region)
    
    def put(self, uri: str, content: str) -> None:
        """Upload to S3"""
        key = self._uri_to_key(uri)
        
        self.s3.put_object(
            Bucket=self.bucket,
            Key=key,
            Body=content.encode('utf-8'),
            ServerSideEncryption='AES256'  # Encrypt at rest
        )
    
    def get(self, uri: str) -> str:
        """Download from S3"""
        key = self._uri_to_key(uri)
        
        try:
            response = self.s3.get_object(Bucket=self.bucket, Key=key)
            return response['Body'].read().decode('utf-8')
        except self.s3.exceptions.NoSuchKey:
            raise FileNotFoundError(f"Object not found: {uri}")
    
    def delete(self, uri: str) -> None:
        """Delete from S3"""
        key = self._uri_to_key(uri)
        self.s3.delete_object(Bucket=self.bucket, Key=key)
    
    def exists(self, uri: str) -> bool:
        """Check existence"""
        key = self._uri_to_key(uri)
        try:
            self.s3.head_object(Bucket=self.bucket, Key=key)
            return True
        except:
            return False
    
    def _uri_to_key(self, uri: str) -> str:
        """Convert s3://bucket/key to key"""
        return uri.replace(f"s3://{self.bucket}/", "")
```

**Content Addressing:**
```python
def store_content(content: str, object_store: S3ObjectStore) -> str:
    """Store content, return URI"""
    # Compute hash
    content_hash = hashlib.sha256(content.encode()).hexdigest()
    
    # URI structure: s3://bucket/prefix/hash
    # Use first 2 chars as prefix (distribution)
    uri = f"s3://{object_store.bucket}/objects/{content_hash[:2]}/{content_hash}"
    
    # Check if already exists (dedup)
    if object_store.exists(uri):
        return uri  # Already stored!
    
    # Store
    object_store.put(uri, content)
    
    return uri
```

**Benefits:**
- Automatic deduplication (same content = same hash = same URI)
- Prefix sharding (aa/, ab/, ac/... for distribution)
- Content verification (hash in URI)

---

## Tier 3: Metadata Store (SQL)

### SQLite Implementation (Current)

```python
import sqlite3
from contextlib import contextmanager

class SQLiteMetadataStore:
    """Local metadata store using SQLite"""
    
    def __init__(self, db_path: str = "./cmc.db"):
        self.db_path = db_path
        self._init_schema()
    
    def _init_schema(self):
        """Create tables"""
        with self._connection() as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS atoms (
                    id TEXT PRIMARY KEY,
                    modality TEXT NOT NULL,
                    content_inline TEXT,
                    content_uri TEXT,
                    created_at TIMESTAMP NOT NULL,
                    valid_from TIMESTAMP,
                    valid_to TIMESTAMP,
                    snapshot_id TEXT NOT NULL,
                    metadata_json TEXT NOT NULL,
                    
                    CHECK ((content_inline IS NOT NULL AND content_uri IS NULL) OR 
                           (content_inline IS NULL AND content_uri IS NOT NULL))
                );
                
                CREATE INDEX IF NOT EXISTS idx_atoms_modality ON atoms(modality);
                CREATE INDEX IF NOT EXISTS idx_atoms_snapshot ON atoms(snapshot_id);
                CREATE INDEX IF NOT EXISTS idx_atoms_created ON atoms(created_at);
                CREATE INDEX IF NOT EXISTS idx_atoms_valid ON atoms(valid_from, valid_to);
                
                CREATE TABLE IF NOT EXISTS snapshots (
                    id TEXT PRIMARY KEY,
                    hash TEXT UNIQUE NOT NULL,
                    created_at TIMESTAMP NOT NULL,
                    parent_snapshot TEXT,
                    notes TEXT,
                    metadata_json TEXT NOT NULL
                );
                
                CREATE INDEX IF NOT EXISTS idx_snapshots_hash ON snapshots(hash);
                CREATE INDEX IF NOT EXISTS idx_snapshots_created ON snapshots(created_at);
                
                CREATE TABLE IF NOT EXISTS tags (
                    atom_id TEXT NOT NULL,
                    key TEXT NOT NULL,
                    value TEXT NOT NULL,
                    weight REAL DEFAULT 1.0,
                    FOREIGN KEY (atom_id) REFERENCES atoms(id) ON DELETE CASCADE
                );
                
                CREATE INDEX IF NOT EXISTS idx_tags_atom ON tags(atom_id);
                CREATE INDEX IF NOT EXISTS idx_tags_kv ON tags(key, value);
            """)
    
    @contextmanager
    def _connection(self):
        """Connection context manager"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
    
    def save_atom(self, atom: Atom) -> None:
        """Persist atom"""
        with self._connection() as conn:
            conn.execute("""
                INSERT OR REPLACE INTO atoms 
                (id, modality, content_inline, content_uri, created_at, 
                 valid_from, valid_to, snapshot_id, metadata_json)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                atom.id,
                atom.modality.value,
                atom.content_ref.inline,
                atom.content_ref.uri,
                atom.created_at,
                atom.valid_from,
                atom.valid_to,
                atom.snapshot_id,
                atom.json()
            ))
            
            # Save tags
            conn.execute("DELETE FROM tags WHERE atom_id = ?", (atom.id,))
            for tag in atom.tags:
                conn.execute("""
                    INSERT INTO tags (atom_id, key, value, weight)
                    VALUES (?, ?, ?, ?)
                """, (atom.id, tag.key, tag.value, tag.weight))
```

---

## Tier 4: Graph Store (SEG Relationships)

### Current (JSONL)

```python
class JSONLGraphStore:
    """Simple graph store using JSONL format"""
    
    def __init__(self, path: str = "./seg_graph.jsonl"):
        self.path = path
    
    def add_node(self, node_id: str, node_type: str, content: str) -> None:
        """Add graph node"""
        record = {
            "type": "node",
            "id": node_id,
            "node_type": node_type,
            "content": content,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        with open(self.path, 'a') as f:
            f.write(json.dumps(record) + '\n')
    
    def add_edge(
        self,
        from_id: str,
        to_id: str,
        edge_type: str,
        weight: float = 1.0
    ) -> None:
        """Add graph edge"""
        record = {
            "type": "edge",
            "from": from_id,
            "to": to_id,
            "edge_type": edge_type,
            "weight": weight,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        with open(self.path, 'a') as f:
            f.write(json.dumps(record) + '\n')
```

**Limitations:**
- No graph queries (must scan file)
- No indexing
- Linear performance

**Advantages:**
- Simple (no dependencies)
- Human-readable
- Easy to debug

### Future (Neo4j)

```python
from neo4j import GraphDatabase

class Neo4jGraphStore:
    """Production graph store using Neo4j"""
    
    def __init__(self, uri: str, auth: Tuple[str, str]):
        self.driver = GraphDatabase.driver(uri, auth=auth)
    
    def add_node(self, node_id: str, node_type: str, content: str) -> None:
        """Add node with Cypher"""
        with self.driver.session() as session:
            session.run("""
                MERGE (n:Node {id: $id})
                SET n.type = $type, n.content = $content, 
                    n.created_at = datetime()
            """, id=node_id, type=node_type, content=content)
    
    def query_lineage(self, node_id: str) -> List[Dict]:
        """Trace provenance"""
        with self.driver.session() as session:
            result = session.run("""
                MATCH path = (n:Node {id: $id})-[:SUPPORTS*]->()
                RETURN path
            """, id=node_id)
            
            return [record["path"] for record in result]
```

---

## Performance Characteristics

### Vector Store

**Faiss (Current):**
- Add: <5ms per vector
- Search (k=100, N=1M): ~10ms
- Memory: ~4bytes × dim × N (1.5GB for 1M × 384d)

**Qdrant (Future):**
- Add: <10ms per vector (persisted)
- Search (k=100, N=10M): ~20ms (HNSW approximate)
- Memory: Disk-backed, configurable cache

### Object Store

**Filesystem (Current):**
- Put: <5ms (local SSD)
- Get: <5ms (local SSD)
- Scale: Limited by disk space

**S3 (Future):**
- Put: ~50-100ms (network latency)
- Get: ~30-50ms (with CloudFront CDN)
- Scale: Unlimited

### Metadata Store

**SQLite (Current):**
- Insert: <5ms
- Query (indexed): <10ms
- Query (full scan): <100ms (10k atoms)
- Scale: ~100k atoms (single file limit)

**PostgreSQL (Future):**
- Insert: <10ms
- Query: <20ms (with proper indexes)
- Scale: Millions of atoms (distributed)

---

## Summary

Storage provides:
- ✅ 4 specialized tiers
- ✅ Abstract interfaces
- ✅ Local implementations (dev)
- ✅ Cloud implementations (production)
- ✅ Performance optimized
- ✅ Scalability path clear

**Core infrastructure for CMC!** ✅

---

**Word Count:** ~2,000  
**Next:** [L3_detailed.md](L3_detailed.md)  
**Parent:** [README.md](README.md)  
**Implementation:** `packages/cmc_service/repository.py`, `storage.py`

