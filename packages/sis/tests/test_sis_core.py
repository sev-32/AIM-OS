"""
Tests for AIM-OS Self-Improvement System Core

Comprehensive tests for the SIS Core functionality including
meta-cognitive analysis, system usage auditing, performance
monitoring, gap identification, improvement implementation,
and continuous learning.
"""

import pytest
from datetime import datetime
from unittest.mock import Mock, patch

from sis.sis_core import SISCore, SISConfig, SISStatus
from sis.meta_cognitive_analyzer import MetaCognitiveAnalyzer, DecisionType


class TestSISCore:
    """Test cases for SIS Core functionality"""
    
    def test_sis_initialization(self):
        """Test SIS Core initialization"""
        config = SISConfig()
        sis = SISCore(config)
        
        assert sis.config == config
        assert isinstance(sis.status, SISStatus)
        assert not sis.status.is_running
        assert sis.improvement_history == []
        assert sis.learning_history == []
    
    def test_sis_start_stop(self):
        """Test SIS Core start and stop functionality"""
        config = SISConfig()
        sis = SISCore(config)
        
        # Test start
        sis.start()
        assert sis.status.is_running
        assert sis.status.last_monitoring is not None
        
        # Test stop
        sis.stop()
        assert not sis.status.is_running
    
    def test_get_status(self):
        """Test getting SIS status"""
        config = SISConfig()
        sis = SISCore(config)
        
        status = sis.get_status()
        assert isinstance(status, SISStatus)
        assert not status.is_running
        assert status.total_improvements == 0
        assert status.successful_improvements == 0
        assert status.failed_improvements == 0
    
    def test_get_performance_metrics(self):
        """Test getting performance metrics"""
        config = SISConfig()
        sis = SISCore(config)
        
        # Set some test data
        sis.status.system_usage_rate = 0.8
        sis.status.performance_score = 0.9
        sis.status.total_improvements = 10
        sis.status.successful_improvements = 8
        sis.status.failed_improvements = 2
        
        metrics = sis.get_performance_metrics()
        
        assert metrics["system_usage_rate"] == 0.8
        assert metrics["performance_score"] == 0.9
        assert metrics["total_improvements"] == 10
        assert metrics["successful_improvements"] == 8
        assert metrics["failed_improvements"] == 2
        assert metrics["success_rate"] == 0.8  # 8/10
    
    def test_get_performance_metrics_zero_improvements(self):
        """Test getting performance metrics with zero improvements"""
        config = SISConfig()
        sis = SISCore(config)
        
        metrics = sis.get_performance_metrics()
        assert metrics["success_rate"] == 0.0


class TestMetaCognitiveAnalyzer:
    """Test cases for Meta-Cognitive Analyzer"""
    
    def test_meta_cognitive_analyzer_initialization(self):
        """Test Meta-Cognitive Analyzer initialization"""
        analyzer = MetaCognitiveAnalyzer()
        
        assert analyzer.decisions == []
        assert analyzer.patterns == []
    
    def test_record_decision(self):
        """Test recording a decision"""
        analyzer = MetaCognitiveAnalyzer()
        
        decision = analyzer.record_decision(
            decision_type=DecisionType.DOCUMENTATION,
            context="User requested documentation",
            rationale="Need to document the system",
            confidence=0.8
        )
        
        assert decision.decision_type == DecisionType.DOCUMENTATION
        assert decision.context == "User requested documentation"
        assert decision.rationale == "Need to document the system"
        assert decision.confidence == 0.8
        assert len(analyzer.decisions) == 1
    
    def test_analyze_decisions_empty(self):
        """Test analyzing empty decision list"""
        analyzer = MetaCognitiveAnalyzer()
        
        analysis = SGIS.analyze_decisions([])
        
        assert analysis.total_decisions == 0
        assert analysis.patterns == []
        assert analysis.efficiency_score == 0.0
        assert analysis.consistency_score == 0.0
        assert analysis.proactive_score == 0.0
        assert analysis.recommendations == []
    
    def test_analyze_decisions_with_data(self):
        """Test analyzing decisions with data"""
        analyzer = MetaCognitiveAnalyzer()
        
        # Record some test decisions
        analyzer.record_decision(
            decision_type=DecisionType.DOCUMENTATION,
            context="User requested documentation",
            rationale="Need to document the system",
            confidence=0.8,
            success=True
        )
        
        analyzer.record_decision(
            decision_type=DecisionType.SYSTEM_SELECTION,
            context="Need to select systems for task",
            rationale="Select relevant systems",
            confidence=0.9,
            success=True
        )
        
        decisions = analyzer.collect_decision_data()
        analysis = analyzer.analyze_decisions(decisions)
        
        assert analysis.total_decisions == 2
        assert analysis.efficiency_score == 1.0  # Both successful
        assert analysis.proactive_score == 0.0  # Both reactive
        assert len(analysis.patterns) > 0
        assert len(analysis.recommendations) > 0
    
    def test_calculate_efficiency_score(self):
        """Test efficiency score calculation"""
        analyzer = MetaCognitiveAnalyzer()
        
        # Test with successful decisions
        decisions = [
            Mock(success=True),
            Mock(success=True),
            Mock(success=False)
        ]
        
        efficiency_score = analyzer._calculate_efficiency_score(decisions)
        assert efficiency_score == 2/3  # 2 successful out of 3 total
    
    def test_calculate_consistency_score(self):
        """Test consistency score calculation"""
        analyzer = MetaCognitiveAnalyzer()
        
        # Test with consistent decisions
        decisions = [
            Mock(decision_type=DecisionType.DOCUMENTATION, confidence=0.8),
            Mock(decision_type=DecisionType.DOCUMENTATION, confidence=0.9),
            Mock(decision_type=DecisionType.SYSTEM_SELECTION, confidence=0.7)
        ]
        
        consistency_score = analyzer._calculate_consistency_score(decisions)
        assert 0.0 <= consistency_score <= 1.0
    
    def test_calculate_proactive_score(self):
        """Test proactive score calculation"""
        analyzer = MetaCognitiveAnalyzer()
        
        # Test with mixed reactive/proactive decisions
        decisions = [
            Mock(context="User requested documentation"),
            Mock(context="Need to select systems for task"),
            Mock(context="Anticipating user needs")
        ]
        
        proactive_score = analyzer._calculate_proactive_score(decisions)
        assert proactive_score == 1/3  # 1 proactive out of 3 total


class TestSISIntegration:
    """Integration tests for SIS components"""
    
    def test_sis_component_integration(self):
        """Test integration between SIS components"""
        config = SISConfig()
        sis = SISCore(config)
        
        # Test that all components are initialized
        assert isinstance(sis.meta_cognitive_analyzer, MetaCognitiveAnalyzer)
        assert isinstance(sis.system_usage_auditor, Mock)  # Mocked in tests
        assert isinstance(sis.performance_monitor, Mock)  # Mocked in tests
        assert isinstance(sis.gap_identifier, Mock)  # Mocked in tests
        assert isinstance(sis.improvement_implementer, Mock)  # Mocked in tests
        assert isinstance(sis.continuous_learner, Mock)  # Mocked in tests
    
    @patch('sis.sis_core.SystemUsageAuditor')
    @patch('sis.sis_core.PerformanceMonitor')
    @patch('sis.sis_core.GapIdentifier')
    @patch('sis.sis_core.ImprovementImplementer')
    @patch('sis.sis_core.ContinuousLearner')
    def test_sis_monitoring_loop(self, mock_learner, mock_implementer, mock_gap_id, mock_perf, mock_auditor):
        """Test SIS monitoring loop functionality"""
        config = SISConfig()
        config.monitoring_interval_minutes = 0.01  # Very short interval for testing
        
        sis = SISCore(config)
        
        # Mock the components
        mock_auditor.return_value.collect_usage_data.return_value = Mock(overall_usage_rate=0.8)
        mock_perf.return_value.collect_performance_data.return_value = Mock(overall_score=0.9)
        mock_gap_id.return_value.identify_gaps.return_value = []
        mock_implementer.return_value.plan_improvements.return_value = []
        
        # Start SIS (this will run the monitoring loop)
        sis.start()
        
        # Let it run briefly
        import time
        time.sleep(0.1)
        
        # Stop SIS
        sis.stop()
        
        # Verify components were called
        assert sis.status.is_running is False
        assert sis.status.system_usage_rate == 0.8
        assert sis.status.performance_score == 0.9


if __name__ == "__main__":
    pytest.main([__file__])
