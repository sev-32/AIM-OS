"""
Goal Timeline Node - Integration of Goals into Timeline System

This module implements the GoalTimelineNode data model and methods for
tracking goals as timeline nodes with past/present/future tracking.
"""

from __future__ import annotations

import json
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, field
from enum import Enum


class GoalStatus(Enum):
    """Goal status enumeration"""
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    BLOCKED = "blocked"
    CANCELLED = "cancelled"


class GoalPriority(Enum):
    """Goal priority levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class KeyResult:
    """Key result for a goal"""
    id: str
    name: str
    metric: str
    target: str
    status: str = "pending"
    completed: bool = False
    completion_date: Optional[datetime] = None


@dataclass
class EmotionalContext:
    """Emotional context for goal tracking"""
    primary: str
    intensity: float  # 0.0 to 1.0
    secondary: List[str] = field(default_factory=list)
    description: Optional[str] = None


@dataclass
class GoalTimelineNode:
    """Goal as a timeline node with past/present/future tracking"""
    
    # Identity
    node_id: str
    goal_id: str  # OBJ-01, OBJ-02, etc.
    name: str
    description: str
    
    # Sequential Ordering
    created_sequence: int  # When created (past)
    current_sequence: int  # Current position (present)
    target_sequence: int  # Target completion (future)
    
    # Status Tracking
    status: GoalStatus = GoalStatus.PLANNED
    progress: float = 0.0  # 0.0 to 1.0
    confidence: float = 0.0  # Confidence in completion (VIF integration)
    priority: GoalPriority = GoalPriority.MEDIUM
    
    # Temporal Context
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    updated_at: datetime = field(default_factory=datetime.now)
    target_completion: Optional[datetime] = None
    actual_completion: Optional[datetime] = None
    
    # Key Results
    key_results: List[KeyResult] = field(default_factory=list)
    completed_krs: int = 0
    total_krs: int = 0
    
    # Emotional Context
    emotional_context: Optional[EmotionalContext] = None
    
    # Integration
    linked_goals: List[str] = field(default_factory=list)  # Other goal IDs
    artifacts: List[str] = field(default_factory=list)  # Code/docs/tests references
    evidence: List[str] = field(default_factory=list)  # Validation references
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def update_progress(self, progress: float, milestone: Optional[str] = None) -> None:
        """Update goal progress"""
        if not 0.0 <= progress <= 1.0:
            raise ValueError("Progress must be between 0.0 and 1.0")
        
        self.progress = progress
        self.updated_at = datetime.now()
        
        # Update milestone if provided
        if milestone:
            if 'milestones' not in self.metadata:
                self.metadata['milestones'] = []
            self.metadata['milestones'].append({
                'timestamp': datetime.now().isoformat(),
                'progress': progress,
                'description': milestone
            })
    
    def update_status(self, status: GoalStatus) -> None:
        """Update goal status"""
        self.status = status
        self.updated_at = datetime.now()
        
        # Set started_at when moving to in_progress
        if status == GoalStatus.IN_PROGRESS and self.started_at is None:
            self.started_at = datetime.now()
        
        # Set actual_completion when completed
        if status == GoalStatus.COMPLETED:
            self.actual_completion = datetime.now()
            self.progress = 1.0
    
    def add_key_result(self, kr: KeyResult) -> None:
        """Add a key result to the goal"""
        self.key_results.append(kr)
        self.total_krs += 1
    
    def complete_key_result(self, kr_id: str) -> None:
        """Mark a key result as completed"""
        for kr in self.key_results:
            if kr.id == kr_id:
                kr.completed = True
                kr.status = "completed"
                kr.completion_date = datetime.now()
                self.completed_krs += 1
                self.update_progress(self._calculate_progress_from_krs())
                break
    
    def _calculate_progress_from_krs(self) -> float:
        """Calculate progress based on completed key results"""
        if self.total_krs == 0:
            return 0.0
        return self.completed_krs / self.total_krs
    
    def link_goal(self, goal_id: str) -> None:
        """Link this goal to another goal"""
        if goal_id not in self.linked_goals:
            self.linked_goals.append(goal_id)
    
    def add_artifact(self, artifact_path: str) -> None:
        """Add an artifact reference"""
        if artifact_path not in self.artifacts:
            self.artifacts.append(artifact_path)
    
    def add_evidence(self, evidence_path: str) -> None:
        """Add evidence reference"""
        if evidence_path not in self.evidence:
            self.evidence.append(evidence_path)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'node_id': self.node_id,
            'goal_id': self.goal_id,
            'name': self.name,
            'description': self.description,
            'created_sequence': self.created_sequence,
            'current_sequence': self.current_sequence,
            'target_sequence': self.target_sequence,
            'status': self.status.value,
            'progress': self.progress,
            'confidence': self.confidence,
            'priority': self.priority.value,
            'created_at': self.created_at.isoformat(),
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'updated_at': self.updated_at.isoformat(),
            'target_completion': self.target_completion.isoformat() if self.target_completion else None,
            'actual_completion': self.actual_completion.isoformat() if self.actual_completion else None,
            'key_results': [
                {
                    'id': kr.id,
                    'name': kr.name,
                    'metric': kr.metric,
                    'target': kr.target,
                    'status': kr.status,
                    'completed': kr.completed,
                    'completion_date': kr.completion_date.isoformat() if kr.completion_date else None
                }
                for kr in self.key_results
            ],
            'completed_krs': self.completed_krs,
            'total_krs': self.total_krs,
            'emotional_context': {
                'primary': self.emotional_context.primary,
                'intensity': self.emotional_context.intensity,
                'secondary': self.emotional_context.secondary,
                'description': self.emotional_context.description
            } if self.emotional_context else None,
            'linked_goals': self.linked_goals,
            'artifacts': self.artifacts,
            'evidence': self.evidence,
            'metadata': self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> GoalTimelineNode:
        """Create from dictionary"""
        goal = cls(
            node_id=data['node_id'],
            goal_id=data['goal_id'],
            name=data['name'],
            description=data['description'],
            created_sequence=data['created_sequence'],
            current_sequence=data['current_sequence'],
            target_sequence=data['target_sequence'],
            status=GoalStatus(data['status']),
            progress=data['progress'],
            confidence=data['confidence'],
            priority=GoalPriority(data['priority']),
            created_at=datetime.fromisoformat(data['created_at']),
            started_at=datetime.fromisoformat(data['started_at']) if data.get('started_at') else None,
            updated_at=datetime.fromisoformat(data['updated_at']),
            target_completion=datetime.fromisoformat(data['target_completion']) if data.get('target_completion') else None,
            actual_completion=datetime.fromisoformat(data['actual_completion']) if data.get('actual_completion') else None,
            completed_krs=data['completed_krs'],
            total_krs=data['total_krs'],
            linked_goals=data.get('linked_goals', []),
            artifacts=data.get('artifacts', []),
            evidence=data.get('evidence', []),
            metadata=data.get('metadata', {})
        )
        
        # Reconstruct key results
        for kr_data in data.get('key_results', []):
            goal.add_key_result(KeyResult(
                id=kr_data['id'],
                name=kr_data['name'],
                metric=kr_data['metric'],
                target=kr_data['target'],
                status=kr_data['status'],
                completed=kr_data['completed'],
                completion_date=datetime.fromisoformat(kr_data['completion_date']) if kr_data.get('completion_date') else None
            ))
        
        # Reconstruct emotional context
        if data.get('emotional_context'):
            ec_data = data['emotional_context']
            goal.emotional_context = EmotionalContext(
                primary=ec_data['primary'],
                intensity=ec_data['intensity'],
                secondary=ec_data.get('secondary', []),
                description=ec_data.get('description')
            )
        
        return goal
