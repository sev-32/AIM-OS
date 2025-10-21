# Observability & Validation Theme (`Metrics`, `Telemetry`, `Replay`)

## Summary
Observability ties metrics, telemetry, and validation harnesses to each invariant. Instrumentation spans plan execution, retrieval pipelines, safety gates, and evolution workflows, feeding dashboards and operator-console views.

## Retrieval (CMC/HHNI)
- Metric: RS-lift vs. static baseline (target ≥ +15% @ p@5).
- Gate: κ abstain if RS < 0.35 or ECE > 0.05.
- Telemetry: DVNS convergence traces, glyph state distributions, snapshot replays.

## Orchestration (APOE)
- Metric: Replay match ≥ 99% for accepted traces.
- Gate: any step band ∈ {C, D} ⇒ ABSTAIN or HITL.
- Telemetry: plan DAG execution spans, κ gate decisions, tool budgets.

## Provenance (VIF/SEG)
- Metric: Lineage coverage = 100%; no orphan claims.
- Export: VIF + SEG packs with replay recipes validated nightly.
- Telemetry: witness emission rate, contradiction alerts.

## Atomic Evolution (SDF-CVF)
- Metric: Parity score P ≥ 0.90.
- Gate: below θ ⇒ QUARANTINE + autofix plan.
- Telemetry: parity trends, drift monitors, quarantine resolution times.

## Operator Console Hooks
- Lineage view with “Why Paused?” explanations.
- Confidence bands and κ status chips.
- Replay button with frozen inputs (witness-backed).

## Open Questions
> ?: How do we unify telemetry schemas (OTel) across packages to ensure cross-service trace stitching?  
> ?: What synthetic workloads validate replay fidelity across major plan types?  
> ?: Can we automate κ calibration drift detection using SEG evidence packs?
