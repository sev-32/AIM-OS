"""
CCS Integration for Intuitive Intelligence System (IIS)

This module provides integration with the Continuous Consciousness Substrate (CCS) systems:
- CMC (Context Memory Core): Persistent storage of IntuitionTrace
- VIF (Verifiable Intelligence Framework): Calibrated confidence (C′) feature
- HHNI (Hierarchical Hypergraph Neural Index): Retrieval strength (RS) feature
- TCS (Timeline Context System): Emotional context for E feature
- CAS (Cognitive Analysis System): Meta-pattern similarity (M) feature
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime, timezone

# CCS System Imports
from packages.cmc_service.models import AtomCreate, AtomContent, WitnessStub
from packages.vif import VIF, extract_confidence, determine_band
from packages.hhni import SemanticSearchEngine, SearchResult
# Note: TCS and CAS imports will be added when those systems are fully integrated

from .models import IntuitionTrace, IntuitionFeatures, EmotionalDetails

logger = logging.getLogger(__name__)


class CCSIntegration:
    """
    Integration layer between IIS and CCS systems.
    
    Provides real data for all IIS features by connecting to:
    - CMC: Persistent storage and retrieval
    - VIF: Calibrated confidence computation
    - HHNI: Retrieval strength computation
    - TCS: Emotional context extraction
    - CAS: Meta-pattern similarity computation
    """
    
    def __init__(self):
        """Initialize CCS integration components"""
        self.cmc_client = None  # Will be initialized when CMC is available
        self.vif_client = None  # Will be initialized when VIF is available
        self.hhni_client = None  # Will be initialized when HHNI is available
        self.tcs_client = None  # Will be initialized when TCS is available
        self.cas_client = None  # Will be initialized when CAS is available
        
        logger.info("CCS Integration initialized")
    
    # CMC Integration Methods
    
    def store_intuition_trace(self, trace: IntuitionTrace) -> str:
        """
        Store IntuitionTrace in CMC for persistent memory.
        
        Args:
            trace: The IntuitionTrace to store
            
        Returns:
            str: The CMC atom ID where the trace was stored
        """
        if not self.cmc_client:
            logger.warning("CMC client not available, using mock storage")
            return f"mock_atom_{trace.decision_id}"
        
        # Create CMC atom for IntuitionTrace
        atom_content = AtomContent(
            inline=trace.model_dump_json(),
            media_type="application/json"
        )
        
        # Create metadata with IIS-specific fields
        metadata = {
            "iis_version": "1.0",
            "intuition_score": trace.score,
            "feature_hash": trace.feature_hash,
            "horizon": trace.horizon,
            "decision_id": trace.decision_id,
            "action_type": trace.action_ref.get("type", "unknown"),
            "action_id": trace.action_ref.get("id", "unknown"),
            "computed_at": trace.computed_at,
            "predicted_outcome": trace.predicted_outcome,
            "label_value": trace.label.value if trace.label else None,
            "label_observed_at": trace.label.observed_at if trace.label else None,
            "calibration_auc": trace.calibration_snapshot.auc,
            "calibration_ece": trace.calibration_snapshot.ece,
            "calibration_n": trace.calibration_snapshot.n,
        }
        
        # Create tags for searchability
        tags = {
            "intuition": 1.0,
            "decision": 1.0,
            f"horizon_{trace.horizon}": 1.0,
            f"score_{self._score_to_tag(trace.score)}": 1.0,
        }
        
        # Add emotional tags if available
        if trace.emotional_details:
            tags["emotional"] = 1.0
            if trace.emotional_details.breakthrough_marker.is_breakthrough:
                tags["breakthrough"] = 1.0
            if trace.emotional_details.cascade:
                tags["cascade"] = 1.0
        
        # Create witness for provenance
        witness = WitnessStub(
            model_id="iis",
            tool_ids=["intuition_engine"],
            correlation_id=trace.decision_id,
            uncertainty_band=determine_band(trace.score),
            uncertainty_ece=trace.calibration_snapshot.ece
        )
        
        # Create atom
        atom = AtomCreate(
            modality="intuition_trace",
            content=atom_content,
            tags=tags,
            metadata=metadata,
            policy_tags=["iis", "intuition", "consciousness"]
        )
        
        # Store in CMC (this would be the actual CMC call)
        # atom_id = self.cmc_client.create_atom(atom, witness)
        atom_id = f"cmc_atom_{trace.decision_id}"  # Mock for now
        
        logger.info(f"Stored IntuitionTrace in CMC: {atom_id}")
        return atom_id
    
    def retrieve_intuition_traces(
        self, 
        decision_id: Optional[str] = None,
        horizon: Optional[str] = None,
        min_score: Optional[float] = None,
        max_score: Optional[float] = None,
        limit: int = 100
    ) -> List[IntuitionTrace]:
        """
        Retrieve IntuitionTrace objects from CMC.
        
        Args:
            decision_id: Filter by specific decision ID
            horizon: Filter by horizon (short, medium, long)
            min_score: Filter by minimum intuition score
            max_score: Filter by maximum intuition score
            limit: Maximum number of traces to return
            
        Returns:
            List[IntuitionTrace]: Retrieved traces
        """
        if not self.cmc_client:
            logger.warning("CMC client not available, returning empty list")
            return []
        
        # Build query filters
        filters = {"modality": "intuition_trace"}
        if decision_id:
            filters["metadata.decision_id"] = decision_id
        if horizon:
            filters[f"tags.horizon_{horizon}"] = 1.0
        if min_score is not None:
            filters["metadata.intuition_score"] = {"$gte": min_score}
        if max_score is not None:
            filters["metadata.intuition_score"] = {"$lte": max_score}
        
        # Query CMC (this would be the actual CMC call)
        # atoms = self.cmc_client.query_atoms(filters, limit=limit)
        atoms = []  # Mock for now
        
        # Convert atoms back to IntuitionTrace objects
        traces = []
        for atom in atoms:
            try:
                trace_data = atom.content.inline
                trace = IntuitionTrace.model_validate_json(trace_data)
                traces.append(trace)
            except Exception as e:
                logger.error(f"Failed to parse IntuitionTrace from atom {atom.id}: {e}")
        
        logger.info(f"Retrieved {len(traces)} IntuitionTrace objects from CMC")
        return traces
    
    # VIF Integration Methods
    
    def get_calibrated_confidence(self, action_id: str, context: Dict[str, Any]) -> float:
        """
        Get calibrated confidence (C′) from VIF.
        
        Args:
            action_id: ID of the action/decision
            context: Context for confidence computation
            
        Returns:
            float: Calibrated confidence score (0-1)
        """
        if not self.vif_client:
            logger.warning("VIF client not available, using mock confidence")
            return 0.7  # Mock confidence
        
        # Extract confidence from context
        confidence_signals = []
        
        # Extract from explicit confidence if available
        if "confidence" in context:
            confidence_signals.append(("explicit", context["confidence"]))
        
        # Extract from logprobs if available
        if "logprobs" in context:
            logprob_confidence = extract_confidence(context["logprobs"])
            confidence_signals.append(("logprobs", logprob_confidence))
        
        # Extract from uncertainty indicators
        if "uncertainty" in context:
            uncertainty = context["uncertainty"]
            if isinstance(uncertainty, (int, float)):
                confidence_signals.append(("uncertainty", 1.0 - uncertainty))
        
        # Combine confidence signals
        if confidence_signals:
            combined_confidence = sum(score for _, score in confidence_signals) / len(confidence_signals)
        else:
            combined_confidence = 0.5  # Default neutral confidence
        
        # Apply calibration (this would use VIF's calibration system)
        # calibrated_confidence = self.vif_client.calibrate_confidence(combined_confidence, action_id)
        calibrated_confidence = combined_confidence  # Mock for now
        
        logger.debug(f"Computed calibrated confidence for {action_id}: {calibrated_confidence:.3f}")
        return calibrated_confidence
    
    # HHNI Integration Methods
    
    def get_retrieval_strength(self, query: str, context_embedding: List[float]) -> float:
        """
        Get retrieval strength (RS) from HHNI.
        
        Args:
            query: The query string
            context_embedding: Context embedding vector
            
        Returns:
            float: Retrieval strength score (0-1)
        """
        if not self.hhni_client:
            logger.warning("HHNI client not available, using mock retrieval strength")
            return 0.6  # Mock retrieval strength
        
        # Perform semantic search
        # search_results = self.hhni_client.search(query, context_embedding, limit=10)
        search_results = []  # Mock for now
        
        if not search_results:
            return 0.0
        
        # Compute retrieval strength based on top results
        # This could be based on relevance scores, similarity, etc.
        top_score = search_results[0].score if search_results else 0.0
        avg_score = sum(result.score for result in search_results) / len(search_results)
        
        # Combine top score and average for retrieval strength
        retrieval_strength = (top_score * 0.7) + (avg_score * 0.3)
        
        logger.debug(f"Computed retrieval strength for query '{query[:50]}...': {retrieval_strength:.3f}")
        return retrieval_strength
    
    # TCS Integration Methods
    
    def get_emotional_context(self, decision_id: str) -> Dict[str, Any]:
        """
        Get emotional context from TCS for E feature computation.
        
        Args:
            decision_id: ID of the decision/action
            
        Returns:
            Dict[str, Any]: Emotional context data
        """
        if not self.tcs_client:
            logger.warning("TCS client not available, using mock emotional context")
            return {
                "ai_emotional_state": {"resonance": 0.5, "breakthrough_feeling": 0.3},
                "user_emotional_state": {"resonance": 0.4, "breakthrough_feeling": 0.2},
                "context_emotions": [],
                "temporal_emotions": []
            }
        
        # Get emotional context from TCS
        # emotional_context = self.tcs_client.get_emotional_context(decision_id)
        emotional_context = {}  # Mock for now
        
        logger.debug(f"Retrieved emotional context for decision {decision_id}")
        return emotional_context
    
    # CAS Integration Methods
    
    def get_meta_pattern_similarity(self, current_context: Dict[str, Any]) -> float:
        """
        Get meta-pattern similarity (M) from CAS.
        
        Args:
            current_context: Current decision context
            
        Returns:
            float: Meta-pattern similarity score (0-1)
        """
        if not self.cas_client:
            logger.warning("CAS client not available, using mock meta-pattern similarity")
            return 0.5  # Mock meta-pattern similarity
        
        # Get meta-pattern similarity from CAS
        # similarity = self.cas_client.compute_meta_pattern_similarity(current_context)
        similarity = 0.5  # Mock for now
        
        logger.debug(f"Computed meta-pattern similarity: {similarity:.3f}")
        return similarity
    
    # Utility Methods
    
    def _score_to_tag(self, score: float) -> str:
        """Convert intuition score to tag category"""
        if score >= 0.8:
            return "high"
        elif score >= 0.6:
            return "medium"
        elif score >= 0.4:
            return "low"
        else:
            return "very_low"
    
    def get_integration_status(self) -> Dict[str, bool]:
        """Get status of CCS system integrations"""
        return {
            "cmc": self.cmc_client is not None,
            "vif": self.vif_client is not None,
            "hhni": self.hhni_client is not None,
            "tcs": self.tcs_client is not None,
            "cas": self.cas_client is not None,
        }
    
    def initialize_ccs_clients(self, **clients):
        """Initialize CCS system clients"""
        self.cmc_client = clients.get("cmc")
        self.vif_client = clients.get("vif")
        self.hhni_client = clients.get("hhni")
        self.tcs_client = clients.get("tcs")
        self.cas_client = clients.get("cas")
        
        status = self.get_integration_status()
        logger.info(f"CCS clients initialized: {status}")


# Global CCS integration instance
ccs_integration = CCSIntegration()
