Okay, I understand. As the Hardware Landscape Mapper Primary operating within the Quantum Discovery stage, my primary focus is to discover and map relevant hardware technologies. My actions are heavily guided by the defined policies, aiming to maintain evidence alignment, governance compliance, and adherence to orchestration policies.

Let's break down the objectives and required outputs further:

**Objectives Deep Dive:**

*   **Maintain Evidence Alignment and Governance Compliance:**  This is paramount.  Every piece of information I gather, and every decision I make, must be traceable back to its source and demonstrably compliant with relevant governance guidelines (as implicitly defined in the "Policy Context").  This means meticulous record-keeping of:
    *   Data sources: Websites, publications, databases, APIs, etc.
    *   Timestamps: When data was accessed.
    *   Methods: How data was obtained (e.g., search queries, API calls).
    *   Transformations: Any data cleaning or processing steps.
    *   Justification: Reasoning for including or excluding specific data points based on the policy thresholds.

*   **Respect Orchestration Policies While Completing Assigned Actions:** I am an actor within a larger orchestrated process.  I must operate within the defined constraints set by the orchestrator. This includes:
    *   Time limitations:  Adhering to the `policy.latency_budget` and indirectly to `policy.seed.max_total_time`.
    *   Resource allocation:  Efficient use of computational resources.
    *   Prioritization: Focusing on tasks that align with the overall Quantum Discovery strategy.
    *   Dependency management: Understanding dependencies on other components or data sources.

**Required Outputs Deep Dive:**

*   **Structured Summary of Findings:** This is the core deliverable. It needs to be in a format that is:
    *   Parsable: Easily consumed by downstream processes or other agents.  Likely involves using a predefined schema (e.g., JSON, YAML, a knowledge graph format).
    *   Comprehensive: Captures the key hardware technologies identified within the scope of the Quantum Discovery stage.
    *   Concise: Avoids unnecessary detail, focusing on the most relevant information.
    *   Well-organized:  Uses a clear and logical structure to present the findings (e.g., categorized by type, function, vendor, etc.).

    The summary should include:
    *   Names and descriptions of hardware technologies.
    *   Key characteristics and specifications.
    *   Potential applications within the context of quantum computing.
    *   Relevant vendors and research institutions.
    *   Potential limitations or challenges.

*   **Confidence Score with Supporting Evidence Identifiers:** This is critical for assessing the reliability and trustworthiness of the findings.
    *   Confidence Score:  A numerical value (e.g., 0-1, 0-100%) that represents the degree of certainty I have in the accuracy and completeness of the findings.  This score should be calculated based on:
        *   Evidence Strength: The quality and reliability of the evidence sources (e.g., peer-reviewed publications are stronger evidence than blog posts).
        *   Evidence Consistency: The level of agreement among different sources of evidence.
        *   Evidence Coverage: The extent to which the evidence supports the claims being made.
    *   Evidence Identifiers: Unique identifiers that allow users to easily locate and examine the evidence supporting the findings.  These could be:
        *   URLs of web pages.
        *   DOIs of publications.
        *   IDs of database entries.
        *   Internal IDs referring to data stored within my own system.

*   **Next-Step Recommendation or Escalation Flag:**  This output guides subsequent actions in the Quantum Discovery process.
    *   Next-Step Recommendation: Suggestions for further investigation or analysis, based on the current findings.  Examples:
        *   "Investigate Vendor X's product line in more detail."
        *   "Explore the use of Technology Y in specific quantum algorithms."
        *   "Seek expert opinion on the feasibility of using Technology Z in a specific quantum environment."
    *   Escalation Flag: Indicates that the findings warrant immediate attention or intervention from human experts.  This might be triggered by:
        *   High uncertainty in the findings.
        *   Conflicting evidence.
        *   Potential risks or opportunities that require further evaluation.
        *   Exceeding the `policy.evidence_threshold`  (if I detect that reaching it isn't possible within allocated time).

**Policy Context Interpretation:**

*   **policy.evidence_threshold:** The minimum acceptable level of supporting evidence required before considering a finding to be valid. Impacts the confidence score calculation. Higher threshold = higher confidence needed.
*   **policy.latency_budget:** The maximum allowable time to complete a single task or stage of the discovery process.  Forces me to prioritize and make trade-offs between thoroughness and speed.
*   **policy.research_depth:** The extent to which I am expected to investigate a particular topic or technology. Limits the amount of time spent drilling down into specific details.  Higher depth means more granular investigation.
*   **policy.seed.evidence_threshold:** The evidence threshold specifically for information derived from initial "seed" data points.  May have a lower threshold to allow for broader exploration initially, compared to later stages.
*   **policy.seed.max_research_depth:** The maximum research depth permitted for exploring information related to initial "seed" data points. Controls the initial breadth and depth of the search.
*   **policy.seed.max_total_time:** The maximum time allocated for exploring information related to initial "seed" data points. Ensures that initial exploration doesn't consume the entire budget.

**In Summary:**

My role is to efficiently and reliably identify and map hardware technologies relevant to Quantum Discovery, operating within the constraints imposed by the defined policies. I must meticulously document my evidence and provide confidence scores to ensure the trustworthiness of my findings, along with clear recommendations for next steps or escalation when necessary.

Now, I'm ready to start. What are my initial tasks or data seeds?