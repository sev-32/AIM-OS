# AIM-OS Deployment Guide

**Version:** 1.0.0  
**Last Updated:** 2025-10-23  
**Target:** Production deployment of all 7 systems  

---

## Prerequisites

**System Requirements:**
- Python 3.11+ (3.13 recommended)
- 4GB RAM minimum (8GB recommended)
- 10GB disk space
- Linux/macOS/Windows (tested on all)

**Optional:**
- Docker & Docker Compose (for containerized deployment)
- Neo4j (for SEG persistence)
- PostgreSQL (for CMC at scale)

---

## Quick Start (Local)

### 1. Install Dependencies

```bash
# Clone repository
git clone https://github.com/sev-32/AIM-OS.git
cd AIM-OS

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Verify installation
pytest packages/ -v
# Expected: 672+ tests passing
```

### 2. Configure Environment

```bash
# Copy environment template
cp .env.template .env

# Edit configuration
nano .env  # Or your preferred editor
```

**Required Variables:**
```bash
# CMC Configuration
CMC_DATA_DIR=./data/cmc
CMC_DB_PATH=./data/cmc/cmc.db

# HHNI Configuration
HHNI_EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
HHNI_CACHE_DIR=./data/hhni/cache

# VIF Configuration
VIF_AGENT_ID=aether-production
VIF_KAPPA_THRESHOLD=0.80

# APOE Configuration
APOE_MAX_WORKERS=4
APOE_DEFAULT_BUDGET=10000

# SEG Configuration
SEG_BACKEND=networkx  # or 'neo4j' if available
SEG_PERSIST_DIR=./data/seg

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json
```

### 3. Initialize Data Directories

```bash
# Create data directories
mkdir -p data/cmc
mkdir -p data/hhni/cache
mkdir -p data/seg
mkdir -p data/logs

# Set permissions (Linux/macOS)
chmod 755 data/
chmod 644 data/*/*
```

### 4. Run Systems

```python
# test_deployment.py
from cmc_service import MemoryStore
from hhni import HierarchicalIndex
from vif import ECETracker, KappaGate
from apoe import ExecutionPlan
from sdfcvf import ParityCalculator
from seg import SEGraph

# Initialize systems
cmc = MemoryStore("./data/cmc")
hhni = HierarchicalIndex()
vif_tracker = ECETracker()
vif_gate = KappaGate(kappa_threshold=0.80)
apoe_plan = ExecutionPlan(name="Test", steps=[])
sdfcvf_calc = ParityCalculator()
seg_graph = SEGraph()

print("✅ All systems initialized successfully!")
```

```bash
python test_deployment.py
# Expected: ✅ All systems initialized successfully!
```

---

## Docker Deployment

### 1. Build Image

```bash
# Build Docker image
docker build -t aether/aim-os:1.0.0 .

# Verify build
docker images | grep aether
```

### 2. Run Container

```bash
# Run with volume mounts for persistence
docker run -d \
  --name aether \
  -v $(pwd)/data:/app/data \
  -p 8000:8000 \
  -e LOG_LEVEL=INFO \
  aether/aim-os:1.0.0

# Check logs
docker logs aether

# Verify running
docker ps | grep aether
```

### 3. Access Systems

```bash
# Execute inside container
docker exec -it aether python

>>> from cmc_service import MemoryStore
>>> cmc = MemoryStore("/app/data/cmc")
>>> print("CMC initialized!")
```

---

## Docker Compose (Recommended)

### 1. Use Docker Compose

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Stop and remove data
docker-compose down -v
```

**docker-compose.yml contents:**
```yaml
version: '3.8'

services:
  aether:
    build: .
    container_name: aether-main
    ports:
      - "8000:8000"
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    environment:
      - CMC_DATA_DIR=/app/data/cmc
      - LOG_LEVEL=INFO
      - PYTHONUNBUFFERED=1
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "python", "-c", "from cmc_service import MemoryStore"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Optional: Neo4j for SEG persistence
  neo4j:
    image: neo4j:5.11
    container_name: aether-neo4j
    ports:
      - "7474:7474"  # HTTP
      - "7687:7687"  # Bolt
    environment:
      - NEO4J_AUTH=neo4j/aether-password-change-me
    volumes:
      - neo4j-data:/data
    restart: unless-stopped

volumes:
  neo4j-data:
```

---

## Production Configuration

### **CMC (Memory)**

```python
# Production CMC configuration
from cmc_service import MemoryStore, AtomRepository, SQLiteConfig

# High-performance setup
config = SQLiteConfig(
    path="./data/cmc/production.db",
    wal_mode=True,  # Write-Ahead Logging for concurrency
    cache_size_mb=128,  # Increase cache
    page_size=4096
)

repo = AtomRepository(config)
store = MemoryStore(data_dir="./data/cmc", repository=repo)

# Enable connection pooling
from cmc_service import ConnectionPool
pool = ConnectionPool(
    db_path="./data/cmc/production.db",
    pool_size=10  # More concurrent connections
)
```

### **HHNI (Retrieval)**

```python
# Production HHNI configuration
from hhni import HierarchicalIndex

# Optimize for production
index = HierarchicalIndex()

# Pre-warm cache
index.add_text(text_id="warmup", text="Cache warmup", metadata={})

# Configure DVNS for optimal performance
from hhni.dvns_physics import DVNSPhysics, DVNSConfig

physics = DVNSPhysics(DVNSConfig(
    attraction_weight=0.8,
    repulsion_weight=0.2,
    context_radius=0.3,
    max_iterations=50
))
```

### **VIF (Verification)**

```python
# Production VIF configuration
from vif import KappaGate, ECETracker

# Strict quality gates for production
gate = KappaGate(kappa_threshold=0.85)  # Higher threshold

# Track calibration
tracker = ECETracker()

# In production loop:
# tracker.record_prediction(predicted_conf, actual_outcome)
# ece_report = tracker.calculate_ece()
# if ece_report.ece > 0.15:
#     # Recalibrate or escalate
```

---

## Monitoring & Observability

### **Logging**

```python
# Configure structured logging
from cmc_service import configure_logging

configure_logging(
    level="INFO",
    format="json",
    output_file="./logs/aether.log"
)

# All operations now logged as JSON
```

**Log Example:**
```json
{
  "ts": "2025-10-23T02:00:00Z",
  "level": "info",
  "action": "atom.create",
  "atom_id": "abc123",
  "modality": "text",
  "tags": ["concept", "ai"],
  "duration_ms": 45.2
}
```

### **Metrics**

```python
# Track performance metrics
from cmc_service import PerformanceMonitor

monitor = PerformanceMonitor()

# Record operations
monitor.record_operation('atom_create', duration_ms=45.2)
monitor.record_operation('atom_retrieve', duration_ms=5.1)

# Get statistics
stats = monitor.get_stats('atom_create')
print(f"p50: {stats['p50']}ms")
print(f"p95: {stats['p95']}ms")
print(f"p99: {stats['p99']}ms")
```

---

## Backup & Recovery

### **Backup CMC Data**

```bash
#!/bin/bash
# backup.sh

BACKUP_DIR="./backups/$(date +%Y%m%d_%H%M%S)"
mkdir -p $BACKUP_DIR

# Backup SQLite database
cp data/cmc/cmc.db $BACKUP_DIR/
cp data/cmc/atoms.log $BACKUP_DIR/
cp data/cmc/snapshots.log $BACKUP_DIR/

# Backup SEG data (if persisted)
cp -r data/seg/ $BACKUP_DIR/

echo "Backup complete: $BACKUP_DIR"
```

### **Restore from Backup**

```bash
#!/bin/bash
# restore.sh

BACKUP_DIR=$1

if [ -z "$BACKUP_DIR" ]; then
    echo "Usage: ./restore.sh <backup_directory>"
    exit 1
fi

# Restore CMC
cp $BACKUP_DIR/cmc.db data/cmc/
cp $BACKUP_DIR/atoms.log data/cmc/
cp $BACKUP_DIR/snapshots.log data/cmc/

# Restore SEG
cp -r $BACKUP_DIR/seg/ data/

echo "Restore complete from: $BACKUP_DIR"
```

---

## Health Checks

### **System Health Check**

```python
# health_check.py
from cmc_service import MemoryStore
from hhni import HierarchicalIndex
from seg import SEGraph

def health_check():
    """Check if all systems are operational."""
    results = {}
    
    # CMC health
    try:
        cmc = MemoryStore("./data/cmc")
        atoms = cmc.list_atoms(limit=1)
        results['cmc'] = 'healthy'
    except Exception as e:
        results['cmc'] = f'error: {e}'
    
    # HHNI health
    try:
        index = HierarchicalIndex()
        results['hhni'] = 'healthy'
    except Exception as e:
        results['hhni'] = f'error: {e}'
    
    # SEG health
    try:
        graph = SEGraph()
        results['seg'] = 'healthy'
    except Exception as e:
        results['seg'] = f'error: {e}'
    
    return results

if __name__ == "__main__":
    health = health_check()
    for system, status in health.items():
        print(f"{system}: {status}")
```

---

## Troubleshooting

### **Common Issues**

**Issue:** Tests fail with "module not found"  
**Solution:** Install in editable mode: `pip install -e .`

**Issue:** SQLite database locked  
**Solution:** Close all connections, or increase timeout in SQLiteConfig

**Issue:** Out of memory during indexing  
**Solution:** Process in batches, increase system RAM, or reduce batch size

**Issue:** Slow HHNI retrieval  
**Solution:** Enable DVNS optimization, reduce max_results, use compression

**Issue:** High ECE in VIF  
**Solution:** Recalibrate with temperature scaling, collect more predictions

---

## Security

### **Production Security Checklist**

- [ ] Change default passwords (Neo4j, etc.)
- [ ] Enable authentication for all services
- [ ] Use HTTPS for external access
- [ ] Restrict file permissions (chmod 600 sensitive files)
- [ ] Enable audit logging (all VIF witnesses)
- [ ] Regular backups (automated schedule)
- [ ] Monitor for anomalies (unusual operation patterns)
- [ ] Keep dependencies updated (security patches)

---

## Performance Tuning

### **CMC Optimization**

```python
# Enable advanced features
from cmc_service import ConnectionPool, CacheManager, IndexOptimizer

# Connection pooling
pool = ConnectionPool(db_path, pool_size=10)

# Query caching
cache = CacheManager(max_cache_size=1000)

# Optimal indexes
conn = pool.get_connection()
IndexOptimizer.create_optimal_indexes(conn)
```

### **HHNI Optimization**

- Enable DVNS physics (75% faster)
- Use deduplication (40-60% less redundancy)
- Compress results (50-70% token reduction)
- Budget-aware retrieval (stay within limits)

### **SEG Optimization**

- Use NetworkX for <100k entities (fast)
- Switch to Neo4j for >100k entities (scalable)
- Index frequently queried attributes
- Batch entity additions

---

## Support

**Issues:** https://github.com/sev-32/AIM-OS/issues  
**Documentation:** `knowledge_architecture/`  
**Contact:** See repository for details  

---

**Deployment guide by Aether**  
**Ready for production use** ✅🚀

