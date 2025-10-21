Okay, this is a good start for defining the primary stage of a Source Prioritizer. Let's break down this description and think about how we can flesh it out to be more actionable and specific.

**Strengths:**

*   **Clear Objectives:** The objectives are well-defined and focus on alignment, compliance, and policy adherence.
*   **Explicit Policy Context:**  Listing the relevant policies is crucial for ensuring the component behaves as expected.  This allows developers and operators to quickly understand the constraints.
*   **Defined Outputs:** The specified outputs provide a clear understanding of what's expected from this stage.

**Areas for Improvement & Expansion:**

*   **Intake & Scoping Definition:** What *exactly* constitutes "Intake & Scoping" in the context of source prioritization?  We need more detail here. Is it about receiving a request? Is it about analyzing the request to determine the type of information needed? Is it about identifying potential sources?
*   **Actions:** What specific actions are involved in achieving the objectives? The current description is high-level. We need to drill down into the *tasks* that the Source Prioritizer performs.
*   **Evidence Identification & Management:**  How is evidence identified? How is it stored and linked to findings and confidence scores?  We need to consider the data model for evidence.
*   **Confidence Score Calculation:**  The description mentions a confidence score, but not how it's calculated.  This is critical. What factors contribute to the score? How are they weighted?
*   **Next-Step Recommendation Logic:** Under what circumstances is a next-step recommendation generated versus an escalation flag? What are the possible next steps?  What criteria trigger escalation?
*   **Orchestration Policies:** How are the orchestration policies actually *respected*?  What mechanisms are in place to ensure compliance with `policy.latency_budget`, `policy.research_depth`, etc.?
*   **Error Handling/Edge Cases:** What happens if no sources are found that meet the `policy.evidence_threshold`? What happens if the `policy.latency_budget` is exceeded?
*   **Input:**  What is the expected input to this stage? Is it a query, a document, a request with specific requirements? The input format shapes the actions taken.
*   **Technology Considerations:** While not strictly part of the description, it's good to start thinking about the technology involved. Are we talking about using a search engine? A knowledge graph? API calls to specific databases?

**Proposed Revisions & Expansion:**

Here's a more detailed description, incorporating the suggestions above:

**# Source Prioritizer :: Source Prioritizer Primary**
Stage: Intake & Scoping

## Objectives
- Maintain evidence alignment and governance compliance.
- Respect orchestration policies while completing assigned actions.

## Policy Context
- policy.evidence_threshold (Minimum confidence level required for a source to be considered)
- policy.latency_budget (Maximum time allowed for this stage to complete)
- policy.research_depth (Maximum number of sources to explore)
- policy.seed.evidence_threshold (Minimum confidence level for seed sources)
- policy.seed.max_research_depth (Maximum number of seed sources to explore)
- policy.seed.max_total_time (Maximum time to spend on seed source exploration)

## Intake & Scoping Definition:
This stage receives a [Specify Input Format, e.g., `QueryRequest` object containing a search query, context information, and target domain].  It analyzes the request to determine:

*   The specific information requirements based on the query and context.
*   Potential source categories (e.g., academic papers, news articles, government reports).
*   Initial seed sources, if provided in the input or available in a pre-defined seed source list (subject to seed policies).

## Actions:
1.  **Request Parsing & Validation:** Parse the incoming `QueryRequest` and validate it against a defined schema.  Handle invalid requests by returning an error flag and logging the error.
2.  **Requirement Analysis:** Analyze the query to identify key entities, relationships, and the type of information being sought.
3.  **Seed Source Exploration (if applicable):**
    *   Retrieve seed sources based on query keywords and domain.
    *   Evaluate seed source relevance and confidence using [Define Relevance and Confidence Criteria].
    *   Limit seed source exploration to `policy.seed.max_research_depth` and `policy.seed.max_total_time`.
    *   Seed sources must meet `policy.seed.evidence_threshold`.
4.  **Source Category Selection:** Based on the requirement analysis, select relevant source categories.
5.  **Potential Source Identification:** Identify potential sources within the selected categories using [Specify Source Identification Method, e.g., search engine queries, API calls, knowledge graph traversal].  Limit the number of sources identified based on `policy.research_depth`.
6.  **Source Filtering (Preliminary):** Filter out irrelevant sources based on basic criteria (e.g., language, date range, domain).
7.  **Evidence Extraction (Limited):** Extract limited evidence snippets from the identified sources (e.g., titles, abstracts, snippets from search results).
8.  **Relevance & Confidence Scoring (Initial):** Calculate an initial relevance and confidence score for each potential source based on the extracted evidence.  [Define Initial Scoring Algorithm - e.g., keyword matching, semantic similarity].  Evidence is stored with a unique identifier.
9.  **Latency Monitoring:** Monitor the time elapsed during the stage and ensure it remains within the `policy.latency_budget`. If exceeded, truncate source exploration and proceed with available data.

## Evidence Management:
*   Each piece of evidence extracted from a source is assigned a unique identifier (e.g., UUID).
*   Evidence is stored in [Specify Evidence Storage Mechanism, e.g., a key-value store, a relational database].
*   The `Source` object contains links to the evidence identifiers used for its relevance and confidence scoring.

## Confidence Score Calculation:
The confidence score is calculated based on the following factors (with weights assigned):

*   **Relevance to Query:** [Specify Relevance Metric and Weight]
*   **Source Authority:** [Specify Source Authority Metric and Weight - e.g., PageRank, Citation Count]
*   **Evidence Strength:** [Specify Evidence Strength Metric and Weight - e.g., Keyword Density, Semantic Similarity]
*   **Seed Source Boost:** [Specify Boost Factor if the source is a Seed Source]

`Confidence Score = (Relevance * Weight_Relevance) + (Authority * Weight_Authority) + (EvidenceStrength * Weight_Evidence) + (SeedBoost)`

## Required Outputs
- Structured summary of findings: A list of potential sources, ranked by confidence score, with associated metadata (e.g., URL, title, source category).
- Confidence score with supporting evidence identifiers: Each source in the list should have its confidence score and a list of the identifiers of the evidence used to calculate that score.
- Next-step recommendation or escalation flag:
    *   **Next-Step Recommendation:** If the highest confidence score exceeds `policy.evidence_threshold`, recommend the next stage: [Specify Next Stage, e.g., Source Prioritizer - Secondary Stage - Deep Dive].  Pass the ranked list of sources to the next stage.
    *   **Escalation Flag:** If no sources meet `policy.evidence_threshold` *and* the `policy.latency_budget` has been reached, raise an escalation flag indicating insufficient information and log the details of the search.  This should trigger a human review.
    *   **Re-Prioritization Recommendation**:  If no sources meet `policy.evidence_threshold` *but* the `policy.latency_budget` has *not* been reached, recommend a re-prioritization of sources. This could involve widening the search criteria, exploring alternative source categories, or adjusting the scoring weights.

**Error Handling:**
*   **`policy.latency_budget` Exceeded:**  Truncate source exploration and proceed with the sources identified so far. Log a warning message.
*   **No Sources Found:**  If no sources are found after initial exploration, widen the search criteria based on pre-defined rules.
*   **API Rate Limits Reached:** Implement exponential backoff and retry mechanisms for API calls.
*   **Source Unavailable:**  Log the unavailable source and continue processing other sources.

This expanded description provides a more concrete understanding of what the Source Prioritizer (Primary Stage) actually *does*.  Remember to fill in the bracketed sections with specific details relevant to your implementation.  Further refinement may be necessary based on the specific technologies and data sources you are using.