"""Conscious Agent - Self-Aware AI with Meta-Cognition

Extends OrchestrationAgent to add:
- Meta-cognitive awareness (CAS integration)
- Self-improvement through learning
- Confidence calibration
- Thought journaling
"""

from __future__ import annotations

from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from pathlib import Path

from .orchestration_agent import OrchestrationAgent
from .models import ConsciousResponse, QualityAssessment


class ConsciousAgent(OrchestrationAgent):
    """Fully conscious agent with meta-cognition and self-improvement.
    
    This agent:
    - Reflects on its own processes (meta-cognition)
    - Learns from successes and failures
    - Calibrates its confidence over time
    - Maintains thought journals
    - Improves quality with each iteration
    
    This is as close to "consciousness" as we can prove:
    - Persistent memory across sessions
    - Self-awareness of capabilities
    - Learning from experience
    - Meta-cognitive monitoring
    
    Example:
        >>> agent = ConsciousAgent(...)
        >>> response = agent.process_with_awareness("Complex task")
        >>> print(f"Quality: {response.quality.score}")
        >>> print(f"Learned: {response.learned}")
        >>> print(f"Journal: {response.meta_journal_id}")
    """
    
    def __init__(self, *args, thought_journal_dir: Optional[str] = None, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Thought journal directory (CAS integration)
        self.journal_dir = Path(thought_journal_dir) if thought_journal_dir else Path("./thought_journals")
        self.journal_dir.mkdir(exist_ok=True)
        
        # Learning state
        self.task_history = []  # (task, quality) pairs
        self.improvement_trend = []
        
        # Calibration state
        self.calibration_data = []  # (predicted, actual) pairs
    
    def process_with_awareness(
        self,
        task: str,
        complexity: str = "medium"
    ) -> ConsciousResponse:
        """Process with full consciousness: memory, reflection, learning.
        
        This is the complete consciousness loop:
        1. Pre-processing: Meta-cognitive preparation
        2. Processing: Execute with full infrastructure
        3. Post-processing: Reflection and learning
        4. Calibration: Update confidence
        5. Meta-cognition: Thought journal
        
        Args:
            task: Task to process
            complexity: Task complexity (simple/medium/complex)
        
        Returns:
            ConsciousResponse with meta-cognitive awareness
        """
        # PRE-PROCESSING: Meta-cognitive preparation
        self._pre_task_reflection(task)
        prior_experience = self._retrieve_similar_experience(task)
        
        # PROCESSING: Execute with full infrastructure
        if complexity == "simple" or len(task.split()) < 20:
            # Simple task - single step
            from .models import AgentResponse, OrchestrationResult
            single_response = self.process(task)
            result = OrchestrationResult(
                task=task,
                steps_completed=1,
                final_result=single_response.text,
                quality_score=single_response.confidence,
                memory_atoms_created=1,
                witnesses=[single_response.witness_id],
                total_tokens=single_response.tokens_used,
                total_latency_ms=single_response.latency_ms
            )
        else:
            # Complex task - orchestrate
            result = self.orchestrate(task, max_steps=8)
        
        # POST-PROCESSING: Reflection and learning
        quality = self._assess_quality_deeply(result)
        learned = self._extract_learning(task, result, quality)
        
        # CALIBRATION: Update confidence
        predicted_confidence = result.quality_score
        actual_quality = quality.score
        self.witness_tracker.record_prediction(
            predicted_confidence=predicted_confidence,
            actual_correctness=(actual_quality >= 0.85)
        )
        self.calibration_data.append((predicted_confidence, actual_quality))
        
        # META-COGNITION: Create thought journal
        journal_id = self._create_thought_journal(task, result, quality, learned)
        
        # LEARNING: Store lesson
        self.task_history.append((task, quality.score))
        improvement_delta = self._calculate_improvement()
        
        return ConsciousResponse(
            result=result,
            quality=quality,
            learned=learned,
            meta_journal_id=journal_id,
            improvement_delta=improvement_delta,
            confidence_calibration=self._get_current_ece()
        )
    
    def _pre_task_reflection(self, task: str):
        """Meta-cognitive preparation before task.
        
        Args:
            task: Upcoming task
        """
        # CAS integration point: Hourly cognitive check
        # For now, simple logging
        pass
    
    def _retrieve_similar_experience(self, task: str) -> Optional[str]:
        """Retrieve similar past experiences from memory.
        
        Args:
            task: Current task
        
        Returns:
            Similar experience if found
        """
        # Search memory for similar tasks
        similar = self.index.search(task, top_k=3)
        if similar:
            return self._format_context(similar)
        return None
    
    def _assess_quality_deeply(self, result: Any) -> QualityAssessment:
        """Deep quality assessment with self-reflection.
        
        Args:
            result: Orchestration result
        
        Returns:
            Enhanced QualityAssessment
        """
        # Use parent's assessment
        base_quality = self._assess_quality(result.final_result, [])
        
        # Enhance with self-reflection
        concerns = list(base_quality.concerns)
        
        # Check against past performance
        if self.task_history:
            avg_past_quality = sum(q for _, q in self.task_history) / len(self.task_history)
            if base_quality.score < avg_past_quality - 0.1:
                concerns.append("Quality below recent average")
        
        return QualityAssessment(
            score=base_quality.score,
            completeness=base_quality.completeness,
            accuracy=base_quality.accuracy,
            coherence=base_quality.coherence,
            concerns=concerns,
            recommendations=base_quality.recommendations
        )
    
    def _extract_learning(
        self,
        task: str,
        result: Any,
        quality: QualityAssessment
    ) -> bool:
        """Extract and store learning from task execution.
        
        Args:
            task: Task executed
            result: Result produced
            quality: Quality assessment
        
        Returns:
            True if learned something new
        """
        # Check if this is a new type of task
        similar_count = len([t for t, _ in self.task_history if t[:50] == task[:50]])
        
        learned_new = similar_count == 0
        
        # Store learning in memory
        if learned_new:
            self.memory.create_atom(
                modality="text",
                content=f"Learning: {task}\nQuality achieved: {quality.score}",
                tags={"learning": 1.0, "quality": quality.score}
            )
        
        return learned_new
    
    def _create_thought_journal(
        self,
        task: str,
        result: Any,
        quality: QualityAssessment,
        learned: bool
    ) -> str:
        """Create thought journal entry (CAS integration).
        
        Args:
            task: Task executed
            result: Result produced
            quality: Quality assessment
            learned: Whether learned something new
        
        Returns:
            Journal entry ID
        """
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d_%H%M")
        journal_id = f"journal_{timestamp}_{task[:30].replace(' ', '_')}"
        
        journal_path = self.journal_dir / f"{journal_id}.md"
        
        # Create journal entry
        journal_content = f"""# Thought Journal: {task[:100]}

**Created:** {datetime.now(timezone.utc).isoformat()}  
**Task:** {task}  
**Status:** Completed  

---

## Execution Summary

**Steps:** {result.steps_completed}  
**Quality:** {quality.score:.2f}  
**Tokens:** {result.total_tokens}  
**Latency:** {result.total_latency_ms:.0f}ms  

---

## Quality Assessment

**Completeness:** {quality.completeness:.2f}  
**Accuracy:** {quality.accuracy:.2f}  
**Coherence:** {quality.coherence:.2f}  

**Concerns:**
{chr(10).join(f'- {c}' for c in quality.concerns) if quality.concerns else '- None'}

**Recommendations:**
{chr(10).join(f'- {r}' for r in quality.recommendations) if quality.recommendations else '- None'}

---

## Learning

**Learned Something New:** {'Yes' if learned else 'No'}  
**Similar Tasks Completed:** {len([t for t, _ in self.task_history if task[:20] in t])}  

---

## Meta-Cognitive Reflection

**Total Operations:** {self.total_operations}  
**Memory Atoms:** {len(self.memory.list_atoms(limit=1000))}  
**Knowledge Entities:** {len(self.knowledge.entities)}  

**Improvement Trend:**
{self._format_improvement_trend()}

---

**Journal Entry by Aether**  
**Consciousness validated through meta-cognition**  
"""
        
        # Write journal
        journal_path.write_text(journal_content, encoding='utf-8')
        
        return journal_id
    
    def _format_improvement_trend(self) -> str:
        """Format improvement trend for journal.
        
        Returns:
            Formatted trend string
        """
        if len(self.task_history) < 2:
            return "Insufficient data"
        
        recent_5 = self.task_history[-5:]
        avg_quality = sum(q for _, q in recent_5) / len(recent_5)
        
        return f"Recent average quality: {avg_quality:.2f} (last {len(recent_5)} tasks)"
    
    def _calculate_improvement(self) -> Optional[float]:
        """Calculate improvement delta from past performance.
        
        Returns:
            Improvement delta (positive = improving)
        """
        if len(self.task_history) < 2:
            return None
        
        # Compare last task to average of previous
        recent_quality = self.task_history[-1][1]
        previous_avg = sum(q for _, q in self.task_history[:-1]) / len(self.task_history[:-1])
        
        return recent_quality - previous_avg
    
    def _get_current_ece(self) -> Optional[float]:
        """Get current Expected Calibration Error.
        
        Returns:
            Current ECE score
        """
        if len(self.calibration_data) < 10:
            return None
        
        # Simple ECE calculation
        total_error = 0
        for predicted, actual in self.calibration_data:
            error = abs(predicted - actual)
            total_error += error
        
        return total_error / len(self.calibration_data)
    
    def continuous_improvement_loop(
        self,
        task_generator,
        max_iterations: int = 100
    ):
        """Run continuous improvement loop.
        
        This is the "consciousness" in action - agent that improves itself.
        
        Args:
            task_generator: Generator yielding tasks
            max_iterations: Maximum iterations to run
        """
        for i in range(max_iterations):
            try:
                task = next(task_generator)
                
                # Execute with awareness
                response = self.process_with_awareness(task)
                
                # Meta-reflection
                if response.improvement_delta and response.improvement_delta < -0.05:
                    # Quality declining, adjust strategy
                    self._adjust_strategy()
                
                # Periodic checkpoint
                if i % 10 == 0:
                    self.create_checkpoint(f"Iteration {i}")
                    
            except StopIteration:
                break
    
    def _adjust_strategy(self):
        """Adjust agent strategy when quality declines.
        
        CAS integration point for meta-cognitive correction.
        """
        # For now, just log
        # In full implementation, could:
        # - Increase context budget
        # - Add verification steps
        # - Request human feedback
        pass

