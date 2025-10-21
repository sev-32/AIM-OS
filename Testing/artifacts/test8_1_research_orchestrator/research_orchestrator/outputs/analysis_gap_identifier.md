Okay, I understand. As the Gap Identifier, my primary function during the Analysis stage is to identify and document discrepancies or "gaps" related to evidence alignment and governance compliance. I must do this while adhering to pre-defined policies governing evidence thresholds, latency budgets, research depth, and seed-related parameters.  My ultimate output will be a structured summary, confidence score, and a recommendation for the next step, including escalation if necessary.

Let's break down each element to ensure I'm ready to execute:

**1. Maintaining Evidence Alignment and Governance Compliance:**

*   **Evidence Alignment:** This implies ensuring that all collected evidence supports and aligns with the objectives of the broader task and overall strategy. This likely involves checking for inconsistencies, contradictions, or missing pieces of evidence.
*   **Governance Compliance:** This refers to adhering to the relevant policies, regulations, and internal guidelines within the organization. This might involve verifying data privacy, security protocols, ethical considerations, and legal requirements.  It also includes adherence to the specific policies listed (evidence threshold, latency budget, research depth, etc.).

**2. Respecting Orchestration Policies:**

*   This is a key constraint.  I must operate within the boundaries defined by the listed policies:
    *   **policy.evidence_threshold:**  Minimum amount of evidence required to make a judgment.  This dictates how much supporting information I need to find before declaring a gap or confirming compliance.
    *   **policy.latency_budget:** Maximum time allowed to complete my analysis. This constraint forces me to prioritize and be efficient in my research and analysis.
    *   **policy.research_depth:** Limits how deeply I can investigate a potential gap.  This prevents me from getting bogged down in excessive research.
    *   **policy.seed.evidence_threshold:** The minimum evidence required when using "seed" data (presumably pre-existing information). This might be lower than the general `policy.evidence_threshold`, but needs to be considered.
    *   **policy.seed.max_research_depth:**  The maximum research depth allowed when using "seed" data.
    *   **policy.seed.max_total_time:** The maximum total time allowed when using "seed" data. This is likely tied to the latency budget and should be considered together.

**3. Required Outputs - Defined Actions:**

*   **Structured Summary of Findings:** This will be a clear and concise description of identified gaps (or lack thereof). It should likely include:
    *   Description of the specific gap or issue.
    *   The impact of the gap on evidence alignment and/or governance compliance.
    *   Identified evidence related to the gap (or lack thereof).
*   **Confidence Score with Supporting Evidence Identifiers:** A numerical or qualitative score indicating the certainty of the findings.  This score *must* be linked to specific evidence identifiers that support the assessment.  A higher score means I have more confidence in the identified gap/compliance status based on the available evidence.
*   **Next-Step Recommendation or Escalation Flag:** Based on the findings and confidence score, I will recommend the appropriate next step. This could include:
    *   **Recommendation:** Suggesting further investigation, remediation steps, or specific actions to address the gap.
    *   **Escalation Flag:**  Raising a flag if the gap is severe, requires immediate attention, or exceeds my authority to resolve. The criteria for escalation should be well-defined.

**Example Scenario:**

Let's say I'm analyzing evidence related to GDPR compliance for a new customer onboarding process.

*   **Potential Gap:**  Missing documented consent procedures for data processing.
*   **Evidence:**  I find internal documentation outlining the process (Evidence ID: DOC-123), but no recorded evidence of customers explicitly consenting (Evidence ID: SEARCH-456 shows no records in the consent database).
*   **Policy Considerations:**
    *   `policy.evidence_threshold = 3 pieces of evidence` (I only have 2 relevant pieces).
    *   `policy.latency_budget = 30 minutes`
    *   `policy.research_depth = 2 levels` (I can only search two layers deep in the database/documentation).
*   **Output:**
    *   **Structured Summary:** "A potential gap exists in GDPR compliance. There is a lack of documented consent procedures for data processing during new customer onboarding. While the process is documented internally (DOC-123), no records of explicit customer consent are found (SEARCH-456)."
    *   **Confidence Score:** 6/10. (Reasoning: I have two pieces of evidence suggesting a gap, but I haven't exceeded the evidence threshold and my research depth was limited).
    *   **Next-Step Recommendation:** "Recommend further investigation to determine if alternative consent capture methods are in place. Increase research depth to uncover potential manual processes or offline records. Re-evaluate evidence once new information is available. Consider reaching out to the data privacy team for clarification."

**Key Questions for Clarification (If Possible):**

*   What is the specific format expected for the "Structured Summary"?  (e.g., JSON, Markdown, Free-form text).
*   What is the defined scale for the "Confidence Score"? (e.g., 1-10, Low/Medium/High).
*   What constitutes an "Escalation Flag"?  What specific criteria trigger it? Who should be notified?
*   What are the specific data sources I have access to for evidence gathering?
*   Are there pre-defined remediation actions for common gap types?
*   Can you provide examples of seed data and how `policy.seed.*` parameters should be applied?

By understanding these requirements and addressing these questions, I can effectively perform my role as the Gap Identifier during the Analysis stage and deliver the required outputs within the defined policy constraints. I am ready to begin when provided with input data.