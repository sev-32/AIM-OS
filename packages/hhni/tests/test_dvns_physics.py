"""Tests for the DVNS physics engine."""

from __future__ import annotations

import math

import pytest

from hhni.dvns_physics import (
    ContextParticle,
    DVNSConfig,
    DVNSPhysics,
    SimulationMetrics,
    SimulationResult,
    Vector,
    create_particles_from_search,
)
from hhni.hierarchical_index import HierarchicalIndex, IndexLevel
from hhni.semantic_search import SemanticSearchEngine


def _make_particle(
    particle_id: str,
    *,
    embedding=None,
    position=None,
    velocity=None,
    mass: float = 1.0,
    relevance: float = 0.8,
    metadata=None,
) -> ContextParticle:
    return ContextParticle(
        id=particle_id,
        content=f"content {particle_id}",
        embedding=list(embedding or [1.0, 0.0, 0.0]),
        position=position or Vector(0.0, 0.0, 0.0),
        velocity=velocity or Vector(0.0, 0.0, 0.0),
        mass=mass,
        relevance_score=relevance,
        metadata=dict(metadata or {}),
    )


# --------------------------------------------------------------------------- #
# Vector utilities


def test_vector_operations():
    v1 = Vector(1, 2, 3)
    v2 = Vector(4, 5, 6)

    assert v1 + v2 == Vector(5, 7, 9)
    assert v2 - v1 == Vector(3, 3, 3)
    assert v1 * 2 == Vector(2, 4, 6)
    assert v2 / 2 == Vector(2, 2.5, 3)
    assert math.isclose(Vector(3, 4, 0).magnitude(), 5.0)
    normalized = Vector(3, 4, 0).normalize()
    assert math.isclose(normalized.magnitude(), 1.0, rel_tol=1e-3)
    assert Vector(2, 0, 0).dot(Vector(0, 3, 0)) == 0


# --------------------------------------------------------------------------- #
# Force unit tests


def test_gravity_attracts_toward_query():
    physics = DVNSPhysics(DVNSConfig(gravity_strength=1.0))
    particle = _make_particle("p1", embedding=[1.0, 0.0, 0.0], position=Vector(5, 0, 0))

    force = physics._compute_gravity(particle, [1.0, 0.0, 0.0], [particle])

    assert force.magnitude() > 0
    assert force.x < 0  # should pull toward origin


def test_gravity_attracts_related_particles():
    physics = DVNSPhysics(DVNSConfig(gravity_strength=1.0))
    p1 = _make_particle("p1", embedding=[1.0, 0.0, 0.0], position=Vector(0, 0, 0))
    p2 = _make_particle("p2", embedding=[0.8, 0.0, 0.0], position=Vector(1, 0, 0))

    force = physics._compute_gravity(p1, [1.0, 0.0, 0.0], [p1, p2])
    assert force.x > 0  # p1 pulled toward p2


def test_elastic_force_maintains_structure():
    physics = DVNSPhysics(DVNSConfig(elastic_strength=1.0, elastic_rest_length=1.0))
    p1 = _make_particle("p1", position=Vector(0, 0, 0), metadata={"source_doc": "doc"})
    p2 = _make_particle("p2", position=Vector(3, 0, 0), metadata={"source_doc": "doc"})

    force = physics._compute_elastic(p1, [p1, p2])
    assert force.magnitude() > 0
    assert force.x > 0  # pulls toward p2 to restore rest length


def test_repulse_separates_contradictions():
    physics = DVNSPhysics(DVNSConfig(repulse_strength=0.5))
    p1 = _make_particle("p1", embedding=[1.0, 0.0, 0.0], position=Vector(0, 0, 0))
    p2 = _make_particle("p2", embedding=[-1.0, 0.0, 0.0], position=Vector(1, 0, 0))

    force = physics._compute_repulse(p1, [p1, p2])
    assert force.magnitude() > 0
    assert force.x < 0  # pushes away from p2


def test_damping_opposes_velocity():
    physics = DVNSPhysics(DVNSConfig(damping_coefficient=0.5))
    particle = _make_particle("p1", velocity=Vector(2, 3, -1))

    damping = physics._compute_damping(particle)
    dot = damping.dot(particle.velocity)
    assert dot < 0


# --------------------------------------------------------------------------- #
# Simulation behaviour


def test_simulation_converges_on_simple_system():
    config = DVNSConfig(
        max_iterations=50,
        convergence_velocity_threshold=0.05,
        gravity_strength=0.4,
        damping_coefficient=0.4,
        max_velocity_magnitude=0.4,
    )
    physics = DVNSPhysics(config)
    particles = [
        _make_particle(f"p{i}", embedding=[float(i), 0.0, 0.0], position=Vector(float(i) * 2, 0, 0))
        for i in range(3)
    ]

    result = physics.optimize_layout(particles, [1.0, 0.0, 0.0])
    assert isinstance(result, SimulationResult)
    assert result.metrics.iterations <= 50
    assert result.metrics.max_velocity <= config.max_velocity_magnitude
    assert result.metrics.avg_displacement < 1.0


def test_positions_clamped_to_bounds():
    config = DVNSConfig(max_distance=2.0)
    physics = DVNSPhysics(config)
    particles = [
        _make_particle("p1", position=Vector(10, 10, 10)),
        _make_particle("p2", position=Vector(-10, -10, -10)),
    ]

    result = physics.optimize_layout(particles, [1.0, 0.0, 0.0], iterations=1)
    for particle in result.particles:
        assert max(abs(particle.position.x), abs(particle.position.y), abs(particle.position.z)) <= config.max_distance


def test_lost_in_middle_scenario():
    config = DVNSConfig(max_iterations=80)
    physics = DVNSPhysics(config)
    particles = [
        _make_particle("p_low_left", embedding=[0.1, 0.0, 0.0], position=Vector(0, 0, 0), mass=0.2, relevance=0.2),
        _make_particle("p_high", embedding=[1.0, 0.0, 0.0], position=Vector(1, 0, 0), mass=1.0, relevance=0.95),
        _make_particle("p_low_right", embedding=[0.1, 0.0, 0.0], position=Vector(2, 0, 0), mass=0.2, relevance=0.2),
    ]

    original_position = particles[1].position

    result = physics.optimize_layout(particles, [1.0, 0.0, 0.0])
    optimized_high = next(p for p in result.particles if p.id == "p_high")

    distance_moved = (optimized_high.position - original_position).magnitude()
    assert distance_moved > 0.1


# --------------------------------------------------------------------------- #
# Integration helpers


def _build_index() -> HierarchicalIndex:
    doc = """Test Document

Section A
Important concept about memory hierarchies.

Section B
Contradictory concept about the same topic.
"""
    index = HierarchicalIndex()
    index.index_document(doc, "doc")
    return index


def test_create_particles_from_search_results():
    index = _build_index()
    search = SemanticSearchEngine(index=index)
    results = search.search("memory concept", target_level=IndexLevel.PARAGRAPH, top_k=3)

    particles = create_particles_from_search(results, index, seed=123)
    assert particles
    assert len(particles) == len(results)
    assert all(p.mass > 0 for p in particles)

    particle_positions = {p.id: p.position for p in particles}
    particles_again = create_particles_from_search(results, index, seed=123)
    assert {p.id: p.position for p in particles_again} == particle_positions


def test_simulation_metrics():
    physics = DVNSPhysics()
    particles = [
        _make_particle("p1", embedding=[1, 0, 0], position=Vector(0, 0, 0)),
        _make_particle("p2", embedding=[0.8, 0.0, 0.0], position=Vector(1, 0, 0)),
    ]

    result = physics.optimize_layout(particles, [1.0, 0.0, 0.0])
    assert isinstance(result.metrics, SimulationMetrics)
    assert result.metrics.iterations >= 1
    assert result.metrics.max_velocity >= 0.0


def test_future_integration_with_budget_manager():
    pytest.skip("Integration test will be implemented after Task 2.2 pipeline wiring.")
