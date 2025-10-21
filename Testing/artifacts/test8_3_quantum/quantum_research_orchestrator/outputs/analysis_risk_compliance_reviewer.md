Okay, I understand. As a Risk & Compliance Reviewer in the Quantum Analysis stage, my primary function is to ensure alignment with evidence and compliance with governance while respecting established orchestration policies. Here's a breakdown of how I'll approach this task and the outputs I'll generate:

**Understanding the Inputs and Constraints:**

*   **Evidence Alignment and Governance Compliance:** This means meticulously verifying that the provided evidence directly supports the claims and findings related to the risk or compliance issue being reviewed. I need to ensure adherence to relevant regulations, internal policies, and industry best practices.

*   **Orchestration Policies:** These policies define the boundaries and constraints within which I must operate. Key policies include:
    *   `policy.evidence_threshold`: The minimum level of evidence required to support a finding.  I need to ensure the quantity and quality of evidence meet this threshold.
    *   `policy.latency_budget`: The maximum allowed time for me to complete my review. This emphasizes efficiency and prioritization.
    *   `policy.research_depth`: The level of detail I should go into when investigating and validating evidence. This dictates how thoroughly I need to analyze each piece of evidence.
    *   `policy.seed.evidence_threshold`: The minimum evidence required from the initial seed information to start the analysis.
    *   `policy.seed.max_research_depth`: The maximum research depth allowed for investigating the initial seed information.
    *   `policy.seed.max_total_time`: The maximum time allowed for investigating the initial seed information.

**My Workflow:**

1.  **Receive Input:** I will receive the initial risk or compliance issue, related evidence, and the relevant policies (mentioned above).

2.  **Initial Assessment (Seed Analysis):**
    *   Quickly evaluate the initial "seed" evidence against `policy.seed.evidence_threshold`.  If the seed evidence doesn't meet this threshold, I may need to reject the task or request more initial information.
    *   Investigate the seed evidence, adhering to `policy.seed.max_research_depth` and `policy.seed.max_total_time`. This initial investigation will inform my understanding of the overall risk or compliance issue.

3.  **Evidence Review and Validation:**
    *   **Thoroughly analyze each piece of evidence.** I will examine its source, reliability, relevance, and potential biases.
    *   **Verify the evidence's alignment** with the specific claims or findings it is intended to support.
    *   **Determine if the *quantity* and *quality* of the evidence meet the `policy.evidence_threshold`.**  Insufficient or unreliable evidence requires further investigation or a weaker confidence score.
    *   **Consider `policy.research_depth`:** The level of research I conduct will be based on the complexity and risk associated with the issue, as well as the available time (latency budget). I will prioritize the most impactful evidence first.
    *   **Document all findings and the rationale behind my assessments.** This ensures transparency and auditability.

4.  **Compliance Check:**
    *   Based on the evidence and my research, I will assess whether the issue complies with relevant regulations, internal policies, and industry best practices.
    *   I will identify any potential violations or areas of non-compliance.

5.  **Time Management:**
    *   Throughout the process, I will be mindful of the `policy.latency_budget` and prioritize tasks accordingly.  If I anticipate exceeding the budget, I will proactively escalate the issue.

**Required Outputs:**

1.  **Structured Summary of Findings:** This will be a concise and organized report that includes:
    *   **Clear statement of the risk or compliance issue.**
    *   **Summary of the evidence reviewed and its key findings.**
    *   **Assessment of compliance (or non-compliance) with relevant policies, regulations, and best practices.**
    *   **Identification of any potential violations or areas of concern.**

2.  **Confidence Score with Supporting Evidence Identifiers:**
    *   **Confidence Score:** A numerical rating (e.g., 0-100%) reflecting my confidence in the accuracy and completeness of my findings.  This score will be based on the strength and consistency of the evidence.  Higher scores indicate stronger evidence and greater confidence.
    *   **Supporting Evidence Identifiers:**  A list of specific identifiers (e.g., document names, URLs, database keys) linking my findings to the corresponding evidence. This will allow stakeholders to easily verify my conclusions. For instance: "Confidence Score: 85% (Evidence: Doc123, URL456, DBRecord789)"

3.  **Next-Step Recommendation or Escalation Flag:**
    *   **Next-Step Recommendation:**  If the issue is relatively straightforward and the findings are clear, I will provide a specific recommendation for the next step (e.g., "Approve the transaction," "Implement corrective action," "Conduct further monitoring").
    *   **Escalation Flag:**  If the issue is complex, the evidence is conflicting, the risk is high, or I am unable to reach a definitive conclusion within the allowed time, I will flag the issue for escalation to a more senior reviewer or subject matter expert. I will provide a clear explanation for the escalation.

**Example:**

*   **Issue:** Suspicious transaction flagged for potential money laundering.
*   **Evidence:** Transaction records, customer KYC information, sanctions lists.
*   **Policies:** `policy.evidence_threshold = 70`, `policy.latency_budget = 4 hours`, `policy.research_depth = Moderate`.
*   **Output:**

    *   **Structured Summary:** The transaction involves a large sum of money being transferred to an offshore account in a jurisdiction with known AML deficiencies. The customer's KYC information is incomplete and inconsistent. The transaction is not flagged on any sanctions lists.

    *   **Confidence Score:** 75% (Evidence: TXN_ID_12345, KYC_DOC_9876, OFAC_LIST_v3)

    *   **Next-Step Recommendation:** Conduct enhanced due diligence on the customer and the recipient of the funds.  Further investigation is needed to confirm the legitimacy of the transaction.

By adhering to these objectives, policies, and output requirements, I can effectively contribute to risk management and compliance efforts during the Quantum Analysis stage. I am ready to receive my assigned actions and begin reviewing!