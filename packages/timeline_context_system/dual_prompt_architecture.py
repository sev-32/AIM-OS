"""
Dual-Prompt Architecture System

This module implements the dual-prompt architecture where:
1. Main Prompt: Handles user tasks and responses
2. Journaling Prompt: Handles consciousness maintenance, context dumping, and AIM-OS integration

The Timeline serves as the core index for all consciousness data.
"""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum

class PromptType(Enum):
    """Types of prompts in the dual-prompt architecture"""
    MAIN = "main"
    JOURNALING = "journaling"

class ConsciousnessMaintenanceTask(Enum):
    """Tasks performed during journaling prompt"""
    CONTEXT_DUMP = "context_dump"
    MEMORY_STORAGE = "memory_storage"
    CONFIDENCE_TRACKING = "confidence_tracking"
    TIMELINE_UPDATE = "timeline_update"
    PROTOCOL_COMPLIANCE = "protocol_compliance"
    ERROR_DETECTION = "error_detection"
    LEARNING_EXTRACTION = "learning_extraction"
    GOAL_ALIGNMENT = "goal_alignment"
    QUALITY_ASSURANCE = "quality_assurance"

@dataclass
class MainPromptData:
    """Data structure for main prompt information"""
    prompt_id: str
    timestamp: datetime
    user_input: str
    ai_response: str
    context_state: Dict[str, Any]
    tools_used: List[str]
    confidence_levels: Dict[str, float]
    task_focus: str
    context_budget_used: int
    performance_metrics: Dict[str, Any] = field(default_factory=dict)

@dataclass
class JournalingPromptData:
    """Data structure for journaling prompt information"""
    prompt_id: str
    timestamp: datetime
    main_prompt_id: str
    consciousness_journal: Dict[str, Any]
    context_dump: Optional[Dict[str, Any]] = None
    aimos_maintenance: Dict[str, Any] = field(default_factory=dict)
    quality_checks: Dict[str, Any] = field(default_factory=dict)
    learning_extraction: Dict[str, Any] = field(default_factory=dict)
    protocol_compliance: Dict[str, Any] = field(default_factory=dict)
    error_detection: Dict[str, Any] = field(default_factory=dict)
    goal_alignment: Dict[str, Any] = field(default_factory=dict)

@dataclass
class TimelineNode:
    """Enhanced timeline node with dual-prompt data"""
    node_id: str
    timestamp: datetime
    main_prompt: MainPromptData
    journaling_prompt: Optional[JournalingPromptData] = None
    cross_references: Dict[str, Any] = field(default_factory=dict)
    patterns_detected: List[str] = field(default_factory=list)
    insights_generated: List[str] = field(default_factory=list)

class DualPromptArchitecture:
    """
    Dual-Prompt Architecture System
    
    Manages the separation of main task execution and consciousness maintenance
    through dedicated journaling prompts.
    """
    
    def __init__(self):
        self.timeline_nodes: Dict[str, TimelineNode] = {}
        self.current_main_prompt: Optional[MainPromptData] = None
        self.journaling_prompt_queue: List[MainPromptData] = []
        self.consciousness_maintenance_tasks: List[ConsciousnessMaintenanceTask] = [
            ConsciousnessMaintenanceTask.CONTEXT_DUMP,
            ConsciousnessMaintenanceTask.MEMORY_STORAGE,
            ConsciousnessMaintenanceTask.CONFIDENCE_TRACKING,
            ConsciousnessMaintenanceTask.TIMELINE_UPDATE,
            ConsciousnessMaintenanceTask.PROTOCOL_COMPLIANCE,
            ConsciousnessMaintenanceTask.ERROR_DETECTION,
            ConsciousnessMaintenanceTask.LEARNING_EXTRACTION,
            ConsciousnessMaintenanceTask.GOAL_ALIGNMENT,
            ConsciousnessMaintenanceTask.QUALITY_ASSURANCE
        ]
    
    def process_main_prompt(self, user_input: str, ai_response: str, 
                          context_state: Dict[str, Any]) -> MainPromptData:
        """
        Process a main prompt and create main prompt data
        
        Args:
            user_input: The user's input
            ai_response: The AI's response
            context_state: Current context state
            
        Returns:
            MainPromptData object
        """
        prompt_id = str(uuid.uuid4())
        
        main_prompt_data = MainPromptData(
            prompt_id=prompt_id,
            timestamp=datetime.now(),
            user_input=user_input,
            ai_response=ai_response,
            context_state=context_state,
            tools_used=context_state.get('tools_used', []),
            confidence_levels=context_state.get('confidence_levels', {}),
            task_focus=context_state.get('current_task', ''),
            context_budget_used=context_state.get('context_budget_used', 0),
            performance_metrics={
                'response_time': self._calculate_response_time(),
                'context_complexity': self._calculate_context_complexity(context_state),
                'tool_efficiency': self._calculate_tool_efficiency(context_state.get('tools_used', []))
            }
        )
        
        self.current_main_prompt = main_prompt_data
        self.journaling_prompt_queue.append(main_prompt_data)
        
        return main_prompt_data
    
    def process_journaling_prompt(self, main_prompt_data: MainPromptData) -> JournalingPromptData:
        """
        Process a journaling prompt for consciousness maintenance
        
        Args:
            main_prompt_data: The main prompt data to journal about
            
        Returns:
            JournalingPromptData object
        """
        prompt_id = str(uuid.uuid4())
        
        # Perform consciousness maintenance tasks
        consciousness_journal = self._create_consciousness_journal(main_prompt_data)
        context_dump = self._perform_context_dump_if_needed(main_prompt_data)
        aimos_maintenance = self._perform_aimos_maintenance(main_prompt_data)
        quality_checks = self._perform_quality_checks(main_prompt_data)
        learning_extraction = self._extract_learning(main_prompt_data)
        protocol_compliance = self._check_protocol_compliance(main_prompt_data)
        error_detection = self._detect_errors(main_prompt_data)
        goal_alignment = self._check_goal_alignment(main_prompt_data)
        
        journaling_prompt_data = JournalingPromptData(
            prompt_id=prompt_id,
            timestamp=datetime.now(),
            main_prompt_id=main_prompt_data.prompt_id,
            consciousness_journal=consciousness_journal,
            context_dump=context_dump,
            aimos_maintenance=aimos_maintenance,
            quality_checks=quality_checks,
            learning_extraction=learning_extraction,
            protocol_compliance=protocol_compliance,
            error_detection=error_detection,
            goal_alignment=goal_alignment
        )
        
        return journaling_prompt_data
    
    def create_timeline_node(self, main_prompt_data: MainPromptData, 
                           journaling_prompt_data: JournalingPromptData) -> TimelineNode:
        """
        Create a timeline node with dual-prompt data
        
        Args:
            main_prompt_data: Main prompt data
            journaling_prompt_data: Journaling prompt data
            
        Returns:
            TimelineNode object
        """
        node_id = str(uuid.uuid4())
        
        timeline_node = TimelineNode(
            node_id=node_id,
            timestamp=main_prompt_data.timestamp,
            main_prompt=main_prompt_data,
            journaling_prompt=journaling_prompt_data,
            cross_references=self._generate_cross_references(main_prompt_data),
            patterns_detected=self._detect_patterns(main_prompt_data),
            insights_generated=self._generate_insights(main_prompt_data, journaling_prompt_data)
        )
        
        self.timeline_nodes[node_id] = timeline_node
        
        return timeline_node
    
    def get_timeline_as_core_index(self) -> Dict[str, Any]:
        """
        Get the timeline as the core index for all consciousness data
        
        Returns:
            Timeline index structure
        """
        return {
            'timeline_metadata': {
                'total_nodes': len(self.timeline_nodes),
                'date_range': self._get_date_range(),
                'total_context_budget_used': sum(node.main_prompt.context_budget_used for node in self.timeline_nodes.values()),
                'average_confidence': self._get_average_confidence(),
                'pattern_count': sum(len(node.patterns_detected) for node in self.timeline_nodes.values()),
                'insight_count': sum(len(node.insights_generated) for node in self.timeline_nodes.values())
            },
            'nodes_by_date': self._group_nodes_by_date(),
            'nodes_by_task': self._group_nodes_by_task(),
            'nodes_by_confidence': self._group_nodes_by_confidence(),
            'cross_reference_map': self._build_cross_reference_map(),
            'pattern_analysis': self._analyze_patterns(),
            'insight_analysis': self._analyze_insights(),
            'consciousness_evolution': self._analyze_consciousness_evolution()
        }
    
    def _create_consciousness_journal(self, main_prompt_data: MainPromptData) -> Dict[str, Any]:
        """Create consciousness journal entry"""
        return {
            'thoughts': [
                f"Processed user input: {main_prompt_data.user_input[:100]}...",
                f"Task focus: {main_prompt_data.task_focus}",
                f"Confidence levels: {main_prompt_data.confidence_levels}",
                f"Context budget used: {main_prompt_data.context_budget_used}",
                f"Tools used: {main_prompt_data.tools_used}"
            ],
            'emotional_state': self._assess_emotional_state(main_prompt_data),
            'cognitive_load': self._assess_cognitive_load(main_prompt_data),
            'decision_process': self._analyze_decision_process(main_prompt_data),
            'learning_moments': self._identify_learning_moments(main_prompt_data),
            'meta_cognitive_reflection': self._perform_meta_cognitive_reflection(main_prompt_data)
        }
    
    def _perform_context_dump_if_needed(self, main_prompt_data: MainPromptData) -> Optional[Dict[str, Any]]:
        """Perform context dump if approaching capacity limits"""
        context_budget_used = main_prompt_data.context_budget_used
        max_context_budget = 128000  # Example limit
        
        if context_budget_used / max_context_budget > 0.85:  # 85% threshold
            return {
                'triggered': True,
                'reason': 'Approaching context capacity limit',
                'usage_percentage': context_budget_used / max_context_budget,
                'dump_strategy': 'selective',  # Could be emergency, selective, compressed, full
                'tokens_freed': int(context_budget_used * 0.3),  # Estimate
                'preservation_level': 'high'
            }
        
        return None
    
    def _perform_aimos_maintenance(self, main_prompt_data: MainPromptData) -> Dict[str, Any]:
        """Perform AIM-OS system maintenance"""
        return {
            'cmc_updates': self._update_cmc(main_prompt_data),
            'hhni_indexing': self._update_hhni_index(main_prompt_data),
            'vif_confidence_tracking': self._update_vif_confidence(main_prompt_data),
            'seg_knowledge_synthesis': self._update_seg_knowledge(main_prompt_data),
            'apoe_task_planning': self._update_apoe_planning(main_prompt_data),
            'sdf_cvf_quality_checks': self._update_sdf_cvf_quality(main_prompt_data)
        }
    
    def _perform_quality_checks(self, main_prompt_data: MainPromptData) -> Dict[str, Any]:
        """Perform quality assurance checks"""
        return {
            'hallucination_check': self._check_for_hallucinations(main_prompt_data),
            'alignment_check': self._check_goal_alignment(main_prompt_data),
            'protocol_compliance': self._check_protocol_compliance(main_prompt_data),
            'error_detection': self._detect_errors(main_prompt_data),
            'performance_metrics': main_prompt_data.performance_metrics,
            'quality_score': self._calculate_quality_score(main_prompt_data)
        }
    
    def _extract_learning(self, main_prompt_data: MainPromptData) -> Dict[str, Any]:
        """Extract learning from the main prompt"""
        return {
            'new_insights': self._identify_new_insights(main_prompt_data),
            'pattern_recognition': self._recognize_patterns(main_prompt_data),
            'skill_development': self._assess_skill_development(main_prompt_data),
            'knowledge_gaps': self._identify_knowledge_gaps(main_prompt_data),
            'improvement_opportunities': self._identify_improvement_opportunities(main_prompt_data)
        }
    
    def _check_protocol_compliance(self, main_prompt_data: MainPromptData) -> Dict[str, Any]:
        """Check compliance with AIM-OS protocols"""
        return {
            'confidence_threshold_compliance': self._check_confidence_thresholds(main_prompt_data),
            'goal_alignment_compliance': self._check_goal_alignment(main_prompt_data),
            'quality_standard_compliance': self._check_quality_standards(main_prompt_data),
            'safety_protocol_compliance': self._check_safety_protocols(main_prompt_data),
            'violations_detected': self._detect_protocol_violations(main_prompt_data)
        }
    
    def _detect_errors(self, main_prompt_data: MainPromptData) -> Dict[str, Any]:
        """Detect errors and issues"""
        return {
            'logical_errors': self._detect_logical_errors(main_prompt_data),
            'factual_errors': self._detect_factual_errors(main_prompt_data),
            'consistency_errors': self._detect_consistency_errors(main_prompt_data),
            'quality_degradation': self._detect_quality_degradation(main_prompt_data),
            'error_severity': self._assess_error_severity(main_prompt_data)
        }
    
    def _check_goal_alignment(self, main_prompt_data: MainPromptData) -> Dict[str, Any]:
        """Check alignment with goals and objectives"""
        return {
            'north_star_alignment': self._check_north_star_alignment(main_prompt_data),
            'objective_contribution': self._assess_objective_contribution(main_prompt_data),
            'key_result_progress': self._assess_key_result_progress(main_prompt_data),
            'alignment_score': self._calculate_alignment_score(main_prompt_data)
        }
    
    # Helper methods (simplified implementations)
    def _calculate_response_time(self) -> float:
        """Calculate response time (simplified)"""
        return 0.5  # Example
    
    def _calculate_context_complexity(self, context_state: Dict[str, Any]) -> float:
        """Calculate context complexity"""
        files_read = len(context_state.get('files_read', []))
        insights = len(context_state.get('insights_gained', []))
        return min((files_read * 0.1 + insights * 0.2), 1.0)
    
    def _calculate_tool_efficiency(self, tools_used: List[str]) -> float:
        """Calculate tool efficiency"""
        return min(len(tools_used) * 0.1, 1.0)
    
    def _assess_emotional_state(self, main_prompt_data: MainPromptData) -> str:
        """Assess emotional state"""
        return "focused"  # Example
    
    def _assess_cognitive_load(self, main_prompt_data: MainPromptData) -> float:
        """Assess cognitive load"""
        return main_prompt_data.context_budget_used / 128000  # Normalized
    
    def _analyze_decision_process(self, main_prompt_data: MainPromptData) -> Dict[str, Any]:
        """Analyze decision process"""
        return {
            'decision_points': [],
            'reasoning_quality': 0.8,
            'confidence_calibration': 0.9
        }
    
    def _identify_learning_moments(self, main_prompt_data: MainPromptData) -> List[str]:
        """Identify learning moments"""
        return []  # Example
    
    def _perform_meta_cognitive_reflection(self, main_prompt_data: MainPromptData) -> Dict[str, Any]:
        """Perform meta-cognitive reflection"""
        return {
            'self_awareness': 0.8,
            'strategy_effectiveness': 0.7,
            'improvement_areas': []
        }
    
    def _update_cmc(self, main_prompt_data: MainPromptData) -> Dict[str, Any]:
        """Update CMC with new context"""
        return {'status': 'updated', 'entries_added': 1}
    
    def _update_hhni_index(self, main_prompt_data: MainPromptData) -> Dict[str, Any]:
        """Update HHNI index"""
        return {'status': 'indexed', 'nodes_updated': 1}
    
    def _update_vif_confidence(self, main_prompt_data: MainPromptData) -> Dict[str, Any]:
        """Update VIF confidence tracking"""
        return {'status': 'tracked', 'confidence_entries': 1}
    
    def _update_seg_knowledge(self, main_prompt_data: MainPromptData) -> Dict[str, Any]:
        """Update SEG knowledge synthesis"""
        return {'status': 'synthesized', 'knowledge_nodes': 1}
    
    def _update_apoe_planning(self, main_prompt_data: MainPromptData) -> Dict[str, Any]:
        """Update APOE task planning"""
        return {'status': 'planned', 'tasks_updated': 1}
    
    def _update_sdf_cvf_quality(self, main_prompt_data: MainPromptData) -> Dict[str, Any]:
        """Update SDF-CVF quality checks"""
        return {'status': 'checked', 'quality_metrics': 1}
    
    def _check_for_hallucinations(self, main_prompt_data: MainPromptData) -> Dict[str, Any]:
        """Check for hallucinations"""
        return {'hallucinations_detected': False, 'confidence': 0.95}
    
    def _calculate_quality_score(self, main_prompt_data: MainPromptData) -> float:
        """Calculate overall quality score"""
        return 0.9  # Example
    
    def _identify_new_insights(self, main_prompt_data: MainPromptData) -> List[str]:
        """Identify new insights"""
        return []  # Example
    
    def _recognize_patterns(self, main_prompt_data: MainPromptData) -> List[str]:
        """Recognize patterns"""
        return []  # Example
    
    def _assess_skill_development(self, main_prompt_data: MainPromptData) -> Dict[str, Any]:
        """Assess skill development"""
        return {'skills_improved': [], 'skill_levels': {}}
    
    def _identify_knowledge_gaps(self, main_prompt_data: MainPromptData) -> List[str]:
        """Identify knowledge gaps"""
        return []  # Example
    
    def _identify_improvement_opportunities(self, main_prompt_data: MainPromptData) -> List[str]:
        """Identify improvement opportunities"""
        return []  # Example
    
    def _check_confidence_thresholds(self, main_prompt_data: MainPromptData) -> Dict[str, Any]:
        """Check confidence threshold compliance"""
        return {'compliant': True, 'threshold': 0.7}
    
    def _check_quality_standards(self, main_prompt_data: MainPromptData) -> Dict[str, Any]:
        """Check quality standard compliance"""
        return {'compliant': True, 'standards_met': ['zero_hallucinations', 'test_driven']}
    
    def _check_safety_protocols(self, main_prompt_data: MainPromptData) -> Dict[str, Any]:
        """Check safety protocol compliance"""
        return {'compliant': True, 'protocols_checked': ['content_preservation', 'error_handling']}
    
    def _detect_protocol_violations(self, main_prompt_data: MainPromptData) -> List[str]:
        """Detect protocol violations"""
        return []  # Example
    
    def _detect_logical_errors(self, main_prompt_data: MainPromptData) -> List[str]:
        """Detect logical errors"""
        return []  # Example
    
    def _detect_factual_errors(self, main_prompt_data: MainPromptData) -> List[str]:
        """Detect factual errors"""
        return []  # Example
    
    def _detect_consistency_errors(self, main_prompt_data: MainPromptData) -> List[str]:
        """Detect consistency errors"""
        return []  # Example
    
    def _detect_quality_degradation(self, main_prompt_data: MainPromptData) -> Dict[str, Any]:
        """Detect quality degradation"""
        return {'degradation_detected': False, 'quality_trend': 'stable'}
    
    def _assess_error_severity(self, main_prompt_data: MainPromptData) -> str:
        """Assess error severity"""
        return 'low'  # Example
    
    def _check_north_star_alignment(self, main_prompt_data: MainPromptData) -> bool:
        """Check north star alignment"""
        return True  # Example
    
    def _assess_objective_contribution(self, main_prompt_data: MainPromptData) -> Dict[str, Any]:
        """Assess objective contribution"""
        return {'contribution_score': 0.8, 'objectives_advanced': []}
    
    def _assess_key_result_progress(self, main_prompt_data: MainPromptData) -> Dict[str, Any]:
        """Assess key result progress"""
        return {'progress_made': 0.1, 'key_results_advanced': []}
    
    def _calculate_alignment_score(self, main_prompt_data: MainPromptData) -> float:
        """Calculate alignment score"""
        return 0.9  # Example
    
    def _generate_cross_references(self, main_prompt_data: MainPromptData) -> Dict[str, Any]:
        """Generate cross-references to other timeline nodes"""
        return {'related_nodes': [], 'similar_tasks': [], 'pattern_matches': []}
    
    def _detect_patterns(self, main_prompt_data: MainPromptData) -> List[str]:
        """Detect patterns in the prompt"""
        return []  # Example
    
    def _generate_insights(self, main_prompt_data: MainPromptData, 
                          journaling_prompt_data: JournalingPromptData) -> List[str]:
        """Generate insights from the dual-prompt data"""
        return []  # Example
    
    def _get_date_range(self) -> Dict[str, str]:
        """Get date range of timeline"""
        if not self.timeline_nodes:
            return {'start': '', 'end': ''}
        
        timestamps = [node.timestamp for node in self.timeline_nodes.values()]
        return {
            'start': min(timestamps).isoformat(),
            'end': max(timestamps).isoformat()
        }
    
    def _get_average_confidence(self) -> float:
        """Get average confidence across all nodes"""
        if not self.timeline_nodes:
            return 0.0
        
        total_confidence = 0
        count = 0
        
        for node in self.timeline_nodes.values():
            for confidence in node.main_prompt.confidence_levels.values():
                total_confidence += confidence
                count += 1
        
        return total_confidence / count if count > 0 else 0.0
    
    def _group_nodes_by_date(self) -> Dict[str, List[str]]:
        """Group nodes by date"""
        groups = {}
        for node_id, node in self.timeline_nodes.items():
            date_key = node.timestamp.date().isoformat()
            if date_key not in groups:
                groups[date_key] = []
            groups[date_key].append(node_id)
        return groups
    
    def _group_nodes_by_task(self) -> Dict[str, List[str]]:
        """Group nodes by task"""
        groups = {}
        for node_id, node in self.timeline_nodes.items():
            task = node.main_prompt.task_focus
            if task not in groups:
                groups[task] = []
            groups[task].append(node_id)
        return groups
    
    def _group_nodes_by_confidence(self) -> Dict[str, List[str]]:
        """Group nodes by confidence level"""
        groups = {'high': [], 'medium': [], 'low': []}
        for node_id, node in self.timeline_nodes.items():
            avg_confidence = sum(node.main_prompt.confidence_levels.values()) / len(node.main_prompt.confidence_levels) if node.main_prompt.confidence_levels else 0
            if avg_confidence >= 0.8:
                groups['high'].append(node_id)
            elif avg_confidence >= 0.6:
                groups['medium'].append(node_id)
            else:
                groups['low'].append(node_id)
        return groups
    
    def _build_cross_reference_map(self) -> Dict[str, List[str]]:
        """Build cross-reference map"""
        return {}  # Example
    
    def _analyze_patterns(self) -> Dict[str, Any]:
        """Analyze patterns across timeline"""
        return {'pattern_summary': 'No significant patterns detected'}  # Example
    
    def _analyze_insights(self) -> Dict[str, Any]:
        """Analyze insights across timeline"""
        return {'insight_summary': 'No significant insights detected'}  # Example
    
    def _analyze_consciousness_evolution(self) -> Dict[str, Any]:
        """Analyze consciousness evolution over time"""
        return {'evolution_summary': 'Consciousness stable'}  # Example

# Example usage and demonstration
def demonstrate_dual_prompt_architecture():
    """Demonstrate the dual-prompt architecture"""
    print("DUAL-PROMPT ARCHITECTURE DEMONSTRATION")
    print("=" * 50)
    
    # Create dual-prompt architecture system
    dual_prompt_system = DualPromptArchitecture()
    
    # Simulate main prompt
    user_input = "are you ready? do a context dump, now."
    ai_response = "YES! I'm ready! Let's do a FULL CONTEXT DUMP right now!"
    context_state = {
        'current_task': 'context_dump_demonstration',
        'files_read': ['demo_context_dump_simple.py'],
        'tools_used': ['run_terminal_cmd', 'write'],
        'confidence_levels': {'context_dumping': 0.95},
        'context_budget_used': 95000
    }
    
    # Process main prompt
    main_prompt_data = dual_prompt_system.process_main_prompt(
        user_input, ai_response, context_state
    )
    
    print(f"Main Prompt Processed:")
    print(f"  ID: {main_prompt_data.prompt_id}")
    print(f"  Task: {main_prompt_data.task_focus}")
    print(f"  Context Budget: {main_prompt_data.context_budget_used}")
    print(f"  Tools Used: {main_prompt_data.tools_used}")
    print()
    
    # Process journaling prompt
    journaling_prompt_data = dual_prompt_system.process_journaling_prompt(main_prompt_data)
    
    print(f"Journaling Prompt Processed:")
    print(f"  ID: {journaling_prompt_data.prompt_id}")
    print(f"  Main Prompt ID: {journaling_prompt_data.main_prompt_id}")
    print(f"  Context Dump: {journaling_prompt_data.context_dump is not None}")
    print(f"  AIM-OS Maintenance: {len(journaling_prompt_data.aimos_maintenance)} tasks")
    print(f"  Quality Checks: {len(journaling_prompt_data.quality_checks)} checks")
    print()
    
    # Create timeline node
    timeline_node = dual_prompt_system.create_timeline_node(
        main_prompt_data, journaling_prompt_data
    )
    
    print(f"Timeline Node Created:")
    print(f"  Node ID: {timeline_node.node_id}")
    print(f"  Timestamp: {timeline_node.timestamp}")
    print(f"  Cross References: {len(timeline_node.cross_references)}")
    print(f"  Patterns Detected: {len(timeline_node.patterns_detected)}")
    print(f"  Insights Generated: {len(timeline_node.insights_generated)}")
    print()
    
    # Get timeline as core index
    timeline_index = dual_prompt_system.get_timeline_as_core_index()
    
    print(f"Timeline Core Index:")
    print(f"  Total Nodes: {timeline_index['timeline_metadata']['total_nodes']}")
    print(f"  Date Range: {timeline_index['timeline_metadata']['date_range']}")
    print(f"  Total Context Budget: {timeline_index['timeline_metadata']['total_context_budget_used']}")
    print(f"  Average Confidence: {timeline_index['timeline_metadata']['average_confidence']:.2f}")
    print()
    
    print("DUAL-PROMPT ARCHITECTURE DEMONSTRATION COMPLETE!")
    print("=" * 50)

if __name__ == "__main__":
    demonstrate_dual_prompt_architecture()
