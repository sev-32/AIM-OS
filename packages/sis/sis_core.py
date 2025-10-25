"""
AIM-OS Self-Improvement System Core

The main orchestrator for the Self-Improvement System that coordinates
all components to enable continuous self-improvement.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid

from .meta_cognitive_analyzer import MetaCognitiveAnalyzer
from .system_usage_auditor import SystemUsageAuditor
from .performance_monitor import PerformanceMonitor
from .gap_identifier import GapIdentifier
from .improvement_implementer import ImprovementImplementer
from .continuous_learner import ContinuousLearner


@dataclass
class SISConfig:
    """Configuration for the Self-Improvement System"""
    
    # Monitoring intervals
    monitoring_interval_minutes: int = 60
    analysis_interval_minutes: int = 120
    improvement_interval_minutes: int = 240
    
    # Thresholds
    usage_threshold: float = 0.7  # Minimum system usage rate
    performance_threshold: float = 0.8  # Minimum performance threshold
    improvement_threshold: float = 0.1  # Minimum improvement threshold
    
    # Enable/disable components
    enable_meta_cognitive_analysis: bool = True
    enable_system_usage_auditing: bool = True
    enable_performance_monitoring: bool = True
    enable_gap_identification: bool = True
    enable_improvement_implementation: bool = True
    enable_continuous_learning: bool = True


@dataclass
class SISStatus:
    """Status of the Self-Improvement System"""
    
    is_running: bool = False
    last_monitoring: Optional[datetime] = None
    last_analysis: Optional[datetime] = None
    last_improvement: Optional[datetime] = None
    total_improvements: int = 0
    successful_improvements: int = 0
    failed_improvements: int = 0
    current_gaps: int = 0
    system_usage_rate: float = 0.0
    performance_score: float = 0.0


class SISCore:
    """
    Core Self-Improvement System orchestrator
    
    Coordinates all SIS components to enable continuous self-improvement
    through meta-cognitive analysis, system usage auditing, performance
    monitoring, gap identification, improvement implementation, and
    continuous learning.
    """
    
    def __init__(self, config: SISConfig):
        """Initialize the SIS Core"""
        self.config = config
        self.status = SISStatus()
        
        # Initialize components
        self.meta_cognitive_analyzer = MetaCognitiveAnalyzer()
        self.system_usage_auditor = SystemUsageAuditor()
        self.performance_monitor = PerformanceMonitor()
        self.gap_identifier = GapIdentifier()
        self.improvement_implementer = ImprovementImplementer()
        self.continuous_learner = ContinuousLearner()
        
        # Improvement history
        self.improvement_history: List[Dict[str, Any]] = []
        self.learning_history: List[Dict[str, Any]] = []
    
    def start(self) -> None:
        """Start the Self-Improvement System"""
        self.status.is_running = True
        self.status.last_monitoring = datetime.now()
        
        # Start monitoring loop
        self._monitoring_loop()
    
    def stop(self) -> None:
        """Stop the Self-Improvement System"""
        self.status.is_running = False
    
    def _monitoring_loop(self) -> None:
        """Main monitoring and improvement loop"""
        while self.status.is_running:
            try:
                # Monitor system usage and performance
                if self.config.enable_system_usage_auditing:
                    self._monitor_system_usage()
                
                if self.config.enable_performance_monitoring:
                    self._monitor_performance()
                
                # Analyze and identify gaps
                if self.config.enable_meta_cognitive_analysis:
                    self._analyze_meta_cognitive()
                
                if self.config.enable_gap_identification:
                    self._identify_gaps()
                
                # Implement improvements
                if self.config.enable_improvement_implementation:
                    self._implement_improvements()
                
                # Learn and adapt
                if self.config.enable_continuous_learning:
                    self._learn_and_adapt()
                
                # Update status
                self._update_status()
                
            except Exception as e:
                # Log error and continue
                print(f"SIS Error: {e}")
                continue
    
    def _monitor_system_usage(self) -> None:
        """Monitor system usage"""
        usage_data = self.system_usage_auditor.collect_usage_data()
        self.system_usage_auditor.analyze_usage(usage_data)
        
        # Update status
        self.status.system_usage_rate = usage_data.overall_usage_rate
        self.status.last_monitoring = datetime.now()
    
    def _monitor_performance(self) -> None:
        """Monitor performance"""
        performance_data = self.performance_monitor.collect_performance_data()
        self.performance_monitor.analyze_performance(performance_data)
        
        # Update status
        self.status.performance_score = performance_data.overall_score
        self.status.last_monitoring = datetime.now()
    
    def _analyze_meta_cognitive(self) -> None:
        """Analyze meta-cognitive processes"""
        decision_data = self.meta_cognitive_analyzer.collect_decision_data()
        analysis_result = self.meta_cognitive_analyzer.analyze_decisions(decision_data)
        
        # Store analysis results
        self._store_analysis_result(analysis_result)
    
    def _identify_gaps(self) -> None:
        """Identify improvement gaps"""
        gaps = self.gap_identifier.identify_gaps()
        self.status.current_gaps = len(gaps)
        
        # Store gap analysis
        self._store_gap_analysis(gaps)
    
    def _implement_improvements(self) -> None:
        """Implement improvements"""
        if self.status.current_gaps > 0:
            improvements = self.improvement_implementer.plan_improvements()
            
            for improvement in improvements:
                try:
                    result = self.improvement_implementer.implement_improvement(improvement)
                    
                    if result.success:
                        self.status.successful_improvements += 1
                        self.improvement_history.append({
                            "id": str(uuid.uuid4()),
                            "timestamp": datetime.now(),
                            "improvement": improvement,
                            "result": result,
                            "success": True
                        })
                    else:
                        self.status.failed_improvements += 1
                        self.improvement_history.append({
                            "id": str(uuid.uuid4()),
                            "timestamp": datetime.now(),
                            "improvement": improvement,
                            "result": result,
                            "success": False
                        })
                    
                    self.status.total_improvements += 1
                    
                except Exception as e:
                    self.status.failed_improvements += 1
                    print(f"Improvement implementation error: {e}")
    
    def _learn_and_adapt(self) -> None:
        """Learn from improvements and adapt"""
        if self.improvement_history:
            learning_result = self.continuous_learner.learn_from_improvements(
                self.improvement_history
            )
            
            # Store learning results
            self.learning_history.append({
                "id": str(uuid.uuid4()),
                "timestamp": datetime.now(),
                "learning_result": learning_result
            })
            
            # Adapt based on learning
            self.continuous_learner.adapt_system(learning_result)
    
    def _update_status(self) -> None:
        """Update system status"""
        self.status.last_improvement = datetime.now()
    
    def _store_analysis_result(self, result: Any) -> None:
        """Store analysis result"""
        # Store in memory system for persistence
        pass
    
    def _store_gap_analysis(self, gaps: List[Any]) -> None:
        """Store gap analysis"""
        # Store in memory system for persistence
        pass
    
    def get_status(self) -> SISStatus:
        """Get current system status"""
        return self.status
    
    def get_improvement_history(self) -> List[Dict[str, Any]]:
        """Get improvement history"""
        return self.improvement_history
    
    def get_learning_history(self) -> List[Dict[str, Any]]:
        """Get learning history"""
        return self.learning_history
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics"""
        return {
            "system_usage_rate": self.status.system_usage_rate,
            "performance_score": self.status.performance_score,
            "total_improvements": self.status.total_improvements,
            "successful_improvements": self.status.successful_improvements,
            "failed_improvements": self.status.failed_improvements,
            "current_gaps": self.status.current_gaps,
            "success_rate": (
                self.status.successful_improvements / self.status.total_improvements
                if self.status.total_improvements > 0 else 0.0
            )
        }
