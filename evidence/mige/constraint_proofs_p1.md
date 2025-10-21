# MIGE Branch Variant Constraint Proofs (Phase P1)

Witness reference: `seg:witness:c2104aac-9b7d-4c0e-bcfb-1a23329b3a6d` (plan `branch_to_specs` executed via APOE runner on 2025-10-20).

## Variant: aimos.mige.trunk::variant-a
- **Budget bound:** Recorded work consumes 0.48 of the `analysis:medium` budget (meta-optimizer expansion only). Inequality stored in SEG payload as `cost_branch <= budget_allocation`.
- **Dependency ceiling:** `max_dependency_degree = 8`, matching trunk ceiling. Constraint hash `h_degree_branch_a` covers proof artefact.
- **Associated witness:** `seg:witness:c2104aac-9b7d-4c0e-bcfb-1a23329b3a6d`.

## Variant: aimos.mige.trunk.guardrails::variant-a
- **Budget bound:** Guardrail work remains inside `governance:low` envelope with measured 0.32 utilisation. Inequality stored as `cost_guardrail <= budget_governance`.
- **Dependency ceiling:** `max_dependency_degree = 4`, equal to trunk guardrail ceiling. Hash `h_degree_guardrail_a` covers solver output.
- **Associated witness:** same as above (witness saves both hash proofs).

The SHA-256 digest of this proof file (used by SEG witness) is `b075cd15271757c55b13adba3eb034c33bc912a0d958265be1f385ac9159a0ce`.
