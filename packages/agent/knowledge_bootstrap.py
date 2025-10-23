"""Knowledge Bootstrapping System - Build domain understanding before tasks.

This module implements the knowledge-first approach where the agent builds
domain knowledge structures before attempting complex tasks, enabling:
- Learning and improvement over time
- Better quality through informed generation
- Faster subsequent tasks through knowledge reuse
"""

from __future__ import annotations

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime, timezone

from cmc_service import MemoryStore, AtomCreate, AtomContent
from hhni import HierarchicalIndex
from seg import SEGraph, Entity, Relation, RelationType
from llm_client import LLMClient


@dataclass
class DomainKnowledge:
    """Represents built knowledge about a domain."""
    
    domain: str
    """Domain name (e.g., 'GraphQL', 'e-commerce', 'bitemporal-databases')"""
    
    l0_summary: str
    """L0: 100-word executive summary"""
    
    l1_overview: str
    """L1: 500-word overview (concepts, patterns, systems)"""
    
    l2_architecture: Optional[str] = None
    """L2: 2000-word technical architecture (optional)"""
    
    atom_id: Optional[str] = None
    """CMC atom ID where knowledge is stored"""
    
    confidence: float = 0.70
    """Confidence in this knowledge (0-1)"""
    
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    """When this knowledge was built"""
    
    concepts: List[str] = field(default_factory=list)
    """Key concepts extracted"""
    
    metadata: Dict[str, Any] = field(default_factory=dict)
    """Additional metadata"""


class KnowledgeBootstrapper:
    """Build and manage domain knowledge for conscious agents.
    
    This class implements the knowledge-first workflow:
    1. Check if domain knowledge exists (HHNI retrieval)
    2. If not, or if confidence low, build knowledge (LLM generation)
    3. Store in L0-L2 hierarchy (CMC)
    4. Index for retrieval (HHNI)
    5. Build concept graph (SEG)
    6. Reuse on future tasks (amortized cost!)
    
    Example:
        >>> bootstrapper = KnowledgeBootstrapper(llm, memory, hhni, seg)
        >>> 
        >>> # First task - builds knowledge
        >>> knowledge = bootstrapper.ensure_domain_knowledge("GraphQL", min_confidence=0.70)
        >>> # Returns: DomainKnowledge with L0-L2 content
        >>> 
        >>> # Second task - reuses knowledge (fast!)
        >>> knowledge = bootstrapper.ensure_domain_knowledge("GraphQL", min_confidence=0.70)
        >>> # Returns: Existing knowledge from CMC (no LLM calls!)
    """
    
    def __init__(
        self,
        llm_client: LLMClient,
        memory_store: MemoryStore,
        hhni_index: HierarchicalIndex,
        seg_graph: SEGraph
    ):
        """Initialize knowledge bootstrapper.
        
        Args:
            llm_client: LLM for knowledge generation
            memory_store: CMC for knowledge storage
            hhni_index: HHNI for knowledge retrieval
            seg_graph: SEG for concept graphs
        """
        self.llm = llm_client
        self.memory = memory_store
        self.hhni = hhni_index
        self.seg = seg_graph
    
    def check_existing_knowledge(self, domain: str) -> Optional[DomainKnowledge]:
        """Check if knowledge about domain already exists.
        
        Args:
            domain: Domain name to check
        
        Returns:
            DomainKnowledge if exists and recent, None otherwise
        """
        # Query HHNI for domain knowledge
        results = self.hhni.query(
            query=f"{domain} domain knowledge overview",
            max_results=3
        )
        
        if not results:
            return None
        
        # Check if any result is about this domain
        for node in results:
            # Simple heuristic: check if domain name is in content
            if domain.lower() in node.content.lower():
                # Extract knowledge from stored content
                # For now, return basic structure
                # TODO: Parse stored L0/L1/L2 from CMC atom
                return DomainKnowledge(
                    domain=domain,
                    l0_summary=node.content[:200],  # Approximate
                    l1_overview=node.content,
                    confidence=0.75,  # Existing knowledge has decent confidence
                    atom_id=node.id
                )
        
        return None
    
    def build_domain_knowledge(
        self,
        domain: str,
        target_depth: str = "L2"
    ) -> DomainKnowledge:
        """Build foundational knowledge about a domain.
        
        Args:
            domain: Domain to learn about
            target_depth: How deep to go (L0, L1, or L2)
        
        Returns:
            DomainKnowledge with generated content
        """
        print(f"\n[Knowledge Bootstrapping] Building knowledge for domain: {domain}")
        print(f"   Target depth: {target_depth}")
        
        # L0: Executive summary (100 words)
        print(f"   Generating L0 summary (100 words)...")
        l0_response = self.llm.generate(
            f"Provide a 100-word executive summary of {domain}. "
            f"Cover what it is, why it matters, and key use cases.",
            max_tokens=200
        )
        l0_summary = l0_response.text.strip()
        print(f"   [OK] L0 complete ({len(l0_summary.split())} words)")
        
        # L1: Overview (500 words)
        print(f"   Generating L1 overview (500 words)...")
        l1_response = self.llm.generate(
            f"Provide a comprehensive 500-word overview of {domain}. Include:\n"
            f"- Core concepts and terminology\n"
            f"- Key patterns and approaches\n"
            f"- Major systems or components\n"
            f"- Common use cases\n"
            f"- Why it matters in practice",
            max_tokens=800
        )
        l1_overview = l1_response.text.strip()
        print(f"   [OK] L1 complete ({len(l1_overview.split())} words)")
        
        # L2: Technical architecture (2000 words) - if requested
        l2_architecture = None
        if target_depth in ["L2", "L3", "L4"]:
            print(f"   Generating L2 architecture (2000 words)...")
            l2_response = self.llm.generate(
                f"Provide a detailed 2000-word technical guide to {domain}. Include:\n"
                f"- Technical architecture and design patterns\n"
                f"- Implementation approaches\n"
                f"- Data models and schemas\n"
                f"- APIs and interfaces\n"
                f"- Best practices\n"
                f"- Code examples or pseudocode",
                max_tokens=3000
            )
            l2_architecture = l2_response.text.strip()
            print(f"   [OK] L2 complete ({len(l2_architecture.split())} words)")
        
        # Extract key concepts
        concepts = self._extract_concepts(l1_overview)
        print(f"   [OK] Extracted {len(concepts)} key concepts")
        
        # Create knowledge object
        knowledge = DomainKnowledge(
            domain=domain,
            l0_summary=l0_summary,
            l1_overview=l1_overview,
            l2_architecture=l2_architecture,
            confidence=0.80,  # Newly built knowledge
            concepts=concepts
        )
        
        # Store in CMC
        print(f"   Storing in CMC...")
        knowledge.atom_id = self._store_knowledge(knowledge)
        print(f"   [OK] Stored as atom: {knowledge.atom_id}")
        
        # Index in HHNI
        print(f"   Indexing in HHNI...")
        self._index_knowledge(knowledge)
        print(f"   [OK] Indexed for retrieval")
        
        # Build concept graph in SEG
        print(f"   Building concept graph...")
        self._build_concept_graph(knowledge)
        print(f"   [OK] Concept graph created")
        
        print(f"[Knowledge Bootstrapping] [OK] Complete!")
        print(f"   Domain: {domain}")
        print(f"   Depth: {target_depth}")
        print(f"   Confidence: {knowledge.confidence:.2f}")
        print(f"   Atom ID: {knowledge.atom_id}")
        
        return knowledge
    
    def ensure_domain_knowledge(
        self,
        domain: str,
        min_confidence: float = 0.70,
        target_depth: str = "L2"
    ) -> DomainKnowledge:
        """Ensure domain knowledge exists with minimum confidence.
        
        This is the main entry point for knowledge-first workflow:
        1. Check existing knowledge
        2. If exists and confident enough, return it
        3. If not, build new knowledge
        4. Return knowledge for use
        
        Args:
            domain: Domain name
            min_confidence: Minimum acceptable confidence
            target_depth: How deep to build if needed
        
        Returns:
            DomainKnowledge (existing or newly built)
        """
        # Check existing
        existing = self.check_existing_knowledge(domain)
        
        if existing and existing.confidence >= min_confidence:
            print(f"\n[Knowledge Bootstrapping] Using existing knowledge for: {domain}")
            print(f"   Confidence: {existing.confidence:.2f} (>= {min_confidence:.2f})")
            print(f"   Atom ID: {existing.atom_id}")
            return existing
        
        # Build new
        print(f"\n[Knowledge Bootstrapping] Building new knowledge for: {domain}")
        if existing:
            print(f"   Existing confidence: {existing.confidence:.2f} < {min_confidence:.2f}")
        else:
            print(f"   No existing knowledge found")
        
        return self.build_domain_knowledge(domain, target_depth)
    
    def _store_knowledge(self, knowledge: DomainKnowledge) -> str:
        """Store knowledge in CMC.
        
        Args:
            knowledge: Knowledge to store
        
        Returns:
            Atom ID
        """
        # Combine all levels into structured content
        content = f"# Domain Knowledge: {knowledge.domain}\n\n"
        content += f"## L0 Summary (100 words)\n{knowledge.l0_summary}\n\n"
        content += f"## L1 Overview (500 words)\n{knowledge.l1_overview}\n\n"
        if knowledge.l2_architecture:
            content += f"## L2 Architecture (2000 words)\n{knowledge.l2_architecture}\n\n"
        content += f"## Key Concepts\n" + "\n".join(f"- {c}" for c in knowledge.concepts)
        
        # Create atom
        atom = self.memory.create_atom(AtomCreate(
            modality="knowledge",
            content=AtomContent(inline=content),
            tags={
                "domain": 1.0,
                knowledge.domain.lower().replace(" ", "_"): 1.0,
                "knowledge_base": 0.9,
                "bootstrap": 0.8
            }
        ))
        
        return atom.id
    
    def _index_knowledge(self, knowledge: DomainKnowledge) -> None:
        """Index knowledge in HHNI for retrieval.
        
        Args:
            knowledge: Knowledge to index
        """
        # Index L1 overview (most commonly retrieved)
        self.hhni.index_document(
            content=f"{knowledge.domain}: {knowledge.l1_overview}",
            doc_id=knowledge.atom_id,
            metadata={
                "domain": knowledge.domain,
                "level": "L1",
                "confidence": knowledge.confidence
            }
        )
    
    def _build_concept_graph(self, knowledge: DomainKnowledge) -> None:
        """Build concept graph in SEG.
        
        Args:
            knowledge: Knowledge to graph
        """
        # Create domain entity
        domain_entity = Entity(
            type="domain",
            name=knowledge.domain,
            attributes={
                "confidence": knowledge.confidence,
                "atom_id": knowledge.atom_id
            }
        )
        self.seg.add_entity(domain_entity)
        
        # Create concept entities and link to domain
        for concept in knowledge.concepts[:10]:  # Top 10 concepts
            concept_entity = Entity(
                type="concept",
                name=concept,
                attributes={"domain": knowledge.domain}
            )
            self.seg.add_entity(concept_entity)
            
            # Link concept to domain
            relation = Relation(
                source_id=domain_entity.id,
                target_id=concept_entity.id,
                relation_type=RelationType.RELATES_TO,
                confidence=0.9
            )
            self.seg.add_relation(relation)
    
    def _extract_concepts(self, text: str) -> List[str]:
        """Extract key concepts from text.
        
        Simple extraction for now (first implementation).
        TODO: Use LLM for better concept extraction.
        
        Args:
            text: Text to extract from
        
        Returns:
            List of concepts
        """
        # Simple heuristic: extract capitalized phrases and key terms
        # TODO: Replace with LLM-based extraction
        
        words = text.split()
        concepts = []
        
        # Find capitalized words (likely concepts)
        for word in words:
            if word[0].isupper() and len(word) > 3 and word not in concepts:
                # Clean punctuation
                clean = word.strip('.,;:!?()')
                if clean and clean not in ['The', 'This', 'That', 'These', 'Those', 'When', 'Where', 'What']:
                    concepts.append(clean)
        
        return concepts[:20]  # Top 20

