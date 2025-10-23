"""Tests for time-slice queries and bitemporal features."""

from __future__ import annotations

from datetime import datetime, timezone, timedelta

import pytest

from seg import SEGraph, Entity, Relation, RelationType


def test_query_at_current_time():
    """Test querying graph at current time."""
    graph = SEGraph()
    
    # Add some entities
    for i in range(3):
        entity = Entity(type="concept", name=f"Entity {i}")
        graph.add_entity(entity)
    
    # Query at current time
    now = datetime.now(timezone.utc)
    time_slice = graph.query_at(now)
    
    assert time_slice.entity_count == 3
    assert time_slice.relation_count == 0
    assert time_slice.evidence_count == 0


def test_query_at_past_time():
    """Test querying graph at a past time shows no entities."""
    graph = SEGraph()
    
    entity = Entity(type="concept", name="New Entity")
    graph.add_entity(entity)
    
    # Query at time before entity was added
    past = datetime.now(timezone.utc) - timedelta(hours=1)
    time_slice = graph.query_at(past)
    
    # Entity didn't exist yet
    assert time_slice.entity_count == 0


def test_get_entity_as_of_time():
    """Test getting entity as of a specific time."""
    graph = SEGraph()
    
    entity = Entity(type="concept", name="Test")
    graph.add_entity(entity)
    
    # Get at current time
    now = datetime.now(timezone.utc)
    result = graph.get_entity(entity.id, as_of=now)
    
    assert result is not None
    assert result.id == entity.id


def test_get_entity_as_of_past_returns_none():
    """Test getting entity at time before it existed returns None."""
    graph = SEGraph()
    
    entity = Entity(type="concept", name="Test")
    graph.add_entity(entity)
    
    # Query before entity existed
    past = datetime.now(timezone.utc) - timedelta(days=1)
    result = graph.get_entity(entity.id, as_of=past)
    
    assert result is None


def test_list_entities_as_of_time():
    """Test listing entities at a specific time."""
    graph = SEGraph()
    
    # Add entities at different times (simulated)
    e1 = Entity(
        type="concept",
        name="Old Entity",
        tt_start=datetime.now(timezone.utc) - timedelta(days=2)
    )
    graph.add_entity(e1)
    
    e2 = Entity(
        type="concept",
        name="New Entity",
        tt_start=datetime.now(timezone.utc)
    )
    graph.add_entity(e2)
    
    # Query at time when only e1 existed
    yesterday = datetime.now(timezone.utc) - timedelta(days=1)
    entities = graph.list_entities(as_of=yesterday)
    
    # Only e1 should be visible
    assert len(entities) == 1
    assert entities[0].name == "Old Entity"


def test_get_relations_as_of_time():
    """Test getting relations at a specific time."""
    graph = SEGraph()
    
    e1 = Entity(type="concept", name="E1")
    e2 = Entity(type="concept", name="E2")
    graph.add_entity(e1)
    graph.add_entity(e2)
    
    relation = Relation(
        source_id=e1.id,
        target_id=e2.id,
        relation_type=RelationType.SUPPORTS
    )
    graph.add_relation(relation)
    
    # Query at current time
    now = datetime.now(timezone.utc)
    relations = graph.get_relations(as_of=now)
    
    assert len(relations) == 1


def test_list_evidence_as_of_time():
    """Test listing evidence at a specific time."""
    from seg import Evidence
    
    graph = SEGraph()
    
    evidence = Evidence(content="Test", source="test")
    graph.add_evidence(evidence)
    
    # Query at current time
    now = datetime.now(timezone.utc)
    evidence_list = graph.list_evidence(as_of=now)
    
    assert len(evidence_list) == 1


def test_get_entity_history():
    """Test getting entity history."""
    graph = SEGraph()
    
    entity = Entity(type="concept", name="Test")
    graph.add_entity(entity)
    
    history = graph.get_entity_history(entity.id)
    
    # Currently only tracks latest version
    assert len(history) == 1
    assert history[0].id == entity.id


def test_get_entity_history_nonexistent():
    """Test getting history of nonexistent entity."""
    graph = SEGraph()
    
    history = graph.get_entity_history("nonexistent")
    
    assert len(history) == 0


def test_update_entity():
    """Test updating entity creates new version."""
    graph = SEGraph()
    
    entity = Entity(type="concept", name="Original Name")
    graph.add_entity(entity)
    
    # Update the entity
    updated = graph.update_entity(entity.id, {"name": "Updated Name"})
    
    assert updated is not None
    assert updated.name == "Updated Name"
    assert updated.tt_start != entity.tt_start  # New transaction time


def test_update_nonexistent_entity():
    """Test updating nonexistent entity returns None."""
    graph = SEGraph()
    
    result = graph.update_entity("nonexistent", {"name": "New"})
    
    assert result is None

