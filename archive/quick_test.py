import sys
sys.path.insert(0, 'packages')

# Test the imports that the MCP server needs
try:
    from cmc_service import MemoryStore
    from hhni import HierarchicalIndex  
    from seg import SEGraph
    print("SUCCESS: All imports successful!")
    
    # Test initialization
    memory = MemoryStore("./mcp_memory")
    hhni = HierarchicalIndex()
    seg = SEGraph()
    print("SUCCESS: All systems initialized successfully!")
    
    print("SUCCESS: MCP server should work! Safe to test.")
    
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
