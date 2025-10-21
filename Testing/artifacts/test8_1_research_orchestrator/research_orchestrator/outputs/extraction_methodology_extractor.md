Okay, I understand. As the Methodology Extractor Primary, my role in the Content Extraction stage is to identify and extract the methodologies used in a given text (or set of texts), adhering to the specified objectives and within the constraints of the defined policies. My focus is on extracting information related to *how* the research or process was conducted, not necessarily *what* the results were.

Here's a breakdown of my responsibilities and how I'll approach the task:

**1. Understanding and Applying Policies:**

*   **`policy.evidence_threshold`**:  This defines the minimum acceptable level of evidence required for me to confidently identify a methodology.  Higher thresholds mean I need stronger, more explicit statements about the methodology used. Lower thresholds allow for inference based on less direct statements.
*   **`policy.latency_budget`**: This dictates the maximum allowable time I have to complete the task. This will influence how thoroughly I can search and analyze the input.
*   **`policy.research_depth`**: This limits how much external research I can conduct to understand specific methodologies mentioned.  A higher depth allows me to delve into unfamiliar methodologies, while a lower depth requires me to focus on well-known and easily understood approaches.
*   **`policy.seed.evidence_threshold`**: This likely refers to the initial level of confidence required when starting the extraction process.  It may be more lenient than the overall `evidence_threshold`, allowing me to explore potential methodologies based on weaker initial signals.
*   **`policy.seed.max_research_depth`**: Similar to `policy.research_depth`, but likely applies to the initial identification phase, limiting how much research I can do on potentially relevant methodologies *before* I've confirmed their use in the text.
*   **`policy.seed.max_total_time`**: This likely specifies a time limit for the initial identification and seed-building phase.

**2. Content Extraction Process:**

*   **Identification:** I will scan the input text for keywords and phrases indicative of methodologies. Examples include:
    *   "The methodology used..."
    *   "We employed a..."
    *   "This study utilized..."
    *   Specific method names (e.g., "Regression analysis," "A/B testing," "Qualitative interviews," "Scrum methodology").
*   **Evidence Gathering:** When I identify a potential methodology, I will gather supporting evidence from the text, noting the specific sentences or paragraphs that describe the methodology.  This will be crucial for calculating the confidence score.
*   **Structuring Findings:** I will structure the extracted information into a clear and concise summary.  This summary will include:
    *   A list of identified methodologies.
    *   A brief description of each methodology as described in the text.
    *   For each methodology, a list of evidence identifiers (e.g., sentence numbers, paragraph numbers, specific quotes).
    *   A confidence score for each identified methodology, based on the strength of the evidence.
*   **Confidence Scoring:** I will assign a confidence score to each identified methodology. This score will be based on:
    *   **Evidence Strength:** How directly the text describes the use of the methodology.
    *   **Evidence Quantity:** How many pieces of evidence support the identification of the methodology.
    *   **Contextual Clarity:** How clear and unambiguous the description of the methodology is.
*   **Documentation and Governance Compliance:**  I will ensure that all extracted information and confidence scores are properly documented and stored in a way that supports evidence alignment and governance compliance.  This might involve using specific tagging or metadata schemes.

**3. Outputs and Next Steps:**

*   **Structured Summary of Findings:**  A well-organized document summarizing the identified methodologies, descriptions, supporting evidence, and confidence scores.  This will be the primary deliverable.
*   **Confidence Scores with Supporting Evidence Identifiers:**  Clearly presented confidence scores for each methodology, along with the specific text identifiers that support the scoring.
*   **Next-Step Recommendation or Escalation Flag:**  Based on the confidence scores and the defined policies, I will recommend one of the following:
    *   **Proceed to the Next Stage:** If the confidence scores for the identified methodologies meet the required threshold, I will recommend proceeding to the next stage of the process (e.g., deeper analysis of the methodologies).
    *   **Further Research:**  If the confidence scores are below the threshold but there is still potential for identifying methodologies, I will recommend further research (e.g., searching for additional information within the text or conducting external research to clarify ambiguities). This would be done within the constraints of the `policy.research_depth` and `policy.latency_budget`.
    *   **Escalation:** If I am unable to identify any methodologies with sufficient confidence, or if I encounter issues that are beyond my capabilities, I will escalate the task to a human reviewer or a more specialized system.

**In summary, I will meticulously extract information about methodologies from the input text, guided by the specified policies and aiming to provide a clear, structured summary with associated confidence scores and recommendations.**

To proceed, please provide me with the input text or document to analyze.  Also, clarify the specific values for the policy parameters (e.g., `policy.evidence_threshold = 0.8`, `policy.latency_budget = 30 minutes`) if they are not already defined. This will allow me to tailor my extraction process to the specific requirements of the task.