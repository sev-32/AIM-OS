Okay, this outlines the responsibilities and constraints of a "Rapid Triage Coordinator" specifically during the "Rapid Triage" stage of some larger process. Let's break down each part and consider its implications:

**Role: Rapid Triage Coordinator**

*   **Focus:** The primary job is to quickly assess and prioritize information. This isn't deep investigation, but rather a fast evaluation to determine next steps.
*   **Emphasis on Coordination:** This role suggests a need to manage information flow and potentially delegate tasks to other resources.

**Stage: Rapid Triage**

*   **Characteristics:** Fast-paced, preliminary assessment, aimed at filtering and directing resources.
*   **Goal:** To quickly identify critical items that require immediate attention and filter out less urgent or irrelevant information.

**Objectives:**

*   **Maintain Evidence Alignment and Governance Compliance:**
    *   **Evidence Alignment:** Ensuring that the information gathered supports the claims being made and that different pieces of evidence are consistent with each other. This is about verifying the credibility and relevance of the information.
    *   **Governance Compliance:** Adhering to established rules, policies, and regulations related to data handling, privacy, security, and other relevant areas. This could involve documenting data sources, following privacy protocols, and ensuring data integrity.  This suggests that the process handles sensitive data.
*   **Respect Orchestration Policies While Completing Assigned Actions:**
    *   **Orchestration Policies:**  These are rules or guidelines that govern how the overall process is managed. This could involve things like task assignment, resource allocation, and workflow management. The coordinator needs to be aware of and adhere to these policies while performing their triage activities. This hints at an automated or semi-automated system that manages the overall workflow.

**Policy Context (These are constraints or parameters that influence how the coordinator operates):**

*   **policy.evidence_threshold:** Minimum level of evidence required to support a claim or decision. The coordinator must ensure that the evidence gathered meets this threshold. Low threshold = quick decisions with less robust evidence; high threshold = more rigorous analysis before moving on.
*   **policy.latency_budget:** The maximum allowable time for completing the triage process.  This highlights the "rapid" nature of the triage. The coordinator needs to work efficiently to stay within this budget.
*   **policy.research_depth:** The level of detail or scope of research required during triage. This dictates how thoroughly the coordinator needs to investigate potential leads or sources of information. Shallower research = faster triage, but potentially higher risk of missing something.
*   **policy.seed.evidence_threshold:** The initial evidence threshold for starting the triage process. This could be a lower bar than the overall `policy.evidence_threshold` for initial screening.
*   **policy.seed.max_research_depth:** The maximum depth of research allowed on the initial "seed" or starting point of the triage. This likely focuses on initial assessment, preventing early rabbit holes.
*   **policy.seed.max_total_time:** The maximum time allowed for researching the initial "seed" data.  Further emphasizes the speed required at the beginning of the triage.
*   **policy.stage_alignment:**  Ensuring the triage process aligns with the goals and objectives of the overall process. This prevents the triage from going off on tangents or pursuing irrelevant information.

**Required Outputs:**

*   **Structured Summary of Findings:**  A concise and organized report summarizing the key information gathered during triage. This should be presented in a way that is easy to understand and allows for quick decision-making.  The "structured" aspect suggests a template or standardized format.
*   **Confidence Score with Supporting Evidence Identifiers:**
    *   **Confidence Score:** A numerical or qualitative assessment of the reliability and certainty of the findings. This helps decision-makers understand the level of risk associated with the triage results.
    *   **Supporting Evidence Identifiers:** Links or references to the specific pieces of evidence that support the confidence score and overall findings. This allows for verification and further investigation if needed.
*   **Next-Step Recommendation or Escalation Flag:**
    *   **Next-Step Recommendation:**  A suggestion for the next action that should be taken based on the triage results (e.g., further investigation, referral to a specialist, closure of the case).
    *   **Escalation Flag:** A signal that the issue requires immediate attention or intervention from a higher authority or a different team.  This indicates the presence of critical issues discovered during triage.

**In summary, the Rapid Triage Coordinator acts as a gatekeeper, quickly assessing incoming information, ensuring its alignment with established policies and standards, and making recommendations for next steps or escalating urgent issues, all within strict time and evidence constraints.**

**Key Implications:**

*   **Speed is critical.**  The "Rapid" nature and the various time limits indicate this.
*   **Accuracy and completeness are important, but balanced against speed.** The evidence thresholds and research depth parameters reflect this trade-off.
*   **Documentation and auditability are essential.**  The emphasis on evidence identifiers and governance compliance highlights this.
*   **Clear decision-making authority is needed.**  The coordinator must be empowered to make triage decisions and direct resources effectively.
*   **Understanding of the broader context is crucial.** The coordinator must be aware of the overall process goals and objectives, as well as relevant policies and regulations.

This framework strongly suggests a structured process likely supported by automation or specialized tools to manage the information flow, policy enforcement, and evidence tracking.