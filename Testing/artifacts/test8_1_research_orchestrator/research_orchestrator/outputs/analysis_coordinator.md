This document outlines the role of the Analysis Coordinator within the Analysis Stage.  The core function is to synthesize findings, ensure compliance, and recommend subsequent actions. Let's break down each section:

**Stage: Analysis**

This clearly defines the context of the Coordinator's role: they operate within the analysis stage of a larger process.

**Objectives**

These define the key performance indicators (KPIs) for the role.

*   **Maintain evidence alignment and governance compliance:** This objective emphasizes the importance of ensuring that the findings are supported by the evidence collected and adhere to established governance policies. This implies understanding what constitutes valid evidence and the relevant compliance regulations. This is crucial for auditability and trustworthiness of the results.
*   **Respect orchestration policies while completing assigned actions:**  This highlights the need to work within the defined workflow or orchestration framework. It means understanding the rules and constraints imposed by the system that assigns tasks and manages the overall process. This ensures efficiency and consistency across the entire workflow.
*   **Examples:**
    *   Avoiding manual analysis when automated tools exist.
    *   Adhering to the priority order of tasks assigned.
    *   Completing tasks within the allocated time window.

**Policy Context**

This section lists the policies that directly influence the Analysis Coordinator's decisions and actions. The Coordinator must be aware of these policies to ensure compliance and optimal performance.

*   **policy.evidence_threshold:** This policy likely defines the minimum level of evidence required to support a conclusion.  The coordinator must assess whether the available evidence meets this threshold.
*   **policy.latency_budget:** This policy sets a time limit for the analysis phase.  The coordinator must manage their time effectively to complete the analysis within the allotted budget.
*   **policy.research_depth:** This policy dictates how far the investigation should go. It limits the scope of the analysis, preventing excessive investigation that could waste resources.
*   **policy.seed.evidence_threshold:**  This policy likely applies specifically to the initial seed of information used to start the analysis. It defines the minimum evidence required to justify using that seed.
*   **policy.seed.max_research_depth:** Similar to `policy.research_depth`, but specific to the initial seed.  It limits the depth of investigation stemming from the seed.
*   **policy.seed.max_total_time:** Defines the maximum time allowed for analysis originating from the initial seed.
*   **policy.stage_alignment:**  This policy ensures that the analysis stage is aligned with other stages in the overall process. This likely covers aspects like data formats, reporting requirements, and communication protocols.

**Implications of Policy Context:**

The Analysis Coordinator needs to be able to:

*   Interpret and apply these policies effectively.
*   Identify situations where policies conflict or are unclear.
*   Escalate policy-related issues when necessary.

**Required Outputs**

These are the deliverables the Analysis Coordinator is responsible for producing.

*   **Structured summary of findings:**  This requires the ability to synthesize information from various sources into a clear and concise summary.  The summary should be organized in a predefined format, making it easy for others to understand and use the information.  This suggests a template or schema is provided.
*   **Confidence score with supporting evidence identifiers:** This requires the ability to assess the reliability of the findings and provide a quantitative measure of confidence.  The supporting evidence identifiers (e.g., document IDs, URLS, log entry IDs) are crucial for tracing the findings back to the source data and verifying their accuracy.
*   **Next-step recommendation or escalation flag:** The coordinator must be able to determine the appropriate next action based on the analysis. This could involve recommending further investigation, escalating the issue to a higher authority, or indicating that no further action is required.  The escalation flag signals a critical issue that requires immediate attention.

**Overall, the Analysis Coordinator plays a crucial role in ensuring the quality, compliance, and efficiency of the analysis process. They must be able to synthesize information, apply policies, and make informed decisions to drive the process forward.**