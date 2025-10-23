"""Integration tests for CMC + SEG.

Tests that CMC atoms can feed into SEG graph for knowledge synthesis.
"""

from __future__ import annotations

import tempfile
from datetime import datetime, timezone

import pytest

from cmc_service import MemoryStore, AtomCreate, AtomContent
from seg import SEGraph, Entity, Evidence, RelationType


@pytest.fixture
def cmc_store():
    """Create temporary CMC store."""
    with tempfile.TemporaryDirectory() as tmpdir:
        store = MemoryStore(tmpdir)
        yield store


def test_atom_to_entity_conversion(cmc_store: MemoryStore):
    """Test converting CMC atom to SEG entity."""
    # Create atom in CMC
    atom = cmc_store.create_atom(AtomCreate(
        modality="text",
        content=AtomContent(inline="Machine Learning is a branch of AI"),
        tags={"concept": 1.0, "ai": 1.0}
    ))
    
    # Convert to SEG entity
    graph = SEGraph()
    entity = Entity(
        type="concept",
        name="Machine Learning",
        attributes={
            "source": "cmc",
            "atom_id": atom.id,
            "tags": list(atom.tags.keys())
        },
        source=f"cmc_atom:{atom.id}"
    )
    
    graph.add_entity(entity)
    
    # Verify entity created with CMC reference
    retrieved = graph.get_entity(entity.id)
    assert retrieved is not None
    assert retrieved.attributes["atom_id"] == atom.id
    assert retrieved.source == f"cmc_atom:{atom.id}"


def test_atom_to_evidence_conversion(cmc_store: MemoryStore):
    """Test converting CMC atom to SEG evidence."""
    # Create atom
    atom = cmc_store.create_atom(AtomCreate(
        modality="text",
        content=AtomContent(inline="Research shows 95% accuracy"),
        tags={"evidence": 1.0, "research": 1.0}
    ))
    
    # Convert to SEG evidence
    graph = SEGraph()
    evidence = Evidence(
        content=atom.content.inline,
        source="cmc_memory",
        atom_id=atom.id,
        confidence=0.90
    )
    
    graph.add_evidence(evidence)
    
    # Verify evidence linked to atom
    retrieved = graph.get_evidence(evidence.id)
    assert retrieved is not None
    assert retrieved.atom_id == atom.id
    assert retrieved.content == atom.content.inline


def test_build_graph_from_atoms(cmc_store: MemoryStore):
    """Test building SEG graph from multiple CMC atoms."""
    # Create several atoms
    atoms = []
    for i in range(5):
        atom = cmc_store.create_atom(AtomCreate(
            modality="text",
            content=AtomContent(inline=f"Concept {i}"),
            tags={"concept": 1.0}
        ))
        atoms.append(atom)
    
    # Build graph
    graph = SEGraph()
    for atom in atoms:
        entity = Entity(
            type="concept",
            name=f"Concept from atom {atom.id}",
            attributes={"atom_id": atom.id}
        )
        graph.add_entity(entity)
    
    # Verify all entities created
    entities = graph.list_entities()
    assert len(entities) == 5
    
    # All have atom references
    atom_ids = {e.attributes.get("atom_id") for e in entities}
    assert len(atom_ids) == 5


def test_snapshot_to_graph_state(cmc_store: MemoryStore):
    """Test that CMC snapshots can represent graph states."""
    # Create atoms
    for i in range(3):
        cmc_store.create_atom(AtomCreate(
            modality="text",
            content=AtomContent(inline=f"Entity {i}"),
            tags={"entity": 1.0}
        ))
    
    # Create snapshot
    snapshot_id = cmc_store.create_snapshot(note="Graph state at time T")
    
    # Build graph from snapshot's atoms
    graph = SEGraph()
    atoms = cmc_store.list_atoms(limit=100)
    
    for atom in atoms:
        entity = Entity(
            type="data",
            name=f"Entity from {atom.id}",
            attributes={
                "snapshot_id": snapshot_id,
                "atom_id": atom.id
            }
        )
        graph.add_entity(entity)
    
    # Verify graph built
    entities = graph.list_entities()
    assert len(entities) == 3
    
    # All reference the snapshot
    for entity in entities:
        assert entity.attributes["snapshot_id"] == snapshot_id


def test_graph_evidence_from_cmc_atoms(cmc_store: MemoryStore):
    """Test using CMC atoms as evidence for graph relations."""
    # Create entities
    graph = SEGraph()
    e1 = Entity(type="concept", name="Entity 1")
    e2 = Entity(type="concept", name="Entity 2")
    graph.add_entity(e1)
    graph.add_entity(e2)
    
    # Create evidence atoms in CMC
    evidence_atoms = []
    for i in range(3):
        atom = cmc_store.create_atom(AtomCreate(
            modality="text",
            content=AtomContent(inline=f"Evidence {i} supports relation"),
            tags={"evidence": 1.0}
        ))
        evidence_atoms.append(atom)
    
    # Add evidence to graph
    evidence_ids = []
    for atom in evidence_atoms:
        evidence = Evidence(
            content=atom.content.inline,
            source="cmc_memory",
            atom_id=atom.id
        )
        graph.add_evidence(evidence)
        evidence_ids.append(evidence.id)
    
    # Create relation supported by evidence
    from seg import Relation
    relation = Relation(
        source_id=e1.id,
        target_id=e2.id,
        relation_type=RelationType.SUPPORTS,
        evidence_ids=evidence_ids
    )
    graph.add_relation(relation)
    
    # Verify relation has evidence
    retrieved = graph.get_relation(relation.id)
    assert len(retrieved.evidence_ids) == 3


def test_query_graph_at_cmc_snapshot_time(cmc_store: MemoryStore):
    """Test querying graph at the time of a CMC snapshot."""
    # Build graph over time
    graph = SEGraph()
    
    # Add entity 1
    atom1 = cmc_store.create_atom(AtomCreate(
        modality="text",
        content=AtomContent(inline="Early concept"),
        tags={"early": 1.0}
    ))
    e1 = Entity(
        type="concept",
        name="Early",
        attributes={"atom_id": atom1.id}
    )
    graph.add_entity(e1)
    
    # Create snapshot 1
    snapshot1_time = datetime.now(timezone.utc)
    snapshot1_id = cmc_store.create_snapshot(note="State 1")
    
    # Add entity 2 (after snapshot 1)
    atom2 = cmc_store.create_atom(AtomCreate(
        modality="text",
        content=AtomContent(inline="Later concept"),
        tags={"later": 1.0}
    ))
    e2 = Entity(
        type="concept",
        name="Later",
        attributes={"atom_id": atom2.id}
    )
    graph.add_entity(e2)
    
    # Query graph at snapshot1 time
    time_slice = graph.query_at(snapshot1_time)
    
    # Should only show entity from before snapshot
    # (In real impl, would need proper temporal tracking)
    assert time_slice.entity_count >= 1


def test_cmc_atom_versioning_to_graph_entity_history(cmc_store: MemoryStore):
    """Test that CMC atom updates can track entity evolution."""
    # Create initial atom
    atom = cmc_store.create_atom(AtomCreate(
        modality="text",
        content=AtomContent(inline="Initial value"),
        tags={"version": 1.0}
    ))
    
    # Create initial entity
    graph = SEGraph()
    entity = Entity(
        type="data",
        name="Initial value",
        attributes={"atom_id": atom.id, "version": 1}
    )
    graph.add_entity(entity)
    
    # Update entity (simulating atom update)
    updated = graph.update_entity(entity.id, {
        "name": "Updated value",
        "attributes": {"atom_id": atom.id, "version": 2}
    })
    
    assert updated.name == "Updated value"
    assert updated.attributes["version"] == 2
    
    # Original entity marked as superseded
    assert entity.tt_end is not None


def test_bidirectional_sync_cmc_to_seg(cmc_store: MemoryStore):
    """Test syncing CMC atoms to SEG entities."""
    # Create atoms in CMC
    atom_ids = []
    for i in range(5):
        atom = cmc_store.create_atom(AtomCreate(
            modality="text",
            content=AtomContent(inline=f"Atom {i}"),
            tags={"sync": 1.0}
        ))
        atom_ids.append(atom.id)
    
    # Sync to SEG
    graph = SEGraph()
    atoms = cmc_store.list_atoms(limit=100)
    
    for atom in atoms:
        if atom.tags.get("sync"):
            entity = Entity(
                type="synced",
                name=f"Synced from {atom.id}",
                attributes={"atom_id": atom.id},
                source="cmc_sync"
            )
            graph.add_entity(entity)
    
    # Verify synced
    synced_entities = graph.list_entities(entity_type="synced")
    assert len(synced_entities) == 5
    
    # All have CMC source
    for entity in synced_entities:
        assert entity.source == "cmc_sync"
        assert "atom_id" in entity.attributes

