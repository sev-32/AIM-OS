#!/usr/bin/env python3
"""
AIM-OS MCP Server - Simple Memory Tools for Cursor
Provides memory/retrieval tools WITHOUT embedding its own LLM
Cursor's AI uses these tools to access AIM-OS memory systems
"""
import sys
import json
import os
from pathlib import Path

# Add packages to path
sys.path.insert(0, str(Path(__file__).parent / "packages"))

from cmc_service import MemoryStore
from hhni import HierarchicalIndex
from seg import SEGraph

class SimpleMCPServer:
    """MCP Server that provides memory tools to Cursor's AI"""
    
    def __init__(self):
        """Initialize memory systems (NO LLM needed!)"""
        def log(msg: str):
            print(f"[MCP-SIMPLE] {msg}", file=sys.stderr, flush=True)
        
        self.log = log
        self.log("Initializing AIM-OS Memory Tools...")
        
        # Initialize ONLY memory systems (no LLM!)
        self.memory = MemoryStore("./mcp_memory")
        self.hhni = HierarchicalIndex()
        self.seg = SEGraph()
        
        self.log("Memory systems ready!")
        self.log("Cursor's AI can now access AIM-OS memory")
    
    def handle_request(self, request: dict) -> dict:
        """Handle an MCP request"""
        method = request.get("method")
        params = request.get("params", {})
        
        try:
            if method == "tools/list":
                return self.list_tools()
            elif method == "tools/call":
                return self.call_tool(params)
            else:
                return {
                    "error": {
                        "code": -32601,
                        "message": f"Method not found: {method}"
                    }
                }
        except Exception as e:
            self.log(f"Error handling {method}: {e}")
            return {
                "error": {
                    "code": -32603,
                    "message": str(e)
                }
            }
    
    def list_tools(self) -> dict:
        """List available MCP tools"""
        return {
            "tools": [
                {
                    "name": "store_memory",
                    "description": "Store information in AIM-OS persistent memory (CMC)",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "content": {
                                "type": "string",
                                "description": "The information to store"
                            },
                            "tags": {
                                "type": "object",
                                "description": "Optional tags for categorization"
                            }
                        },
                        "required": ["content"]
                    }
                },
                {
                    "name": "retrieve_memory",
                    "description": "Search AIM-OS memory for relevant past information",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "What to search for"
                            },
                            "limit": {
                                "type": "integer",
                                "description": "Max results to return"
                            }
                        },
                        "required": ["query"]
                    }
                },
                {
                    "name": "get_memory_stats",
                    "description": "Get statistics about AIM-OS memory system",
                    "inputSchema": {
                        "type": "object",
                        "properties": {}
                    }
                }
            ]
        }
    
    def call_tool(self, params: dict) -> dict:
        """Call a tool"""
        tool_name = params.get("name")
        args = params.get("arguments", {})
        
        if tool_name == "store_memory":
            content = args.get("content")
            tags = args.get("tags", {})
            
            # Store in CMC
            from cmc_service.models import Atom
            from datetime import datetime
            
            atom = Atom(
                content=content,
                tags=tags,
                timestamp=datetime.utcnow()
            )
            
            atom_id = self.memory.store_atom(atom)
            
            # Index in HHNI
            self.hhni.add_paragraph(content)
            
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"Stored in memory with ID: {atom_id}"
                    }
                ],
                "isError": False
            }
        
        elif tool_name == "retrieve_memory":
            query = args.get("query")
            limit = args.get("limit", 5)
            
            # Search HHNI
            from hhni.models import IndexLevel
            results = self.hhni.query(query, target_level=IndexLevel.PARAGRAPH, max_results=limit)
            
            memories = [getattr(r, 'content', str(r)) for r in results[:limit]]
            
            if not memories:
                result_text = "No relevant memories found."
            else:
                result_text = "\n\n".join(f"Memory {i+1}:\n{m}" for i, m in enumerate(memories))
            
            return {
                "content": [
                    {
                        "type": "text",
                        "text": result_text
                    }
                ],
                "isError": False
            }
        
        elif tool_name == "get_memory_stats":
            # Get memory stats
            atoms = self.memory.list_atoms()
            
            stats = {
                "total_memories": len(atoms),
                "systems_active": ["CMC", "HHNI", "SEG"],
                "status": "operational"
            }
            
            return {
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps(stats, indent=2)
                    }
                ],
                "isError": False
            }
        
        else:
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"Unknown tool: {tool_name}"
                    }
                ],
                "isError": True
            }
    
    def run(self):
        """Run the server loop (stdio)"""
        self.log("Starting stdio loop...")
        
        # Read from stdin line by line
        while True:
            try:
                line = sys.stdin.readline()
                if not line:  # EOF
                    break
                    
                request = json.loads(line.strip())
                self.log(f"Received: {request.get('method')}")
                
                response = self.handle_request(request)
                
                # Add request ID if present
                if "id" in request:
                    response["id"] = request["id"]
                
                # Send response to stdout with explicit flush
                response_json = json.dumps(response)
                sys.stdout.write(response_json + '\n')
                sys.stdout.flush()
                
            except json.JSONDecodeError as e:
                self.log(f"Invalid JSON: {e}")
                error_response = {
                    "error": {
                        "code": -32700,
                        "message": "Parse error"
                    }
                }
                sys.stdout.write(json.dumps(error_response) + '\n')
                sys.stdout.flush()
            except Exception as e:
                self.log(f"Error: {e}")
                import traceback
                traceback.print_exc(file=sys.stderr)

if __name__ == "__main__":
    try:
        server = SimpleMCPServer()
        server.run()
    except Exception as e:
        print(f"[MCP-SIMPLE] FATAL: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)

