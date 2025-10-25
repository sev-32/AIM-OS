"""
Cross-Model Atom Storage

Storage system for cross-model atoms, enabling efficient storage, retrieval,
and querying of cross-model consciousness operations while maintaining
CMC bitemporal storage principles.
"""

import logging
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple

from cmc_service.cross_model_atoms import CrossModelAtom, CrossModelAtomContent
from cmc_service.models import Atom, AtomContent, AtomCreate
from cmc_service.memory_store import MemoryStore


logger = logging.getLogger(__name__)


class StorageConfig:
    """Configuration for storage system"""
    
    def __init__(self,
                 enable_indexing: bool = True,
                 enable_compression: bool = True,
                 enable_caching: bool = True,
                 cache_size: int = 1000):
        self.enable_indexing = enable_indexing
        self.enable_compression = enable_indexing
        self.enable_caching = enable_caching
        self.cache_size = cache_size


class StorageResult:
    """Result of storage operation"""
    
    def __init__(self,
                 success: bool,
                 atom_id: str,
                 storage_time: float,
                 metadata: Dict[str, Any]):
        self.success = success
        self.atom_id = atom_id
        self.storage_time = storage_time
        self.metadata = metadata
        self.timestamp = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "success": self.success,
            "atom_id": self.atom_id,
            "storage_time": self.storage_time,
            "metadata": self.metadata,
            "timestamp": self.timestamp.isoformat()
        }


class IndexResult:
    """Result of indexing operation"""
    
    def __init__(self,
                 success: bool,
                 index_type: str,
                 index_count: int,
                 metadata: Dict[str, Any]):
        self.success = success
        self.index_type = index_type
        self.index_count = index_count
        self.metadata = metadata
        self.timestamp = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "success": self.success,
            "index_type": self.index_type,
            "index_count": self.index_count,
            "metadata": self.metadata,
            "timestamp": self.timestamp.isoformat()
        }


class CrossModelIndexer:
    """Indexer for cross-model atoms"""
    
    def __init__(self):
        self.model_index = {}
        self.insight_index = {}
        self.quality_index = {}
        self.cost_index = {}
        self.timestamp_index = {}
    
    def index_by_models(self, source_models: List[str]) -> IndexResult:
        """Index atom by source models"""
        
        try:
            index_count = 0
            for model_id in source_models:
                if model_id not in self.model_index:
                    self.model_index[model_id] = []
                
                # Add to index (in real implementation, would store atom references)
                index_count += 1
            
            return IndexResult(
                success=True,
                index_type="model_index",
                index_count=index_count,
                metadata={"models_indexed": source_models}
            )
            
        except Exception as e:
            logger.error(f"Error indexing by models: {e}")
            return IndexResult(
                success=False,
                index_type="model_index",
                index_count=0,
                metadata={"error": str(e)}
            )
    
    def index_by_insight_type(self, insight_type: str) -> IndexResult:
        """Index atom by insight type"""
        
        try:
            if insight_type not in self.insight_index:
                self.insight_index[insight_type] = []
            
            # Add to index
            return IndexResult(
                success=True,
                index_type="insight_index",
                index_count=1,
                metadata={"insight_type": insight_type}
            )
            
        except Exception as e:
            logger.error(f"Error indexing by insight type: {e}")
            return IndexResult(
                success=False,
                index_type="insight_index",
                index_count=0,
                metadata={"error": str(e)}
            )
    
    def index_by_quality(self, quality_score: float) -> IndexResult:
        """Index atom by quality score"""
        
        try:
            # Index by quality range
            quality_range = self._get_quality_range(quality_score)
            if quality_range not in self.quality_index:
                self.quality_index[quality_range] = []
            
            # Add to index
            return IndexResult(
                success=True,
                index_type="quality_index",
                index_count=1,
                metadata={"quality_range": quality_range, "quality_score": quality_score}
            )
            
        except Exception as e:
            logger.error(f"Error indexing by quality: {e}")
            return IndexResult(
                success=False,
                index_type="quality_index",
                index_count=0,
                metadata={"error": str(e)}
            )
    
    def index_by_cost(self, cost_breakdown: Dict[str, float]) -> IndexResult:
        """Index atom by cost"""
        
        try:
            total_cost = sum(cost_breakdown.values())
            cost_range = self._get_cost_range(total_cost)
            if cost_range not in self.cost_index:
                self.cost_index[cost_range] = []
            
            # Add to index
            return IndexResult(
                success=True,
                index_type="cost_index",
                index_count=1,
                metadata={"cost_range": cost_range, "total_cost": total_cost}
            )
            
        except Exception as e:
            logger.error(f"Error indexing by cost: {e}")
            return IndexResult(
                success=False,
                index_type="cost_index",
                index_count=0,
                metadata={"error": str(e)}
            )
    
    def index_by_timestamp(self, timestamp: datetime) -> IndexResult:
        """Index atom by timestamp"""
        
        try:
            # Index by date
            date_key = timestamp.date().isoformat()
            if date_key not in self.timestamp_index:
                self.timestamp_index[date_key] = []
            
            # Add to index
            return IndexResult(
                success=True,
                index_type="timestamp_index",
                index_count=1,
                metadata={"date": date_key, "timestamp": timestamp.isoformat()}
            )
            
        except Exception as e:
            logger.error(f"Error indexing by timestamp: {e}")
            return IndexResult(
                success=False,
                index_type="timestamp_index",
                index_count=0,
                metadata={"error": str(e)}
            )
    
    def _get_quality_range(self, quality_score: float) -> str:
        """Get quality range for indexing"""
        if quality_score >= 0.9:
            return "excellent"
        elif quality_score >= 0.7:
            return "good"
        elif quality_score >= 0.5:
            return "fair"
        else:
            return "poor"
    
    def _get_cost_range(self, total_cost: float) -> str:
        """Get cost range for indexing"""
        if total_cost <= 0.01:
            return "low"
        elif total_cost <= 0.05:
            return "medium"
        elif total_cost <= 0.10:
            return "high"
        else:
            return "very_high"
    
    def get_index_statistics(self) -> Dict[str, Any]:
        """Get index statistics"""
        return {
            "model_index_size": len(self.model_index),
            "insight_index_size": len(self.insight_index),
            "quality_index_size": len(self.quality_index),
            "cost_index_size": len(self.cost_index),
            "timestamp_index_size": len(self.timestamp_index),
            "total_index_entries": (
                len(self.model_index) + len(self.insight_index) +
                len(self.quality_index) + len(self.cost_index) +
                len(self.timestamp_index)
            )
        }


class StorageEngine:
    """Storage engine for cross-model atoms"""
    
    def __init__(self, memory_store: MemoryStore):
        self.memory_store = memory_store
        self.storage_cache = {}
    
    def store_atom(self, atom_id: str, content: CrossModelAtomContent,
                  timestamp: datetime, valid_from: datetime,
                  valid_to: Optional[datetime]) -> StorageResult:
        """Store atom in CMC"""
        
        try:
            # Create AtomContent
            atom_content = AtomContent(
                inline=content.to_dict()
            )
            
            # Create AtomCreate
            atom_create = AtomCreate(
                modality="cross_model",
                content=atom_content
            )
            
            # Store in CMC
            storage_start = datetime.now()
            result = self.memory_store.create_atom(atom_create)
            storage_time = (datetime.now() - storage_start).total_seconds()
            
            return StorageResult(
                success=True,
                atom_id=atom_id,
                storage_time=storage_time,
                metadata={"storage_result": result}
            )
            
        except Exception as e:
            logger.error(f"Error storing atom: {e}")
            return StorageResult(
                success=False,
                atom_id=atom_id,
                storage_time=0.0,
                metadata={"error": str(e)}
            )
    
    def retrieve_atom(self, atom_id: str) -> Optional[Atom]:
        """Retrieve atom from CMC"""
        
        try:
            # Retrieve from CMC
            atom = self.memory_store.get_atom(atom_id)
            return atom
            
        except Exception as e:
            logger.error(f"Error retrieving atom: {e}")
            return None
    
    def store_model_insight(self, insight_data: Dict[str, Any]) -> StorageResult:
        """Store model insight"""
        
        try:
            # Store model insight as separate atom
            insight_content = AtomContent(
                inline=insight_data
            )
            
            insight_create = AtomCreate(
                modality="model_insight",
                content=insight_content
            )
            
            storage_start = datetime.now()
            result = self.memory_store.create_atom(insight_create)
            storage_time = (datetime.now() - storage_start).total_seconds()
            
            return StorageResult(
                success=True,
                atom_id=result.get("atom_id", ""),
                storage_time=storage_time,
                metadata={"insight_data": insight_data}
            )
            
        except Exception as e:
            logger.error(f"Error storing model insight: {e}")
            return StorageResult(
                success=False,
                atom_id="",
                storage_time=0.0,
                metadata={"error": str(e)}
            )
    
    def store_transfer_record(self, transfer_data: Dict[str, Any]) -> StorageResult:
        """Store transfer record"""
        
        try:
            # Store transfer record as separate atom
            transfer_content = AtomContent(
                inline=transfer_data
            )
            
            transfer_create = AtomCreate(
                modality="transfer_record",
                content=transfer_content
            )
            
            storage_start = datetime.now()
            result = self.memory_store.create_atom(transfer_create)
            storage_time = (datetime.now() - storage_start).total_seconds()
            
            return StorageResult(
                success=True,
                atom_id=result.get("atom_id", ""),
                storage_time=storage_time,
                metadata={"transfer_data": transfer_data}
            )
            
        except Exception as e:
            logger.error(f"Error storing transfer record: {e}")
            return StorageResult(
                success=False,
                atom_id="",
                storage_time=0.0,
                metadata={"error": str(e)}
            )


class CrossModelAtomStorage:
    """Storage strategy for cross-model atoms"""
    
    def __init__(self, config: StorageConfig, memory_store: MemoryStore):
        self.config = config
        self.storage_engine = StorageEngine(memory_store)
        self.indexer = CrossModelIndexer()
        self.storage_cache = {}
        logger.info(f"Initialized CrossModelAtomStorage with config: {config}")
    
    def store_cross_model_atom(self, atom: CrossModelAtom) -> StorageResult:
        """Store cross-model atom"""
        
        logger.info(f"Storing cross-model atom: {atom.atom_id}")
        
        try:
            # Store atom content
            content_result = self._store_atom_content(atom)
            
            # Store model insights
            insights_result = self._store_model_insights(atom.model_insights)
            
            # Store transfer history
            transfer_result = self._store_transfer_history(atom.transfer_history)
            
            # Index atom for retrieval
            index_result = self._index_atom(atom)
            
            # Cache atom if caching is enabled
            if self.config.enable_caching:
                self._cache_atom(atom)
            
            # Create combined result
            combined_result = StorageResult(
                success=(
                    content_result.success and
                    insights_result.success and
                    transfer_result.success and
                    index_result.success
                ),
                atom_id=atom.atom_id,
                storage_time=(
                    content_result.storage_time +
                    insights_result.storage_time +
                    transfer_result.storage_time
                ),
                metadata={
                    "content_result": content_result.to_dict(),
                    "insights_result": insights_result.to_dict(),
                    "transfer_result": transfer_result.to_dict(),
                    "index_result": index_result.to_dict()
                }
            )
            
            logger.info(f"Successfully stored cross-model atom: {atom.atom_id}")
            return combined_result
            
        except Exception as e:
            logger.error(f"Error storing cross-model atom: {e}")
            return StorageResult(
                success=False,
                atom_id=atom.atom_id,
                storage_time=0.0,
                metadata={"error": str(e)}
            )
    
    def retrieve_cross_model_atom(self, atom_id: str) -> Optional[CrossModelAtom]:
        """Retrieve cross-model atom"""
        
        try:
            # Check cache first
            if self.config.enable_caching and atom_id in self.storage_cache:
                return self.storage_cache[atom_id]
            
            # Retrieve from storage
            atom = self.storage_engine.retrieve_atom(atom_id)
            if atom is None:
                return None
            
            # Convert to CrossModelAtom
            cross_model_atom = CrossModelAtom.from_cmc_atom(atom)
            
            # Cache if caching is enabled
            if self.config.enable_caching:
                self._cache_atom(cross_model_atom)
            
            return cross_model_atom
            
        except Exception as e:
            logger.error(f"Error retrieving cross-model atom: {e}")
            return None
    
    def _store_atom_content(self, atom: CrossModelAtom) -> StorageResult:
        """Store atom content"""
        
        return self.storage_engine.store_atom(
            atom_id=atom.atom_id,
            content=atom.content,
            timestamp=atom.timestamp,
            valid_from=atom.valid_from,
            valid_to=atom.valid_to
        )
    
    def _store_model_insights(self, model_insights: List[Any]) -> StorageResult:
        """Store model insights"""
        
        try:
            storage_results = []
            total_time = 0.0
            
            for insight in model_insights:
                insight_data = {
                    "model_id": insight.model_id,
                    "model_version": insight.model_version,
                    "insight_type": insight.insight_type,
                    "insight_content": insight.insight_content,
                    "insight_confidence": insight.insight_confidence,
                    "insight_quality": insight.insight_quality,
                    "context_used": insight.context_used,
                    "context_compression_ratio": insight.context_compression_ratio,
                    "response_time": insight.response_time,
                    "token_count": insight.token_count,
                    "cost": insight.cost,
                    "quality_metrics": insight.quality_metrics,
                    "validation_results": insight.validation_results
                }
                
                result = self.storage_engine.store_model_insight(insight_data)
                storage_results.append(result)
                total_time += result.storage_time
            
            return StorageResult(
                success=all(r.success for r in storage_results),
                atom_id="model_insights",
                storage_time=total_time,
                metadata={"insights_stored": len(storage_results)}
            )
            
        except Exception as e:
            logger.error(f"Error storing model insights: {e}")
            return StorageResult(
                success=False,
                atom_id="model_insights",
                storage_time=0.0,
                metadata={"error": str(e)}
            )
    
    def _store_transfer_history(self, transfer_history: List[Any]) -> StorageResult:
        """Store transfer history"""
        
        try:
            storage_results = []
            total_time = 0.0
            
            for transfer in transfer_history:
                transfer_data = {
                    "transfer_id": transfer.transfer_id,
                    "transfer_timestamp": transfer.transfer_timestamp.isoformat(),
                    "source_model": transfer.source_model,
                    "target_model": transfer.target_model,
                    "transfer_type": transfer.transfer_type,
                    "transfer_content": transfer.transfer_content,
                    "transfer_metadata": transfer.transfer_metadata,
                    "transfer_quality": transfer.transfer_quality,
                    "transfer_confidence": transfer.transfer_confidence,
                    "transfer_completeness": transfer.transfer_completeness,
                    "validation_checks": transfer.validation_checks,
                    "validation_results": transfer.validation_results,
                    "transfer_latency": transfer.transfer_latency,
                    "transfer_size": transfer.transfer_size,
                    "transfer_compression_ratio": transfer.transfer_compression_ratio
                }
                
                result = self.storage_engine.store_transfer_record(transfer_data)
                storage_results.append(result)
                total_time += result.storage_time
            
            return StorageResult(
                success=all(r.success for r in storage_results),
                atom_id="transfer_history",
                storage_time=total_time,
                metadata={"transfers_stored": len(storage_results)}
            )
            
        except Exception as e:
            logger.error(f"Error storing transfer history: {e}")
            return StorageResult(
                success=False,
                atom_id="transfer_history",
                storage_time=0.0,
                metadata={"error": str(e)}
            )
    
    def _index_atom(self, atom: CrossModelAtom) -> IndexResult:
        """Index atom for retrieval"""
        
        try:
            index_results = []
            
            # Index by source models
            if self.config.enable_indexing:
                model_index_result = self.indexer.index_by_models(atom.source_models)
                index_results.append(model_index_result)
                
                # Index by insight type
                insight_index_result = self.indexer.index_by_insight_type(atom.content.content_type)
                index_results.append(insight_index_result)
                
                # Index by quality score
                quality_index_result = self.indexer.index_by_quality(atom.quality_score)
                index_results.append(quality_index_result)
                
                # Index by cost
                cost_index_result = self.indexer.index_by_cost(atom.cost_breakdown)
                index_results.append(cost_index_result)
                
                # Index by timestamp
                timestamp_index_result = self.indexer.index_by_timestamp(atom.timestamp)
                index_results.append(timestamp_index_result)
            
            # Calculate total index count
            total_index_count = sum(result.index_count for result in index_results)
            
            return IndexResult(
                success=all(result.success for result in index_results),
                index_type="cross_model_atom",
                index_count=total_index_count,
                metadata={"index_results": [result.to_dict() for result in index_results]}
            )
            
        except Exception as e:
            logger.error(f"Error indexing atom: {e}")
            return IndexResult(
                success=False,
                index_type="cross_model_atom",
                index_count=0,
                metadata={"error": str(e)}
            )
    
    def _cache_atom(self, atom: CrossModelAtom) -> None:
        """Cache atom for fast retrieval"""
        
        if len(self.storage_cache) >= self.config.cache_size:
            # Remove oldest entry (simple LRU)
            oldest_key = next(iter(self.storage_cache))
            del self.storage_cache[oldest_key]
        
        self.storage_cache[atom.atom_id] = atom
    
    def get_storage_statistics(self) -> Dict[str, Any]:
        """Get storage statistics"""
        
        return {
            "indexing_enabled": self.config.enable_indexing,
            "compression_enabled": self.config.enable_compression,
            "caching_enabled": self.config.enable_caching,
            "cache_size": len(self.storage_cache),
            "max_cache_size": self.config.cache_size,
            "indexer_statistics": self.indexer.get_index_statistics()
        }
