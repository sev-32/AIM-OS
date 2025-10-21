Okay, this outlines the core responsibilities and constraints of a Web Agent tasked with performing literature searches within a broader workflow. Let's break down the components:

**Purpose:**

The agent's primary role is literature search, contributing to a larger goal (not explicitly stated but implied). It must perform this search effectively while adhering to specific policies and producing structured, actionable results.

**Objectives:**

*   **Maintain Evidence Alignment and Governance Compliance:**  This is a crucial objective.  It emphasizes that the agent must:
    *   **Evidence Alignment:**  The findings must directly support the overall research objective and be traceable to their sources.  No "fishing expeditions" or inclusion of irrelevant information.
    *   **Governance Compliance:**  The agent must operate within the specified rules and guidelines, including data privacy, copyright, and internal organizational policies.  This objective likely requires careful source selection and citation management.
*   **Respect Orchestration Policies while Completing Assigned Actions:** The agent is part of a larger system ("orchestration").  It can't just do whatever it wants.  It needs to be aware of and adhere to policies that govern the entire workflow, such as:
    *   **Prioritization:**  The agent needs to understand how its task fits into the overall workflow and prioritize its actions accordingly.
    *   **Resource Allocation:** It might have limitations on the resources it can use (e.g., number of searches, API calls, compute time).
    *   **Dependencies:**  It might need to wait for other agents or processes to complete their tasks before proceeding.

**Policy Context:**

These variables influence how the agent executes its tasks. Understanding them is critical for effective operation.

*   **`policy.evidence_threshold`:**  Defines the minimum level of confidence or quality of evidence required for inclusion.  This could be based on source credibility, sample size, statistical significance, or other factors.  A higher threshold means the agent will be more selective.
*   **`policy.latency_budget`:**  Specifies the maximum allowable time for the agent to complete its task.  This dictates how quickly the agent must find, process, and summarize the information. It could affect the depth of the search.
*   **`policy.research_depth`:**  Controls how far the agent should delve into the literature.  A shallow search might only involve a few top-level sources, while a deeper search might involve following citations, exploring related articles, and even contacting authors.  This will likely be combined with `policy.latency_budget` to optimize the trade-off between speed and thoroughness.
*   **`policy.seed.evidence_threshold`:**  Similar to `policy.evidence_threshold`, but specifically applies to the "seed" or initial sources used to start the literature search. This ensures that the initial data is reliable.
*   **`policy.seed.max_research_depth`:**  Specifies the maximum depth the agent can explore from the initial "seed" sources.  This prevents the agent from getting lost in tangential information.
*   **`policy.seed.max_total_time`:**  Specifies the maximum amount of time dedicated to analyzing the initial "seed" sources before expanding the search.  This ensures that the agent doesn't spend too long on the initial seeds and can broaden the search.

**Required Outputs:**

These outputs are what the agent *must* produce for the next stage of the workflow.  They need to be clear, consistent, and actionable.

*   **Structured summary of findings:** This implies the agent needs to extract relevant information from the literature and present it in a standardized format.  This could be a table, a list of bullet points, or a structured document using a specific schema. The format likely depends on what the downstream processes require.
*   **Confidence score with supporting evidence identifiers:**  The agent must provide a measure of how confident it is in its findings.  Crucially, it *must* link that confidence score to the specific evidence that supports it.  This allows downstream processes to assess the validity of the findings.  Evidence identifiers might be URLs, DOI's, or internal references to specific documents or sections.
*   **Next-step recommendation or escalation flag:**  The agent needs to make a recommendation based on its findings.  This could be:
    *   **Next-step recommendation:** Suggesting specific actions that should be taken based on the literature search (e.g., "Investigate X," "Contact Author Y," "Conduct a new search using different keywords").
    *   **Escalation flag:**  Indicating that the agent is unable to complete its task or has encountered a situation that requires human intervention.  This might be due to:
        *   Insufficient evidence
        *   Conflicting information
        *   Ethical concerns
        *   Technical difficulties

**In Summary:**

This is a well-defined description of a web agent for literature search. The emphasis on governance, evidence alignment, and structured outputs suggests a focus on reliability and auditability. The policy context provides the agent with the necessary constraints to operate effectively within the broader workflow. This design promotes reproducibility and trustworthy results.