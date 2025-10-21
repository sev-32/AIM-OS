Okay, this is a good starting point for defining the "Contradiction Detector Primary" stage within a larger orchestration.  Let's break down and expand upon each section to make it more actionable and complete.  I'll add details that are consistent with the objectives, policy context, and required outputs.

**# Contradiction Detector :: Contradiction Detector Primary**
**Stage: Analysis**

**## Objectives**

*   **Maintain evidence alignment and governance compliance:** Ensure that all evidence considered is relevant to the claims being assessed for contradiction, adheres to data privacy regulations, and is traceable back to its source.  This also includes adhering to established procedures for handling sensitive or classified information, if applicable.
*   **Respect orchestration policies while completing assigned actions:**  Operate within the defined constraints of the orchestration, including time limits (latency budget), depth of research, and evidence thresholds.  Prioritize actions that contribute most effectively to the overall goals of the orchestration.
*   **Detect and flag contradictions with high accuracy:** Identify and report contradictions between statements, claims, or pieces of evidence based on a defined logic and understanding of the subject matter. The goal is to minimize both false positives (flagging non-contradictory information) and false negatives (missing genuine contradictions).
*   **Provide contextual understanding of the contradiction:**  Beyond simply flagging a contradiction, provide information about *why* the contradiction exists, including the sources of the conflicting information, the specific elements that contradict each other, and potential explanations for the discrepancy.
*   **Generate actionable recommendations:**  Based on the detected contradictions, provide clear recommendations for next steps, such as further investigation, request for clarification, escalation to a human reviewer, or rejection of a claim.

**## Policy Context**

*   `policy.evidence_threshold`: (e.g., 0.7) - Minimum confidence score required for a piece of evidence to be considered valid. Evidence below this threshold should be discarded or flagged for further review.
*   `policy.latency_budget`: (e.g., 30 seconds) - Maximum time allowed for this stage to complete its analysis.  This influences the scope of research and the complexity of the analysis that can be performed.
*   `policy.research_depth`: (e.g., 3) -  Specifies the maximum number of steps or levels of recursion to follow when researching supporting or refuting evidence (e.g., 3 levels of linked articles).
*   `policy.seed.evidence_threshold`: (e.g., 0.9) - Minimum confidence score for the initial seed evidence that triggers this analysis. This ensures a strong starting point.
*   `policy.seed.max_research_depth`: (e.g., 5) - Maximum research depth permitted when evaluating the seed evidence itself.  This allows for validating the starting point but limits runaway exploration.
*   `policy.seed.max_total_time`: (e.g., 60 seconds) - Maximum time allowed for initially validating the seed evidence.  This prevents the process from getting stuck on a weak or problematic starting point.

**## Inputs**

*   **`claim`:** The central statement or assertion being evaluated for contradictions (e.g., "The Earth is flat").
*   **`evidence_set`:** A collection of evidence documents, facts, and statements that are relevant to the `claim`. This can be a structured dataset, a set of text documents, a graph of relationships, or other forms of data. Each piece of evidence should have a unique identifier.
*   **`evidence_metadata`:** (Optional) Metadata associated with each piece of evidence, such as its source, creation date, author, and confidence score.
*   **`context`:** (Optional)  Any relevant contextual information that might influence the interpretation of the claim or evidence (e.g., the domain or subject area, the intended audience).

**## Process**

1.  **Evidence Preprocessing:**
    *   Filter the `evidence_set` based on `policy.evidence_threshold`. Discard evidence with a confidence score below this threshold.
    *   Normalize and standardize the evidence data (e.g., convert text to lowercase, remove punctuation, apply stemming or lemmatization).  This can improve the accuracy of comparison algorithms.
    *   Index the evidence data to enable efficient searching and retrieval.

2.  **Contradiction Detection:**
    *   **Semantic Analysis:** Use Natural Language Processing (NLP) techniques to understand the meaning of the `claim` and each piece of `evidence`.  This may involve:
        *   Named entity recognition (NER)
        *   Part-of-speech (POS) tagging
        *   Dependency parsing
        *   Semantic role labeling
    *   **Logical Inference:** Apply logical rules and reasoning to infer the relationships between the `claim` and the `evidence`.  Determine whether the evidence supports, contradicts, or is neutral towards the claim.
    *   **Conflict Resolution:** If multiple pieces of evidence contradict each other, attempt to resolve the conflict by considering factors such as the source credibility, the evidence recency, and the contextual information.
    *   **Timeboxing:** Monitor the elapsed time and ensure that the process stays within the `policy.latency_budget`.  Prioritize the most promising avenues of investigation.
    *   **Research Depth:** Respect `policy.research_depth` to avoid endlessly digging for evidence.

3.  **Seed Evidence Validation:**
    *   If the initial `evidence_set` is derived from a single "seed" piece of evidence, validate the seed evidence against `policy.seed.evidence_threshold`, `policy.seed.max_research_depth`, and `policy.seed.max_total_time`.  If the seed evidence fails these checks, the entire process may be aborted or redirected.

**## Required Outputs**

*   **Structured Summary of Findings:**
    *   A concise summary of the contradictions detected, including:
        *   The `claim` being evaluated.
        *   A list of contradicting pieces of evidence, identified by their unique identifiers.
        *   For each contradiction, a brief explanation of *why* the contradiction exists.
        *   The confidence level of the contradiction detection.
        *   List of supporting evidence (evidence that supports or refutes the contradiction).
*   **Confidence Score with Supporting Evidence Identifiers:**
    *   A numerical confidence score (e.g., 0.0-1.0) representing the overall confidence in the detected contradictions.
    *   For each contradicting piece of evidence, a list of identifiers for the evidence that supports the conclusion of contradiction.  This provides traceability and allows for further investigation.
*   **Next-Step Recommendation or Escalation Flag:**
    *   A clear recommendation for the next step in the orchestration, such as:
        *   `INVESTIGATE`:  Further investigation is needed to resolve the contradictions. This might involve gathering more evidence, requesting clarification, or consulting with subject matter experts.
        *   `ESCALATE`: The contradictions are complex or ambiguous, and require human review.
        *   `REJECT`: The contradictions are strong enough to warrant rejecting the claim.
        *   `ACCEPT`: No contradictions found. Further analysis may be needed.
    *   An escalation flag (e.g., a boolean value) indicating whether the case should be escalated to a human reviewer.  This flag should be set based on predefined criteria, such as the complexity of the contradictions, the sensitivity of the information involved, or the lack of sufficient evidence to make a definitive determination.

**## Error Handling and Logging**

*   Implement robust error handling to gracefully handle unexpected errors or exceptions during the analysis.
*   Log all significant events and decisions, including the evidence considered, the contradictions detected, the confidence scores, and the next-step recommendations. This is essential for auditing and debugging.

**Example Output (JSON):**

```json
{
  "claim": "The Earth is flat.",
  "contradictions": [
    {
      "evidence_id": "evidence_123",
      "explanation": "Evidence_123 states that the Earth is a sphere based on satellite imagery, which contradicts the claim that the Earth is flat.",
      "confidence": 0.95,
      "supporting_evidence_ids": ["evidence_456", "evidence_789"]
    }
  ],
  "overall_confidence": 0.90,
  "recommendation": "REJECT",
  "escalate": false,
  "metadata":{
    "policy_evidence_threshold_met": true,
    "within_latency_budget":true,
    "research_depth_achieved":3
  }
}
```

**Key Considerations:**

*   **Domain Expertise:**  The accuracy of the contradiction detection will depend on the system's understanding of the relevant domain. Consider using domain-specific knowledge graphs or ontologies to improve the accuracy of the analysis.
*   **Ambiguity:**  Natural language is often ambiguous. The system should be able to handle ambiguity by considering multiple interpretations of the claim and evidence.
*   **Scalability:**  The system should be able to handle large volumes of evidence efficiently.
*   **Explainability:**  It's important for the system to be able to explain *why* it detected a contradiction. This will help users understand the system's reasoning and build trust in its results.
*   **Regular Evaluation:** Continuously evaluate the system's performance and make adjustments as needed to improve its accuracy and effectiveness.

This expanded definition provides a more comprehensive and actionable description of the "Contradiction Detector Primary" stage.  It includes details on inputs, process steps, outputs, error handling, and key considerations, all aligned with the initial objectives and policy context.  Remember to tailor the specific details to your particular use case and environment.