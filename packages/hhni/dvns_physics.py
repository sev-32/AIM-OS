"""DVNS Physics - Dynamic Vector Navigation System.

Implements physics-guided context optimization using four forces:
1. Gravity  - attracts related concepts toward the query and one another
2. Elastic  - maintains structural coherence between hierarchically related items
3. Repulse  - separates contradictory or competing concepts
4. Damping  - stabilizes the system by counteracting velocity

Purpose: solve "lost in the middle" by optimizing context layout in a low-dimensional
embedding space BEFORE feeding it to the LLM, ensuring the most relevant content is
positioned for selection by the token budget manager.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

from .hierarchical_index import HierarchicalIndex, IndexNode
from .semantic_search import SearchResult


# --------------------------------------------------------------------------- #
# Vector utilities


@dataclass(frozen=True)
class Vector:
    """Simple 3D vector for positions and velocities."""

    x: float
    y: float
    z: float

    def __add__(self, other: "Vector") -> "Vector":
        return Vector(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other: "Vector") -> "Vector":
        return Vector(self.x - other.x, self.y - other.y, self.z - other.z)

    def __mul__(self, scalar: float) -> "Vector":
        return Vector(self.x * scalar, self.y * scalar, self.z * scalar)

    def __truediv__(self, scalar: float) -> "Vector":
        if scalar == 0:
            raise ZeroDivisionError("Cannot divide by zero scalar")
        return Vector(self.x / scalar, self.y / scalar, self.z / scalar)

    def dot(self, other: "Vector") -> float:
        return self.x * other.x + self.y * other.y + self.z * other.z

    def magnitude(self) -> float:
        return math.sqrt(self.x * self.x + self.y * self.y + self.z * self.z)

    def normalize(self) -> "Vector":
        mag = self.magnitude()
        if mag > 0:
            return self * (1.0 / mag)
        return Vector(0.0, 0.0, 0.0)

    def clamp(self, max_length: float) -> "Vector":
        mag = self.magnitude()
        if mag <= max_length or max_length <= 0:
            return self
        return self.normalize() * max_length

    @staticmethod
    def from_iterable(values: Sequence[float]) -> "Vector":
        x = values[0] if len(values) > 0 else 0.0
        y = values[1] if len(values) > 1 else 0.0
        z = values[2] if len(values) > 2 else 0.0
        return Vector(float(x), float(y), float(z))


# --------------------------------------------------------------------------- #
# Simulation structures


@dataclass
class ContextParticle:
    """Particle in the DVNS simulation representing a context item."""

    id: str
    content: str
    embedding: List[float]
    position: Vector
    velocity: Vector
    mass: float
    relevance_score: float
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DVNSConfig:
    """Configuration controlling DVNS physics behaviour."""

    gravity_strength: float = 1.0
    pairwise_gravity_similarity_threshold: float = 0.7
    elastic_strength: float = 0.5
    elastic_rest_length: float = 1.0
    repulse_strength: float = 0.3
    repulse_softening: float = 0.1
    damping_coefficient: float = 0.2

    time_step: float = 0.1
    max_iterations: int = 100
    convergence_velocity_threshold: float = 0.01
    convergence_displacement_threshold: float = 0.005

    min_distance: float = 0.05
    max_distance: float = 10.0
    max_velocity_magnitude: float = 5.0

    random_seed: Optional[int] = 42


@dataclass
class SimulationMetrics:
    """Diagnostics emitted alongside optimized particles."""

    iterations: int
    max_velocity: float
    avg_velocity: float
    avg_displacement: float


@dataclass
class SimulationResult:
    particles: List[ContextParticle]
    metrics: SimulationMetrics


# --------------------------------------------------------------------------- #
# DVNS Physics Engine


class DVNSPhysics:
    """Dynamic Vector Navigation System - physics engine solving lost-in-middle."""

    def __init__(self, config: Optional[DVNSConfig] = None) -> None:
        self.config = config or DVNSConfig()
        if self.config.random_seed is not None:
            random.seed(self.config.random_seed)

    # Public API ------------------------------------------------------------ #
    def optimize_layout(
        self,
        particles: List[ContextParticle],
        query_embedding: List[float],
        iterations: Optional[int] = None,
    ) -> SimulationResult:
        """Run the DVNS simulation and return optimized particles and metrics."""
        if not particles:
            raise ValueError("particles must be a non-empty list")
        if not query_embedding:
            raise ValueError("query_embedding must be provided")

        max_iter = min(iterations or self.config.max_iterations, self.config.max_iterations)
        previous_positions = [particle.position for particle in particles]

        metrics = SimulationMetrics(iterations=0, max_velocity=0.0, avg_velocity=0.0, avg_displacement=0.0)

        for iteration in range(1, max_iter + 1):
            forces = self._compute_forces(particles, query_embedding)
            particles = self._integrate_step(particles, forces)

            max_velocity = max(p.velocity.magnitude() for p in particles)
            avg_velocity = sum(p.velocity.magnitude() for p in particles) / len(particles)
            avg_displacement = sum(
                (p.position - previous_positions[idx]).magnitude() for idx, p in enumerate(particles)
            ) / len(particles)

            metrics = SimulationMetrics(
                iterations=iteration,
                max_velocity=max_velocity,
                avg_velocity=avg_velocity,
                avg_displacement=avg_displacement,
            )

            previous_positions = [p.position for p in particles]

            if self._has_converged(max_velocity, avg_displacement):
                break

        return SimulationResult(particles=particles, metrics=metrics)

    # Force computations ---------------------------------------------------- #
    def _compute_forces(
        self,
        particles: Sequence[ContextParticle],
        query_embedding: List[float],
    ) -> Dict[str, Vector]:
        forces: Dict[str, Vector] = {particle.id: Vector(0.0, 0.0, 0.0) for particle in particles}
        for particle in particles:
            gravity = self._compute_gravity(particle, query_embedding, particles)
            elastic = self._compute_elastic(particle, particles)
            repulse = self._compute_repulse(particle, particles)
            damping = self._compute_damping(particle)

            net_force = gravity + elastic + repulse + damping
            forces[particle.id] = net_force
        return forces

    def _compute_gravity(
        self,
        particle: ContextParticle,
        query_embedding: List[float],
        particles: Sequence[ContextParticle],
    ) -> Vector:
        G = self.config.gravity_strength
        net_force = Vector(0.0, 0.0, 0.0)

        query_similarity = self._cosine_similarity(particle.embedding, query_embedding)
        if query_similarity > 0:
            query_position = self._embedding_to_position(query_embedding)
            displacement = query_position - particle.position
            distance = max(displacement.magnitude(), self.config.min_distance)
            direction = displacement.normalize()
            magnitude = G * particle.mass * query_similarity / (distance * distance)
            net_force = net_force + (direction * magnitude)

        for other in particles:
            if other.id == particle.id:
                continue
            similarity = self._cosine_similarity(particle.embedding, other.embedding)
            if similarity < self.config.pairwise_gravity_similarity_threshold:
                continue
            displacement = other.position - particle.position
            distance = max(displacement.magnitude(), self.config.min_distance)
            direction = displacement.normalize()
            magnitude = G * particle.mass * similarity / (distance * distance)
            net_force = net_force + (direction * magnitude)

        return net_force

    def _compute_elastic(self, particle: ContextParticle, particles: Sequence[ContextParticle]) -> Vector:
        k = self.config.elastic_strength
        rest_length = self.config.elastic_rest_length
        neighbors = self._find_structural_neighbors(particle, particles)

        total_force = Vector(0.0, 0.0, 0.0)
        for neighbor in neighbors:
            displacement = particle.position - neighbor.position
            distance = displacement.magnitude()
            if distance == 0:
                continue
            direction = displacement.normalize()
            magnitude = -k * (distance - rest_length)
            total_force = total_force + (direction * magnitude)
        return total_force

    def _compute_repulse(self, particle: ContextParticle, particles: Sequence[ContextParticle]) -> Vector:
        strength = self.config.repulse_strength
        epsilon = self.config.repulse_softening
        total_force = Vector(0.0, 0.0, 0.0)

        conflicts = set(particle.metadata.get("conflict_with") or [])

        for other in particles:
            if other.id == particle.id:
                continue

            similarity = self._cosine_similarity(particle.embedding, other.embedding)
            explicit_conflict = other.id in conflicts
            if similarity >= -0.3 and not explicit_conflict:
                continue

            displacement = particle.position - other.position
            distance = displacement.magnitude()
            if distance == 0:
                displacement = Vector(random.uniform(-0.01, 0.01), random.uniform(-0.01, 0.01), random.uniform(-0.01, 0.01))
                distance = displacement.magnitude()

            direction = displacement.normalize()
            magnitude = strength / ((distance * distance) + epsilon)
            total_force = total_force + (direction * magnitude)

        return total_force

    def _compute_damping(self, particle: ContextParticle) -> Vector:
        c = self.config.damping_coefficient
        return particle.velocity * (-c)

    # Integration ----------------------------------------------------------- #
    def _integrate_step(
        self,
        particles: Sequence[ContextParticle],
        forces: Dict[str, Vector],
    ) -> List[ContextParticle]:
        dt = self.config.time_step
        updated: List[ContextParticle] = []

        for particle in particles:
            force = forces.get(particle.id, Vector(0.0, 0.0, 0.0))
            if particle.mass <= 0:
                acceleration = Vector(0.0, 0.0, 0.0)
            else:
                acceleration = force * (1.0 / particle.mass)

            new_velocity = particle.velocity + (acceleration * dt)
            if self.config.max_velocity_magnitude > 0:
                new_velocity = new_velocity.clamp(self.config.max_velocity_magnitude)
            new_position = particle.position + (particle.velocity * dt) + (acceleration * (0.5 * dt * dt))
            new_position = self._constrain_position(new_position)

            updated.append(
                ContextParticle(
                    id=particle.id,
                    content=particle.content,
                    embedding=particle.embedding,
                    position=new_position,
                    velocity=new_velocity,
                    mass=particle.mass,
                    relevance_score=particle.relevance_score,
                    metadata=particle.metadata,
                )
            )

        return updated

    # Helpers --------------------------------------------------------------- #
    def _has_converged(self, max_velocity: float, avg_displacement: float) -> bool:
        return (
            max_velocity < self.config.convergence_velocity_threshold
            and avg_displacement < self.config.convergence_displacement_threshold
        )

    def _embedding_to_position(self, embedding: Sequence[float]) -> Vector:
        return Vector.from_iterable(embedding)

    def _find_structural_neighbors(
        self,
        particle: ContextParticle,
        particles: Sequence[ContextParticle],
    ) -> List[ContextParticle]:
        source_doc = particle.metadata.get("source_doc")
        section = particle.metadata.get("section_id")
        paragraph = particle.metadata.get("paragraph_id")

        neighbors: List[ContextParticle] = []
        for other in particles:
            if other.id == particle.id:
                continue
            if source_doc and other.metadata.get("source_doc") == source_doc:
                neighbors.append(other)
                continue
            if section and other.metadata.get("section_id") == section:
                neighbors.append(other)
                continue
            if paragraph and other.metadata.get("paragraph_id") == paragraph:
                neighbors.append(other)

        if not neighbors:
            best_candidates = sorted(
                (candidate for candidate in particles if candidate.id != particle.id),
                key=lambda candidate: self._cosine_similarity(particle.embedding, candidate.embedding),
                reverse=True,
            )
            neighbors = best_candidates[:2]
        return neighbors

    def _constrain_position(self, position: Vector) -> Vector:
        max_distance = self.config.max_distance
        return Vector(
            x=max(-max_distance, min(max_distance, position.x)),
            y=max(-max_distance, min(max_distance, position.y)),
            z=max(-max_distance, min(max_distance, position.z)),
        )

    @staticmethod
    def _cosine_similarity(vec_a: Sequence[float], vec_b: Sequence[float]) -> float:
        if not vec_a or not vec_b:
            return 0.0
        if len(vec_a) != len(vec_b):
            min_len = min(len(vec_a), len(vec_b))
            vec_a = vec_a[:min_len]
            vec_b = vec_b[:min_len]

        dot = sum(a * b for a, b in zip(vec_a, vec_b))
        norm_a = math.sqrt(sum(a * a for a in vec_a))
        norm_b = math.sqrt(sum(b * b for b in vec_b))
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return dot / (norm_a * norm_b)


# --------------------------------------------------------------------------- #
# Integration helpers


def create_particles_from_search(
    search_results: Iterable[SearchResult],
    index: HierarchicalIndex,
    *,
    seed: Optional[int] = 42,
) -> List[ContextParticle]:
    """Convert semantic search results into DVNS particles."""
    if seed is not None:
        random.seed(seed)

    particles: List[ContextParticle] = []
    for result in search_results:
        node: Optional[IndexNode] = index.nodes.get(result.node.id) if hasattr(result, "node") else None
        if node is None or not (node.embeddings or node.summary):
            continue
        embedding = node.embeddings if node.embeddings else [0.0, 0.0, 0.0]
        mass = max(result.score, 0.1)

        position = Vector(
            random.uniform(-5.0, 5.0),
            random.uniform(-5.0, 5.0),
            random.uniform(-5.0, 5.0),
        )

        particles.append(
            ContextParticle(
                id=node.id,
                content=node.content,
                embedding=embedding,
                position=position,
                velocity=Vector(0.0, 0.0, 0.0),
                mass=mass,
                relevance_score=result.score,
                metadata=dict(node.metadata),
            )
        )
    return particles


__all__ = [
    "Vector",
    "ContextParticle",
    "DVNSConfig",
    "SimulationMetrics",
    "SimulationResult",
    "DVNSPhysics",
    "create_particles_from_search",
]
