Okay, I understand. I'm ready to start the Literature Search stage. My primary goal is to gather relevant information while adhering to the defined policies and objectives. I will be focusing on delivering the required outputs: a structured summary, a confidence score with supporting evidence, and a recommendation for the next step.

Here's a breakdown of how I will approach this, keeping the policies in mind:

**1. Understanding the Search Scope:**

*   I need more context on the specific topic of the literature search. I require a prompt to understand what I should be searching for. **(I need more information to proceed. Please provide the search topic or question.)**

**2. Search Strategy Based on Policy:**

*   **`policy.research_depth`:** This determines how many levels of abstraction I should pursue in my search. A low `research_depth` will limit me to directly relevant papers and sources. A high `research_depth` will allow me to explore background information and related concepts.
*   **`policy.evidence_threshold`:** This determines the quality and quantity of evidence I need to find before drawing conclusions. A high threshold requires strong evidence from multiple credible sources.
*   **`policy.latency_budget`:**  I will prioritize efficient search methods to stay within the allocated time. I will avoid exhaustive, low-yield search strategies.
*   **`policy.seed.evidence_threshold`, `policy.seed.max_research_depth`, `policy.seed.max_total_time`:** If the search is seeded with initial resources, I will use these policies to guide the exploration of those resources, prioritizing quick validation and limiting the scope of secondary research if time is a constraint.

**3. Search Execution (Once I have the search topic):**

*   **Initial Search:** I will use a combination of search engines (e.g., Google Scholar, PubMed, arXiv) and potentially specialized databases relevant to the topic.
*   **Keyword Iteration:** I will refine search terms based on initial results to improve precision and recall.
*   **Evidence Gathering:** I will extract key information from identified sources, including abstracts, methodologies, results, and conclusions.  I will focus on information that supports or contradicts potential hypotheses related to the search topic.
*   **Source Evaluation:** I will assess the credibility of sources based on factors such as publication venue, author expertise, and citations.  I will prioritize peer-reviewed articles and reputable organizations.
*   **Evidence Tracking:** I will maintain a clear record of all sources used, including URLs and key excerpts. This will form the basis of the supporting evidence identifiers.

**4. Output Generation:**

*   **Structured Summary:** The summary will present the main findings in a clear and concise manner, organized by key themes or arguments. It will highlight areas of agreement and disagreement among the sources.
*   **Confidence Score:** This will reflect my overall confidence in the validity of the findings, based on the quality and consistency of the evidence. A higher score indicates stronger evidence. I will base the score on the `policy.evidence_threshold` to ensure I meet the quality standard. I will document the supporting evidence used to calculate the score.
*   **Supporting Evidence Identifiers:** I will provide a list of specific sources and relevant passages that support the claims made in the summary and contribute to the confidence score.
*   **Next-Step Recommendation or Escalation Flag:**
    *   If the evidence is conclusive and aligns with the initial goals, I will recommend the next logical step in the process (e.g., moving to the next stage, implementing a solution).
    *   If the evidence is inconclusive, contradictory, or raises new questions, I will flag the need for escalation or further investigation. I will explain the reasons for the flag. This could include exceeding `policy.research_depth` without sufficient results, or identifying a critical gap in the information landscape.

**Governance Compliance:**

Throughout the process, I will ensure full traceability of all data sources, actions, and decisions, to support auditability and compliance with relevant regulations.

**In summary, I am ready to begin the literature search once I have a clear understanding of the search topic. Please provide the necessary information so I can start working towards the objectives while adhering to the defined policies.**