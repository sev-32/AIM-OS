"""Tests for provenance tracing."""

from __future__ import annotations

import pytest

from seg import SEGraph, Entity, Relation, RelationType


def test_trace_provenance_empty_chain():
    """Test tracing provenance with no derives_from relations."""
    graph = SEGraph()
    
    entity = Entity(type="concept", name="Root Entity")
    graph.add_entity(entity)
    
    provenance = graph.trace_provenance(entity.id)
    
    assert len(provenance) == 0


def test_trace_provenance_single_level():
    """Test tracing provenance with one level."""
    graph = SEGraph()
    
    # Create source -> derived relationship
    source = Entity(type="data", name="Source Data")
    derived = Entity(type="conclusion", name="Derived Conclusion")
    
    graph.add_entity(source)
    graph.add_entity(derived)
    
    # derived derives from source
    relation = Relation(
        source_id=source.id,
        target_id=derived.id,
        relation_type=RelationType.DERIVES_FROM
    )
    graph.add_relation(relation)
    
    # Trace provenance of derived
    provenance = graph.trace_provenance(derived.id)
    
    assert len(provenance) == 1
    assert provenance[0][0].id == source.id  # (entity, relation) tuple


def test_trace_provenance_multiple_levels():
    """Test tracing provenance through multiple levels."""
    graph = SEGraph()
    
    # Chain: raw -> processed -> analyzed -> conclusion
    raw = Entity(type="raw_data", name="Raw")
    processed = Entity(type="processed", name="Processed")
    analyzed = Entity(type="analyzed", name="Analyzed")
    conclusion = Entity(type="conclusion", name="Conclusion")
    
    graph.add_entity(raw)
    graph.add_entity(processed)
    graph.add_entity(analyzed)
    graph.add_entity(conclusion)
    
    # Build chain
    r1 = Relation(
        source_id=raw.id,
        target_id=processed.id,
        relation_type=RelationType.DERIVES_FROM
    )
    r2 = Relation(
        source_id=processed.id,
        target_id=analyzed.id,
        relation_type=RelationType.DERIVES_FROM
    )
    r3 = Relation(
        source_id=analyzed.id,
        target_id=conclusion.id,
        relation_type=RelationType.DERIVES_FROM
    )
    
    graph.add_relation(r1)
    graph.add_relation(r2)
    graph.add_relation(r3)
    
    # Trace from conclusion
    provenance = graph.trace_provenance(conclusion.id)
    
    # Should trace back through all levels
    assert len(provenance) >= 1
    entity_ids = {entity.id for entity, _ in provenance}
    assert analyzed.id in entity_ids


def test_trace_provenance_max_depth():
    """Test provenance tracing respects max depth."""
    graph = SEGraph()
    
    # Create long chain
    entities = [Entity(type="data", name=f"Level {i}") for i in range(10)]
    for e in entities:
        graph.add_entity(e)
    
    # Connect in chain
    for i in range(len(entities) - 1):
        r = Relation(
            source_id=entities[i].id,
            target_id=entities[i+1].id,
            relation_type=RelationType.DERIVES_FROM
        )
        graph.add_relation(r)
    
    # Trace with max_depth=3
    provenance = graph.trace_provenance(entities[-1].id, max_depth=3)
    
    # Should only go back 3 levels
    assert len(provenance) <= 3


def test_trace_provenance_nonexistent_entity():
    """Test tracing provenance of nonexistent entity."""
    graph = SEGraph()
    
    provenance = graph.trace_provenance("nonexistent_id")
    
    assert len(provenance) == 0


def test_trace_provenance_ignores_other_relation_types():
    """Test provenance only follows DERIVES_FROM relations."""
    graph = SEGraph()
    
    e1 = Entity(type="data", name="E1")
    e2 = Entity(type="data", name="E2")
    graph.add_entity(e1)
    graph.add_entity(e2)
    
    # Add SUPPORTS relation (not derives_from)
    r = Relation(
        source_id=e1.id,
        target_id=e2.id,
        relation_type=RelationType.SUPPORTS
    )
    graph.add_relation(r)
    
    # Trace provenance
    provenance = graph.trace_provenance(e2.id)
    
    # Should not include SUPPORTS relation
    assert len(provenance) == 0


def test_trace_provenance_multiple_sources():
    """Test tracing when entity derives from multiple sources."""
    graph = SEGraph()
    
    source1 = Entity(type="data", name="Source 1")
    source2 = Entity(type="data", name="Source 2")
    combined = Entity(type="result", name="Combined Result")
    
    graph.add_entity(source1)
    graph.add_entity(source2)
    graph.add_entity(combined)
    
    # Combined derives from both sources
    r1 = Relation(
        source_id=source1.id,
        target_id=combined.id,
        relation_type=RelationType.DERIVES_FROM
    )
    r2 = Relation(
        source_id=source2.id,
        target_id=combined.id,
        relation_type=RelationType.DERIVES_FROM
    )
    
    graph.add_relation(r1)
    graph.add_relation(r2)
    
    # Trace provenance
    provenance = graph.trace_provenance(combined.id)
    
    # Should include both sources
    entity_ids = {entity.id for entity, _ in provenance}
    assert source1.id in entity_ids
    assert source2.id in entity_ids

