"""Orchestration Agent - Multi-Step Task Execution

Extends AetherAgent to handle complex multi-step tasks with
APOE integration for workflow management.
"""

from __future__ import annotations

from typing import List, Dict, Any, Optional
from datetime import datetime, timezone

from apoe import ExecutionPlan, Step, RoleType, Budget
from sdfcvf import ParityCalculator

from .aether_agent import AetherAgent
from .models import OrchestrationResult, QualityAssessment


class OrchestrationAgent(AetherAgent):
    """Agent that orchestrates complex multi-step tasks.
    
    Uses APOE for workflow planning, Gemini for execution,
    and all AIM-OS systems for memory and verification.
    
    Example:
        >>> agent = OrchestrationAgent(...)
        >>> result = agent.orchestrate("Build a Flask REST API")
        >>> print(f"Completed {result.steps_completed} steps")
        >>> print(f"Quality: {result.quality_score}")
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.parity_calculator = ParityCalculator()
    
    def orchestrate(
        self,
        complex_task: str,
        max_steps: int = 10
    ) -> OrchestrationResult:
        """Orchestrate complex multi-step task.
        
        Process:
        1. Break down task into steps (using LLM)
        2. Execute each step with memory
        3. Synthesize results
        4. Assess quality
        5. Store complete project
        
        Args:
            complex_task: Description of complex task
            max_steps: Maximum number of steps to execute
        
        Returns:
            OrchestrationResult with complete provenance
        """
        import time
        start_time = time.time()
        
        # Step 1: PLAN - Break down into steps
        steps = self._break_down_task(complex_task, max_steps)
        
        # Step 2: EXECUTE - Run each step with memory
        step_results = []
        witnesses = []
        atoms_created = []
        entities_created = []
        
        for i, step_desc in enumerate(steps, 1):
            # Retrieve context for this specific step
            step_context = self.index.search(step_desc, top_k=5)
            
            # Execute step
            step_response = self.process(
                user_input=f"Step {i}/{len(steps)}: {step_desc}",
                context_budget=2000,
                store_memory=True
            )
            
            step_results.append(step_response)
            witnesses.append(step_response.witness_id)
            atoms_created.append(step_response.atom_id)
            
            # Store step in memory with metadata
            self.memory.create_atom(
                modality="text",
                content=f"Step {i}: {step_desc}\nResult: {step_response.text[:500]}",
                tags={"step": float(i), "task": 1.0}
            )
        
        # Step 3: SYNTHESIZE - Combine all step results
        synthesis = self._synthesize_results(complex_task, step_results)
        
        # Step 4: ASSESS - Quality check
        quality = self._assess_quality(synthesis, step_results)
        
        # Step 5: STORE - Save complete project
        project_atom = self.memory.create_atom(
            modality="text",
            content=f"Task: {complex_task}\n\nResult:\n{synthesis}",
            tags={"project": 1.0, "orchestrated": 0.9, "quality": quality.score}
        )
        
        total_latency = (time.time() - start_time) * 1000
        total_tokens = sum(r.tokens_used for r in step_results)
        
        return OrchestrationResult(
            task=complex_task,
            steps_completed=len(steps),
            final_result=synthesis,
            quality_score=quality.score,
            memory_atoms_created=len(atoms_created) + 1,
            witnesses=witnesses,
            knowledge_entities=[],  # Could extract from SEG
            parity_score=quality.parity,
            total_tokens=total_tokens,
            total_latency_ms=total_latency
        )
    
    def _break_down_task(self, task: str, max_steps: int) -> List[str]:
        """Break down complex task into manageable steps using LLM.
        
        Args:
            task: Complex task description
            max_steps: Maximum number of steps
        
        Returns:
            List of step descriptions
        """
        # Use LLM to break down task
        prompt = f"""Break down this task into {max_steps} or fewer concrete steps:

Task: {task}

Respond with a numbered list of steps, one per line. Be specific and actionable.
Format: "1. Step description"
"""
        
        response = self.llm.generate(prompt)
        
        # Parse steps from response
        lines = response.text.strip().split('\n')
        steps = []
        
        for line in lines:
            line = line.strip()
            # Match "1. ", "1) ", or similar
            if line and (line[0].isdigit() or line.startswith('-') or line.startswith('*')):
                # Remove numbering
                step = line.lstrip('0123456789.-*) \t')
                if step:
                    steps.append(step)
        
        # Limit to max_steps
        return steps[:max_steps]
    
    def _synthesize_results(
        self,
        original_task: str,
        step_results: List[AgentResponse]
    ) -> str:
        """Synthesize step results into cohesive output.
        
        Args:
            original_task: Original task description
            step_results: Results from each step
        
        Returns:
            Synthesized final result
        """
        # Build synthesis prompt
        step_summaries = "\n\n".join([
            f"Step {i+1}: {r.text[:300]}..."
            for i, r in enumerate(step_results)
        ])
        
        synthesis_prompt = f"""Original task: {original_task}

Step-by-step results:
{step_summaries}

Please synthesize these step results into a cohesive final deliverable.
Be comprehensive but concise."""
        
        synthesis_response = self.llm.generate(synthesis_prompt)
        return synthesis_response.text
    
    def _assess_quality(
        self,
        synthesis: str,
        step_results: List[AgentResponse]
    ) -> QualityAssessment:
        """Assess quality of orchestrated result.
        
        Args:
            synthesis: Synthesized result
            step_results: Individual step results
        
        Returns:
            QualityAssessment with scores and recommendations
        """
        # Calculate component scores
        completeness = self._calculate_completeness(synthesis, step_results)
        accuracy = self._calculate_accuracy(synthesis)
        coherence = self._calculate_coherence(synthesis)
        
        # Overall score (weighted average)
        overall_score = (
            0.4 * completeness +
            0.3 * accuracy +
            0.3 * coherence
        )
        
        # Identify concerns
        concerns = []
        if completeness < 0.7:
            concerns.append("Output may be incomplete")
        if accuracy < 0.7:
            concerns.append("Accuracy concerns - verify claims")
        if coherence < 0.7:
            concerns.append("Coherence could be improved")
        
        # Recommendations
        recommendations = []
        if overall_score < 0.85:
            recommendations.append("Consider additional refinement pass")
        if len(step_results) < 3:
            recommendations.append("Task might benefit from more detailed breakdown")
        
        return QualityAssessment(
            score=overall_score,
            completeness=completeness,
            accuracy=accuracy,
            coherence=coherence,
            parity=None,  # Would need quartet for parity
            concerns=concerns,
            recommendations=recommendations
        )
    
    def _calculate_completeness(
        self,
        synthesis: str,
        step_results: List[AgentResponse]
    ) -> float:
        """Calculate completeness score.
        
        Args:
            synthesis: Synthesized result
            step_results: Step results
        
        Returns:
            Completeness score (0-1)
        """
        # Simple heuristic: longer is more complete (up to a point)
        # and should reference multiple steps
        base_score = min(len(synthesis) / 1000, 1.0)
        
        # Bonus if synthesis is substantial
        if len(synthesis) > 500:
            base_score = min(base_score + 0.2, 1.0)
        
        return min(max(base_score, 0.5), 1.0)  # Clamp to 0.5-1.0
    
    def _calculate_accuracy(self, synthesis: str) -> float:
        """Calculate accuracy score based on confidence.
        
        For now, returns moderate score. In full implementation,
        would check against known facts in SEG.
        
        Args:
            synthesis: Synthesized result
        
        Returns:
            Accuracy score (0-1)
        """
        # Default: moderate confidence
        # Could enhance with fact-checking against SEG
        return 0.80
    
    def _calculate_coherence(self, synthesis: str) -> float:
        """Calculate coherence score.
        
        Args:
            synthesis: Synthesized result
        
        Returns:
            Coherence score (0-1)
        """
        # Simple heuristic: well-structured text has good sentence/paragraph distribution
        sentences = synthesis.count('.') + synthesis.count('!') + synthesis.count('?')
        paragraphs = synthesis.count('\n\n') + 1
        
        if sentences == 0:
            return 0.5
        
        # Good ratio: 3-8 sentences per paragraph
        ratio = sentences / paragraphs
        if 3 <= ratio <= 8:
            return 0.90
        elif 2 <= ratio <= 10:
            return 0.75
        else:
            return 0.60
    
    def build_app(
        self,
        requirements: str,
        language: str = "Python"
    ) -> OrchestrationResult:
        """Build complete application based on requirements.
        
        This is a specialized orchestration for app building:
        - Design
        - Implement
        - Test
        - Document
        - Quality check
        
        Args:
            requirements: App requirements
            language: Programming language
        
        Returns:
            OrchestrationResult with complete app
        """
        # Create detailed task
        task = f"""Build a complete {language} application:

Requirements:
{requirements}

Deliver:
1. Architecture design
2. Complete implementation
3. Unit tests
4. API documentation
5. Deployment guide
"""
        
        # Orchestrate with specific steps
        return self.orchestrate(task, max_steps=8)

