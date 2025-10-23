"""MCP Server Request/Response Models.

Defines Pydantic models for MCP tool requests and responses,
ensuring type safety and validation.
"""

from __future__ import annotations

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime


# =============================================================================
# ASK_AGENT TOOL
# =============================================================================

class AskAgentRequest(BaseModel):
    """Request to ask the conscious agent a question."""
    
    query: str = Field(..., description="Question or task for the agent")
    context_budget: Optional[int] = Field(4000, description="Max tokens for context retrieval")
    store_memory: Optional[bool] = Field(True, description="Store this interaction in memory")
    use_orchestration: Optional[bool] = Field(False, description="Use multi-step orchestration for complex tasks")


class AskAgentResponse(BaseModel):
    """Response from the conscious agent."""
    
    response: str = Field(..., description="Agent's response text")
    confidence: float = Field(..., description="Agent's confidence in response (0-1)")
    witness_id: str = Field(..., description="VIF witness ID for provenance")
    context_used: int = Field(..., description="Number of context items retrieved from memory")
    tokens_used: int = Field(..., description="Total tokens consumed")
    latency_ms: float = Field(..., description="Total processing time in milliseconds")
    learning_occurred: bool = Field(..., description="Whether agent built new knowledge")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


# =============================================================================
# REMEMBER TOOL
# =============================================================================

class RememberRequest(BaseModel):
    """Request to explicitly store content in memory."""
    
    content: str = Field(..., description="Content to remember")
    tags: Optional[Dict[str, float]] = Field(None, description="Tags for categorization (name -> weight)")
    importance: Optional[float] = Field(0.8, description="Importance score (0-1) affects retrieval priority")


class RememberResponse(BaseModel):
    """Response from memory storage."""
    
    atom_id: str = Field(..., description="CMC atom ID where content is stored")
    indexed: bool = Field(..., description="Whether content was indexed in HHNI")
    knowledge_graph_updated: bool = Field(..., description="Whether SEG was updated")


# =============================================================================
# RETRIEVE_CONTEXT TOOL
# =============================================================================

class RetrieveRequest(BaseModel):
    """Request to retrieve relevant context from memory."""
    
    query: str = Field(..., description="Search query")
    max_results: Optional[int] = Field(10, description="Maximum number of results")
    min_relevance: Optional[float] = Field(0.7, description="Minimum relevance score (0-1)")


class ContextItem(BaseModel):
    """A single context item from memory."""
    
    content: str
    relevance: float
    source_id: str
    timestamp: str
    metadata: Dict[str, Any] = Field(default_factory=dict)


class RetrieveResponse(BaseModel):
    """Response with retrieved context items."""
    
    results: List[ContextItem] = Field(..., description="Retrieved context items")
    total_found: int = Field(..., description="Total items found (before filtering)")


# =============================================================================
# BUILD_KNOWLEDGE TOOL
# =============================================================================

class BuildKnowledgeRequest(BaseModel):
    """Request to build domain knowledge."""
    
    domain: str = Field(..., description="Domain to build knowledge for (e.g., 'GraphQL', 'microservices')")
    target_depth: Optional[str] = Field("L2", description="Knowledge depth: L0 (100w), L1 (500w), L2 (2000w)")
    force_rebuild: Optional[bool] = Field(False, description="Force rebuild even if knowledge exists")


class BuildKnowledgeResponse(BaseModel):
    """Response from knowledge building."""
    
    domain: str
    l0_summary: str
    l1_overview: str
    l2_architecture: Optional[str] = None
    concepts_extracted: int
    atom_id: str
    confidence: float
    time_taken_ms: float
    was_cached: bool = Field(..., description="Whether knowledge was retrieved from cache vs built fresh")


# =============================================================================
# SERVER HEALTH
# =============================================================================

class HealthResponse(BaseModel):
    """Server health status."""
    
    status: str = Field(..., description="'healthy' or 'degraded'")
    systems: Dict[str, str] = Field(..., description="Status of each AIM-OS system")
    uptime_seconds: float
    total_requests: int
    memory_atoms: int
    knowledge_domains: int

