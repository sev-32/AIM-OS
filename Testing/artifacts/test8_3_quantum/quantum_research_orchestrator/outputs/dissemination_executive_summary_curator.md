Okay, this is a good start for defining the role and responsibilities of the "Executive Summary Curator" during the "Stakeholder Dissemination" stage. Let's break down what it tells us and then consider how to expand it for clarity and operational effectiveness.

**Understanding the Current Definition**

*   **Role:**  The Executive Summary Curator synthesizes information into a digestible format for stakeholders. Their primary concern is maintaining accuracy and adhering to governance.
*   **Stage:** They operate during the "Stakeholder Dissemination" stage, implying previous analysis and findings are ready to be communicated.
*   **Objectives:**
    *   **Alignment & Compliance:** Ensures the executive summary is consistent with the underlying evidence and follows established governance procedures.
    *   **Policy Adherence:**  Respects pre-defined policies during their work.
*   **Policy Context:**  These policies act as constraints and guidelines for the curator's work:
    *   `policy.evidence_threshold`: The minimum amount/strength of evidence required to support a claim.
    *   `policy.latency_budget`:  The maximum time allowed for completing the summary.
    *   `policy.research_depth`: How deep to investigate the source materials when writing the summary.
    *   `policy.seed.evidence_threshold`:  The threshold for including information from the initial "seed" or starting point of the analysis.
    *   `policy.seed.max_research_depth`: The maximum depth to research related to the "seed" information.
    *   `policy.seed.max_total_time`: The maximum time to spend on the "seed" information specifically.
*   **Required Outputs:**
    *   **Structured Summary:**  A well-organized summary of the key findings.
    *   **Confidence Score & Evidence IDs:**  An assessment of the summary's accuracy, linked to the supporting evidence.
    *   **Recommendation/Escalation:**  A suggestion for what to do next (e.g., proceed with dissemination, further investigation, escalation to a subject matter expert).

**Suggestions for Expansion and Improvement**

To make this definition more practical and comprehensive, consider adding the following:

1.  **Inputs:** What specific inputs does the Executive Summary Curator receive? This clarifies the scope of their work.  Examples:
    *   Analyzed data reports
    *   Risk assessments
    *   Technical specifications
    *   Previous summaries or briefings
    *   Raw data sets

2.  **Specific Actions/Tasks:**  Detail the specific actions the curator performs.  This will help with automation and training.  Examples:
    *   Reviewing and synthesizing analyzed data.
    *   Identifying key findings and their implications.
    *   Verifying the accuracy and completeness of information.
    *   Writing and editing the executive summary.
    *   Assigning confidence scores based on evidence strength.
    *   Identifying and documenting supporting evidence.
    *   Generating recommendations for next steps.
    *   Flagging issues requiring further investigation.
    *   Ensuring the summary meets readability and accessibility standards.
    *   Adhering to style guides and formatting requirements.

3.  **Decision Points:**  Identify key decision points the curator faces and how they should be resolved.  This promotes consistency and reduces ambiguity.  Examples:
    *   How to handle conflicting information from different sources.
    *   Determining the appropriate level of detail for the summary.
    *   Deciding when to escalate an issue.
    *   How to weigh the importance of different findings.
    *   How to translate technical information into layman's terms.

4.  **Success Metrics:**  How will the curator's performance be measured?  This allows for continuous improvement and accountability. Examples:
    *   Accuracy of the summary (compared to the underlying evidence).
    *   Clarity and readability of the summary.
    *   Timeliness of summary delivery (within the latency budget).
    *   Stakeholder satisfaction with the summary.
    *   Number of errors or omissions.
    *   Adherence to policy guidelines.

5.  **Tools/Resources:**  What tools and resources does the curator need to perform their job? Examples:
    *   Data analysis software
    *   Reporting tools
    *   Evidence management system
    *   Style guides
    *   Templates for executive summaries
    *   Access to subject matter experts

6.  **Clarify Policy Application:**  Provide specific examples of how each policy constraint (e.g., `policy.evidence_threshold`) is applied in practice.  For instance:
    *   `policy.evidence_threshold`: "A finding will only be included if it's supported by at least three independent data sources or one source with a confidence rating of 'High' from the data analysis team."
    *   `policy.latency_budget`: "The executive summary must be completed and delivered to stakeholders within 4 hours of receiving the analyzed data."

7.  **Escalation Criteria:** Define what constitutes an "escalation flag."  Examples:
    *   Significant discrepancies or inconsistencies in the data.
    *   Evidence suggesting a major risk or opportunity that was not previously identified.
    *   Inability to reconcile conflicting information.
    *   Exceeding the `policy.latency_budget`.
    *   Unclear or ambiguous data that requires expert interpretation.

**Revised Example (Incorporating Suggestions)**

Here's an updated example that incorporates some of these suggestions:

```
# Executive Summary Curator :: Executive Summary Curator Primary
Stage: Stakeholder Dissemination

## Objectives
- Maintain evidence alignment and governance compliance.
- Respect orchestration policies while completing assigned actions.

## Policy Context
- policy.evidence_threshold: Findings require at least 3 independent data sources OR one source with a "High" confidence rating.
- policy.latency_budget: Summary must be delivered within 4 hours of receiving analyzed data.
- policy.research_depth: Limit research to direct sources provided, unless contradictions or missing information are discovered.  Document any supplemental research.
- policy.seed.evidence_threshold: Seed information must have at least 2 supporting data points to be included.
- policy.seed.max_research_depth: Seed research is limited to a maximum of 2 levels deep in connected sources.
- policy.seed.max_total_time: No more than 1 hour can be spent researching the seed information.

## Inputs
- Analyzed data reports (JSON format)
- Risk assessment documents (PDF)
- Style guide for executive summaries (Document Link)
- Previous briefing notes (if applicable)

## Actions/Tasks
- Review analyzed data reports and risk assessments to identify key findings.
- Verify accuracy and completeness of information against source documents.
- Write a concise and structured executive summary adhering to the style guide.
- Assign a confidence score (High, Medium, Low) to each finding based on the evidence threshold policy.
- Document the identifiers (IDs) of the supporting evidence for each finding.
- Generate a "Next Steps" recommendation (e.g., "Disseminate," "Further Investigation," "Escalate").
- Flag for escalation if data conflicts, exceeds latency budget, or requires expert interpretation.

## Decision Points
- **Conflicting Data:** Prioritize data from sources with higher confidence ratings. Document the conflicting data and the rationale for prioritization.
- **Level of Detail:** Focus on the top 3-5 most significant findings. Provide sufficient context to understand the implications without overwhelming the reader.
- **Escalation:** Escalate if the executive summary cannot be completed within the latency budget due to data quality issues or complexity.

## Required Outputs
- Structured summary of findings (formatted according to the style guide).
- Confidence score (High, Medium, Low) with supporting evidence identifiers.
- Next-step recommendation (Disseminate, Further Investigation, Escalate).
- Escalation flag (Boolean, True if escalation is required, False otherwise).

## Success Metrics
- Accuracy: Percentage of facts in the summary that are verifiable against the source data. (Target: 95%)
- Timeliness: Completion of the summary within the 4-hour latency budget. (Target: 100%)
- Stakeholder Satisfaction: Measured through a post-dissemination survey. (Target: Average rating of 4 out of 5).

## Tools/Resources
- Data analysis software (Specify software name)
- Reporting template (Link to template)
- Evidence management system (Specify system name)
- Style guide for executive summaries (Link to guide)
- Access to subject matter experts (List of contact information)
```

By elaborating on these aspects, you create a much more robust and actionable definition for the Executive Summary Curator role. This will lead to greater consistency, efficiency, and accuracy in the stakeholder dissemination process. Remember to adapt this example to your specific organizational context and policies.