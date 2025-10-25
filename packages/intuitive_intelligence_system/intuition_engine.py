"""
Intuition Engine - Core IntuitionScore Computation and Learning

Implements the mathematical framework for AI intuition, combining
ChatGPT's engineering rigor with Sonnet's emotional richness.
"""

from __future__ import annotations

import numpy as np
from typing import Dict, Any, Optional, Tuple
from datetime import datetime
import logging

from .models import IntuitionTrace, IntuitionFeatures, EmotionalDetails
from .emotional_salience import EmotionalSalienceTracker
from .ccs_integration import ccs_integration

logger = logging.getLogger(__name__)


class IntuitionEngine:
    """
    Core engine for computing IntuitionScore and learning from outcomes.
    
    Implements:
    - IntuitionScore computation: I(x) = σ(w·x)
    - Online SGD learning from labeled outcomes
    - Calibration tracking (AUC, ECE)
    - Drift detection and recalibration
    """
    
    def __init__(self, learning_rate: float = 0.01, regularization: float = 0.001):
        """
        Initialize the intuition engine.
        
        Args:
            learning_rate: SGD learning rate for weight updates
            regularization: L2 regularization strength
        """
        self.learning_rate = learning_rate
        self.regularization = regularization
        
        # Initialize weights (7 features: C', RS, M, E, F, U, bias)
        self.weights = np.random.normal(0, 0.1, 7)
        
        # Calibration tracking
        self.calibration_history = []
        self.auc_history = []
        self.ece_history = []
        
        # Emotional salience tracker
        self.est = EmotionalSalienceTracker()
        
        # Drift detection thresholds
        self.auc_drift_threshold = 0.05
        self.ece_drift_threshold = 0.1
        
        logger.info("IntuitionEngine initialized with 7 features")
    
    def compute_intuition_score_with_ccs(
        self, 
        action_id: str, 
        query: str, 
        context: Dict[str, Any],
        emotional_context: Dict[str, Any]
    ) -> Tuple[float, IntuitionTrace]:
        """
        Compute IntuitionScore using real CCS data.
        
        Args:
            action_id: ID of the action/decision
            query: Query string for retrieval
            context: General context for decision
            emotional_context: Emotional context for EST
            
        Returns:
            Tuple[float, IntuitionTrace]: IntuitionScore and complete trace
        """
        # Get real features from CCS systems
        C_prime = ccs_integration.get_calibrated_confidence(action_id, context)
        RS = ccs_integration.get_retrieval_strength(query, context.get("embedding", []))
        M = ccs_integration.get_meta_pattern_similarity(context)
        
        # Get emotional context from TCS
        tcs_emotional_context = ccs_integration.get_emotional_context(action_id)
        
        # Merge emotional contexts
        merged_emotional_context = {**emotional_context, **tcs_emotional_context}
        
        # Create features with real CCS data
        features = IntuitionFeatures(
            C_prime=C_prime,
            RS=RS,
            M=M,
            E=0.0,  # Will be computed by EST
            F=0.0,  # MVP - no 4D predictor yet
            U=0.1   # Mock miscalibration penalty for now
        )
        
        # Compute intuition score with enhanced emotional context
        return self.compute_intuition_score(features, merged_emotional_context)

    def compute_intuition_score(
        self, 
        features: IntuitionFeatures,
        emotional_context: Optional[Dict[str, Any]] = None
    ) -> Tuple[float, IntuitionTrace]:
        """
        Compute IntuitionScore for given features.
        
        Args:
            features: Core intuition features
            emotional_context: Optional emotional context for EST
            
        Returns:
            Tuple of (intuition_score, intuition_trace)
        """
        # Compute emotional salience if context provided
        emotional_details = None
        if emotional_context:
            emotional_details = self.est.compute_emotional_salience(
                emotional_context.get('idea', ''),
                emotional_context.get('context', {}),
                emotional_context.get('ai_response', {}),
                emotional_context.get('user_response', {})
            )
            # Update E feature with computed emotional salience
            features.E = emotional_details.compute_emotional_salience()
        
        # Convert to feature vector
        x = np.array(features.to_vector())
        
        # Compute raw score
        z = np.dot(self.weights, x)
        
        # Apply logistic function
        intuition_score = 1 / (1 + np.exp(-z))
        
        # Create intuition trace
        trace = IntuitionTrace(
            features=features,
            emotional_details=emotional_details,
            score=intuition_score,
            predicted_outcome=intuition_score
        )
        
        logger.debug(f"Computed IntuitionScore: {intuition_score:.4f} for decision {trace.decision_id}")
        
        return intuition_score, trace

    def store_trace_in_cmc(self, trace: IntuitionTrace) -> str:
        """
        Store IntuitionTrace in CMC for persistent memory.
        
        Args:
            trace: The IntuitionTrace to store
            
        Returns:
            str: The CMC atom ID where the trace was stored
        """
        return ccs_integration.store_intuition_trace(trace)

    def update_from_outcome(
        self, 
        trace: IntuitionTrace, 
        outcome: bool,
        observed_at: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Update weights based on observed outcome.
        
        Args:
            trace: Original intuition trace
            outcome: True for success, False for failure
            observed_at: When outcome was observed
            
        Returns:
            Update metrics and calibration info
        """
        if observed_at is None:
            observed_at = datetime.utcnow()
        
        # Update label in trace
        trace.label = {
            "value": 1 if outcome else 0,
            "observed_at": observed_at.isoformat()
        }
        
        # Get feature vector
        x = np.array(trace.features.to_vector())
        
        # Compute current prediction
        z = np.dot(self.weights, x)
        current_score = 1 / (1 + np.exp(-z))
        
        # Compute loss (binary cross-entropy)
        label = 1 if outcome else 0
        loss = -(label * np.log(current_score + 1e-8) + 
                (1 - label) * np.log(1 - current_score + 1e-8))
        
        # Compute gradient
        gradient = (current_score - label) * x
        
        # Add regularization
        gradient += self.regularization * self.weights
        
        # Update weights
        self.weights = self.weights - self.learning_rate * gradient
        
        # Update calibration tracking
        self._update_calibration_metrics(trace, outcome)
        
        # Check for drift
        drift_detected = self._check_drift()
        
        logger.info(f"Updated weights from outcome {outcome}, loss: {loss:.4f}")
        
        return {
            "loss": loss,
            "gradient_norm": np.linalg.norm(gradient),
            "weight_norm": np.linalg.norm(self.weights),
            "calibration_metrics": self._get_current_calibration(),
            "drift_detected": drift_detected
        }
    
    def _update_calibration_metrics(self, trace: IntuitionTrace, outcome: bool) -> None:
        """Update calibration tracking metrics"""
        # Add to history
        self.calibration_history.append({
            "predicted": trace.score,
            "actual": 1 if outcome else 0,
            "timestamp": datetime.utcnow()
        })
        
        # Keep only last 1000 entries for efficiency
        if len(self.calibration_history) > 1000:
            self.calibration_history = self.calibration_history[-1000:]
    
    def _get_current_calibration(self) -> Dict[str, float]:
        """Get current calibration metrics"""
        if len(self.calibration_history) < 10:
            return {"auc": 0.5, "ece": 0.0, "n": len(self.calibration_history)}
        
        # Compute AUC (simplified - in practice use sklearn.metrics.roc_auc_score)
        predictions = [h["predicted"] for h in self.calibration_history]
        actuals = [h["actual"] for h in self.calibration_history]
        
        # Simple AUC approximation
        auc = self._compute_auc(predictions, actuals)
        
        # Compute ECE (Expected Calibration Error)
        ece = self._compute_ece(predictions, actuals)
        
        return {
            "auc": auc,
            "ece": ece,
            "n": len(self.calibration_history)
        }
    
    def _compute_auc(self, predictions: list, actuals: list) -> float:
        """Compute AUC (simplified implementation)"""
        if len(predictions) != len(actuals) or len(predictions) == 0:
            return 0.5
        
        # Sort by prediction score (descending)
        sorted_data = sorted(zip(predictions, actuals), key=lambda x: x[0], reverse=True)
        
        # Count positive and negative examples
        pos_count = sum(actuals)
        neg_count = len(actuals) - pos_count
        
        if pos_count == 0 or neg_count == 0:
            return 0.5
        
        # Compute AUC using Mann-Whitney U statistic
        auc = 0.0
        tp = 0
        fp = 0
        
        for pred, actual in sorted_data:
            if actual == 1:
                tp += 1
            else:
                fp += 1
                auc += tp
        
        return auc / (pos_count * neg_count)
    
    def _compute_ece(self, predictions: list, actuals: list, n_bins: int = 10) -> float:
        """Compute Expected Calibration Error"""
        bin_boundaries = np.linspace(0, 1, n_bins + 1)
        bin_lowers = bin_boundaries[:-1]
        bin_uppers = bin_boundaries[1:]
        
        ece = 0
        for bin_lower, bin_upper in zip(bin_lowers, bin_uppers):
            in_bin = [(p, a) for p, a in zip(predictions, actuals) 
                     if bin_lower <= p < bin_upper]
            
            if len(in_bin) == 0:
                continue
            
            bin_predictions = [p for p, a in in_bin]
            bin_actuals = [a for p, a in in_bin]
            
            bin_accuracy = sum(bin_actuals) / len(bin_actuals)
            bin_confidence = sum(bin_predictions) / len(bin_predictions)
            
            ece += abs(bin_accuracy - bin_confidence) * len(in_bin)
        
        return ece / len(predictions)
    
    def _check_drift(self) -> bool:
        """Check for calibration drift"""
        if len(self.calibration_history) < 10:
            return False
        
        current_metrics = self._get_current_calibration()
        
        # Check AUC drift
        if len(self.auc_history) > 0:
            auc_drift = abs(current_metrics["auc"] - self.auc_history[-1])
            if auc_drift > self.auc_drift_threshold:
                logger.warning(f"AUC drift detected: {auc_drift:.4f}")
                return True
        
        # Check ECE drift
        if len(self.ece_history) > 0:
            ece_drift = abs(current_metrics["ece"] - self.ece_history[-1])
            if ece_drift > self.ece_drift_threshold:
                logger.warning(f"ECE drift detected: {ece_drift:.4f}")
                return True
        
        # Update history (only if we have enough data)
        if len(self.calibration_history) >= 10:
            self.auc_history.append(current_metrics["auc"])
            self.ece_history.append(current_metrics["ece"])
        
        return False
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current engine metrics"""
        calibration = self._get_current_calibration()
        
        return {
            "weights": self.weights.tolist(),
            "weight_norm": float(np.linalg.norm(self.weights)),
            "calibration": calibration,
            "learning_rate": self.learning_rate,
            "regularization": self.regularization,
            "n_updates": len(self.calibration_history)
        }
    
    def recalibrate(self) -> Dict[str, Any]:
        """Trigger recalibration (placeholder for Platt/Isotonic)"""
        logger.info("Recalibration triggered - implementing recalibration logic")
        
        # For MVP, just reset some weights
        # In full implementation, use Platt scaling or Isotonic regression
        
        return {
            "recalibrated": True,
            "timestamp": datetime.utcnow().isoformat(),
            "method": "placeholder"
        }
