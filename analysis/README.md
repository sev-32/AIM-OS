# Analysis Workspace Guide

This folder is **memory-native**: every doc is destined for atomization, snapshots, and SEG lineage.

## Ritual
1. Draft or edit materials under `analysis/` (themed bundles, summaries, notes).
2. Run `pnpm ingest:analysis` (see `scripts/ingest-analysis.ts`) to write atoms → snapshots → SEG edges.
3. Reference resulting snapshot IDs (`snap:...`) and SEG nodes in themed docs, plans, and ADRs.

## Structure
- `raw/` – text exports of source DOCX/PDF assets.
- `core_map.md` – structural outline of the master thesis.
- `MASTER_INDEX.md` – invariants, document cross-links, external proposals.
- `supporting_docs_catalog.csv` & `supporting_docs_notes.md` – metadata + summaries with invariant tags.
- `themes/` – deep analysis per subsystem (memory, orchestration, safety, governance, observability).
- `summaries/` – tiered summaries for different context budgets (overview, mid, deep).
- `chunks/` – generated plan chunks tracked in `chunks/index.json`.
- `PLAN.md` – collaborative master plan and external ideas.

## Conventions
- Tag docs with invariants: `[CMC]`, `[APOE]`, `[VIF]`, `[SDF-CVF]`, `[SEG]`.
- Cite using snapshot IDs or SEG node references.
- Open questions use `> ?: ...` blocks; observability aggregates them.
- Keep tone concise and evidence-oriented; log rationale + sources for major changes.

## Tooling
- `scripts/build_chunks.py` – refresh summaries, chunks, registry metadata.
- `scripts/ingest-analysis.ts` – pushes markdown into CMC (atoms/snapshots/SEG).
- `analysis/chunks/index.json` – discovery map for chunks and summaries (id, path, tokens, tags).

## Next Steps
- Populate themed bundles with synthesized insights and backlog items.
- Enrich supporting notes and map them to invariants.
- Coordinate with APOE plans (`plans/*.acl`) to ensure analysis outputs feed executable workflows.
