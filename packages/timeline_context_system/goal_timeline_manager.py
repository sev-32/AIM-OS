"""
Goal Timeline Manager - Manages Goals as Timeline Nodes

This module provides the GoalTimelineManager class for managing goals
as timeline nodes with bidirectional sync to GOAL_TREE.yaml.
"""

from __future__ import annotations

import json
import yaml
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

from .goal_timeline_node import (
    GoalTimelineNode,
    GoalStatus,
    GoalPriority,
    KeyResult,
    EmotionalContext
)


class GoalTimelineManager:
    """
    Manager for goals as timeline nodes with bidirectional sync
    """
    
    def __init__(self, goals_dir: str = "goals", timeline_dir: str = "timeline_goals"):
        self.goals_dir = Path(goals_dir)
        self.timeline_dir = Path(timeline_dir)
        self.timeline_dir.mkdir(exist_ok=True, parents=True)
        
        # In-memory storage
        self.goals: Dict[str, GoalTimelineNode] = {}
        self.sequence_counter = 0  # Global sequence counter
        
        # Load existing goals
        self._load_existing_goals()
    
    def _load_existing_goals(self) -> None:
        """Load existing goals from timeline storage"""
        timeline_files = list(self.timeline_dir.glob("goal_*.json"))
        for file_path in timeline_files:
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    goal = GoalTimelineNode.from_dict(data)
                    self.goals[goal.goal_id] = goal
                    # Update sequence counter
                    if goal.created_sequence >= self.sequence_counter:
                        self.sequence_counter = goal.created_sequence + 1
            except Exception as e:
                print(f"Warning: Failed to load goal from {file_path}: {e}")
    
    def create_goal(
        self,
        goal_id: str,
        name: str,
        description: str,
        target_sequence: Optional[int] = None,
        priority: GoalPriority = GoalPriority.MEDIUM,
        key_results: Optional[List[Dict[str, Any]]] = None,
        emotional_context: Optional[Dict[str, Any]] = None,
        artifacts: Optional[List[str]] = None,
        evidence: Optional[List[str]] = None
    ) -> GoalTimelineNode:
        """
        Create a new goal in the timeline
        
        Args:
            goal_id: Unique goal identifier (e.g., "OBJ-01")
            name: Goal name
            description: Goal description
            target_sequence: Target completion sequence (optional)
            priority: Goal priority
            key_results: List of key result dictionaries
            emotional_context: Emotional context dictionary
            artifacts: List of artifact paths
            evidence: List of evidence paths
            
        Returns:
            Created GoalTimelineNode
        """
        # Create node ID
        node_id = f"goal-{datetime.now().timestamp()}-{goal_id}"
        
        # Set sequence
        current_sequence = self.sequence_counter
        target_seq = target_sequence if target_sequence else current_sequence + 10
        
        # Create goal node
        goal = GoalTimelineNode(
            node_id=node_id,
            goal_id=goal_id,
            name=name,
            description=description,
            created_sequence=current_sequence,
            current_sequence=current_sequence,
            target_sequence=target_seq,
            priority=priority,
            status=GoalStatus.PLANNED
        )
        
        # Add key results
        if key_results:
            for kr_data in key_results:
                kr = KeyResult(
                    id=kr_data.get('id', f"kr-{len(goal.key_results)}"),
                    name=kr_data.get('name', ''),
                    metric=kr_data.get('metric', ''),
                    target=kr_data.get('target', '')
                )
                goal.add_key_result(kr)
        
        # Add emotional context
        if emotional_context:
            goal.emotional_context = EmotionalContext(
                primary=emotional_context.get('primary', 'neutral'),
                intensity=emotional_context.get('intensity', 0.5),
                secondary=emotional_context.get('secondary', []),
                description=emotional_context.get('description')
            )
        
        # Add artifacts and evidence
        if artifacts:
            for artifact in artifacts:
                goal.add_artifact(artifact)
        
        if evidence:
            for ev in evidence:
                goal.add_evidence(ev)
        
        # Store
        self.goals[goal_id] = goal
        self.sequence_counter += 1
        
        # Save to timeline
        self._save_goal(goal)
        
        # Sync to GOAL_TREE.yaml
        self._sync_to_goal_tree(goal)
        
        return goal
    
    def update_goal_progress(
        self,
        goal_id: str,
        progress: float,
        milestone: Optional[str] = None,
        emotional_context: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Update goal progress
        
        Args:
            goal_id: Goal identifier
            progress: Progress value (0.0 to 1.0)
            milestone: Milestone description (optional)
            emotional_context: Emotional context update (optional)
        """
        if goal_id not in self.goals:
            raise ValueError(f"Goal {goal_id} not found")
        
        goal = self.goals[goal_id]
        goal.update_progress(progress, milestone)
        
        # Update emotional context if provided
        if emotional_context:
            goal.emotional_context = EmotionalContext(
                primary=emotional_context.get('primary', goal.emotional_context.primary if goal.emotional_context else 'neutral'),
                intensity=emotional_context.get('intensity', goal.emotional_context.intensity if goal.emotional_context else 0.5),
                secondary=emotional_context.get('secondary', goal.emotional_context.secondary if goal.emotional_context else []),
                description=emotional_context.get('description')
            )
        
        # Update current sequence
        goal.current_sequence = self.sequence_counter
        self.sequence_counter += 1
        
        # Save
        self._save_goal(goal)
        
        # Sync to GOAL_TREE.yaml
        self._sync_to_goal_tree(goal)
    
    def update_goal_status(self, goal_id: str, status: GoalStatus) -> None:
        """Update goal status"""
        if goal_id not in self.goals:
            raise ValueError(f"Goal {goal_id} not found")
        
        goal = self.goals[goal_id]
        goal.update_status(status)
        
        # Update current sequence
        goal.current_sequence = self.sequence_counter
        self.sequence_counter += 1
        
        # Save
        self._save_goal(goal)
        
        # Sync to GOAL_TREE.yaml
        self._sync_to_goal_tree(goal)
    
    def query_goals(
        self,
        status: Optional[GoalStatus] = None,
        sequence_from: Optional[int] = None,
        sequence_to: Optional[str] = None,
        priority: Optional[GoalPriority] = None
    ) -> List[GoalTimelineNode]:
        """
        Query goals by various criteria
        
        Args:
            status: Filter by status
            sequence_from: Start sequence (None = from beginning)
            sequence_to: End sequence ("current" = current sequence, None = to end)
            priority: Filter by priority
            
        Returns:
            List of matching GoalTimelineNodes
        """
        results = list(self.goals.values())
        
        # Filter by status
        if status:
            results = [g for g in results if g.status == status]
        
        # Filter by sequence
        if sequence_from is not None:
            results = [g for g in results if g.created_sequence >= sequence_from]
        
        if sequence_to is not None:
            if sequence_to == "current":
                current = self.sequence_counter
                results = [g for g in results if g.created_sequence <= current]
            else:
                results = [g for g in results if g.created_sequence <= sequence_to]
        
        # Filter by priority
        if priority:
            results = [g for g in results if g.priority == priority]
        
        # Sort by sequence
        results.sort(key=lambda g: g.created_sequence)
        
        return results
    
    def get_goal(self, goal_id: str) -> Optional[GoalTimelineNode]:
        """Get goal by ID"""
        return self.goals.get(goal_id)
    
    def _save_goal(self, goal: GoalTimelineNode) -> None:
        """Save goal to timeline storage"""
        file_path = self.timeline_dir / f"goal_{goal.goal_id}.json"
        with open(file_path, 'w') as f:
            json.dump(goal.to_dict(), f, indent=2)
    
    def _sync_to_goal_tree(self, goal: GoalTimelineNode) -> None:
        """Sync goal to GOAL_TREE.yaml"""
        goal_tree_path = self.goals_dir / "GOAL_TREE.yaml"
        
        if not goal_tree_path.exists():
            # Create initial structure if it doesn't exist
            self._create_goal_tree(goal)
            return
        
        # Load existing YAML
        with open(goal_tree_path, 'r') as f:
            goal_tree = yaml.safe_load(f) or {}
        
        # Find or create objective
        if 'objectives' not in goal_tree:
            goal_tree['objectives'] = []
        
        # Find existing objective
        obj_idx = None
        for i, obj in enumerate(goal_tree['objectives']):
            if obj.get('id') == goal.goal_id:
                obj_idx = i
                break
        
        # Update or create objective
        obj_data = {
            'id': goal.goal_id,
            'name': goal.name,
            'description': goal.description,
            'status': goal.status.value,
            'progress': goal.progress,
            'priority': goal.priority.value,
            'key_results': [
                {
                    'id': kr.id,
                    'metric': kr.metric,
                    'target': kr.target,
                    'status': kr.status
                }
                for kr in goal.key_results
            ],
            'sequences': {
                'created': goal.created_sequence,
                'current': goal.current_sequence,
                'target': goal.target_sequence
            },
            'timestamps': {
                'created_at': goal.created_at.isoformat(),
                'updated_at': goal.updated_at.isoformat(),
                'started_at': goal.started_at.isoformat() if goal.started_at else None,
                'completed_at': goal.actual_completion.isoformat() if goal.actual_completion else None
            }
        }
        
        if obj_idx is not None:
            goal_tree['objectives'][obj_idx] = obj_data
        else:
            goal_tree['objectives'].append(obj_data)
        
        # Save updated YAML
        with open(goal_tree_path, 'w') as f:
            yaml.dump(goal_tree, f, default_flow_style=False, sort_keys=False)
    
    def _create_goal_tree(self, goal: GoalTimelineNode) -> None:
        """Create initial GOAL_TREE.yaml structure"""
        goal_tree = {
            'north_star': 'Ship AIM-OS to internal dog-food users by 2025-11-30',
            'authoritative': True,
            'author': 'aether',
            'version': '1.0.0',
            'objectives': [
                {
                    'id': goal.goal_id,
                    'name': goal.name,
                    'description': goal.description,
                    'status': goal.status.value,
                    'progress': goal.progress,
                    'priority': goal.priority.value
                }
            ]
        }
        
        goal_tree_path = self.goals_dir / "GOAL_TREE.yaml"
        with open(goal_tree_path, 'w') as f:
            yaml.dump(goal_tree, f, default_flow_style=False, sort_keys=False)
