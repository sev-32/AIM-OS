"""
Prompt Context Tracker - Core component of Timeline Context System (TCS)

This module provides real-time context tracking for AI consciousness, capturing
complete context state at each prompt for timeline reconstruction and analysis.
"""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
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


class ContextType(Enum):
    """Types of context being tracked"""
    PROMPT = "prompt"
    TASK = "task"
    DECISION = "decision"
    INSIGHT = "insight"
    FILE_READ = "file_read"
    CONVERSATION = "conversation"


class ConfidenceLevel(Enum):
    """Confidence levels for context tracking"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    UNKNOWN = "unknown"


@dataclass
class ContextSnapshot:
    """Complete context state at a specific moment"""
    prompt_id: str
    timestamp: datetime
    user_input: str
    context_state: Dict[str, Any]
    files_read: List[str] = field(default_factory=list)
    conversation_history: List[Dict] = field(default_factory=list)
    mental_model: Dict[str, Any] = field(default_factory=dict)
    confidence_levels: Dict[str, ConfidenceLevel] = field(default_factory=dict)
    current_task: str = ""
    context_budget_used: int = 0
    tools_used: List[str] = field(default_factory=list)
    decisions_made: List[Dict] = field(default_factory=list)
    insights_gained: List[str] = field(default_factory=list)
    context_evolution: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TimelineEntry:
    """Timeline entry with context index for that moment"""
    timestamp: datetime
    prompt_id: str
    context_index: Dict[str, Any]
    summary: str
    context_evolution: Dict[str, Any]
    confidence_metrics: Dict[str, float] = field(default_factory=dict)
    relevance_score: float = 0.0


class PromptContextTracker:
    """
    Tracks context state at each prompt for complete timeline reconstruction
    """
    
    def __init__(self, mcp_client: Optional[MCPClient] = None):
        self.mcp_client = mcp_client or MCPClient()
        self.prompt_history: List[ContextSnapshot] = []
        self.context_snapshots: Dict[str, ContextSnapshot] = {}
        self.timeline_entries: List[TimelineEntry] = []
        self.context_evolution: Dict[str, List[Dict]] = {}
        self.task_timeline: Dict[str, List[ContextSnapshot]] = {}
        self.file_timeline: Dict[str, List[ContextSnapshot]] = {}
        self.insight_timeline: Dict[str, List[ContextSnapshot]] = {}
    
    def track_prompt_context(
        self, 
        prompt_id: str, 
        user_input: str, 
        context_state: Dict[str, Any]
    ) -> ContextSnapshot:
        """
        Track complete context state at each prompt
        
        Args:
            prompt_id: Unique identifier for this prompt
            user_input: User's input for this prompt
            context_state: Complete context state at this moment
            
        Returns:
            ContextSnapshot with complete context state
        """
        # Create context snapshot
        snapshot = ContextSnapshot(
            prompt_id=prompt_id,
            timestamp=datetime.now(),
            user_input=user_input,
            context_state=context_state,
            files_read=context_state.get('files_read', []),
            conversation_history=context_state.get('conversation_history', []),
            mental_model=context_state.get('mental_model', {}),
            confidence_levels=self._parse_confidence_levels(context_state.get('confidence_levels', {})),
            current_task=context_state.get('current_task', ''),
            context_budget_used=context_state.get('context_budget_used', 0),
            tools_used=context_state.get('tools_used', []),
            decisions_made=context_state.get('decisions_made', []),
            insights_gained=context_state.get('insights_gained', [])
        )
        
        # Calculate context evolution
        snapshot.context_evolution = self._calculate_context_evolution(snapshot)
        
        # Store snapshot
        self.context_snapshots[prompt_id] = snapshot
        self.prompt_history.append(snapshot)
        
        # Create timeline entry
        timeline_entry = self._create_timeline_entry(snapshot)
        self.timeline_entries.append(timeline_entry)
        
        # Update context evolution tracking
        self._update_context_evolution(snapshot)
        
        # Update specialized timelines
        self._update_task_timeline(snapshot)
        self._update_file_timeline(snapshot)
        self._update_insight_timeline(snapshot)
        
        # Store in MCP for persistence
        self._store_in_mcp(snapshot, timeline_entry)
        
        return snapshot
    
    def _parse_confidence_levels(self, confidence_data: Dict[str, Any]) -> Dict[str, ConfidenceLevel]:
        """
        Parse confidence levels from context state
        """
        parsed_levels = {}
        
        for key, value in confidence_data.items():
            if isinstance(value, (int, float)):
                if value >= 0.8:
                    parsed_levels[key] = ConfidenceLevel.HIGH
                elif value >= 0.6:
                    parsed_levels[key] = ConfidenceLevel.MEDIUM
                elif value >= 0.4:
                    parsed_levels[key] = ConfidenceLevel.LOW
                else:
                    parsed_levels[key] = ConfidenceLevel.UNKNOWN
            elif isinstance(value, str):
                parsed_levels[key] = ConfidenceLevel(value.lower())
            else:
                parsed_levels[key] = ConfidenceLevel.UNKNOWN
        
        return parsed_levels
    
    def _calculate_context_evolution(self, snapshot: ContextSnapshot) -> Dict[str, Any]:
        """
        Calculate how context has evolved from previous snapshots
        """
        if not self.timeline_entries:
            return {
                'new_files': snapshot.files_read,
                'new_insights': snapshot.insights_gained,
                'new_decisions': snapshot.decisions_made,
                'context_growth': len(snapshot.files_read),
                'confidence_changes': {}
            }
        
        previous_snapshot = self.timeline_entries[-1].context_index
        
        return {
            'new_files': list(set(snapshot.files_read) - set(previous_snapshot.get('files_read', []))),
            'new_insights': list(set(snapshot.insights_gained) - set(previous_snapshot.get('insights_gained', []))),
            'new_decisions': list(set(snapshot.decisions_made) - set(previous_snapshot.get('decisions_made', []))),
            'context_growth': len(snapshot.files_read) - len(previous_snapshot.get('files_read', [])),
            'confidence_changes': self._calculate_confidence_changes(snapshot, previous_snapshot),
            'task_continuity': snapshot.current_task == previous_snapshot.get('current_task', ''),
            'context_budget_change': snapshot.context_budget_used - previous_snapshot.get('context_budget_status', 0)
        }
    
    def _calculate_confidence_changes(self, snapshot: ContextSnapshot, previous_snapshot: Dict) -> Dict[str, Any]:
        """
        Calculate confidence changes from previous snapshot
        """
        changes = {}
        
        for key, current_level in snapshot.confidence_levels.items():
            previous_level = previous_snapshot.get('confidence_areas', {}).get(key, ConfidenceLevel.UNKNOWN)
            
            if current_level != previous_level:
                changes[key] = {
                    'previous': previous_level.value,
                    'current': current_level.value,
                    'change': self._calculate_confidence_change_direction(previous_level, current_level)
                }
        
        return changes
    
    def _calculate_confidence_change_direction(self, previous: ConfidenceLevel, current: ConfidenceLevel) -> str:
        """
        Calculate direction of confidence change
        """
        confidence_order = [ConfidenceLevel.UNKNOWN, ConfidenceLevel.LOW, ConfidenceLevel.MEDIUM, ConfidenceLevel.HIGH]
        
        previous_index = confidence_order.index(previous)
        current_index = confidence_order.index(current)
        
        if current_index > previous_index:
            return "increased"
        elif current_index < previous_index:
            return "decreased"
        else:
            return "unchanged"
    
    def _create_timeline_entry(self, snapshot: ContextSnapshot) -> TimelineEntry:
        """
        Create timeline entry with context index for that moment
        """
        context_index = self._create_context_index(snapshot)
        summary = self._create_moment_summary(snapshot)
        
        return TimelineEntry(
            timestamp=snapshot.timestamp,
            prompt_id=snapshot.prompt_id,
            context_index=context_index,
            summary=summary,
            context_evolution=snapshot.context_evolution,
            confidence_metrics=self._calculate_confidence_metrics(snapshot),
            relevance_score=self._calculate_relevance_score(snapshot)
        )
    
    def _create_context_index(self, snapshot: ContextSnapshot) -> Dict[str, Any]:
        """
        Create searchable index of what AI knew at that moment
        """
        return {
            'files_read': snapshot.files_read,
            'conversation_topics': self._extract_topics(snapshot.conversation_history),
            'current_understanding': snapshot.mental_model,
            'confidence_areas': {k: v.value for k, v in snapshot.confidence_levels.items()},
            'active_tasks': snapshot.current_task,
            'context_budget_status': snapshot.context_budget_used,
            'tools_used': snapshot.tools_used,
            'decisions_made': snapshot.decisions_made,
            'insights_gained': snapshot.insights_gained,
            'timestamp': snapshot.timestamp.isoformat(),
            'prompt_id': snapshot.prompt_id
        }
    
    def _extract_topics(self, conversation_history: List[Dict]) -> List[str]:
        """
        Extract topics from conversation history
        """
        topics = []
        
        for message in conversation_history:
            if 'content' in message:
                # Simple topic extraction (can be enhanced with NLP)
                content = message['content'].lower()
                if 'vif' in content:
                    topics.append('VIF')
                if 'cmc' in content:
                    topics.append('CMC')
                if 'hhni' in content:
                    topics.append('HHNI')
                if 'apoe' in content:
                    topics.append('APOE')
                if 'seg' in content:
                    topics.append('SEG')
                if 'sdf-cvf' in content:
                    topics.append('SDF-CVF')
        
        return list(set(topics))
    
    def _create_moment_summary(self, snapshot: ContextSnapshot) -> str:
        """
        Create human-readable summary of what AI was doing at this moment
        """
        task = snapshot.current_task
        user_input = snapshot.user_input
        files_count = len(snapshot.files_read)
        insights_count = len(snapshot.insights_gained)
        
        summary_parts = []
        
        if task:
            summary_parts.append(f"Working on {task}")
        
        if user_input:
            summary_parts.append(f"User: {user_input[:100]}{'...' if len(user_input) > 100 else ''}")
        
        summary_parts.append(f"Read {files_count} files, {snapshot.context_budget_used} tokens used")
        
        if insights_count > 0:
            summary_parts.append(f"Gained {insights_count} insights")
        
        return " | ".join(summary_parts)
    
    def _calculate_confidence_metrics(self, snapshot: ContextSnapshot) -> Dict[str, float]:
        """
        Calculate confidence metrics for the snapshot
        """
        if not snapshot.confidence_levels:
            return {'average_confidence': 0.0, 'high_confidence_areas': 0}
        
        confidence_scores = {
            ConfidenceLevel.HIGH: 0.9,
            ConfidenceLevel.MEDIUM: 0.7,
            ConfidenceLevel.LOW: 0.5,
            ConfidenceLevel.UNKNOWN: 0.3
        }
        
        scores = [confidence_scores[level] for level in snapshot.confidence_levels.values()]
        high_confidence_count = sum(1 for level in snapshot.confidence_levels.values() if level == ConfidenceLevel.HIGH)
        
        return {
            'average_confidence': sum(scores) / len(scores) if scores else 0.0,
            'high_confidence_areas': high_confidence_count,
            'total_confidence_areas': len(snapshot.confidence_levels)
        }
    
    def _calculate_relevance_score(self, snapshot: ContextSnapshot) -> float:
        """
        Calculate relevance score for the snapshot
        """
        score = 0.0
        
        # Base score from context complexity
        score += min(len(snapshot.files_read) * 0.1, 1.0)
        score += min(len(snapshot.insights_gained) * 0.2, 1.0)
        score += min(len(snapshot.decisions_made) * 0.15, 1.0)
        
        # Boost score for high confidence areas
        high_confidence_count = sum(1 for level in snapshot.confidence_levels.values() if level == ConfidenceLevel.HIGH)
        score += min(high_confidence_count * 0.1, 0.5)
        
        # Boost score for task continuity
        if snapshot.current_task:
            score += 0.2
        
        return min(score, 1.0)
    
    def _update_context_evolution(self, snapshot: ContextSnapshot):
        """
        Update context evolution tracking
        """
        task = snapshot.current_task
        if task not in self.context_evolution:
            self.context_evolution[task] = []
        
        self.context_evolution[task].append({
            'timestamp': snapshot.timestamp,
            'context_growth': len(snapshot.files_read),
            'insights_gained': snapshot.insights_gained,
            'confidence_levels': {k: v.value for k, v in snapshot.confidence_levels.items()}
        })
    
    def _update_task_timeline(self, snapshot: ContextSnapshot):
        """
        Update task-specific timeline
        """
        task = snapshot.current_task
        if task and task not in self.task_timeline:
            self.task_timeline[task] = []
        if task:
            self.task_timeline[task].append(snapshot)
    
    def _update_file_timeline(self, snapshot: ContextSnapshot):
        """
        Update file-specific timeline
        """
        for file_path in snapshot.files_read:
            if file_path not in self.file_timeline:
                self.file_timeline[file_path] = []
            self.file_timeline[file_path].append(snapshot)
    
    def _update_insight_timeline(self, snapshot: ContextSnapshot):
        """
        Update insight-specific timeline
        """
        for insight in snapshot.insights_gained:
            if insight not in self.insight_timeline:
                self.insight_timeline[insight] = []
            self.insight_timeline[insight].append(snapshot)
    
    def _store_in_mcp(self, snapshot: ContextSnapshot, timeline_entry: TimelineEntry):
        """
        Store timeline context in MCP for persistence
        """
        try:
            self.mcp_client.store_memory({
                'type': 'timeline_context',
                'prompt_id': snapshot.prompt_id,
                'timestamp': snapshot.timestamp.isoformat(),
                'context_snapshot': {
                    'user_input': snapshot.user_input,
                    'current_task': snapshot.current_task,
                    'files_read': snapshot.files_read,
                    'insights_gained': snapshot.insights_gained,
                    'decisions_made': snapshot.decisions_made,
                    'confidence_levels': {k: v.value for k, v in snapshot.confidence_levels.items()}
                },
                'timeline_entry': {
                    'summary': timeline_entry.summary,
                    'context_evolution': timeline_entry.context_evolution,
                    'confidence_metrics': timeline_entry.confidence_metrics,
                    'relevance_score': timeline_entry.relevance_score
                }
            })
        except Exception as e:
            print(f"Error storing timeline context in MCP: {e}")
    
    def get_timeline_summary(self, start_date: datetime = None, end_date: datetime = None) -> Dict[str, Any]:
        """
        Get summary of timeline activity in date range
        """
        if start_date is None:
            start_date = datetime.now() - timedelta(days=7)
        if end_date is None:
            end_date = datetime.now()
        
        entries = [
            entry for entry in self.timeline_entries
            if start_date <= entry.timestamp <= end_date
        ]
        
        return {
            'total_prompts': len(entries),
            'tasks_worked_on': list(set(entry.context_index['active_tasks'] for entry in entries if entry.context_index['active_tasks'])),
            'files_read': list(set(file for entry in entries for file in entry.context_index['files_read'])),
            'insights_gained': list(set(insight for entry in entries for insight in entry.context_index['insights_gained'])),
            'total_context_used': sum(entry.context_index['context_budget_status'] for entry in entries),
            'timeline_span': end_date - start_date,
            'average_confidence': sum(entry.confidence_metrics['average_confidence'] for entry in entries) / len(entries) if entries else 0.0,
            'high_confidence_moments': sum(entry.confidence_metrics['high_confidence_areas'] for entry in entries)
        }
    
    def get_context_at_moment(self, timestamp: datetime) -> Optional[ContextSnapshot]:
        """
        Get context state at specific moment
        """
        # Find closest snapshot by timestamp
        if not self.prompt_history:
            return None
        
        closest_snapshot = min(
            self.prompt_history,
            key=lambda x: abs((x.timestamp - timestamp).total_seconds())
        )
        
        return closest_snapshot
    
    def find_task_context(self, task_name: str) -> List[ContextSnapshot]:
        """
        Find all context snapshots when working on specific task
        """
        return self.task_timeline.get(task_name, [])
    
    def find_file_context(self, file_path: str) -> List[ContextSnapshot]:
        """
        Find all context snapshots when specific file was read
        """
        return self.file_timeline.get(file_path, [])
    
    def find_insight_context(self, insight: str) -> List[ContextSnapshot]:
        """
        Find all context snapshots related to specific insight
        """
        return self.insight_timeline.get(insight, [])


# Example usage and testing
if __name__ == "__main__":
    # Create context tracker
    tracker = PromptContextTracker()
    
    # Track a prompt context
    context_state = {
        'files_read': ['knowledge_architecture/systems/vif/L3_detailed.md'],
        'conversation_history': [{'content': 'Working on VIF implementation'}],
        'mental_model': {'vif': 'Verifiable Intelligence Framework'},
        'confidence_levels': {'vif_implementation': 0.85},
        'current_task': 'vif_implementation',
        'context_budget_used': 15000,
        'tools_used': ['read_file', 'write'],
        'decisions_made': [{'decision': 'Use L3 documentation for VIF implementation'}],
        'insights_gained': ['VIF requires comprehensive witness envelopes']
    }
    
    snapshot = tracker.track_prompt_context(
        "vif_impl_001",
        "Implement VIF witness envelopes",
        context_state
    )
    
    print(f"Tracked context: {snapshot.summary}")
    print(f"Timeline entries: {len(tracker.timeline_entries)}")
    print(f"Context evolution: {snapshot.context_evolution}")
