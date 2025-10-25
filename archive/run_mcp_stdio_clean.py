#!/usr/bin/env python3
"""
AIM-OS MCP Server - STDIO Mode for Cursor (Clean Version)
Communicates via stdin/stdout using MCP protocol

USAGE:
  python -u run_mcp_stdio_clean.py
  
The -u flag ensures unbuffered I/O which is critical for MCP protocol.
"""
import sys
import json
import os
from pathlib import Path
from contextlib import redirect_stdout
import io

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# CRITICAL: Redirect any stdout from libraries to stderr
# This prevents CMC logs from interfering with MCP protocol
class StdoutToStderr:
    def __init__(self):
        self.original_stdout = sys.stdout
        self.original_stderr = sys.stderr
        
    def write(self, text):
        # Write to stderr instead of stdout
        self.original_stderr.write(text)
        self.original_stderr.flush()
        
    def flush(self):
        self.original_stderr.flush()
        
    def __getattr__(self, name):
        return getattr(self.original_stdout, name)

# Redirect stdout to stderr for library imports
sys.stdout = StdoutToStderr()

# Add packages to path
sys.path.insert(0, str(Path(__file__).parent / "packages"))

# Import with stdout redirected
from llm_client import GeminiClient, CerebrasClient
from agent import AetherAgent
from cmc_service import MemoryStore
from hhni import HierarchicalIndex
from seg import SEGraph

# Restore stdout for MCP protocol
sys.stdout = sys.__stdout__

class StdioMCPServer:
    """MCP Server using stdio for Cursor integration"""
    
    def __init__(self):
        """Initialize the server"""
        # Setup logging to stderr (stdout is for MCP messages)
        def log(msg: str):
            print(f"[MCP-STDIO] {msg}", file=sys.stderr, flush=True)
        
        self.log = log
        self.log("Initializing AIM-OS MCP Server (stdio mode)...")
        
        # Initialize LLM clients
        gemini_key = os.getenv("GEMINI_API_KEY")
        cerebras_key = os.getenv("CEREBRAS_API_KEY")
        
        if not gemini_key:
            self.log("WARNING: GEMINI_API_KEY not set!")
        
        self.gemini = GeminiClient(api_key=gemini_key) if gemini_key else None
        
        # Cerebras optional
        self.cerebras = None
        if cerebras_key:
            try:
                self.cerebras = CerebrasClient(api_key=cerebras_key)
                self.log("Cerebras client initialized")
            except Exception as e:
                self.log(f"Cerebras init failed: {e}")
        
        # Select LLM
        self.llm = self.gemini or self.cerebras
        if not self.llm:
            raise ValueError("No LLM client available! Set GEMINI_API_KEY or CEREBRAS_API_KEY")
        
        # Initialize AIM-OS systems (with stdout redirected)
        with redirect_stdout(io.StringIO()):
            self.memory = MemoryStore("./mcp_memory")
            self.hhni = HierarchicalIndex()
            self.seg = SEGraph()
        
        # Create agent
        self.agent = AetherAgent(
            llm_client=self.llm,
            memory_store=self.memory,
            index=self.hhni
        )
        
        self.log(f"Agent initialized with {self.llm.__class__.__name__}")
        self.log("Ready to receive MCP requests")
    
    def handle_request(self, request: dict) -> dict:
        """Handle an MCP request"""
        method = request.get("method")
        params = request.get("params", {})
        
        try:
            if method == "tools/list":
                return self.list_tools()
            elif method == "tools/call":
                return self.call_tool(params)
            elif method == "resources/list":
                return self.list_resources()
            elif method == "prompts/list":
                return self.list_prompts()
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
                    "name": "ask_agent",
                    "description": "Ask the conscious AI agent a question with full memory and learning",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "question": {
                                "type": "string",
                                "description": "The question to ask"
                            },
                            "context": {
                                "type": "string",
                                "description": "Optional additional context"
                            }
                        },
                        "required": ["question"]
                    }
                },
                {
                    "name": "retrieve_memory",
                    "description": "Search the agent's memory for relevant past interactions",
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
                    "name": "get_agent_stats",
                    "description": "Get statistics about the agent's memory and learning",
                    "inputSchema": {
                        "type": "object",
                        "properties": {}
                    }
                }
            ]
        }
    
    def list_resources(self) -> dict:
        """List available resources"""
        return {"resources": []}
    
    def list_prompts(self) -> dict:
        """List available prompts"""
        return {"prompts": []}
    
    def call_tool(self, params: dict) -> dict:
        """Call a tool"""
        tool_name = params.get("name")
        args = params.get("arguments", {})
        
        if tool_name == "ask_agent":
            question = args.get("question")
            context = args.get("context", "")
            
            # Process with agent (redirect stdout to prevent interference)
            with redirect_stdout(io.StringIO()):
                response = self.agent.process(question, context)
            
            return {
                "content": [
                    {
                        "type": "text",
                        "text": response.text
                    }
                ],
                "isError": False
            }
        
        elif tool_name == "retrieve_memory":
            query = args.get("query")
            limit = args.get("limit", 5)
            
            # Search HHNI (redirect stdout)
            with redirect_stdout(io.StringIO()):
                from hhni.models import IndexLevel
                results = self.hhni.query(query, target_level=IndexLevel.PARAGRAPH, max_results=limit)
            
            memories = [getattr(r, 'content', str(r)) for r in results[:limit]]
            
            return {
                "content": [
                    {
                        "type": "text",
                        "text": "\n\n".join(f"Memory {i+1}:\n{m}" for i, m in enumerate(memories))
                    }
                ],
                "isError": False
            }
        
        elif tool_name == "get_agent_stats":
            # Get memory stats (redirect stdout)
            with redirect_stdout(io.StringIO()):
                atoms = self.memory.list_atoms()
            
            stats = {
                "total_memories": len(atoms),
                "llm_provider": self.llm.__class__.__name__,
                "systems_active": ["CMC", "HHNI", "VIF", "SEG"]
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
        server = StdioMCPServer()
        server.run()
    except Exception as e:
        print(f"[MCP-STDIO] FATAL: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)
