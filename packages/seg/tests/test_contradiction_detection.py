"""Tests for contradiction detection."""

from __future__ import annotations

import pytest

from seg import SEGraph, Entity, Relation, RelationType


def test_detect_contradictions_empty_graph():
    """Test detecting contradictions in empty graph."""
    graph = SEGraph()
    
    contradictions = graph.detect_contradictions()
    
    assert len(contradictions) == 0


def test_detect_contradictions_no_contradicts_relations():
    """Test detecting contradictions when no CONTRADICTS relations exist."""
    graph = SEGraph()
    
    e1 = Entity(type="claim", name="Claim 1")
    e2 = Entity(type="claim", name="Claim 2")
    graph.add_entity(e1)
    graph.add_entity(e2)
    
    # Add SUPPORTS relation (not a contradiction)
    r = Relation(
        source_id=e1.id,
        target_id=e2.id,
        relation_type=RelationType.SUPPORTS
    )
    graph.add_relation(r)
    
    contradictions = graph.detect_contradictions()
    
    assert len(contradictions) == 0


def test_detect_explicit_contradiction():
    """Test detecting explicit CONTRADICTS relation."""
    graph = SEGraph()
    
    e1 = Entity(type="claim", name="Earth is flat")
    e2 = Entity(type="claim", name="Earth is round")
    graph.add_entity(e1)
    graph.add_entity(e2)
    
    # Add CONTRADICTS relation
    r = Relation(
        source_id=e1.id,
        target_id=e2.id,
        relation_type=RelationType.CONTRADICTS,
        confidence=0.95
    )
    graph.add_relation(r)
    
    contradictions = graph.detect_contradictions()
    
    assert len(contradictions) == 1
    assert contradictions[0].entity1_id == e1.id
    assert contradictions[0].entity2_id == e2.id
    assert contradictions[0].contradiction_type == "explicit_contradiction"


def test_detect_multiple_contradictions():
    """Test detecting multiple contradictions."""
    graph = SEGraph()
    
    e1 = Entity(type="claim", name="Claim A")
    e2 = Entity(type="claim", name="Claim B")
    e3 = Entity(type="claim", name="Claim C")
    e4 = Entity(type="claim", name="Claim D")
    
    graph.add_entity(e1)
    graph.add_entity(e2)
    graph.add_entity(e3)
    graph.add_entity(e4)
    
    # e1 contradicts e2
    r1 = Relation(
        source_id=e1.id,
        target_id=e2.id,
        relation_type=RelationType.CONTRADICTS
    )
    
    # e3 contradicts e4
    r2 = Relation(
        source_id=e3.id,
        target_id=e4.id,
        relation_type=RelationType.CONTRADICTS
    )
    
    graph.add_relation(r1)
    graph.add_relation(r2)
    
    contradictions = graph.detect_contradictions()
    
    assert len(contradictions) == 2


def test_contradiction_stored_in_graph():
    """Test that detected contradictions are stored."""
    graph = SEGraph()
    
    e1 = Entity(type="claim", name="A")
    e2 = Entity(type="claim", name="B")
    graph.add_entity(e1)
    graph.add_entity(e2)
    
    r = Relation(
        source_id=e1.id,
        target_id=e2.id,
        relation_type=RelationType.CONTRADICTS
    )
    graph.add_relation(r)
    
    contradictions = graph.detect_contradictions()
    
    # Check stored in graph
    assert len(graph.contradictions) == 1
    
    # Check returned list matches stored
    contradiction_id = contradictions[0].id
    assert contradiction_id in graph.contradictions


def test_contradiction_includes_confidence():
    """Test that contradiction includes relation confidence."""
    graph = SEGraph()
    
    e1 = Entity(type="claim", name="A")
    e2 = Entity(type="claim", name="B")
    graph.add_entity(e1)
    graph.add_entity(e2)
    
    r = Relation(
        source_id=e1.id,
        target_id=e2.id,
        relation_type=RelationType.CONTRADICTS,
        confidence=0.75
    )
    graph.add_relation(r)
    
    contradictions = graph.detect_contradictions()
    
    assert contradictions[0].confidence == 0.75


def test_contradiction_explanation():
    """Test that contradiction has explanation."""
    graph = SEGraph()
    
    e1 = Entity(type="claim", name="Sky is red")
    e2 = Entity(type="claim", name="Sky is blue")
    graph.add_entity(e1)
    graph.add_entity(e2)
    
    r = Relation(
        source_id=e1.id,
        target_id=e2.id,
        relation_type=RelationType.CONTRADICTS
    )
    graph.add_relation(r)
    
    contradictions = graph.detect_contradictions()
    
    assert "contradicts" in contradictions[0].explanation.lower()

