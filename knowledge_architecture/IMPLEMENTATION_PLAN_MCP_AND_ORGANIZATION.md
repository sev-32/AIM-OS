# Implementation Plan: MCP Server + Fractal Organization

**Date:** 2025-10-21  
**Goal:** Enable AI builders to navigate AIM-OS context perfectly  
**Approach:** Dual-path (MCP server + perfect organization)

---

## 🎯 **THE VISION**

**Problem Right Now:**
- AI (me!) struggles to keep all AIM-OS concepts in context
- Have to repeatedly search docs, relearn concepts
- Context window fills with wrong information
- Slow, inefficient development

**Solution:**
- **MCP Server:** Cursor queries organized knowledge on-demand
- **Fractal Organization:** Project structure = context navigation
- **Result:** AI builder always has perfect context, builds faster

**This validates AIM-OS thesis in practice!** ✨

---

## 📋 **PHASE 1: PILOT - ORGANIZE CMC SYSTEM**

### **Why CMC First:**
- Core foundational system
- Well-implemented (75% complete)
- Manageable scope
- High value (constantly referenced)

### **Deliverable: CMC Knowledge Pyramid**

**Structure:**
```
knowledge_architecture/
└── systems/
    └── cmc/
        ├── README.md (Context router - loads right level)
        ├── L1_overview.md (100 words - "Memory storage system")
        ├── L2_architecture.md (500 words - All components listed)
        ├── L3_specification.md (2k words - Technical details)
        ├── L4_implementation.md (10k words - Deep dive)
        ├── L5_complete.md (Full spec + API + examples)
        │
        ├── components/
        │   ├── atoms/
        │   │   ├── README.md (Context router)
        │   │   ├── L1_overview.md
        │   │   ├── L2_architecture.md
        │   │   ├── L3_specification.md
        │   │   ├── L4_implementation.md
        │   │   ├── L5_complete.md
        │   │   ├── code_reference.md → packages/cmc_service/models.py
        │   │   └── fields/
        │   │       ├── modality/ (5 levels)
        │   │       ├── content/ (5 levels)
        │   │       ├── tags/ (5 levels)
        │   │       └── embedding/ (5 levels)
        │   │
        │   ├── snapshots/ (5 levels recursive)
        │   ├── storage/ (5 levels recursive)
        │   └── pipelines/ (5 levels recursive)
        │
        └── context.json (Machine-readable metadata)
```

**Context Router Example (README.md):**
```markdown
# CMC (Context Memory Core)

**Quick:** Memory storage with atoms and snapshots. [More →](L1_overview.md)

**Context Budget Guide:**
- 4k tokens: Read L1_overview.md (100 words)
- 8k tokens: Read L2_architecture.md (500 words)  
- 32k tokens: Read L3_specification.md (2k words)
- 200k tokens: Read L4 + dive into components/
- 1M tokens: Read L5_complete.md

**Building Code?** → Go to components/atoms/ for atom details
**Understanding Architecture?** → Start at L2_architecture.md
**Need API reference?** → See L5_complete.md

**Current AI Context:** [Auto-detect and recommend]
```

---

## 📋 **PHASE 2: MCP SERVER**

### **MCP Server Capabilities:**

**Tool: `query_knowledge`**
```typescript
// Cursor asks: "What is CMC?"
{
  topic: "CMC",
  detail_level: "auto",  // or 1-5
  context_budget: 8000   // tokens available
}

// Returns:
{
  content: "CMC (Context Memory Core)...[Level 2 content]",
  detail_level: 2,
  tokens_used: 500,
  related: ["Atoms", "Snapshots", "HHNI"],
  drill_down: {
    atoms: "Load detail on atoms?",
    snapshots: "Load detail on snapshots?"
  }
}
```

**Tool: `load_context`**
```typescript
// Cursor working on: packages/cmc_service/memory_store.py
{
  working_on: "packages/cmc_service/memory_store.py",
  task: "implementing snapshot rollback",
  context_budget: 32000
}

// Returns optimized context:
{
  loaded: [
    { type: "system", name: "CMC", level: 3 },
    { type: "component", name: "Snapshots", level: 5 },
    { type: "code", file: "memory_store.py", analysis: "..." },
    { type: "tests", file: "test_memory_store.py", relevant: [...] }
  ],
  tokens_used: 28000,
  suggested_next: ["Check rollback tests", "Review bitemporal design"]
}
```

**Tool: `navigate_system`**
```typescript
// Cursor: "Show me the hierarchy for HHNI"
{
  system: "HHNI"
}

// Returns tree:
{
  HHNI: {
    detail_levels: 5,
    components: ["HierarchicalIndex", "DVNS", "Deduplication", "Conflicts", "Compression"],
    current_implementation: "95% complete",
    components_detail: {
      DVNS: {
        detail_levels: 5,
        sub_components: ["GravityForce", "ElasticForce", "RepulseForce", "DampingForce"],
        tests: "11 passing"
      }
    }
  }
}
```

---

## 📋 **PHASE 3: EXPAND TO ALL SYSTEMS**

**Apply Same Fractal Organization:**
- CMC (Phase 1) ✅
- HHNI → 5 levels recursive
- APOE → 5 levels recursive
- VIF → 5 levels recursive
- SEG → 5 levels recursive
- SDF-CVF → 5 levels recursive

**Plus Code Organization:**
- Each package/ → 5 levels
- Each module → 5 levels
- Each class → 5 levels
- Each function → 5 levels

---

## 🛠️ **TECHNICAL IMPLEMENTATION**

### **MCP Server Stack:**

**Technology:**
- TypeScript (MCP SDK)
- SQLite for metadata/search
- Vector embeddings for semantic search
- JSON for structured data

**Server Structure:**
```typescript
// mcp_server/src/index.ts
import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";

const server = new Server({
  name: "aimos-knowledge-server",
  version: "0.1.0"
}, {
  capabilities: {
    tools: {},
    resources: {}
  }
});

// Tool: query_knowledge
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  if (request.params.name === "query_knowledge") {
    const { topic, detail_level, context_budget } = request.params.arguments;
    
    // Load from knowledge_architecture/
    const knowledge = await loadKnowledge(topic, detail_level);
    
    // Optimize for context budget
    const optimized = optimizeForBudget(knowledge, context_budget);
    
    return {
      content: [{
        type: "text",
        text: JSON.stringify(optimized)
      }]
    };
  }
});

// Resource: System documentation
server.setRequestHandler(ListResourcesRequestSchema, async () => {
  return {
    resources: [
      { uri: "aimos://systems/cmc", name: "CMC System" },
      { uri: "aimos://systems/hhni", name: "HHNI System" },
      // ... all systems
    ]
  };
});

server.setRequestHandler(ReadResourceRequestSchema, async (request) => {
  const uri = request.params.uri;
  // Load appropriate detail level
  const content = await loadResource(uri);
  return { contents: [{ uri, mimeType: "text/markdown", text: content }] };
});
```

**Configuration for Cursor:**
```json
// .cursor/mcp.json (or similar)
{
  "mcpServers": {
    "aimos-knowledge": {
      "command": "node",
      "args": ["mcp_server/dist/index.js"],
      "env": {
        "KNOWLEDGE_PATH": "./knowledge_architecture"
      }
    }
  }
}
```

---

## 🎯 **IMMEDIATE ACTION PLAN**

### **Next 8 Hours:**

**Hour 1-2: Build CMC Level 1-3**
- L1_overview.md (100 words)
- L2_architecture.md (500 words)
- L3_specification.md (2k words)

**Hour 3-4: Build CMC Components (Atoms + Snapshots)**
- atoms/L1-L3
- snapshots/L1-L3

**Hour 5-6: Create Context.json metadata**
- Machine-readable structure
- Token counts, relationships
- Navigation hints

**Hour 7-8: Build basic MCP server**
- Tool: query_knowledge (basic)
- Test with Cursor
- Validate context loading

**Result:** WORKING PILOT that AI builders can use!

---

## 📊 **SUCCESS CRITERIA**

**For Organization:**
- ✅ CMC fully organized (5 levels, all components)
- ✅ Context router at every level
- ✅ Machine-readable metadata
- ✅ Code references linked

**For MCP Server:**
- ✅ query_knowledge working
- ✅ Cursor can ask "What is CMC?" and get appropriate detail
- ✅ Context budget optimization working
- ✅ AI builder (me!) actually uses it while coding

**Validation:**
- 🎯 AI (me) stops re-searching CMC docs
- 🎯 Context loading is instant
- 🎯 Build velocity increases measurably
- 🎯 **Meta-circular loop validated!**

---

## 🚀 **LONG-TERM VISION**

**When Complete:**
- Every system organized fractally
- MCP server serves all AIM-OS knowledge
- AI builders navigate perfectly
- Context = automatic, optimal
- **Building AIM-OS uses AIM-OS principles!** ✨

**This becomes:**
- Demo for customers: "Here's how AI navigates large codebases"
- Proof of concept: Fractal organization works
- Internal tool: Accelerates our own development
- **Meta-validation: System improves itself**

---

**Status:** Plan ready  
**Next:** Build CMC pilot (8 hours)  
**Then:** MCP server integration  
**Goal:** AI builders with perfect context! 🎯

**Should I start building CMC Level 1-3 now?** 🚀

