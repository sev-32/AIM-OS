# Test 8.x Orchestration Comparison Report

This report compares the orchestration executions produced in Tests 8.1–8.5. Every scenario was generated with `packages/orchestration_builder/generator.py` and executed against `gemini-2.0-flash-exp` using `scripts/run_orchestration_executor.py`.

## Summary Table

| Test | Purpose | Agents | Stages | Total Runtime (s) | Avg Agent Runtime (s) | Runtime Range (s) | Audit |
| --- | --- | ---:| ---:| ---:| ---:| --- | --- |
| 8.1 Baseline | Original 28-agent research pipeline | 28 | 6 | 248.33 | 8.87 | 2.71 – 16.09 | `Testing/artifacts/test8_1_research_orchestrator/research_orchestrator/audit/orchestration_run.json` |
| 8.2 Compact | Reduced complexity (10 agents / 3 stages) | 19 | 4 | 183.56 | 9.66 | 5.36 – 12.77 | `Testing/artifacts/test8_2_compact/research_orchestrator_compact/audit/orchestration_run.json` |
| 8.3 Quantum Domain | Same shape, quantum computing topic | 19 | 4 | 201.32 | 10.60 | 7.51 – 17.88 | `Testing/artifacts/test8_3_quantum/quantum_research_orchestrator/audit/orchestration_run.json` |
| 8.4 Policy Stress | Strict governance caps (depth=1, high evidence) | 16 | 4 | 157.16 | 9.82 | 4.29 – 15.97 | `Testing/artifacts/test8_4_policy/policy_stress_test_orchestrator/audit/orchestration_run.json` |
| 8.5 Minimal | Minimal viable (5 agents / 2 stages) | 13 | 3 | 120.17 | 9.24 | 1.07 – 13.68 | `Testing/artifacts/test8_5_minimal/minimal_research_orchestrator/audit/orchestration_run.json` |

_Note_: “Agents” includes the six global orchestration roles; per-stage counts are visible in the audit `stage_breakdown`.

## Scenario Observations

### Test 8.2 – Compact Complexity
- Execution is ~26% faster than baseline while still touching four stages (intake, investigation, delivery, orchestration).
- Outputs remain coherent but still largely describe process guidance rather than domain-specific findings.
- Suggestion: introduce seed evidence snippets to encourage concrete summaries when complexity is reduced.

### Test 8.3 – Alternate Domain (Quantum Computing)
- Runtime increases slightly because Gemini responses are longer; average agent latency grows to 10.6 s.
- Content references quantum terminology only when prompt wording includes it; many outputs still default to meta instructions.
- Domain adaptation is limited without explicit factual context—consider injecting curated briefs per stage.

### Test 8.4 – Policy Stress Test
- Despite strict policies, runtimes stay similar; no evidence of enforced truncation or escalations in outputs.
- Responses acknowledge policy constraints but do not show graceful degradation (no “cannot comply” messaging).
- Recommendation: adjust prompts to explicitly report when thresholds prevent action (e.g., “insufficient evidence, escalating”).

### Test 8.5 – Minimal Viable Orchestration
- Smallest graph (13 agents, three stages) finishes in ~120 s; min latency drops to ~1 s for some outputs.
- Content is still process-oriented, suggesting minimal pipelines retain governance language but need richer context to produce actionable insights.
- Useful baseline for “small-team” workflows once prompt conditioning is improved.

## Quality Trends & Patterns
- **Complexity vs. Quality:** Reducing agents/stages lowers runtime but does not by itself improve outcome quality; Gemini continues to describe operating procedures unless fed concrete evidence.
- **Domain Sensitivity:** Changing topic names alone yields limited adaptation. To achieve specialized narratives, stage prompts should include domain briefs or retrieved facts.
- **Policy Sensitivity:** Tight constraints are acknowledged textually but not enforced behaviorally. Adding explicit instructions about what to do when policies block work (e.g., emit escalation notices) should help.
- **Minimal Footprint:** Even the minimal test preserves global governance agents, which keep audits comprehensive. Useful for lightweight orchestrations once prompt tuning delivers factual output.

## Recommendations
1. **Enrich prompts with seed evidence** (citations, bullet facts) so agents produce substantive domain content rather than meta-guidance.
2. **Add explicit escalation behaviors** to policy-sensitive prompts—have agents emit “insufficient evidence / exceeded latency budget” messages when thresholds are hit.
3. **Consider staged fine-tuning or few-shot examples** for specialist domains (quantum, urban planning, blockchain) to drive domain-aware language.
4. **Capture structured metrics automatically** (agent count, runtime stats) inside the executor to streamline future comparison reports.

All artifacts (audits + outputs) reside under `Testing/artifacts/test8_x_*` for detailed review.
