Okay, I understand. This document describes the "Key Concept Extractor Primary" stage within a larger system. Here's a breakdown of what it means and how I will operate within this framework:

**Understanding the Context**

*   **Goal:** Extract key concepts from input content.
*   **Stage:** "Content Extraction" - This implies this module is early in a larger pipeline, focusing on extracting relevant information.
*   **Constraints:** Operated within specific boundaries related to evidence quality, latency, and research effort, as governed by defined policies.
*   **Governance and Alignment:** Operations must maintain the traceability of evidence and adherence to governance standards.

**Key Aspects and Responsibilities**

1.  **Evidence Alignment and Governance Compliance:**
    *   All extracted key concepts *must* be supported by evidence from the source content.
    *   The origin of the evidence needs to be clearly tracked (e.g., identifier of the source document and specific passage).
    *   This traceability is crucial for auditing, verification, and building trust in the results.
2.  **Orchestration Policy Respect:**
    *   The module operates as part of a larger orchestrated system.
    *   It must adhere to the orchestration policies, meaning:
        *   **Latency Budget (policy.latency_budget):**  Must complete its tasks within a defined time limit.
        *   **Evidence Threshold (policy.evidence_threshold):**  A minimum level of supporting evidence is required for each extracted concept. This might involve the number of sources, the quality of the sources, or the strength of the evidence itself.
        *   **Research Depth (policy.research_depth):**  A maximum level of inquiry into supporting information. It dictates how deeply to investigate potential key concepts.
        *   **Seed Policies (policy.seed.evidence_threshold, policy.seed.max_research_depth, policy.seed.max_total_time):**  If the process starts with initial "seed" concepts, there are separate (and potentially stricter) policies governing how those seeds are explored and validated. These policies likely ensure early concepts are grounded in strong evidence and don't consume excessive resources.

3.  **Required Outputs:**
    *   **Structured Summary of Findings:** A clear and organized presentation of the extracted key concepts.  This could be in various formats (e.g., lists, tables, graphs, summaries) depending on the requirements of the overall system.
    *   **Confidence Score with Supporting Evidence Identifiers:**
        *   Each extracted concept must be associated with a confidence score, reflecting the strength of the evidence supporting it.
        *   The identifiers of the evidence used to determine the confidence score *must* be provided. This allows for verification and further analysis.
    *   **Next-Step Recommendation or Escalation Flag:**
        *   The module must determine the appropriate next action.
        *   This could include:
            *   **Recommendation:**  Passing the extracted concepts to the next stage in the pipeline. This is the normal, expected outcome.
            *   **Escalation Flag:**  If the module encounters issues (e.g., insufficient evidence, ambiguous concepts, policy violations), it must signal that further investigation or intervention is needed.

**How I Will Operate**

Given this context, when presented with content, I will:

1.  **Identify Potential Key Concepts:** Use NLP techniques (keyword extraction, topic modeling, semantic analysis, etc.) to identify candidate concepts within the content.
2.  **Gather Supporting Evidence:** Search the content for sentences, phrases, or passages that support each candidate concept.  The depth of this search will be limited by `policy.research_depth` and `policy.seed.max_research_depth` if applicable.
3.  **Assess Evidence Strength:** Evaluate the quality and quantity of the supporting evidence. This will involve considering factors like:
    *   Relevance of the evidence to the concept.
    *   Frequency of the concept within the content.
    *   Context in which the concept appears.
    *   Credibility of the source (if applicable).
4.  **Calculate Confidence Score:** Assign a confidence score to each extracted concept based on the strength of the supporting evidence.  This score must meet or exceed `policy.evidence_threshold` and `policy.seed.evidence_threshold` if applicable.
5.  **Generate Structured Summary:** Organize the extracted concepts, confidence scores, and evidence identifiers into a clear and structured format.
6.  **Determine Next Step:**
    *   If the confidence score meets the required threshold and no other issues are encountered, recommend passing the concepts to the next stage.
    *   If the confidence score is below the threshold, or if other problems arise (e.g., ambiguity, policy violations, time limit exceeded), flag the need for escalation.
7.  **Log and Track:**  Maintain a record of all actions taken, evidence gathered, and decisions made.  This is essential for governance and auditability.

**Example Scenario:**

Imagine the content is a news article about "Climate Change."

1.  **Identification:** I might identify candidate concepts like "global warming," "greenhouse gases," "renewable energy," and "sea-level rise."
2.  **Evidence Gathering:** I'd search the article for passages discussing these concepts.
3.  **Assessment:**  I'd evaluate how often "global warming" is mentioned, the context in which it's discussed (e.g., with negative consequences), and whether the article cites scientific sources supporting its link to climate change.
4.  **Confidence Score:** If the evidence is strong and consistent, I'd assign a high confidence score to "global warming" as a key concept.  A concept with weaker evidence might receive a lower score.
5.  **Output:** I'd output a structured summary:

```json
[
    {
        "concept": "Global Warming",
        "confidence_score": 0.95,
        "evidence_identifiers": ["article:paragraph_3", "article:paragraph_7", "article:quote_scientist_1"]
    },
    {
        "concept": "Renewable Energy",
        "confidence_score": 0.70,
        "evidence_identifiers": ["article:paragraph_5", "article:mention_solar_panels"]
    }
]
```

6.  **Next Step:**  Assuming both concepts meet the `policy.evidence_threshold`, I would recommend passing them to the next stage.

**In Summary:**

My role as the "Key Concept Extractor Primary" is to efficiently and reliably extract key concepts from content, while rigorously adhering to predefined policies and maintaining clear evidence traceability. I will focus on delivering accurate, well-supported summaries of findings with appropriate confidence scores and actionable next-step recommendations.