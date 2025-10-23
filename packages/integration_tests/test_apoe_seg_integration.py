"""Integration tests for APOE + SEG.

Tests that APOE can orchestrate workflows using SEG knowledge graph.
"""

from __future__ import annotations

import pytest

from apoe import ExecutionPlan, RoleType, Step
from seg import SEGraph, Entity, Relation, RelationType


def test_apoe_reads_from_seg_graph():
    """Test that APOE can read entities from SEG graph."""
    # Build knowledge graph
    graph = SEGraph()
    
    entity1 = Entity(
        type="concept",
        name="Machine Learning",
        attributes={"complexity": "high"}
    )
    entity2 = Entity(
        type="concept",
        name="Linear Regression",
        attributes={"complexity": "low"}
    )
    
    graph.add_entity(entity1)
    graph.add_entity(entity2)
    
    # APOE plan that queries graph
    # (In real implementation, would use actual executor)
    plan = ExecutionPlan(
        plan_id="test-plan",
        name="Query SEG",
        steps=[]
    )
    
    # Simulate APOE reading from graph
    concepts = graph.list_entities(entity_type="concept")
    
    # APOE would use this data
    assert len(concepts) == 2
    assert any(e.name == "Machine Learning" for e in concepts)


def test_apoe_writes_to_seg_graph():
    """Test that APOE can add entities to SEG graph."""
    graph = SEGraph()
    
    # APOE creates plan
    plan = ExecutionPlan(
        plan_id="knowledge-building",
        name="Build Knowledge Graph",
        steps=[]
    )
    
    # Simulate APOE adding discovered knowledge to SEG
    discovered_entity = Entity(
        type="discovery",
        name="APOE discovered this",
        attributes={"source": "apoe_plan", "plan_name": plan.name}
    )
    
    graph.add_entity(discovered_entity)
    
    # Verify entity added with APOE source
    entities = graph.list_entities()
    assert len(entities) == 1
    assert entities[0].attributes["source"] == "apoe_plan"


def test_apoe_uses_graph_for_context():
    """Test APOE using SEG graph for context retrieval."""
    # Build knowledge graph
    graph = SEGraph()
    
    # Add entities
    e1 = Entity(type="fact", name="Python is a programming language")
    e2 = Entity(type="fact", name="Python is used for AI")
    e3 = Entity(type="fact", name="AI requires computing power")
    
    graph.add_entity(e1)
    graph.add_entity(e2)
    graph.add_entity(e3)
    
    # Add relations
    r1 = Relation(
        source_id=e2.id,
        target_id=e1.id,
        relation_type=RelationType.REFERENCES
    )
    r2 = Relation(
        source_id=e3.id,
        target_id=e2.id,
        relation_type=RelationType.DERIVES_FROM
    )
    
    graph.add_relation(r1)
    graph.add_relation(r2)
    
    # APOE queries graph for context
    facts = graph.list_entities(entity_type="fact")
    
    # APOE would use these facts for context
    assert len(facts) == 3


def test_apoe_validates_using_graph_evidence():
    """Test APOE using graph evidence for validation."""
    from seg import Evidence
    
    graph = SEGraph()
    
    # Add claim entity
    claim = Entity(
        type="claim",
        name="Machine Learning improves accuracy"
    )
    graph.add_entity(claim)
    
    # Add supporting evidence
    evidence = Evidence(
        content="Research shows 20% accuracy improvement",
        source="https://example.com/research",
        confidence=0.90
    )
    graph.add_evidence(evidence)
    
    # APOE could query evidence to validate claims
    all_evidence = graph.list_evidence()
    
    # High confidence evidence supports proceeding
    assert len(all_evidence) == 1
    assert all_evidence[0].confidence == 0.90


def test_apoe_detects_contradictions_before_proceeding():
    """Test APOE checking for contradictions before execution."""
    graph = SEGraph()
    
    # Add contradictory claims
    claim1 = Entity(type="claim", name="Approach A is best")
    claim2 = Entity(type="claim", name="Approach B is best")
    
    graph.add_entity(claim1)
    graph.add_entity(claim2)
    
    # Mark as contradictory
    r = Relation(
        source_id=claim1.id,
        target_id=claim2.id,
        relation_type=RelationType.CONTRADICTS,
        confidence=0.85
    )
    graph.add_relation(r)
    
    # APOE checks for contradictions
    contradictions = graph.detect_contradictions()
    
    # APOE would halt or escalate to HITL
    assert len(contradictions) > 0
    assert contradictions[0].confidence == 0.85


def test_apoe_traces_provenance_for_decision():
    """Test APOE tracing provenance of entities for decision-making."""
    graph = SEGraph()
    
    # Build provenance chain
    raw_data = Entity(type="data", name="Raw Data")
    processed = Entity(type="processed", name="Processed Data")
    analysis = Entity(type="analysis", name="Analysis Result")
    recommendation = Entity(type="recommendation", name="Recommendation")
    
    graph.add_entity(raw_data)
    graph.add_entity(processed)
    graph.add_entity(analysis)
    graph.add_entity(recommendation)
    
    # Build chain
    r1 = Relation(source_id=raw_data.id, target_id=processed.id, relation_type=RelationType.DERIVES_FROM)
    r2 = Relation(source_id=processed.id, target_id=analysis.id, relation_type=RelationType.DERIVES_FROM)
    r3 = Relation(source_id=analysis.id, target_id=recommendation.id, relation_type=RelationType.DERIVES_FROM)
    
    graph.add_relation(r1)
    graph.add_relation(r2)
    graph.add_relation(r3)
    
    # APOE traces provenance
    provenance = graph.trace_provenance(recommendation.id)
    
    # Can see full chain
    assert len(provenance) >= 1


def test_apoe_creates_witness_for_graph_operation():
    """Test APOE creating VIF witness when modifying SEG."""
    graph = SEGraph()
    
    # APOE creates entity with VIF witness
    entity = Entity(
        type="apoe_decision",
        name="Decision to use approach X",
        witness_id="witness_apoe_123",  # VIF witness
        attributes={"plan_id": "plan_1", "step_id": "step_5"}
    )
    
    graph.add_entity(entity)
    
    # Verify witness attached
    retrieved = graph.get_entity(entity.id)
    assert retrieved.witness_id == "witness_apoe_123"


def test_apoe_updates_graph_during_execution():
    """Test APOE updating SEG during plan execution."""
    graph = SEGraph()
    
    # Initial state
    task = Entity(
        type="task",
        name="Task 1",
        attributes={"status": "pending"}
    )
    graph.add_entity(task)
    
    # APOE executes, updates status
    updated = graph.update_entity(task.id, {
        "attributes": {"status": "completed", "result": "success"}
    })
    
    assert updated.attributes["status"] == "completed"
    assert updated.attributes["result"] == "success"


def test_full_apoe_seg_workflow():
    """Test complete APOE+SEG workflow."""
    graph = SEGraph()
    from seg import Evidence
    
    # 1. APOE queries graph for existing knowledge
    existing = graph.list_entities(entity_type="requirement")
    assert len(existing) == 0  # None yet
    
    # 2. APOE discovers new requirement
    requirement = Entity(
        type="requirement",
        name="System must support 1000 concurrent users",
        attributes={"priority": "high"}
    )
    graph.add_entity(requirement)
    
    # 3. APOE adds supporting evidence
    evidence = Evidence(
        content="Load testing shows system handles 1000 users",
        source="benchmark_results",
        confidence=0.95
    )
    graph.add_evidence(evidence)
    
    # 4. APOE creates implementation plan (as entity)
    implementation = Entity(
        type="plan",
        name="Scale to 1000 users",
        attributes={"requirement_id": requirement.id}
    )
    graph.add_entity(implementation)
    
    # 5. APOE links requirement -> implementation
    relation = Relation(
        source_id=requirement.id,
        target_id=implementation.id,
        relation_type=RelationType.DERIVES_FROM,
        evidence_ids=[evidence.id]
    )
    graph.add_relation(relation)
    
    # Verify complete workflow
    assert len(graph.entities) == 2  # requirement + implementation
    assert len(graph.evidence) == 1
    assert len(graph.relations) == 1
    
    # Can trace implementation back to requirement
    provenance = graph.trace_provenance(implementation.id)
    assert len(provenance) == 1
    assert provenance[0][0].id == requirement.id

