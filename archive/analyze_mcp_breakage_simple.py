#!/usr/bin/env python3
import re
import os

print("=" * 80)
print("ANALYZING WHAT BROKE THE 16-TOOL MCP SERVER")
print("=" * 80)

# Read the cross-model server
with open("run_mcp_cross_model.py", 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

print("\n1. CHECKING FOR COMMON BREAKAGE PATTERNS:")
print("-" * 50)

# Check for import errors
imports = re.findall(r'^import\s+(\w+)', content, re.MULTILINE)
print(f"Imports found: {imports}")

# Check for missing dependencies
problematic_imports = []
for imp in imports:
    if imp in ['llm', 'memory_store', 'hhni', 'seg', 'apoe', 'vif']:
        problematic_imports.append(imp)

if problematic_imports:
    print(f"POTENTIAL ISSUE: Complex imports: {problematic_imports}")

# Check for environment variable dependencies
env_vars = re.findall(r'os\.environ\[[\'"]([^\'"]+)[\'"]\]', content)
if env_vars:
    print(f"ENVIRONMENT DEPENDENCIES: {env_vars}")

# Check for API key dependencies
api_keys = re.findall(r'API_KEY', content)
if api_keys:
    print(f"API KEY DEPENDENCIES: Found {len(api_keys)} references")

# Check for complex initialization
init_patterns = [
    'MemoryStore',
    'HHNI',
    'SEG',
    'APOE', 
    'VIF',
    'CrossModelConsciousness'
]

complex_init = []
for pattern in init_patterns:
    if pattern in content:
        complex_init.append(pattern)

if complex_init:
    print(f"COMPLEX INITIALIZATION: {complex_init}")

print("\n2. TOOLS AFTER THE 6TH (WHAT BREAKS IT?):")
print("-" * 50)

tools = [
    "store_memory",           # 1
    "get_memory_stats",       # 2  
    "retrieve_memory",        # 3
    "create_plan",           # 4
    "track_confidence",      # 5
    "synthesize_knowledge",  # 6
    "select_models",         # 7 - FIRST ADDITIONAL
    "extract_insights",      # 8
    "transfer_insights",     # 9
    "execute_task",          # 10
    "generate_witness",      # 11
    "calibrate_confidence",  # 12
    "replay_operation",      # 13
    "store_cross_model_atom", # 14
    "query_cross_model_atoms", # 15
    "get_cross_model_stats"   # 16
]

print("Tools 7-16 (the additions that might have broken it):")
for i in range(6, 16):
    tool = tools[i]
    if tool in content:
        print(f"  {i+1}. {tool} - Found")
    else:
        print(f"  {i+1}. {tool} - Missing")

print("\n3. DIAGNOSIS:")
print("-" * 50)

print("LIKELY BREAKING POINTS:")
print("1. Complex imports (LLM, MemoryStore, HHNI, etc.)")
print("2. API key dependencies")
print("3. Heavy initialization in __init__")
print("4. Tools 7+ require complex AIM-OS systems")
print("5. Environment variable issues")
print("6. Import path problems")

print("\nRECOMMENDATION:")
print("The 16-tool server is too complex for Cursor's MCP implementation.")
print("We need to either:")
print("1. Fix the complex dependencies")
print("2. Use the 6-tool version")
print("3. Create a simplified 16-tool version")
