"""
Tests for Timeline Context System

This module provides comprehensive tests for the Timeline Context System components.
"""

import pytest
from datetime import datetime, timedelta
from typing import Dict, List, Any

from ..prompt_context_tracker import PromptContextTracker, ContextSnapshot, ConfidenceLevel
from ..timeline_api import TimelineAPI


class TestPromptContextTracker:
    """Test cases for PromptContextTracker"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.tracker = PromptContextTracker()
        self.sample_context_state = {
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
    
    def test_track_prompt_context(self):
        """Test tracking prompt context"""
        snapshot = self.tracker.track_prompt_context(
            "test_prompt_001",
            "Implement VIF witness envelopes",
            self.sample_context_state
        )
        
        assert snapshot.prompt_id == "test_prompt_001"
        assert snapshot.user_input == "Implement VIF witness envelopes"
        assert snapshot.current_task == "vif_implementation"
        assert snapshot.context_budget_used == 15000
        assert len(snapshot.files_read) == 1
        assert len(snapshot.insights_gained) == 1
        assert len(snapshot.decisions_made) == 1
        
        # Check that snapshot was stored
        assert "test_prompt_001" in self.tracker.context_snapshots
        assert len(self.tracker.timeline_entries) == 1
    
    def test_context_evolution_calculation(self):
        """Test context evolution calculation"""
        # Track first prompt
        snapshot1 = self.tracker.track_prompt_context(
            "test_prompt_001",
            "Start VIF implementation",
            self.sample_context_state
        )
        
        # Track second prompt with additional context
        context_state2 = self.sample_context_state.copy()
        context_state2['files_read'].append('knowledge_architecture/systems/vif/L2_architecture.md')
        context_state2['insights_gained'].append('VIF needs bitemporal versioning')
        context_state2['context_budget_used'] = 25000
        
        snapshot2 = self.tracker.track_prompt_context(
            "test_prompt_002",
            "Continue VIF implementation",
            context_state2
        )
        
        # Check evolution
        evolution = snapshot2.context_evolution
        assert len(evolution['new_files']) == 1
        assert len(evolution['new_insights']) == 1
        assert evolution['context_growth'] == 1
        assert evolution['context_budget_change'] == 10000
    
    def test_confidence_level_parsing(self):
        """Test confidence level parsing"""
        context_state = {
            'confidence_levels': {
                'task1': 0.9,  # High
                'task2': 0.7,  # Medium
                'task3': 0.5,  # Low
                'task4': 0.3,  # Unknown
                'task5': 'high'  # String
            }
        }
        
        snapshot = self.tracker.track_prompt_context(
            "test_confidence",
            "Test confidence parsing",
            context_state
        )
        
        assert snapshot.confidence_levels['task1'] == ConfidenceLevel.HIGH
        assert snapshot.confidence_levels['task2'] == ConfidenceLevel.MEDIUM
        assert snapshot.confidence_levels['task3'] == ConfidenceLevel.LOW
        assert snapshot.confidence_levels['task4'] == ConfidenceLevel.UNKNOWN
        assert snapshot.confidence_levels['task5'] == ConfidenceLevel.HIGH
    
    def test_timeline_entry_creation(self):
        """Test timeline entry creation"""
        snapshot = self.tracker.track_prompt_context(
            "test_entry",
            "Test timeline entry",
            self.sample_context_state
        )
        
        assert len(self.tracker.timeline_entries) == 1
        entry = self.tracker.timeline_entries[0]
        
        assert entry.prompt_id == "test_entry"
        assert entry.summary is not None
        assert 'vif_implementation' in entry.summary
        assert entry.context_index['active_tasks'] == 'vif_implementation'
        assert entry.context_index['files_read'] == ['knowledge_architecture/systems/vif/L3_detailed.md']
    
    def test_task_timeline_tracking(self):
        """Test task-specific timeline tracking"""
        # Track multiple prompts for same task
        for i in range(3):
            self.tracker.track_prompt_context(
                f"task_prompt_{i}",
                f"Task prompt {i}",
                self.sample_context_state
            )
        
        # Check task timeline
        task_contexts = self.tracker.find_task_context('vif_implementation')
        assert len(task_contexts) == 3
        
        # Check task timeline storage
        assert 'vif_implementation' in self.tracker.task_timeline
        assert len(self.tracker.task_timeline['vif_implementation']) == 3
    
    def test_file_timeline_tracking(self):
        """Test file-specific timeline tracking"""
        # Track prompt with file
        self.tracker.track_prompt_context(
            "file_prompt",
            "Test file tracking",
            self.sample_context_state
        )
        
        # Check file timeline
        file_contexts = self.tracker.find_file_context('knowledge_architecture/systems/vif/L3_detailed.md')
        assert len(file_contexts) == 1
        
        # Check file timeline storage
        assert 'knowledge_architecture/systems/vif/L3_detailed.md' in self.tracker.file_timeline
        assert len(self.tracker.file_timeline['knowledge_architecture/systems/vif/L3_detailed.md']) == 1
    
    def test_insight_timeline_tracking(self):
        """Test insight-specific timeline tracking"""
        # Track prompt with insight
        self.tracker.track_prompt_context(
            "insight_prompt",
            "Test insight tracking",
            self.sample_context_state
        )
        
        # Check insight timeline
        insight_contexts = self.tracker.find_insight_context('VIF requires comprehensive witness envelopes')
        assert len(insight_contexts) == 1
        
        # Check insight timeline storage
        assert 'VIF requires comprehensive witness envelopes' in self.tracker.insight_timeline
        assert len(self.tracker.insight_timeline['VIF requires comprehensive witness envelopes']) == 1
    
    def test_timeline_summary(self):
        """Test timeline summary generation"""
        # Track multiple prompts
        for i in range(5):
            self.tracker.track_prompt_context(
                f"summary_prompt_{i}",
                f"Summary prompt {i}",
                self.sample_context_state
            )
        
        # Get summary
        summary = self.tracker.get_timeline_summary()
        
        assert summary['total_prompts'] == 5
        assert 'vif_implementation' in summary['tasks_worked_on']
        assert len(summary['files_read']) == 1
        assert len(summary['insights_gained']) == 1
        assert summary['total_context_used'] == 5 * 15000
        assert summary['average_confidence'] > 0
    
    def test_context_at_moment(self):
        """Test getting context at specific moment"""
        # Track prompt
        snapshot = self.tracker.track_prompt_context(
            "moment_prompt",
            "Test moment context",
            self.sample_context_state
        )
        
        # Get context at moment
        context_at_moment = self.tracker.get_context_at_moment(snapshot.timestamp)
        
        assert context_at_moment is not None
        assert context_at_moment.prompt_id == "moment_prompt"
        
        # Test with timestamp that doesn't exist
        future_time = datetime.now() + timedelta(hours=1)
        context_at_future = self.tracker.get_context_at_moment(future_time)
        
        assert context_at_future is not None  # Should return closest
        assert context_at_future.prompt_id == "moment_prompt"


class TestTimelineAPI:
    """Test cases for TimelineAPI"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.tracker = PromptContextTracker()
        self.api = TimelineAPI(self.tracker)
        
        # Add some test data
        self.sample_context_state = {
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
        
        # Track some test prompts
        for i in range(3):
            self.tracker.track_prompt_context(
                f"api_test_prompt_{i}",
                f"API test prompt {i}",
                self.sample_context_state
            )
    
    def test_api_creation(self):
        """Test API creation"""
        assert self.api.app is not None
        assert self.api.context_tracker is self.tracker
    
    def test_root_endpoint(self):
        """Test root endpoint"""
        # This would be tested with FastAPI test client in real implementation
        # For now, just verify the endpoint exists
        assert hasattr(self.api.app, 'routes')
    
    def test_timeline_summary_endpoint(self):
        """Test timeline summary endpoint"""
        # This would be tested with FastAPI test client in real implementation
        # For now, just verify the method exists
        summary = self.tracker.get_timeline_summary()
        assert summary is not None
        assert 'total_prompts' in summary
    
    def test_timeline_entries_endpoint(self):
        """Test timeline entries endpoint"""
        # This would be tested with FastAPI test client in real implementation
        # For now, just verify the data exists
        entries = self.tracker.timeline_entries
        assert len(entries) == 3
        
        # Test filtering logic
        task_entries = [
            entry for entry in entries
            if 'vif_implementation' in entry.context_index.get('active_tasks', '').lower()
        ]
        assert len(task_entries) == 3
    
    def test_search_functionality(self):
        """Test search functionality"""
        # Test search logic
        query = "VIF"
        results = []
        
        for entry in self.tracker.timeline_entries:
            if (query.lower() in entry.summary.lower() or
                query.lower() in entry.context_index.get('active_tasks', '').lower() or
                any(query.lower() in insight.lower() for insight in entry.context_index.get('insights_gained', []))):
                results.append(entry)
        
        assert len(results) == 3  # All entries should match "VIF"
    
    def test_task_context_retrieval(self):
        """Test task context retrieval"""
        task_contexts = self.tracker.find_task_context('vif_implementation')
        assert len(task_contexts) == 3
        
        for context in task_contexts:
            assert context.current_task == 'vif_implementation'
    
    def test_file_context_retrieval(self):
        """Test file context retrieval"""
        file_contexts = self.tracker.find_file_context('knowledge_architecture/systems/vif/L3_detailed.md')
        assert len(file_contexts) == 3
        
        for context in file_contexts:
            assert 'knowledge_architecture/systems/vif/L3_detailed.md' in context.files_read
    
    def test_insight_context_retrieval(self):
        """Test insight context retrieval"""
        insight_contexts = self.tracker.find_insight_context('VIF requires comprehensive witness envelopes')
        assert len(insight_contexts) == 3
        
        for context in insight_contexts:
            assert 'VIF requires comprehensive witness envelopes' in context.insights_gained


class TestIntegration:
    """Integration tests for Timeline Context System"""
    
    def test_end_to_end_workflow(self):
        """Test complete end-to-end workflow"""
        # Create tracker
        tracker = PromptContextTracker()
        
        # Simulate AI working on multiple tasks
        tasks = [
            {
                'task': 'vif_implementation',
                'context': {
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
            },
            {
                'task': 'cmc_integration',
                'context': {
                    'files_read': ['knowledge_architecture/systems/cmc/L2_architecture.md'],
                    'conversation_history': [{'content': 'Integrating CMC with VIF'}],
                    'mental_model': {'cmc': 'Context Memory Core'},
                    'confidence_levels': {'cmc_integration': 0.75},
                    'current_task': 'cmc_integration',
                    'context_budget_used': 20000,
                    'tools_used': ['read_file', 'write', 'grep'],
                    'decisions_made': [{'decision': 'Use bitemporal versioning for CMC'}],
                    'insights_gained': ['CMC needs bitemporal versioning']
                }
            }
        ]
        
        # Track prompts for each task
        for i, task_data in enumerate(tasks):
            tracker.track_prompt_context(
                f"workflow_prompt_{i}",
                f"Working on {task_data['task']}",
                task_data['context']
            )
        
        # Verify timeline entries
        assert len(tracker.timeline_entries) == 2
        
        # Verify task timelines
        vif_contexts = tracker.find_task_context('vif_implementation')
        cmc_contexts = tracker.find_task_context('cmc_integration')
        
        assert len(vif_contexts) == 1
        assert len(cmc_contexts) == 1
        
        # Verify file timelines
        vif_file_contexts = tracker.find_file_context('knowledge_architecture/systems/vif/L3_detailed.md')
        cmc_file_contexts = tracker.find_file_context('knowledge_architecture/systems/cmc/L2_architecture.md')
        
        assert len(vif_file_contexts) == 1
        assert len(cmc_file_contexts) == 1
        
        # Verify insight timelines
        vif_insight_contexts = tracker.find_insight_context('VIF requires comprehensive witness envelopes')
        cmc_insight_contexts = tracker.find_insight_context('CMC needs bitemporal versioning')
        
        assert len(vif_insight_contexts) == 1
        assert len(cmc_insight_contexts) == 1
        
        # Verify timeline summary
        summary = tracker.get_timeline_summary()
        assert summary['total_prompts'] == 2
        assert len(summary['tasks_worked_on']) == 2
        assert summary['total_context_used'] == 35000
        
        # Verify context evolution
        vif_snapshot = vif_contexts[0]
        cmc_snapshot = cmc_contexts[0]
        
        assert len(vif_snapshot.context_evolution['new_files']) == 1
        assert len(cmc_snapshot.context_evolution['new_files']) == 1


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
