# AIM-OS Total System Map

_Last updated: 2025-10-20 (o3 integration)_

## 1. Purpose
This map anchors the Memory-to-Idea Growth Engine (MIGE) inside the wider AIM-OS corpus. It gives contributors a single place to see what exists, how artefacts relate, and where to plug in code and governance changes.

## 2. Document Inventory
### 2.1 Foundation Sources
- `Documentation/A Total System of Memory.docx` - core thesis defining the five invariants.
- `Documentation/AEONWAVE.docx`, `Documentation/General Agentic Intelligence.docx`, `Documentation/Multi-Agent Helixion Ensemble Architecture.docx` - supporting architectures for memory and orchestration.
- `Documentation/memory into idea.docx`, `Documentation/total system map.docx` - seed material that informs MIGE.

### 2.2 Analysis Layer (`analysis/`)
- `PLAN.md`, `MASTER_INDEX.md`, `IMPROVEMENTS_LOG.md`, `SYSTEM_STATUS.md`.
- Themed syntheses in `analysis/themes/` plus three-tier summaries in `analysis/summaries/`.
- Raw extracts under `analysis/raw/` and semantic chunks in `analysis/chunks/`.

### 2.3 Collaboration Layer (`ideas/`)
- `REGISTRY.md`, `TEAM_INFRASTRUCTURE.md`, `TEAM_SCHEDULE.md`, `ROLE_AWARENESS_MATRIX.md`.
- Active idea folders (architects, builders, integrators, analysts, guardians, designers, philosophers).
- Templates and onboarding flows (`ideas/templates/SEED.md`, `ideas/START_HERE.md`).

### 2.4 Automation and Scripts (`scripts/`)
- `build_chunks.py`, `ingest-analysis.ts`, `run-plan.ts`, `seed-seg.ts` (planned).

### 2.5 Governance and Status
- `AI_HANDOFF_CONTROL.md`, `BRADEN_STATUS_UPDATE.md`, `LOW_COST_EXEC_PLAN.md`, `MISSION_ACCOMPLISHED.md`, `QUICK_REFERENCE.md`.

## 3. Concept Mesh
- **BTSM:** Tracks subsystems with MPD payloads and temporal edges. Feeds roadmap gating and blast-radius analysis.
- **HVCA:** Mind trio (meta-optimizer, retriever, constraint enforcer) drives idea maturation under APOE.
- **SEG:** Evidence graph linking every artefact back to source and validation witnesses.
- **SDF-CVF:** Ensures code, docs, tests, and proofs move together under gating.
- **MIGE:** The operational loop binding BTSM and HVCA to deliver safe, auditable evolution.

All BTSM node identifiers must follow the `mpd_id` convention defined in `schemas/mpd.py` so blast-radius queries and MPD lookups stay aligned.

## 4. Implementation Touchpoints
| Domain | Key Paths | Notes |
|--------|-----------|-------|
| Memory graph | `packages/cmc_service/memory_store.py`, `schemas/` | Add MPD models, time-slice queries, SEG keys. |
| Planning engine | `packages/apoe_runner/` (planned), `ideas/REGISTRY.md` | Store ACL templates (`seed_to_tensor`, `tensor_to_trunk`, `branch_to_specs`). |
| Evidence | `packages/cmc_service/models.py`, `benchmarks/` | Extend SEG schema with bitemporal fields and replay harness. |
| Governance | `AI_HANDOFF_CONTROL.md`, `goals/KPI_METRICS.json` | Track Two-Key reviewers (Braden - Product, Opus 4.1 - Guardian) and KPIs (VisionFit, Lineage Completeness, Replay Rate, Lead Time). |
| Experience | `deploy/console/`, `docs/` | UI for BTSM tree, graph neighbourhood, and blast-radius explorer. |

## 5. Change Tracking
1. **Source of Truth:** Git history plus SEG witnesses once automation lands.
2. **Manual Logs:** `analysis/IMPROVEMENTS_LOG.md`, `ideas/*/ONBOARDING_LOG.md`, `BRADEN_STATUS_UPDATE.md`.
3. **Registry Hooks:** `ideas/REGISTRY.md` records status of each initiative.
4. **Future Enhancements:** configure `scripts/change_watch.py` (planned) to detect cross-file drift and update master index automatically.

## 6. System Maturity Snapshot
| Capability | Status | Notes |
|------------|--------|-------|
| Vision and architecture | High | Extensive source corpus and indexed analyses. |
| Documentation hygiene | Medium | Major guides refreshed, some legacy artefacts pending ASCII cleanup. |
| Implementation | Low | Core services scaffolded, execution runners outstanding. |
| Validation | Low | KPI definitions drafted; harnesses and dashboards to be built. |
| Operations | Emerging | Governance rituals captured; automation in backlog. |

## 7. Critical Path
1. **Perfect the map:** Solidify MPD schema, align BTSM nodes with `analysis/PLAN.md` section 4.1 owners, and publish updated registry slices.
2. **Instrument MIGE:** Stand up meta-optimizer package, retriever adapters, symbolic enforcer, and APOE gating.
3. **Automate evidence:** Emit SEG packets for each pipeline stage and surface KPIs in `goals/KPI_METRICS.json` dashboards.
4. **Scale safely:** Enable Harmony Search, Two-Key governance, blast-radius sentries, and continuous replay drills.

## 8. How to Use This Map
1. Start with `Documentation/MEMORY_TO_IDEA_INTEGRATION_GUIDE.md` for the fused blueprint.
2. Consult this total map to understand where artefacts live and how they connect.
3. Branch into `analysis/PLAN.md` for current execution priorities.
4. Register work in `ideas/REGISTRY.md` and capture witnesses in SEG once automation is live.

The map is self-updating: each roadmap revision should reference this file, ensuring AIM-OS stays traceable from concept to deployment.
