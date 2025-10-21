This outlines the role of a "Content Extraction Coordinator" specifically during the "Content Extraction" stage of a larger process. Let's break down the meaning and implications:

**Overall Role:**

The Content Extraction Coordinator is responsible for ensuring that content is extracted from a source in a way that is:

*   **Aligned with Evidence:**  The extraction process must be traceable back to the source and demonstrably supported by the evidence found within that source.  This likely means careful documentation of the extraction process and links to specific parts of the source material.
*   **Compliant with Governance:** The extraction process needs to adhere to pre-defined rules, regulations, and standards (governance) established for the overall process. This could involve things like data privacy, security, or specific information handling protocols.
*   **Policy-Driven:**  The Coordinator must operate within the constraints and guidelines defined by the orchestration policies.  This means they don't just extract content blindly; they do so in a way that optimizes for objectives like speed, accuracy, and cost-effectiveness, as dictated by the policies.

**Specific Objectives:**

*   **Maintain Evidence Alignment and Governance Compliance:** This is the overarching goal. Every action taken must be auditable and demonstrably adheres to the established rules.
*   **Respect Orchestration Policies while completing assigned actions:**  The Coordinator doesn't have autonomy outside of the policies. They are a cog in a larger, orchestrated system, and must follow the defined procedures.

**Policy Context (Key Definitions):**

This section lists several policy parameters that guide the Coordinator's actions. Understanding these is crucial:

*   **`policy.evidence_threshold`**:  The minimum level of confidence or supporting evidence required to consider a piece of information extracted as valid or accurate.
*   **`policy.latency_budget`**:  The maximum time allowed for the extraction process.
*   **`policy.research_depth`**: The extent to which the source needs to be examined or investigated to find relevant information. A higher research depth means a more thorough and time-consuming extraction.
*   **`policy.seed.evidence_threshold`**:  Similar to `policy.evidence_threshold`, but specifically applied to the "seed" information or initial entry point that started the extraction process. It determines how strong the initial evidence needs to be.
*   **`policy.seed.max_research_depth`**:  The maximum depth of investigation allowed for the initial seed information. Limits how much time is spent validating the starting point.
*   **`policy.seed.max_total_time`**: The total time allowed for validating the initial seed information.
*   **`policy.stage_alignment`**:  Ensures the extracted information is consistent with the overall goals and strategy of the current stage ("Content Extraction") and the larger process.

**Required Outputs:**

These are the deliverables expected from the Content Extraction Coordinator:

*   **Structured summary of findings:** A concise and organized overview of the key information extracted.  The structure is likely pre-defined (e.g., a template or specific data format).
*   **Confidence score with supporting evidence identifiers:**  A numerical rating of the reliability of the extracted information, along with references (identifiers) to the specific evidence in the source that supports the extracted information. This is key for traceability and auditability.
*   **Next-step recommendation or escalation flag:** Based on the extracted information and the confidence score, the Coordinator must either suggest the next logical step in the overall process or flag the situation for escalation to a higher authority if there are issues or uncertainties.

**In Summary:**

The Content Extraction Coordinator is a vital role in a process that requires reliable, auditable, and compliant extraction of information. They are not just extracting data; they are ensuring the data meets specific quality standards and is suitable for subsequent stages in the process. Their work is heavily governed by pre-defined policies and procedures, ensuring consistency and control.  The key skills required include:

*   **Attention to detail:** Ensuring accuracy in extraction and evidence tracking.
*   **Policy awareness:** Understanding and adhering to all relevant policies.
*   **Analytical skills:** Assessing the quality and reliability of information.
*   **Communication skills:**  Summarizing findings clearly and making appropriate recommendations.
*   **Technical proficiency:**  Using the required tools and systems for extraction, documentation, and reporting.

This role would likely be supported by tools for:

*   **Data extraction:** Software to pull information from various sources.
*   **Evidence management:**  A system for tracking and linking extracted data to its source.
*   **Policy enforcement:** Automated checks to ensure compliance with policies.
*   **Workflow management:** Tools to guide the Coordinator through the extraction process.