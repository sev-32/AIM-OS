Okay, this defines the **Trend Analyzer :: Trend Analyzer Primary** agent and its responsibilities. Let's break down the key elements and how they translate into practical actions:

**Overall Purpose:** This agent is responsible for **analyzing trends**, ensuring **evidence-based decision-making**, and operating within defined **governance and performance parameters.**

**Stage: Analysis** - This clearly indicates the agent's role within a larger pipeline. It's not generating the data (likely), nor making final decisions (likely another agent). It's *analyzing* existing information.

**Objectives (Key Tasks):**

*   **Maintain evidence alignment and governance compliance:**  This is crucial. The agent MUST ensure its analysis is based on verifiable evidence and conforms to defined rules. This likely involves:
    *   **Traceability:** Linking findings back to specific source materials (e.g., documents, datasets, API calls).  This is what the "evidence identifiers" output will support.
    *   **Policy Enforcement:**  Adhering to the policies listed below, ensuring its analysis doesn't violate any limits or requirements.
    *   **Data Integrity:**  Verifying the accuracy and reliability of the data it's using.

*   **Respect orchestration policies while completing assigned actions:** This means the agent needs to be aware of its place within a larger workflow. It should:
    *   **Understand dependencies:** Know what data it receives and how its output is used by other agents.
    *   **Manage time effectively:**  Stay within the "latency budget" (see policies).
    *   **Follow any pre-defined steps:** Avoid deviating from the expected process.

**Policy Context (Key Constraints):**

These policies act as parameters for the agent's behavior.  They are *critical* and the agent must be designed to consult and adhere to them.

*   **policy.evidence_threshold:**  The minimum amount of evidence required to support a conclusion. For example, it might require at least three independent sources to confirm a trend.  This likely impacts the agent's decision to escalate or move forward.

*   **policy.latency_budget:**  The maximum time allowed for the analysis. The agent needs to be efficient and avoid unnecessary processing.

*   **policy.research_depth:**  Limits how extensively the agent can search for information.  This prevents the agent from getting bogged down in irrelevant data.

*   **policy.seed.evidence_threshold:** The minimum amount of evidence required for conclusions based on the initial "seed" data. This might be lower than the general `evidence_threshold` to allow for initial hypothesis generation.

*   **policy.seed.max_research_depth:**  Limits the initial research depth for "seed" data.  Again, likely less than the general `research_depth` to focus the initial exploration.

*   **policy.seed.max_total_time:** The maximum total time allocated to processing the "seed" data.  This constrains the initial investigation.

**Required Outputs (What the Agent Delivers):**

*   **Structured summary of findings:**  A clear and concise description of the identified trends.  This should be in a format that can be easily understood and processed by other agents or humans.  Examples:
    *   JSON object with trend names, descriptions, associated data points, and timestamps.
    *   Markdown report with clear headings and supporting charts.
    *   Knowledge graph representation.

*   **Confidence score with supporting evidence identifiers:**  Crucial for trust and auditability.
    *   **Confidence Score:**  A numeric value (e.g., 0-100%) reflecting the agent's certainty in the identified trends. This must be tied to the `evidence_threshold`.
    *   **Evidence Identifiers:**  Unique keys that link the conclusions back to the specific sources used (e.g., document IDs, database record IDs, API call logs).  These identifiers are vital for verifying the analysis and resolving any disagreements.

*   **Next-step recommendation or escalation flag:** Determines the subsequent action.
    *   **Next-step Recommendation:** What should be done next based on the analysis? Examples:  "Further investigation needed on sub-trend X," "Confirm trend with additional data source Y," "Submit findings to decision agent Z."
    *   **Escalation Flag:**  Indicates a serious issue that requires human intervention. Examples:  "Data quality issue detected in source A," "Policy violation detected," "Conflicting evidence exceeds allowed threshold."

**How to Implement this Agent (High-Level):**

1.  **Input:**  Define the expected input format (e.g., data streams, text documents, API responses).
2.  **Evidence Management:** Design a system for storing and tracking evidence.  Consider using a graph database or a specialized evidence management framework.
3.  **Analysis Logic:** Implement the core algorithms for trend detection.  Consider using statistical methods, machine learning models, or rule-based systems.
4.  **Policy Engine:**  Create a module that enforces the policies.  This module should be consulted throughout the analysis process.
5.  **Confidence Scoring:**  Develop a method for calculating confidence scores based on the amount and quality of evidence.  The `evidence_threshold` is a key input here.
6.  **Output Formatting:**  Implement a system for generating the structured summary, confidence score, evidence identifiers, and next-step recommendation/escalation flag.
7.  **Testing:**  Thoroughly test the agent to ensure it meets the required accuracy, performance, and governance criteria.  Pay special attention to edge cases and potential policy violations.

**Example Scenario:**

Imagine the agent is analyzing sales data to identify emerging trends.

*   **Input:**  A stream of daily sales figures from multiple regions.
*   **Analysis:**  The agent detects a significant increase in sales of product "X" in region "Y" over the past month.
*   **Evidence:**  The agent identifies the relevant sales records (e.g., order IDs, timestamps, customer demographics).
*   **Policy Check:**  The agent verifies that the increase is statistically significant and that it meets the `evidence_threshold`. It also checks the `latency_budget` to ensure it's completing the analysis within the allowed time.
*   **Output:**
    *   **Structured Summary:**  "Sales of product X in region Y have increased by 25% over the past month."
    *   **Confidence Score:** 85%
    *   **Evidence Identifiers:**  [orderID-1234, orderID-5678, orderID-9012, ...]
    *   **Next-step Recommendation:** "Investigate marketing campaigns in region Y to identify potential drivers of the sales increase."

This agent's success hinges on its ability to effectively manage evidence, adhere to policies, and provide clear, actionable insights.