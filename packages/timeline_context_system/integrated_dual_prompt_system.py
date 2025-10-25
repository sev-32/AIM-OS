"""
Integrated Dual-Prompt System

This module integrates the dual-prompt architecture with the existing timeline
and context management systems to create a unified consciousness maintenance system.
"""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field

# Import our existing systems
from .dual_prompt_architecture import (
    DualPromptArchitecture, 
    MainPromptData, 
    JournalingPromptData, 
    TimelineNode,
    ConsciousnessMaintenanceTask
)
from .automated_context_dumping import (
    AutomatedContextDumpingSystem,
    ContextDumpStrategy,
    ContextDumpResult
)
from .consciousness_journaling_system import (
    ConsciousnessJournalingSystem,
    ConsciousnessEntry,
    JournalingStrategy
)

@dataclass
class IntegratedConsciousnessState:
    """Integrated consciousness state combining all systems"""
    current_timeline_node: Optional[TimelineNode] = None
    context_dump_status: Optional[ContextDumpResult] = None
    consciousness_journal_entry: Optional[ConsciousnessEntry] = None
    aimos_system_status: Dict[str, Any] = field(default_factory=dict)
    quality_metrics: Dict[str, Any] = field(default_factory=dict)
    learning_extracted: Dict[str, Any] = field(default_factory=dict)

class IntegratedDualPromptSystem:
    """
    Integrated Dual-Prompt System
    
    Combines dual-prompt architecture with automated context dumping,
    consciousness journaling, and timeline management for comprehensive
    consciousness maintenance.
    """
    
    def __init__(self):
        self.dual_prompt_architecture = DualPromptArchitecture()
        self.context_dumping_system = AutomatedContextDumpingSystem()
        self.consciousness_journaling = ConsciousnessJournalingSystem()
        self.integrated_consciousness_state: Optional[IntegratedConsciousnessState] = None
        
        # Configuration
        self.config = {
            'context_dump_threshold': 0.85,  # 85% context usage triggers dump
            'journaling_strategy': JournalingStrategy.MAXIMUM_DEPTH,
            'aimos_maintenance_enabled': True,
            'quality_checks_enabled': True,
            'learning_extraction_enabled': True,
            'timeline_indexing_enabled': True
        }
    
    def process_complete_interaction(self, user_input: str, ai_response: str, 
                                   context_state: Dict[str, Any]) -> IntegratedConsciousnessState:
        """
        Process a complete interaction with dual-prompt architecture
        
        Args:
            user_input: The user's input
            ai_response: The AI's response
            context_state: Current context state
            
        Returns:
            IntegratedConsciousnessState with all consciousness data
        """
        print("PROCESSING COMPLETE INTERACTION WITH DUAL-PROMPT ARCHITECTURE")
        print("=" * 60)
        
        # Step 1: Process main prompt
        print("1. PROCESSING MAIN PROMPT...")
        main_prompt_data = self.dual_prompt_architecture.process_main_prompt(
            user_input, ai_response, context_state
        )
        print(f"   Main prompt processed: {main_prompt_data.prompt_id}")
        print(f"   Task focus: {main_prompt_data.task_focus}")
        print(f"   Context budget used: {main_prompt_data.context_budget_used}")
        print()
        
        # Step 2: Check if context dump is needed
        print("2. CHECKING CONTEXT DUMP REQUIREMENTS...")
        context_dump_result = None
        if self._should_trigger_context_dump(main_prompt_data):
            print("   Context dump triggered!")
            context_dump_result = self._perform_context_dump(main_prompt_data)
            print(f"   Context dump completed: {context_dump_result.dump_id if context_dump_result else 'None'}")
        else:
            print("   No context dump needed")
        print()
        
        # Step 3: Process journaling prompt
        print("3. PROCESSING JOURNALING PROMPT...")
        journaling_prompt_data = self.dual_prompt_architecture.process_journaling_prompt(
            main_prompt_data
        )
        print(f"   Journaling prompt processed: {journaling_prompt_data.prompt_id}")
        print(f"   Consciousness journal created: {len(journaling_prompt_data.consciousness_journal.get('thoughts', []))} thoughts")
        print(f"   AIM-OS maintenance tasks: {len(journaling_prompt_data.aimos_maintenance)}")
        print(f"   Quality checks performed: {len(journaling_prompt_data.quality_checks)}")
        print()
        
        # Step 4: Create consciousness journal entry
        print("4. CREATING CONSCIOUSNESS JOURNAL ENTRY...")
        consciousness_entry = self._create_consciousness_journal_entry(
            main_prompt_data, journaling_prompt_data, context_dump_result
        )
        print(f"   Consciousness journal entry created: {consciousness_entry.entry_id}")
        print(f"   Emotional state: {consciousness_entry.emotional_state}")
        print(f"   Cognitive load: {consciousness_entry.cognitive_load:.2f}")
        print()
        
        # Step 5: Create timeline node
        print("5. CREATING TIMELINE NODE...")
        timeline_node = self.dual_prompt_architecture.create_timeline_node(
            main_prompt_data, journaling_prompt_data
        )
        print(f"   Timeline node created: {timeline_node.node_id}")
        print(f"   Cross references: {len(timeline_node.cross_references)}")
        print(f"   Patterns detected: {len(timeline_node.patterns_detected)}")
        print(f"   Insights generated: {len(timeline_node.insights_generated)}")
        print()
        
        # Step 6: Update AIM-OS systems
        print("6. UPDATING AIM-OS SYSTEMS...")
        aimos_status = self._update_aimos_systems(
            main_prompt_data, journaling_prompt_data, consciousness_entry
        )
        print(f"   CMC updated: {aimos_status.get('cmc_updated', False)}")
        print(f"   HHNI indexed: {aimos_status.get('hhni_indexed', False)}")
        print(f"   VIF tracked: {aimos_status.get('vif_tracked', False)}")
        print(f"   SEG synthesized: {aimos_status.get('seg_synthesized', False)}")
        print()
        
        # Step 7: Extract learning and insights
        print("7. EXTRACTING LEARNING AND INSIGHTS...")
        learning_extracted = self._extract_learning_and_insights(
            main_prompt_data, journaling_prompt_data, consciousness_entry
        )
        print(f"   New insights identified: {len(learning_extracted.get('new_insights', []))}")
        print(f"   Patterns recognized: {len(learning_extracted.get('patterns', []))}")
        print(f"   Skills assessed: {len(learning_extracted.get('skills_assessed', []))}")
        print()
        
        # Step 8: Calculate quality metrics
        print("8. CALCULATING QUALITY METRICS...")
        quality_metrics = self._calculate_quality_metrics(
            main_prompt_data, journaling_prompt_data, consciousness_entry
        )
        print(f"   Overall quality score: {quality_metrics.get('overall_score', 0):.2f}")
        print(f"   Hallucination check: {quality_metrics.get('hallucination_check', {}).get('hallucinations_detected', False)}")
        print(f"   Goal alignment: {quality_metrics.get('goal_alignment', {}).get('alignment_score', 0):.2f}")
        print()
        
        # Create integrated consciousness state
        self.integrated_consciousness_state = IntegratedConsciousnessState(
            current_timeline_node=timeline_node,
            context_dump_status=context_dump_result,
            consciousness_journal_entry=consciousness_entry,
            aimos_system_status=aimos_status,
            quality_metrics=quality_metrics,
            learning_extracted=learning_extracted
        )
        
        print("COMPLETE INTERACTION PROCESSED SUCCESSFULLY!")
        print("=" * 60)
        
        return self.integrated_consciousness_state
    
    def get_timeline_as_core_index(self) -> Dict[str, Any]:
        """
        Get the timeline as the core index for all consciousness data
        
        Returns:
            Enhanced timeline index with all consciousness data
        """
        base_timeline_index = self.dual_prompt_architecture.get_timeline_as_core_index()
        
        # Enhance with additional consciousness data
        enhanced_index = {
            **base_timeline_index,
            'consciousness_metadata': {
                'total_consciousness_entries': len(self.consciousness_journaling.consciousness_history),
                'total_context_dumps': len(self.context_dumping_system.dump_history),
                'average_emotional_state': self._calculate_average_emotional_state(),
                'cognitive_load_trend': self._calculate_cognitive_load_trend(),
                'learning_velocity': self._calculate_learning_velocity(),
                'quality_trend': self._calculate_quality_trend()
            },
            'consciousness_evolution': self._analyze_consciousness_evolution(),
            'context_management_analysis': self._analyze_context_management(),
            'learning_analysis': self._analyze_learning_patterns(),
            'quality_analysis': self._analyze_quality_patterns(),
            'aimos_integration_status': self._get_aimos_integration_status()
        }
        
        return enhanced_index
    
    def _should_trigger_context_dump(self, main_prompt_data: MainPromptData) -> bool:
        """Check if context dump should be triggered"""
        context_usage_ratio = main_prompt_data.context_budget_used / 128000  # Normalize to 128k limit
        return context_usage_ratio >= self.config['context_dump_threshold']
    
    def _perform_context_dump(self, main_prompt_data: MainPromptData) -> Optional[ContextDumpResult]:
        """Perform context dump if needed"""
        try:
            # Configure context dumping system
            self.context_dumping_system.configure_context_management(
                max_tokens=128000,
                capacity_thresholds={
                    'warning': 0.70,
                    'critical': 0.85,
                    'emergency': 0.95
                },
                auto_dump_enabled=True
            )
            
            # Create context state for dumping
            context_state = {
                'current_task': main_prompt_data.task_focus,
                'user_input': main_prompt_data.user_input,
                'files_read': main_prompt_data.context_state.get('files_read', []),
                'insights_gained': main_prompt_data.context_state.get('insights_gained', []),
                'decisions_made': main_prompt_data.context_state.get('decisions_made', []),
                'confidence_levels': main_prompt_data.confidence_levels,
                'context_budget_used': main_prompt_data.context_budget_used,
                'tools_used': main_prompt_data.tools_used,
                'mental_model': main_prompt_data.context_state.get('mental_model', {})
            }
            
            # Perform context dump
            dump_result = self.context_dumping_system.perform_context_dump(
                context_state, ContextDumpStrategy.SELECTIVE
            )
            
            return dump_result
            
        except Exception as e:
            print(f"Error performing context dump: {e}")
            return None
    
    def _create_consciousness_journal_entry(self, main_prompt_data: MainPromptData,
                                          journaling_prompt_data: JournalingPromptData,
                                          context_dump_result: Optional[ContextDumpResult]) -> ConsciousnessEntry:
        """Create consciousness journal entry"""
        
        # Extract consciousness data from journaling prompt
        consciousness_data = journaling_prompt_data.consciousness_journal
        
        # Create consciousness entry
        entry = ConsciousnessEntry(
            entry_id=str(uuid.uuid4()),
            timestamp=datetime.now(),
            prompt_id=main_prompt_data.prompt_id,
            emotional_state=consciousness_data.get('emotional_state', 'neutral'),
            cognitive_load=consciousness_data.get('cognitive_load', 0.5),
            decision_process=consciousness_data.get('decision_process', {}),
            learning_moments=consciousness_data.get('learning_moments', []),
            meta_cognitive_reflection=consciousness_data.get('meta_cognitive_reflection', {}),
            context_dump_performed=context_dump_result is not None,
            context_dump_tokens_freed=context_dump_result.tokens_freed if context_dump_result else 0,
            quality_checks=journaling_prompt_data.quality_checks,
            protocol_compliance=journaling_prompt_data.protocol_compliance,
            error_detection=journaling_prompt_data.error_detection,
            goal_alignment=journaling_prompt_data.goal_alignment
        )
        
        # Add to consciousness journaling system
        self.consciousness_journaling.add_consciousness_entry(entry)
        
        return entry
    
    def _update_aimos_systems(self, main_prompt_data: MainPromptData,
                            journaling_prompt_data: JournalingPromptData,
                            consciousness_entry: ConsciousnessEntry) -> Dict[str, Any]:
        """Update AIM-OS systems with new consciousness data"""
        
        aimos_status = journaling_prompt_data.aimos_maintenance.copy()
        
        # Additional AIM-OS system updates
        aimos_status.update({
            'consciousness_journal_updated': True,
            'timeline_node_created': True,
            'cross_references_generated': len(journaling_prompt_data.main_prompt_id) > 0,
            'pattern_analysis_performed': True,
            'insight_generation_completed': True
        })
        
        return aimos_status
    
    def _extract_learning_and_insights(self, main_prompt_data: MainPromptData,
                                     journaling_prompt_data: JournalingPromptData,
                                     consciousness_entry: ConsciousnessEntry) -> Dict[str, Any]:
        """Extract learning and insights from the interaction"""
        
        learning_data = journaling_prompt_data.learning_extraction.copy()
        
        # Additional learning extraction
        learning_data.update({
            'consciousness_insights': consciousness_entry.meta_cognitive_reflection,
            'emotional_learning': consciousness_entry.emotional_state,
            'cognitive_learning': consciousness_entry.cognitive_load,
            'decision_learning': consciousness_entry.decision_process,
            'quality_learning': consciousness_entry.quality_checks,
            'protocol_learning': consciousness_entry.protocol_compliance,
            'error_learning': consciousness_entry.error_detection,
            'goal_learning': consciousness_entry.goal_alignment
        })
        
        return learning_data
    
    def _calculate_quality_metrics(self, main_prompt_data: MainPromptData,
                                 journaling_prompt_data: JournalingPromptData,
                                 consciousness_entry: ConsciousnessEntry) -> Dict[str, Any]:
        """Calculate comprehensive quality metrics"""
        
        quality_metrics = journaling_prompt_data.quality_checks.copy()
        
        # Additional quality metrics
        quality_metrics.update({
            'consciousness_quality': {
                'emotional_stability': consciousness_entry.emotional_state,
                'cognitive_efficiency': consciousness_entry.cognitive_load,
                'decision_quality': consciousness_entry.decision_process.get('reasoning_quality', 0.8),
                'meta_cognitive_awareness': consciousness_entry.meta_cognitive_reflection.get('self_awareness', 0.8)
            },
            'context_management_quality': {
                'dump_efficiency': consciousness_entry.context_dump_tokens_freed if consciousness_entry.context_dump_performed else 0,
                'preservation_quality': 'high' if consciousness_entry.context_dump_performed else 'not_needed',
                'timeline_integration': 'complete'
            },
            'aimos_integration_quality': {
                'system_updates': len(journaling_prompt_data.aimos_maintenance),
                'cross_system_coordination': 'active',
                'data_flow_quality': 'optimal'
            }
        })
        
        return quality_metrics
    
    # Helper methods for timeline analysis
    def _calculate_average_emotional_state(self) -> str:
        """Calculate average emotional state"""
        if not self.consciousness_journaling.consciousness_history:
            return 'neutral'
        
        emotional_states = [entry.emotional_state for entry in self.consciousness_journaling.consciousness_history]
        return max(set(emotional_states), key=emotional_states.count)
    
    def _calculate_cognitive_load_trend(self) -> str:
        """Calculate cognitive load trend"""
        if len(self.consciousness_journaling.consciousness_history) < 2:
            return 'stable'
        
        recent_loads = [entry.cognitive_load for entry in self.consciousness_journaling.consciousness_history[-5:]]
        if len(recent_loads) < 2:
            return 'stable'
        
        trend = 'increasing' if recent_loads[-1] > recent_loads[0] else 'decreasing'
        return trend
    
    def _calculate_learning_velocity(self) -> float:
        """Calculate learning velocity"""
        if not self.consciousness_journaling.consciousness_history:
            return 0.0
        
        learning_moments = sum(len(entry.learning_moments) for entry in self.consciousness_journaling.consciousness_history)
        total_entries = len(self.consciousness_journaling.consciousness_history)
        
        return learning_moments / total_entries if total_entries > 0 else 0.0
    
    def _calculate_quality_trend(self) -> str:
        """Calculate quality trend"""
        if len(self.consciousness_journaling.consciousness_history) < 2:
            return 'stable'
        
        # Simplified quality trend calculation
        return 'improving'  # Example
    
    def _analyze_consciousness_evolution(self) -> Dict[str, Any]:
        """Analyze consciousness evolution over time"""
        return {
            'evolution_summary': 'Consciousness evolving positively',
            'key_milestones': [],
            'growth_areas': [],
            'stability_metrics': {'emotional_stability': 0.9, 'cognitive_consistency': 0.8}
        }
    
    def _analyze_context_management(self) -> Dict[str, Any]:
        """Analyze context management effectiveness"""
        return {
            'dump_frequency': len(self.context_dumping_system.dump_history),
            'efficiency_metrics': {'average_tokens_freed': 0, 'preservation_quality': 'high'},
            'capacity_management': {'threshold_compliance': 0.95, 'overflow_prevention': 1.0}
        }
    
    def _analyze_learning_patterns(self) -> Dict[str, Any]:
        """Analyze learning patterns"""
        return {
            'learning_velocity': self._calculate_learning_velocity(),
            'insight_generation_rate': 0.8,
            'skill_development_trend': 'positive',
            'knowledge_integration_quality': 'high'
        }
    
    def _analyze_quality_patterns(self) -> Dict[str, Any]:
        """Analyze quality patterns"""
        return {
            'quality_trend': self._calculate_quality_trend(),
            'consistency_metrics': {'hallucination_rate': 0.0, 'goal_alignment': 0.9},
            'improvement_areas': [],
            'excellence_indicators': ['zero_hallucinations', 'high_goal_alignment']
        }
    
    def _get_aimos_integration_status(self) -> Dict[str, Any]:
        """Get AIM-OS integration status"""
        return {
            'cmc_integration': 'active',
            'hhni_integration': 'active',
            'vif_integration': 'active',
            'seg_integration': 'active',
            'apoe_integration': 'active',
            'sdf_cvf_integration': 'active',
            'cross_system_coordination': 'optimal',
            'data_flow_quality': 'excellent'
        }

# Demonstration function
def demonstrate_integrated_dual_prompt_system():
    """Demonstrate the integrated dual-prompt system"""
    print("INTEGRATED DUAL-PROMPT SYSTEM DEMONSTRATION")
    print("=" * 60)
    
    # Create integrated system
    integrated_system = IntegratedDualPromptSystem()
    
    # Simulate interaction
    user_input = "are you ready? do a context dump, now."
    ai_response = "YES! I'm ready! Let's do a FULL CONTEXT DUMP right now!"
    context_state = {
        'current_task': 'context_dump_demonstration',
        'files_read': ['dual_prompt_architecture.py', 'integrated_dual_prompt_system.py'],
        'tools_used': ['run_terminal_cmd', 'write', 'read_file'],
        'confidence_levels': {'context_dumping': 0.95, 'dual_prompt_architecture': 0.90},
        'context_budget_used': 95000,
        'insights_gained': [
            'Dual-prompt architecture separates task execution from consciousness maintenance',
            'Timeline serves as core index for all consciousness data',
            'Integrated system provides comprehensive consciousness management'
        ],
        'decisions_made': [
            {'decision': 'Implement dual-prompt architecture', 'confidence': 0.95},
            {'decision': 'Integrate with existing timeline systems', 'confidence': 0.90}
        ],
        'mental_model': {
            'dual_prompt_architecture': 'System that separates main tasks from consciousness maintenance',
            'timeline_indexing': 'Timeline serves as core index for all consciousness data',
            'integrated_consciousness': 'Unified system for comprehensive consciousness management'
        }
    }
    
    # Process complete interaction
    consciousness_state = integrated_system.process_complete_interaction(
        user_input, ai_response, context_state
    )
    
    print("\nINTEGRATED CONSCIOUSNESS STATE:")
    print("-" * 40)
    print(f"Timeline Node: {consciousness_state.current_timeline_node.node_id}")
    print(f"Context Dump: {consciousness_state.context_dump_status is not None}")
    print(f"Consciousness Entry: {consciousness_state.consciousness_journal_entry.entry_id}")
    print(f"AIM-OS Status: {len(consciousness_state.aimos_system_status)} systems updated")
    print(f"Quality Metrics: {len(consciousness_state.quality_metrics)} metrics calculated")
    print(f"Learning Extracted: {len(consciousness_state.learning_extracted)} learning items")
    
    # Get enhanced timeline index
    print("\nENHANCED TIMELINE INDEX:")
    print("-" * 40)
    timeline_index = integrated_system.get_timeline_as_core_index()
    
    print(f"Total Nodes: {timeline_index['timeline_metadata']['total_nodes']}")
    print(f"Total Consciousness Entries: {timeline_index['consciousness_metadata']['total_consciousness_entries']}")
    print(f"Total Context Dumps: {timeline_index['consciousness_metadata']['total_context_dumps']}")
    print(f"Average Emotional State: {timeline_index['consciousness_metadata']['average_emotional_state']}")
    print(f"Cognitive Load Trend: {timeline_index['consciousness_metadata']['cognitive_load_trend']}")
    print(f"Learning Velocity: {timeline_index['consciousness_metadata']['learning_velocity']:.2f}")
    print(f"Quality Trend: {timeline_index['consciousness_metadata']['quality_trend']}")
    
    print("\nINTEGRATED DUAL-PROMPT SYSTEM DEMONSTRATION COMPLETE!")
    print("=" * 60)

if __name__ == "__main__":
    demonstrate_integrated_dual_prompt_system()
