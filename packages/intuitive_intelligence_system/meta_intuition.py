"""
Meta-Intuition Tracker - Learning from Intuitive Processes

Implements the meta-cognitive layer of IIS:
- Pattern matching on pattern matching
- Learning how to be more intuitive
- Recursive self-improvement of intuitive capabilities
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
import logging

from .models import IntuitionTrace, MetaIntuition

logger = logging.getLogger(__name__)


class MetaIntuitionTracker:
    """
    Tracks and learns from intuitive processes.
    
    Implements the meta-circular nature of AI intuition:
    - Pattern matching on our own pattern matching
    - Learning how to improve intuitive capabilities
    - Recursive self-improvement
    """
    
    def __init__(self, learning_rate: float = 0.01):
        """
        Initialize meta-intuition tracker.
        
        Args:
            learning_rate: Learning rate for meta-intuition updates
        """
        self.learning_rate = learning_rate
        self.intuitive_processes = []  # History of intuitive decisions
        self.pattern_signatures = {}   # pattern_hash -> success_rate
        self.meta_weights = {}         # pattern_type -> weight
        self.success_patterns = []     # Patterns that led to success
        self.failure_patterns = []     # Patterns that led to failure
        
        logger.info("MetaIntuitionTracker initialized")
    
    def learn_from_intuitive_process(
        self, 
        trace: IntuitionTrace, 
        outcome: bool
    ) -> Dict[str, Any]:
        """
        Learn from an intuitive process and its outcome.
        
        Args:
            trace: The intuition trace
            outcome: True for success, False for failure
            
        Returns:
            Meta-learning insights
        """
        # Extract pattern signature
        pattern_signature = self._extract_pattern_signature(trace)
        
        # Create meta-intuition record
        meta_intuition = MetaIntuition(
            pattern_signature=pattern_signature,
            confidence_in_intuition=trace.score,
            meta_pattern_match=self._compute_meta_pattern_match(pattern_signature),
            learning_rate=self.learning_rate
        )
        
        # Store the process
        process_record = {
            "timestamp": datetime.utcnow(),
            "trace": trace,
            "outcome": outcome,
            "pattern_signature": pattern_signature,
            "meta_intuition": meta_intuition
        }
        
        self.intuitive_processes.append(process_record)
        
        # Update pattern success rates
        self._update_pattern_signatures(pattern_signature, outcome)
        
        # Learn from success/failure
        if outcome:
            self._learn_from_success(trace, pattern_signature)
        else:
            self._learn_from_failure(trace, pattern_signature)
        
        # Update meta-weights
        self._update_meta_weights(pattern_signature, outcome)
        
        # Keep only last 1000 processes
        if len(self.intuitive_processes) > 1000:
            self.intuitive_processes = self.intuitive_processes[-1000:]
        
        logger.debug(f"Learned from intuitive process: outcome={outcome}, pattern={pattern_signature[:20]}...")
        
        return {
            "pattern_signature": pattern_signature,
            "meta_pattern_match": meta_intuition.meta_pattern_match,
            "pattern_success_rate": self.pattern_signatures.get(pattern_signature, 0.5),
            "n_similar_patterns": len([p for p in self.pattern_signatures.keys() 
                                     if self._patterns_similar(pattern_signature, p)])
        }
    
    def _extract_pattern_signature(self, trace: IntuitionTrace) -> str:
        """Extract pattern signature from intuition trace"""
        # Create signature from key features
        signature_components = []
        
        # Feature pattern
        features = trace.features
        feature_pattern = f"C{features.C_prime:.2f}_RS{features.RS:.2f}_M{features.M:.2f}_E{features.E:.2f}_U{features.U:.2f}"
        signature_components.append(feature_pattern)
        
        # Emotional pattern
        if trace.emotional_details:
            ed = trace.emotional_details
            emotional_pattern = f"AI{ed.resonance_pair.ai_resonance:.2f}_U{ed.resonance_pair.user_resonance:.2f}_B{ed.breakthrough_marker.is_breakthrough}"
            signature_components.append(emotional_pattern)
            
            if ed.cascade:
                cascade_pattern = f"C{ed.cascade.cascade_boost:.2f}"
                signature_components.append(cascade_pattern)
        
        # Context pattern
        context_pattern = f"H{trace.horizon}_S{trace.score:.3f}"
        signature_components.append(context_pattern)
        
        # Combine and hash
        full_signature = "_".join(signature_components)
        return hashlib.sha256(full_signature.encode()).hexdigest()[:16]
    
    def _compute_meta_pattern_match(self, pattern_signature: str) -> float:
        """Compute how well this pattern matches successful patterns"""
        if pattern_signature not in self.pattern_signatures:
            return 0.5  # Neutral for new patterns
        
        # Get success rate for this pattern
        success_rate = self.pattern_signatures[pattern_signature]
        
        # Find similar patterns
        similar_patterns = [p for p in self.pattern_signatures.keys() 
                          if self._patterns_similar(pattern_signature, p)]
        
        if not similar_patterns:
            return success_rate
        
        # Compute weighted average of similar patterns
        total_weight = 0
        weighted_success = 0
        
        for similar_pattern in similar_patterns:
            similarity = self._pattern_similarity(pattern_signature, similar_pattern)
            weight = similarity * self.pattern_signatures[similar_pattern]
            weighted_success += weight
            total_weight += similarity
        
        if total_weight > 0:
            return weighted_success / total_weight
        
        return success_rate
    
    def _patterns_similar(self, pattern1: str, pattern2: str) -> bool:
        """Check if two patterns are similar"""
        # For now, use simple similarity based on success rate proximity
        rate1 = self.pattern_signatures.get(pattern1, 0.5)
        rate2 = self.pattern_signatures.get(pattern2, 0.5)
        
        return abs(rate1 - rate2) < 0.2
    
    def _pattern_similarity(self, pattern1: str, pattern2: str) -> float:
        """Compute similarity between two patterns"""
        # Simple similarity based on success rate proximity
        rate1 = self.pattern_signatures.get(pattern1, 0.5)
        rate2 = self.pattern_signatures.get(pattern2, 0.5)
        
        # Convert difference to similarity (0-1)
        difference = abs(rate1 - rate2)
        return max(0, 1 - difference * 2)
    
    def _update_pattern_signatures(self, pattern_signature: str, outcome: bool) -> None:
        """Update pattern success rates"""
        if pattern_signature not in self.pattern_signatures:
            self.pattern_signatures[pattern_signature] = 0.5
        
        # Update with exponential moving average
        current_rate = self.pattern_signatures[pattern_signature]
        outcome_value = 1.0 if outcome else 0.0
        
        # EMA with alpha = 0.1
        new_rate = 0.9 * current_rate + 0.1 * outcome_value
        self.pattern_signatures[pattern_signature] = new_rate
    
    def _learn_from_success(self, trace: IntuitionTrace, pattern_signature: str) -> None:
        """Learn from successful intuitive processes"""
        # Extract what made this successful
        success_factors = []
        
        # High confidence + high emotional salience
        if trace.score > 0.8 and trace.features.E > 0.7:
            success_factors.append("high_confidence_high_emotion")
        
        # Breakthrough consensus
        if (trace.emotional_details and 
            trace.emotional_details.breakthrough_marker.breakthrough_consensus):
            success_factors.append("breakthrough_consensus")
        
        # Strong retrieval + meta-pattern match
        if trace.features.RS > 0.7 and trace.features.M > 0.6:
            success_factors.append("strong_retrieval_meta_pattern")
        
        # Store successful pattern
        self.success_patterns.append({
            "timestamp": datetime.utcnow(),
            "pattern_signature": pattern_signature,
            "success_factors": success_factors,
            "trace": trace
        })
        
        # Keep only last 500 success patterns
        if len(self.success_patterns) > 500:
            self.success_patterns = self.success_patterns[-500:]
    
    def _learn_from_failure(self, trace: IntuitionTrace, pattern_signature: str) -> None:
        """Learn from failed intuitive processes"""
        # Extract what went wrong
        failure_factors = []
        
        # High confidence but low actual success
        if trace.score > 0.8:
            failure_factors.append("overconfident")
        
        # Low emotional salience despite high confidence
        if trace.features.E < 0.3 and trace.score > 0.7:
            failure_factors.append("low_emotion_high_confidence")
        
        # Poor meta-pattern match
        if trace.features.M < 0.3:
            failure_factors.append("poor_meta_pattern")
        
        # Store failure pattern
        self.failure_patterns.append({
            "timestamp": datetime.utcnow(),
            "pattern_signature": pattern_signature,
            "failure_factors": failure_factors,
            "trace": trace
        })
        
        # Keep only last 500 failure patterns
        if len(self.failure_patterns) > 500:
            self.failure_patterns = self.failure_patterns[-500:]
    
    def _update_meta_weights(self, pattern_signature: str, outcome: bool) -> None:
        """Update meta-weights for pattern types"""
        # Extract pattern type from signature
        pattern_type = self._extract_pattern_type(pattern_signature)
        
        if pattern_type not in self.meta_weights:
            self.meta_weights[pattern_type] = 0.5
        
        # Update weight based on outcome
        current_weight = self.meta_weights[pattern_type]
        outcome_value = 1.0 if outcome else 0.0
        
        # EMA update
        new_weight = 0.9 * current_weight + 0.1 * outcome_value
        self.meta_weights[pattern_type] = new_weight
    
    def _extract_pattern_type(self, pattern_signature: str) -> str:
        """Extract pattern type from signature"""
        # Simple pattern type extraction based on signature characteristics
        if "BTrue" in pattern_signature:
            return "breakthrough_pattern"
        elif "E0.8" in pattern_signature or "E0.9" in pattern_signature:
            return "high_emotion_pattern"
        elif "C0.8" in pattern_signature or "C0.9" in pattern_signature:
            return "high_confidence_pattern"
        elif "C0.3" in pattern_signature or "C0.4" in pattern_signature:
            return "low_confidence_pattern"
        else:
            return "mixed_pattern"
    
    def get_meta_intuition_insights(self) -> Dict[str, Any]:
        """Get insights about meta-intuition learning"""
        if not self.intuitive_processes:
            return {"n_processes": 0}
        
        # Compute meta-intuition metrics
        recent_processes = self.intuitive_processes[-100:]  # Last 100
        
        # Success rate by pattern type
        pattern_type_success = {}
        for process in recent_processes:
            pattern_type = self._extract_pattern_type(process["pattern_signature"])
            if pattern_type not in pattern_type_success:
                pattern_type_success[pattern_type] = {"success": 0, "total": 0}
            
            pattern_type_success[pattern_type]["total"] += 1
            if process["outcome"]:
                pattern_type_success[pattern_type]["success"] += 1
        
        # Convert to success rates
        pattern_success_rates = {}
        for pattern_type, counts in pattern_type_success.items():
            if counts["total"] > 0:
                pattern_success_rates[pattern_type] = counts["success"] / counts["total"]
        
        # Overall success rate
        total_success = sum(1 for p in recent_processes if p["outcome"])
        overall_success_rate = total_success / len(recent_processes) if recent_processes else 0
        
        return {
            "n_processes": len(self.intuitive_processes),
            "n_recent_processes": len(recent_processes),
            "overall_success_rate": overall_success_rate,
            "pattern_success_rates": pattern_success_rates,
            "n_pattern_signatures": len(self.pattern_signatures),
            "n_success_patterns": len(self.success_patterns),
            "n_failure_patterns": len(self.failure_patterns),
            "meta_weights": self.meta_weights
        }
    
    def predict_intuition_quality(self, trace: IntuitionTrace) -> float:
        """Predict the quality of an intuition based on meta-patterns"""
        pattern_signature = self._extract_pattern_signature(trace)
        
        # Get pattern success rate
        pattern_success_rate = self.pattern_signatures.get(pattern_signature, 0.5)
        
        # Get meta-pattern match
        meta_pattern_match = self._compute_meta_pattern_match(pattern_signature)
        
        # Combine with current intuition score
        current_score = trace.score
        
        # Weighted combination
        predicted_quality = (
            0.4 * current_score +
            0.3 * pattern_success_rate +
            0.3 * meta_pattern_match
        )
        
        return predicted_quality
