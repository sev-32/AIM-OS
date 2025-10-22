# Part I: First Principles & Invariants

**Chapters:** 1-3  
**Length:** ~8,000 words  
**Purpose:** Establish why AIM-OS must exist and define core axioms  
**HHNI Level:** SECTION

---

## 📊 **500-Word Summary**

Part I establishes the foundational thesis that large language models are not "chatbots" but **machine-communication engines**—systems that mediate between humans, documents, tools, and code. Current AI fails catastrophically in five ways: context loss (ephemeral windows force forgetting), hallucinations (no grounding or witnesses), improvisation (one-shot prompting with no planning), black-box opacity (no replay or audit capability), and drift (code/docs/tests diverge over time). These aren't bugs—they're architectural gaps that cannot be fixed with better prompts or bigger models.

**Chapter 1 (The Why)** presents six transitions that define the solution: from ephemeral context to structured memory (CMC), from improvisation to compilation (APOE), from claims to witnesses (VIF), from drift to atomic evolution (SDF-CVF), and from documents to evidence graphs (SEG). The machine-communication thesis argues that LLMs should operate as protocol translators with perfect memory, verifiable outputs, and self-improvement capability.

**Chapter 2 (System Axioms)** formalizes five invariants with mathematical definitions:

1. **Memory Invariant (CMC):** ∀ context c, ∃ reversible mapping c ↔ atom a
2. **Orchestration Invariant (APOE):** ∀ plan p, ∃ budget b | execution(p) ≤ b  
3. **Witness Invariant (VIF):** ∀ output o, ∃ provenance w | trace(o) → w
4. **Substrate Invariant (SEG):** ∀ claim c, ∃ evidence e in temporal graph
5. **Evolution Invariant (SDF-CVF):** ∀ change Δ, parity(code,docs,tests,traces) ≥ P_min

Each invariant includes formal statement, proof obligations, and counter-examples showing systems without the invariant fail. Design constraints derived from axioms establish requirements: single-writer (C-1), snapshot immutability (C-2), provenance completeness (C-3), budget enforcement (C-4), κ-gating (C-5), parity requirement (C-6), time ordering (C-7), and evidence linkage (C-8).

**Chapter 3 (Design North Star)** introduces the C-3PO workshop metaphor (roles and scopes for specialized agents), explains safety-as-capability through κ-gating and abstention semantics, and presents the IDE-in-the-loop rationale—why development environments must integrate verification directly. The threat model preview (detailed in Part VIII) shows STRIDE×LLM attack vectors: prompt injection, RAG poisoning, exfiltration, tool abuse, SSRF, context flooding, supply-chain compromise, provenance forgery, HITL bypass, and policy rot. Each threat has specific controls tied to invariants.

**Key Relationships:**
- Part I feeds all subsequent parts (axioms are referenced throughout)
- Invariants in Chapter 2 become implementation specs in Parts II-VI
- Design constraints become gates in APOE (Part IV) and SDF-CVF (Part VI)
- Threat model connects to Security (Part VIII) and VIF/SEG (Part V)

**Implementation Status:**
- Axioms: ✅ Formalized and documented
- Invariants: ✅ 4/6 partially implemented (CMC 75%, HHNI 95%, APOE 55%, VIF 30%, SEG 35%, SDF-CVF 50%)
- Design constraints: ✅ Most enforced in code (C-1, C-2, C-3 operational; C-4, C-5, C-6, C-7, C-8 partial)

**Evidence:**
- Tests validate single-writer (C-1): `test_memory_store.py`
- Tests validate snapshot immutability (C-2): `test_snapshot_deterministic`
- Witness emission (C-3): `packages/seg/witness.py` operational
- Budget tracking (C-4): `budget_manager.py` working but not fully enforced
- κ-gating (C-5): In prompts, not yet behavioral
- Parity (C-6): Policy framework exists, not automated
- Time ordering (C-7): Timestamps in all atoms
- Evidence linkage (C-8): SEG witnesses connected

---

## 🎯 **Key Takeaways from Part I**

1. **AI needs cognitive architecture, not just bigger models**
2. **Five invariants are provably necessary for trustworthy AGI**
3. **Design constraints derive mathematically from invariants**
4. **Threat model shows what happens without invariants**
5. **Safety is capability (κ-gating), not post-hoc checking**

---

**Next:** `part_02_cmc_hhni.md` - Memory & Indexing architecture  
**Or:** `level_3_paragraphs/part_01/` for deeper dive into specific topics

