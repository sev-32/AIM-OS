Okay, this document outlines the role of a "Quality Checker Primary" within a "Produce" stage, likely in a larger orchestration process. Let's break down each section to understand the implications:

**Role:** Quality Checker Primary

**Stage:** Produce - This indicates the role happens after research and likely before deployment or presentation of results. The "Produce" stage probably involves solidifying and packaging the findings.

**Overall Goal:** To ensure the "produced" output (whatever it is) meets quality standards, aligns with evidence, and follows governance policies. This is a critical gatekeeper role.

**Detailed Breakdown:**

*   **Objectives:**
    *   **Maintain evidence alignment and governance compliance:** This is the core objective.  The Quality Checker must verify that the work produced is:
        *   **Evidence-aligned:** The findings are supported by the research and evidence gathered. There are no unsupported claims or leaps in logic. Every conclusion is traceable back to the source data.
        *   **Governance compliant:** The work adheres to internal and external policies, regulations, and guidelines. This could include data privacy, ethical considerations, legal requirements, or internal best practices.
    *   **Respect orchestration policies while completing assigned actions:** This emphasizes the role exists within a larger workflow.  The Quality Checker must work within the constraints defined by the orchestration system.  This means:
        *   Following defined processes.
        *   Meeting deadlines.
        *   Using provided tools and systems.
        *   Avoiding actions that disrupt the overall workflow.

*   **Policy Context:** This section lists key policies that directly impact the Quality Checker's work. Understanding these policies is crucial for effective quality assurance.
    *   **policy.evidence_threshold:** This policy defines the minimum amount and strength of evidence required to support a claim or conclusion.  The Quality Checker must ensure that the evidence meets or exceeds this threshold.
    *   **policy.latency_budget:**  This policy defines the time allocated for this quality check.  It forces efficiency and prioritization.  The Quality Checker must balance thoroughness with speed.
    *   **policy.research_depth:** This policy dictates how deeply the Quality Checker is expected to investigate the evidence. This is likely related to the risk associated with incorrect conclusions. Shallower research depth means less investigation into the source.
    *   **policy.seed.evidence_threshold:** This likely refers to a "seed" set of initial data or assumptions used to start the process. This policy dictates the minimum evidence required to *initially* accept these seeds.
    *   **policy.seed.max_research_depth:**  Similar to `policy.research_depth`, but specifically for the "seed" data. It limits the amount of investigation the Quality Checker must perform on the initial data.
    *   **policy.seed.max_total_time:**  Limits the time spent researching seed data.

*   **Required Outputs:** These are the tangible results the Quality Checker must produce.
    *   **Structured summary of findings:** A clear, concise, and organized summary of the quality check.  This likely includes:
        *   A list of issues or concerns found.
        *   Explanations of why those issues are problematic (related to the policies).
        *   Specific references to the evidence or policies that support the findings.
    *   **Confidence score with supporting evidence identifiers:**  A numerical or qualitative score indicating the Quality Checker's confidence in the accuracy and validity of the produced output.  Crucially, this score *must* be supported by specific identifiers that link the score back to the evidence used to assess the quality.  This allows others to understand *why* the score was assigned.
    *   **Next-step recommendation or escalation flag:**  Based on the findings, the Quality Checker must recommend the next appropriate action.  This could include:
        *   Accepting the output (no further action needed).
        *   Requesting revisions or further research.
        *   Escalating the issue to a higher authority (if the problem is serious or cannot be resolved by the Quality Checker).

**In Summary:**

The "Quality Checker Primary" role is a critical quality assurance step within a structured process.  The person in this role must be knowledgeable about the relevant policies, capable of analyzing evidence, and able to effectively communicate their findings and recommendations. The emphasis on structured outputs, confidence scores, and evidence identifiers highlights the need for transparency and accountability in the quality assurance process. The policy context highlights that the role is constrained by time, budget, and depth of research permissible. This means the quality checker will have to make judgements and use risk management skills.