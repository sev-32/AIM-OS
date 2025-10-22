"""Deterministic Replay System

Enables bit-identical reproduction of AI operations by capturing
all necessary state (context, seeds, parameters) in VIF witnesses.

This is critical for:
- Debugging AI behavior
- Auditing decisions
- Verifying claims
- Legal compliance
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional, Callable
from datetime import datetime
import hashlib


@dataclass
class ReplayResult:
    """Result of replay operation"""
    success: bool
    output: Optional[Any] = None
    output_hash: Optional[str] = None
    matches_original: bool = False
    original_hash: Optional[str] = None
    error: Optional[str] = None
    execution_time_ms: float = 0.0
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            "success": self.success,
            "matches_original": self.matches_original,
            "output_hash": self.output_hash,
            "original_hash": self.original_hash,
            "error": self.error,
            "execution_time_ms": self.execution_time_ms,
        }


class ReplayEngine:
    """Engine for deterministic replay of AI operations
    
    Given a VIF witness, can reproduce the exact operation by:
    1. Restoring context from CMC snapshot
    2. Setting deterministic parameters (seed, temperature)
    3. Re-executing with identical inputs
    4. Comparing output hash for verification
    
    Examples:
        >>> from vif import VIF
        >>> engine = ReplayEngine()
        >>> 
        >>> # Original operation captured in VIF
        >>> original_vif = VIF(
        ...     model_id="gpt-4",
        ...     model_provider="openai",
        ...     context_snapshot_id="snap_123",
        ...     prompt_hash=VIF.hash_text("What is 2+2?"),
        ...     prompt_tokens=5,
        ...     confidence_score=0.99,
        ...     confidence_band="A",
        ...     output_hash=VIF.hash_text("4"),
        ...     output_tokens=1,
        ...     total_tokens=6,
        ...     replay_seed=42,
        ...     temperature=0.0,
        ... )
        >>> 
        >>> # Replay operation
        >>> result = engine.replay(original_vif, operation_fn)
        >>> assert result.matches_original
    """
    
    def __init__(
        self,
        context_loader: Optional[Callable[[str], Dict[str, Any]]] = None,
    ):
        """Initialize replay engine
        
        Args:
            context_loader: Function to load context from snapshot ID
                          (Will integrate with CMC)
        """
        self.context_loader = context_loader
    
    def replay(
        self,
        vif: Any,  # VIF witness
        operation: Callable[[Dict[str, Any]], Any],
        *,
        verify_hash: bool = True,
    ) -> ReplayResult:
        """Replay an operation from its VIF witness
        
        Args:
            vif: VIF witness containing full provenance
            operation: Function that executes the operation
            verify_hash: If True, verify output hash matches
            
        Returns:
            ReplayResult with success status and verification
        """
        import time
        
        start_time = time.perf_counter()
        
        try:
            # Load context from snapshot
            context = self._load_context(vif.context_snapshot_id)
            
            # Prepare replay parameters
            replay_params = {
                "context": context,
                "seed": vif.replay_seed,
                "temperature": vif.temperature,
                "top_p": vif.top_p,
                "top_k": vif.top_k,
                "max_tokens": vif.max_tokens,
                **vif.other_params,
            }
            
            # Execute operation
            output = operation(replay_params)
            
            # Calculate execution time
            execution_time_ms = (time.perf_counter() - start_time) * 1000.0
            
            # Hash output
            output_str = str(output)
            output_hash = hashlib.sha256(output_str.encode("utf-8")).hexdigest()
            
            # Verify against original
            matches = False
            if verify_hash:
                matches = (output_hash == vif.output_hash)
            
            return ReplayResult(
                success=True,
                output=output,
                output_hash=output_hash,
                matches_original=matches,
                original_hash=vif.output_hash,
                execution_time_ms=execution_time_ms,
            )
        
        except Exception as e:
            execution_time_ms = (time.perf_counter() - start_time) * 1000.0
            
            return ReplayResult(
                success=False,
                error=str(e),
                execution_time_ms=execution_time_ms,
            )
    
    def _load_context(self, snapshot_id: str) -> Dict[str, Any]:
        """Load context from CMC snapshot
        
        Args:
            snapshot_id: CMC snapshot ID
            
        Returns:
            Context dictionary
        """
        if self.context_loader:
            return self.context_loader(snapshot_id)
        else:
            # Fallback: return empty context
            # (In production, would load from CMC)
            return {"snapshot_id": snapshot_id}
    
    def verify_witness(
        self,
        vif: Any,  # VIF witness
        actual_output: str,
    ) -> bool:
        """Verify an output matches its witness
        
        Args:
            vif: VIF witness
            actual_output: Actual output to verify
            
        Returns:
            True if output hash matches witness
        """
        actual_hash = hashlib.sha256(actual_output.encode("utf-8")).hexdigest()
        return actual_hash == vif.output_hash
    
    def batch_replay(
        self,
        vifs: list[Any],
        operation: Callable[[Dict[str, Any]], Any],
    ) -> list[ReplayResult]:
        """Replay multiple operations in batch
        
        Args:
            vifs: List of VIF witnesses
            operation: Operation function
            
        Returns:
            List of ReplayResults
        """
        results = []
        for vif in vifs:
            result = self.replay(vif, operation)
            results.append(result)
        return results
    
    def calculate_reproducibility_rate(
        self,
        results: list[ReplayResult]
    ) -> float:
        """Calculate what fraction of replays matched original
        
        Args:
            results: List of replay results
            
        Returns:
            Reproducibility rate (0.0-1.0)
        """
        if not results:
            return 0.0
        
        matches = sum(1 for r in results if r.matches_original)
        return matches / len(results)


def create_replay_witness(
    operation_name: str,
    original_vif: Any,
    replay_result: ReplayResult,
) -> Dict[str, Any]:
    """Create a witness for a replay operation
    
    Args:
        operation_name: Name of operation that was replayed
        original_vif: VIF of original operation
        replay_result: Result of replay
        
    Returns:
        Replay witness dictionary
    """
    return {
        "operation": operation_name,
        "original_vif_id": original_vif.id,
        "replay_timestamp": datetime.now().isoformat(),
        "success": replay_result.success,
        "matches_original": replay_result.matches_original,
        "output_hash": replay_result.output_hash,
        "original_output_hash": original_vif.output_hash,
        "execution_time_ms": replay_result.execution_time_ms,
        "error": replay_result.error,
    }


class ReplayCache:
    """Cache for replay results to avoid redundant replays"""
    
    def __init__(self, max_size: int = 1000):
        """Initialize replay cache
        
        Args:
            max_size: Maximum number of cached results
        """
        self.cache: Dict[str, ReplayResult] = {}
        self.max_size = max_size
    
    def get(self, vif_id: str) -> Optional[ReplayResult]:
        """Get cached replay result"""
        return self.cache.get(vif_id)
    
    def put(self, vif_id: str, result: ReplayResult) -> None:
        """Cache replay result"""
        if len(self.cache) >= self.max_size:
            # Simple eviction: remove oldest
            oldest_key = next(iter(self.cache))
            del self.cache[oldest_key]
        
        self.cache[vif_id] = result
    
    def has(self, vif_id: str) -> bool:
        """Check if result is cached"""
        return vif_id in self.cache
    
    def clear(self) -> None:
        """Clear cache"""
        self.cache.clear()
    
    def size(self) -> int:
        """Get cache size"""
        return len(self.cache)

