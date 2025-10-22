# Modality Field - Content Type System

**Field of:** Atom (CMC Component)  
**Type:** Enum (string)  
**Purpose:** Classify what kind of content this atom contains  
**Status:** ✅ Fully Implemented

---

## 🎯 **Quick Context (50 words)**

Modality categorizes atom content: `text` (natural language), `code` (programming), `event` (system actions), `tool:call` (tool invocations), `tool:result` (tool outputs), `image`, `audio`. Enables filtering ("show me only code atoms"), modality-specific processing (code parsing vs text chunking), and appropriate rendering. Immutable once set.

**[More detail below ↓]**

---

## 📊 **Context Budget Guide**

**4k Context:** Read this README  
**8k Context:** Read [L1_overview.md](L1_overview.md) (all modalities explained)  
**32k Context:** Read [L2_specification.md](L2_specification.md) (implementation details)  
**200k+ Context:** Read L3-L5 for exhaustive documentation

---

## 📦 **Modality Values**

| Value | Purpose | Example |
|-------|---------|---------|
| `text` | Natural language | Documents, conversations, notes |
| `code` | Programming code | Functions, classes, scripts |
| `event` | System/user events | User login, file modified, error |
| `tool:call` | Tool invocation | API request, function call |
| `tool:result` | Tool output | API response, function return |
| `image` | Image data | Screenshots, diagrams, photos |
| `audio` | Audio data | Voice recordings, music |

---

## 🔧 **Implementation**

**File:** `packages/cmc_service/models.py`

```python
from enum import Enum

class Modality(str, Enum):
    TEXT = "text"
    CODE = "code"
    EVENT = "event"
    TOOL_CALL = "tool:call"
    TOOL_RESULT = "tool:result"
    IMAGE = "image"
    AUDIO = "audio"
```

**Usage:**
```python
atom = Atom(
    modality=Modality.CODE,
    content_ref=ContentRef(inline="def hello(): pass"),
    ...
)

# Filter by modality
code_atoms = query_atoms(filters={'modality': 'code'})
```

---

## 🔗 **Relationships**

**Modality affects:**
- **Atomization:** How content is split (code→functions, text→paragraphs)
- **HHNI Indexing:** Hierarchical path structure differs by modality
- **Rendering:** UI displays code with syntax highlighting, text as prose
- **Embeddings:** Some models specialized for code vs text

**Modality used by:**
- Write Pipeline (determines parsing strategy)
- HHNI Service (assigns appropriate hierarchical structure)
- Query Filters (modality-specific searches)
- UI Renderers (modality-appropriate display)

---

## 📚 **Detail Levels**

**L0 (This File):** Quick reference  
**L1:** [L1_overview.md](L1_overview.md) - All modalities with examples  
**L2:** [L2_specification.md](L2_specification.md) - Implementation guide  
**L3:** [L3_usage_patterns.md](L3_usage_patterns.md) - Common patterns  
**L4:** [L4_extension_guide.md](L4_extension_guide.md) - Adding new modalities

---

**Parent:** [../../README.md](../../README.md) (Atoms component)  
**Siblings:** [../content_ref/](../content_ref/), [../embedding/](../embedding/), [../tags/](../tags/)  
**Status:** ✅ Core field, production-ready  

**This demonstrates FULL FRACTAL recursion:** System → Component → Sub-Component → Field → Complete! 🌀

