Okay, this outlines the purpose and constraints for a `Draft Writer`. Let's break down what this means and how to approach it in practice:

**Understanding the Role: Draft Writer**

The `Draft Writer` isn't just about writing; it's about *structured summarization and assessment* based on evidence, under specific constraints.  Think of it as a crucial step in a larger pipeline where information needs to be distilled and evaluated. The "Delivery & QA" stage suggests this draft is close to being finalized or used in a downstream application.

**Key Responsibilities:**

*   **Evidence-Based Summarization:**  Creating concise and organized summaries from provided (or researched) evidence.
*   **Confidence Assessment:**  Evaluating the reliability and strength of the summary and assigning a confidence score.
*   **Compliance and Governance:**  Adhering to predefined policies related to evidence quality, research depth, and timing.
*   **Orchestration Awareness:**  Working within the overall workflow and respecting its dependencies (e.g., not exceeding time budgets if another task depends on this).
*   **Recommendation and Escalation:**  Knowing when to proceed with the next step based on confidence levels, or when to escalate issues that require human intervention (e.g., conflicting evidence, insufficient data).

**Detailed Breakdown of Elements:**

*   **Stage: Delivery & QA:** This emphasizes the need for high quality and accuracy. The draft is likely being reviewed or used in a downstream process.

*   **Objectives:**
    *   **Maintain evidence alignment and governance compliance:** This is paramount. Every statement in the summary must be traceable back to specific evidence.  Policy requirements must be met.
    *   **Respect orchestration policies while completing assigned actions:**  The Writer must be a good "citizen" within the larger system.  Time limits, resource usage, and data dependencies are important.

*   **Policy Context:**  These policies are the *constraints* within which the Writer operates. Let's explore each one:
    *   **`policy.evidence_threshold`:**  The minimum quality or amount of evidence required to support a statement. This could be measured in terms of source credibility, sample size (if data-driven), etc.  If the evidence doesn't meet this threshold, the summary should reflect that low confidence.
    *   **`policy.latency_budget`:**  The maximum time allowed to complete the task. This impacts how much time can be spent on research and refinement.
    *   **`policy.research_depth`:**  The extent to which the Writer should delve into researching the topic.  A low depth might only involve summarizing provided documents.  A high depth might require finding external sources.
    *   **`policy.seed.evidence_threshold`:** This relates to the initial seed data (the starting point). It sets the minimum bar for the evidence used as a base.
    *   **`policy.seed.max_research_depth`:** Like `policy.research_depth`, but specifically applied to the initial seed information.  Limits how far the Writer should go in verifying the starting point.
    *   **`policy.seed.max_total_time`:**  Similar to `policy.latency_budget`, but focused on the time spent processing the initial seed data.

*   **Required Outputs:**
    *   **Structured summary of findings:**  A well-organized summary, potentially using a specific format (e.g., bullet points, numbered lists, tables).  Crucially, this summary *isn't just a paraphrase*. It's a synthesized view of the evidence, highlighting key insights and contradictions.
    *   **Confidence score with supporting evidence identifiers:**  A numerical or qualitative score representing the Writer's confidence in the summary's accuracy and completeness.  Each statement should be linked to the specific evidence used to support it (e.g., document ID, paragraph number, URL).
    *   **Next-step recommendation or escalation flag:**  A clear indication of what should happen next.  This might be:
        *   "Proceed to review." (High confidence, all policies met)
        *   "Further research required on X aspect." (Low confidence due to insufficient evidence)
        *   "Evidence conflicts on Y; escalate to human review." (Contradictory information that needs expert judgment)

**How to Approach Draft Writing (in practice):**

1.  **Understand the Input:** Determine what type of input this writer is receiving and what form it takes. Is it a document, set of documents, or data stream?  Is there a specific question or task that needs to be addressed?

2.  **Policy Enforcement:**
    *   **Evidence Threshold:** Establish a method to evaluate the evidence. What are the criteria to assess its credibility, relevance, and quality? Consider a scoring system or rubric.
    *   **Latency Budget:**  Use a timer to track progress and ensure the task stays within the allowed timeframe. Prioritize tasks based on importance.
    *   **Research Depth:**  Develop a research strategy that aligns with the allowed depth. Avoid rabbit holes and unnecessary exploration.
    *   **Seed Policy:** Ensure the starting information meets the seed requirements. If not, flag for manual review or augment as needed.

3.  **Summarization:**
    *   Identify key claims, arguments, or data points.
    *   Synthesize the information into a clear and concise summary.
    *   Maintain a strict audit trail linking each statement to its supporting evidence.

4.  **Confidence Scoring:**
    *   Develop a scoring system based on factors like:
        *   Evidence quality (based on evidence threshold)
        *   Coverage (how much of the topic is covered by the available evidence)
        *   Consistency (absence of contradictions)
        *   Subjectivity (how much interpretation was required)
    *   Assign a confidence score to each statement in the summary.
    *   Calculate an overall confidence score for the entire summary.

5.  **Next-Step Recommendation:**
    *   Based on the confidence score and policy compliance, determine the appropriate next step.
    *   Provide a clear and actionable recommendation.

**Example Scenario:**

Let's say the task is to summarize news articles about a specific company's new product launch, and the `policy.evidence_threshold` requires at least two independent sources confirming key features. The `latency_budget` is 30 minutes.

*   **Input:** A list of URLs to news articles.
*   **Action:**
    *   Fetch and parse the articles.
    *   Identify claims about the product's features, price, and availability.
    *   For each claim, find at least two independent sources (meet the `evidence_threshold`).
    *   If a claim is only supported by the company's press release, flag it as "low confidence."
    *   Summarize the confirmed features, price, and availability.
    *   Assign a confidence score based on the number of independently confirmed claims.
    *   If key information is missing (e.g., launch date), recommend further research.  If there are conflicting reports about the price, escalate for human review.

**In Summary:**

The `Draft Writer` is a critical role in a system that relies on accurate, evidence-based information. By following the policies, providing clear summaries, and assessing confidence levels, the Writer ensures that the information used in downstream processes is reliable and trustworthy. This requires a strong understanding of the policy constraints, a structured approach to summarization, and a systematic way to evaluate the confidence in the generated summary.