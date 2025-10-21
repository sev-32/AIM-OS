# Docker Deployment Guide - HHNI Infrastructure

## Quick Start

### Prerequisites
- Docker Desktop (or Docker Engine + Docker Compose)
- At least 4GB RAM available for containers
- Ports 5080, 6080, 8080, 9080, 6333 available

### Start the Stack

```powershell
# From AIM-OS root directory
cd deploy
docker compose up -d

# Check status
docker compose ps

# View logs
docker compose logs -f
```

### Expected Output

```
NAME                IMAGE                 STATUS          PORTS
dgraph-zero         dgraph/dgraph:latest  Up 2 minutes    0.0.0.0:5080->5080/tcp, 0.0.0.0:6080->6080/tcp
dgraph-alpha        dgraph/dgraph:latest  Up 2 minutes    0.0.0.0:8080->8080/tcp, 0.0.0.0:9080->9080/tcp
qdrant              qdrant/qdrant:latest  Up 2 minutes    0.0.0.0:6333->6333/tcp
```

## Services

### DGraph (Graph Database)
- **Zero (consensus):** `localhost:5080` (internal), `localhost:6080` (metrics)
- **Alpha (GraphQL):** `localhost:8080` (GraphQL endpoint), `localhost:9080` (gRPC)
- **Storage:** `./data/dgraph/`

### Qdrant (Vector Database)
- **REST API:** `localhost:6333`
- **Storage:** `./data/qdrant/`

## Health Checks

### DGraph Health
```powershell
# GraphQL playground (browser)
start http://localhost:8080

# Query state
curl http://localhost:8080/state

# Health endpoint
curl http://localhost:8080/health
```

### Qdrant Health
```powershell
# Collections list
curl http://localhost:6333/collections

# Health check
curl http://localhost:6333/healthz
```

## Apply HHNI Schema

```powershell
# From AIM-OS root
python scripts/hhni_schema_apply.py
```

Expected output:
```
Schema applied successfully to DGraph at http://localhost:8080
```

## Initialize Qdrant Collections

```powershell
# From AIM-OS root with Python venv active
python -c "
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

client = QdrantClient(url='http://localhost:6333')

# Create paragraph collection
client.create_collection(
    collection_name='hhni_paragraphs',
    vectors_config=VectorParams(size=384, distance=Distance.COSINE)
)

# Create sentence collection
client.create_collection(
    collection_name='hhni_sentences',
    vectors_config=VectorParams(size=384, distance=Distance.COSINE)
)

print('Collections created successfully')
"
```

## Test Integration

```powershell
# Set environment variables
$env:DGRAPH_URL="http://localhost:8080"
$env:QDRANT_URL="http://localhost:6333"

# Run HHNI integration tests
python -m pytest packages/hhni/tests/ -v

# Run CMC+HHNI integration tests
python -m pytest packages/cmc_service/tests/test_integration_e2e.py -v
```

## Troubleshooting

### Port Conflicts
If ports are already in use, edit `deploy/docker-compose.yml`:
```yaml
ports:
  - "8081:8080"  # Change left side (host port)
```

### Data Persistence
Data is stored in `deploy/data/`:
- `dgraph/zero/` - DGraph Zero state
- `dgraph/alpha/` - DGraph Alpha state & data
- `qdrant/` - Qdrant vector storage

### Reset Everything
```powershell
cd deploy
docker compose down -v
rm -r data/
docker compose up -d
```

### Performance Tuning
Edit `deploy/docker-compose.yml`:
```yaml
command: >
  dgraph alpha --my=dgraph-alpha:7080 --zero dgraph-zero:5080
               --lru_mb 2048  # Increase cache (default 1024)
               --badger.vlog_max_entries 100000
```

## Security Notes

### Current Configuration (Development)
- **Network whitelist:** `127.0.0.1,172.18.0.0/16` (Docker network + localhost)
- **No authentication** enabled (add for production)
- **Data volumes** stored locally (mount external for production)

### Production Hardening
1. **Enable DGraph ACL:**
   ```yaml
   command: >
     dgraph alpha --acl secret-key=<random-key>
   ```

2. **Enable Qdrant API key:**
   ```yaml
   environment:
     QDRANT__SERVICE__API_KEY: "your-secure-key"
   ```

3. **Use TLS/SSL** for all endpoints

4. **Firewall rules** to restrict external access

## Monitoring

### DGraph Metrics
```powershell
# Prometheus metrics
curl http://localhost:6080/metrics
```

### Qdrant Metrics
```powershell
# Collection stats
curl http://localhost:6333/collections/hhni_paragraphs
```

### Docker Stats
```powershell
docker stats dgraph-zero dgraph-alpha qdrant
```

## Backup & Restore

### DGraph Backup
```powershell
# Export data
docker exec dgraph-alpha dgraph export -f /dgraph/export

# Data in deploy/data/dgraph/alpha/export/
```

### Qdrant Backup
```powershell
# Snapshot collection
curl -X POST http://localhost:6333/collections/hhni_paragraphs/snapshots/create

# Download snapshot (returns snapshot name)
curl http://localhost:6333/collections/hhni_paragraphs/snapshots/<snapshot_name> > backup.snapshot
```

## Next Steps

1. ✅ Start Docker stack
2. ✅ Apply HHNI schema
3. ✅ Initialize Qdrant collections
4. ✅ Run integration tests
5. 🔄 Load test with 1K atoms
6. 🔄 Performance benchmarking

---

*For production deployment guidance, see `docs/PRODUCTION_DEPLOYMENT.md` (coming soon)*

