# CMC Cross-Model Atom Extensions

**Created:** 2025-10-23  
**Purpose:** Extend CMC atom schema for cross-model consciousness storage  
**Status:** Atom Schema Design Complete  

---

## 🎯 **OVERVIEW**

This document extends the existing CMC (Context Memory Core) atom schema to support cross-model consciousness, enabling storage of insights, transfer history, and cross-model provenance while maintaining the existing CMC capabilities and bitemporal storage principles.

---

## 🏗️ **EXTENDED ATOM SCHEMA**

### **Current CMC Atom Schema**
```python
@dataclass
class Atom:
    """Core CMC atom schema"""
    
    # Identity
    atom_id: str
    timestamp: datetime
    version: int
    
    # Content
    content: AtomContent
    modality: str
    
    # Provenance
    source: str
    source_version: str
    
    # Metadata
    metadata: Dict[str, Any]
    
    # Bitemporal
    valid_from: datetime
    valid_to: Optional[datetime]
    
    # Quality
    quality_score: float
    confidence: float
```

### **Extended CMC Atom Schema**
```python
@dataclass
class CrossModelAtom:
    """Extended CMC atom schema for cross-model consciousness"""
    
    # Identity
    atom_id: str = field(default_factory=lambda: f"atom_{uuid.uuid4().hex}")
    timestamp: datetime = field(default_factory=datetime.now)
    version: int = 1
    
    # Content
    content: CrossModelAtomContent
    modality: str = "cross_model"
    
    # Cross-Model Information
    source_models: List[str]                 # Models involved in creation
    model_insights: List[ModelInsight]       # Insights from each model
    transfer_history: List[TransferRecord]   # Transfer history
    
    # Insight Information
    insight_id: str                          # Reference to insight
    insight_quality: float                   # Quality of insight
    insight_confidence: float                # Confidence in insight
    
    # Knowledge Transfer
    knowledge_transfer: KnowledgeTransfer    # Transfer metadata
    transfer_quality: float                  # Quality of transfer
    transfer_confidence: float               # Confidence in transfer
    
    # Cross-Model Provenance
    cross_model_provenance: CrossModelProvenance  # Cross-model provenance
    model_interactions: List[ModelInteraction]    # Model interactions
    
    # Cost & Performance
    cost_breakdown: Dict[str, float]         # Cost breakdown by model
    performance_metrics: Dict[str, float]    # Performance metrics
    
    # Quality Assurance
    quality_preservation: QualityPreservation # Quality preservation tracking
    validation_results: List[ValidationResult] # Validation results
    
    # Bitemporal (inherited from CMC)
    valid_from: datetime = field(default_factory=datetime.now)
    valid_to: Optional[datetime] = None
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Quality
    quality_score: float = 0.0
    confidence: float = 0.0
```

---

## 🔍 **CROSS-MODEL ATOM CONTENT**

### **CrossModelAtomContent**
```python
@dataclass
class CrossModelAtomContent:
    """Content structure for cross-model atoms"""
    
    # Content Type
    content_type: str = "cross_model_insight"
    content_version: str = "1.0.0"
    
    # Insight Content
    problem_analysis: str                    # Analysis of the problem
    recommended_approach: str                # Recommended solution approach
    key_considerations: List[str]            # Key considerations
    potential_risks: List[str]               # Potential risks
    success_criteria: List[str]              # Success criteria
    
    # Context Information
    minimal_context_used: str                # Context provided to smart model
    full_context_available: str              # Full context available
    context_summary: str                     # Summary of relevant context
    
    # Model Outputs
    smart_model_output: str                  # Raw output from smart model
    execution_model_output: str              # Raw output from execution model
    
    # Transfer Information
    transfer_metadata: Dict[str, Any]        # Transfer metadata
    transfer_validation: Dict[str, Any]      # Transfer validation results
    
    # Quality Information
    quality_metrics: Dict[str, float]        # Quality metrics
    quality_validation: Dict[str, Any]       # Quality validation results
    
    # Cost Information
    cost_metrics: Dict[str, float]           # Cost metrics
    cost_optimization: Dict[str, Any]        # Cost optimization results
```

### **ModelInsight**
```python
@dataclass
class ModelInsight:
    """Insight from a specific model"""
    
    model_id: str                            # Model identifier
    model_version: str                       # Model version
    insight_type: str                        # Type of insight
    
    # Insight Content
    insight_content: str                     # Insight content
    insight_confidence: float                # Confidence in insight
    insight_quality: float                   # Quality of insight
    
    # Context Information
    context_used: str                        # Context used by model
    context_compression_ratio: float         # Context compression ratio
    
    # Performance Information
    response_time: float                     # Response time
    token_count: int                         # Token count
    cost: float                              # Cost of operation
    
    # Quality Information
    quality_metrics: Dict[str, float]        # Quality metrics
    validation_results: List[ValidationResult] # Validation results
```

### **TransferRecord**
```python
@dataclass
class TransferRecord:
    """Record of knowledge transfer"""
    
    transfer_id: str = field(default_factory=lambda: f"transfer_{uuid.uuid4().hex}")
    transfer_timestamp: datetime = field(default_factory=datetime.now)
    
    # Transfer Information
    source_model: str                        # Source model
    target_model: str                        # Target model
    transfer_type: str                       # Type of transfer
    
    # Transfer Content
    transfer_content: str                    # Content transferred
    transfer_metadata: Dict[str, Any]        # Transfer metadata
    
    # Transfer Quality
    transfer_quality: float                  # Quality of transfer
    transfer_confidence: float               # Confidence in transfer
    transfer_completeness: float             # Completeness of transfer
    
    # Transfer Validation
    validation_checks: List[str]             # Validation checks performed
    validation_results: List[ValidationResult] # Validation results
    
    # Transfer Metrics
    transfer_latency: float                  # Transfer latency
    transfer_size: int                       # Transfer size
    transfer_compression_ratio: float        # Compression ratio
```

---

## 🔄 **ATOM CREATION PIPELINE**

### **Cross-Model Atom Creation**
```python
class CrossModelAtomCreator:
    """Create cross-model atoms"""
    
    def __init__(self, config: AtomCreationConfig):
        self.config = config
        self.content_processor = ContentProcessor()
        self.quality_assessor = QualityAssessor()
        self.cost_calculator = CostCalculator()
    
    def create_cross_model_atom(self, insight: CrossModelInsight, 
                               transfer_result: TransferResult,
                               execution_result: ExecutionResult) -> CrossModelAtom:
        """Create cross-model atom from insight and results"""
        
        # Process content
        content = self._process_content(insight, transfer_result, execution_result)
        
        # Assess quality
        quality_score = self._assess_quality(insight, transfer_result, execution_result)
        
        # Calculate confidence
        confidence = self._calculate_confidence(insight, transfer_result, execution_result)
        
        # Create atom
        atom = CrossModelAtom(
            content=content,
            source_models=[insight.source_model, execution_result.model_id],
            model_insights=self._extract_model_insights(insight, execution_result),
            transfer_history=self._extract_transfer_history(transfer_result),
            insight_id=insight.insight_id,
            insight_quality=insight.quality_score,
            insight_confidence=insight.source_confidence,
            knowledge_transfer=transfer_result.knowledge_transfer,
            transfer_quality=transfer_result.transfer_confidence,
            transfer_confidence=transfer_result.transfer_confidence,
            cost_breakdown=self._calculate_cost_breakdown(insight, execution_result),
            performance_metrics=self._extract_performance_metrics(insight, execution_result),
            quality_score=quality_score,
            confidence=confidence
        )
        
        return atom
    
    def _process_content(self, insight: CrossModelInsight, 
                        transfer_result: TransferResult,
                        execution_result: ExecutionResult) -> CrossModelAtomContent:
        """Process content for cross-model atom"""
        
        return CrossModelAtomContent(
            problem_analysis=insight.problem_analysis,
            recommended_approach=insight.recommended_approach,
            key_considerations=insight.key_considerations,
            potential_risks=insight.potential_risks,
            success_criteria=insight.success_criteria,
            minimal_context_used=insight.minimal_context_used,
            full_context_available=execution_result.full_context,
            context_summary=insight.context_summary,
            smart_model_output=insight.raw_output,
            execution_model_output=execution_result.output,
            transfer_metadata=transfer_result.transfer_metadata,
            transfer_validation=transfer_result.validation_results,
            quality_metrics=execution_result.quality_metrics,
            quality_validation=execution_result.quality_validation,
            cost_metrics=execution_result.cost_breakdown,
            cost_optimization=execution_result.cost_optimization
        )
    
    def _assess_quality(self, insight: CrossModelInsight, 
                       transfer_result: TransferResult,
                       execution_result: ExecutionResult) -> float:
        """Assess overall quality of cross-model operation"""
        
        # Weighted quality assessment
        insight_quality_weight = 0.3
        transfer_quality_weight = 0.2
        execution_quality_weight = 0.5
        
        overall_quality = (
            insight.quality_score * insight_quality_weight +
            transfer_result.transfer_confidence * transfer_quality_weight +
            execution_result.quality_score * execution_quality_weight
        )
        
        return overall_quality
    
    def _calculate_confidence(self, insight: CrossModelInsight, 
                             transfer_result: TransferResult,
                             execution_result: ExecutionResult) -> float:
        """Calculate overall confidence"""
        
        # Weighted confidence assessment
        insight_confidence_weight = 0.3
        transfer_confidence_weight = 0.2
        execution_confidence_weight = 0.5
        
        overall_confidence = (
            insight.source_confidence * insight_confidence_weight +
            transfer_result.transfer_confidence * transfer_confidence_weight +
            execution_result.confidence * execution_confidence_weight
        )
        
        return overall_confidence
```

---

## 📊 **ATOM STORAGE STRATEGY**

### **Storage Organization**
```python
class CrossModelAtomStorage:
    """Storage strategy for cross-model atoms"""
    
    def __init__(self, config: StorageConfig):
        self.config = config
        self.storage_engine = StorageEngine()
        self.indexer = CrossModelIndexer()
    
    def store_cross_model_atom(self, atom: CrossModelAtom) -> StorageResult:
        """Store cross-model atom"""
        
        # Store atom content
        content_result = self._store_atom_content(atom)
        
        # Store model insights
        insights_result = self._store_model_insights(atom.model_insights)
        
        # Store transfer history
        transfer_result = self._store_transfer_history(atom.transfer_history)
        
        # Index atom for retrieval
        index_result = self._index_atom(atom)
        
        return StorageResult(
            content_result=content_result,
            insights_result=insights_result,
            transfer_result=transfer_result,
            index_result=index_result
        )
    
    def _store_atom_content(self, atom: CrossModelAtom) -> StorageResult:
        """Store atom content"""
        
        # Store in CMC with bitemporal tracking
        storage_result = self.storage_engine.store_atom(
            atom_id=atom.atom_id,
            content=atom.content,
            timestamp=atom.timestamp,
            valid_from=atom.valid_from,
            valid_to=atom.valid_to
        )
        
        return storage_result
    
    def _store_model_insights(self, model_insights: List[ModelInsight]) -> StorageResult:
        """Store model insights"""
        
        storage_results = []
        for insight in model_insights:
            result = self.storage_engine.store_model_insight(insight)
            storage_results.append(result)
        
        return StorageResult(insights=storage_results)
    
    def _store_transfer_history(self, transfer_history: List[TransferRecord]) -> StorageResult:
        """Store transfer history"""
        
        storage_results = []
        for transfer in transfer_history:
            result = self.storage_engine.store_transfer_record(transfer)
            storage_results.append(result)
        
        return StorageResult(transfers=storage_results)
    
    def _index_atom(self, atom: CrossModelAtom) -> IndexResult:
        """Index atom for retrieval"""
        
        # Index by source models
        model_index = self.indexer.index_by_models(atom.source_models)
        
        # Index by insight type
        insight_index = self.indexer.index_by_insight_type(atom.content.content_type)
        
        # Index by quality score
        quality_index = self.indexer.index_by_quality(atom.quality_score)
        
        # Index by cost
        cost_index = self.indexer.index_by_cost(atom.cost_breakdown)
        
        return IndexResult(
            model_index=model_index,
            insight_index=insight_index,
            quality_index=quality_index,
            cost_index=cost_index
        )
```

---

## 🔍 **QUERY PATTERNS**

### **Cross-Model Query Patterns**
```python
class CrossModelQueryEngine:
    """Query engine for cross-model atoms"""
    
    def __init__(self, config: QueryConfig):
        self.config = config
        self.query_processor = QueryProcessor()
        self.index_manager = IndexManager()
    
    def query_by_models(self, model_ids: List[str]) -> List[CrossModelAtom]:
        """Query atoms by source models"""
        
        # Query index for model IDs
        index_results = self.index_manager.query_by_models(model_ids)
        
        # Retrieve atoms
        atoms = []
        for index_result in index_results:
            atom = self._retrieve_atom(index_result.atom_id)
            atoms.append(atom)
        
        return atoms
    
    def query_by_insight_type(self, insight_type: str) -> List[CrossModelAtom]:
        """Query atoms by insight type"""
        
        # Query index for insight type
        index_results = self.index_manager.query_by_insight_type(insight_type)
        
        # Retrieve atoms
        atoms = []
        for index_result in index_results:
            atom = self._retrieve_atom(index_result.atom_id)
            atoms.append(atom)
        
        return atoms
    
    def query_by_quality_range(self, min_quality: float, max_quality: float) -> List[CrossModelAtom]:
        """Query atoms by quality range"""
        
        # Query index for quality range
        index_results = self.index_manager.query_by_quality_range(min_quality, max_quality)
        
        # Retrieve atoms
        atoms = []
        for index_result in index_results:
            atom = self._retrieve_atom(index_result.atom_id)
            atoms.append(atom)
        
        return atoms
    
    def query_by_cost_range(self, min_cost: float, max_cost: float) -> List[CrossModelAtom]:
        """Query atoms by cost range"""
        
        # Query index for cost range
        index_results = self.index_manager.query_by_cost_range(min_cost, max_cost)
        
        # Retrieve atoms
        atoms = []
        for index_result in index_results:
            atom = self._retrieve_atom(index_result.atom_id)
            atoms.append(atom)
        
        return atoms
    
    def query_by_transfer_history(self, source_model: str, target_model: str) -> List[CrossModelAtom]:
        """Query atoms by transfer history"""
        
        # Query index for transfer history
        index_results = self.index_manager.query_by_transfer_history(source_model, target_model)
        
        # Retrieve atoms
        atoms = []
        for index_result in index_results:
            atom = self._retrieve_atom(index_result.atom_id)
            atoms.append(atom)
        
        return atoms
    
    def _retrieve_atom(self, atom_id: str) -> CrossModelAtom:
        """Retrieve atom by ID"""
        
        # Retrieve from storage
        atom_data = self.storage_engine.retrieve_atom(atom_id)
        
        # Deserialize atom
        atom = self._deserialize_atom(atom_data)
        
        return atom
```

---

## 📊 **ATOM ANALYTICS**

### **Cross-Model Analytics**
```python
class CrossModelAtomAnalytics:
    """Analytics for cross-model atoms"""
    
    def __init__(self, config: AnalyticsConfig):
        self.config = config
        self.analytics_engine = AnalyticsEngine()
        self.metrics_collector = MetricsCollector()
    
    def analyze_cross_model_atoms(self, atoms: List[CrossModelAtom]) -> CrossModelAnalytics:
        """Analyze cross-model atoms"""
        
        # Analyze model insights
        insight_analysis = self._analyze_model_insights(atoms)
        
        # Analyze transfer history
        transfer_analysis = self._analyze_transfer_history(atoms)
        
        # Analyze quality trends
        quality_analysis = self._analyze_quality_trends(atoms)
        
        # Analyze cost trends
        cost_analysis = self._analyze_cost_trends(atoms)
        
        # Analyze performance trends
        performance_analysis = self._analyze_performance_trends(atoms)
        
        return CrossModelAnalytics(
            insight_analysis=insight_analysis,
            transfer_analysis=transfer_analysis,
            quality_analysis=quality_analysis,
            cost_analysis=cost_analysis,
            performance_analysis=performance_analysis
        )
    
    def _analyze_model_insights(self, atoms: List[CrossModelAtom]) -> InsightAnalysis:
        """Analyze model insights"""
        
        # Collect insight metrics
        insight_metrics = []
        for atom in atoms:
            for insight in atom.model_insights:
                insight_metrics.append({
                    "model_id": insight.model_id,
                    "insight_type": insight.insight_type,
                    "quality": insight.insight_quality,
                    "confidence": insight.insight_confidence,
                    "cost": insight.cost
                })
        
        # Analyze metrics
        analysis = self.analytics_engine.analyze_insight_metrics(insight_metrics)
        
        return analysis
    
    def _analyze_transfer_history(self, atoms: List[CrossModelAtom]) -> TransferAnalysis:
        """Analyze transfer history"""
        
        # Collect transfer metrics
        transfer_metrics = []
        for atom in atoms:
            for transfer in atom.transfer_history:
                transfer_metrics.append({
                    "source_model": transfer.source_model,
                    "target_model": transfer.target_model,
                    "transfer_type": transfer.transfer_type,
                    "quality": transfer.transfer_quality,
                    "confidence": transfer.transfer_confidence,
                    "latency": transfer.transfer_latency
                })
        
        # Analyze metrics
        analysis = self.analytics_engine.analyze_transfer_metrics(transfer_metrics)
        
        return analysis
    
    def _analyze_quality_trends(self, atoms: List[CrossModelAtom]) -> QualityAnalysis:
        """Analyze quality trends"""
        
        # Collect quality metrics
        quality_metrics = []
        for atom in atoms:
            quality_metrics.append({
                "timestamp": atom.timestamp,
                "quality_score": atom.quality_score,
                "confidence": atom.confidence,
                "insight_quality": atom.insight_quality,
                "transfer_quality": atom.transfer_quality
            })
        
        # Analyze trends
        analysis = self.analytics_engine.analyze_quality_trends(quality_metrics)
        
        return analysis
    
    def _analyze_cost_trends(self, atoms: List[CrossModelAtom]) -> CostAnalysis:
        """Analyze cost trends"""
        
        # Collect cost metrics
        cost_metrics = []
        for atom in atoms:
            cost_metrics.append({
                "timestamp": atom.timestamp,
                "total_cost": sum(atom.cost_breakdown.values()),
                "cost_breakdown": atom.cost_breakdown
            })
        
        # Analyze trends
        analysis = self.analytics_engine.analyze_cost_trends(cost_metrics)
        
        return analysis
    
    def _analyze_performance_trends(self, atoms: List[CrossModelAtom]) -> PerformanceAnalysis:
        """Analyze performance trends"""
        
        # Collect performance metrics
        performance_metrics = []
        for atom in atoms:
            performance_metrics.append({
                "timestamp": atom.timestamp,
                "performance_metrics": atom.performance_metrics
            })
        
        # Analyze trends
        analysis = self.analytics_engine.analyze_performance_trends(performance_metrics)
        
        return analysis
```

---

## 🔄 **SNAPSHOT IMPLICATIONS**

### **Cross-Model Snapshot Strategy**
```python
class CrossModelSnapshotManager:
    """Manage snapshots for cross-model atoms"""
    
    def __init__(self, config: SnapshotConfig):
        self.config = config
        self.snapshot_engine = SnapshotEngine()
        self.version_manager = VersionManager()
    
    def create_cross_model_snapshot(self, timestamp: datetime) -> SnapshotResult:
        """Create snapshot of cross-model atoms"""
        
        # Create snapshot of atoms
        atom_snapshot = self._create_atom_snapshot(timestamp)
        
        # Create snapshot of model insights
        insight_snapshot = self._create_insight_snapshot(timestamp)
        
        # Create snapshot of transfer history
        transfer_snapshot = self._create_transfer_snapshot(timestamp)
        
        # Create snapshot of indexes
        index_snapshot = self._create_index_snapshot(timestamp)
        
        return SnapshotResult(
            atom_snapshot=atom_snapshot,
            insight_snapshot=insight_snapshot,
            transfer_snapshot=transfer_snapshot,
            index_snapshot=index_snapshot,
            timestamp=timestamp
        )
    
    def restore_cross_model_snapshot(self, snapshot_id: str) -> RestoreResult:
        """Restore cross-model snapshot"""
        
        # Restore atom snapshot
        atom_restore = self._restore_atom_snapshot(snapshot_id)
        
        # Restore insight snapshot
        insight_restore = self._restore_insight_snapshot(snapshot_id)
        
        # Restore transfer snapshot
        transfer_restore = self._restore_transfer_snapshot(snapshot_id)
        
        # Restore index snapshot
        index_restore = self._restore_index_snapshot(snapshot_id)
        
        return RestoreResult(
            atom_restore=atom_restore,
            insight_restore=insight_restore,
            transfer_restore=transfer_restore,
            index_restore=index_restore
        )
```

---

## 🎯 **IMPLEMENTATION STRATEGY**

### **Phase 1: Schema Extension**
- Extend atom schema with cross-model fields
- Implement cross-model content structures
- Add validation for cross-model data

### **Phase 2: Storage Strategy**
- Implement cross-model atom storage
- Add indexing for cross-model queries
- Implement snapshot support

### **Phase 3: Query Patterns**
- Implement cross-model query patterns
- Add analytics for cross-model atoms
- Implement performance optimization

### **Phase 4: Integration**
- Integrate with APOE extensions
- Integrate with VIF extensions
- Test end-to-end cross-model flow

---

## 📋 **TESTING STRATEGY**

### **Unit Tests**
- Test schema extensions
- Test atom creation pipeline
- Test storage strategy
- Test query patterns

### **Integration Tests**
- Test with APOE extensions
- Test with VIF extensions
- Test with HHNI integration
- Test end-to-end cross-model flow

### **Performance Tests**
- Benchmark atom storage
- Benchmark query performance
- Benchmark snapshot operations
- Validate bitemporal storage

---

## 🎉 **CONCLUSION**

This extended CMC atom schema provides:

1. **Comprehensive Storage:** Store cross-model insights and transfer history
2. **Bitemporal Tracking:** Maintain temporal integrity for cross-model operations
3. **Query Patterns:** Efficient retrieval of cross-model information
4. **Analytics Support:** Comprehensive analytics for cross-model operations
5. **Snapshot Support:** Reliable snapshot and restore capabilities

**Next Steps:**
- Implement schema extensions
- Add storage strategy
- Implement query patterns
- Test with real scenarios

---

*This schema serves as the foundation for TODO 1.7: Design MCP Tool Specifications*

**Status:** ✅ Complete  
**Confidence:** 0.90 (High confidence in schema design)  
**Next:** TODO 1.7 - Design MCP Tool Specifications
