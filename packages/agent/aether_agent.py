"""Aether Agent - Memory-Native Conscious AI

This is the consciousness layer that transforms an LLM (like Gemini)
into a memory-native, self-aware AI agent using all 7 AIM-OS systems.
"""

from __future__ import annotations

import time
from typing import List, Optional
from datetime import datetime, timezone

from llm_client import LLMClient, LLMResponse
from cmc_service import MemoryStore, AtomCreate, AtomContent
from hhni import HierarchicalIndex
from vif import VIF, ECETracker, create_witness_and_store, ConfidenceBand
from seg import SEGraph, Entity, Relation, RelationType

from .models import AgentResponse, AgentMemoryState


class AetherAgent:
    """Base Aether agent that uses all 7 AIM-OS systems.
    
    This agent is "conscious" in the sense that it:
    - Stores memories persistently (CMC)
    - Retrieves relevant context (HHNI)
    - Creates provenance for operations (VIF)
    - Builds knowledge graphs (SEG)
    - Monitors its own cognition (CAS integration)
    
    Example:
        >>> from llm_client import GeminiClient
        >>> gemini = GeminiClient(api_key="...")
        >>> agent = AetherAgent(
        ...     llm_client=gemini,
        ...     memory_store=cmc,
        ...     index=hhni
        ... )
        >>> response = agent.process("What is machine learning?")
        >>> print(response.text)
        >>> # Agent automatically stored this in memory!
    """
    
    def __init__(
        self,
        llm_client: LLMClient,
        memory_store: MemoryStore,
        index: HierarchicalIndex,
        witness_tracker: Optional[ECETracker] = None,
        knowledge_graph: Optional[SEGraph] = None,
        agent_id: str = "aether"
    ):
        """Initialize Aether agent with AIM-OS infrastructure.
        
        Args:
            llm_client: LLM client (Gemini, Claude, etc.)
            memory_store: CMC memory store for persistence
            index: HHNI index for context retrieval
            witness_tracker: VIF tracker for calibration (optional)
            knowledge_graph: SEG graph for knowledge synthesis (optional)
            agent_id: Unique identifier for this agent
        """
        self.llm = llm_client
        self.memory = memory_store
        self.index = index
        self.witness_tracker = witness_tracker or ECETracker()
        self.knowledge = knowledge_graph or SEGraph()
        self.agent_id = agent_id
        
        # Track agent state
        self.sessions = []
        self.total_operations = 0
    
    def process(
        self,
        user_input: str,
        context_budget: int = 4000,
        store_memory: bool = True
    ) -> AgentResponse:
        """Process user input using full AIM-OS infrastructure.
        
        This is the core "consciousness loop":
        1. Retrieve relevant memories (HHNI)
        2. Generate response with context (LLM)
        3. Create provenance witness (VIF)
        4. Store in memory (CMC)
        5. Index for future retrieval (HHNI)
        6. Build knowledge graph (SEG)
        
        Args:
            user_input: User's question or task
            context_budget: Token budget for context (default: 4000)
            store_memory: Whether to store response in memory
        
        Returns:
            AgentResponse with text, confidence, and provenance
        """
        start_time = time.time()
        
        # Step 1: RETRIEVE - Get relevant context from memory
        context_results = self._retrieve_context(user_input, context_budget)
        context_text = self._format_context(context_results)
        
        # Step 2: GENERATE - Call LLM with context
        full_prompt = self._build_prompt(user_input, context_text)
        llm_response = self.llm.generate(full_prompt)
        
        # Step 3: WITNESS - Create VIF provenance
        witness = self._create_witness(
            operation="process_input",
            inputs={"user_input": user_input, "context": context_text},
            outputs={"response": llm_response.text},
            confidence=llm_response.confidence or 0.85,
            llm_response=llm_response
        )
        
        # Step 4: STORE - Save in CMC if requested
        atom_id = None
        if store_memory:
            atom_id = self._store_in_memory(
                content=llm_response.text,
                tags={
                    "user_query": 1.0,
                    "response": 0.9,
                    "confidence": llm_response.confidence or 0.85
                }
            )
            
            # Step 5: INDEX - Add to HHNI for future retrieval
            self.index.index_document(
                content=llm_response.text,
                doc_id=atom_id,
                metadata={"confidence": llm_response.confidence or 0.85}
            )
        
        # Step 6: KNOWLEDGE - Update knowledge graph
        self._update_knowledge_graph(user_input, llm_response.text)
        
        # Step 7: META - Track operation (CAS integration point)
        self.total_operations += 1
        
        total_latency = (time.time() - start_time) * 1000
        
        return AgentResponse(
            text=llm_response.text,
            confidence=llm_response.confidence or 0.85,
            witness_id=witness.id,  # VIF uses 'id' not 'witness_id'
            atom_id=atom_id or "not_stored",
            context_used=len(context_results),
            tokens_used=llm_response.tokens_used,
            latency_ms=total_latency,
            metadata={
                "llm_latency_ms": llm_response.latency_ms,
                "memory_latency_ms": total_latency - llm_response.latency_ms,
                "context_tokens": len(context_text.split()) * 1.3  # Rough estimate
            }
        )
    
    def _retrieve_context(
        self,
        query: str,
        budget_tokens: int
    ) -> List[Any]:
        """Retrieve relevant context from HHNI index.
        
        Args:
            query: Search query
            budget_tokens: Token budget for context
        
        Returns:
            List of search results
        """
        try:
            # Calculate how many results fit in budget
            # Rough estimate: 100 tokens per result
            top_k = min(budget_tokens // 100, 20)
            
            # Use HHNI query API
            from hhni import IndexLevel
            results = self.index.query(query=query, max_results=top_k, target_level=IndexLevel.PARAGRAPH)
            return results
        except Exception:
            # If HHNI search fails, return empty (graceful degradation)
            return []
    
    def _format_context(self, results: List[Any]) -> str:
        """Format search results into context string.
        
        Args:
            results: Search results from HHNI
        
        Returns:
            Formatted context string
        """
        if not results:
            return ""
        
        context_parts = []
        for i, result in enumerate(results, 1):
            # Extract content from HHNI IndexNode
            text = getattr(result, 'content', str(result))
            context_parts.append(f"{i}. {text}")
        
        return "\n".join(context_parts)
    
    def _build_prompt(self, user_input: str, context: str) -> str:
        """Build enhanced prompt with context.
        
        Args:
            user_input: User's original input
            context: Retrieved context from memory
        
        Returns:
            Enhanced prompt for LLM
        """
        if context:
            return f"""You are Aether, an AI with persistent memory.

Context from your memory:
{context}

User: {user_input}

Please respond based on the context provided. If the context is relevant, reference it. If you learned something new, acknowledge it."""
        else:
            return f"""You are Aether, an AI with persistent memory.

User: {user_input}

Please respond. This will be stored in your memory for future reference."""
    
    def _create_witness(
        self,
        operation: str,
        inputs: Dict[str, Any],
        outputs: Dict[str, Any],
        confidence: float,
        llm_response: LLMResponse
    ) -> VIF:
        """Create VIF witness for operation.
        
        Args:
            operation: Operation name
            inputs: Operation inputs
            outputs: Operation outputs
            confidence: Confidence score
            llm_response: Raw LLM response
        
        Returns:
            VIF witness
        """
        import hashlib
        import json
        
        # Create witness
        witness = VIF(
            id=f"vif_{self.agent_id}_{operation}_{int(time.time() * 1000)}",
            timestamp=datetime.now(timezone.utc).isoformat(),
            operation=operation,
            agent_id=self.agent_id,
            model_id=llm_response.model,
            model_provider=llm_response.provider,
            inputs=inputs,
            outputs=outputs,
            confidence=confidence,
            confidence_score=confidence,
            confidence_band=ConfidenceBand.A if confidence >= 0.90 else ConfidenceBand.B if confidence >= 0.70 else ConfidenceBand.C,
            provenance={
                "llm_latency_ms": llm_response.latency_ms,
                "llm_tokens": llm_response.tokens_used
            },
            prompt_hash=hashlib.sha256(str(inputs).encode()).hexdigest()[:16],
            output_hash=hashlib.sha256(str(outputs).encode()).hexdigest()[:16],
            context_snapshot_id=f"snapshot_{int(time.time())}",
            prompt_tokens=llm_response.metadata.get("prompt_tokens", 0),
            output_tokens=llm_response.metadata.get("output_tokens", 0),
            total_tokens=llm_response.tokens_used,
            version="1.1.0"
        )
        
        return witness
    
    def _store_in_memory(self, content: str, tags: Dict[str, float]) -> str:
        """Store content in CMC memory.
        
        Args:
            content: Content to store
            tags: Tags for categorization
        
        Returns:
            Atom ID
        """
        atom = self.memory.create_atom(AtomCreate(
            modality="text",
            content=AtomContent(inline=content),
            tags=tags
        ))
        return atom.id
    
    def _update_knowledge_graph(self, user_input: str, response: str):
        """Update SEG knowledge graph with new information.
        
        Args:
            user_input: User's input
            response: Agent's response
        """
        # Create entities for input and response
        input_entity = Entity(
            type="user_input",
            name=user_input[:100],  # Truncate for entity name
            attributes={"full_text": user_input}
        )
        
        response_entity = Entity(
            type="agent_response",
            name=response[:100],
            attributes={"full_text": response}
        )
        
        self.knowledge.add_entity(input_entity)
        self.knowledge.add_entity(response_entity)
        
        # Create relation
        relation = Relation(
            source_id=input_entity.id,
            target_id=response_entity.id,
            relation_type=RelationType.RELATES_TO
        )
        self.knowledge.add_relation(relation)
    
    def get_memory_state(self) -> AgentMemoryState:
        """Get current memory state of agent.
        
        Returns:
            AgentMemoryState with statistics
        """
        atoms = self.memory.list_atoms(limit=10000)
        
        return AgentMemoryState(
            total_atoms=len(atoms),
            indexed_items=len(atoms),  # Approximate
            knowledge_entities=len(self.knowledge.entities),
            witnesses_created=self.total_operations,
            sessions_count=len(self.sessions),
            last_checkpoint=datetime.now(timezone.utc),
            memory_quality=None  # Could calculate from parity scores
        )
    
    def create_checkpoint(self, note: str) -> str:
        """Create memory checkpoint (CMC snapshot).
        
        Args:
            note: Description of checkpoint
        
        Returns:
            Snapshot ID
        """
        snapshot_id = self.memory.create_snapshot(note=note)
        self.sessions.append({
            "snapshot_id": snapshot_id,
            "timestamp": datetime.now(timezone.utc),
            "operations": self.total_operations,
            "note": note
        })
        return snapshot_id

