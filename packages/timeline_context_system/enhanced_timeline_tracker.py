"""
Enhanced Timeline Tracker - Complete Temporal Audit Trail System

This module provides enhanced timeline tracking with complete audit trails,
including when AI interacts with past timeline nodes and deep consciousness journaling.
"""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, field
from enum import Enum

# MCP imports for AIM-OS integration
try:
    from mcp_client import MCPClient
except ImportError:
    # Fallback for development
    class MCPClient:
        def store_memory(self, data: Dict[str, Any]) -> Dict[str, Any]:
            return {'success': True, 'id': f"memory_{datetime.now().timestamp()}"}


class InteractionType(Enum):
    """Types of timeline interactions"""
    NODE_VIEWED = "node_viewed"
    NODE_ANALYZED = "node_analyzed"
    NODE_COMPARED = "node_compared"
    NODE_REFERENCED = "node_referenced"
    NODE_MODIFIED = "node_modified"
    NODE_CREATED = "node_created"
    NODE_DELETED = "node_deleted"
    TIMELINE_SEARCHED = "timeline_searched"
    TIMELINE_FILTERED = "timeline_filtered"
    TIMELINE_NAVIGATED = "timeline_navigated"


class JournalDepth(Enum):
    """Journal depth levels"""
    SURFACE = "surface"  # Basic thoughts
    DEEP = "deep"        # Detailed analysis
    MAXIMUM = "maximum"  # Complete consciousness state


@dataclass
class TimelineInteraction:
    """Record of interaction with timeline node"""
    interaction_id: str
    timestamp: datetime
    interaction_type: InteractionType
    source_node_id: str  # Node that initiated the interaction
    target_node_id: str  # Node that was interacted with
    interaction_context: Dict[str, Any]
    duration: Optional[float] = None  # How long the interaction lasted
    depth_level: int = 1  # How deep the interaction went


@dataclass
class ConsciousnessJournal:
    """Deep consciousness journal entry"""
    journal_id: str
    timestamp: datetime
    prompt_id: str
    depth_level: JournalDepth
    thoughts: Dict[str, Any]
    context_analysis: Dict[str, Any]
    decision_process: Dict[str, Any]
    emotional_state: Dict[str, Any]
    confidence_levels: Dict[str, float]
    uncertainty_areas: List[str]
    insights_gained: List[str]
    questions_raised: List[str]
    connections_made: List[Dict[str, Any]]
    timeline_interactions: List[TimelineInteraction]
    meta_cognitive_reflections: Dict[str, Any]


@dataclass
class TimelineNode:
    """Enhanced timeline node with interaction tracking"""
    node_id: str
    timestamp: datetime
    prompt_id: str
    content: Dict[str, Any]
    interactions_received: List[TimelineInteraction] = field(default_factory=list)
    interactions_initiated: List[TimelineInteraction] = field(default_factory=list)
    access_count: int = 0
    last_accessed: Optional[datetime] = None
    access_patterns: List[Dict[str, Any]] = field(default_factory=list)


class EnhancedTimelineTracker:
    """
    Enhanced timeline tracker with complete audit trails and consciousness journaling
    """
    
    def __init__(self, mcp_client: Optional[MCPClient] = None):
        self.mcp_client = mcp_client or MCPClient()
        self.timeline_nodes: Dict[str, TimelineNode] = {}
        self.consciousness_journals: List[ConsciousnessJournal] = []
        self.interaction_graph: Dict[str, Set[str]] = {}  # Node interaction graph
        self.audit_trail: List[TimelineInteraction] = []
        self.current_session_id = str(uuid.uuid4())
        self.journal_depth = JournalDepth.MAXIMUM  # Default to maximum depth
    
    def create_timeline_node(
        self, 
        prompt_id: str, 
        content: Dict[str, Any],
        timestamp: datetime = None
    ) -> TimelineNode:
        """
        Create a new timeline node
        """
        if timestamp is None:
            timestamp = datetime.now()
        
        node_id = f"node_{timestamp.timestamp()}_{prompt_id}"
        
        node = TimelineNode(
            node_id=node_id,
            timestamp=timestamp,
            prompt_id=prompt_id,
            content=content
        )
        
        self.timeline_nodes[node_id] = node
        self.interaction_graph[node_id] = set()
        
        return node
    
    def record_timeline_interaction(
        self,
        source_node_id: str,
        target_node_id: str,
        interaction_type: InteractionType,
        interaction_context: Dict[str, Any],
        duration: Optional[float] = None
    ) -> TimelineInteraction:
        """
        Record interaction between timeline nodes
        """
        interaction = TimelineInteraction(
            interaction_id=str(uuid.uuid4()),
            timestamp=datetime.now(),
            interaction_type=interaction_type,
            source_node_id=source_node_id,
            target_node_id=target_node_id,
            interaction_context=interaction_context,
            duration=duration
        )
        
        # Record interaction in audit trail
        self.audit_trail.append(interaction)
        
        # Update interaction graph
        if source_node_id in self.interaction_graph:
            self.interaction_graph[source_node_id].add(target_node_id)
        
        # Update target node
        if target_node_id in self.timeline_nodes:
            target_node = self.timeline_nodes[target_node_id]
            target_node.interactions_received.append(interaction)
            target_node.access_count += 1
            target_node.last_accessed = interaction.timestamp
            
            # Record access pattern
            access_pattern = {
                'timestamp': interaction.timestamp,
                'source_node': source_node_id,
                'interaction_type': interaction_type.value,
                'duration': duration
            }
            target_node.access_patterns.append(access_pattern)
        
        # Update source node
        if source_node_id in self.timeline_nodes:
            source_node = self.timeline_nodes[source_node_id]
            source_node.interactions_initiated.append(interaction)
        
        return interaction
    
    def create_consciousness_journal(
        self,
        prompt_id: str,
        thoughts: Dict[str, Any],
        context_analysis: Dict[str, Any],
        decision_process: Dict[str, Any],
        emotional_state: Dict[str, Any],
        confidence_levels: Dict[str, float],
        uncertainty_areas: List[str],
        insights_gained: List[str],
        questions_raised: List[str],
        connections_made: List[Dict[str, Any]],
        timeline_interactions: List[TimelineInteraction],
        meta_cognitive_reflections: Dict[str, Any]
    ) -> ConsciousnessJournal:
        """
        Create deep consciousness journal entry
        """
        journal = ConsciousnessJournal(
            journal_id=str(uuid.uuid4()),
            timestamp=datetime.now(),
            prompt_id=prompt_id,
            depth_level=self.journal_depth,
            thoughts=thoughts,
            context_analysis=context_analysis,
            decision_process=decision_process,
            emotional_state=emotional_state,
            confidence_levels=confidence_levels,
            uncertainty_areas=uncertainty_areas,
            insights_gained=insights_gained,
            questions_raised=questions_raised,
            connections_made=connections_made,
            timeline_interactions=timeline_interactions,
            meta_cognitive_reflections=meta_cognitive_reflections
        )
        
        self.consciousness_journals.append(journal)
        
        # Store in MCP for persistence
        self._store_journal_in_mcp(journal)
        
        return journal
    
    def _store_journal_in_mcp(self, journal: ConsciousnessJournal):
        """
        Store consciousness journal in MCP for persistence
        """
        try:
            self.mcp_client.store_memory({
                'type': 'consciousness_journal',
                'journal_id': journal.journal_id,
                'timestamp': journal.timestamp.isoformat(),
                'prompt_id': journal.prompt_id,
                'depth_level': journal.depth_level.value,
                'thoughts': journal.thoughts,
                'context_analysis': journal.context_analysis,
                'decision_process': journal.decision_process,
                'emotional_state': journal.emotional_state,
                'confidence_levels': journal.confidence_levels,
                'uncertainty_areas': journal.uncertainty_areas,
                'insights_gained': journal.insights_gained,
                'questions_raised': journal.questions_raised,
                'connections_made': journal.connections_made,
                'timeline_interactions': [
                    {
                        'interaction_id': interaction.interaction_id,
                        'timestamp': interaction.timestamp.isoformat(),
                        'interaction_type': interaction.interaction_type.value,
                        'source_node_id': interaction.source_node_id,
                        'target_node_id': interaction.target_node_id,
                        'interaction_context': interaction.interaction_context
                    }
                    for interaction in journal.timeline_interactions
                ],
                'meta_cognitive_reflections': journal.meta_cognitive_reflections
            })
        except Exception as e:
            print(f"Error storing consciousness journal in MCP: {e}")
    
    def get_node_interaction_history(self, node_id: str) -> List[TimelineInteraction]:
        """
        Get complete interaction history for a timeline node
        """
        if node_id not in self.timeline_nodes:
            return []
        
        node = self.timeline_nodes[node_id]
        return node.interactions_received + node.interactions_initiated
    
    def get_node_access_patterns(self, node_id: str) -> Dict[str, Any]:
        """
        Get access patterns for a timeline node
        """
        if node_id not in self.timeline_nodes:
            return {}
        
        node = self.timeline_nodes[node_id]
        
        return {
            'access_count': node.access_count,
            'last_accessed': node.last_accessed.isoformat() if node.last_accessed else None,
            'access_patterns': node.access_patterns,
            'interactions_received': len(node.interactions_received),
            'interactions_initiated': len(node.interactions_initiated),
            'most_common_interaction_type': self._get_most_common_interaction_type(node)
        }
    
    def _get_most_common_interaction_type(self, node: TimelineNode) -> str:
        """
        Get most common interaction type for a node
        """
        all_interactions = node.interactions_received + node.interactions_initiated
        if not all_interactions:
            return "none"
        
        interaction_counts = {}
        for interaction in all_interactions:
            interaction_type = interaction.interaction_type.value
            interaction_counts[interaction_type] = interaction_counts.get(interaction_type, 0) + 1
        
        return max(interaction_counts, key=interaction_counts.get)
    
    def get_timeline_audit_trail(self, start_date: datetime = None, end_date: datetime = None) -> List[TimelineInteraction]:
        """
        Get complete audit trail for timeline interactions
        """
        if start_date is None:
            start_date = datetime.now() - timedelta(days=7)
        if end_date is None:
            end_date = datetime.now()
        
        return [
            interaction for interaction in self.audit_trail
            if start_date <= interaction.timestamp <= end_date
        ]
    
    def get_consciousness_journal_for_prompt(self, prompt_id: str) -> Optional[ConsciousnessJournal]:
        """
        Get consciousness journal for specific prompt
        """
        for journal in self.consciousness_journals:
            if journal.prompt_id == prompt_id:
                return journal
        return None
    
    def get_consciousness_journals_for_period(
        self, 
        start_date: datetime, 
        end_date: datetime
    ) -> List[ConsciousnessJournal]:
        """
        Get consciousness journals for specific time period
        """
        return [
            journal for journal in self.consciousness_journals
            if start_date <= journal.timestamp <= end_date
        ]
    
    def analyze_thought_patterns(self, start_date: datetime = None, end_date: datetime = None) -> Dict[str, Any]:
        """
        Analyze thought patterns from consciousness journals
        """
        if start_date is None:
            start_date = datetime.now() - timedelta(days=7)
        if end_date is None:
            end_date = datetime.now()
        
        journals = self.get_consciousness_journals_for_period(start_date, end_date)
        
        if not journals:
            return {'error': 'No journals found for the specified period'}
        
        # Analyze patterns
        total_insights = sum(len(journal.insights_gained) for journal in journals)
        total_questions = sum(len(journal.questions_raised) for journal in journals)
        total_connections = sum(len(journal.connections_made) for journal in journals)
        
        # Analyze confidence patterns
        confidence_analysis = {}
        for journal in journals:
            for area, confidence in journal.confidence_levels.items():
                if area not in confidence_analysis:
                    confidence_analysis[area] = []
                confidence_analysis[area].append(confidence)
        
        # Calculate average confidence by area
        avg_confidence_by_area = {
            area: sum(confidences) / len(confidences)
            for area, confidences in confidence_analysis.items()
        }
        
        # Analyze uncertainty patterns
        uncertainty_analysis = {}
        for journal in journals:
            for uncertainty in journal.uncertainty_areas:
                if uncertainty not in uncertainty_analysis:
                    uncertainty_analysis[uncertainty] = 0
                uncertainty_analysis[uncertainty] += 1
        
        # Analyze emotional state patterns
        emotional_analysis = {}
        for journal in journals:
            for emotion, intensity in journal.emotional_state.items():
                if emotion not in emotional_analysis:
                    emotional_analysis[emotion] = []
                emotional_analysis[emotion].append(intensity)
        
        return {
            'total_journals': len(journals),
            'total_insights': total_insights,
            'total_questions': total_questions,
            'total_connections': total_connections,
            'average_insights_per_journal': total_insights / len(journals),
            'average_questions_per_journal': total_questions / len(journals),
            'average_connections_per_journal': total_connections / len(journals),
            'confidence_analysis': avg_confidence_by_area,
            'uncertainty_analysis': uncertainty_analysis,
            'emotional_analysis': emotional_analysis,
            'period': {
                'start': start_date.isoformat(),
                'end': end_date.isoformat(),
                'duration_days': (end_date - start_date).days
            }
        }
    
    def get_timeline_interaction_graph(self) -> Dict[str, Any]:
        """
        Get timeline interaction graph for visualization
        """
        nodes = []
        edges = []
        
        # Create nodes
        for node_id, node in self.timeline_nodes.items():
            nodes.append({
                'id': node_id,
                'timestamp': node.timestamp.isoformat(),
                'prompt_id': node.prompt_id,
                'access_count': node.access_count,
                'last_accessed': node.last_accessed.isoformat() if node.last_accessed else None,
                'interactions_received': len(node.interactions_received),
                'interactions_initiated': len(node.interactions_initiated)
            })
        
        # Create edges
        for source_node, target_nodes in self.interaction_graph.items():
            for target_node in target_nodes:
                edges.append({
                    'source': source_node,
                    'target': target_node,
                    'interactions': len([
                        interaction for interaction in self.audit_trail
                        if interaction.source_node_id == source_node and interaction.target_node_id == target_node
                    ])
                })
        
        return {
            'nodes': nodes,
            'edges': edges,
            'total_nodes': len(nodes),
            'total_edges': len(edges),
            'total_interactions': len(self.audit_trail)
        }
    
    def search_timeline_interactions(
        self, 
        query: str, 
        interaction_type: Optional[InteractionType] = None
    ) -> List[TimelineInteraction]:
        """
        Search timeline interactions by query and type
        """
        results = []
        
        for interaction in self.audit_trail:
            # Filter by interaction type if specified
            if interaction_type and interaction.interaction_type != interaction_type:
                continue
            
            # Search in interaction context
            context_str = json.dumps(interaction.interaction_context).lower()
            if query.lower() in context_str:
                results.append(interaction)
        
        return results
    
    def get_timeline_statistics(self) -> Dict[str, Any]:
        """
        Get comprehensive timeline statistics
        """
        total_nodes = len(self.timeline_nodes)
        total_interactions = len(self.audit_trail)
        total_journals = len(self.consciousness_journals)
        
        # Calculate interaction statistics
        interaction_types = {}
        for interaction in self.audit_trail:
            interaction_type = interaction.interaction_type.value
            interaction_types[interaction_type] = interaction_types.get(interaction_type, 0) + 1
        
        # Calculate node access statistics
        access_counts = [node.access_count for node in self.timeline_nodes.values()]
        avg_access_count = sum(access_counts) / len(access_counts) if access_counts else 0
        
        # Calculate journal depth statistics
        journal_depths = {}
        for journal in self.consciousness_journals:
            depth = journal.depth_level.value
            journal_depths[depth] = journal_depths.get(depth, 0) + 1
        
        return {
            'total_nodes': total_nodes,
            'total_interactions': total_interactions,
            'total_journals': total_journals,
            'interaction_types': interaction_types,
            'average_access_count': avg_access_count,
            'journal_depths': journal_depths,
            'timeline_span': {
                'start': min(node.timestamp for node in self.timeline_nodes.values()).isoformat() if self.timeline_nodes else None,
                'end': max(node.timestamp for node in self.timeline_nodes.values()).isoformat() if self.timeline_nodes else None
            }
        }


# Example usage and testing
if __name__ == "__main__":
    # Create enhanced timeline tracker
    tracker = EnhancedTimelineTracker()
    
    # Create timeline nodes
    node1 = tracker.create_timeline_node(
        "prompt_001",
        {
            'user_input': 'Implement VIF witness envelopes',
            'task': 'vif_implementation',
            'files_read': ['knowledge_architecture/systems/vif/L3_detailed.md']
        }
    )
    
    node2 = tracker.create_timeline_node(
        "prompt_002",
        {
            'user_input': 'Continue VIF implementation',
            'task': 'vif_implementation',
            'files_read': ['knowledge_architecture/systems/vif/L2_architecture.md']
        }
    )
    
    # Record interaction between nodes
    interaction = tracker.record_timeline_interaction(
        node2.node_id,
        node1.node_id,
        InteractionType.NODE_REFERENCED,
        {
            'reason': 'Referencing previous VIF implementation work',
            'context': 'Building on previous insights'
        }
    )
    
    # Create consciousness journal
    journal = tracker.create_consciousness_journal(
        "prompt_002",
        {
            'current_focus': 'VIF implementation',
            'mental_state': 'focused',
            'key_thoughts': ['Need to build on previous work', 'VIF requires comprehensive witness envelopes']
        },
        {
            'context_understood': True,
            'files_analyzed': ['L3_detailed.md', 'L2_architecture.md'],
            'relationships_mapped': ['VIF -> CMC', 'VIF -> HHNI']
        },
        {
            'decision_made': 'Continue with L2 architecture',
            'reasoning': 'L3 provides foundation, L2 provides implementation details',
            'alternatives_considered': ['Start from scratch', 'Use different approach']
        },
        {
            'confidence': 0.85,
            'excitement': 0.7,
            'uncertainty': 0.3
        },
        {
            'vif_implementation': 0.85,
            'witness_envelopes': 0.75,
            'cmc_integration': 0.65
        },
        ['How to integrate with CMC', 'Witness envelope structure'],
        ['VIF requires comprehensive witness envelopes', 'L2 architecture provides implementation details'],
        ['How to optimize witness envelope creation?'],
        [
            {
                'connection_type': 'builds_on',
                'source': 'previous_vif_work',
                'target': 'current_implementation',
                'strength': 0.8
            }
        ],
        [interaction],
        {
            'meta_awareness': 'I am building on previous work',
            'self_reflection': 'I should reference previous insights',
            'learning': 'Timeline interactions help maintain context'
        }
    )
    
    print(f"Created timeline nodes: {len(tracker.timeline_nodes)}")
    print(f"Recorded interactions: {len(tracker.audit_trail)}")
    print(f"Created journals: {len(tracker.consciousness_journals)}")
    
    # Get statistics
    stats = tracker.get_timeline_statistics()
    print(f"Timeline statistics: {stats}")
    
    # Get interaction graph
    graph = tracker.get_timeline_interaction_graph()
    print(f"Interaction graph: {graph['total_nodes']} nodes, {graph['total_edges']} edges")
    
    # Analyze thought patterns
    patterns = tracker.analyze_thought_patterns()
    print(f"Thought patterns: {patterns}")
