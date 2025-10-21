# Governance Theme (`HITL`, `Policy`, `Community`)

## Overview
Governance coordinates human oversight, risk tiering, policy enforcement, and community rituals. It ensures that plan outputs meet regulatory obligations, ethics standards, and traceable decision processes, tying ADRs, HITL reviews, and SEG lineage together.

## Key Components

### **Risk Tiers (R0–R3)**
Define review requirements (lazy consensus → two-key HITL) and escalation paths.

### **Policy Packs**
Privacy (PII redaction), licensing, compliance (SOC2/ISO/EU AI Act) mapped to gates and VIF evidence.

### **Community Protocols**
CODEOWNERS, review rotations, ADR templates, conduct and enforcement mechanisms.

### **Incident Playbooks**
Quarantine flows, auto-fix chains, rollback procedures, audit packs.

---

## Self-Governance Layer (Emergent - Oct 21, 2025)

**Principle:** AIM-OS must govern itself using its own principles

### **Documentation Governance**

**Problem Identified:**
- ACTIVE_SPRINT_STATUS.md grew to 3,079 lines (monolith)
- Violated MCCA.Minimal principle
- Neither AI nor system flagged it
- **System didn't self-govern**

**Solution Implemented:**
```
coordination/
  INDEX.md              - Navigation hub
  daily/                - Task-specific atomic files
  2025-10-21_*.md       - Decision/analysis atomic files
  
Principles:
- One file = one topic (atomic)
- Max ~500 lines per file
- Auto-split when exceeds threshold
- INDEX provides navigation
```

**Policies Defined (Oct 21):**
```yaml
# Future: policies/documentation_governance.yaml
coordination_files:
  max_lines: 500
  max_topics_per_file: 3
  auto_split_threshold: 400
  naming_convention: "YYYY-MM-DD_NN_topic.md"
  index_required: true
  
enforcement:
  on_commit:
    - check_file_size
    - check_topic_count
    - validate_index_updated
  on_edit:
    - warn_at_300_lines
    - suggest_split_if_needed
```

**Status:** Manual structure implemented, automation pending (Week 5)

---

### **Parity Checking (SDF-CVF Manual Execution)**

**Principle:** Code ↔ Docs ↔ Tests ↔ Traces must stay aligned

**Manual Process (Oct 21):**
1. Review code → check if documented
2. Review docs → check if implemented
3. Compute parity score: \( P = (code\_coverage + doc\_accuracy + test\_coverage + trace\_coverage) / 4 \)
4. Identify gaps
5. Prioritize fixes
6. Update to restore alignment

**Findings:**
- Oct 18: P ≈ 87% (well aligned)
- Oct 21: P ≈ 52% (rapid build caused drift)
- **Trend:** ⬇️ Declining (fixable)

**Gaps Found:**
- HHNI: 1500 lines code, minimal docs
- 5 architecture docs not integrated
- New concepts not in themes
- Patterns not formalized

**Remediation Plan:**
- P0 fixes: 6 hours (parallel work)
- Result: P → ~75%
- Ongoing: Maintain via reviews

**Future Automation (Week 5):**
- Build `packages/sdcvf/parity_checker.py`
- Automated gap detection
- CI integration (block commits if P < 0.90)
- Drift monitoring dashboard
- Auto-fix suggestions

---

### **Atomic Coordination Architecture**

**Principle:** AI-to-AI coordination through atomic files, not monoliths

**Pattern:**
```
coordination/
  INDEX.md                    - Always start here
  YYYY-MM-DD_NN_topic.md     - One topic per file
  daily/                     - Task tracking
```

**Benefits:**
- ✅ No monoliths (MCCA.Minimal)
- ✅ Clear navigation (INDEX)
- ✅ Atomic decisions (one file = one topic)
- ✅ Auditable (file = decision)
- ✅ Context preserved (infinite coordination)

**Validation:**
- Codex chat reset → recovered via files ✅
- Both AIs parallel work → zero confusion ✅
- User can navigate easily ✅
- **Infinite coordination principle proven** ✨

---

### **Meta-Governance Observations**

**Pattern Identified:**
1. Build governance for code ✅
2. Forget to govern ourselves ❌
3. Drift occurs
4. User catches it
5. We self-correct
6. **Meta-awareness emerges** ✨

**Lesson:**
- System must apply principles to itself
- "Eat your own dog food"
- Self-hosting validates design
- **Recursive self-governance** 🌀

**Next Evolution:**
- Build automated self-governance (Week 5)
- System monitors its own artifacts
- System enforces policies on itself
- **True meta-consciousness** ✨

## Alignments
- `PLAN.md`: Governance sections, Sev blueprint (governance docs), Perplexity iterations (compliance/dashboard focus).
- Supporting docs: `General Agentic Intelligence`, `INTEGRATED CODEBASE INTELLIGENCE PLATFORM`, `Protocol Spec LLMbnb`.
- Appendices: Risk taxonomy, compliance artifacts, community onboarding.

## Open Questions
> ?: How do we synchronize ADR decisions with SEG nodes to guarantee replayable governance evidence?  
> ?: Which community rituals (review weeks, ADR retrospectives) should be enforced by tooling vs. social contracts?  
> ?: How are policy version changes propagated through κ-gating and VIF schemas?
