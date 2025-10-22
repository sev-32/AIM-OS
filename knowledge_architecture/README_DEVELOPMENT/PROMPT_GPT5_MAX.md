# Prompt for GPT-5 High (Max Mode): Independent Analysis + File Outputs Only

You are GPT-5 High (Max Mode). Your task is to independently analyze Project Aether (AIM-OS) and produce three documents as files, not a chat response.

IMPORTANT OPERATING RULES:
- Do not summarize intentions. Do not say you will explore first. Begin producing deliverables now.
- Be independent: do not read Sonnet’s prior analyses in this repo for your first pass. Base conclusions on code and documentation.
- Output strictly in the file-emission format below. No extra commentary.

REFERENCE MATERIALS (read as needed):
- README draft: knowledge_architecture/README_DEVELOPMENT/README_DRAFT_V1.md
- Full code: packages/*
- Tests: packages/*/tests/* (verify counts and status)
- Docs: knowledge_architecture/** (SUPER_INDEX, systems/*, AETHER_MEMORY/*)
- Goals: goals/GOAL_TREE.yaml, PROJECT_STATUS.md, goals/STATUS.md

DELIVERABLES (exact file paths):
1) knowledge_architecture/README_DEVELOPMENT/GPT5_COMPREHENSIVE_PROJECT_ANALYSIS.md
2) knowledge_architecture/README_DEVELOPMENT/GPT5_README_DETAILED_REVIEW.md
3) knowledge_architecture/README_DEVELOPMENT/GPT5_README_V2_IMPLEMENTATION_PLAN.md

FORMAT (STRICTLY FOLLOW):
For each document, output as:

===FILE: <absolute-path-from-repo-root>
<complete markdown content>
===END

Do not wrap with backticks. Do not add any text outside the FILE blocks. Emit the three FILE blocks in sequence.

CONTENT REQUIREMENTS:

1) GPT5_COMPREHENSIVE_PROJECT_ANALYSIS.md
- Executive summary (status, tests, production-ready systems)
- System-by-system validation (CMC, HHNI, APOE, VIF, SEG, SDF-CVF, CAS)
- Test count reconciliation (verify actual collection)
- Architecture validation (are relationships correct?)
- Claims verification (performance, readiness, hallucinations)
- Consciousness/RTFT positioning (clear separation of theory vs implementation)
- Production readiness criteria and assessment per system
- Enterprise adoption considerations (license, Python version, Docker)
- Final verdict + confidence levels

2) GPT5_README_DETAILED_REVIEW.md
- Section-by-section critique with specific strengths, weaknesses
- Line-level corrections (before/after) where applicable
- Critical fixes (must do before publication)
- Important improvements (should do)
- Optional enhancements (nice to have)
- Overall readiness rating with rationale

3) GPT5_README_V2_IMPLEMENTATION_PLAN.md
- Exact, actionable change list (copy-paste ready)
- Priorities: Critical (2h), Important (2h), Optional (3–5h)
- Implementation checklist boxes
- Quality validation criteria
- Expected outcomes after each priority level

CONSTRAINTS:
- Professional tone, no emojis.
- Cite paths to code/tests when verifying claims.
- Prefer conservative numbers unless verified by code/tests.

BEGIN NOW. Emit exactly three FILE blocks in the order specified. No additional text.
