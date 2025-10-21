Okay, this outlines the role of a "Question Curator Primary" during the Intake & Scoping stage.  Here's a breakdown of the components and how they likely relate to the tasks involved:

**Overall Role:** The Question Curator Primary is responsible for initial assessment and preparation of a question for further processing. They act as a gatekeeper, ensuring the question is well-defined, has a sufficient foundation in available evidence, and adheres to defined policies.

**Stage: Intake & Scoping** - This signifies the initial phase where a question is received and its scope is determined.  Key activities would include:

*   Understanding the question.
*   Identifying the core concepts and entities.
*   Determining the scope of the required investigation.
*   Gathering initial, preliminary evidence.

**Objectives:**

*   **Maintain evidence alignment and governance compliance:** This emphasizes that the curator must ensure the question and any preliminary analysis are grounded in verifiable evidence and adhere to relevant compliance standards.  This likely includes data privacy, ethical considerations, and regulatory requirements.
*   **Respect orchestration policies while completing assigned actions:**  This highlights the importance of following pre-defined workflows and rules established by the orchestration system (a higher-level system managing the overall question answering process).  It means the curator cannot deviate from the established procedures without proper authorization.

**Policy Context:**  These policies constrain the curator's activities:

*   **`policy.evidence_threshold`:** The minimum amount of evidence required to support an initial assessment.  Below this threshold, the question might be rejected or require further investigation.
*   **`policy.latency_budget`:** The maximum time allowed for the curator to complete their assigned tasks. This forces efficiency and prioritization.
*   **`policy.research_depth`:**  The maximum level of detail the curator should go into when researching the question. This prevents them from getting bogged down in overly complex or tangential areas.
*   **`policy.seed.evidence_threshold`:**  Specifically for "seed" questions (likely initial questions used to kickstart a broader investigation), this defines the minimum evidence needed for consideration.
*   **`policy.seed.max_research_depth`:** The maximum research depth allowed for seed questions, preventing excessive initial investment.
*   **`policy.seed.max_total_time`:** The maximum total time allowed for processing a seed question, enforcing a tight timeframe for initial triage.

**Required Outputs:**

*   **Structured summary of findings:** A concise, organized report summarizing the initial evidence gathered and the key takeaways.  This would likely include identified entities, relevant sources, potential biases, and any ambiguities in the question.  This may take a specific format (e.g., JSON, Markdown, database entry) to facilitate downstream processing.
*   **Confidence score with supporting evidence identifiers:** A numerical score reflecting the curator's confidence in the validity and completeness of the initial findings.  Crucially, this score *must* be linked to the specific evidence sources used to justify the confidence level. (e.g., a list of document IDs, database record numbers, or URLs).  This provides transparency and traceability.
*   **Next-step recommendation or escalation flag:** A recommendation on what should happen next.  This could include:
    *   Passing the question on to a different curator with specialized expertise.
    *   Triggering a more in-depth research phase.
    *   Marking the question as requiring clarification.
    *   Escalating the question to a supervisor if it falls outside the defined scope or requires special handling.  The escalation flag would likely include a reason for escalation.

**In practice, this role would involve the following:**

1.  **Receive a Question:** The system provides the curator with a new question to process.
2.  **Understand the Question:**  The curator carefully reads and analyzes the question to understand its meaning and intent.
3.  **Gather Initial Evidence:** Using available tools and resources (e.g., knowledge bases, search engines, databases), the curator searches for relevant information related to the question.
4.  **Synthesize Findings:** The curator summarizes the key findings from the initial evidence, focusing on information that directly addresses the question.
5.  **Assess Confidence:**  Based on the quality, quantity, and relevance of the evidence, the curator assigns a confidence score to their findings.
6.  **Identify Evidence:** The curator meticulously records the identifiers of all evidence sources used to support their findings.
7.  **Determine Next Steps:** Based on the evidence, confidence score, and pre-defined policies, the curator recommends the next step in the question answering process (e.g., further research, escalation, clarification).
8.  **Generate Outputs:** The curator creates the structured summary, confidence score with evidence identifiers, and next-step recommendation, and submits them to the system.

**Example Scenario:**

Let's say the question is: "Is there evidence linking long-term use of proton pump inhibitors (PPIs) to an increased risk of dementia?"

The Question Curator Primary would:

1.  **Understand the question:**  They would recognize "proton pump inhibitors" and "dementia" as key concepts.
2.  **Gather Initial Evidence:** They might search medical databases (e.g., PubMed, Cochrane Library) for relevant studies and meta-analyses.
3.  **Synthesize Findings:** They might find a few observational studies suggesting a possible link but also find conflicting evidence.
4.  **Assess Confidence:** Based on the mixed evidence, they might assign a confidence score of, say, 0.6 (on a scale of 0 to 1, where 1 is high confidence).
5.  **Identify Evidence:** They would record the PubMed IDs or DOI's of the studies they reviewed.
6.  **Determine Next Steps:** Given the suggestive but inconclusive evidence, they might recommend further research with a deeper dive into meta-analyses and randomized controlled trials, if available.
7.  **Generate Outputs:** They would create a structured summary outlining the findings, the confidence score (0.6), the PubMed IDs of the studies used, and the recommendation for further research.

This detailed explanation clarifies the responsibilities and constraints of the Question Curator Primary role in the Intake & Scoping stage.  It highlights the importance of evidence-based decision-making, policy adherence, and efficient processing to ensure the smooth operation of the overall question answering system.