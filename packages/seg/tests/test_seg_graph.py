"""Tests for SEGraph operations."""

from __future__ import annotations

from datetime import datetime, timezone, timedelta

import pytest

from seg import SEGraph, Entity, Relation, Evidence, RelationType


def test_create_empty_graph():
    """Test creating an empty SEG graph."""
    graph = SEGraph()
    
    assert graph.graph is not None
    assert len(graph.entities) == 0
    assert len(graph.relations) == 0
    assert len(graph.evidence) == 0


def test_add_entity():
    """Test adding an entity to the graph."""
    graph = SEGraph()
    entity = Entity(
        type="concept",
        name="Neural Networks",
        attributes={"field": "ai"}
    )
    
    result = graph.add_entity(entity)
    
    assert result == entity
    assert entity.id in graph.entities
    assert len(graph.entities) == 1


def test_get_entity():
    """Test retrieving an entity from the graph."""
    graph = SEGraph()
    entity = Entity(type="concept", name="Test")
    graph.add_entity(entity)
    
    retrieved = graph.get_entity(entity.id)
    
    assert retrieved is not None
    assert retrieved.id == entity.id
    assert retrieved.name == "Test"


def test_get_nonexistent_entity():
    """Test getting an entity that doesn't exist."""
    graph = SEGraph()
    
    result = graph.get_entity("nonexistent_id")
    
    assert result is None


def test_add_multiple_entities():
    """Test adding multiple entities."""
    graph = SEGraph()
    
    entities = [
        Entity(type="concept", name=f"Concept {i}")
        for i in range(5)
    ]
    
    for entity in entities:
        graph.add_entity(entity)
    
    assert len(graph.entities) == 5


def test_list_entities():
    """Test listing all entities."""
    graph = SEGraph()
    
    for i in range(3):
        entity = Entity(type="concept", name=f"Entity {i}")
        graph.add_entity(entity)
    
    entities = graph.list_entities()
    
    assert len(entities) == 3


def test_list_entities_by_type():
    """Test filtering entities by type."""
    graph = SEGraph()
    
    graph.add_entity(Entity(type="concept", name="C1"))
    graph.add_entity(Entity(type="concept", name="C2"))
    graph.add_entity(Entity(type="person", name="P1"))
    
    concepts = graph.list_entities(entity_type="concept")
    people = graph.list_entities(entity_type="person")
    
    assert len(concepts) == 2
    assert len(people) == 1


def test_add_relation():
    """Test adding a relation between entities."""
    graph = SEGraph()
    
    entity1 = Entity(type="concept", name="Entity 1")
    entity2 = Entity(type="concept", name="Entity 2")
    graph.add_entity(entity1)
    graph.add_entity(entity2)
    
    relation = Relation(
        source_id=entity1.id,
        target_id=entity2.id,
        relation_type=RelationType.SUPPORTS,
        confidence=0.9
    )
    
    result = graph.add_relation(relation)
    
    assert result == relation
    assert relation.id in graph.relations
    assert len(graph.relations) == 1


def test_add_relation_missing_source():
    """Test adding relation with missing source entity fails."""
    graph = SEGraph()
    
    entity2 = Entity(type="concept", name="Entity 2")
    graph.add_entity(entity2)
    
    relation = Relation(
        source_id="nonexistent",
        target_id=entity2.id,
        relation_type=RelationType.SUPPORTS
    )
    
    with pytest.raises(ValueError, match="Source entity"):
        graph.add_relation(relation)


def test_add_relation_missing_target():
    """Test adding relation with missing target entity fails."""
    graph = SEGraph()
    
    entity1 = Entity(type="concept", name="Entity 1")
    graph.add_entity(entity1)
    
    relation = Relation(
        source_id=entity1.id,
        target_id="nonexistent",
        relation_type=RelationType.SUPPORTS
    )
    
    with pytest.raises(ValueError, match="Target entity"):
        graph.add_relation(relation)


def test_get_relation():
    """Test retrieving a relation."""
    graph = SEGraph()
    
    entity1 = Entity(type="concept", name="E1")
    entity2 = Entity(type="concept", name="E2")
    graph.add_entity(entity1)
    graph.add_entity(entity2)
    
    relation = Relation(
        source_id=entity1.id,
        target_id=entity2.id,
        relation_type=RelationType.SUPPORTS
    )
    graph.add_relation(relation)
    
    retrieved = graph.get_relation(relation.id)
    
    assert retrieved is not None
    assert retrieved.id == relation.id


def test_get_relations_by_source():
    """Test getting relations filtered by source entity."""
    graph = SEGraph()
    
    e1 = Entity(type="concept", name="E1")
    e2 = Entity(type="concept", name="E2")
    e3 = Entity(type="concept", name="E3")
    graph.add_entity(e1)
    graph.add_entity(e2)
    graph.add_entity(e3)
    
    # e1 -> e2
    r1 = Relation(source_id=e1.id, target_id=e2.id, relation_type=RelationType.SUPPORTS)
    # e1 -> e3
    r2 = Relation(source_id=e1.id, target_id=e3.id, relation_type=RelationType.REFERENCES)
    # e2 -> e3
    r3 = Relation(source_id=e2.id, target_id=e3.id, relation_type=RelationType.SUPPORTS)
    
    graph.add_relation(r1)
    graph.add_relation(r2)
    graph.add_relation(r3)
    
    relations_from_e1 = graph.get_relations(source_id=e1.id)
    
    assert len(relations_from_e1) == 2


def test_get_relations_by_target():
    """Test getting relations filtered by target entity."""
    graph = SEGraph()
    
    e1 = Entity(type="concept", name="E1")
    e2 = Entity(type="concept", name="E2")
    e3 = Entity(type="concept", name="E3")
    graph.add_entity(e1)
    graph.add_entity(e2)
    graph.add_entity(e3)
    
    # e1 -> e3
    r1 = Relation(source_id=e1.id, target_id=e3.id, relation_type=RelationType.SUPPORTS)
    # e2 -> e3
    r2 = Relation(source_id=e2.id, target_id=e3.id, relation_type=RelationType.SUPPORTS)
    
    graph.add_relation(r1)
    graph.add_relation(r2)
    
    relations_to_e3 = graph.get_relations(target_id=e3.id)
    
    assert len(relations_to_e3) == 2


def test_get_relations_by_type():
    """Test getting relations filtered by type."""
    graph = SEGraph()
    
    e1 = Entity(type="concept", name="E1")
    e2 = Entity(type="concept", name="E2")
    graph.add_entity(e1)
    graph.add_entity(e2)
    
    r1 = Relation(source_id=e1.id, target_id=e2.id, relation_type=RelationType.SUPPORTS)
    r2 = Relation(source_id=e2.id, target_id=e1.id, relation_type=RelationType.CONTRADICTS)
    
    graph.add_relation(r1)
    graph.add_relation(r2)
    
    supports = graph.get_relations(relation_type=RelationType.SUPPORTS)
    contradicts = graph.get_relations(relation_type=RelationType.CONTRADICTS)
    
    assert len(supports) == 1
    assert len(contradicts) == 1


def test_get_incoming_relations():
    """Test getting incoming relations to an entity."""
    graph = SEGraph()
    
    e1 = Entity(type="concept", name="E1")
    e2 = Entity(type="concept", name="E2")
    e3 = Entity(type="concept", name="E3")
    graph.add_entity(e1)
    graph.add_entity(e2)
    graph.add_entity(e3)
    
    # e1 -> e3, e2 -> e3
    r1 = Relation(source_id=e1.id, target_id=e3.id, relation_type=RelationType.SUPPORTS)
    r2 = Relation(source_id=e2.id, target_id=e3.id, relation_type=RelationType.SUPPORTS)
    
    graph.add_relation(r1)
    graph.add_relation(r2)
    
    incoming = graph.get_incoming_relations(e3.id)
    
    assert len(incoming) == 2


def test_get_outgoing_relations():
    """Test getting outgoing relations from an entity."""
    graph = SEGraph()
    
    e1 = Entity(type="concept", name="E1")
    e2 = Entity(type="concept", name="E2")
    e3 = Entity(type="concept", name="E3")
    graph.add_entity(e1)
    graph.add_entity(e2)
    graph.add_entity(e3)
    
    # e1 -> e2, e1 -> e3
    r1 = Relation(source_id=e1.id, target_id=e2.id, relation_type=RelationType.SUPPORTS)
    r2 = Relation(source_id=e1.id, target_id=e3.id, relation_type=RelationType.REFERENCES)
    
    graph.add_relation(r1)
    graph.add_relation(r2)
    
    outgoing = graph.get_outgoing_relations(e1.id)
    
    assert len(outgoing) == 2


def test_add_evidence():
    """Test adding evidence to the graph."""
    graph = SEGraph()
    
    evidence = Evidence(
        content="Test evidence",
        source="test_source"
    )
    
    result = graph.add_evidence(evidence)
    
    assert result == evidence
    assert evidence.id in graph.evidence
    assert len(graph.evidence) == 1


def test_get_evidence():
    """Test retrieving evidence."""
    graph = SEGraph()
    
    evidence = Evidence(
        content="Test evidence",
        source="test"
    )
    graph.add_evidence(evidence)
    
    retrieved = graph.get_evidence(evidence.id)
    
    assert retrieved is not None
    assert retrieved.id == evidence.id


def test_list_evidence():
    """Test listing all evidence."""
    graph = SEGraph()
    
    for i in range(3):
        evidence = Evidence(
            content=f"Evidence {i}",
            source="test"
        )
        graph.add_evidence(evidence)
    
    evidence_list = graph.list_evidence()
    
    assert len(evidence_list) == 3


def test_graph_stats():
    """Test getting graph statistics."""
    graph = SEGraph()
    
    # Add entities
    e1 = Entity(type="concept", name="E1")
    e2 = Entity(type="concept", name="E2")
    graph.add_entity(e1)
    graph.add_entity(e2)
    
    # Add relation
    r = Relation(source_id=e1.id, target_id=e2.id, relation_type=RelationType.SUPPORTS)
    graph.add_relation(r)
    
    # Add evidence
    ev = Evidence(content="Test", source="test")
    graph.add_evidence(ev)
    
    stats = graph.stats()
    
    assert stats["entity_count"] == 2
    assert stats["relation_count"] == 1
    assert stats["evidence_count"] == 1
    assert stats["graph_nodes"] == 3  # 2 entities + 1 evidence
    assert stats["graph_edges"] == 1


def test_to_dict_and_from_dict():
    """Test serialization and deserialization of graph."""
    graph = SEGraph()
    
    # Build a small graph
    e1 = Entity(type="concept", name="E1")
    e2 = Entity(type="concept", name="E2")
    graph.add_entity(e1)
    graph.add_entity(e2)
    
    r = Relation(source_id=e1.id, target_id=e2.id, relation_type=RelationType.SUPPORTS)
    graph.add_relation(r)
    
    ev = Evidence(content="Test", source="test")
    graph.add_evidence(ev)
    
    # Serialize
    data = graph.to_dict()
    
    assert "entities" in data
    assert "relations" in data
    assert "evidence" in data
    assert "stats" in data
    
    # Deserialize
    restored_graph = SEGraph.from_dict(data)
    
    assert len(restored_graph.entities) == 2
    assert len(restored_graph.relations) == 1
    assert len(restored_graph.evidence) == 1

