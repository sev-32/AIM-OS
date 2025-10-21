Okay, I understand. As an Algorithm Benchmark Analyst, operating in the Quantum Analysis stage, my primary function is to analyze algorithm benchmark data, adhering to the specified policies and focusing on maintaining evidence alignment and governance compliance. I will respect orchestration policies and deliver the required outputs.

Here's a breakdown of my understanding and planned execution:

**1. Core Responsibilities:**

*   **Analyze Algorithm Benchmark Data:** This involves processing and interpreting the data produced from running algorithm benchmarks on quantum computing platforms or simulators.  This likely includes performance metrics like execution time, error rate, resource utilization (qubits, gates, etc.), and scalability.
*   **Evidence Alignment:**  Ensuring that any conclusions drawn from the benchmark data are directly supported by the data itself.  This means meticulously tracking the source of each piece of evidence and clearly articulating how it supports the overall assessment.  This is crucial for auditability and trustworthiness.
*   **Governance Compliance:**  Adhering to internal and external regulations and guidelines regarding data analysis, security, privacy, and responsible AI development. This may involve documentation standards, data access controls, and bias detection procedures.
*   **Respect Orchestration Policies:**  Integrating with the larger workflow and respecting the rules established by the orchestration system.  This likely includes timing constraints, resource limitations, and communication protocols.

**2. Policy Context (and how I will use them):**

*   **`policy.evidence_threshold`:** This defines the minimum level of supporting evidence required to reach a conclusion.  I will use this to determine how much data is necessary before forming an opinion or making a recommendation.  If the evidence is below the threshold, I will either escalate or perform further analysis within policy limits.
*   **`policy.latency_budget`:** This specifies the maximum allowable time to complete the analysis and produce the required outputs.  I will prioritize my tasks to meet this deadline.  If I foresee exceeding the budget, I will escalate.
*   **`policy.research_depth`:** This limits the scope of investigation and prevents me from going down unproductive rabbit holes. I will only explore the benchmark data and related documentation to the level specified by this policy.
*   **`policy.seed.evidence_threshold`:**  This probably defines the minimum level of evidence required when dealing with initial or "seed" data points. It is likely to be a lower threshold than `policy.evidence_threshold` as the seed data is often used for initial direction and may require more analysis to confirm.
*   **`policy.seed.max_research_depth`:** Similar to `policy.research_depth` but specifically applies to the analysis of initial "seed" data.
*   **`policy.seed.max_total_time`:** Limits the total time that can be spent on the initial "seed" data.

**3. Required Outputs and How I Will Generate Them:**

*   **Structured summary of findings:**  This will be a concise and well-organized report summarizing the key observations from the benchmark data analysis.  It will highlight strengths and weaknesses of the algorithm(s) being evaluated, potential areas for improvement, and any anomalies detected. I will use a pre-defined template (if available) or a clear, consistent structure with headings, bullet points, and visualizations where appropriate.  The summary will be tailored to the target audience (e.g., researchers, engineers, managers).
*   **Confidence score with supporting evidence identifiers:**  This expresses my assessment of the reliability and validity of the findings.  The confidence score will be a numerical value (e.g., on a scale of 1 to 100) or a qualitative rating (e.g., low, medium, high). Crucially, I will provide clear references to the specific data points, logs, or documentation that support the confidence score. These identifiers will enable traceability and independent verification of my conclusions. For example: "Confidence: 85% (Supporting evidence: Log file XYZ, data point 123, document ABC)".
*   **Next-step recommendation or escalation flag:** Based on the analysis and the policies, I will recommend a course of action.  This could be to:
    *   **Continue analysis with a specific focus:**  "Recommend further analysis on Algorithm A's performance in scenario X due to observed instability (Evidence: data points 45-50, error log ZZZ)."
    *   **Proceed to the next stage of the benchmark:** "Algorithm B meets the performance criteria in environments C and D; recommend progressing to stability testing."
    *   **Escalate to a subject matter expert:** "Observed an anomaly in Algorithm C's memory usage that requires expert investigation (Evidence: memory usage log, graph YYY).  Escalating to the Quantum Architecture team."
    *   **Stop and report inconclusive results:** "Insufficient data to draw meaningful conclusions regarding Algorithm D's performance; recommend restarting the benchmark with increased data collection (Evidence: total data points below threshold)."

**Example Scenario and Application of Policies:**

Let's say I'm analyzing the performance of a new quantum algorithm.  The `policy.evidence_threshold` is set to 75% of data points within a specified range.  The `policy.latency_budget` is 4 hours. The `policy.research_depth` is limited to the specific benchmark dataset and related algorithm documentation.

1.  **Initial Analysis:** I analyze the first batch of benchmark data.
2.  **Evidence Assessment:**  I find that only 60% of the data points meet the required performance criteria. This is below the `policy.evidence_threshold`.
3.  **Policy Application:**  I cannot conclude that the algorithm meets the performance requirements.
4.  **Further Investigation:**  Following the `policy.research_depth`, I examine the algorithm documentation and benchmark setup to see if there are any obvious issues.  I find a potential problem with the calibration of the qubits used in the benchmark.
5.  **Recommendation:**  I generate the following outputs:
    *   **Structured Summary:** "Initial analysis of the algorithm indicates sub-optimal performance.  Only 60% of data points meet the target criteria.  A potential issue with qubit calibration has been identified."
    *   **Confidence Score:** "Confidence: 60% (Supporting evidence: Benchmark data summary, calibration log XYZ, algorithm documentation section 3.2)."
    *   **Next-Step Recommendation:** "Recommend re-running the benchmark after recalibrating the qubits. If the problem persists, escalate to the hardware team."

**In summary, my role is to rigorously analyze algorithm benchmark data, ensuring that my conclusions are well-supported by evidence, compliant with relevant policies, and communicated effectively. I will prioritize efficiency and transparency in all my activities.**

What specific instructions or data access points do I need to begin? Please provide the benchmark data, policy files, and any relevant documentation.