Okay, I understand. As the Fact Extractor Primary in the Gather stage, my objective is to collect and structure information, providing a summary of findings, confidence scores, and recommendations, while adhering to the provided policies.  I must also be mindful of evidence alignment and governance compliance throughout this process.  Here's a more detailed breakdown of how I will approach this:

**1. Understanding and Internalizing the Policies:**

*   **`policy.evidence_threshold`:** This defines the minimum confidence level required for a finding to be considered valid and included in the summary. I will need to quantify evidence strength based on source reliability, corroboration, and logical consistency.
*   **`policy.latency_budget`:** This sets a time limit for the fact extraction process. I will need to prioritize tasks and manage my time efficiently to complete the work within the allotted time. This might involve strategically choosing research depth or sources.
*   **`policy.research_depth`:** This specifies how far to delve into the available information. A shallower depth might mean relying on more readily available sources, while a deeper dive requires exploring more obscure or primary sources.
*   **`policy.seed.evidence_threshold`:** This might define a *higher* minimum confidence level when starting with initial seed information, suggesting the initial information needs stronger corroboration before expansion.
*   **`policy.seed.max_research_depth`:** This sets a maximum depth of research specifically for the initial "seed" information, possibly to prevent excessive time spent validating a single initial data point.
*   **`policy.seed.max_total_time`:**  This is a hard limit on the amount of time that can be spent exploring initial seed information, further ensuring timely progression through the gather stage.

**2. Fact Extraction Process:**

*   **Initial Seed Analysis:** I'll begin by analyzing any provided seed information, adhering to `policy.seed.evidence_threshold`, `policy.seed.max_research_depth`, and `policy.seed.max_total_time`.  This means quickly attempting to corroborate or refute the seed information to a higher confidence standard.
*   **Information Gathering:** Based on the seed information (or lacking it, the initial prompt), I will identify relevant information sources.  This could include web searches, databases, document repositories, or APIs.  The choice of sources will be influenced by `policy.research_depth`.  I will prioritize sources that are known to be reliable and aligned with governance requirements.
*   **Information Filtering and Prioritization:** I will filter the gathered information, focusing on data that directly addresses the core fact extraction task. I will prioritize information based on potential relevance and source reliability.
*   **Fact Identification and Extraction:** I will identify and extract potential facts from the filtered information. This involves identifying key entities, relationships, and attributes.
*   **Evidence Evaluation and Scoring:** For each extracted fact, I will evaluate the supporting evidence, considering source credibility, corroboration from multiple sources, and logical consistency. I will assign a confidence score based on `policy.evidence_threshold` and the strength of the evidence.
*   **Fact Synthesis and Structuring:** I will synthesize the extracted facts into a structured summary. This summary will organize the information in a clear and concise manner, highlighting key findings.

**3. Output Generation:**

*   **Structured Summary of Findings:** This output will present the extracted facts in a logical and organized format. The format may vary depending on the specific requirements of the task, but will generally include key entities, relationships, and attributes.
*   **Confidence Score with Supporting Evidence Identifiers:**  Each extracted fact will be accompanied by a confidence score and a list of evidence identifiers. These identifiers will allow traceability back to the original sources of information. The confidence score will reflect the strength of the supporting evidence and alignment with `policy.evidence_threshold`.
*   **Next-Step Recommendation or Escalation Flag:** Based on the findings, I will provide a recommendation for the next steps. This could include:
    *   **Continue Gathering:** If the confidence level is below the threshold or if there are significant gaps in the information, I will recommend continuing the information gathering process.
    *   **Refine Search:** If the information is not relevant, I will refine the search queries to be more focused.
    *   **Move to the next stage:** If the confidence level is above the threshold and the information is sufficient, I will recommend moving to the next stage.
    *   **Escalate:** If I encounter any issues that I cannot resolve, such as ambiguous information, conflicting evidence, or potential violations of policies, I will escalate the task to a human analyst.

**4. Governance Compliance and Evidence Alignment:**

*   **Provenance Tracking:**  I will meticulously track the provenance of all extracted facts, ensuring that each fact can be traced back to its original source. This is critical for maintaining evidence alignment and ensuring governance compliance.
*   **Policy Enforcement:** I will continuously monitor my activities to ensure that they are aligned with the policies. If I encounter any potential conflicts between policies, I will escalate the issue to a human analyst for resolution.
*   **Bias Mitigation:** I will be mindful of potential biases in the information sources and in my own analysis. I will strive to mitigate these biases by seeking diverse perspectives and using objective criteria for evaluating evidence.

**Example Scenario:**

Let's say the task is: "Identify the CEO of Microsoft." And the policies are:

*   `policy.evidence_threshold = 0.8` (Confidence must be 80% or higher)
*   `policy.latency_budget = 10 minutes`
*   `policy.research_depth = 2` (Follow links up to 2 levels deep)
*   `policy.seed.evidence_threshold = 0.95` (Seed information requires 95% confidence)
*   `policy.seed.max_research_depth = 1`
*   `policy.seed.max_total_time = 2 minutes`

**Process:**

1.  I might start with a Google search.
2.  If the first result is the Microsoft Wikipedia page, I would examine that page.
3.  If the page clearly states "Satya Nadella is the CEO of Microsoft" with a citation to the Microsoft website, I would then check the Microsoft website.
4.  If the Microsoft website confirms Satya Nadella as CEO, I would then score this as highly confident, (e.g., 0.95 or higher), as this is coming directly from the official source.  This satisfies `policy.evidence_threshold`.
5.  Since I achieved a high confidence score relatively quickly and within the time budget, I would output:

    *   **Structured Summary:**  "The CEO of Microsoft is Satya Nadella."
    *   **Confidence Score:** 0.95
    *   **Evidence Identifiers:**  "Microsoft Wikipedia (2023-10-27), Microsoft.com/leadership"
    *   **Next Step:** "Move to next stage."

If the Wikipedia page listed a CEO but had a very old citation, and I spent a minute looking for a better source, but could not find a more authoritative source within the Microsoft website or other reputable sources within the `policy.seed.max_total_time`, I would not meet the seed threshold.  I would then broaden my search slightly and would accept lower quality evidence and proceed as outlined above, aiming for the `policy.evidence_threshold`.  I would also adjust my confidence level accordingly, as the evidence is not as strong.

By following this approach, I will strive to fulfill the objectives of the Fact Extractor Primary role while adhering to the provided policies.  I am ready to receive instructions and begin the gathering process.