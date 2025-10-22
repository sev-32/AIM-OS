# Prompt for Gemini Pro: Independent README Review & Project Analysis

You are Gemini Pro. Produce three documents as files (not chat), independently of other AI outputs.

RULES:
- Start producing the files now. Do not say you will explore first.
- Be independent: do not copy prior analyses in this repo for your first pass.
- Output strictly in FILE blocks as specified.

REFERENCES:
- README draft: knowledge_architecture/README_DEVELOPMENT/README_DRAFT_V1.md
- Code: packages/*, tests in packages/*/tests/*
- Docs: knowledge_architecture/** (SUPER_INDEX, systems/*, AETHER_MEMORY/*)
- Goals: goals/GOAL_TREE.yaml, PROJECT_STATUS.md, goals/STATUS.md

OUTPUT FILES (exact paths):
1) knowledge_architecture/README_DEVELOPMENT/GEMINI_COMPREHENSIVE_PROJECT_ANALYSIS.md
2) knowledge_architecture/README_DEVELOPMENT/GEMINI_README_DETAILED_REVIEW.md
3) knowledge_architecture/README_DEVELOPMENT/GEMINI_README_V2_IMPLEMENTATION_PLAN.md

OUTPUT FORMAT (strict):
===FILE: <absolute-path-from-repo-root>
<complete markdown content>
===END

REQUIREMENTS:
- Validate system statuses, test counts (collect-only pass preferred), architecture relationships
- Identify claim gaps (performance, readiness, hallucination phrasing)
- Provide actionable, prioritized change plan
- Keep tone professional; cite file paths for evidence

BEGIN NOW. Emit exactly three FILE blocks in the order above. No extra text.
