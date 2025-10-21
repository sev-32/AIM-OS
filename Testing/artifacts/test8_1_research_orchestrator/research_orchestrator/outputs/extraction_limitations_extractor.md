Okay, I understand. This "Limitations Extractor Primary" stage is responsible for extracting information specifically about **limitations** from a given content source.  My job is to:

1.  **Extract Limitations:** Identify and isolate statements, phrases, or sections within the content that describe limitations of a product, service, research study, or any other subject.
2.  **Maintain Compliance:** Ensure all actions adhere to the provided policies:
    *   **Evidence Alignment & Governance:**  This likely means documenting the source and location of each identified limitation within the content, making it traceable and auditable.
    *   **Orchestration Policies:** Follow the established workflow and guidelines within the larger system.
3.  **Adhere to Policy Parameters:** Respect the constraints outlined in the `policy.*` variables:
    *   `policy.evidence_threshold`:  The minimum level of confidence (or number of supporting references) required before considering a limitation as valid.
    *   `policy.latency_budget`: The maximum time allowed for this stage to complete its analysis.
    *   `policy.research_depth`:  The extent to which I should delve into the source material to find limitations. A higher depth implies a more thorough search.
    *   `policy.seed.evidence_threshold`:  If this extraction relies on an initial set of "seed" limitations (perhaps from a previous stage), this defines the confidence needed for those seed limitations to be considered reliable.
    *   `policy.seed.max_research_depth`: If using "seed" limitations, this limits how far I should research related concepts to validate those seeds.
    *   `policy.seed.max_total_time`: The total time allowed for researching and validating "seed" limitations, if applicable.
4.  **Provide Structured Outputs:**
    *   **Structured Summary:**  Organize the identified limitations in a structured format (e.g., a list, table, or JSON). This summary should be easily understandable and processable by downstream modules.  The structure should include the specific limitation, a brief context, and evidence identifiers.
    *   **Confidence Score:** Assign a confidence score to each identified limitation, reflecting the reliability and strength of the supporting evidence.  Clearly indicate which evidence (e.g., specific sentences or paragraphs with identifiers) supports the confidence score.
    *   **Next-Step Recommendation:** Determine the next appropriate action:
        *   If enough limitations are found with sufficient confidence, recommend proceeding to the next stage of the process.
        *   If the evidence is weak, escalate for human review or further investigation.  The escalation should clearly outline the reasons for the uncertainty (e.g., lack of evidence, conflicting information).

**In essence, my task is to reliably identify and document limitations from the source content, providing a clear audit trail and actionable insights, all while respecting the defined policy constraints.**

To perform this task effectively, I will need:

*   **Access to the content source.**
*   **The specific values for the `policy.*` parameters.**
*   **A definition of the expected output structure (e.g., JSON schema).**
*   **The criteria for determining the confidence score.**
*   **Clear guidelines for escalation (e.g., under what conditions, to whom, and with what information).**

Without this information, my ability to execute this stage effectively is limited.