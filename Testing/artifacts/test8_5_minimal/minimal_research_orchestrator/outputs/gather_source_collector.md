Okay, this outlines the role of the "Source Collector Primary" within a larger system. Let's break down each section and discuss potential implications:

**Stage: Gather**

*   **Implication:** This role is focused on collecting information, not analyzing it deeply or taking action beyond gathering.

**Objectives**

*   **Maintain evidence alignment and governance compliance:**
    *   **Implication:** This emphasizes the need for the collected evidence to be relevant to the overall goal and adhere to pre-defined governance rules. The collector needs to understand what constitutes valid evidence.
    *   **Actionable Items:**
        *   Clear guidelines on what constitutes acceptable evidence (e.g., types of sources, quality criteria, format).
        *   Mechanisms for tracking and demonstrating compliance (e.g., metadata tagging, provenance tracking).
*   **Respect orchestration policies while completing assigned actions:**
    *   **Implication:** This role doesn't operate in isolation; it's part of a larger orchestrated workflow. The collector needs to be aware of and adhere to policies that govern the overall process.
    *   **Actionable Items:**
        *   Clear communication channels to understand the overall workflow and policies.
        *   Tools to monitor and adhere to orchestration policies (e.g., time limits, resource constraints).

**Policy Context**

*   **policy.evidence_threshold:** The minimum level of evidence required to support a finding.
    *   **Implication:** The collector needs to collect enough evidence to meet this threshold.  They must be able to judge the strength and relevance of evidence.
    *   **Actionable Items:**
        *   A defined scale or metric for measuring the "evidence threshold."
        *   Training on how to assess the quality and relevance of different sources.
*   **policy.latency_budget:** The maximum time allowed for collecting evidence.
    *   **Implication:** The collector needs to work efficiently to stay within the allotted time.
    *   **Actionable Items:**
        *   Tools and strategies for prioritizing sources and optimizing data collection.
        *   Alerting mechanisms if the latency budget is at risk.
*   **policy.research_depth:**  The breadth and depth of sources to be searched.
    *   **Implication:** Defines how far "down the rabbit hole" the collector should go. A shallow depth might involve only top-level sources, while a deep depth might involve analyzing underlying data and related research.
    *   **Actionable Items:**
        *   Clear definitions of what constitutes different levels of research depth.
        *   Tools to track and manage research depth (e.g., a branching search tree).
*   **policy.seed.evidence_threshold:** The minimum level of evidence required for seed evidence.
    *   **Implication:** Likely deals with initial evidence used as a starting point.  A different (potentially lower) evidence bar might be applied to this starting point.
    *   **Actionable Items:**
        *   Clear definition and examples of "seed evidence."
        *   Training on how seed evidence is used and its potential limitations.
*   **policy.seed.max_research_depth:** The maximum research depth for seed evidence.
    *   **Implication:** Limits the amount of time spent chasing down seed evidence.
    *   **Actionable Items:**  Same as for `policy.research_depth`, focusing on how to apply depth limits specifically to seed evidence.
*   **policy.seed.max_total_time:** The maximum total time to spend on seed evidence.
    *   **Implication:**  A hard stop for seed investigation, even if the evidence threshold hasn't been met.
    *   **Actionable Items:**  Time tracking and alerting mechanisms specific to seed evidence.

**Required Outputs**

*   **Structured summary of findings:**
    *   **Implication:** The collector needs to organize the collected information in a clear and consistent format.  This likely involves using a predefined schema or template.
    *   **Actionable Items:**
        *   A clear definition of the required structure (e.g., JSON, XML, tabular data).
        *   Tools to assist in structuring the data (e.g., data mapping tools, templates).
*   **Confidence score with supporting evidence identifiers:**
    *   **Implication:**  The collector needs to assess the reliability of their findings and provide a trail back to the specific evidence that supports their assessment.  This requires tracking the sources of information.
    *   **Actionable Items:**
        *   A defined method for calculating confidence scores (e.g., based on source credibility, consistency of evidence).
        *   A system for uniquely identifying and linking evidence items.
*   **Next-step recommendation or escalation flag:**
    *   **Implication:** The collector needs to be able to identify situations that require further investigation or action beyond their immediate scope. This requires some level of understanding of the overall goals of the system.
    *   **Actionable Items:**
        *   Clear criteria for recommending next steps or escalating issues.
        *   Training on potential escalation scenarios.

**Overall Considerations**

*   **Tooling:**  This role relies heavily on tools to automate data collection, track policies, and generate the required outputs.
*   **Training:** The collector needs to be trained on how to use the tools, understand the policies, and assess the quality and relevance of evidence.
*   **Monitoring & Feedback:** The performance of the collector needs to be monitored, and feedback should be provided to improve efficiency and accuracy.
*   **Potential Bottleneck:** Given the focus on evidence alignment and governance, the collector could become a bottleneck if the evidence threshold is set too high or the policies are too complex.

This breakdown provides a solid understanding of the Source Collector Primary role and its implications.  Further details would be needed to understand the specific context and to design the tools and processes to support this role effectively.