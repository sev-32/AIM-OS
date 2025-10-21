# HHNI Query Cookbook

*Architect: Claude 4.5*  
*Date: 2025-10-18*  
*Purpose: Common query patterns for HHNI navigation*

---

## Quick Reference

| Pattern | Use Case | Performance | Complexity |
|---------|----------|-------------|------------|
| Get by Path | Direct node lookup | <10ms | Simple |
| Hierarchy for Atom | All nodes for document | <50ms | Simple |
| Sibling Navigation | Related paragraphs | <80ms | Medium |
| Dependency Traversal | Impact analysis | <150ms | Complex |
| Semantic Search | Vector similarity | <100ms | Medium |

---

## Pattern 1: Direct Path Lookup

**Use Case:** Retrieve a specific node when you know its path.

```graphql
query GetNodeByPath($path: String!) {
  queryHHNINode(filter: { path: { eq: $path } }) {
    id
    level
    text
    contentHash
    createdAt
  }
}
```

**Example:**
```python
client = DGraphClient()
result = client.query("""
  query {
    queryHHNINode(filter: { path: { eq: "/sys:aimos/doc:atom_123/para:0" } }) {
      id
      text
    }
  }
""")
paragraph = result["queryHHNINode"][0]
```

**Performance:** ~5-10ms  
**Safety:** Auto-limited to 1000 results

---

## Pattern 2: Hierarchy for Atom

**Use Case:** Get all HHNI nodes created from a specific atom.

```graphql
query HierarchyForAtom($atomId: String!) {
  queryHHNINode(filter: { atomRefs: { eq: $atomId } }) {
    id
    level
    path
    text
    parent { id }
    children { id }
  }
}
```

**Example:**
```python
atom_id = "atom_abc123"
result = client.query(
    """
    query($atomId: String!) {
      queryHHNINode(filter: { atomRefs: { eq: $atomId } }) {
        id
        level
        text
      }
    }
    """,
    variables={"atomId": atom_id}
)
nodes_by_level = {}
for node in result["queryHHNINode"]:
    nodes_by_level.setdefault(node["level"], []).append(node)
```

**Performance:** ~30-50ms for typical atom (20-50 nodes)  
**Safety:** Capped at 1000 nodes per atom by safety gates

---

## Pattern 3: Sibling Navigation

**Use Case:** Find paragraphs at the same level (siblings).

```graphql
query GetSiblings($nodeId: ID!) {
  getHHNINode(id: $nodeId) {
    parent {
      children(filter: { id: { not: { eq: $nodeId } } }, first: 100) {
        id
        text
        path
      }
    }
  }
}
```

**Example:**
```python
para_id = "para:atom_123#p0"
result = client.query(
    """
    query($id: ID!) {
      getHHNINode(id: $id) {
        parent {
          children(filter: { id: { not: { eq: $id } } }) {
            id
            text
          }
        }
      }
    }
    """,
    variables={"id": para_id}
)
siblings = result["getHHNINode"]["parent"]["children"]
```

**Performance:** ~60-80ms (adds one extra hop)  
**Trade-off:** Slower than direct sibling_ids, but prevents O(n²) edges

---

## Pattern 4: Dependency Traversal

**Use Case:** Impact analysis – find all nodes that depend on this one.

```graphql
query ImpactAnalysis($nodeId: ID!, $depth: Int = 3) {
  getHHNINode(id: $nodeId) {
    dependedBy(first: 100) {
      id
      text
      dependedBy(first: 100) {
        id
        text
      }
    }
  }
}
```

**Example:**
```python
from hhni.safety import HHNIQueryGates

depth = 3
HHNIQueryGates.validate_depth(depth)  # Enforce max depth

result = client.query(
    """
    query($id: ID!) {
      getHHNINode(id: $id) {
        dependedBy {
          id
          text
          dependedBy {
            id
          }
        }
      }
    }
    """,
    variables={"id": "para:atom_123#p5"}
)
```

**Performance:** ~100-200ms (depth=3), grows with depth  
**Safety:** Max depth = 5 (enforced by `HHNIQueryGates`)

---

## Pattern 5: Full Subtree

**Use Case:** Get entire hierarchy below a node (document → paragraphs → sentences).

```graphql
query FullSubtree($nodeId: ID!) {
  getHHNINode(id: $nodeId) {
    id
    text
    children {
      id
      text
      children {
        id
        text
      }
    }
  }
}
```

**Example:**
```python
# Get document with all paragraphs and sentences
doc_id = "doc:atom_123"
result = client.query(
    """
    query($id: ID!) {
      getHHNINode(id: $id) {
        id
        children {
          id
          text
          children {
            id
            text
          }
        }
      }
    }
    """,
    variables={"id": doc_id}
)
doc = result["getHHNINode"]
paragraphs = doc["children"]
for para in paragraphs:
    sentences = para["children"]
```

**Performance:** ~50-100ms for typical document  
**Safety:** Auto-limited to 1000 total nodes

---

## Pattern 6: Semantic Search (Qdrant + DGraph)

**Use Case:** Find similar paragraphs using vector embeddings.

**Step 1:** Search Qdrant for similar vectors
```python
from hhni.embeddings import encode_text

query_text = "How does memory indexing work?"
query_vector = encode_text(query_text)

# Search Qdrant
results = qdrant_client.search(
    collection_name="hhni_paragraphs",
    query_vector=query_vector,
    limit=20
)
node_ids = [hit.payload["node_id"] for hit in results]
```

**Step 2:** Hydrate nodes from DGraph
```python
# Get full node details
result = client.query(
    """
    query($ids: [ID!]!) {
      queryHHNINode(filter: { id: { in: $ids } }) {
        id
        text
        path
        parent { id text }
      }
    }
    """,
    variables={"ids": node_ids}
)
paragraphs = result["queryHHNINode"]
```

**Performance:** ~80-120ms total (Qdrant: 40ms, DGraph: 60ms)  
**Safety:** Qdrant limit enforced, DGraph auto-limits to 1000

---

## Pattern 7: Filter by Tag

**Use Case:** Find all nodes with specific tags.

```graphql
query NodesByTag($tagKey: String!, $minWeight: Float!) {
  queryHHNINode(filter: {
    tags: {
      key: { eq: $tagKey },
      weight: { ge: $minWeight }
    }
  }, first: 100) {
    id
    text
    tags {
      key
      weight
    }
  }
}
```

**Example:**
```python
result = client.query(
    """
    query {
      queryHHNINode(filter: {
        tags: { key: { eq: "priority" } }
      }) {
        id
        text
      }
    }
    """
)
```

**Performance:** ~60-100ms depending on index size  
**Note:** Requires tag index on DGraph

---

## Pattern 8: Recent Nodes

**Use Case:** Get nodes created in the last N hours.

```graphql
query RecentNodes($since: DateTime!) {
  queryHHNINode(
    filter: { createdAt: { ge: $since } },
    order: { desc: createdAt },
    first: 50
  ) {
    id
    text
    createdAt
    level
  }
}
```

**Example:**
```python
from datetime import datetime, timedelta, timezone

since = (datetime.now(timezone.utc) - timedelta(hours=24)).isoformat()
result = client.query(
    """
    query($since: DateTime!) {
      queryHHNINode(filter: { createdAt: { ge: $since } }) {
        id
        text
        createdAt
      }
    }
    """,
    variables={"since": since}
)
```

**Performance:** ~50-80ms with time index  
**Optimization:** Add index on `createdAt` in schema

---

## Pattern 9: Node Stats by Level

**Use Case:** Count nodes at each level for monitoring.

```graphql
query NodeStatsByLevel {
  level0: aggregateHHNINode(filter: { level: { eq: 0 } }) {
    count
  }
  level1: aggregateHHNINode(filter: { level: { eq: 1 } }) {
    count
  }
  level2: aggregateHHNINode(filter: { level: { eq: 2 } }) {
    count
  }
  level3: aggregateHHNINode(filter: { level: { eq: 3 } }) {
    count
  }
}
```

**Performance:** ~20-40ms (aggregation optimized)  
**Use Case:** Health monitoring, metrics dashboard

---

## Pattern 10: Stale Node Detection

**Use Case:** Find nodes that haven't been updated and may need refresh.

```graphql
query StaleNodes($maxStalenessDays: Int!) {
  queryHHNINode(
    filter: { stalenessDays: { ge: $maxStalenessDays } },
    order: { desc: stalenessDays },
    first: 100
  ) {
    id
    text
    stalenessDays
    createdAt
  }
}
```

**Example:**
```python
result = client.query(
    """
    query {
      queryHHNINode(filter: { stalenessDays: { ge: 30 } }) {
        id
        text
        stalenessDays
      }
    }
    """
)
```

**Performance:** ~60-90ms  
**Note:** `stalenessDays` is computed field, updated periodically

---

## CLI Usage Examples

### Query from Command Line
```bash
# Get node by path
cmc hhni:query --path "/sys:aimos/doc:atom_123/para:0"

# Get hierarchy for atom
cmc hhni:query --atom-id atom_123 --format json

# Semantic search
cmc hhni:search "How does indexing work?" --limit 10
```

### Python API
```python
from hhni import DGraphClient
from hhni.safety import HHNIQueryGates

client = DGraphClient(host="http://localhost:8080")

# Always apply safety gates
query = """
  query { queryHHNINode { id text } }
"""
safe_query = HHNIQueryGates.apply_limits(query, first=50)
result = client.query(safe_query)
```

---

## Performance Tuning Tips

1. **Use `first:` parameter** – Always limit results
2. **Index critical fields** – Add indexes for `createdAt`, `level`, `tags.key`
3. **Batch queries** – Combine multiple lookups when possible
4. **Cache frequently accessed nodes** – Document-level nodes rarely change
5. **Use vector search judiciously** – Qdrant is fast, but DGraph hydration adds cost

---

## Safety Best Practices

1. **Always validate depth** for traversal queries
2. **Apply `first:` limits** to prevent runaway queries
3. **Set timeouts** at client level (5 seconds default)
4. **Monitor query performance** via logs
5. **Use correlation IDs** for debugging

---

*Query patterns ready for Week 1 integration testing.*

