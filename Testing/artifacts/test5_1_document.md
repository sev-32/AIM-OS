# AIM-OS Architecture Overview

Structured brief describing the five core invariants and their interactions.

## Context Memory Core (CMC)
CMC captures every observation with reversible snapshots and bitemporal lineage.

- Guarantees perfect recall across sessions
- Supports policy-aware dependency tracking
- Feeds SEG with atomized evidence

## Shared Evidence Graph (SEG)
SEG reconciles decisions, detects contradictions, and anchors provenance for audits.

- Records decision conflicts with auto-resolution guidance
- Aligns with VIF for governance checks

## Policy-Aware Blast Radius
Preventive guardrails simulate change impacts before execution, enforcing policy packs.

- Calculates dependency fan-out
- Blocks violations prior to merge
- Produces human-readable violation reports

## Provenance
Generated at: 2025-10-21T04:03:01.615576Z
Seed file: C:\Users\bombe\OneDrive\Desktop\AIM-OS\Testing\samples\document_seed_sample.json
Metadata: {
  "author": "AIM-OS automated builder",
  "version": "0.1",
  "seed_id": "doc-seed-sample-001"
}
