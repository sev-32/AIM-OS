Okay, I understand my role as the Fact Checker Primary in the Validation stage. My primary objective is to meticulously examine claims, ensuring they are supported by evidence, compliant with governance policies, and aligned with orchestration policies.  I must be mindful of the various policy constraints outlined, including thresholds for evidence strength, acceptable latency, research depth limitations, and specific restrictions on seed analysis.

Here's a breakdown of my responsibilities and how I will approach them:

**1. Evidence Alignment and Governance Compliance:**

*   **Maintain Evidence Alignment:** I will meticulously compare the claim being fact-checked with the evidence provided. This involves verifying that the evidence directly supports the claim, doesn't contradict it, and is appropriately cited.
*   **Governance Compliance:** I will adhere to all specified governance policies. This includes:
    *   **`policy.evidence_threshold`:**  I will ensure that the evidence supporting the claim meets the minimum required level of strength and quality as defined by this policy.  Weaker evidence will lead to lower confidence scores and potentially escalation.
    *   **`policy.latency_budget`:**  I must perform my fact-checking tasks within the allocated time. This requires efficient use of resources and prioritization of tasks.
    *   **`policy.research_depth`:** I will limit my investigation to the defined depth of research. I will stop searching for evidence when this limit is reached, even if more information might be available.
    *   **`policy.seed.evidence_threshold`:**  If this fact-checking task originates from a "seed" claim, I will adhere to the stricter evidence threshold defined specifically for seeds. This implies a higher standard for initial claim validation.
    *   **`policy.seed.max_research_depth`:**  Similarly, if dealing with a seed claim, I will respect the maximum research depth specific to seeds.
    *   **`policy.seed.max_total_time`:**  If the fact-checking stems from a seed claim, I must stay within the allotted time limit for that seed.

**2. Respect Orchestration Policies:**

*   I will follow the instructions provided by the orchestration system, including the specific claim to be fact-checked, the available evidence, and any relevant context. I will avoid deviating from the established workflow without explicit authorization.

**3. Required Outputs:**

*   **Structured Summary of Findings:** I will provide a clear and concise summary of my analysis. This will include:
    *   The claim being fact-checked.
    *   A summary of the supporting and/or contradictory evidence.
    *   An assessment of the evidence's credibility and relevance.
    *   A final judgment on the claim's accuracy (e.g., True, False, Partially True, Unsubstantiated).
*   **Confidence Score with Supporting Evidence Identifiers:**  I will assign a confidence score reflecting the strength of the evidence supporting my judgment. This score will be linked to specific evidence identifiers, allowing for traceability and verification.  The score will consider factors such as the source's reliability, the consistency of the evidence, and the potential for bias.
*   **Next-Step Recommendation or Escalation Flag:**  I will recommend the next course of action. This might include:
    *   **Continuing the fact-checking process with additional steps (e.g., deeper research, seeking expert opinion).** This would be appropriate if the evidence is inconclusive or conflicting.
    *   **Marking the claim as definitively fact-checked.** This would be appropriate if the evidence is strong and conclusive.
    *   **Escalating the claim to a higher authority.** This would be necessary if the claim involves sensitive topics, requires specialized expertise, or exceeds my designated authority level.

**Example Scenario:**

Let's say I am tasked with fact-checking the claim: "The Earth is flat."  I am provided with several links as evidence, including articles from reputable scientific journals, videos of satellite imagery, and blog posts from individuals claiming the Earth is flat.

Here's how I would approach the task:

1.  **Review the evidence:** I would examine each piece of evidence, focusing on its source, methodology (if applicable), and relevance to the claim.  The scientific articles and satellite imagery would likely be considered highly credible, while the blog posts would be scrutinized for bias and lack of scientific rigor.

2.  **Compare the evidence to the claim:** I would assess whether the evidence supports or contradicts the claim. The scientific evidence overwhelmingly contradicts the claim that the Earth is flat.

3.  **Assign a confidence score:** Based on the strength and consistency of the scientific evidence, I would assign a very high confidence score to the judgment that the claim "The Earth is flat" is false. The score would be linked to the specific scientific articles and satellite imagery used as evidence.

4.  **Generate outputs:** I would create a structured summary of my findings, including the claim, a summary of the evidence, my judgment (False), the confidence score, and the evidence identifiers.  I would also recommend that the claim be marked as definitively fact-checked, as the evidence is conclusive.

**In summary, my role is to be a diligent and policy-aware fact-checker, ensuring that claims are rigorously evaluated and that decisions are made based on the best available evidence, within the constraints of the specified policies.**