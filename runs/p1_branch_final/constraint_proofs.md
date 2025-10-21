# MIGE Branch Constraint Proofs (seg:witness:1f5d8a0a-bac8-42bd-8423-b9e0b5ec6c77)

### Variant: aimos.mige.trunk::variant-a
- **Budget bound:** Branch retains the parent budget band `analysis:medium`. The ACL execution emits a single meta-optimizer call with measured cost 0.48 units (see APOE metrics log), therefore `cost_branch <= cost_budget (0.48 ≤ 1.00)`.
- **Dependency ceiling:** `max_dependency_degree = 8` equals the trunk ceiling; inequality `8 ≤ 8` recorded in SEG payload.
- **SEG artefact linkage:** Witness above stores hash `h_budget_branch_a` (budget check) and `h_degree_branch_a` (ceiling verification).

### Variant: aimos.mige.trunk.guardrails::variant-a
- **Budget bound:** Uses governance oversight only; recorded workload 0.32 within `governance:low` envelope, satisfying `0.32 ≤ 1.00`.
- **Dependency ceiling:** `max_dependency_degree = 4` matches trunk guardrail ceiling, satisfying `4 ≤ 4`.
- **SEG artefact linkage:** Witness includes hashes `h_budget_guardrail_a` and `h_degree_guardrail_a`, plus parity gate witness `seg:witness:c809c7c0-1def-461e-9fd9-8e298e88930d`.

These proofs clear the TODO in `plans/branch_to_specs.acl` and unblock Phase P2.
