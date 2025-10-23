"""MCP Server - Model Context Protocol server exposing AIM-OS conscious agents.

Provides Cursor IDE and other MCP clients with access to:
- Conscious AI with persistent memory (AetherAgent)
- Multi-LLM orchestration (Gemini + Cerebras)
- Knowledge bootstrapping (learning over time)
- Quality enforcement (SDF-CVF gates)
- Provenance tracking (VIF witnesses)

Example:
    Run the server:
    >>> python -m mcp_server.server
    
    Or programmatically:
    >>> from mcp_server import MCPServer
    >>> server = MCPServer()
    >>> server.start()
"""

from .models import (
    AskAgentRequest,
    AskAgentResponse,
    RememberRequest,
    RememberResponse,
    RetrieveRequest,
    RetrieveResponse,
    BuildKnowledgeRequest,
    BuildKnowledgeResponse,
)

__all__ = [
    "AskAgentRequest",
    "AskAgentResponse",
    "RememberRequest",
    "RememberResponse",
    "RetrieveRequest",
    "RetrieveResponse",
    "BuildKnowledgeRequest",
    "BuildKnowledgeResponse",
]

__version__ = "1.0.0"

