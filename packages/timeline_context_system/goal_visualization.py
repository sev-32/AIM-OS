"""
Goal Visualization Module

This module provides visualization capabilities for goal timelines,
including sequence-based views, status dashboards, and progress tracking.
"""

from __future__ import annotations

from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass

from .goal_timeline_node import GoalTimelineNode, GoalStatus, GoalPriority
from .goal_timeline_manager import GoalTimelineManager


@dataclass
class GoalTimelineView:
    """Goal timeline visualization data"""
    goal_id: str
    name: str
    status: str
    created_sequence: int
    current_sequence: int
    target_sequence: int
    progress: float
    priority: str
    created_at: str
    updated_at: str
    started_at: Optional[str]
    completed_at: Optional[str]
    key_results_total: int
    key_results_completed: int
    linked_goals: List[str]
    artifacts: List[str]
    evidence: List[str]


@dataclass
class GoalStatusDashboard:
    """Goal status dashboard data"""
    total_goals: int
    by_status: Dict[str, int]
    by_priority: Dict[str, int]
    by_progress: Dict[str, int]
    sequence_range: Dict[str, int]
    recent_activity: List[Dict[str, Any]]


class GoalVisualization:
    """Goal visualization generator"""
    
    def __init__(self, manager: GoalTimelineManager):
        self.manager = manager
    
    def get_timeline_view(self, goal_id: str) -> Optional[GoalTimelineView]:
        """
        Get timeline view for a specific goal
        
        Args:
            goal_id: Goal identifier
            
        Returns:
            GoalTimelineView or None if goal not found
        """
        goal = self.manager.get_goal(goal_id)
        if not goal:
            return None
        
        return GoalTimelineView(
            goal_id=goal.goal_id,
            name=goal.name,
            status=goal.status.value,
            created_sequence=goal.created_sequence,
            current_sequence=goal.current_sequence,
            target_sequence=goal.target_sequence,
            progress=goal.progress,
            priority=goal.priority.value,
            created_at=goal.created_at.isoformat(),
            updated_at=goal.updated_at.isoformat(),
            started_at=goal.started_at.isoformat() if goal.started_at else None,
            completed_at=goal.actual_completion.isoformat() if goal.actual_completion else None,
            key_results_total=goal.total_krs,
            key_results_completed=goal.completed_krs,
            linked_goals=goal.linked_goals,
            artifacts=goal.artifacts,
            evidence=goal.evidence
        )
    
    def get_all_timeline_views(self) -> List[GoalTimelineView]:
        """Get timeline views for all goals"""
        views = []
        for goal_id in self.manager.goals.keys():
            view = self.get_timeline_view(goal_id)
            if view:
                views.append(view)
        return views
    
    def get_status_dashboard(self) -> GoalStatusDashboard:
        """Get goal status dashboard"""
        all_goals = list(self.manager.goals.values())
        
        # Count by status
        by_status = {}
        for status in GoalStatus:
            by_status[status.value] = len([g for g in all_goals if g.status == status])
        
        # Count by priority
        by_priority = {}
        for priority in GoalPriority:
            by_priority[priority.value] = len([g for g in all_goals if g.priority == priority])
        
        # Count by progress ranges
        by_progress = {
            '0%': len([g for g in all_goals if g.progress == 0.0]),
            '1-25%': len([g for g in all_goals if 0.0 < g.progress <= 0.25]),
            '26-50%': len([g for g in all_goals if 0.25 < g.progress <= 0.50]),
            '51-75%': len([g for g in all_goals if 0.50 < g.progress <= 0.75]),
            '76-99%': len([g for g in all_goals if 0.75 < g.progress < 1.0]),
            '100%': len([g for g in all_goals if g.progress == 1.0])
        }
        
        # Sequence range
        if all_goals:
            sequences = [g.created_sequence for g in all_goals]
            sequence_range = {
                'min': min(sequences),
                'max': max(sequences),
                'current': self.manager.sequence_counter
            }
        else:
            sequence_range = {'min': 0, 'max': 0, 'current': 0}
        
        # Recent activity (last 10 updates)
        recent_activity = sorted(
            all_goals,
            key=lambda g: g.updated_at,
            reverse=True
        )[:10]
        
        recent_activity_data = []
        for goal in recent_activity:
            recent_activity_data.append({
                'goal_id': goal.goal_id,
                'name': goal.name,
                'status': goal.status.value,
                'updated_at': goal.updated_at.isoformat(),
                'progress': goal.progress
            })
        
        return GoalStatusDashboard(
            total_goals=len(all_goals),
            by_status=by_status,
            by_priority=by_priority,
            by_progress=by_progress,
            sequence_range=sequence_range,
            recent_activity=recent_activity_data
        )
    
    def get_sequence_timeline(self, start_sequence: Optional[int] = None, end_sequence: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get sequence-based timeline view
        
        Args:
            start_sequence: Start sequence (None = from beginning)
            end_sequence: End sequence (None = to end)
            
        Returns:
            List of goal timeline events
        """
        all_goals = list(self.manager.goals.values())
        
        # Filter by sequence if specified
        if start_sequence is not None:
            all_goals = [g for g in all_goals if g.created_sequence >= start_sequence]
        if end_sequence is not None:
            all_goals = [g for g in all_goals if g.created_sequence <= end_sequence]
        
        # Sort by sequence
        all_goals.sort(key=lambda g: g.created_sequence)
        
        # Build timeline events
        timeline = []
        for goal in all_goals:
            timeline.append({
                'sequence': goal.created_sequence,
                'goal_id': goal.goal_id,
                'name': goal.name,
                'status': goal.status.value,
                'progress': goal.progress,
                'current_sequence': goal.current_sequence,
                'target_sequence': goal.target_sequence
            })
        
        return timeline
    
    def get_goal_progress_chart_data(self, goal_id: str) -> Optional[Dict[str, Any]]:
        """
        Get progress chart data for a goal
        
        Args:
            goal_id: Goal identifier
            
        Returns:
            Chart data or None if goal not found
        """
        goal = self.manager.get_goal(goal_id)
        if not goal:
            return None
        
        milestones = goal.metadata.get('milestones', [])
        
        chart_data = {
            'goal_id': goal.goal_id,
            'name': goal.name,
            'milestones': milestones,
            'current_progress': goal.progress,
            'key_results': {
                'total': goal.total_krs,
                'completed': goal.completed_krs,
                'pending': goal.total_krs - goal.completed_krs
            },
            'status_history': self._get_status_history(goal)
        }
        
        return chart_data
    
    def _get_status_history(self, goal: GoalTimelineNode) -> List[Dict[str, Any]]:
        """Get status change history for a goal"""
        # This would be enhanced to track status changes over time
        # For now, return current status
        history = [
            {
                'status': goal.status.value,
                'timestamp': goal.updated_at.isoformat(),
                'sequence': goal.current_sequence
            }
        ]
        
        # Add created status if different from current
        if goal.status != GoalStatus.PLANNED:
            history.insert(0, {
                'status': GoalStatus.PLANNED.value,
                'timestamp': goal.created_at.isoformat(),
                'sequence': goal.created_sequence
            })
        
        return history
    
    def export_timeline_json(self) -> Dict[str, Any]:
        """
        Export complete timeline as JSON
        
        Returns:
            JSON-serializable timeline data
        """
        all_goals = list(self.manager.goals.values())
        
        return {
            'metadata': {
                'total_goals': len(all_goals),
                'sequence_counter': self.manager.sequence_counter,
                'exported_at': datetime.now().isoformat()
            },
            'goals': [goal.to_dict() for goal in all_goals],
            'dashboard': self.get_status_dashboard()
        }
    
    def export_timeline_text(self) -> str:
        """
        Export timeline as human-readable text
        
        Returns:
            Formatted text timeline
        """
        lines = []
        lines.append("=" * 80)
        lines.append("GOAL TIMELINE - SEQUENCE-BASED VIEW")
        lines.append("=" * 80)
        lines.append("")
        
        # Dashboard summary
        dashboard = self.get_status_dashboard()
        lines.append(f"Total Goals: {dashboard.total_goals}")
        lines.append(f"Sequence Range: {dashboard.sequence_range['min']} to {dashboard.sequence_range['max']} (current: {dashboard.sequence_range['current']})")
        lines.append("")
        
        # Status summary
        lines.append("By Status:")
        for status, count in dashboard.by_status.items():
            if count > 0:
                lines.append(f"  {status}: {count}")
        lines.append("")
        
        # Priority summary
        lines.append("By Priority:")
        for priority, count in dashboard.by_priority.items():
            if count > 0:
                lines.append(f"  {priority}: {count}")
        lines.append("")
        
        # Goal timeline
        lines.append("-" * 80)
        lines.append("GOAL TIMELINE (by sequence)")
        lines.append("-" * 80)
        lines.append("")
        
        timeline = self.get_sequence_timeline()
        for event in timeline:
            lines.append(f"Seq {event['sequence']}: {event['goal_id']} - {event['name']}")
            lines.append(f"  Status: {event['status']}, Progress: {event['progress']:.0%}")
            lines.append(f"  Current: {event['current_sequence']}, Target: {event['target_sequence']}")
            lines.append("")
        
        return "\n".join(lines)
