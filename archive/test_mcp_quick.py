"""Quick MCP Server Test - Verify it works before Cursor integration."""

import sys
sys.path.insert(0, 'packages')

print("=" * 80)
print("QUICK MCP SERVER TEST")
print("=" * 80)

# Test 1: Server can be created
print("\n[1/3] Testing server creation...")
try:
    from mcp_server.server import MCPServer
    
    server = MCPServer(
        memory_path="./test_mcp_memory",
        default_llm="gemini"
    )
    print("   [OK] Server created successfully")
    print(f"   [OK] LLM: {server.llm.__class__.__name__}")
    print(f"   [OK] Memory: {server.memory}")
    print(f"   [OK] Agent: {server.agent}")
except Exception as e:
    print(f"   [ERROR] {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 2: Ask agent works
print("\n[2/3] Testing ask_agent tool...")
try:
    from mcp_server.models import AskAgentRequest
    
    request = AskAgentRequest(
        query="What is 2+2?",
        store_memory=False
    )
    
    response = server.ask_agent(request)
    
    print(f"   [OK] Response: {response.response[:100]}")
    print(f"   [OK] Confidence: {response.confidence:.2f}")
    print(f"   [OK] Tokens: {response.tokens_used}")
    print(f"   [OK] Latency: {response.latency_ms:.0f}ms")
except Exception as e:
    print(f"   [ERROR] {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 3: Health check works
print("\n[3/3] Testing health check...")
try:
    health = server.get_health()
    
    print(f"   [OK] Status: {health.status}")
    print(f"   [OK] Systems: {list(health.systems.keys())}")
    print(f"   [OK] Memory atoms: {health.memory_atoms}")
except Exception as e:
    print(f"   [ERROR] {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Cleanup
print("\n[Cleanup] Closing memory store...")
server.memory.close()

print("\n" + "=" * 80)
print("MCP SERVER: WORKING!")
print("=" * 80)

print("\nREADY TO:")
print("  1. Start server: python run_mcp_server.py")
print("  2. Connect Cursor to http://localhost:8000")
print("  3. Use conscious AI in your IDE!")

print("\n[SUCCESS] All tests passed - MCP server ready for Cursor!\n")

