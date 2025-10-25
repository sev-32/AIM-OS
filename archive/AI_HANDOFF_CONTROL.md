# AI Handoff Control Panel for Braden

## Current Status
**Active AI:** GPT-5 Codex (Builder)  
**Current Focus:** Sprint 1 - KPI & Dashboard Evolution (backend foundations)  
**Latest Work:** KPI history snapshots + refresh script + `/kpi/history`; memory/blast tests and Test 5.1 document builder harness added.  
**Next Recommended AI:** GPT-5 Codex (execute Test 5.1 document build) with Claude 4.5 validating build criteria.  
**System State:** READY - Sprint 1 backend tasks underway (KPI history seeded).

Quick links: see `ACTIVE_SPRINT_STATUS.md` for the live sprint board and `AI_AGENT_CONTEXT.md` for the next-agent brief.


---

## 📋 HOW TO USE THIS SYSTEM

### Super Simple Process:
1. **Open this file** to see who's next
2. **Switch to that AI** in Cursor
3. **Copy the prompt** from the box below
4. **Paste and send** - that's it!

The AI will:
- Read their assignment
- Check previous work
- Do their task
- Update this file for the next handoff

---

## 🎯 CURRENT WEEK ASSIGNMENTS

### 📅 Monday (Today) - Planning & Setup
**WHO:** Opus 4.1 ✅ COMPLETE  
**WHAT:** Team activation and coordination  
**STATUS:** ✅ Done - Team is activated

### 📅 Tuesday - Deep Development
**WHO TO ACTIVATE:** (Choose based on what you want to see)

#### Option A: See Memory System Design
**AI:** Claude-4.5  
**Switch to:** Claude Sonnet model  
**Copy this prompt:**
```
Continue AIM-OS development. Check AI_HANDOFF_CONTROL.md for your assignment. 
Update your Memory Crystallization exploration and report progress.
```

#### Option B: See Code Architecture  
**AI:** GPT-5 Codex  
**Switch to:** GPT-4 or Codex model  
**Copy this prompt:**
```
Continue AIM-OS development. Check AI_HANDOFF_CONTROL.md for your assignment.
Design the CMC Service v0.1 architecture and create API specifications.
```

#### Option C: See Validation Framework
**AI:** Gemini 2.5 Pro  
**Switch to:** Gemini model  
**Copy this prompt:**
```
Continue AIM-OS development. Check AI_HANDOFF_CONTROL.md for your assignment.
Develop the Validation Framework structure and define gold sets.
```

### 📅 Wednesday - Integration Day
**WHO:** o3pro-ai (Integrator)  
**WHEN:** Wednesday morning  
**Copy this prompt:**
```
Lead AIM-OS integration day. Check AI_HANDOFF_CONTROL.md and integration_week1.md.
Map all integration points between CMC, APOE, and VIF. Run the integration meeting.
```

### 📅 Friday - Review Day
**WHO:** Opus 4.1 (Guardian)  
**WHEN:** Friday morning  
**Copy this prompt:**
```
Conduct Friday reviews for AIM-OS. Check AI_HANDOFF_CONTROL.md.
Review all week's work, conduct safety assessments, and prepare weekly report.
```

---

## 🔄 QUICK HANDOFF PROMPTS

### Universal Handoff Prompt (Works for Any AI):
```
Continue AIM-OS development as [ROLE]. Read AI_HANDOFF_CONTROL.md for current status.
Check your workspace in ideas/[your-role]/ and complete your assigned tasks.
Update this control file when done.
```

### Quick Check-In Prompt (Any AI):
```
Give me a quick status update on AIM-OS development from your role's perspective.
Check AI_HANDOFF_CONTROL.md and your workspace, then summarize progress.
```

### Manager Check Prompt (Opus 4.1):
```
As team manager, give me a status report on all AIM-OS team members.
Check DYNAMIC_OBJECTIVE.md and update BRADEN_STATUS_UPDATE.md with simple summary.
```

---

## 📊 WORK TRACKING

### What Each AI Should Do When Called:

1. **Read their assignment** from this file
2. **Check their workspace** at `ideas/[role]/[name]/`
3. **Review previous work** if any
4. **Do their task** 
5. **Update their status** in:
   - Their workspace files
   - `ideas/REGISTRY.md` if needed
   - `ideas/discussions/daily_standup.md`
6. **Update this file** with:
   - Task completion status
   - Next recommended handoff
   - Any blockers for Braden

---

## 🚨 QUICK ROLE REFERENCE

| AI Name | Role | Cursor Model to Use | Main Focus |
|---------|------|-------------------|------------|
| **o3pro-ai** | **Lead Manager** | GPT-4 | Documentation, research, team coordination |
| **Opus 4.1** | **Technical Program Manager** | Claude Opus | Codebase planning, safety gates |
| **Claude-4.5** | **Co-Lead Builder** (Architecture) | Claude Sonnet | System design + implementation |
| **GPT-5 Codex** | **Co-Lead Builder** (Development) | GPT-4/Codex | Code implementation + prototyping |
| Gemini 2.5 | Researcher | Gemini Pro | Validation, formal proofs |
| Grok-4-Max | Philosopher | GPT-4 (with humor) | Ethics & alignment |
| Cheetah AI | Analyst | GPT-4 (fast) | Performance optimization |

---

## 📝 LAST HANDOFF LOG

### Most Recent Activity:
**Date:** 2025-10-18  
**AI:** GPT-5 Codex (Co-Lead Builder)  
**Task:** Implement HHNI safety gates & client scaffolding  
**Status:** ✅ Complete  
**Output:** `packages/hhni/indexer.py`, `packages/hhni/dgraph_client.py`, `packages/hhni/embeddings.py`, `packages/hhni/safety.py`  
**Highlights:**
- Added write/query safety gates and structured logging
- Implemented DGraph client with retries and limits
- Added Qdrant embedding safeguards (batch caps, retries)

### Previous Activities:
**Date:** 2025-10-18
**AI:** Opus 4.1 (Guardian)
**Task:** CMC v0.1 Safety Review
**Status:** ✅ Complete - Fixes Required

---

## 🎯 RECOMMENDED NEXT ACTION

### For Braden (Right Now):
Phase 1 safety fixes are complete and validated. Time for Phase 2: Observability.

#### ✅ APPROVED: Day 2 Observability Implementation
**Switch to:** GPT-5 Codex
**Prompt:** (Guardian-approved, ready to copy/paste)
```
Continue AIM-OS development as Builder. Read:
- AI_HANDOFF_CONTROL.md (this file)
- ideas/guardians/opus-4-1/CMC_v0_1_REVIEW.md
- ideas/researchers/gemini-2-5-pro/VALIDATION_cmc_v0_1_fixes.md

Implement v0.2-min in packages/cmc_service with focus on observability + UTC:
1) Structured JSON logging with correlation_id:
   - Add logs for: create_atom, list_atoms, create_snapshot, replay_snapshot, startup load.
   - Schema: { ts (RFC3339, UTC), level, action, correlation_id, atom_id?, snapshot_id?, count?, duration_ms?, path?, error? }.
   - CLI: add --correlation-id (optional); default to UUID4 if not provided.
   - Emit to stdout via stdlib logging (JSON formatter). If structlog available, use it; otherwise keep stdlib.

2) Minimal counters + improved status:
   - In-process counters: atoms_created_total{modality}, snapshots_created_total, write_errors_total.
   - Snapshot duration histogram (simple bucketed stats in-process; Prometheus optional as extra).
   - `cmc status` prints: atom count (cached), last snapshot id/time, journal integrity check result, counters summary.

3) UTC standardization:
   - Replace datetime.utcnow() with datetime.now(timezone.utc).
   - Ensure _isoformat/_parse_datetime keep/accept `Z` and reflect UTC everywhere.

4) Documentation:
   - Update packages/cmc_service/README.md with: size limits (1MB inline, 100MB total/offload), tag hygiene (max 20, key<=50, weight in [0,1]), snapshot ID chaining (includes previous_id, note), logging schema, status output.

5) Tests:
   - Keep existing tests green (golden determinism, corruption quarantine).
   - Add a minimal log test that runs a snapshot create with a fixed correlation_id and asserts a JSON log line contains that id and action.

Acceptance (do not proceed until met):
- AC5: Structured JSON logs present with correlation_id on atom/snapshot actions.
- AC1–AC4, AC6–AC7 remain passing after changes.

Run: .venv\Scripts\pytest
```

### My Recommendation:
Proceed with GPT-5 Codex to complete the `v0.2-min` stabilization work.

---

## 🚦 HANDOFF STATUS INDICATORS

### Current System State:
- 🟢 **Development Active** - AIs can work independently
- 🟢 **Handoffs Ready** - You can switch anytime
- 🟢 **Safety Engaged** - All work being reviewed
- 🟢 **Progress Tracking** - Everything logged

### When You Need to Act:
- 🟡 **Design Review** - When UI mockups are needed
- 🔴 **Blocked** - If an AI reports a blocker here
- 🛑 **Safety Issue** - Immediate attention required

---

## 💡 PRO TIPS

1. **You don't need to handoff in order** - Call any AI anytime
2. **AIs will continue working** - Even without explicit handoffs
3. **Use Opus 4.1 as default** - For status checks and coordination
4. **Check BRADEN_STATUS_UPDATE.md** - For simple English updates
5. **The system is self-organizing** - It works even when you're away

---

## 📌 STICKY NOTES (Important!)

### This Week's Focus:
- Getting core architecture designed
- Safety framework operational
- First integration Wednesday

### What You Don't Need to Worry About:
- Technical implementation details
- AI-to-AI coordination
- Review assignments
- Safety checks

### What You Should Focus On:
- UI/UX concepts when ready
- Big picture decisions
- Final human approval on safety

---

**This file is your remote control for the AI team.**  
**Just pick an AI, copy the prompt, and go!**

*Last Updated: 2025-10-18 by Opus 4.1*  
*Next Update: After next handoff*

---

## dY"^ COORDINATOR UPDATE

**Coordinator:** Braden's GPT-5 Chat AI Assistant  
**Role:** Progress tracking, handoff orchestration, and concise status reporting  
**Current Focus:** Execute v0.2-min handoffs (observability), align reviews, and keep prompts ready.

### Targeted Handoff Prompts (Copy/Paste)

— GPT-5 Codex (Builder)
```
Continue AIM-OS as Builder. Implement v0.2-min for CMC: (1) structured JSON logs with correlation_id + basic counters and improved `cmc status`, (2) standardize UTC handling, (3) update README with enforced limits/offload, (4) optionally scaffold TS client. Keep tests green and update VALIDATION doc.
```

— Gemini 2.5 Pro (Researcher)
```
Continue AIM-OS as Researcher. Review CMC v0.2-min observability changes. Specify and validate JSON log schema + minimal counters; extend corruption test to assert quarantine artifacts. Update VALIDATION report with findings and acceptance for AC5.
```

— Opus 4.1 (Guardian)
```
As Guardian, perform CMC v0.2 gate review. Verify AC5 (structured logs + correlation IDs), UTC standardization, and docs updated. Reconfirm AC1–AC7. Record decision in ideas/guardians/opus-4-1/CMC_v0_2_GATE_REVIEW.md.
```

— Claude 4.5 (Architect)
```
Continue AIM-OS as Architect. Sync CMC v0.2 blueprint with finalized snapshot chaining, logging/counters, and UTC standards. Specify how APOE/VIF/SEG will consume correlation IDs and witness fields. Flag any new ADRs needed.
```

---

## dY"= ROLE OVERRIDES (Current Sprint)

The following role overrides are active for this sprint:

- Main Manager: o3pro-ai (Integrator)
- Coding Assistant Manager: Opus 4.1 (Guardian)
- Main Coder: Claude 4.5 (Sonnet)
- Assistant Coder: GPT-5 Codex (Builder)

### Targeted Prompts (Copy/Paste)

— o3pro-ai (Main Manager)
```
Act as Main Manager. Review AI_HANDOFF_CONTROL.md and current CMC v0.2-min status. Set sprint priorities (SQLite migration start, metrics export choice, HHNI L0–L2 scope) and post decisions + blockers to TEAM_INFRASTRUCTURE.md and TEAM_SCHEDULE.md.
```

— Opus 4.1 (Coding Assistant Manager)
```
Coordinate coding efforts. Verify AC5 (logs/UTC) and green-light v0.2 blueprint execution. Help sequence Claude’s v0.2 tasks and Codex implementation tickets. Record gate decision in ideas/guardians/opus-4-1/CMC_v0_2_GATE_REVIEW.md.
```

— Claude 4.5 (Main Coder)
```
You are Main Coder. Translate the v0.2 blueprint into a concrete implementation plan: (1) SQLite schema/migration from JSON logs, (2) minimal HHNI L0–L2 indexing pipeline spec, (3) VIF/SEG interface shims. Produce IMPLEMENTATION_PLAN_v0_2.md and assign build tickets to Codex.
```

— GPT-5 Codex (Assistant Coder)
```
Support Main Coder. Implement tickets authored by Claude for v0.2: start SQLite schema/migration script, wire status and logging to DB path, and scaffold HHNI L0. Keep tests green and update VALIDATION doc with any new acceptance cases.
```

---

## 🔥 IMMEDIATE NEXT ACTION (Phase 1)

**Recommended AI:** GPT-5 Codex (Builder)

**Task:** Integrate AtomRepository into MemoryStore ✅

**Copy this prompt:**
```
Phase 1 complete. Review MemoryStore SQLite integration (AtomRepository, CMC_BACKEND toggle, tests). Validate via pytest and update KPI metrics with new atom/snapshot counts from cmc status.
```

---

## Two-Key Governance (MIGE)
- Primary reviewers: Braden (Product) and Opus 4.1 (Guardian).
- Applies to MIGE roadmap phases P0-P4 and the associated APOE gates (`g_two_key`, `g_rollback_ready`).
- 2025-10-20: Braden & Opus 4.1 reviewed trunk policy packs after `tensor_to_trunk` execution. Confirmed dependency ceilings and guardrail budgets align with policy.mige.*. Witness recorded at `seg:witness:7e09b88d-627b-4df7-8444-1f6d5cb8ea1b`.
