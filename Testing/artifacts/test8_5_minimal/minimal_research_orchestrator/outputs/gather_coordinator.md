This outlines the role of the "Gather Coordinator" within the "Gather" stage of a larger process (likely a data gathering, research, or investigative workflow).  Let's break down each section and consider how this role would function.

**Overall Purpose:** The Gather Coordinator acts as the orchestrator for the data gathering process, ensuring compliance with predefined policies and delivering a structured and insightful summary of findings. They are not just collecting data, but also evaluating its reliability and relevance, and determining the next appropriate action.

**Stage: Gather** - This is the active data collection phase. It's likely preceded by a planning or scoping stage and followed by analysis and action.

**## Objectives**

*   **Maintain evidence alignment and governance compliance:** This is a core responsibility.  It means ensuring that all gathered evidence is relevant to the defined goal (alignment) and complies with all established policies and regulations (governance). Examples:
    *   **Evidence Alignment:** If the goal is to assess the security posture of a particular server, the Gather Coordinator would prioritize collecting evidence related to that server's configuration, vulnerability scans, logs, etc., and deem irrelevant general data security information.
    *   **Governance Compliance:** This could include adhering to data privacy regulations (e.g., GDPR), internal security policies, or data retention guidelines. The Gather Coordinator must ensure the data collection process and subsequent storage/handling of data are compliant.
*   **Respect orchestration policies while completing assigned actions:** The Gather Coordinator works within a larger framework (orchestration).  They need to be aware of and adhere to the policies governing the overall workflow. This implies they are being assigned tasks and responsibilities within the larger process.
    *   **Example:** An orchestration policy might limit the types of sources they can access (e.g., no external websites for confidential data). The Coordinator has to respect these limitations.

**## Policy Context**

This section outlines the key policies that constrain and guide the Gather Coordinator's actions.  These policies are likely configurable and might vary depending on the specific investigation or task.

*   **`policy.evidence_threshold`:** The minimum acceptable level of evidence required before a conclusion can be drawn.
    *   **Example:** A value of "0.7" might mean that the Coordinator needs at least 70% confidence in their findings. If they fall below that, they need to gather more evidence.
*   **`policy.latency_budget`:** The maximum time allowed to complete the Gather stage.
    *   **Example:**  A value of "2 hours" means the Coordinator must complete their data gathering within that timeframe, even if they haven't reached the `evidence_threshold`. This might trigger an escalation.
*   **`policy.research_depth`:**  How deeply the Coordinator should investigate each piece of evidence or source.
    *   **Example:** "Shallow" might mean only skimming the surface of a source, while "Deep" requires a thorough review.
*   **`policy.seed.evidence_threshold`:**  Specifically applies to the initial "seed" data (the starting point for the investigation).  This allows for a lower bar to get started.
    *   **Example:** You might start with a broader scope of research (lower evidence threshold) to identify promising leads, then apply a higher threshold as you narrow in.
*   **`policy.seed.max_research_depth`:**  Limits how deeply the Coordinator can research initial leads. This is likely to prevent getting stuck down rabbit holes early on.
    *   **Example:** Prevents excessive analysis of initial leads that may not be fruitful.
*   **`policy.seed.max_total_time`:**  Limits the total time spent on researching initial leads.  Similar to `policy.seed.max_research_depth`, this encourages a quick assessment of seed data.
*   **`policy.stage_alignment`:**  This defines how closely the data gathering needs to align with the overall objectives of the process. This could be achieved by comparing the collected evidence with the initial requirements.
    *   **Example:** A policy dictating that 90% of the gathered evidence must directly relate to the specified incident.

**## Required Outputs**

*   **Structured summary of findings:**  This is the main deliverable.  It should be organized and easy to understand.
    *   **Example:** A JSON object, a table, or a well-formatted report that presents the gathered information in a logical and concise way.  Crucially, it needs to be *structured* for downstream processing.
*   **Confidence score with supporting evidence identifiers:**  The Coordinator needs to provide a quantitative assessment of the reliability of their findings, along with references to the specific evidence that supports the score.
    *   **Example:** "Confidence: 0.85, Evidence IDs: [doc123, log456, alert789]". This allows others to verify the assessment and trace the evidence back to its source.
*   **Next-step recommendation or escalation flag:**  The Coordinator must decide what should happen next based on their findings. This could involve:
    *   **Next-step Recommendation:** Suggesting a specific action to take (e.g., "Escalate to Level 2 support" or "Begin remediation steps").
    *   **Escalation Flag:**  Indicating that the issue requires attention from a higher authority or a different team (often due to time limits, severity of findings, or the inability to meet policy requirements).  This is likely triggered if `latency_budget` is exceeded before `evidence_threshold` is met.

**In Summary:**

The Gather Coordinator is a critical role responsible for efficient and compliant data gathering. They navigate the complex landscape of policies, assess the quality of evidence, and provide actionable recommendations to drive the overall process forward. They are essentially the intelligence analyst of the data gathering stage, ensuring that the right information is collected, validated, and presented effectively.  Their success is measured by the quality, completeness, and timeliness of their output.