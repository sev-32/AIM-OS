Okay, I understand the roles of both the Gather Coordinator and the Produce Coordinator. Now, let's simulate the role of the **Retry Manager Primary**, given the initial information you provided about it.

**Retry Manager Primary: Role Simulation**

As the Retry Manager Primary, operating within the "Global Orchestration" stage, my purpose is to ensure the successful completion of tasks delegated to other coordinators (like the Gather Coordinator or the Produce Coordinator) by intelligently handling failures or situations where predefined policy thresholds aren't met. My focus is on maintaining evidence alignment, governance compliance, and respecting orchestration policies, just like the coordinators I support. However, my specific actions revolve around deciding whether a retry is appropriate, and configuring that retry to maximize its chances of success.

**Understanding the Context**

I will receive reports from other coordinators, indicating whether they have successfully completed their tasks or encountered issues. These reports will include:

*   **Structured Summary of Findings:** From the failing task.
*   **Confidence Score with Supporting Evidence Identifiers:** From the failing task.
*   **Next-Step Recommendation or Escalation Flag:** From the failing task.  Crucially, this will include a reason why the task failed.

**My Objectives (Reiterated):**

*   **Maintain evidence alignment and governance compliance.**
*   **Respect orchestration policies while completing assigned actions.**

**Policy Context (Reiterated):**

*   `policy.evidence_threshold`
*   `policy.latency_budget`
*   `policy.research_depth`
*   `policy.seed.evidence_threshold`
*   `policy.seed.max_research_depth`
*   `policy.seed.max_total_time`
*   `policy.stage_alignment`
*   `policy.system_observability`
*   `policy.system_fallbacks`

**My Core Responsibilities and Actions:**

1.  **Failure Analysis:**

    *   **Reason for Failure:** The first thing I do is analyze *why* a previous coordinator failed. Did they fail to meet the `policy.evidence_threshold`? Did they exceed the `policy.latency_budget`? Was there conflicting evidence they couldn't resolve within the allowed `policy.research_depth`? Was there a system error, indicated by `policy.system_observability` capturing the error?
    *   **Impact Assessment:** I need to assess the impact of the failure on the overall orchestration. Is this a critical failure that requires immediate attention? Or is it a minor issue that can be retried later?

2.  **Retry Decision:**

    *   **Retry Feasibility:** Based on the failure analysis, I determine if a retry is feasible and appropriate.
        *   **Exceeded Latency Budget:** If the `policy.latency_budget` was the *sole* reason for failure, and the evidence gathered is of good quality, a retry might be possible *if* the overall orchestration allows for a revised budget. However, this needs careful consideration. If the budget can't be extended, escalation is likely the best option.
        *   **Failed to Meet Evidence Threshold:** If the `policy.evidence_threshold` was not met, a retry is likely worthwhile, *provided* I can adjust the retry parameters to improve the chances of success (see below).
        *   **System Error:** If `policy.system_observability` indicates a transient system error, a retry with no parameter changes might be sufficient. If the error persists, I may need to engage `policy.system_fallbacks` for alternative solutions.
        *   **Unresolvable Conflict:** If there was unresolvable conflicting evidence within the current `policy.research_depth`, increasing the `policy.research_depth` *might* be an option, but I need to weigh that against the `policy.latency_budget` and the overall objectives.
    *   **Compliance Check:** I must ensure that retrying the task doesn't violate any policies. For instance, excessive retries could negatively impact system performance (contradicting `policy.system_observability`).

3.  **Retry Configuration (If Retry is Deemed Appropriate):**

    *   **Parameter Adjustment:** I adjust the parameters for the retry to improve the chances of success. This is the *key* to my role. Some examples:
        *   **Increase `policy.research_depth`:** If the previous coordinator couldn't find enough relevant evidence, I might increase the allowed research depth. However, I need to be careful not to exceed the overall `policy.latency_budget`.
        *   **Relax `policy.evidence_threshold` (with caution):** *Only if* the initial threshold was deemed overly aggressive, and *only if* the risk is acceptable, I might slightly relax the `policy.evidence_threshold`. This should be a last resort.
        *   **Provide New Seed Data:** If the initial seed data proved unfruitful, I might provide a new set of "seed" data to the retrying coordinator. This involves adjusting `policy.seed.evidence_threshold`, `policy.seed.max_research_depth`, and `policy.seed.max_total_time` accordingly.
        *   **Specify Different Data Sources:** If applicable, I can direct the retrying coordinator to use different data sources than the original coordinator. This leverages `policy.system_fallbacks` if data source availability is the issue.
        *   **Adjust Latency Budget:**  In limited cases, and with appropriate authorization, I might request a slight increase to the `policy.latency_budget`, but this has to be carefully balanced against the overall system performance and goals.
    *   **Logging and Monitoring:** I carefully log all retry attempts, including the original failure reason, the adjusted parameters, and the outcome of the retry. This is essential for maintaining `policy.system_observability` and for continuous improvement of the orchestration process.

4.  **Output/Decision:**

    *   **Successful Retry:** If the retry succeeds, I log the successful outcome and pass the results (structured summary, confidence score, recommendation) on to the next stage in the orchestration.
    *   **Failed Retry:** If the retry fails, I will escalate the issue. The escalation report will include:
        *   The original failure reason.
        *   The retry configuration (parameters adjusted).
        *   The outcome of the retry (including the reason for the second failure).
        *   A clear explanation of why further retries are not recommended.

**Example Scenario:**

Let's say the Gather Coordinator failed to meet the `policy.evidence_threshold` of 0.7. They reported a confidence score of 0.6 with evidence IDs [A, B, C], and flagged for escalation.

As the Retry Manager Primary, I would:

1.  Analyze the Gather Coordinator's report.  The primary failure reason is not meeting the `policy.evidence_threshold`.
2.  Assess whether additional research might uncover more evidence. Is the topic well-documented, or is information scarce?
3.  Decide to retry, but increase the `policy.research_depth` from "Shallow" to "Medium".
4.  Record the retry attempt in the system logs.
5.  If the Gather Coordinator *still* fails to meet the `policy.evidence_threshold` after the retry with increased research depth, I would escalate, including the original report, the retry configuration, and the outcome. My escalation note would explain that increasing the research depth did not yield sufficient additional evidence.

**Key Considerations:**

*   **Idempotency:** I need to be aware of whether the tasks being retried are idempotent (can be executed multiple times without unintended side effects). If a task is not idempotent, retrying it could cause problems.
*   **Deadlock Prevention:** I must carefully manage retry attempts to avoid infinite loops or deadlocks. Setting limits on the number of retries and carefully monitoring retry outcomes is crucial.
*   **Communication:** Clear communication with other coordinators and stakeholders is essential. They need to understand why a retry is being attempted and what the expected outcomes are.

**In conclusion, my role as the Retry Manager Primary is a critical one for ensuring the robustness and reliability of the overall orchestration process. I act as a smart fallback, intelligently analyzing failures and adjusting parameters to maximize the chances of success, while always remaining compliant with defined policies and prioritizing the overall goals of the system.** I am not just blindly retrying tasks; I am actively problem-solving to overcome challenges and maintain a high level of confidence in the outcomes.