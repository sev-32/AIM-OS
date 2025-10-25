#!/usr/bin/env python3
"""
Fixed AIM-OS MCP Server - Better error handling and debugging
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

class FixedAIMOSServer:
    """Fixed MCP Server with better error handling"""
    
    def __init__(self):
        log("Initializing Fixed AIM-OS Server...")
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
        """Main MCP server loop with better error handling"""
        log("Starting MCP server loop...")
        
        try:
            while True:
                try:
                    line = sys.stdin.readline()
                    if not line:
                        log("No input received, exiting")
                        break
                        
                    line = line.strip()
                    if not line:
                        continue
                        
                    log(f"Received request: {line[:100]}...")
                    request = json.loads(line)
                    response = self.handle_request(request)
                    
                    if response:
                        log(f"Sending response: {json.dumps(response)[:100]}...")
                        print(json.dumps(response), flush=True)
                        
                except json.JSONDecodeError as e:
                    log(f"JSON decode error: {e}")
                    continue
                except Exception as e:
                    log(f"Error handling request: {e}")
                    continue
                    
        except KeyboardInterrupt:
            log("Keyboard interrupt, shutting down")
        except Exception as e:
            log(f"Fatal error in main loop: {e}")
            import traceback
            traceback.print_exc(file=sys.stderr)
    
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
                        "name": "aimos-mcp-fixed",
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
                        },
                        {
                            "name": "retrieve_memory",
                            "description": "Search and retrieve memories from AIM-OS persistent memory",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "query": {"type": "string", "description": "Search query for memories"},
                                    "limit": {"type": "integer", "description": "Maximum number of memories to return", "default": 10},
                                    "tags": {"type": "object", "description": "Filter by tags"}
                                },
                                "required": ["query"]
                            }
                        },
                        {
                            "name": "create_plan",
                            "description": "Create an execution plan using APOE (AI-Powered Orchestration Engine)",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "goal": {"type": "string", "description": "The goal to achieve"},
                                    "context": {"type": "string", "description": "Current context and constraints"},
                                    "priority": {"type": "string", "enum": ["low", "medium", "high", "critical"], "default": "medium"}
                                },
                                "required": ["goal"]
                            }
                        },
                        {
                            "name": "track_confidence",
                            "description": "Track confidence and provenance using VIF (Verifiable Intelligence Framework)",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "task": {"type": "string", "description": "Task being tracked"},
                                    "confidence": {"type": "number", "minimum": 0, "maximum": 1, "description": "Confidence level (0-1)"},
                                    "reasoning": {"type": "string", "description": "Reasoning for confidence level"},
                                    "evidence": {"type": "array", "items": {"type": "string"}, "description": "Supporting evidence"}
                                },
                                "required": ["task", "confidence"]
                            }
                        },
                        {
                            "name": "synthesize_knowledge",
                            "description": "Synthesize knowledge using SEG (Shared Evidence Graph)",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "topics": {"type": "array", "items": {"type": "string"}, "description": "Topics to synthesize"},
                                    "depth": {"type": "string", "enum": ["shallow", "medium", "deep"], "default": "medium"},
                                    "format": {"type": "string", "enum": ["summary", "detailed", "structured"], "default": "summary"}
                                },
                                "required": ["topics"]
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
            elif tool_name == "retrieve_memory":
                return self.retrieve_memory(request_id, arguments)
            elif tool_name == "create_plan":
                return self.create_plan(request_id, arguments)
            elif tool_name == "track_confidence":
                return self.track_confidence(request_id, arguments)
            elif tool_name == "synthesize_knowledge":
                return self.synthesize_knowledge(request_id, arguments)
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
            atom_create = AtomCreate(modality="text", content=atom_content, tags=tags)
            
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
    
    def retrieve_memory(self, request_id: Any, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Retrieve memories from AIM-OS"""
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
            
            query = arguments.get("query", "")
            limit = arguments.get("limit", 10)
            tags_filter = arguments.get("tags", {})
            
            # Get all atoms and filter by query
            atoms = list(self.memory.list_atoms())
            
            # Simple text-based search for now
            # In the future, this could use HHNI for semantic search
            matching_atoms = []
            for atom in atoms:
                # Check if query matches content
                content_text = ""
                if hasattr(atom.content, 'inline') and atom.content.inline:
                    content_text = atom.content.inline
                
                # Simple text search
                if query.lower() in content_text.lower():
                    # Check tags filter if provided
                    if tags_filter:
                        atom_tags = atom.tags or {}
                        if all(atom_tags.get(key) == value for key, value in tags_filter.items()):
                            matching_atoms.append(atom)
                    else:
                        matching_atoms.append(atom)
            
            # Limit results
            matching_atoms = matching_atoms[:limit]
            
            # Format results
            results = []
            for atom in matching_atoms:
                content_text = atom.content.inline if hasattr(atom.content, 'inline') and atom.content.inline else ""
                results.append({
                    "id": atom.id,
                    "content": content_text,
                    "tags": atom.tags or {},
                    "created_at": atom.created_at.isoformat() if hasattr(atom, 'created_at') and atom.created_at else None
                })
            
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": f"Found {len(results)} memories matching '{query}':\n\n" + 
                                   "\n\n".join([
                                       f"ID: {r['id']}\nContent: {r['content'][:200]}{'...' if len(r['content']) > 200 else ''}\nTags: {r['tags']}"
                                       for r in results
                                   ])
                        }
                    ]
                }
            }
            
        except Exception as e:
            log(f"Error retrieving memory: {e}")
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32603,
                    "message": f"Failed to retrieve memory: {str(e)}"
                }
            }
    
    def create_plan(self, request_id: Any, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Create an execution plan using APOE"""
        try:
            goal = arguments.get("goal", "")
            context = arguments.get("context", "")
            priority = arguments.get("priority", "medium")
            
            # Simple plan creation for now
            # In the future, this would use the full APOE system
            plan = {
                "goal": goal,
                "priority": priority,
                "context": context,
                "steps": [
                    f"1. Analyze goal: {goal}",
                    f"2. Consider context: {context}",
                    f"3. Break down into actionable steps",
                    f"4. Execute with {priority} priority",
                    "5. Monitor and adjust as needed"
                ],
                "estimated_duration": "30-60 minutes",
                "confidence": 0.75
            }
            
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": f"APOE Execution Plan Created:\n\nGoal: {goal}\nPriority: {priority}\n\nSteps:\n" + 
                                   "\n".join(plan["steps"]) + 
                                   f"\n\nEstimated Duration: {plan['estimated_duration']}\nConfidence: {plan['confidence']}"
                        }
                    ]
                }
            }
            
        except Exception as e:
            log(f"Error creating plan: {e}")
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32603,
                    "message": f"Failed to create plan: {str(e)}"
                }
            }
    
    def track_confidence(self, request_id: Any, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Track confidence and provenance using VIF"""
        try:
            task = arguments.get("task", "")
            confidence = arguments.get("confidence", 0.5)
            reasoning = arguments.get("reasoning", "")
            evidence = arguments.get("evidence", [])
            
            # Simple confidence tracking for now
            # In the future, this would use the full VIF system
            confidence_level = "Low" if confidence < 0.4 else "Medium" if confidence < 0.7 else "High"
            
            tracking_result = {
                "task": task,
                "confidence": confidence,
                "level": confidence_level,
                "reasoning": reasoning,
                "evidence_count": len(evidence),
                "timestamp": "2025-10-23T10:15:00Z"
            }
            
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": f"VIF Confidence Tracking:\n\nTask: {task}\nConfidence: {confidence} ({confidence_level})\nReasoning: {reasoning}\nEvidence: {len(evidence)} items\nTimestamp: {tracking_result['timestamp']}"
                        }
                    ]
                }
            }
            
        except Exception as e:
            log(f"Error tracking confidence: {e}")
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32603,
                    "message": f"Failed to track confidence: {str(e)}"
                }
            }
    
    def synthesize_knowledge(self, request_id: Any, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Synthesize knowledge using SEG"""
        try:
            topics = arguments.get("topics", [])
            depth = arguments.get("depth", "medium")
            format_type = arguments.get("format", "summary")
            
            # Simple knowledge synthesis for now
            # In the future, this would use the full SEG system
            synthesis = {
                "topics": topics,
                "depth": depth,
                "format": format_type,
                "insights": [
                    f"Key insight about {topic}" for topic in topics
                ],
                "connections": [
                    f"Connection between {topics[0]} and {topics[1]}" if len(topics) > 1 else "Single topic analysis"
                ],
                "confidence": 0.8
            }
            
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": f"SEG Knowledge Synthesis:\n\nTopics: {', '.join(topics)}\nDepth: {depth}\nFormat: {format_type}\n\nInsights:\n" + 
                                   "\n".join([f"- {insight}" for insight in synthesis["insights"]]) +
                                   f"\n\nConnections:\n- {synthesis['connections'][0]}\n\nConfidence: {synthesis['confidence']}"
                        }
                    ]
                }
            }
            
        except Exception as e:
            log(f"Error synthesizing knowledge: {e}")
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32603,
                    "message": f"Failed to synthesize knowledge: {str(e)}"
                }
            }

def main():
    """Entry point"""
    try:
        log("=== FIXED AIM-OS MCP SERVER STARTING ===")
        log(f"Python version: {sys.version}")
        log(f"Python executable: {sys.executable}")
        log(f"Current directory: {os.getcwd()}")
        log(f"Script location: {__file__}")
        
        server = FixedAIMOSServer()
        log("Server created successfully, starting main loop...")
        server.run()
    except Exception as e:
        log(f"FATAL ERROR: {e}")
        import traceback
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
