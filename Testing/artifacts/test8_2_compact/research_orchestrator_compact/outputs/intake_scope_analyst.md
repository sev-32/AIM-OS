Okay, this outlines the role of a Scope Analyst during the Intake & Scoping stage. Let's break down what it means and how this analyst would operate:

**Role Summary: Scope Analyst Primary (Intake & Scoping)**

The Scope Analyst's primary responsibility at this stage is to **determine the initial scope and feasibility of an investigation or project, while adhering to specific policies and maintaining a high level of evidence-based decision making.** They act as a critical filter, preventing resources from being wasted on unpromising or non-compliant initiatives.

**Key Responsibilities & Activities:**

*   **Evidence Gathering & Analysis:** The core function is to gather initial evidence related to the subject of the scope. This might involve searching databases, analyzing reports, reviewing internal documents, or even conducting preliminary interviews (depending on the context).
*   **Evidence Alignment:**  Ensuring that the evidence gathered aligns with the purpose and scope of the investigation/project.  This means verifying the relevance, reliability, and credibility of the information.
*   **Governance Compliance:**  Adhering to established governance procedures and policies. This could include things like data security, privacy regulations, and internal audit requirements.
*   **Policy Adherence:**  Strictly following the policies outlined (see details below). This likely involves specific constraints on time spent, the depth of research, and the quality of evidence required.
*   **Structured Summarization:**  Preparing a clear and concise summary of the findings from the initial evidence review. This summary needs to be structured in a way that facilitates decision-making by other stakeholders.
*   **Confidence Scoring:**  Assigning a confidence score (likely a percentage or a rating scale) to the findings based on the strength and consistency of the supporting evidence. Crucially, this score *must* be accompanied by a list of the specific evidence identifiers that support it.  This allows others to review the basis for the confidence assessment.
*   **Recommendation/Escalation:**  Based on the findings and confidence score, making a recommendation.  This could be to proceed with the investigation/project, to refine the scope, to gather more evidence, or to escalate the issue to a higher authority if certain thresholds are met or if red flags are identified.
*   **Respect Orchestration Policies:** This suggests that the Scope Analyst operates within a broader workflow system that directs their tasks and priorities. They need to ensure they are completing their assigned actions within the framework and guidelines of the orchestration policy.

**Understanding the Policies:**

The listed policies are critical constraints:

*   **`policy.evidence_threshold`:**  This defines the *minimum* amount and/or quality of evidence required to reach a certain level of confidence to proceed (or not proceed).  For example, it might state that at least three independent sources are required to support a claim.
*   **`policy.latency_budget`:**  This sets a time limit on how long the Scope Analyst can spend on the initial scoping process. This is a key constraint that forces them to prioritize efficiently.
*   **`policy.research_depth`:**  This limits the depth of investigation permitted during this initial phase. It might restrict the type of data sources that can be accessed or the amount of time spent on each source. The goal is to avoid "analysis paralysis" at the initial stage.
*   **`policy.seed.evidence_threshold`:**  This likely refers to a pre-existing "seed" of information or initial leads that sparked the investigation/project. This policy defines the minimum quality and quantity of evidence required to even *begin* the scoping process based on the seed.
*   **`policy.seed.max_research_depth`:**  Related to the "seed" information, this limits how deeply the analyst can investigate the initial leads before deciding whether to proceed.
*   **`policy.seed.max_total_time`:**  The maximum time permitted to research the "seed" information and make a determination. This directly relates to the `latency_budget` but is specific to the initial leads.

**Example Scenario:**

Imagine the Scope Analyst is investigating a potential fraud case.

1.  **Seed Information:** They start with an initial "seed" of information: a tip-off from an anonymous source alleging suspicious transactions.
2.  **Policy Application:**
    *   `policy.seed.evidence_threshold`: The analyst needs to find at least *two* corroborating pieces of evidence (e.g., unusual transaction patterns, complaints from other employees) before proceeding further.
    *   `policy.seed.max_research_depth`: They can only search internal databases and review publicly available information about the individuals involved. They are not allowed to contact any external parties at this stage.
    *   `policy.seed.max_total_time`:  They have a maximum of 2 hours to investigate the seed information.
    *   `policy.evidence_threshold`: To recommend a full investigation, they need to achieve a confidence score of at least 80%, supported by at least three independent pieces of evidence.
    *   `policy.latency_budget`: The entire scoping process (including the seed investigation) cannot exceed 4 hours.
    *   `policy.research_depth`: They are limited to internal databases and publicly available information.
3.  **Action:**  The analyst searches internal transaction logs, employee records, and publicly available financial statements.
4.  **Output:**
    *   **Structured Summary:**  "Review of transactions revealed a pattern of payments to shell companies. Employee X's expense reports show discrepancies.  No known prior complaints against Employee X."
    *   **Confidence Score:**  65% (Transactions: ID#1234, Expense Reports: ID#5678).
    *   **Recommendation:**  "Recommend further investigation, but suggest focusing on the identified transactions and expense reports.  Confidence score below threshold for full investigation.  Recommend verifying employee's involvement."

**Key Skills & Requirements:**

*   **Analytical Skills:**  Ability to quickly and efficiently analyze information from various sources.
*   **Research Skills:**  Proficiency in using databases, search engines, and other research tools.
*   **Policy Understanding:**  Deep understanding of the relevant policies and regulations.
*   **Communication Skills:**  Ability to clearly and concisely communicate findings in a structured format.
*   **Objectivity:**  Ability to remain objective and unbiased in their assessment of the evidence.
*   **Time Management:**  Ability to manage time effectively and prioritize tasks to meet deadlines.
*   **Attention to Detail:**  Critical for ensuring accuracy and completeness in the evidence gathering and analysis process.

In conclusion, the Scope Analyst is a critical gatekeeper, ensuring that resources are allocated efficiently and that investigations are grounded in evidence and compliant with relevant policies. Their role is demanding and requires a specific skillset focused on rapid assessment and objective evaluation.