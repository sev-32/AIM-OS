"""
GOAL_TREE.yaml Bidirectional Sync

This module provides bidirectional synchronization between GOAL_TREE.yaml
and the timeline goal system.
"""

from __future__ import annotations

import yaml
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

from .goal_timeline_node import GoalTimelineNode, GoalStatus, GoalPriority
from .goal_timeline_manager import GoalTimelineManager


class GoalTreeSync:
    """
    Bidirectional sync between GOAL_TREE.yaml and timeline
    """
    
    def __init__(self, goals_dir: str = "goals", timeline_dir: str = "timeline_goals"):
        self.goals_dir = Path(goals_dir)
        self.goal_tree_path = self.goals_dir / "GOAL_TREE.yaml"
        self.manager = GoalTimelineManager(goals_dir, timeline_dir)
    
    def load_from_yaml(self) -> None:
        """
        Load existing goals from GOAL_TREE.yaml and create timeline nodes
        """
        if not self.goal_tree_path.exists():
            print(f"GOAL_TREE.yaml not found at {self.goal_tree_path}")
            return
        
        with open(self.goal_tree_path, 'r') as f:
            goal_tree = yaml.safe_load(f)
        
        objectives = goal_tree.get('objectives', [])
        
        for obj in objectives:
            goal_id = obj.get('id')
            if not goal_id:
                continue
            
            # Check if already exists in timeline
            existing = self.manager.get_goal(goal_id)
            if existing:
                print(f"Goal {goal_id} already exists in timeline, skipping")
                continue
            
            # Convert YAML status to GoalStatus
            status_str = obj.get('status', 'planned')
            status = self._parse_status(status_str)
            
            # Convert YAML data to timeline node
            key_results = []
            for kr in obj.get('key_results', []):
                key_results.append({
                    'id': kr.get('id'),
                    'name': kr.get('name', ''),
                    'metric': kr.get('metric', ''),
                    'target': kr.get('target', '')
                })
            
            # Create goal
            goal = self.manager.create_goal(
                goal_id=goal_id,
                name=obj.get('name', ''),
                description=obj.get('description', ''),
                priority=GoalPriority.MEDIUM,  # Default, can be enhanced
                key_results=key_results,
                artifacts=obj.get('artifacts', []),
                evidence=obj.get('evidence', [])
            )
            
            # Set status
            if status != GoalStatus.PLANNED:
                self.manager.update_goal_status(goal_id, status)
            
            # Set progress based on key results if available
            progress = self._calculate_progress_from_yaml(obj)
            if progress > 0.0:
                self.manager.update_goal_progress(goal_id, progress)
            
            print(f"Loaded goal {goal_id}: {goal.name}")
    
    def sync_timeline_to_yaml(self, goal_id: str) -> None:
        """
        Sync a specific goal from timeline to YAML
        """
        goal = self.manager.get_goal(goal_id)
        if not goal:
            raise ValueError(f"Goal {goal_id} not found in timeline")
        
        # Load current YAML
        with open(self.goal_tree_path, 'r') as f:
            goal_tree = yaml.safe_load(f)
        
        # Find and update objective
        objectives = goal_tree.get('objectives', [])
        obj_idx = None
        for i, obj in enumerate(objectives):
            if obj.get('id') == goal_id:
                obj_idx = i
                break
        
        # Prepare objective data
        obj_data = {
            'id': goal.goal_id,
            'name': goal.name,
            'description': goal.description,
            'status': goal.status.value,
            'key_results': [
                {
                    'id': kr.id,
                    'name': kr.name,
                    'metric': kr.metric,
                    'target': kr.target,
                    'status': kr.status
                }
                for kr in goal.key_results
            ],
            'artifacts': goal.artifacts,
            'evidence': goal.evidence
        }
        
        # Add sequences if not already present
        if 'sequences' not in obj_data:
            obj_data['sequences'] = {
                'created': goal.created_sequence,
                'current': goal.current_sequence,
                'target': goal.target_sequence
            }
        
        # Add timestamps if not already present
        if 'timestamps' not in obj_data:
            obj_data['timestamps'] = {
                'created_at': goal.created_at.isoformat(),
                'updated_at': goal.updated_at.isoformat(),
                'started_at': goal.started_at.isoformat() if goal.started_at else None,
                'completed_at': goal.actual_completion.isoformat() if goal.actual_completion else None
            }
        
        if obj_idx is not None:
            # Update existing objective
            objectives[obj_idx] = obj_data
        else:
            # Add new objective
            objectives.append(obj_data)
        
        goal_tree['objectives'] = objectives
        
        # Save updated YAML
        with open(self.goal_tree_path, 'w') as f:
            yaml.dump(goal_tree, f, default_flow_style=False, sort_keys=False)
        
        print(f"Synced goal {goal_id} to GOAL_TREE.yaml")
    
    def sync_all_timeline_to_yaml(self) -> None:
        """Sync all goals from timeline to YAML"""
        goals = self.manager.goals
        for goal_id in goals.keys():
            self.sync_timeline_to_yaml(goal_id)
    
    def detect_conflicts(self) -> List[Dict[str, Any]]:
        """
        Detect conflicts between YAML and timeline
        
        Returns list of conflict descriptions
        """
        conflicts = []
        
        if not self.goal_tree_path.exists():
            return conflicts
        
        with open(self.goal_tree_path, 'r') as f:
            goal_tree = yaml.safe_load(f)
        
        objectives = goal_tree.get('objectives', [])
        
        for obj in objectives:
            goal_id = obj.get('id')
            if not goal_id:
                continue
            
            timeline_goal = self.manager.get_goal(goal_id)
            if not timeline_goal:
                conflicts.append({
                    'goal_id': goal_id,
                    'type': 'missing_in_timeline',
                    'description': f"Goal {goal_id} exists in YAML but not in timeline"
                })
                continue
            
            # Check for status conflicts
            yaml_status = self._parse_status(obj.get('status', 'planned'))
            if yaml_status != timeline_goal.status:
                conflicts.append({
                    'goal_id': goal_id,
                    'type': 'status_mismatch',
                    'description': f"Status mismatch: YAML={yaml_status.value}, Timeline={timeline_goal.status.value}",
                    'yaml_status': yaml_status.value,
                    'timeline_status': timeline_goal.status.value
                })
            
            # Check for key result conflicts
            yaml_krs = {kr.get('id') for kr in obj.get('key_results', [])}
            timeline_krs = {kr.id for kr in timeline_goal.key_results}
            
            if yaml_krs != timeline_krs:
                conflicts.append({
                    'goal_id': goal_id,
                    'type': 'key_results_mismatch',
                    'description': f"Key results differ: YAML has {len(yaml_krs)}, Timeline has {len(timeline_krs)}",
                    'yaml_kr_ids': list(yaml_krs),
                    'timeline_kr_ids': list(timeline_krs)
                })
        
        # Check for goals in timeline but not in YAML
        for goal_id, goal in self.manager.goals.items():
            found = any(obj.get('id') == goal_id for obj in objectives)
            if not found:
                conflicts.append({
                    'goal_id': goal_id,
                    'type': 'missing_in_yaml',
                    'description': f"Goal {goal_id} exists in timeline but not in YAML"
                })
        
        return conflicts
    
    def resolve_conflicts(self, strategy: str = "timeline_wins") -> None:
        """
        Resolve conflicts based on strategy
        
        Strategies:
        - "timeline_wins": Timeline takes precedence
        - "yaml_wins": YAML takes precedence
        - "merge": Attempt to merge both
        """
        conflicts = self.detect_conflicts()
        
        if not conflicts:
            print("No conflicts detected")
            return
        
        print(f"Resolving {len(conflicts)} conflicts using strategy: {strategy}")
        
        if strategy == "timeline_wins":
            self.sync_all_timeline_to_yaml()
        elif strategy == "yaml_wins":
            # Clear timeline and reload from YAML
            self.manager.goals.clear()
            self.load_from_yaml()
        elif strategy == "merge":
            # Complex merging logic - for now, use timeline_wins
            self.sync_all_timeline_to_yaml()
        
        print(f"Resolved {len(conflicts)} conflicts")
    
    def _parse_status(self, status_str: str) -> GoalStatus:
        """Parse status string to GoalStatus enum"""
        status_map = {
            'planned': GoalStatus.PLANNED,
            'in_progress': GoalStatus.IN_PROGRESS,
            'completed': GoalStatus.COMPLETED,
            'blocked': GoalStatus.BLOCKED,
            'cancelled': GoalStatus.CANCELLED
        }
        return status_map.get(status_str.lower(), GoalStatus.PLANNED)
    
    def _calculate_progress_from_yaml(self, obj: Dict[str, Any]) -> float:
        """Calculate progress from YAML data"""
        key_results = obj.get('key_results', [])
        if not key_results:
            return 0.0
        
        # Check if any key results have completion indicators
        completed = 0
        for kr in key_results:
            # Check for status field or completion indicator
            if kr.get('status') == 'completed' or kr.get('completed', False):
                completed += 1
        
        return completed / len(key_results) if key_results else 0.0
