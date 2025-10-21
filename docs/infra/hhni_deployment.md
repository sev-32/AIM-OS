# HHNI Deployment Guide

*Maintainer: o3pro-ai (Lead Manager)*  
*Date: 2025-10-18*

---

## Overview

This document explains how to spin up the HHNI infrastructure stack—DGraph (Zero + Alpha) and Qdrant—apply the GraphQL schema, and verify basic health.

> **Prerequisites**
> * Docker >= 20.10
> * `python3` available for schema upload script
> * Ports `8080`, `5080`, `6080`, `6333` free on host

---

## 1  Start the Stack

```bash
cd deploy
docker compose up -d
```

Containers:

| Container       | Purpose                 | Ports |
|-----------------|-------------------------|-------|
| `dgraph-zero`   | Cluster coordinator     | 5080, 6080 |
| `dgraph-alpha`  | GraphQL endpoint        | 8080 (HTTP), 9080 (gRPC) |
| `qdrant`        | Vector search database  | 6333 |

Volumes are persisted under `deploy/data/` so container restarts preserve data.

---

## 2  Apply GraphQL Schema

```bash
python scripts/hhni_schema_apply.py \
  --dgraph-url http://localhost:8080 \
  --schema schemas/hhni.graphql
```

Expected output:

```text
Schema applied {"data":{"updateGQLSchema":{"gqlSchema":{"id":"0x1"}}}}
```

If you receive an error, ensure the Alpha container is healthy and retry.

---

## 3  Initialize Qdrant Collections

```python
from qdrant_client import QdrantClient

client = QdrantClient(url="http://localhost:6333")

for name, dim in {
    "hhni_paragraphs": 384,
    "hhni_sentences": 384,
}.items():
    if name not in {c.name for c in client.get_collections().collections}:
        client.recreate_collection(name=name, vector_size=dim, distance="Cosine")
        print("Created", name)
```

You can run the snippet from a `python` REPL or save as `scripts/init_qdrant.py`.

---

## 4  Health Checks

### DGraph

```bash
curl -s http://localhost:8080/health?all | jq
```

`status` should be `healthy` and membership should list one Alpha/Zero.

### Qdrant

```bash
curl -s http://localhost:6333/collections | jq
```

Should list `hhni_paragraphs` and `hhni_sentences` collections.

---

## 5  Environment Variables

Export these for the CLI / MemoryStore integration:

```bash
export DGRAPH_URL=http://localhost:8080
export QDRANT_URL=http://localhost:6333
```

Add them to your shell profile or Docker Compose `.env` if desired.

---

## 6  Smoke Test (HHNI Build)

```bash
# In project root, with virtualenv active and extras installed
cmc hhni:build --file docs/example.txt --tag priority:0.9 \
  --base-path packages/cmc_service/data
```

Expected JSON output includes `"nodes": [...]` with at least 1 document node.

---

## 7  Shut Down

```bash
docker compose -f deploy/docker-compose.yml down
```

Volumes persist in `deploy/data/`.

---

## Troubleshooting

| Symptom | Possible Cause | Fix |
|---------|----------------|-----|
| `Schema does not apply` | Alpha not ready | Wait 5 s then re-run script |
| `Cannot connect to Qdrant` | Port 6333 blocked | Check firewall / VPN |
| `Node explosion detected` | Atom too large | Lower priority or split file |

---

Stack validated by **o3pro-ai** — ready for Week 1 execution.
