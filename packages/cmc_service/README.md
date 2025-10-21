# CMC Service (Phase 1 Prototype)

Deterministic memory store powering the Context Memory Core (CMC).  
The service persists **atoms** (observations) and **snapshots** (timeline checkpoints), exposes a lightweight REST API, and feeds higher layers such as BTSM, HHNI, and SEG with structured provenance.

---

## Key Capabilities

- Deterministic append-only journaling with replayable snapshots
- Dual storage backends (`JSONL` for portability, `SQLite` for low‑latency queries)
- HTTP API for MPD nodes/edges, KPI history, and blast-radius simulation
- BTSM trunk/edge generation built on shared `schemas` models
- Structured JSON logging plus Prometheus metrics for observability
- CLI utilities for creating/listing atoms and snapshots

---

## Storage Backends

| Backend | Description | Configuration |
| --- | --- | --- |
| `jsonl` | Writes atoms/snapshots to flat files under `data/` | Default (`CMC_BACKEND=jsonl`) |
| `sqlite` | ACID-compliant database used by repo tests and BTSM integration | `CMC_BACKEND=sqlite` with `CMC_SQLITE_PATH=./data/cmc.sqlite` |

Additional limits enforced by `MemoryStore` (`packages/cmc_service/memory_store.py:63`):
- Inline payload size ≤ **1 MB** (`MAX_INLINE_PAYLOAD`)
- Total payload directory ≤ **100 MB**
- ≤ 20 tags per atom, tag key length ≤ 50 chars, tag weights ∈ [0, 1]

All timestamps are serialized as RFC 3339 UTC strings.

---

## HTTP API Highlights

| Method | Path | Purpose | Schema |
| --- | --- | --- | --- |
| GET | `/mpd/nodes` | List MPD nodes with optional policy/owner filters | `schemas.MPDNode` |
| POST | `/mpd/nodes` | Upsert MPD nodes | `schemas.MPDNode` |
| POST | `/mpd/seed/trunk` | Derive BTSM trunk from a vision tensor payload | `vision_tensor -> schemas.MPDNode` |
| GET | `/mpd/edges` | Fetch MPD edges | `schemas.BitemporalEdge` |
| POST | `/mpd/edges` | Upsert edges (policy inheritance enforced) | `schemas.BitemporalEdge` |
| POST | `/mpd/edges/depends-on` | Convenience helper for dependency edges | `schemas.BitemporalEdge` |
| POST | `/mpd/blast-radius` | Simulate dependency impact for change reviews | `BlastRadiusResponse` |
| GET | `/kpi/history` | Return KPI history records for dashboards | `KPIHistoryRecord` |
| GET | `/health` | Liveness probe |

Full FastAPI application lives in `packages/cmc_service/api.py`.

---

## BTSM & Shared Schemas

- BTSM utilities (`packages/cmc_service/btsm.py:27`) translate vision tensor summaries into MPD trunk nodes and `depends_on` edges.
- Shared data models are defined in `packages/schemas/*` (`MPDNode`, `KPIReference`, `BitemporalEdge`) to keep BTSM, API, and migrations in sync.
- Tests validate round‑trips via `packages/cmc_service/tests/test_bitemporal.py` and `test_policy_integration.py`.

---

## Metrics & Logging

`packages/cmc_service/logging_utils.py` configures Prometheus counters/histograms emitted via CLI (`cmc metrics:dump`) or FastAPI endpoints:

| Metric | Description |
| --- | --- |
| `cmc_snapshot_duration_seconds` | Histogram of snapshot creation latency |
| `cmc_write_errors_total` | Total write failures |
| `cmc_atoms_created_total{modality}` | Count of created atoms by modality |
| `cmc_snapshots_created_total` | Total snapshots produced |

Logs are JSON-formatted with correlation IDs to simplify ingestion into SEG/VIF pipelines. Example payload:

```json
{
  "ts": "2025-10-21T12:00:00.123456Z",
  "level": "info",
  "action": "snapshot.create",
  "snapshot_id": "snap:20251021:A1",
  "atom_count": 42,
  "duration_ms": 15.4
}
```

---

## CLI Quick Start

```bash
# Install editable dependencies
pip install -e .[test]

# Initialize SQLite back-end
export CMC_BACKEND=sqlite
export CMC_SQLITE_PATH=./data/cmc.sqlite

# Create atom + snapshot
cmc atoms create --modality text --payload ./examples/sample_atom.json
cmc snapshots create --note "demo"

# Inspect metrics
cmc metrics dump
```

---

## Tests

Run targeted suites or the full battery:

```bash
# Core repository behaviour
pytest packages/cmc_service/tests/test_repository.py

# API + policy integration
pytest packages/cmc_service/tests
```

All suites now rely on the shared `packages/schemas` module for MPD/BTSM parity.

Run the provided script to register the HHNI schema:

```bash
python scripts/hhni_schema_apply.py --dgraph-url http://localhost:8080 --schema schemas/hhni.graphql
```

### CLI Usage

```bash
# Build HHNI nodes from a file (priority ≥ 0.6 triggers automatically)
cmc hhni:build --file docs/example.txt --tag priority:0.7

# Force HHNI build regardless of priority
cmc hhni:build --file docs/example.txt --force
```

The command returns both the newly created atom and the serialized HHNI nodes.

## Status Command

`cmc status` returns a JSON object summarizing the current state:

```json
{
  "atom_count": 120,
  "latest_snapshot": {
    "id": "...",
    "created_at": "2025-10-18T11:30:12.000000Z"
  },
  "counters": {
    "atoms_created_total": {"text": 100},
    "snapshots_created_total": 10,
    "write_errors_total": 0
  },
  "snapshot_duration_ms": [15.4, 16.2],
  "journal_intact": {
    "atoms_log_ok": true,
    "snapshots_log_ok": true
  }
}
```

## Quick Start

```bash
# Ensure virtual environment is active
python -m venv .venv
.venv\Scripts\activate

# Install in editable mode with test extras (HHNI optional extras shown)
pip install -e .[test,hhni]

# Ingest a file as an atom
cmc atoms:create --file analysis\raw\A Total System of Memory.txt --tag source:plan

# Create a snapshot and replay it
cmc snapshots:create --note "Initial import"
cmc snapshots:replay SNAPSHOT_ID

# (Optional) Build HHNI nodes
docker compose -f deploy/docker-compose.yml up -d
cmc hhni:build --file docs/example.txt --tag priority:0.7

# (Optional) Force JSONL backend for legacy comparison
set CMC_BACKEND=jsonl
cmc status
```

Data is stored under `packages/cmc_service/data/` by default. Configure a custom location using `--base-path` on CLI commands or by instantiating `MemoryStore` with a specific directory.

## Tests

Execute the unit suite with:

```bash
.venv\Scripts\pytest
```

The tests cover deterministic snapshot IDs, replay correctness, tag filtering, logging behavior, and HHNI safety gates/parsers.

## Next Steps

- Integrate SEG/VIF exports and parity checks
- Add failure-injection tests for log corruption handling
- Prototype HHNI indexing and hybrid storage backends
- Implement chaos testing for HHNI client retries and circuit breakers
