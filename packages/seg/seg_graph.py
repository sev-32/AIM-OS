"""SEG (Shared Evidence Graph) main graph implementation.

Uses NetworkX for in-memory graph storage with bitemporal support.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional, List, Dict, Any, Tuple
import networkx as nx

from .models import (
    Entity,
    Relation,
    Evidence,
    Contradiction,
    TimeSlice,
    RelationType,
)


class SEGraph:
    """Shared Evidence Graph with bitemporal tracking.
    
    Manages entities, relations, and evidence with full time-travel capabilities.
    """
    
    def __init__(self):
        """Initialize empty SEG graph."""
        self.graph = nx.MultiDiGraph()  # Directed graph with multiple edges
        self.entities: Dict[str, Entity] = {}
        self.relations: Dict[str, Relation] = {}
        self.evidence: Dict[str, Evidence] = {}
        self.contradictions: Dict[str, Contradiction] = {}
    
    # ===== ENTITY OPERATIONS =====
    
    def add_entity(self, entity: Entity) -> Entity:
        """Add entity to graph.
        
        Args:
            entity: Entity to add
            
        Returns:
            The added entity
            
        Example:
            entity = Entity(
                type="concept",
                name="Neural Networks",
                attributes={"field": "ai"}
            )
            graph.add_entity(entity)
        """
        # Add to NetworkX graph
        self.graph.add_node(
            entity.id,
            node_type="entity",
            **entity.model_dump()
        )
        
        # Store in lookup dict
        self.entities[entity.id] = entity
        
        return entity
    
    def get_entity(self, entity_id: str, as_of: Optional[datetime] = None) -> Optional[Entity]:
        """Get entity by ID, optionally at a specific time.
        
        Args:
            entity_id: Entity ID
            as_of: Optional timestamp for time-travel query
            
        Returns:
            Entity if found and valid at the given time, None otherwise
        """
        entity = self.entities.get(entity_id)
        
        if entity is None:
            return None
        
        # If no time specified, return current version
        if as_of is None:
            return entity
        
        # Check if entity was valid at the given time
        if entity.tt_start <= as_of:
            if entity.tt_end is None or entity.tt_end > as_of:
                return entity
        
        return None
    
    def update_entity(self, entity_id: str, updates: Dict[str, Any]) -> Optional[Entity]:
        """Update entity attributes.
        
        Args:
            entity_id: Entity ID to update
            updates: Dictionary of attribute updates
            
        Returns:
            Updated entity, or None if not found
        """
        entity = self.entities.get(entity_id)
        
        if entity is None:
            return None
        
        # Create updated entity with new transaction time
        updated_data = entity.model_dump()
        updated_data.update(updates)
        updated_data['tt_start'] = datetime.now(timezone.utc)
        
        updated_entity = Entity(**updated_data)
        
        # Mark old version as ended
        entity.tt_end = datetime.now(timezone.utc)
        
        # Add new version
        self.entities[entity_id] = updated_entity
        self.graph.nodes[entity_id].update(updated_entity.model_dump())
        
        return updated_entity
    
    def list_entities(self, entity_type: Optional[str] = None, as_of: Optional[datetime] = None) -> List[Entity]:
        """List all entities, optionally filtered by type and time.
        
        Args:
            entity_type: Optional filter by entity type
            as_of: Optional timestamp for time-travel query
            
        Returns:
            List of matching entities
        """
        entities = []
        
        for entity in self.entities.values():
            # Filter by type if specified
            if entity_type and entity.type != entity_type:
                continue
            
            # Filter by time if specified
            if as_of:
                if entity.tt_start > as_of:
                    continue
                if entity.tt_end and entity.tt_end <= as_of:
                    continue
            
            entities.append(entity)
        
        return entities
    
    # ===== RELATION OPERATIONS =====
    
    def add_relation(self, relation: Relation) -> Relation:
        """Add relation (edge) between entities.
        
        Args:
            relation: Relation to add
            
        Returns:
            The added relation
            
        Example:
            relation = Relation(
                source_id="entity_1",
                target_id="entity_2",
                relation_type=RelationType.SUPPORTS,
                confidence=0.85
            )
            graph.add_relation(relation)
        """
        # Verify entities exist
        if relation.source_id not in self.entities:
            raise ValueError(f"Source entity {relation.source_id} not found")
        if relation.target_id not in self.entities:
            raise ValueError(f"Target entity {relation.target_id} not found")
        
        # Add to NetworkX graph
        self.graph.add_edge(
            relation.source_id,
            relation.target_id,
            key=relation.id,
            edge_type="relation",
            **relation.model_dump()
        )
        
        # Store in lookup dict
        self.relations[relation.id] = relation
        
        return relation
    
    def get_relation(self, relation_id: str) -> Optional[Relation]:
        """Get relation by ID."""
        return self.relations.get(relation_id)
    
    def get_relations(
        self,
        source_id: Optional[str] = None,
        target_id: Optional[str] = None,
        relation_type: Optional[RelationType] = None,
        as_of: Optional[datetime] = None
    ) -> List[Relation]:
        """Get relations with optional filters.
        
        Args:
            source_id: Filter by source entity
            target_id: Filter by target entity
            relation_type: Filter by relation type
            as_of: Optional timestamp for time-travel query
            
        Returns:
            List of matching relations
        """
        relations = []
        
        for relation in self.relations.values():
            # Apply filters
            if source_id and relation.source_id != source_id:
                continue
            if target_id and relation.target_id != target_id:
                continue
            if relation_type and relation.relation_type != relation_type:
                continue
            
            # Time filter
            if as_of:
                if relation.tt_start > as_of:
                    continue
                if relation.tt_end and relation.tt_end <= as_of:
                    continue
            
            relations.append(relation)
        
        return relations
    
    def get_incoming_relations(self, entity_id: str) -> List[Relation]:
        """Get all relations pointing to this entity."""
        return self.get_relations(target_id=entity_id)
    
    def get_outgoing_relations(self, entity_id: str) -> List[Relation]:
        """Get all relations from this entity."""
        return self.get_relations(source_id=entity_id)
    
    # ===== EVIDENCE OPERATIONS =====
    
    def add_evidence(self, evidence: Evidence) -> Evidence:
        """Add evidence to graph.
        
        Args:
            evidence: Evidence to add
            
        Returns:
            The added evidence
        """
        # Add to NetworkX graph as a node
        self.graph.add_node(
            evidence.id,
            node_type="evidence",
            **evidence.model_dump()
        )
        
        # Store in lookup dict
        self.evidence[evidence.id] = evidence
        
        return evidence
    
    def get_evidence(self, evidence_id: str) -> Optional[Evidence]:
        """Get evidence by ID."""
        return self.evidence.get(evidence_id)
    
    def list_evidence(self, as_of: Optional[datetime] = None) -> List[Evidence]:
        """List all evidence, optionally at a specific time."""
        evidence_list = []
        
        for evidence in self.evidence.values():
            if as_of:
                if evidence.tt_start > as_of:
                    continue
                if evidence.tt_end and evidence.tt_end <= as_of:
                    continue
            
            evidence_list.append(evidence)
        
        return evidence_list
    
    # ===== TIME-TRAVEL QUERIES =====
    
    def query_at(self, timestamp: datetime) -> TimeSlice:
        """Get a snapshot of the graph at a specific time.
        
        Args:
            timestamp: Point in time to query
            
        Returns:
            TimeSlice with counts and metadata
            
        Example:
            # See what the graph looked like yesterday
            snapshot = graph.query_at(datetime(2025, 10, 22))
            print(f"Had {snapshot.entity_count} entities")
        """
        entities = self.list_entities(as_of=timestamp)
        relations = self.get_relations(as_of=timestamp)
        evidence = self.list_evidence(as_of=timestamp)
        
        return TimeSlice(
            timestamp=timestamp,
            entity_count=len(entities),
            relation_count=len(relations),
            evidence_count=len(evidence),
            metadata={
                "query_type": "time_slice",
                "entities": [e.id for e in entities[:10]],  # Sample
                "relations": [r.id for r in relations[:10]]  # Sample
            }
        )
    
    def get_entity_history(self, entity_id: str) -> List[Entity]:
        """Get complete history of an entity across all versions.
        
        Args:
            entity_id: Entity ID
            
        Returns:
            List of entity versions, oldest first
        """
        # For now, we only have current version
        # In a full implementation, we'd track all versions
        entity = self.entities.get(entity_id)
        return [entity] if entity else []
    
    def trace_provenance(self, entity_id: str, max_depth: int = 5) -> List[Tuple[Entity, Relation]]:
        """Trace provenance chain for an entity.
        
        Args:
            entity_id: Entity to trace
            max_depth: Maximum depth to traverse
            
        Returns:
            List of (entity, relation) pairs showing provenance chain
        """
        provenance = []
        visited = set()
        
        def trace_recursive(current_id: str, depth: int):
            if depth >= max_depth or current_id in visited:
                return
            
            visited.add(current_id)
            
            # Get incoming "derives_from" relations
            incoming = self.get_incoming_relations(current_id)
            for relation in incoming:
                if relation.relation_type == RelationType.DERIVES_FROM:
                    source_entity = self.get_entity(relation.source_id)
                    if source_entity:
                        provenance.append((source_entity, relation))
                        trace_recursive(relation.source_id, depth + 1)
        
        trace_recursive(entity_id, 0)
        return provenance
    
    # ===== CONTRADICTION DETECTION =====
    
    def detect_contradictions(self) -> List[Contradiction]:
        """Detect potential contradictions in the graph.
        
        Returns:
            List of detected contradictions
            
        Example:
            contradictions = graph.detect_contradictions()
            for c in contradictions:
                print(f"Found contradiction: {c.explanation}")
        """
        contradictions = []
        
        # Look for explicit CONTRADICTS relations
        contradicting_relations = self.get_relations(relation_type=RelationType.CONTRADICTS)
        
        for relation in contradicting_relations:
            entity1 = self.get_entity(relation.source_id)
            entity2 = self.get_entity(relation.target_id)
            
            if entity1 and entity2:
                contradiction = Contradiction(
                    entity1_id=entity1.id,
                    entity2_id=entity2.id,
                    contradiction_type="explicit_contradiction",
                    similarity=0.0,  # Explicitly marked as contradictory
                    confidence=relation.confidence,
                    explanation=f"{entity1.name} contradicts {entity2.name}"
                )
                contradictions.append(contradiction)
        
        # Store detected contradictions
        for contradiction in contradictions:
            self.contradictions[contradiction.id] = contradiction
        
        return contradictions
    
    # ===== GRAPH STATISTICS =====
    
    def stats(self) -> Dict[str, Any]:
        """Get graph statistics.
        
        Returns:
            Dictionary with entity counts, relation counts, etc.
        """
        return {
            "entity_count": len(self.entities),
            "relation_count": len(self.relations),
            "evidence_count": len(self.evidence),
            "contradiction_count": len(self.contradictions),
            "graph_nodes": self.graph.number_of_nodes(),
            "graph_edges": self.graph.number_of_edges()
        }
    
    # ===== PERSISTENCE (Future) =====
    
    def to_dict(self) -> Dict[str, Any]:
        """Export graph to dictionary (for serialization)."""
        return {
            "entities": {id: e.model_dump() for id, e in self.entities.items()},
            "relations": {id: r.model_dump() for id, r in self.relations.items()},
            "evidence": {id: e.model_dump() for id, e in self.evidence.items()},
            "contradictions": {id: c.model_dump() for id, c in self.contradictions.items()},
            "stats": self.stats()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SEGraph':
        """Import graph from dictionary."""
        graph = cls()
        
        # Load entities
        for entity_data in data.get("entities", {}).values():
            entity = Entity(**entity_data)
            graph.add_entity(entity)
        
        # Load evidence
        for evidence_data in data.get("evidence", {}).values():
            evidence = Evidence(**evidence_data)
            graph.add_evidence(evidence)
        
        # Load relations
        for relation_data in data.get("relations", {}).values():
            relation = Relation(**relation_data)
            graph.add_relation(relation)
        
        return graph

