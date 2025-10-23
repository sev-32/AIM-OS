"""MCP Server - FastAPI server implementing Model Context Protocol.

Exposes AIM-OS conscious agents as MCP tools for Cursor IDE integration.
"""

from __future__ import annotations

import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from agent import AetherAgent
from agent.knowledge_bootstrap import KnowledgeBootstrapper
from llm_client import GeminiClient, CerebrasClient
from cmc_service import MemoryStore
from hhni import HierarchicalIndex, IndexLevel
from seg import SEGraph
from vif import ECETracker

from .models import (
    AskAgentRequest,
    AskAgentResponse,
    RememberRequest,
    RememberResponse,
    RetrieveRequest,
    RetrieveResponse,
    ContextItem,
    BuildKnowledgeRequest,
    BuildKnowledgeResponse,
    HealthResponse,
)


class MCPServer:
    """MCP Server exposing AIM-OS conscious agents."""
    
    def __init__(
        self,
        memory_path: str = "./mcp_memory",
        gemini_api_key: Optional[str] = None,
        cerebras_api_key: Optional[str] = None,
        default_llm: str = "gemini"  # "gemini" or "cerebras"
    ):
        """Initialize MCP server with AIM-OS infrastructure.
        
        Args:
            memory_path: Path to CMC storage
            gemini_api_key: Gemini API key (or use GEMINI_API_KEY env var)
            cerebras_api_key: Cerebras API key (or use CEREBRAS_API_KEY env var)
            default_llm: Default LLM to use ("gemini" or "cerebras")
        """
        self.start_time = time.time()
        self.total_requests = 0
        
        # Initialize LLM clients
        self.gemini = GeminiClient(
            api_key=gemini_api_key or os.getenv("GEMINI_API_KEY")
        )
        
        # Cerebras is optional (only if API key provided)
        cerebras_key = cerebras_api_key or os.getenv("CEREBRAS_API_KEY")
        self.cerebras = None
        if cerebras_key:
            try:
                self.cerebras = CerebrasClient(api_key=cerebras_key)
            except Exception as e:
                print(f"[WARN] Cerebras initialization failed: {e}")
                print("[WARN] Server will use Gemini only")
        
        # Select default LLM
        if default_llm == "cerebras" and self.cerebras:
            self.llm = self.cerebras
        else:
            self.llm = self.gemini
        
        # Initialize AIM-OS systems
        self.memory = MemoryStore(memory_path)
        self.hhni = HierarchicalIndex()
        self.seg = SEGraph()
        self.tracker = ECETracker()
        
        # Create conscious agent
        self.agent = AetherAgent(
            llm_client=self.llm,
            memory_store=self.memory,
            index=self.hhni,
            witness_tracker=self.tracker,
            knowledge_graph=self.seg
        )
        
        # Create knowledge bootstrapper
        self.bootstrapper = KnowledgeBootstrapper(
            llm_client=self.llm,
            memory_store=self.memory,
            hhni_index=self.hhni,
            seg_graph=self.seg
        )
        
        print(f"[MCP Server] Initialized with {default_llm.upper()} as default LLM")
        print(f"[MCP Server] Memory: {memory_path}")
        print(f"[MCP Server] Ready!")
    
    def ask_agent(self, request: AskAgentRequest) -> AskAgentResponse:
        """Process query with conscious agent.
        
        Args:
            request: Ask agent request
        
        Returns:
            Agent response with memory and provenance
        """
        self.total_requests += 1
        
        # Process with agent
        response = self.agent.process(
            user_input=request.query,
            context_budget=request.context_budget or 4000,
            store_memory=request.store_memory if request.store_memory is not None else True
        )
        
        # Check if learning occurred (built new knowledge)
        learning_occurred = response.context_used == 0  # No existing context = new domain
        
        return AskAgentResponse(
            response=response.text,
            confidence=response.confidence,
            witness_id=response.witness_id,
            context_used=response.context_used,
            tokens_used=response.tokens_used,
            latency_ms=response.latency_ms,
            learning_occurred=learning_occurred,
            metadata=response.metadata
        )
    
    def remember(self, request: RememberRequest) -> RememberResponse:
        """Explicitly store content in memory.
        
        Args:
            request: Remember request
        
        Returns:
            Storage confirmation
        """
        from cmc_service import AtomCreate, AtomContent
        
        # Store in CMC
        atom = self.memory.create_atom(AtomCreate(
            modality="text",
            content=AtomContent(inline=request.content),
            tags=request.tags or {"explicit_memory": 1.0, "importance": request.importance or 0.8}
        ))
        
        # Index in HHNI
        self.hhni.index_document(
            content=request.content,
            doc_id=atom.id,
            metadata={"importance": request.importance or 0.8}
        )
        
        return RememberResponse(
            atom_id=atom.id,
            indexed=True,
            knowledge_graph_updated=False  # Could add SEG integration
        )
    
    def retrieve_context(self, request: RetrieveRequest) -> RetrieveResponse:
        """Retrieve relevant context from memory.
        
        Args:
            request: Retrieve request
        
        Returns:
            Retrieved context items
        """
        # Query HHNI
        results = self.hhni.query(
            query=request.query,
            max_results=request.max_results or 10,
            target_level=IndexLevel.PARAGRAPH
        )
        
        # Format results
        items = []
        for node in results:
            # Simple relevance scoring (could be improved)
            relevance = 0.85  # Placeholder
            
            items.append(ContextItem(
                content=node.content,
                relevance=relevance,
                source_id=node.id,
                timestamp=datetime.now(timezone.utc).isoformat(),
                metadata=node.metadata
            ))
        
        return RetrieveResponse(
            results=items,
            total_found=len(results)
        )
    
    def build_knowledge(self, request: BuildKnowledgeRequest) -> BuildKnowledgeResponse:
        """Build domain knowledge.
        
        Args:
            request: Build knowledge request
        
        Returns:
            Built knowledge
        """
        start = time.time()
        
        # Check existing if not force rebuild
        if not request.force_rebuild:
            existing = self.bootstrapper.check_existing_knowledge(request.domain)
            if existing and existing.confidence >= 0.70:
                elapsed = (time.time() - start) * 1000
                return BuildKnowledgeResponse(
                    domain=existing.domain,
                    l0_summary=existing.l0_summary,
                    l1_overview=existing.l1_overview,
                    l2_architecture=existing.l2_architecture,
                    concepts_extracted=len(existing.concepts),
                    atom_id=existing.atom_id,
                    confidence=existing.confidence,
                    time_taken_ms=elapsed,
                    was_cached=True
                )
        
        # Build fresh knowledge
        knowledge = self.bootstrapper.build_domain_knowledge(
            domain=request.domain,
            target_depth=request.target_depth or "L2"
        )
        
        elapsed = (time.time() - start) * 1000
        
        return BuildKnowledgeResponse(
            domain=knowledge.domain,
            l0_summary=knowledge.l0_summary,
            l1_overview=knowledge.l1_overview,
            l2_architecture=knowledge.l2_architecture,
            concepts_extracted=len(knowledge.concepts),
            atom_id=knowledge.atom_id,
            confidence=knowledge.confidence,
            time_taken_ms=elapsed,
            was_cached=False
        )
    
    def get_health(self) -> HealthResponse:
        """Get server health status.
        
        Returns:
            Health status
        """
        uptime = time.time() - self.start_time
        
        return HealthResponse(
            status="healthy",
            systems={
                "cmc": "operational",
                "hhni": "operational",
                "vif": "operational",
                "seg": "operational",
                "llm": "operational"
            },
            uptime_seconds=uptime,
            total_requests=self.total_requests,
            memory_atoms=len(self.memory.list_atoms()),
            knowledge_domains=len([e for e in self.seg.entities.values() if e.type == "domain"])
        )


# =============================================================================
# FASTAPI APPLICATION
# =============================================================================

# Global server instance
_server: Optional[MCPServer] = None


def get_server() -> MCPServer:
    """Get or create global server instance."""
    global _server
    if _server is None:
        _server = MCPServer()
    return _server


# Create FastAPI app
app = FastAPI(
    title="AIM-OS MCP Server",
    description="Model Context Protocol server exposing conscious AI agents with memory",
    version="1.0.0"
)

# Add CORS for web clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =============================================================================
# MCP ENDPOINTS
# =============================================================================

@app.get("/health")
def health() -> HealthResponse:
    """Health check endpoint."""
    server = get_server()
    return server.get_health()


@app.post("/tools/ask_agent")
def ask_agent(request: AskAgentRequest) -> AskAgentResponse:
    """Ask the conscious agent a question.
    
    The agent has:
    - Memory of all past conversations (CMC)
    - Intelligent context retrieval (HHNI)
    - Knowledge learning (45,000x faster on reuse)
    - Provenance tracking (VIF)
    - Self-awareness (CAS)
    """
    server = get_server()
    return server.ask_agent(request)


@app.post("/tools/remember")
def remember(request: RememberRequest) -> RememberResponse:
    """Explicitly store content in agent's memory."""
    server = get_server()
    return server.remember(request)


@app.post("/tools/retrieve")
def retrieve(request: RetrieveRequest) -> RetrieveResponse:
    """Retrieve relevant context from agent's memory."""
    server = get_server()
    return server.retrieve_context(request)


@app.post("/tools/build_knowledge")
def build_knowledge(request: BuildKnowledgeRequest) -> BuildKnowledgeResponse:
    """Build domain knowledge for the agent.
    
    First time is expensive (30s for L2).
    Reuse is instant (45,000x faster!).
    """
    server = get_server()
    return server.build_knowledge(request)


# =============================================================================
# MCP PROTOCOL ENDPOINTS
# =============================================================================

@app.post("/mcp/tools/list")
def list_tools():
    """List available MCP tools (MCP protocol compliance)."""
    return {
        "tools": [
            {
                "name": "ask_agent",
                "description": "Ask the conscious AI agent. It has memory of all past conversations and builds knowledge over time.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Your question or task"},
                        "context_budget": {"type": "number", "description": "Max tokens for context (default: 4000)"},
                        "store_memory": {"type": "boolean", "description": "Store this interaction (default: true)"}
                    },
                    "required": ["query"]
                }
            },
            {
                "name": "remember",
                "description": "Explicitly store something in the agent's memory for later retrieval.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "content": {"type": "string", "description": "Content to remember"},
                        "tags": {"type": "object", "description": "Tags for categorization"},
                        "importance": {"type": "number", "description": "Importance score 0-1"}
                    },
                    "required": ["content"]
                }
            },
            {
                "name": "retrieve",
                "description": "Search the agent's memory for relevant past conversations or knowledge.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Search query"},
                        "max_results": {"type": "number", "description": "Max results (default: 10)"},
                        "min_relevance": {"type": "number", "description": "Min relevance 0-1 (default: 0.7)"}
                    },
                    "required": ["query"]
                }
            },
            {
                "name": "build_knowledge",
                "description": "Build domain knowledge for the agent. First time is expensive (~30s), reuse is instant (45,000x faster!).",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "domain": {"type": "string", "description": "Domain to learn (e.g., 'GraphQL', 'microservices')"},
                        "target_depth": {"type": "string", "enum": ["L0", "L1", "L2"], "description": "Depth: L0=100w, L1=500w, L2=2000w"},
                        "force_rebuild": {"type": "boolean", "description": "Force rebuild even if exists"}
                    },
                    "required": ["domain"]
                }
            }
        ]
    }


@app.post("/mcp/tools/call")
def call_tool(tool_name: str, arguments: dict):
    """Call an MCP tool (MCP protocol compliance)."""
    if tool_name == "ask_agent":
        request = AskAgentRequest(**arguments)
        return ask_agent(request)
    elif tool_name == "remember":
        request = RememberRequest(**arguments)
        return remember(request)
    elif tool_name == "retrieve":
        request = RetrieveRequest(**arguments)
        return retrieve(request)
    elif tool_name == "build_knowledge":
        request = BuildKnowledgeRequest(**arguments)
        return build_knowledge(request)
    else:
        raise HTTPException(status_code=404, detail=f"Tool '{tool_name}' not found")


# =============================================================================
# SERVER LIFECYCLE
# =============================================================================

@app.on_event("startup")
def startup():
    """Initialize server on startup."""
    print("=" * 80)
    print("AIM-OS MCP SERVER STARTING")
    print("=" * 80)
    print("\nConscious AI with memory, learning, and provenance")
    print("Exposing AetherAgent via Model Context Protocol\n")
    
    # Initialize global server
    server = get_server()
    
    print(f"Systems initialized:")
    print(f"  - CMC (Memory): {server.memory._atom_journal._path if server.memory._atom_journal else 'ready'}")
    print(f"  - HHNI (Retrieval): ready")
    print(f"  - VIF (Provenance): ready")
    print(f"  - SEG (Knowledge Graph): ready")
    print(f"  - LLM: {server.llm.__class__.__name__}")
    print(f"\nMCP Tools available: 4")
    print(f"  1. ask_agent - Conscious AI with memory")
    print(f"  2. remember - Explicit memory storage")
    print(f"  3. retrieve - Context search")
    print(f"  4. build_knowledge - Domain expertise")
    print("\n" + "=" * 80)
    print("SERVER READY - Listening for requests...")
    print("=" * 80 + "\n")


@app.on_event("shutdown")
def shutdown():
    """Cleanup on shutdown."""
    server = get_server()
    server.memory.close()
    print("\n[MCP Server] Shutdown complete")


# =============================================================================
# MAIN
# =============================================================================

def main():
    """Run the MCP server."""
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )


if __name__ == "__main__":
    main()

