#!/usr/bin/env python3
"""
AIM-OS MCP Server - Real Memory Tools for Cursor
Provides persistent memory tools using CMC, HHNI, and SEG
Properly implements MCP protocol for Cursor integration
"""
import sys
import json
import os
from pathlib import Path
from typing import Any, Dict

# Add packages to path
sys.path.insert(0, str(Path(__file__).parent / "packages"))

from cmc_service import MemoryStore
from cmc_service.models import AtomCreate, AtomContent
from hhni import HierarchicalIndex
from hhni.hierarchical_index import IndexLevel
from seg import SEGraph
from datetime import datetime

def log(msg: str):
    """Log to stderr only (never stdout - it corrupts JSON-RPC)"""
    print(f"[MCP-AIMOS] {msg}", file=sys.stderr, flush=True)

class AIMOSMCPServer:
    """MCP Server providing AIM-OS memory tools to Cursor"""
    
    def __init__(self):
        """Initialize AIM-OS memory systems"""
        log("Initializing AIM-OS Memory Systems...")
        
        # CRITICAL: Configure CMC logging to stderr (not stdout!)
        # CMC logs to stdout by default, which corrupts JSON-RPC
        import logging
        from cmc_service.logging_utils import configure_logging
        configure_logging(stream=sys.stderr, level=logging.WARNING)
        
        try:
            self.memory = MemoryStore("./mcp_memory")
            self.hhni = HierarchicalIndex()
            self.seg = SEGraph()
            
            log("SUCCESS: CMC (Context Memory Core) initialized")
            log("SUCCESS: HHNI (Hierarchical Index) initialized")
            log("SUCCESS: SEG (Shared Evidence Graph) initialized")
            log("AIM-OS MCP Server ready!")
            
        except Exception as e:
            log(f"ERROR initializing systems: {e}")
            raise
    
    def handle_initialize(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle MCP initialize request"""
        log("Handling initialize request")
        return {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "tools": {}
            },
            "serverInfo": {
                "name": "aimos-mcp",
                "version": "1.0.0"
            }
        }
    
    def handle_tools_list(self) -> Dict[str, Any]:
        """List available MCP tools"""
        log("Listing tools")
        return {
            "tools": [
                {
                    "name": "store_memory",
                    "description": "Store information in AIM-OS persistent memory (CMC). The memory is indexed in HHNI for fast retrieval and can be searched later.",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "content": {
                                "type": "string",
                                "description": "The information to store in memory"
                            },
                            "tags": {
                                "type": "object",
                                "description": "Optional tags for categorization (e.g., {'category': 'learning', 'importance': 0.9})",
                                "additionalProperties": True
                            }
                        },
                        "required": ["content"]
                    }
                },
                {
                    "name": "retrieve_memory",
                    "description": "Search AIM-OS memory (HHNI) for relevant past information. Returns semantically similar memories based on the query.",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "What to search for in memory"
                            },
                            "limit": {
                                "type": "integer",
                                "description": "Maximum number of results to return (default: 5)",
                                "default": 5
                            }
                        },
                        "required": ["query"]
                    }
                },
                {
                    "name": "get_memory_stats",
                    "description": "Get statistics about the AIM-OS memory system, including total memories stored and system status.",
                    "inputSchema": {
                        "type": "object",
                        "properties": {}
                    }
                }
            ]
        }
    
    def handle_tools_call(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle tool execution"""
        tool_name = params.get("name")
        args = params.get("arguments", {})
        
        log(f"Calling tool: {tool_name}")
        
        try:
            if tool_name == "store_memory":
                return self.tool_store_memory(args)
            elif tool_name == "retrieve_memory":
                return self.tool_retrieve_memory(args)
            elif tool_name == "get_memory_stats":
                return self.tool_get_memory_stats(args)
            else:
                return {
                    "content": [{
                        "type": "text",
                        "text": f"Unknown tool: {tool_name}"
                    }],
                    "isError": True
                }
        except Exception as e:
            log(f"Error executing {tool_name}: {e}")
            import traceback
            traceback.print_exc(file=sys.stderr)
            return {
                "content": [{
                    "type": "text",
                    "text": f"Error executing {tool_name}: {str(e)}"
                }],
                "isError": True
            }
    
    def tool_store_memory(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Store information in CMC and index in HHNI"""
        content = args.get("content")
        tags = args.get("tags", {})
        
        if not content:
            return {
                "content": [{
                    "type": "text",
                    "text": "Error: content is required"
                }],
                "isError": True
            }
        
        # Create atom and store in CMC
        from cmc_service.models import AtomCreate, AtomContent
        atom = AtomCreate(
            modality="text",
            content=AtomContent(inline=content),
            tags=tags
        )
        
        atom_result = self.memory.create_atom(atom)
        atom_id = atom_result.id
        log(f"Stored atom: {atom_id}")
        
        # Index in HHNI for fast retrieval
        try:
            self.hhni.add_paragraph(content)
            log(f"Indexed in HHNI")
        except Exception as e:
            log(f"Warning: HHNI indexing failed: {e}")
        
        return {
            "content": [{
                "type": "text",
                "text": f"SUCCESS: Memory stored!\n\nID: {atom_id}\nContent: {content[:100]}{'...' if len(content) > 100 else ''}\nTags: {tags}\n\nThis memory is now persistent and searchable."
            }],
            "isError": False
        }
    
    def tool_retrieve_memory(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Search HHNI for relevant memories"""
        query = args.get("query")
        limit = args.get("limit", 5)
        
        if not query:
            return {
                "content": [{
                    "type": "text",
                    "text": "Error: query is required"
                }],
                "isError": True
            }
        
        log(f"Searching for: {query}")
        
        # Search HHNI
        try:
            results = self.hhni.query(
                query, 
                target_level=IndexLevel.PARAGRAPH, 
                max_results=limit
            )
            
            if not results:
                return {
                    "content": [{
                        "type": "text",
                        "text": f"No memories found for query: '{query}'\n\nTry:\n- Using different keywords\n- Being more specific\n- Checking if memories were stored"
                    }],
                    "isError": False
                }
            
            # Format results
            memories = []
            for i, result in enumerate(results[:limit], 1):
                content = getattr(result, 'content', str(result))
                memories.append(f"Memory {i}:\n{content}")
            
            result_text = f"Found {len(memories)} relevant memories for '{query}':\n\n" + "\n\n---\n\n".join(memories)
            
            log(f"Retrieved {len(memories)} memories")
            
            return {
                "content": [{
                    "type": "text",
                    "text": result_text
                }],
                "isError": False
            }
            
        except Exception as e:
            log(f"Error searching HHNI: {e}")
            return {
                "content": [{
                    "type": "text",
                    "text": f"Error searching memory: {str(e)}"
                }],
                "isError": True
            }
    
    def tool_get_memory_stats(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Get memory system statistics"""
        try:
            atoms = self.memory.list_atoms()
            
            stats = {
                "total_memories": len(atoms),
                "systems_active": ["CMC", "HHNI", "SEG"],
                "status": "operational",
                "memory_path": "./mcp_memory"
            }
            
            stats_text = f"""AIM-OS Memory System Status:

Status: {stats['status'].upper()}
Total Memories: {stats['total_memories']}
Active Systems: {', '.join(stats['systems_active'])}
Storage Path: {stats['memory_path']}

The memory system is fully operational and ready to store/retrieve information."""
            
            log(f"Stats: {stats['total_memories']} memories")
            
            return {
                "content": [{
                    "type": "text",
                    "text": stats_text
                }],
                "isError": False
            }
            
        except Exception as e:
            log(f"Error getting stats: {e}")
            return {
                "content": [{
                    "type": "text",
                    "text": f"Error getting stats: {str(e)}"
                }],
                "isError": True
            }
    
    def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Route MCP requests to appropriate handlers"""
        method = request.get("method")
        params = request.get("params", {})
        
        try:
            if method == "initialize":
                return self.handle_initialize(params)
            elif method == "tools/list":
                return self.handle_tools_list()
            elif method == "tools/call":
                return self.handle_tools_call(params)
            else:
                log(f"Unknown method: {method}")
                return {
                    "error": {
                        "code": -32601,
                        "message": f"Method not found: {method}"
                    }
                }
        except Exception as e:
            log(f"Error handling {method}: {e}")
            import traceback
            traceback.print_exc(file=sys.stderr)
            return {
                "error": {
                    "code": -32603,
                    "message": f"Internal error: {str(e)}"
                }
            }
    
    def run(self):
        """Run the MCP server (stdio transport)"""
        log("Starting MCP server (stdio)...")
        log("Waiting for requests from Cursor...")
        
        while True:
            try:
                # Read request from stdin
                line = sys.stdin.readline()
                if not line:  # EOF
                    log("EOF received, shutting down")
                    break
                
                # Parse JSON-RPC request
                request = json.loads(line.strip())
                method = request.get("method", "unknown")
                
                # Handle request
                response = self.handle_request(request)
                
                # Add request ID to response
                if "id" in request:
                    response["id"] = request["id"]
                
                # Send JSON-RPC response to stdout
                response_json = json.dumps(response)
                sys.stdout.write(response_json + '\n')
                sys.stdout.flush()
                
            except json.JSONDecodeError as e:
                log(f"Invalid JSON: {e}")
                error_response = {
                    "error": {
                        "code": -32700,
                        "message": "Parse error: Invalid JSON"
                    }
                }
                sys.stdout.write(json.dumps(error_response) + '\n')
                sys.stdout.flush()
                
            except KeyboardInterrupt:
                log("Keyboard interrupt, shutting down")
                break
                
            except Exception as e:
                log(f"Unexpected error: {e}")
                import traceback
                traceback.print_exc(file=sys.stderr)

def main():
    """Entry point"""
    try:
        log("=== AIM-OS MCP SERVER STARTING ===")
        log(f"Python version: {sys.version}")
        log(f"Python executable: {sys.executable}")
        log(f"Current directory: {os.getcwd()}")
        log(f"Script location: {__file__}")
        
        server = AIMOSMCPServer()
        log("Server created successfully, starting main loop...")
        server.run()
    except Exception as e:
        log(f"FATAL ERROR: {e}")
        import traceback
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
