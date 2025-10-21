Okay, this defines the role of a Literature Reviewer within a specific system, focusing on initial investigation.  Let's break down the implications of each element:

**Stage: Investigation**

*   This indicates this is likely the initial phase of a larger research process. The focus is on exploring the existing literature to understand the landscape and identify key themes and potential avenues for further investigation.

**Objectives**

*   **Maintain evidence alignment and governance compliance:** This is crucial. The reviewer must ensure that all claims and conclusions are directly supported by the evidence found in the literature and that the entire process adheres to established governance rules and regulations (e.g., citation standards, data privacy, ethical considerations). This suggests a robust audit trail is needed.
*   **Respect orchestration policies while completing assigned actions:** The reviewer operates within a larger, orchestrated workflow. They must follow the pre-defined steps and protocols established by this orchestration system. This likely means the reviewer has defined inputs and outputs and a specific set of tasks to perform.

**Policy Context**

This section defines parameters and constraints that govern the reviewer's actions:

*   **policy.evidence_threshold:**  Minimum level of supporting evidence required for inclusion.  A higher threshold means stricter criteria for accepting a source or conclusion.  This influences the types of sources considered (e.g., peer-reviewed vs. grey literature) and the depth of analysis.
*   **policy.latency_budget:**  Maximum allowed time to complete the review process.  This constrains the number of sources that can be analyzed and the depth of analysis performed on each.
*   **policy.research_depth:**  The breadth and depth of the search.  A deeper search would involve a wider range of databases, search terms, and potentially manual searching. A shallower search would be more focused.
*   **policy.seed.evidence_threshold:** The evidence threshold specifically for the initial seed sources or articles that kick off the research. This might be lower than the general `policy.evidence_threshold` to cast a wider net at the beginning.
*   **policy.seed.max_research_depth:** The maximum research depth allowed starting from the initial "seed" papers.  This prevents the initial search from becoming too broad or taking too long.  It's likely a limit on the number of citations followed from the seed papers.
*   **policy.seed.max_total_time:** Maximum allowed time for the initial research based on the "seed" papers. This limits the initial scoping phase and prevents it from consuming the entire latency budget.

**Required Outputs**

*   **Structured summary of findings:**  A concise and organized presentation of the key insights gleaned from the literature review. This likely follows a predefined format (e.g., bullet points, tables, specific headings) to ensure consistency.
*   **Confidence score with supporting evidence identifiers:** This is essential for evaluating the reliability of the findings. The confidence score reflects the reviewer's assessment of the strength of the evidence.  The evidence identifiers (e.g., citation keys, URLs) provide traceability to the original sources that support the findings.
*   **Next-step recommendation or escalation flag:** The reviewer needs to determine the next course of action based on their findings. This could be a recommendation to continue the research in a specific direction, to explore alternative approaches, or to escalate the issue if they encounter a critical problem (e.g., lack of relevant data, ethical concerns).

**In summary, this document describes a Literature Reviewer operating in an automated system. Their job is to:**

1.  **Investigate:** Explore existing literature on a specific topic.
2.  **Summarize:**  Produce a structured summary of the key findings.
3.  **Assess:** Evaluate the confidence in those findings based on the evidence.
4.  **Recommend:** Suggest the next step in the research process or flag issues for escalation.

**Key Considerations:**

*   **Automation:** The document strongly implies a degree of automation in the literature review process. This suggests the reviewer might be using software tools to assist with searching, analyzing, and summarizing the literature.
*   **Traceability:**  Evidence alignment and governance compliance highlight the importance of traceability. The system needs to be able to track the origin and evolution of each finding.
*   **Constraint Management:** The policy context defines explicit constraints on the reviewer's activities. The system must effectively manage these constraints to ensure the review is completed within the allowed time and resources.

This is a well-defined role that is designed to be repeatable, reliable, and efficient. It emphasizes evidence-based reasoning and adherence to pre-defined rules and policies.