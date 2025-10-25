"""
Meta-Cognitive Analyzer

Analyzes AI decision-making processes and identifies patterns for improvement.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum


class DecisionType(Enum):
    """Types of decisions"""
    DOCUMENTATION = "documentation"
    SYSTEM_SELECTION = "system_selection"
    IMPLEMENTATION = "implementation"
    KNOWLEDGE_CAPTURE = "knowledge_capture"
    INTEGRATION = "integration"


class PatternType(Enum):
    """Types of patterns"""
    REACTIVE = "reactive"
    PROACTIVE = "proactive"
    CONSISTENT = "consistent"
    INCONSISTENT = "inconsistent"
    EFFICIENT = "efficient"
    INEFFICIENT = "inefficient"


@dataclass
class Decision:
    """Represents a decision made by the AI"""
    
    id: str
    timestamp: datetime
    decision_type: DecisionType
    context: str
    rationale: str
    confidence: float
    outcome: Optional[str] = None
    success: Optional[bool] = None


@dataclass
class DecisionPattern:
    """Represents a pattern in decision-making"""
    
    pattern_type: PatternType
    frequency: int
    confidence: float
    examples: List[Decision]
    description: str


@dataclass
class MetaCognitiveAnalysis:
    """Results of meta-cognitive analysis"""
    
    total_decisions: int
    patterns: List[DecisionPattern]
    efficiency_score: float
    consistency_score: float
    proactive_score: float
    recommendations: List[str]
    timestamp: datetime


class MetaCognitiveAnalyzer:
    """
    Analyzes AI decision-making processes and identifies patterns
    
    Provides insights into how the AI makes decisions, identifies
    patterns, detects biases, and recommends improvements.
    """
    
    def __init__(self):
        """Initialize the Meta-Cognitive Analyzer"""
        self.decisions: List[Decision] = []
        self.patterns: List[DecisionPattern] = []
    
    def record_decision(
        self,
        decision_type: DecisionType,
        context: str,
        rationale: str,
        confidence: float,
        outcome: Optional[str] = None,
        success: Optional[bool] = None
    ) -> Decision:
        """Record a decision for analysis"""
        
        decision = Decision(
            id=f"decision_{len(self.decisions) + 1}",
            timestamp=datetime.now(),
            decision_type=decision_type,
            context=context,
            rationale=rationale,
            confidence=confidence,
            outcome=outcome,
            success=success
        )
        
        self.decisions.append(decision)
        return decision
    
    def collect_decision_data(self) -> List[Decision]:
        """Collect decision data for analysis"""
        return self.decisions.copy()
    
    def analyze_decisions(self, decisions: List[Decision]) -> MetaCognitiveAnalysis:
        """Analyze decisions and identify patterns"""
        
        if not decisions:
            return MetaCognitiveAnalysis(
                total_decisions=0,
                patterns=[],
                efficiency_score=0.0,
                consistency_score=0.0,
                proactive_score=0.0,
                recommendations=[],
                timestamp=datetime.now()
            )
        
        # Identify patterns
        patterns = self._identify_patterns(decisions)
        
        # Calculate scores
        efficiency_score = self._calculate_efficiency_score(decisions)
        consistency_score = self._calculate_consistency_score(decisions)
        proactive_score = self._calculate_proactive_score(decisions)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(decisions, patterns)
        
        return MetaCognitiveAnalysis(
            total_decisions=len(decisions),
            patterns=patterns,
            efficiency_score=efficiency_score,
            consistency_score=consistency_score,
            proactive_score=proactive_score,
            recommendations=recommendations,
            timestamp=datetime.now()
        )
    
    def _identify_patterns(self, decisions: List[Decision]) -> List[DecisionPattern]:
        """Identify patterns in decisions"""
        patterns = []
        
        # Analyze decision types
        decision_types = {}
        for decision in decisions:
            if decision.decision_type not in decision_types:
                decision_types[decision.decision_type] = []
            decision_types[decision.decision_type].append(decision)
        
        # Identify reactive vs proactive patterns
        reactive_count = 0
        proactive_count = 0
        
        for decision in decisions:
            if "request" in decision.context.lower() or "asked" in decision.context.lower():
                reactive_count += 1
            else:
                proactive_count += 1
        
        if reactive_count > proactive_count:
            patterns.append(DecisionPattern(
                pattern_type=PatternType.REACTIVE,
                frequency=reactive_count,
                confidence=reactive_count / len(decisions),
                examples=decisions[:min(5, len(decisions))],
                description=f"Reactive decision-making pattern: {reactive_count} reactive vs {proactive_count} proactive decisions"
            ))
        else:
            patterns.append(DecisionPattern(
                pattern_type=PatternType.PROACTIVE,
                frequency=proactive_count,
                confidence=proactive_count / len(decisions),
                examples=decisions[:min(5, len(decisions))],
                description=f"Proactive decision-making pattern: {proactive_count} proactive vs {reactive_count} reactive decisions"
            ))
        
        # Identify consistency patterns
        consistency_scores = []
        for decision_type, type_decisions in decision_types.items():
            if len(type_decisions) > 1:
                # Calculate consistency within decision type
                confidences = [d.confidence for d in type_decisions]
                consistency = 1.0 - (max(confidences) - min(confidences))
                consistency_scores.append(consistency)
        
        if consistency_scores:
            avg_consistency = sum(consistency_scores) / len(consistency_scores)
            if avg_consistency > 0.8:
                patterns.append(DecisionPattern(
                    pattern_type=PatternType.CONSISTENT,
                    frequency=len(decisions),
                    confidence=avg_consistency,
                    examples=decisions[:min(5, len(decisions))],
                    description=f"Consistent decision-making pattern with {avg_consistency:.2f} consistency score"
                ))
            else:
                patterns.append(DecisionPattern(
                    pattern_type=PatternType.INCONSISTENT,
                    frequency=len(decisions),
                    confidence=1.0 - avg_consistency,
                    examples=decisions[:min(5, len(decisions))],
                    description=f"Inconsistent decision-making pattern with {avg_consistency:.2f} consistency score"
                ))
        
        return patterns
    
    def _calculate_efficiency_score(self, decisions: List[Decision]) -> float:
        """Calculate efficiency score based on decision outcomes"""
        if not decisions:
            return 0.0
        
        successful_decisions = [d for d in decisions if d.success is True]
        return len(successful_decisions) / len(decisions)
    
    def _calculate_consistency_score(self, decisions: List[Decision]) -> float:
        """Calculate consistency score based on decision patterns"""
        if not decisions:
            return 0.0
        
        # Group decisions by type
        decision_types = {}
        for decision in decisions:
            if decision.decision_type not in decision_types:
                decision_types[decision.decision_type] = []
            decision_types[decision.decision_type].append(decision)
        
        # Calculate consistency within each type
        consistency_scores = []
        for decision_type, type_decisions in decision_types.items():
            if len(type_decisions) > 1:
                confidences = [d.confidence for d in type_decisions]
                consistency = 1.0 - (max(confidences) - min(confidences))
                consistency_scores.append(consistency)
        
        return sum(consistency_scores) / len(consistency_scores) if consistency_scores else 1.0
    
    def _calculate_proactive_score(self, decisions: List[Decision]) -> float:
        """Calculate proactive score based on decision context"""
        if not decisions:
            return 0.0
        
        proactive_count = 0
        for decision in decisions:
            if not ("request" in decision.context.lower() or "asked" in decision.context.lower()):
                proactive_count += 1
        
        return proactive_count / len(decisions)
    
    def _generate_recommendations(
        self,
        decisions: List[Decision],
        patterns: List[DecisionPattern]
    ) -> List[str]:
        """Generate recommendations based on analysis"""
        recommendations = []
        
        # Check for reactive patterns
        reactive_patterns = [p for p in patterns if p.pattern_type == PatternType.REACTIVE]
        if reactive_patterns:
            recommendations.append("Increase proactive decision-making by anticipating needs and creating solutions before they are requested")
        
        # Check for inconsistency patterns
        inconsistent_patterns = [p for p in patterns if p.pattern_type == PatternType.INCONSISTENT]
        if inconsistent_patterns:
            recommendations.append("Improve decision consistency by establishing clear criteria and following established patterns")
        
        # Check for low efficiency
        efficiency_score = self._calculate_efficiency_score(decisions)
        if efficiency_score < 0.8:
            recommendations.append("Improve decision efficiency by better planning and execution")
        
        # Check for low proactivity
        proactive_score = self._calculate_proactive_score(decisions)
        if proactive_score < 0.3:
            recommendations.append("Increase proactive behavior by anticipating needs and creating value before it is requested")
        
        return recommendations
