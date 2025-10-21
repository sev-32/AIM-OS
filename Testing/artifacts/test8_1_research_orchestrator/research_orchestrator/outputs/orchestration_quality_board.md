Okay, I've reviewed the descriptions of each role, and I understand the need for a "Quality Board :: Quality Board Primary" role that operates at the "Global Orchestration" stage. The purpose of this board is to oversee the entire process and ensure quality across all the different stages and roles involved.  Here's a breakdown of the responsibilities, policies, and outputs for this role, drawing upon the information provided:

**Quality Board :: Quality Board Primary**
Stage: Global Orchestration

## Objectives

*   **Ensure consistent adherence to governance policies across all stages.** This means actively monitoring all the individual roles (Search Coordination, Content Extraction, Analysis, Validation, Reporting) to ensure they are each operating within their policy constraints and contributing to the overall governance goals.
*   **Optimize the overall orchestration for efficiency and effectiveness.**  This involves looking at the "big picture" and identifying areas where the process can be improved. This may involve adjusting policy parameters, re-allocating resources, or modifying workflows.
*   **Identify and address policy conflicts or ambiguities.** When individual roles encounter conflicting or unclear policies, the Quality Board resolves these issues to ensure consistent application.
*   **Manage risk and ensure compliance with regulatory requirements.** Proactively identify potential risks throughout the process and take steps to mitigate them.

## Policy Context

The Quality Board is responsible for overseeing and potentially adjusting *all* of the following policies based on performance and feedback from the individual coordinator roles:

*   **policy.evidence_threshold:**  The Board monitors how this threshold is impacting each stage. Are some stages struggling to meet the threshold, causing bottlenecks? Is the threshold too low, leading to unreliable findings?  The Board might adjust this threshold globally or, in some cases, for specific stages.
*   **policy.latency_budget:**  The Board tracks the overall time spent in each stage. Are some stages consistently exceeding their latency budget?  If so, the Board investigates the root cause (e.g., insufficient resources, overly complex tasks, unrealistic budgets) and implements corrective actions.  This may involve reallocating resources, streamlining processes, or adjusting the budget.
*   **policy.research_depth:** The Board evaluates whether the research depth is appropriate for each stage. Is too much time being spent on deep research that yields little value?  Is the research depth too shallow, missing critical information?
*   **policy.seed.evidence_threshold:** The Board oversees the use of "seed" information and ensures that it meets the required evidence threshold before being used as a starting point for further investigation.
*   **policy.seed.max_research_depth:** The Board monitors how deeply the individual coordinators are investigating seed information and ensures that they are not exceeding the limits.
*   **policy.seed.max_total_time:** The Board monitors how much time is being spent investigating seed information and ensures that they are not exceeding the limits.
*   **policy.stage_alignment:** The Board ensures that all stages are aligned and working towards the overall objectives. This involves monitoring communication and collaboration between stages and resolving any conflicts or inconsistencies.
*   **policy.system_observability:** The Board needs access to system-wide data to monitor performance, identify issues, and track key metrics.
*   **policy.system_fallbacks:**  The Board is responsible for defining and maintaining fallback procedures in case of system failures or unexpected events.

**Specifically, the Quality Board uses the outputs of the individual roles to inform policy adjustments. For example:**

*   **If the Reporting Coordinator consistently reports low confidence scores,** the Quality Board might investigate whether the `policy.evidence_threshold` is set too low in earlier stages (e.g., Search Coordination or Content Extraction).
*   **If the Validation Coordinator consistently flags issues for escalation,** the Quality Board might review the `policy.research_depth` in the Analysis stage to ensure that the analysis is sufficiently thorough.
*   **If the Search Coordinator is consistently exceeding the `policy.latency_budget`,** the Quality Board might investigate whether the search strategy is too broad or if the available resources are inadequate.

## Required Outputs

The Quality Board itself produces outputs that reflect its oversight and guidance.

*   **Policy adjustment recommendations:** Based on the monitoring of individual stage performance, the Quality Board recommends adjustments to the policies outlined above.  These recommendations should be data-driven and clearly justified.
*   **Performance dashboards and reports:** The Board creates dashboards and reports to visualize key performance indicators (KPIs) across all stages.  These dashboards allow the Board to quickly identify trends, anomalies, and areas for improvement.  Example KPIs include:
    *   Average confidence scores
    *   Time spent in each stage
    *   Number of escalations
    *   Compliance violations
*   **Risk assessments and mitigation plans:** The Board conducts regular risk assessments to identify potential threats to the overall process and develops mitigation plans to address those threats.
*   **Audit reports:** The Board conducts audits to ensure compliance with governance policies and regulatory requirements.
*   **Training and guidance materials:** The Board develops and delivers training materials to ensure that all roles are aware of the relevant policies and procedures.
*   **Escalation resolutions:** The Board is responsible for resolving escalations that cannot be handled at the individual stage level.
*   **Process Improvement Proposals:** The board suggests significant process improvements based on observed trends and policy effectiveness.

**Key Skills for Quality Board Members:**

*   **Deep understanding of the entire process:**  Board members must have a comprehensive understanding of all stages and their interdependencies.
*   **Analytical skills:** The ability to analyze data, identify trends, and draw meaningful conclusions.
*   **Policy expertise:**  A thorough understanding of the relevant governance policies and regulatory requirements.
*   **Communication and collaboration skills:**  The ability to communicate effectively with individuals at all levels of the organization and to collaborate with other stakeholders.
*   **Decision-making skills:** The ability to make sound judgments based on the available information.
*   **Risk Management:** Identifying and evaluating potential risks.
*   **Strategic Thinking:**  Considering long-term implications of decisions.

**Success Metrics:**

The Quality Board's success can be measured by:

*   **Overall improvement in confidence scores.**
*   **Reduction in the number of escalations.**
*   **Adherence to latency budgets.**
*   **Fewer compliance violations.**
*   **Increased efficiency and effectiveness of the overall process.**
*   **Positive feedback from individual coordinators.**

In conclusion, the Quality Board serves as a critical oversight function, ensuring that the entire process is operating efficiently, effectively, and in compliance with relevant policies and regulations. It acts as a central point for monitoring performance, identifying issues, and driving continuous improvement.  Its data-driven approach to policy adjustments is crucial for maximizing the value of the entire orchestrated system.