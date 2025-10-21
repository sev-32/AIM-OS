# Safety & Trust Theme (`VIF`, `Policy`, `Threat Model`)

## Overview
Safety is treated as capability: plans abstain or degrade when risk exceeds κ thresholds. VIF (Verifiable Intelligence Framework) ensures every boundary emits signed, replayable witnesses with uncertainty vectors; policy gates enforce capability boundaries and guardrail compliance.

## Key Mechanics
- **VIF Envelopes:** Include actor, snapshot, model, prompt template, tool calls, uncertainty metrics (entropy, ECE, band), and kappa decision.
- **Shared Evidence Graph:** Witness and claim nodes form time-sliced provenance; contradictions and support edges document trust.
- **Policy Gates:** Hard predicates (e.g., disallowed domains, PII exfil) cause abort; soft predicates trigger degrade/reroute/HITL.
- **Degrade Modes:** Context diet, template hardening, safe-mode tools, temperature sweeps; budget-aware κ adaptations.

## Alignments
- `PLAN.md`: Safety sections, Perplexity Iter. 1–3 (uncertainty, HITL), Sev blueprint (vif-service, sdcvf-gatekeeper).
- Supporting docs: `INTEGRATED CODEBASE INTELLIGENCE PLATFORM`, `General Agentic Intelligence`, `The Token Problem` (uncertainty), `VORTEX` (interpretability).
- Operator console: lineage panel, confidence chips, gate explanations.

## Open Questions
> ?: What calibration suites (ECE bins, stratified domains) are required to keep κ thresholds reliable?  
> ?: How do we surface real-time risk dashboards (κ abstentions, policy violations) without overwhelming users?  
> ?: What is the escalation workflow for contradictions in SEG when adversarial inputs are detected?  
