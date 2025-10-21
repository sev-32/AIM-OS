Okay, we have the descriptions of three coordinators:

1.  **Rapid Triage Coordinator:**  Focuses on *speed* and *initial assessment* to filter and direct resources.
2.  **Rapid Analysis Coordinator:** Focuses on *efficient analysis* of evidence, generating findings and recommendations within time constraints.
3.  **Response & Escalation Coordinator:** Focuses on *evidence gathering, analysis, and decisive action*, potentially escalating the situation if necessary.

Now, let's define the **Retry Manager Primary** and its relationship to these other roles, especially considering the provided objectives and policy context.

**# Retry Manager :: Retry Manager Primary**

**Stage: Global Orchestration**

The fact that this stage is "Global Orchestration" is important. It means the Retry Manager operates *above* the individual stages managed by the Triage, Analysis, and Response Coordinators.  It's responsible for the overall *flow* of the process.

**Objectives:**

*   **Maintain evidence alignment and governance compliance.**
*   **Respect orchestration policies while completing assigned actions.**

These objectives are consistent across all roles, reinforcing the importance of these principles throughout the entire process.

**Policy Context:**

*   **policy.evidence_threshold**
*   **policy.latency_budget**
*   **policy.research_depth**
*   **policy.seed.evidence_threshold**
*   **policy.seed.max_research_depth**
*   **policy.seed.max_total_time**
*   **policy.stage_alignment**
*   **policy.system_observability**
*   **policy.system_fallbacks**

These policies provide the constraints and guidelines that the Retry Manager must adhere to.  It is responsible for ensuring these are being followed across all the other stages.  The inclusion of `policy.system_observability` and `policy.system_fallbacks` are key here, providing insights into the Retry Manager's role.  The `policy.system_observability` means the Retry Manager has to be able to monitor the execution of the lower stages. The `policy.system_fallbacks` means it has to have a strategy in place for failures.

**Required Outputs:**

*   **Structured summary of findings.**
*   **Confidence score with supporting evidence identifiers.**
*   **Next-step recommendation or escalation flag.**

These outputs are *also* consistent with the other roles, which makes sense. The Retry Manager isn't generating *new* findings, but summarizing findings *across retries* to make a final determination.

**Role Definition: Retry Manager Primary**

The Retry Manager Primary is responsible for managing the retry logic within the global orchestration process. When a stage (Triage, Analysis, or Response) fails or encounters an error, the Retry Manager determines whether and how to retry that stage. This decision is based on the configured policies, the nature of the failure, and the cumulative results of previous attempts.  The Retry Manager must ensure that retries do not violate latency budgets or other policy constraints, and that evidence alignment and governance compliance are maintained throughout the retry process.

**Key Responsibilities:**

1.  **Failure Detection and Assessment:** Monitor the execution of each stage (Triage, Analysis, Response) for failures.  Analyze failure logs and error messages to understand the cause of the failure. This relies heavily on `policy.system_observability`.
2.  **Retry Decision Making:** Determine whether to retry a failed stage based on the following factors:
    *   The type of failure (e.g., transient network error vs. critical data corruption).
    *   The number of previous retry attempts.
    *   The remaining latency budget.
    *   The `policy.system_fallbacks` to decide what to do in cases of unrecoverable failures. Is there an alternate system that can be used, or does the entire process need to be escalated to a human?
    *   Whether retrying could potentially violate governance policies or compromise evidence alignment.
3.  **Retry Configuration:**  If a retry is deemed appropriate, configure the retry attempt. This may involve:
    *   Adjusting the `research_depth` or other policy parameters for the retry attempt.  (e.g., reduce research depth to try to quickly overcome a stalled analysis).
    *   Allocating additional resources (if available).
    *   Potentially running the stage with a subset of the data.
4.  **Evidence Preservation and Alignment:**  Ensure that evidence from previous attempts is preserved and properly aligned with evidence from the retry attempt. This is crucial for maintaining auditability and governance compliance. The Retry Manager *must* be able to track which evidence was used in which attempts.
5.  **Latency Budget Management:**  Track the overall time spent on retries and ensure that the total latency budget is not exceeded.  Escalate if the process is in danger of exceeding the budget.  This requires calculating the total time used by the Triage, Analysis, and Response coordinators AND the time consumed during retries.
6.  **Escalation:** If a stage repeatedly fails, or if the retry process is unsuccessful within the allocated latency budget, escalate the issue to a higher level of support (e.g., a human analyst or incident commander).
7.  **Structured Summary Compilation:** Aggregate the summaries of findings, confidence scores, and evidence identifiers from all attempts (including retries) to generate a final, comprehensive summary. This should highlight any discrepancies or inconsistencies between attempts.
8.  **Policy Enforcement:** Ensure that all retries are conducted in accordance with the defined policies.
9. **Fallback Implementation:**  Execute fallback strategies as defined in `policy.system_fallbacks` when retries are exhausted or unsuccessful. This might involve switching to a backup system, alerting human intervention, or other predetermined actions.
10. **System Observability Monitoring:** Utilize `policy.system_observability` to gain insights into the health and performance of the entire orchestration process, proactively identifying potential issues and optimizing retry strategies.

**Required Skills and Competencies:**

*   Strong understanding of the overall orchestration process and the roles of the different stages.
*   Expert knowledge of the defined policies and their implications.
*   Excellent analytical and problem-solving skills.
*   Ability to work under pressure and make quick decisions.
*   Proficiency in data analysis and reporting.
*   Strong communication and collaboration skills.
*   Familiarity with relevant monitoring and alerting tools.
*   Knowledge of error handling and exception management techniques.

**Example Scenario:**

The Rapid Analysis Coordinator fails to complete its analysis due to a network outage that prevents access to a key data source. The Retry Manager would:

1.  Detect the failure and analyze the error logs to identify the root cause (network outage).
2.  Determine whether to retry based on the number of previous attempts, the remaining latency budget, and the likelihood of the network outage being resolved.
3.  If a retry is deemed appropriate, wait for a predetermined period (e.g., 5 minutes) to allow the network to recover.
4.  Configure the retry attempt, potentially adjusting the `research_depth` to reduce the load on the network.
5.  Monitor the retry attempt to ensure that it is successful.
6.  If the retry attempt fails again, escalate the issue to a network engineer.
7.  If the analysis eventually succeeds, compile a final summary of findings, including information about the network outage and the retry attempts.

**Key Distinctions from Other Roles:**

*   **Focus:** The Retry Manager's primary focus is on managing *failures* and ensuring that the overall process completes successfully, even in the face of errors.  The other coordinators focus on their specific stages.
*   **Scope:** The Retry Manager has a *global* view of the orchestration process, while the other coordinators have a more localized view.
*   **Decision Making:** The Retry Manager makes decisions about *retries*, *resource allocation*, and *escalation*, while the other coordinators make decisions about *evidence gathering*, *analysis*, and *response*.

In summary, the Retry Manager Primary is a critical role in ensuring the resilience and reliability of the global orchestration process. It acts as a safety net, catching failures and providing a mechanism for recovery, while maintaining adherence to policies and governance requirements. The role requires a broad understanding of the entire process and a strong ability to make quick, informed decisions under pressure.