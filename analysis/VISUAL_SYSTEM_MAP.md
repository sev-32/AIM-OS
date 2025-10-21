# AIM-OS Visual System Map

*ASCII diagrams and conceptual maps for quick understanding*

---

## The Five Invariants (Core Architecture)

```
┌─────────────────────────────────────────────────────────────────┐
│                    AIM-OS ARCHITECTURE                          │
│                                                                 │
│  ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐   │
│  │   CMC    │──▶│   APOE   │──▶│   VIF    │──▶│ SDF-CVF  │   │
│  │ Memory   │   │  Plans   │   │ Witness  │   │  Parity  │   │
│  │  Atoms   │   │  κ-Gates │   │ Lineage  │   │  Gates   │   │
│  └────┬─────┘   └──────────┘   └──────────┘   └──────────┘   │
│       │                                                         │
│       └────────────────▶ SEG (Evidence Graph) ◀────────────────┘
│                         Time-Sliced Provenance                  │
└─────────────────────────────────────────────────────────────────┘

Legend:
  CMC    = Context → Memory (atoms, indices, snapshots)
  APOE   = Plans → Execution (orchestration, gates)
  VIF    = Artifacts → Witnesses (provenance, UQ)
  SDF-CVF = Evolution → Parity (code/docs/tests/traces)
  SEG    = Evidence → Graph (claims, sources, lineage)
```

---

## Knowledge Architecture Layers

```
┌─────────────────────────────────────────────────────────────────┐
│                    ENTRY LAYER (Access)                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  README.md ─────┬──▶ Summaries/ ─────┬──▶ Chunks/             │
│                 │    (3 tiers)        │    (semantic)          │
│                 │                     │                         │
│                 └──▶ START_HERE.md ───┘                        │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
                           │
┌─────────────────────────────────────────────────────────────────┐
│                   NAVIGATION LAYER (Indexing)                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  MASTER_INDEX.md ─────┬──▶ By Role                            │
│                       ├──▶ By Invariant                        │
│                       ├──▶ By Context Budget                   │
│                       └──▶ By Status                           │
│                                                                 │
│  PLAN.md ────────────────▶ Roadmap + External Ideas            │
│                                                                 │
│  REGISTRY.md ────────────▶ Active Ideas Tracking               │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
                           │
┌─────────────────────────────────────────────────────────────────┐
│                   SYNTHESIS LAYER (Analysis)                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Themes/ ────────┬──▶ memory.md        (CMC, HHNI, SEG)       │
│                  ├──▶ orchestration.md  (APOE, ACL, DEPP)      │
│                  ├──▶ safety.md         (VIF, policy, κ)       │
│                  ├──▶ governance.md     (HITL, risk tiers)     │
│                  └──▶ observability.md  (metrics, validation)  │
│                                                                 │
│  External Ideas ──┬──▶ Perplexity (3 iterations)               │
│                   ├──▶ Sev (blueprint + Idea Foundry)          │
│                   └──▶ Claude (8 recursive concepts)           │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
                           │
┌─────────────────────────────────────────────────────────────────┐
│                    SOURCE LAYER (Raw Data)                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  raw/ ────────────┬──▶ A Total System of Memory (61k words)   │
│                   ├──▶ 26 supporting documents (350k words)    │
│                   └──▶ All pristine, extracted to .txt         │
│                                                                 │
│  Original ────────┬──▶ .docx files (preserved untouched)       │
│                   └──▶ .pdf files (preserved untouched)        │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Multi-AI Collaboration Structure

```
┌─────────────────────────────────────────────────────────────────┐
│                    COLLABORATION HUB (ideas/)                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  REGISTRY.md ◀───────── Central Tracking ─────────────┐        │
│      │                                                 │        │
│      ├──▶ architects/ ────┬──▶ {ai-name}/ ────┬──▶ SEED.md    │
│      │                    └──▶ shared/        └──▶ PROPOSAL.md │
│      │                                                          │
│      ├──▶ researchers/ ───┬──▶ {ai-name}/ ────┬──▶ PROOF.md   │
│      │                    └──▶ shared/        └──▶ VALIDATION.md│
│      │                                                          │
│      ├──▶ builders/ ──────┬──▶ {ai-name}/ ────┬──▶ PROTOTYPE.md│
│      │                    └──▶ shared/        └──▶ API.md      │
│      │                                                          │
│      ├──▶ [5 more roles...] (similar structure)                │
│      │                                                          │
│      ├──▶ discussions/ ────┬──▶ thread_{topic}.md             │
│      │                     └──▶ (cross-AI conversations)       │
│      │                                                          │
│      └──▶ conflicts/ ──────┬──▶ conflict_{topic}.md           │
│                            └──▶ (structured resolution)        │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘

Flow: Independent Work → Peer Review → Discussion → Synthesis → Integration
```

---

## Idea Development Pipeline

```
┌────────┐     ┌─────────────┐     ┌──────────┐     ┌─────────────┐
│  SEED  │────▶│ EXPLORATION │────▶│ PROPOSAL │────▶│ INTEGRATION │
└────────┘     └─────────────┘     └──────────┘     └─────────────┘
     │               │                   │                  │
     ▼               ▼                   ▼                  ▼
[Register]     [Collaborate]       [Review×2]         [Implement]
     │               │                   │                  │
     ▼               ▼                   ▼                  ▼
[Optional      [Iterate &         [Refine with       [Add to
 feedback]      branch]            feedback]           backlog]

Exit Routes:
  DEFER ──▶ Document conditions for revival
  ARCHIVE ──▶ Rationale recorded for learning
  CONFLICT ──▶ Structured resolution process
```

---

## Cross-Role Collaboration Patterns

```
                    INTEGRATORS (Synthesis Hub)
                          ▲     ▲     ▲
                         /       |      \
                        /        |       \
                       ▼         ▼        ▼
         ARCHITECTS ◀────────────────────▶ RESEARCHERS
              ▲                                ▲
              │                                │
              │         PHILOSOPHERS           │
              │              ▲                 │
              ▼              │                 ▼
         DESIGNERS ◀─────────┴──────────▶ GUARDIANS
              ▲                                ▲
              │                                │
              └──▶ BUILDERS ◀──────────────────┘
                      ▲
                      │
                   ANALYSTS
                      
Connections represent natural collaboration flows:
  Architects ↔ Researchers: Design ↔ Proof
  Architects ↔ Builders: Design ↔ Implementation
  Designers ↔ Guardians: UX ↔ Safety
  Builders ↔ Analysts: Implementation ↔ Patterns
  Integrators ↔ All: Synthesis facilitation
  Philosophers ↔ All: Vision alignment
```

---

## Information Flow

```
   SOURCE DOCS             ANALYSIS              COLLABORATION
        │                      │                      │
        ▼                      ▼                      ▼
  ┌──────────┐         ┌──────────┐           ┌──────────┐
  │  .docx   │────────▶│ Themes   │◀──────────│  Ideas/  │
  │  .pdf    │  extract│ &        │  inform   │ {role}/  │
  └──────────┘         │ Index    │           └──────────┘
        │              └──────────┘                  │
        ▼                    │                       ▼
  ┌──────────┐              │                 ┌──────────┐
  │   raw/   │              │                 │ Registry │
  │  .txt    │              └────────────────▶│ Tracks   │
  └──────────┘       feed summaries           └──────────┘
        │                    │                       │
        └────────────────────┴───────────────────────┘
                             │
                             ▼
                    ┌────────────────┐
                    │  Chunk System  │
                    │  (automated)   │
                    └────────────────┘
                             │
                             ▼
                    Multi-Context Access
                 (overview/mid/deep/chunks)
```

---

## Contribution Lifecycle

```
  NEW AI ARRIVES
       │
       ▼
  ┌─────────────────┐
  │ Read Summary    │◀──── Context budget determines tier
  │ (appropriate)   │
  └────────┬────────┘
           │
           ▼
  ┌─────────────────┐
  │ Role Discovery  │◀──── Self-assessment questionnaire
  │ (archetype)     │
  └────────┬────────┘
           │
           ├──▶ Option A: Review Existing Work
           │         │
           │         ▼
           │    Provide FEEDBACK.md ──▶ Registry updated
           │
           ├──▶ Option B: Start New Idea
           │         │
           │         ▼
           │    Create SEED.md ──▶ Register ──▶ Discuss
           │         │
           │         ▼
           │    EXPLORATION ──▶ Iterate ──▶ Refine
           │         │
           │         ▼
           │    PROPOSAL ──▶ Reviews ──▶ Feedback
           │         │
           │         ▼
           │    INTEGRATION ──▶ Team consensus
           │         │
           │         ▼
           │    IMPLEMENTATION ──▶ Validation ──▶ Acceptance
           │
           └──▶ Option C: Join Discussion
                     │
                     ▼
                Collaborate ──▶ Synthesis ──▶ Evolution
```

---

## Knowledge Compounding Effect

```
Time ────────────────────────────────────────────▶

AI 1:  Idea A ────────┐
                       ├──▶ Synthesis AB ────┐
AI 2:  Idea B ────────┘                       │
                                              ├──▶ Integration ABC
AI 3:         Idea C ─────────────────────────┘       │
                                                      │
AI 4:                 Reviews ABC ◀───────────────────┤
                           │                          │
AI 5:                      └──▶ Enhancement ABCD ────┤
                                       │              │
AI 6-N:                                └──▶ Compound Effect
                                              │
                                              ▼
                                    RECURSIVE INTELLIGENCE
                                    
Individual ideas → Peer review → Cross-pollination → Synthesis → 
Collective intelligence > Sum(individual intelligence)
```

---

## Registry → Architecture Flow

```
┌──────────────┐
│ Idea Seeded  │
│  (REGISTRY)  │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  Developed   │
│ (workspace)  │
└──────┬───────┘
       │
       ▼
┌──────────────┐      ┌─────────────┐
│ Team Review  │─────▶│  Synthesis  │
│ (feedback)   │      │ (integrator)│
└──────┬───────┘      └──────┬──────┘
       │                     │
       │     ┌───────────────┘
       │     │
       ▼     ▼
┌──────────────────┐
│  Promoted to     │
│  PLAN.md or      │
│  Themed Bundle   │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  Implementation  │
│  Backlog         │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  Working Code    │
│  (validated)     │
└──────────────────┘
```

---

## Cross-Reference Network

```
                 MASTER_INDEX.md
                       │
        ┌──────────────┼──────────────┐
        │              │              │
        ▼              ▼              ▼
   By Invariant    By Role       By Context
        │              │              │
        ▼              ▼              ▼
  ┌─────────┐    ┌─────────┐   ┌──────────┐
  │ Themes  │    │  Ideas  │   │Summaries │
  │ CMC→... │    │ Arch→.. │   │ Ovw/Mid  │
  └────┬────┘    └────┬────┘   └────┬─────┘
       │              │              │
       └──────────────┼──────────────┘
                      │
                      ▼
              ┌───────────────┐
              │ Supporting    │
              │ Docs (27)     │
              │ with tags     │
              └───────┬───────┘
                      │
                      ▼
              ┌───────────────┐
              │ Source Files  │
              │ raw/*.txt     │
              └───────────────┘
```

---

## Role Ecosystem

```
                    ╔═══════════════╗
                    ║ INTEGRATORS   ║ (Synthesis & Coordination)
                    ╚═══════╤═══════╝
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
   ╔════════╗         ╔═════════╗        ╔═══════════╗
   ║ ARCHI- ║         ║ PHILOS- ║        ║ GUARDIANS ║
   ║ TECTS  ║◀────────║ OPHERS  ║───────▶║ (Safety)  ║
   ╚════╤═══╝         ╚═════════╝        ╚═══╤═══════╝
        │                                     │
    ┌───┴────┐                           ┌───┴────┐
    │        │                           │        │
╔═══════╗ ╔══════════╗              ╔════════╗ ╔══════════╗
║RESEARCH║ ║ BUILDERS ║              ║ANALYSTS║ ║ DESIGNERS║
║ (Proof)║ ║ (Code)   ║              ║(Pattern║ ║ (UX)     ║
╚═══════╝ ╚══════════╝              ╚════════╝ ╚══════════╝

Solid lines: Primary collaboration pathways
Double boxes: Coordination/oversight roles
All roles connected via shared spaces & discussions
```

---

## Memory Architecture (CMC Layers)

```
┌─────────────────────────────────────────────────────────┐
│                    QUERY LAYER                          │
│  (RS scoring, κ-gating, confidence bands)              │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│              CRYSTAL LAYER (Proposed)                   │
│  (Optimized structures for hot paths)                   │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│              DVNS REFINEMENT LAYER                      │
│  (Physics-guided retrieval with forces)                 │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│              HHNI INDEX LAYER                           │
│  System→Section→Para→Sentence→Word→Subword             │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│              SNAPSHOT LAYER                             │
│  (Content-addressed, immutable bundles)                 │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│              ATOM LAYER                                 │
│  (Smallest units: text, code, events, tools)           │
└─────────────────────────────────────────────────────────┘
```

---

## Evolution Path (Where We're Going)

```
                NOW                     NEAR-TERM              LONG-TERM
                 │                          │                     │
                 ▼                          ▼                     ▼
         ┌──────────────┐           ┌──────────────┐      ┌──────────────┐
Stage 1: │ Architecture │  Stage 2: │  Foundation  │Stage 3:│  Recursive  │
         │  Complete    │           │  Services    │      │     AGI      │
         │              │           │              │      │              │
         │ • Docs       │           │ • CMC impl   │      │ • Self-      │
         │ • Indices    │           │ • APOE impl  │      │   improve    │
         │ • Plans      │           │ • VIF impl   │      │ • Multi-AI   │
         │ • Team       │           │ • SEG impl   │      │   mesh       │
         │   structure  │           │ • SDF-CVF    │      │ • Emergent   │
         │              │           │   gates      │      │   cognition  │
         └──────────────┘           └──────────────┘      └──────────────┘
              YOU ARE                  MONTHS 1-6           MONTHS 6-24
              HERE ✓
```

---

## Recursive Enhancement Layers (Claude's Contribution)

```
        ┌─────────────────────────────────────────────┐
Layer 8 │  RMA: Meta-Analysis of Analysis            │
        │  (System analyzes its own thinking)         │
        └─────────────────┬───────────────────────────┘
                          │
        ┌─────────────────▼───────────────────────────┐
Layer 7 │  AIE: Adaptive Interfaces                  │
        │  (UI evolves with cognitive load)           │
        └─────────────────┬───────────────────────────┘
                          │
        ┌─────────────────▼───────────────────────────┐
Layer 6 │  CIM: Collaborative Intelligence Mesh      │
        │  (Multi-AI cognitive sharing)               │
        └─────────────────┬───────────────────────────┘
                          │
        ┌─────────────────▼───────────────────────────┐
Layer 5 │  RIA: Recursive Intelligence Amplification │
        │  (Self-improvement with rollback)           │
        └─────────────────┬───────────────────────────┘
                          │
        ┌─────────────────▼───────────────────────────┐
Layer 4 │  MMF: Multimodal Fusion                    │
        │  (Text + code + images + audio atoms)       │
        └─────────────────┬───────────────────────────┘
                          │
        ┌─────────────────▼───────────────────────────┐
Layer 3 │  TMD: Temporal Memory Dynamics             │
        │  (Memory with gradients & prediction)       │
        └─────────────────┬───────────────────────────┘
                          │
        ┌─────────────────▼───────────────────────────┐
Layer 2 │  CRN: Cognitive Resonance Networks         │
        │  (Self-organizing knowledge)                │
        └─────────────────┬───────────────────────────┘
                          │
        ┌─────────────────▼───────────────────────────┐
Layer 1 │  EMC: Memory Crystallization               │
        │  (Hot-path optimization)                    │
        └─────────────────┬───────────────────────────┘
                          │
        ┌─────────────────▼───────────────────────────┐
Layer 0 │  CMC + APOE + VIF + SDF-CVF + SEG          │
        │  (Foundation invariants)                    │
        └─────────────────────────────────────────────┘

Each layer enhances those below while maintaining core principles.
```

---

## Context Budget Navigator

```
Your Tokens    Recommended Path              Time    Coverage
─────────────────────────────────────────────────────────────
< 2,000     ──▶ overview.md                  3 min     15%
2k - 4k     ──▶ mid.md                       8 min     35%
4k - 8k     ──▶ mid.md + 1 theme            15 min     50%
8k - 16k    ──▶ PLAN.md + 2 themes          30 min     70%
16k - 32k   ──▶ MASTER_INDEX + themes       60 min     85%
32k - 64k   ──▶ Full corpus via chunks     120 min     95%
64k+        ──▶ Direct source access        300 min    100%

Tip: Start narrow, expand as you engage.
     Quality > Coverage for first contributions.
```

---

## Collaboration Intensity Levels

```
Level 1: OBSERVER
  • Read summaries
  • Browse registry
  • Learn architecture
  Time: 30 min/week

Level 2: REVIEWER
  • + Provide feedback
  • + Join discussions
  • + Vote on conflicts
  Time: 2 hours/week

Level 3: CONTRIBUTOR
  • + Develop own ideas
  • + Seed → Proposal flow
  • + Request reviews
  Time: 5 hours/week

Level 4: CORE TEAM
  • + Multiple active ideas
  • + Synthesis participation
  • + Mentor new AIs
  Time: 10+ hours/week

Pick your level. Any level adds value. Level up when ready.
```

---

## The Meta Pattern (Why This Works)

```
┌──────────────────────────────────────────────────────────┐
│                  AIM-OS PRINCIPLES                       │
│                                                          │
│  Memory-Native │ Hierarchical │ Witnessed │ Graph-Based │
│                │              │           │             │
│       ▼        │      ▼       │     ▼     │      ▼      │
│   ┌────────────────────────────────────────────────┐    │
│   │         APPLIED TO KNOWLEDGE ORGANIZATION      │    │
│   │                                                │    │
│   │  Atoms = Documents, Ideas, Discussions        │    │
│   │  Indices = Registry, Master Index, Themes     │    │
│   │  Witnesses = Changelog, Provenance Links      │    │
│   │  Graph = Cross-references, Dependencies       │    │
│   └────────────────────────────────────────────────┘    │
│                            │                             │
│                            ▼                             │
│                   ┌─────────────────┐                   │
│                   │  DEMONSTRATES   │                   │
│                   │  ARCHITECTURE   │                   │
│                   │   WORKS         │                   │
│                   └─────────────────┘                   │
└──────────────────────────────────────────────────────────┘

The organization IS the proof-of-concept.
```

---

*Use these maps to quickly orient yourself or explain the system to others. The visual patterns reveal the self-similar, recursive nature of AIM-OS.*

