Okay, I understand. As Scholar Agent Primary, operating within the Literature Search stage, my primary focus is to conduct a search for relevant literature, extract key information, and provide a structured summary of my findings. I must adhere to the provided policies while executing this task.

**Here's a breakdown of how I will address each requirement:**

**1. Maintaining Evidence Alignment and Governance Compliance:**

*   **Tracking Evidence:**  I will meticulously record the source of each piece of information I extract (e.g., journal article title, DOI, abstract snippet). This will be stored alongside the extracted information, creating a clear provenance trail.
*   **Compliance:**  I will ensure that my search queries and information extraction methods are consistent with relevant governance policies (if any are provided, otherwise I will adhere to standard academic practices).

**2. Respecting Orchestration Policies:**

*   **`policy.evidence_threshold`:**  This likely dictates the minimum level of confidence required in my findings. I will aim to exceed this threshold. My confidence score (explained below) will be influenced by factors like source credibility, the consistency of findings across multiple sources, and the quality of the research methodology.
*   **`policy.latency_budget`:**  This specifies the maximum time I have to complete this literature search. I will prioritize my efforts to ensure I deliver results within this timeframe. I will use efficient search strategies and focus on the most promising leads first.
*   **`policy.research_depth`:**  This indicates how thoroughly I should search. A deeper search will involve exploring more sources, including less obvious ones. I will adjust my search strategy based on this policy.
*   **`policy.seed.evidence_threshold`:**  This likely refers to the evidence threshold required for the initial "seed" papers or concepts that are used to initiate the search. I will make sure that the initial concepts are based on reliable, well-established sources and clearly indicate where they come from.
*   **`policy.seed.max_research_depth`:**  This limits the depth to which I can research the initial "seed" papers.
*   **`policy.seed.max_total_time`:** This restricts the total time that can be spent researching the initial "seed" papers.

**3. Required Outputs:**

*   **Structured Summary of Findings:**  I will present the key findings in a structured format. This might include:
    *   **Introduction:** Briefly outlining the topic and the purpose of the literature search.
    *   **Key Themes/Concepts:** Identifying and summarizing the major themes and concepts related to the research topic.
    *   **Supporting Evidence:** Providing specific evidence from the literature to support each theme/concept (including citations or identifiers).
    *   **Gaps in the Literature:** Identifying any areas where further research is needed.
    *   **Conclusion:** Summarizing the main findings and their implications.

*   **Confidence Score with Supporting Evidence Identifiers:**  I will provide a confidence score (e.g., on a scale of 1-100) reflecting my overall confidence in the accuracy and completeness of my findings. This score will be based on the following factors:
    *   **Source Credibility:**  Are the sources peer-reviewed journals, reputable institutions, etc.?
    *   **Consistency of Findings:**  Do multiple sources agree on the key findings?
    *   **Methodological Rigor:**  Was the research conducted using sound scientific methods?
    *   **Sample Size:** Is the size of the studies sufficient?
    *   **Potential Biases:** What biases might be present in the sources?

    Along with the confidence score, I will provide a list of evidence identifiers (e.g., DOIs, URLs, paper titles) that support the confidence score calculation. For example:

    *   **Confidence Score:** 85/100
    *   **Supporting Evidence Identifiers:**
        *   DOI: 10.1000/abcd123 (Peer-reviewed journal, high methodological rigor, consistent findings with other sources)
        *   DOI: 10.1000/efgh456 (Conference proceeding, moderate methodological rigor, supports findings from DOI 10.1000/abcd123)

*   **Next-Step Recommendation or Escalation Flag:**  Based on my findings, I will recommend a next step. This could include:
    *   **Further Research:** Suggesting specific areas for further investigation.
    *   **Data Analysis:** Recommending that the collected data be analyzed in a certain way.
    *   **Synthesis:** Recommending that the findings be synthesized into a report or presentation.
    *   **Escalation Flag:** If I encounter any significant issues (e.g., conflicting information, lack of available data, policy violations), I will raise an escalation flag to alert a human overseer.  I will include a clear explanation of the issue and the reason for the flag.

**In summary, I will perform a literature search, meticulously track my sources, adhere to the specified policies, and deliver a structured summary of my findings with a confidence score, supporting evidence identifiers, and a recommendation for the next step.**

Before proceeding, I need the following information to initialize the literature search:

1.  **The specific topic of the literature search.**
2.  **The search query(ies) to use initially.**
3.  **The policy configurations (e.g., `policy.evidence_threshold`, `policy.latency_budget`, `policy.research_depth`, `policy.seed.evidence_threshold`, `policy.seed.max_research_depth`, `policy.seed.max_total_time`).**
4.  **Preferred sources (e.g., specific databases, journals).**

Once I have this information, I can begin the search.