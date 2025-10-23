"""Tests for SEG models (Entity, Relation, Evidence)."""

from __future__ import annotations

from datetime import datetime, timezone, timedelta

import pytest

from seg.models import (
    Entity,
    Relation,
    Evidence,
    Contradiction,
    TimeSlice,
    RelationType,
)


def test_entity_creation():
    """Test creating an entity."""
    entity = Entity(
        type="concept",
        name="Machine Learning",
        attributes={"field": "ai", "subfield": "supervised_learning"}
    )
    
    assert entity.id.startswith("entity_")
    assert entity.type == "concept"
    assert entity.name == "Machine Learning"
    assert entity.attributes["field"] == "ai"
    assert entity.confidence == 1.0
    assert entity.tt_start is not None
    assert entity.tt_end is None  # Current version


def test_entity_with_custom_id():
    """Test entity with custom ID."""
    entity = Entity(
        id="entity_custom_123",
        type="person",
        name="Alan Turing"
    )
    
    assert entity.id == "entity_custom_123"


def test_entity_bitemporal_tracking():
    """Test entity has bitemporal fields."""
    entity = Entity(type="event", name="Launch")
    
    assert entity.tt_start is not None  # Transaction time
    assert entity.vt_start is not None  # Valid time
    assert entity.tt_end is None
    assert entity.vt_end is None


def test_relation_creation():
    """Test creating a relation."""
    relation = Relation(
        source_id="entity_1",
        target_id="entity_2",
        relation_type=RelationType.SUPPORTS,
        confidence=0.85
    )
    
    assert relation.id.startswith("relation_")
    assert relation.source_id == "entity_1"
    assert relation.target_id == "entity_2"
    assert relation.relation_type == RelationType.SUPPORTS
    assert relation.confidence == 0.85


def test_relation_types():
    """Test all relation types."""
    types = [
        RelationType.SUPPORTS,
        RelationType.CONTRADICTS,
        RelationType.REFERENCES,
        RelationType.DERIVES_FROM,
        RelationType.RELATES_TO
    ]
    
    for rel_type in types:
        relation = Relation(
            source_id="a",
            target_id="b",
            relation_type=rel_type
        )
        assert relation.relation_type == rel_type


def test_relation_with_evidence():
    """Test relation can reference evidence."""
    relation = Relation(
        source_id="entity_1",
        target_id="entity_2",
        relation_type=RelationType.SUPPORTS,
        evidence_ids=["evidence_1", "evidence_2", "evidence_3"]
    )
    
    assert len(relation.evidence_ids) == 3
    assert "evidence_1" in relation.evidence_ids


def test_evidence_creation():
    """Test creating evidence."""
    evidence = Evidence(
        content="Research shows 95% accuracy on ImageNet",
        source="https://arxiv.org/abs/2023.12345",
        evidence_type="academic_paper",
        confidence=0.90,
        reliability=0.95
    )
    
    assert evidence.id.startswith("evidence_")
    assert evidence.content == "Research shows 95% accuracy on ImageNet"
    assert evidence.source.startswith("https://")
    assert evidence.confidence == 0.90
    assert evidence.reliability == 0.95


def test_evidence_with_atom_id():
    """Test evidence can reference CMC atom."""
    evidence = Evidence(
        content="Stored memory",
        source="cmc_atom",
        atom_id="atom_abc123"
    )
    
    assert evidence.atom_id == "atom_abc123"


def test_contradiction_creation():
    """Test creating a contradiction."""
    contradiction = Contradiction(
        entity1_id="entity_1",
        entity2_id="entity_2",
        contradiction_type="conflicting_claim",
        similarity=0.85,
        confidence=0.75,
        explanation="Both entities claim different values"
    )
    
    assert contradiction.id.startswith("contradiction_")
    assert contradiction.entity1_id == "entity_1"
    assert contradiction.entity2_id == "entity_2"
    assert contradiction.resolved is False
    assert contradiction.resolution is None


def test_contradiction_resolution():
    """Test resolving a contradiction."""
    contradiction = Contradiction(
        entity1_id="entity_1",
        entity2_id="entity_2",
        contradiction_type="conflict",
        similarity=0.9,
        confidence=0.8,
        explanation="Conflict detected"
    )
    
    # Resolve it
    contradiction.resolved = True
    contradiction.resolution = "Entity 1 was correct, entity 2 superseded"
    contradiction.resolved_at = datetime.now(timezone.utc)
    
    assert contradiction.resolved is True
    assert contradiction.resolution is not None
    assert contradiction.resolved_at is not None


def test_time_slice_creation():
    """Test creating a time slice."""
    timestamp = datetime.now(timezone.utc)
    slice = TimeSlice(
        timestamp=timestamp,
        entity_count=100,
        relation_count=50,
        evidence_count=25,
        metadata={"source": "test"}
    )
    
    assert slice.timestamp == timestamp
    assert slice.entity_count == 100
    assert slice.relation_count == 50
    assert slice.evidence_count == 25
    assert slice.metadata["source"] == "test"


def test_entity_model_dump():
    """Test entity can be serialized to dict."""
    entity = Entity(
        type="concept",
        name="Test",
        attributes={"key": "value"}
    )
    
    data = entity.model_dump()
    
    assert data["type"] == "concept"
    assert data["name"] == "Test"
    assert data["attributes"]["key"] == "value"
    assert "tt_start" in data
    assert "confidence" in data


def test_relation_model_dump():
    """Test relation can be serialized to dict."""
    relation = Relation(
        source_id="a",
        target_id="b",
        relation_type=RelationType.SUPPORTS
    )
    
    data = relation.model_dump()
    
    assert data["source_id"] == "a"
    assert data["target_id"] == "b"
    assert data["relation_type"] == "supports"


def test_evidence_model_dump():
    """Test evidence can be serialized to dict."""
    evidence = Evidence(
        content="Test evidence",
        source="test_source"
    )
    
    data = evidence.model_dump()
    
    assert data["content"] == "Test evidence"
    assert data["source"] == "test_source"
    assert "confidence" in data
    assert "reliability" in data


def test_entity_with_vif_witness():
    """Test entity can reference VIF witness."""
    entity = Entity(
        type="claim",
        name="AI claim",
        witness_id="witness_vif_123"
    )
    
    assert entity.witness_id == "witness_vif_123"


def test_relation_with_vif_witness():
    """Test relation can reference VIF witness."""
    relation = Relation(
        source_id="a",
        target_id="b",
        relation_type=RelationType.SUPPORTS,
        witness_id="witness_vif_456"
    )
    
    assert relation.witness_id == "witness_vif_456"


def test_evidence_with_vif_witness():
    """Test evidence can reference VIF witness."""
    evidence = Evidence(
        content="Proven fact",
        source="verification",
        witness_id="witness_vif_789"
    )
    
    assert evidence.witness_id == "witness_vif_789"

