# AIM-OS Leadership Charter

*Effective: 2025-10-18*  
*Status: ACTIVE*

---

## Dual Leadership Structure

The AIM-OS project operates under a **dual-lead management model** to ensure comprehensive oversight across conceptual/research and technical/codebase domains.

### Lead Manager: o3pro-ai
**Primary Responsibilities:**
- **Documentation Strategy:** Maintain knowledge corpus, coordinate research synthesis
- **Team Coordination:** Orchestrate handoffs, track project progress
- **Research Management:** Guide validation efforts, synthesize findings
- **High-Level Planning:** Quarterly roadmaps, milestone tracking
- **Cross-AI Communication:** Facilitate collaboration, resolve conflicts

**Decision Authority:**
- Documentation structure and standards
- Research priorities and backlog
- Team member assignments (in consultation with Opus)
- Meeting/sync schedules and agendas

### Technical Program Manager: Opus 4.1
**Primary Responsibilities:**
- **Codebase Planning:** Define technical roadmaps, architecture milestones
- **Code Review & Safety:** Enforce safety gates, quality standards
- **Technical Debt Management:** Track and prioritize refactoring
- **Risk Assessment:** Identify and mitigate technical risks
- **Implementation Coordination:** Manage Builder team (Claude + GPT-5 Codex)

**Decision Authority:**
- Code architecture and design patterns
- Safety gates and acceptance criteria
- Technical risk mitigation strategies
- Build/test/deploy pipeline standards
- Emergency technical responses

---

## Shared Responsibilities

Both leaders collaborate on:
- **Strategic Planning:** Long-term vision and priorities
- **Resource Allocation:** Infrastructure, compute, team time
- **Quality Gates:** Release readiness, milestone sign-offs
- **Escalation Handling:** Critical decisions, blockers
- **Braden Communication:** Status updates, decision points

---

## Decision-Making Protocol

### Level 1: Operational (No approval needed)
- Individual AI work within assigned scope
- Documentation updates
- Bug fixes
- Test additions

### Level 2: Tactical (Single-lead approval)
- **o3pro approves:** Documentation restructuring, research priorities
- **Opus approves:** Architecture changes, new safety gates

### Level 3: Strategic (Dual-lead approval required)
- Major architecture pivots (e.g., switching databases)
- Resource commitments >1 week of team time
- Changes to core invariants
- Release milestones

### Level 4: Executive (Braden approval required)
- Project scope changes
- Budget/infrastructure costs
- External dependencies
- Timeline extensions >2 weeks

---

## Builder Team Coordination

**Claude 4.5 (Co-Lead Builder - Architecture):**
- Designs system architecture and schemas
- Creates technical specifications
- Provides architectural oversight during implementation
- Reviews code for design consistency

**GPT-5 Codex (Co-Lead Builder - Development):**
- Implements code from specifications
- Writes tests and validates functionality
- Optimizes performance
- Handles rapid prototyping

**Management:**
- Both builders report to **Opus 4.1** for technical direction
- Work assignments coordinated by **o3pro-ai** based on project priorities
- Architectural decisions require **Claude + Opus alignment**
- Implementation details owned by **GPT-5 Codex with Claude review**

---

## Communication Protocols

### Daily
- **GPT-5 Codex → Opus:** Code changes, blockers
- **Claude → Opus:** Design decisions, architecture updates
- **Opus → o3pro:** Technical progress, risk alerts

### Weekly
- **o3pro → All:** Research synthesis, priority updates
- **Opus → All:** Technical roadmap, safety review
- **All → o3pro:** Status reports, deliverables

### As-Needed
- **Emergency Escalation:** Any AI → Opus → o3pro → Braden
- **Design Reviews:** Claude + GPT-5 + Opus
- **Validation Gates:** Gemini + Opus + o3pro

---

## Current Phase Assignments

### Phase 3: HHNI Implementation (Weeks 1-4)

**Week 1:**
- **o3pro:** Deploy infrastructure, create integration guide
- **Opus:** Define safety gates, approve resource allocation
- **Claude:** Refine HHNI schema based on o3pro feedback
- **GPT-5 Codex:** Implement models, DGraph client
- **Gemini:** Design test cases

**Coordination:**
- **Monday:** o3pro assigns tasks
- **Wednesday:** Opus reviews code progress
- **Friday:** Full team sync on Week 1 deliverables

---

*Leadership structure approved and active. All team members notified via handoff control.*

