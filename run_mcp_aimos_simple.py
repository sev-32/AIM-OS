#!/usr/bin/env python3
"""
Simplified AIM-OS MCP Server - Focus on MCP Protocol
Minimal version to debug Cursor integration issues
"""
import sys
import json
import os
from pathlib import Path
from typing import Any, Dict

# Add packages to path
sys.path.insert(0, str(Path(__file__).parent / "packages"))

def log(msg: str):
    """Log to stderr only (never stdout - it corrupts JSON-RPC)"""
    print(f"[MCP-AIMOS] {msg}", file=sys.stderr, flush=True)

class SimpleAIMOSServer:
    """Simplified MCP Server for debugging"""
    
    def __init__(self):
        log("Initializing Simple AIM-OS Server...")
        try:
            # CRITICAL: Configure CMC logging to stderr BEFORE importing
            import logging
            from cmc_service.logging_utils import configure_logging
            configure_logging(stream=sys.stderr, level=logging.WARNING)
            
            # Try to import AIM-OS modules
            from cmc_service import MemoryStore
            from cmc_service.models import AtomCreate, AtomContent
            
            self.memory = MemoryStore("./mcp_memory")
            log("SUCCESS: Memory systems initialized")
            
        except Exception as e:
            log(f"ERROR: Failed to initialize memory systems: {e}")
            self.memory = None
    
    def run(self):
        """Main MCP server loop"""
        log("Starting MCP server loop...")
        
        while True:
            try:
                line = sys.stdin.readline()
                if not line:
                    break
                    
                request = json.loads(line.strip())
                response = self.handle_request(request)
                
                if response:
                    print(json.dumps(response), flush=True)
                    
            except json.JSONDecodeError as e:
                log(f"JSON decode error: {e}")
                continue
            except Exception as e:
                log(f"Error handling request: {e}")
                continue
    
    def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle MCP requests"""
        method = request.get("method")
        request_id = request.get("id")
        
        log(f"Handling request: {method}")
        
        if method == "initialize":
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {}
                    },
                    "serverInfo": {
                        "name": "aimos-mcp-simple",
                        "version": "1.0.0"
                    }
                }
            }
        
        elif method == "tools/list":
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "tools": [
                        {
                            "name": "store_memory",
                            "description": "Store information in AIM-OS persistent memory",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "content": {"type": "string"},
                                    "tags": {"type": "object"}
                                },
                                "required": ["content"]
                            }
                        },
                        {
                            "name": "get_memory_stats",
                            "description": "Get statistics about the AIM-OS memory system",
                            "inputSchema": {
                                "type": "object",
                                "properties": {}
                            }
                        }
                    ]
                }
            }
        
        elif method == "tools/call":
            tool_name = request.get("params", {}).get("name")
            arguments = request.get("params", {}).get("arguments", {})
            
            if tool_name == "store_memory":
                return self.store_memory(request_id, arguments)
            elif tool_name == "get_memory_stats":
                return self.get_memory_stats(request_id, arguments)
            else:
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32601,
                        "message": f"Unknown tool: {tool_name}"
                    }
                }
        
        return None
    
    def store_memory(self, request_id: Any, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Store memory in AIM-OS"""
        try:
            if not self.memory:
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32603,
                        "message": "Memory system not initialized"
                    }
                }
            
            content = arguments.get("content", "")
            tags = arguments.get("tags", {})
            
            from cmc_service.models import AtomCreate, AtomContent
            
            atom_content = AtomContent(inline=content)
            atom_create = AtomCreate(content=atom_content, tags=tags)
            
            atom = self.memory.create_atom(atom_create)
            
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": f"Memory stored successfully! ID: {atom.id}"
                        }
                    ]
                }
            }
            
        except Exception as e:
            log(f"Error storing memory: {e}")
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32603,
                    "message": f"Failed to store memory: {str(e)}"
                }
            }
    
    def get_memory_stats(self, request_id: Any, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Get memory system statistics"""
        try:
            if not self.memory:
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": "Memory system not initialized"
                            }
                        ]
                    }
                }
            
            # Get basic stats
            try:
                atoms = list(self.memory.list_atoms())
                total_memories = len(atoms)
            except Exception as e:
                log(f"Error getting atom count: {e}")
                total_memories = 0
            
            stats = {
                "status": "OPERATIONAL",
                "total_memories": total_memories,
                "storage_path": "./mcp_memory"
            }
            
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": f"AIM-OS Memory System Status:\n\nStatus: {stats['status']}\nTotal Memories: {stats['total_memories']}\nStorage Path: {stats['storage_path']}"
                        }
                    ]
                }
            }
            
        except Exception as e:
            log(f"Error getting memory stats: {e}")
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32603,
                    "message": f"Failed to get memory stats: {str(e)}"
                }
            }

def main():
    """Entry point"""
    try:
        log("=== SIMPLE AIM-OS MCP SERVER STARTING ===")
        log(f"Python version: {sys.version}")
        log(f"Python executable: {sys.executable}")
        log(f"Current directory: {os.getcwd()}")
        log(f"Script location: {__file__}")
        
        server = SimpleAIMOSServer()
        log("Server created successfully, starting main loop...")
        server.run()
    except Exception as e:
        log(f"FATAL ERROR: {e}")
        import traceback
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
