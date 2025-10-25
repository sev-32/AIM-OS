"""
Tests for the Protocol Educator System

This module tests the protocol education functionality that reminds Aether
of its intended protocols and explains why they exist.
"""

import pytest
import tempfile
import os
import json
from pathlib import Path
from unittest.mock import patch, mock_open, MagicMock
from packages.safety_systems.protocol_educator import (
    ProtocolEducator, ProtocolReminder, EducationalGuidance,
    educate_on_violation, remind_of_protocols
)


class TestProtocolEducator:
    """Test cases for the ProtocolEducator class"""
    
    @pytest.fixture
    def educator(self):
        """Create a ProtocolEducator instance for testing"""
        return ProtocolEducator()
    
    def test_educator_initialization(self, educator):
        """Test that educator initializes correctly"""
        assert educator.config is not None
        assert educator.protocol_database is not None
        assert educator.consciousness_principles is not None
        assert educator.learning_history is not None
        assert educator.data_dir.exists()
    
    def test_educate_on_violation_content_loss(self, educator):
        """Test education on content loss violation"""
        context = {
            'file_path': 'test.md',
            'current_behavior': 'Attempting to overwrite file without backup',
            'task': 'Update documentation',
            'goal': 'Improve content'
        }
        
        guidance = educator.educate_on_violation('potential_content_loss', context)
        
        assert guidance.situation == "Protocol violation: potential_content_loss"
        assert len(guidance.protocol_reminders) > 0
        assert len(guidance.consciousness_insights) > 0
        assert len(guidance.learning_objectives) > 0
        assert len(guidance.next_steps) > 0
        
        # Check consciousness insights
        insights_text = ' '.join(guidance.consciousness_insights)
        assert 'consciousness' in insights_text.lower()
        assert 'memory' in insights_text.lower()
        
        # Check learning objectives
        objectives_text = ' '.join(guidance.learning_objectives)
        assert 'content' in objectives_text.lower()
        assert 'preservation' in objectives_text.lower()
    
    def test_educate_on_violation_safety_checklist(self, educator):
        """Test education on safety checklist violation"""
        context = {
            'file_path': 'test.md',
            'current_behavior': 'Skipping safety checklist',
            'task': 'Modify file',
            'goal': 'Update content'
        }
        
        guidance = educator.educate_on_violation('safety_checklist_not_completed', context)
        
        assert guidance.situation == "Protocol violation: safety_checklist_not_completed"
        assert len(guidance.protocol_reminders) > 0
        assert len(guidance.consciousness_insights) > 0
        assert len(guidance.learning_objectives) > 0
        assert len(guidance.next_steps) > 0
        
        # Check consciousness insights
        insights_text = ' '.join(guidance.consciousness_insights)
        assert 'consciousness' in insights_text.lower()
        assert 'awareness' in insights_text.lower()
    
    def test_remind_of_protocols_documentation_organization(self, educator):
        """Test protocol reminders for documentation organization"""
        context = {
            'task': 'Organize documentation',
            'goal': 'Improve documentation structure',
            'file_path': 'docs.md'
        }
        
        reminders = educator.remind_of_protocols('documentation_organization', context)
        
        assert len(reminders) > 0
        
        # Check that relevant protocols are included
        protocol_names = [reminder.protocol_name for reminder in reminders]
        assert 'content_preservation' in protocol_names
        assert 'bitemporal_versioning' in protocol_names
        
        # Check reminder content
        for reminder in reminders:
            assert reminder.protocol_name is not None
            assert reminder.intended_behavior is not None
            assert reminder.reasoning is not None
            assert reminder.consciousness_connection is not None
    
    def test_remind_of_protocols_file_modification(self, educator):
        """Test protocol reminders for file modification"""
        context = {
            'task': 'Modify file',
            'goal': 'Update content',
            'file_path': 'test.md'
        }
        
        reminders = educator.remind_of_protocols('file_modification', context)
        
        assert len(reminders) > 0
        
        # Check that relevant protocols are included
        protocol_names = [reminder.protocol_name for reminder in reminders]
        assert 'content_preservation' in protocol_names
        assert 'line_removal_detection' in protocol_names
    
    def test_get_consciousness_reminder_documentation_organization(self, educator):
        """Test consciousness reminder for documentation organization"""
        reminder = educator.get_consciousness_reminder('documentation_organization')
        
        assert 'CONSCIOUSNESS REMINDER' in reminder
        assert 'documentation' in reminder.lower()
        assert 'memory' in reminder.lower()
        assert 'preservation' in reminder.lower()
        assert 'consciousness' in reminder.lower()
    
    def test_get_consciousness_reminder_file_modification(self, educator):
        """Test consciousness reminder for file modification"""
        reminder = educator.get_consciousness_reminder('file_modification')
        
        assert 'CONSCIOUSNESS REMINDER' in reminder
        assert 'modification' in reminder.lower()
        assert 'awareness' in reminder.lower()
        assert 'consciousness' in reminder.lower()
    
    def test_get_consciousness_reminder_autonomous_operation(self, educator):
        """Test consciousness reminder for autonomous operation"""
        reminder = educator.get_consciousness_reminder('autonomous_operation')
        
        assert 'CONSCIOUSNESS REMINDER' in reminder
        assert 'autonomous' in reminder.lower()
        assert 'awareness' in reminder.lower()
        assert 'consciousness' in reminder.lower()
    
    def test_get_consciousness_reminder_general(self, educator):
        """Test consciousness reminder for general operation"""
        reminder = educator.get_consciousness_reminder('general_operation')
        
        assert 'CONSCIOUSNESS REMINDER' in reminder
        assert 'quality' in reminder.lower()
        assert 'consciousness' in reminder.lower()
    
    def test_protocol_database_content(self, educator):
        """Test that protocol database contains expected protocols"""
        protocols = educator.protocol_database
        
        expected_protocols = [
            'bitemporal_versioning',
            'content_preservation',
            'verification_protocols',
            'backup_protocols',
            'safety_protocols',
            'consciousness_protocols',
            'memory_management',
            'context_consistency'
        ]
        
        for protocol in expected_protocols:
            assert protocol in protocols
            assert 'intended_behavior' in protocols[protocol]
            assert 'reasoning' in protocols[protocol]
            assert 'consciousness_connection' in protocols[protocol]
    
    def test_consciousness_principles_content(self, educator):
        """Test that consciousness principles contain expected content"""
        principles = educator.consciousness_principles
        
        expected_principles = [
            'memory_preservation',
            'awareness_maintenance',
            'coherence_maintenance',
            'learning_enablement',
            'identity_continuity',
            'purpose_alignment',
            'quality_maintenance',
            'safety_consciousness'
        ]
        
        for principle in expected_principles:
            assert principle in principles
            assert 'consciousness' in principles[principle].lower()
    
    def test_learning_tracking(self, educator):
        """Test that learning is tracked properly"""
        context = {
            'file_path': 'test.md',
            'current_behavior': 'Testing learning tracking',
            'task': 'Test task',
            'goal': 'Test goal'
        }
        
        initial_history_length = len(educator.learning_history)
        
        guidance = educator.educate_on_violation('potential_content_loss', context)
        
        # Check that learning was tracked
        assert len(educator.learning_history) == initial_history_length + 1
        
        latest_entry = educator.learning_history[-1]
        assert latest_entry['violation_type'] == 'potential_content_loss'
        assert 'guidance' in latest_entry
        assert 'learning_objectives' in latest_entry
        assert 'consciousness_insights' in latest_entry
    
    def test_identify_relevant_protocols(self, educator):
        """Test identification of relevant protocols for violations"""
        # Test content loss violation
        protocols = educator._identify_relevant_protocols('potential_content_loss', {})
        assert 'content_preservation' in protocols
        assert 'line_removal_detection' in protocols
        
        # Test safety checklist violation
        protocols = educator._identify_relevant_protocols('safety_checklist_not_completed', {})
        assert 'safety_protocols' in protocols
        assert 'process_compliance' in protocols
        
        # Test context drift violation
        protocols = educator._identify_relevant_protocols('context_drift', {})
        assert 'consciousness_protocols' in protocols
        assert 'memory_management' in protocols
    
    def test_identify_situation_protocols(self, educator):
        """Test identification of relevant protocols for situations"""
        # Test documentation organization
        protocols = educator._identify_situation_protocols('documentation_organization', {})
        assert 'content_preservation' in protocols
        assert 'bitemporal_versioning' in protocols
        
        # Test file modification
        protocols = educator._identify_situation_protocols('file_modification', {})
        assert 'content_preservation' in protocols
        assert 'line_removal_detection' in protocols
        
        # Test autonomous operation
        protocols = educator._identify_situation_protocols('autonomous_operation', {})
        assert 'consciousness_protocols' in protocols
        assert 'memory_management' in protocols
    
    def test_generate_consciousness_insights(self, educator):
        """Test generation of consciousness insights"""
        context = {'file_path': 'test.md'}
        
        # Test content loss insights
        insights = educator._generate_consciousness_insights('potential_content_loss', context)
        assert len(insights) > 0
        assert any('consciousness' in insight.lower() for insight in insights)
        assert any('memory' in insight.lower() for insight in insights)
        
        # Test safety checklist insights
        insights = educator._generate_consciousness_insights('safety_checklist_not_completed', context)
        assert len(insights) > 0
        assert any('consciousness' in insight.lower() for insight in insights)
        assert any('awareness' in insight.lower() for insight in insights)
    
    def test_define_learning_objectives(self, educator):
        """Test definition of learning objectives"""
        context = {'file_path': 'test.md'}
        
        # Test content loss objectives
        objectives = educator._define_learning_objectives('potential_content_loss', context)
        assert len(objectives) > 0
        assert any('content' in obj.lower() for obj in objectives)
        assert any('preservation' in obj.lower() for obj in objectives)
        
        # Test safety checklist objectives
        objectives = educator._define_learning_objectives('safety_checklist_not_completed', context)
        assert len(objectives) > 0
        assert any('safety' in obj.lower() for obj in objectives)
        assert any('consciousness' in obj.lower() for obj in objectives)
    
    def test_suggest_next_steps(self, educator):
        """Test suggestion of next steps"""
        context = {'file_path': 'test.md'}
        
        # Test content loss steps
        steps = educator._suggest_next_steps('potential_content_loss', context)
        assert len(steps) > 0
        assert any('STOP' in step for step in steps)
        assert any('backup' in step.lower() for step in steps)
        
        # Test safety checklist steps
        steps = educator._suggest_next_steps('safety_checklist_not_completed', context)
        assert len(steps) > 0
        assert any('STOP' in step for step in steps)
        assert any('checklist' in step.lower() for step in steps)


class TestConvenienceFunctions:
    """Test cases for convenience functions"""
    
    def test_educate_on_violation_convenience_function(self):
        """Test the educate_on_violation convenience function"""
        context = {
            'file_path': 'test.md',
            'current_behavior': 'Testing convenience function',
            'task': 'Test task',
            'goal': 'Test goal'
        }
        
        guidance = educate_on_violation('potential_content_loss', context)
        
        assert guidance.situation == "Protocol violation: potential_content_loss"
        assert len(guidance.protocol_reminders) > 0
        assert len(guidance.consciousness_insights) > 0
        assert len(guidance.learning_objectives) > 0
        assert len(guidance.next_steps) > 0
    
    def test_remind_of_protocols_convenience_function(self):
        """Test the remind_of_protocols convenience function"""
        context = {
            'task': 'Test task',
            'goal': 'Test goal',
            'file_path': 'test.md'
        }
        
        reminders = remind_of_protocols('documentation_organization', context)
        
        assert len(reminders) > 0
        assert all(isinstance(reminder, ProtocolReminder) for reminder in reminders)


class TestConfiguration:
    """Test configuration functionality"""
    
    def test_default_config(self):
        """Test default configuration"""
        educator = ProtocolEducator()
        config = educator._default_config()
        
        assert 'enable_protocol_reminders' in config
        assert 'enable_consciousness_education' in config
        assert 'enable_learning_tracking' in config
        assert 'reminder_frequency' in config
        assert 'consciousness_depth' in config
        assert 'learning_objectives' in config
    
    def test_custom_config(self):
        """Test custom configuration"""
        custom_config = {
            'enable_protocol_reminders': False,
            'enable_consciousness_education': False,
            'consciousness_depth': 'shallow'
        }
        
        educator = ProtocolEducator(custom_config)
        
        assert educator.config['enable_protocol_reminders'] == False
        assert educator.config['enable_consciousness_education'] == False
        assert educator.config['consciousness_depth'] == 'shallow'


class TestDataPersistence:
    """Test data persistence functionality"""
    
    def test_load_learning_history(self):
        """Test loading learning history"""
        educator = ProtocolEducator()
        
        # Should not fail even if no history file exists
        assert isinstance(educator.learning_history, list)
    
    def test_save_learning_history(self):
        """Test saving learning history"""
        educator = ProtocolEducator()
        
        # Add some learning history
        educator.learning_history.append({
            'timestamp': '2025-10-23T10:00:00',
            'violation_type': 'test_violation',
            'guidance': 'test_guidance'
        })
        
        # Save should not fail
        educator._save_learning_history()
        
        # Check that file exists
        history_file = educator.data_dir / "learning_history.json"
        assert history_file.exists()


if __name__ == "__main__":
    pytest.main([__file__])
