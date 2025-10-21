# Memory-to-Idea Growth Engine (MIGE) for AIM-OS

_Last updated: 2025-10-20_

## 1. Purpose
AIM-OS already preserves perfect memory (CMC, HHNI, SEG) and orchestrates work (APOE, SDF-CVF). MIGE supplies the missing repeatable engine that turns human intent into auditable, deployable systems while keeping change under governance. It does this by combining the Bitemporal Total System Map (BTSM) with the Harmonised Verifiable Cognitive Architecture (HVCA).

## 2. Source Blueprints
- **Bitemporal Total System Map (BTSM):** Living inventory of every subsystem, dependency, and policy pack. Each node carries Minimal-Perfect-Details (MPD): `id`, `type`, `purpose`, `capabilities`, `interfaces`, `manager_of[]`, `depends_on[]`, `policy_pack_ids[]`, `budgets`, `owners`, `kpis`, `lifecycle`, `witness`, `links`. Edges are stamped with transaction and valid times so the map can be replayed.
- **Harmonised Verifiable Cognitive Architecture (HVCA):** Three-mind neuro-symbolic loop. Mind 1 (Meta-Optimizer) shapes the vision tensor, Mind 2 (Context Retriever) gathers context slices with DVNS and REX-RAG, and Mind 3 (Constraint Enforcer) ensures feasibility using symbolic reasoning and MCCA scores. Minds coordinate through APOE and every exchange emits VIF evidence.

## 3. Conceptual Flow
```
Human Seed -> Vision Tensor (Mind 1)
           -> BTSM Trunk Index (Mind 2)
           -> Branch Blueprints (Mind 2)
           -> Design Proofs and KPI Packs (Mind 3)
           -> Atomic Commit + SEG Witness + Deploy (SDF-CVF)
```
Each transition is guarded by APOE gates and produces artefacts that land in the evidence graph.

## 4. Seed-to-Perfect Pipeline
| Stage | Description | Primary Gates | Resulting Artefacts |
|-------|-------------|---------------|---------------------|
| A | Seed and vision tensor | `g_vision_fit` (>= 0.90) | Vision capsule, strategy brief |
| B | Trunk indexing | `g_trunk_coherence`, `g_scope_coverage` | BTSM trunk nodes with MPD payloads |
| C | Branch variants | `g_variant_parity`, `g_budget_guard` | Blueprint trio with blast-radius notes |
| D | Leaf proofs | `g_symbolic_consistency`, `g_test_parity` | Proof bundles, executable tests |
| E | Evolution controls | `g_two_key`, `g_rollback_ready` | Signed SEG packets, deployment checklist |

## 5. Implementation Roadmap
1. **Weeks 1-2: Foundation**
   - Extend SEG schema with `tt_start`, `tt_end`, `vt_start`, `vt_end`.
   - Introduce `schemas/mpd.py` (Pydantic) and `schemas/edge.py` to enforce MPD structure.
2. **Weeks 3-4: Vision Tensor**
   - Create `packages/meta_optimizer/` with prompts, embeddings, and VisionFit scoring.
   - Add `g_vision_fit` gate to the SDF-CVF guardrail catalogue.
3. **Weeks 5-8: BTSM CRUD and UI alpha**
   - Extend `packages/cmc_service` with `/nodes`, `/edges`, `/blast-radius` endpoints.
   - Prototype React UI (tree plus graph plus impact heatmap) in `deploy/console`.
4. **Weeks 9-12: Full HVCA loop**
   - Build retriever adapters (DVNS slice, REX-RAG) and symbolic enforcer services.
   - Publish APOE plan templates: `seed_to_tensor.acl`, `tensor_to_trunk.acl`, `branch_to_specs.acl`.
5. **Weeks 13-16: Safety and scale**
   - Wire Harmony Search tuning, Two-Key governance workflow, and regression KPIs.
   - Land dashboards in `benchmarks/dashboards/` for VisionFit, Lineage Completeness, Blast-Radius score.

## 6. Integration Touchpoints
- **Memory layer:** `packages/cmc_service/memory_store.py` stores MPD payloads and SEG identifiers. Add MPD helpers and time-slice queries.
- **Planning layer:** `ideas/REGISTRY.md` and `analysis/PLAN.md` reference the roadmap and assign owners for each gate.
- **Execution layer:** `packages/apoe_runner/` (planned) consumes the ACL templates and triggers meta-optimizer, retriever, and enforcer actions.
- **Governance layer:** `AI_HANDOFF_CONTROL.md` tracks Two-Key signers, while `goals/KPI_METRICS.json` records VisionFit, Lineage Completeness, Replay Rate, and Lead Time.
- **Automation:** Scripts under `scripts/` will emit SEG witness packets and refresh BTSM views (`scripts/build_btsm_snapshot.py`, planned).

## 7. Core KPIs
| KPI | Target | Captured in |
|-----|--------|-------------|
| VisionFit cosine alignment | >= 0.90 | `goals/KPI_METRICS.json` |
| Lineage completeness | >= 95% | SEG lineage audit |
| Blast-radius false negatives | 0 | APOE audit trail |
| Replay success rate | >= 99% | SEG replay harness |
| Idea-to-deploy lead time | <= 14 days | Operations dashboard |

## 8. Risks and Mitigations
- **Coupling explosion:** Mitigate with blast-radius sentries, dependency ceilings (per-node `max_dependency_degree` defined in `schemas/mpd.py`), and MCCA enforcement before commits.
- **Model drift:** Continuous VisionFit scoring, ensemble prompts, and fallback symbolic checks keep Mind 1 aligned.
- **Policy violations:** APOE plan gates reference policy packs; ACL execution fails closed and records violation context.
- **Governance fatigue:** Two-Key flow rotates reviewers and automates sign-off reminders through `AI_HANDOFF_CONTROL.md`.

## 9. Operating Principle
Every artifact produced by MIGE must be an atomic, witnessed commit. When in doubt, favour traceability over cleverness; evidence-first evolution keeps AIM-OS safe to scale.
