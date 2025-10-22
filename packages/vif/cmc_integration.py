"""VIF Integration with CMC

Stores VIF witnesses as CMC atoms for persistence and retrieval.
"""

from __future__ import annotations

from typing import Optional, List, Dict, Any
import json


def vif_to_atom_payload(vif: Any) -> Dict[str, Any]:
    """Convert VIF witness to CMC AtomCreate payload
    
    Args:
        vif: VIF witness instance
        
    Returns:
        Dictionary compatible with CMC AtomCreate
        
    Examples:
        >>> from vif import VIF, ConfidenceBand
        >>> vif = VIF(
        ...     model_id="gpt-4",
        ...     model_provider="openai",
        ...     context_snapshot_id="snap_123",
        ...     prompt_hash="hash1",
        ...     prompt_tokens=10,
        ...     confidence_score=0.95,
        ...     confidence_band=ConfidenceBand.A,
        ...     output_hash="hash2",
        ...     output_tokens=5,
        ...     total_tokens=15,
        ... )
        >>> payload = vif_to_atom_payload(vif)
        >>> assert payload["modality"] == "witness"
        >>> assert "vif" in payload["content"]["inline"]
    """
    # Serialize VIF to JSON
    vif_json = json.dumps(vif.to_dict(), indent=2)
    
    # Create CMC atom payload
    payload = {
        "modality": "witness",
        "content": {
            "inline": vif_json,
            "media_type": "application/json"
        },
        "tags": {
            "vif_id": vif.id,
            "model_id": vif.model_id,
            "confidence_score": vif.confidence_score,
            "confidence_band": vif.confidence_band.value if hasattr(vif.confidence_band, 'value') else str(vif.confidence_band),
            "kappa_gate_passed": 1.0 if vif.kappa_gate_passed else 0.0,
            "task_criticality": vif.task_criticality.value if hasattr(vif.task_criticality, 'value') else str(vif.task_criticality),
            "created_at": vif.created_at.timestamp() if hasattr(vif.created_at, 'timestamp') else 0.0,
        },
        "metadata": {
            "vif_version": vif.version,
            "context_snapshot_id": vif.context_snapshot_id,
            "total_tokens": vif.total_tokens,
            "execution_time_ms": vif.execution_time_ms,
            "parent_vif_id": vif.parent_vif_id,
        }
    }
    
    # Add optional fields
    if vif.ece_score is not None:
        payload["tags"]["ece_score"] = vif.ece_score
    
    if vif.parent_vif_id:
        payload["tags"]["has_parent"] = 1.0
    
    return payload


def atom_to_vif(atom: Any) -> Any:
    """Convert CMC atom back to VIF witness
    
    Args:
        atom: CMC Atom instance
        
    Returns:
        VIF witness instance
        
    Raises:
        ValueError: If atom is not a witness modality
    """
    if atom.modality != "witness":
        raise ValueError(f"Atom modality must be 'witness', got '{atom.modality}'")
    
    # Extract VIF JSON from atom content
    vif_json = atom.content.get("inline")
    if not vif_json:
        raise ValueError("Witness atom has no inline content")
    
    # Parse VIF from JSON
    vif_data = json.loads(vif_json)
    
    # Import VIF here to avoid circular dependency
    from .witness import VIF
    
    return VIF.from_dict(vif_data)


class VIFStore:
    """High-level API for storing and retrieving VIF witnesses via CMC
    
    Examples:
        >>> from vif import VIF
        >>> store = VIFStore(cmc_store)
        >>> 
        >>> # Create witness
        >>> vif = VIF(...)
        >>> 
        >>> # Store in CMC
        >>> atom_id = store.store_witness(vif)
        >>> 
        >>> # Retrieve later
        >>> retrieved_vif = store.get_witness(atom_id)
        >>> assert retrieved_vif.id == vif.id
    """
    
    def __init__(self, cmc_store: Any):
        """Initialize VIF store
        
        Args:
            cmc_store: CMC MemoryStore instance
        """
        self.cmc = cmc_store
    
    def store_witness(
        self,
        vif: Any,
        *,
        correlation_id: Optional[str] = None,
    ) -> str:
        """Store VIF witness in CMC
        
        Args:
            vif: VIF witness to store
            correlation_id: Optional correlation ID for tracking
            
        Returns:
            CMC atom ID
        """
        # Convert VIF to atom payload
        payload_dict = vif_to_atom_payload(vif)
        
        # Import CMC models
        from cmc_service.models import AtomCreate, AtomContent
        
        # Create AtomCreate instance
        payload = AtomCreate(
            modality=payload_dict["modality"],
            content=AtomContent(**payload_dict["content"]),
            tags=payload_dict["tags"],
            metadata=payload_dict["metadata"],
        )
        
        # Store in CMC
        atom = self.cmc.create_atom(payload, correlation_id=correlation_id)
        
        return atom.id
    
    def get_witness(self, atom_id: str) -> Any:
        """Retrieve VIF witness from CMC
        
        Args:
            atom_id: CMC atom ID
            
        Returns:
            VIF witness instance
        """
        atom = self.cmc.get_atom(atom_id)
        return atom_to_vif(atom)
    
    def query_witnesses(
        self,
        *,
        model_id: Optional[str] = None,
        min_confidence: Optional[float] = None,
        max_confidence: Optional[float] = None,
        confidence_band: Optional[str] = None,
        task_criticality: Optional[str] = None,
        kappa_gate_passed: Optional[bool] = None,
        limit: int = 100,
    ) -> List[Any]:
        """Query VIF witnesses with filters
        
        Args:
            model_id: Filter by model ID
            min_confidence: Minimum confidence score
            max_confidence: Maximum confidence score
            confidence_band: Filter by band (A/B/C)
            task_criticality: Filter by criticality
            kappa_gate_passed: Filter by gate status
            limit: Maximum results
            
        Returns:
            List of VIF witnesses matching filters
        """
        # This would integrate with CMC query system
        # For now, placeholder implementation
        
        # In production, would use CMC's tag-based queries:
        # cmc.query_by_tags({"modality": "witness", "confidence_band": "A", ...})
        
        raise NotImplementedError("VIF querying requires CMC query system enhancement")
    
    def get_witness_lineage(self, vif_id: str) -> Dict[str, Any]:
        """Get complete lineage tree for a witness
        
        Args:
            vif_id: VIF witness ID
            
        Returns:
            Lineage tree showing parents and children
        """
        # Find atom with this VIF ID
        # (Would use CMC tag query: {"vif_id": vif_id})
        
        raise NotImplementedError("Lineage tracking requires CMC integration")
    
    def get_calibration_history(
        self,
        model_id: str,
        *,
        limit: int = 1000,
    ) -> List[tuple[float, bool]]:
        """Get calibration history for a model
        
        Args:
            model_id: Model to get history for
            limit: Maximum number of records
            
        Returns:
            List of (confidence, was_correct) tuples for ECE calculation
        """
        # Would query CMC for all witnesses from this model
        # Extract confidence scores and outcomes
        
        raise NotImplementedError("Calibration history requires CMC integration")


def create_witness_and_store(
    cmc_store: Any,
    operation_name: str,
    prompt: str,
    output: str,
    confidence: float,
    context_snapshot_id: str,
    **kwargs
) -> tuple[Any, str]:
    """Convenience: create VIF witness and store in CMC
    
    Args:
        cmc_store: CMC MemoryStore
        operation_name: Name of operation
        prompt: Prompt text
        output: Output text  
        confidence: Confidence score
        context_snapshot_id: CMC snapshot ID
        **kwargs: Additional VIF fields
        
    Returns:
        (vif_witness, cmc_atom_id)
    """
    from .witness import VIF, ConfidenceBand, TaskCriticality
    from .confidence_bands import determine_band
    
    # Extract model info from kwargs
    model_id = kwargs.pop("model_id", "unknown")
    model_provider = kwargs.pop("model_provider", "unknown")
    
    # Create VIF
    vif = VIF(
        model_id=model_id,
        model_provider=model_provider,
        context_snapshot_id=context_snapshot_id,
        prompt_hash=VIF.hash_text(prompt),
        prompt_tokens=len(prompt.split()),  # Rough estimate
        confidence_score=confidence,
        confidence_band=determine_band(confidence),
        output_hash=VIF.hash_text(output),
        output_tokens=len(output.split()),  # Rough estimate
        total_tokens=len(prompt.split()) + len(output.split()),
        **kwargs  # Remaining kwargs
    )
    
    # Store in CMC
    store = VIFStore(cmc_store)
    atom_id = store.store_witness(vif)
    
    return vif, atom_id

