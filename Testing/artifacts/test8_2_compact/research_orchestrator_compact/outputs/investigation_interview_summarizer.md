Okay, this outlines the "Interview Summarizer Primary" stage within a larger "Interview Summarizer" process. Let's break down what it means in practical terms:

**Goal:** To create a structured summary of an interview, adhering to specific policies and providing a confidence score.

**Key Aspects:**

*   **Stage:** Investigation - This suggests the primary function is to analyze the interview and extract key information.
*   **Evidence Alignment & Governance:** Ensuring the summary is based on demonstrable evidence from the interview and follows defined organizational guidelines. Think: Fact-checking, source attribution, and adherence to data privacy policies.
*   **Orchestration Policies:** Working within a larger workflow, this step needs to respect established rules for how different parts of the process interact (e.g., data flow, prioritization, error handling).  It can't just do whatever it wants; it has to fit within the broader system.

**Policy Context (Crucial):** This is where the specific limitations and priorities are defined.  The system needs to be aware of these:

*   **`policy.evidence_threshold`:**  The minimum amount of evidence required to support a conclusion. For example, at least 3 mentions of a topic before it's considered significant.
*   **`policy.latency_budget`:** The maximum acceptable time to complete this stage. Time is a constraint!
*   **`policy.research_depth`:**  How much extra research (if any) is allowed beyond the immediate interview transcript.  Is the system allowed to look up external definitions or context for terms used in the interview?
*   **`policy.seed.evidence_threshold`:** If this summarization is seeded (started) with an existing, potentially incomplete summary, this sets the evidence threshold for considering elements from that seed.  Lower values would accept potentially weaker initial assertions.
*   **`policy.seed.max_research_depth`:** Similar to `policy.research_depth`, but it pertains to research allowed on the *seed summary* itself.  How much should the system investigate the source or validity of the seed?
*   **`policy.seed.max_total_time`:** The maximum time allocated specifically to investigating the seed. This is separate from the overall `policy.latency_budget` that governs the entire summarization process.

**Required Outputs:**

*   **Structured Summary:** A well-organized summary of the interview findings.  This could be in a specific format (e.g., a table, bullet points, a paragraph with headings).
*   **Confidence Score & Evidence IDs:** A numerical score indicating the system's certainty in its summary, along with identifiers linking the summary points back to specific sections of the interview transcript (or other sources, depending on `policy.research_depth`).
*   **Next-Step Recommendation/Escalation Flag:**  Based on the findings, the system needs to suggest what to do next (e.g., pass the summary to a reviewer, trigger another process, highlight a potential problem) or flag the summary for escalation if something requires human attention.

**In Summary (TL;DR):**

This stage is all about creating a reliable, evidence-based summary of an interview within a specific time limit, adhering to defined policies, and recommending the next steps based on the summarized content.  The policies control the balance between speed, accuracy, and the amount of external research permitted.