"""
Unit tests for GoalTimelineNode
"""

import pytest
from datetime import datetime
from packages.timeline_context_system.goal_timeline_node import (
    GoalTimelineNode,
    GoalStatus,
    GoalPriority,
    KeyResult,
    EmotionalContext
)


class TestGoalTimelineNode:
    """Test GoalTimelineNode creation and methods"""
    
    def test_create_goal_timeline_node(self):
        """Test creating a basic goal timeline node"""
        goal = GoalTimelineNode(
            node_id="test-node-1",
            goal_id="OBJ-01",
            name="Test Goal",
            description="Test description",
            created_sequence=0,
            current_sequence=0,
            target_sequence=10
        )
        
        assert goal.node_id == "test-node-1"
        assert goal.goal_id == "OBJ-01"
        assert goal.name == "Test Goal"
        assert goal.status == GoalStatus.PLANNED
        assert goal.progress == 0.0
        assert goal.priority == GoalPriority.MEDIUM
    
    def test_update_progress(self):
        """Test updating goal progress"""
        goal = GoalTimelineNode(
            node_id="test-node-1",
            goal_id="OBJ-01",
            name="Test Goal",
            description="Test description",
            created_sequence=0,
            current_sequence=0,
            target_sequence=10
        )
        
        goal.update_progress(0.5, "Halfway milestone")
        assert goal.progress == 0.5
        assert 'milestones' in goal.metadata
        assert len(goal.metadata['milestones']) == 1
    
    def test_update_progress_invalid(self):
        """Test updating progress with invalid value"""
        goal = GoalTimelineNode(
            node_id="test-node-1",
            goal_id="OBJ-01",
            name="Test Goal",
            description="Test description",
            created_sequence=0,
            current_sequence=0,
            target_sequence=10
        )
        
        with pytest.raises(ValueError):
            goal.update_progress(1.5)  # Invalid: > 1.0
        
        with pytest.raises(ValueError):
            goal.update_progress(-0.5)  # Invalid: < 0.0
    
    def test_update_status(self):
        """Test updating goal status"""
        goal = GoalTimelineNode(
            node_id="test-node-1",
            goal_id="OBJ-01",
            name="Test Goal",
            description="Test description",
            created_sequence=0,
            current_sequence=0,
            target_sequence=10
        )
        
        goal.update_status(GoalStatus.IN_PROGRESS)
        assert goal.status == GoalStatus.IN_PROGRESS
        assert goal.started_at is not None
        
        goal.update_status(GoalStatus.COMPLETED)
        assert goal.status == GoalStatus.COMPLETED
        assert goal.actual_completion is not None
        assert goal.progress == 1.0
    
    def test_add_key_result(self):
        """Test adding key results"""
        goal = GoalTimelineNode(
            node_id="test-node-1",
            goal_id="OBJ-01",
            name="Test Goal",
            description="Test description",
            created_sequence=0,
            current_sequence=0,
            target_sequence=10
        )
        
        kr = KeyResult(
            id="KR-1",
            name="First KR",
            metric="Count",
            target="10"
        )
        
        goal.add_key_result(kr)
        assert len(goal.key_results) == 1
        assert goal.total_krs == 1
    
    def test_complete_key_result(self):
        """Test completing a key result"""
        goal = GoalTimelineNode(
            node_id="test-node-1",
            goal_id="OBJ-01",
            name="Test Goal",
            description="Test description",
            created_sequence=0,
            current_sequence=0,
            target_sequence=10
        )
        
        kr = KeyResult(
            id="KR-1",
            name="First KR",
            metric="Count",
            target="10"
        )
        
        goal.add_key_result(kr)
        goal.complete_key_result("KR-1")
        
        assert goal.completed_krs == 1
        assert goal.key_results[0].completed is True
        assert goal.progress == 1.0  # 1/1 KRs completed
    
    def test_link_goals(self):
        """Test linking goals"""
        goal = GoalTimelineNode(
            node_id="test-node-1",
            goal_id="OBJ-01",
            name="Test Goal",
            description="Test description",
            created_sequence=0,
            current_sequence=0,
            target_sequence=10
        )
        
        goal.link_goal("OBJ-02")
        assert "OBJ-02" in goal.linked_goals
    
    def test_add_artifact(self):
        """Test adding artifacts"""
        goal = GoalTimelineNode(
            node_id="test-node-1",
            goal_id="OBJ-01",
            name="Test Goal",
            description="Test description",
            created_sequence=0,
            current_sequence=0,
            target_sequence=10
        )
        
        goal.add_artifact("path/to/artifact.py")
        assert "path/to/artifact.py" in goal.artifacts
    
    def test_add_evidence(self):
        """Test adding evidence"""
        goal = GoalTimelineNode(
            node_id="test-node-1",
            goal_id="OBJ-01",
            name="Test Goal",
            description="Test description",
            created_sequence=0,
            current_sequence=0,
            target_sequence=10
        )
        
        goal.add_evidence("path/to/evidence.md")
        assert "path/to/evidence.md" in goal.evidence
    
    def test_to_dict(self):
        """Test serialization to dictionary"""
        goal = GoalTimelineNode(
            node_id="test-node-1",
            goal_id="OBJ-01",
            name="Test Goal",
            description="Test description",
            created_sequence=0,
            current_sequence=0,
            target_sequence=10
        )
        
        data = goal.to_dict()
        assert data['node_id'] == "test-node-1"
        assert data['goal_id'] == "OBJ-01"
        assert data['name'] == "Test Goal"
        assert data['status'] == "planned"
        assert data['progress'] == 0.0
    
    def test_from_dict(self):
        """Test deserialization from dictionary"""
        data = {
            'node_id': 'test-node-1',
            'goal_id': 'OBJ-01',
            'name': 'Test Goal',
            'description': 'Test description',
            'created_sequence': 0,
            'current_sequence': 0,
            'target_sequence': 10,
            'status': 'planned',
            'progress': 0.0,
            'confidence': 0.0,
            'priority': 'medium',
            'created_at': '2025-01-01T00:00:00',
            'started_at': None,
            'updated_at': '2025-01-01T00:00:00',
            'target_completion': None,
            'actual_completion': None,
            'key_results': [],
            'completed_krs': 0,
            'total_krs': 0,
            'emotional_context': None,
            'linked_goals': [],
            'artifacts': [],
            'evidence': [],
            'metadata': {}
        }
        
        goal = GoalTimelineNode.from_dict(data)
        assert goal.node_id == "test-node-1"
        assert goal.goal_id == "OBJ-01"
        assert goal.name == "Test Goal"
        assert goal.status == GoalStatus.PLANNED
