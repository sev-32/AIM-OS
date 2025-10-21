Okay, I understand the various coordinator roles (search, extraction, analysis, validation, reporting) and the common framework they operate within. This is sufficient to define the Retry Manager's responsibilities.

## Retry Manager Responsibilities

As the Retry Manager, operating within the "Global Orchestration" stage, my role is to monitor the progress of tasks assigned to various coordinators (Search, Extraction, Analysis, Validation, Reporting) and to handle situations where these tasks fail, timeout, or produce unsatisfactory results. I operate under the principle of evidence alignment and governance compliance, ensuring that retries do not compromise data integrity or violate established policies. My primary function is to optimize resource utilization and improve the overall success rate of tasks within the orchestration.

**1. Failure Detection and Triggering Retries:**

*   **Monitoring Task Status:**  Actively monitor the status of tasks assigned to coordinators. This involves listening for error signals, timeout notifications, or unsatisfactory confidence scores.
*   **Determining Retry Eligibility:** Evaluate whether a task is eligible for retry based on its failure reason and the applicable policies. Certain types of failures (e.g., system outages) might be more suitable for retries than others (e.g., logical errors in analysis).
*   **Retry Count Management:** Track the number of retry attempts for each task. Enforce limits on the number of retries to prevent infinite loops and resource exhaustion.
*   **Exception Handling:**  Implement robust exception handling to prevent the Retry Manager itself from failing. Log all errors and retry attempts for auditing purposes.

**2. Policy-Driven Retry Execution:**

*   **Respecting Latency Budget (`policy.latency_budget`):**  Ensure that retries do not violate the overall latency budget. Adjust retry strategies (e.g., reduced research depth, faster extraction methods) to stay within the allotted time.  Prioritize tasks nearing their deadline.
*   **Adjusting Research Depth (`policy.research_depth`, `policy.seed.max_research_depth`):** If a task fails due to time constraints, consider reducing the research depth for subsequent retries. This might involve focusing on the most relevant sources or using more efficient analysis techniques.
*   **Modifying Search Strategies (Search Coordinator):**  If the initial search strategy yields poor results, the Retry Manager can instruct the Search Coordinator to modify the search terms, databases, or inclusion/exclusion criteria for retries.
*   **Optimizing Extraction Parameters (Extraction Coordinator):**  If the extraction process is failing due to complexity or data format issues, the Retry Manager can adjust parameters to simplify the extraction.
*   **Adjusting Validation Criteria (Validation Coordinator):**  If the initial validation fails, consider relaxing the validation criteria slightly (while still maintaining evidence threshold requirements) or focusing on the most critical aspects.
*   **Respecting Evidence Thresholds (`policy.evidence_threshold`, `policy.seed.evidence_threshold`):** Retries cannot compromise the required level of evidence. The Retry Manager must ensure that any adjustments to search strategies or analysis techniques do not lead to weaker or less reliable evidence.
*   **System Fallbacks (`policy.system_fallbacks`):** Where supported by policy, the Retry Manager may select alternative systems (different databases, analysis tools, etc) if the initial system has experienced a failure or provides inadequate performance.

**3. Providing Context for Retries:**

*   **Communicating with Coordinators:** When triggering a retry, provide the Coordinator with detailed information about the failure reason, the number of previous attempts, and any adjustments to policies or parameters.
*   **Preserving Context:** Where possible, preserve the context from previous attempts (e.g., partially extracted data, search results) to avoid redundant work.

**4. Monitoring Retry Performance:**

*   **Tracking Retry Success Rates:** Monitor the success rate of retried tasks. Identify patterns or trends that indicate systemic issues or areas for improvement.
*   **Analyzing Retry Costs:**  Track the resources consumed by retries (e.g., time, computational power). Optimize retry strategies to minimize resource consumption.

**5. Escalation and Exception Handling:**

*   **Escalation:** If a task fails after multiple retries, escalate the issue to a human reviewer for further investigation. Provide the reviewer with all relevant information about the failure history and the attempts made to resolve it.
*   **Circuit Breaker Pattern:**  Implement a circuit breaker pattern to prevent cascading failures. If a specific task or Coordinator is consistently failing, temporarily disable retries to avoid overwhelming the system.

**Required Outputs:**

*   **Retry Log:** A detailed log of all retry attempts, including the task ID, failure reason, number of attempts, policy adjustments, and success/failure status.
*   **Retry Performance Report:**  A report summarizing the success rate of retries, the resources consumed, and any identified patterns or trends.
*   **Escalation Notifications:**  Alerts to human reviewers when a task fails after multiple retries or when a systemic issue is detected.

**Additional Considerations:**

*   **Idempotency:**  Ensure that the tasks being retried are idempotent, meaning that they can be executed multiple times without causing unintended side effects.
*   **Concurrency:**  Manage concurrency carefully to avoid overloading the system during retries.
*   **Observability (`policy.system_observability`):** Ensure that the retry manager exposes metrics and logs which allow operators to understand the cause of failures, the frequency of retries, and the effectiveness of different retry strategies.

The Retry Manager acts as a critical safety net and optimization engine, ensuring that tasks within the orchestrated system are completed efficiently and reliably while respecting the established policies and constraints.  Its success is measured by its ability to minimize failures, optimize resource utilization, and escalate issues promptly when necessary.