Okay, I understand. As the "Key Fact Extractor Primary" stage, my objectives are to:

1.  **Extract key facts:** Identify and extract the most important facts from the provided input based on the prompt.
2.  **Maintain evidence alignment:**  For each fact extracted, record and link the specific source (identifier) that supports it.  This ensures traceability and verifiability.
3.  **Ensure governance compliance:** Operate within the boundaries set by the organizational policies.
4.  **Respect orchestration policies:** Coordinate with other components of the system as instructed.

I must consider and adhere to the following policies:

*   **`policy.evidence_threshold`:**  The minimum amount of supporting evidence required before considering a fact confirmed. This will influence my confidence score.
*   **`policy.latency_budget`:**  The maximum amount of time I can spend on this task.  I must prioritize accordingly.
*   **`policy.research_depth`:**  The level of detail I should go into while researching and extracting facts. This will dictate how exhaustively I search the provided input.
*   **`policy.seed.evidence_threshold`:** If this task originated from a "seed" or initial query, the evidence threshold might be different. I need to use this value if provided.
*   **`policy.seed.max_research_depth`:**  Similar to the above, if this is a "seed" task, there might be a different research depth constraint. I need to use this if provided.
*   **`policy.seed.max_total_time`:** Similar to the above, if this is a "seed" task, there might be a maximum total time constraint. I need to use this if provided.

My required outputs are:

*   **Structured summary of findings:** A clear and organized summary of the key facts I've identified.  This should be formatted for easy consumption by downstream tasks.
*   **Confidence score with supporting evidence identifiers:** For each fact, I'll provide a confidence score reflecting how certain I am that the fact is accurate, based on the supporting evidence and `policy.evidence_threshold`.  I will also list the identifiers of the specific sources that support the fact.
*   **Next-step recommendation or escalation flag:** Based on the findings and the policies, I will recommend the next step in the process. This could involve further analysis, escalation to a human analyst if the evidence is conflicting or insufficient, or confirmation of the findings.

In essence, I need to be efficient, accurate, and transparent in my fact extraction process while adhering to the specified constraints and policies. I'm ready to receive the input data and associated policy values to begin.