# Graph Schema

**Type:** SEG Component  
**Purpose:** Define nodes and edges for evidence graph  
**Status:** 30% Implemented

---

## 🎯 **Quick Context (50 words)**

Graph schema defines SEG's structure: 4 node types (Claim, Source, Derivation, Agent) and 5 edge types (supports, contradicts, derives, witnesses, cites). Every piece of evidence becomes a typed node, every relationship becomes a typed edge. Foundation for queryable, traceable, contradiction-aware knowledge representation.

---

## 📦 **Node Types**

### **1. Claim**
**What:** Factual assertion (evidence)  
**Example:** "OAuth2 uses JWT tokens"  
**Fields:** content, confidence, created_at, valid_from, valid_to

### **2. Source**
**What:** Origin of evidence  
**Example:** VIF witness, document, user input  
**Fields:** vif_id, document_path, creator

### **3. Derivation**
**What:** How claim was derived  
**Example:** APOE execution trace, inference chain  
**Fields:** plan_id, inputs, outputs, reasoning

### **4. Agent**
**What:** Who/what created claim  
**Example:** Human user, AI model, system component  
**Fields:** agent_type, model_id, user_id

---

## 📦 **Edge Types**

### **1. supports**
Evidence backs up claim  
**Example:** Source S → supports → Claim C

### **2. contradicts**
Evidence conflicts with claim  
**Example:** Claim C1 ← contradicts → Claim C2

### **3. derives**
Claim produced from others  
**Example:** Derivation D → derives → Claim C

### **4. witnesses**
VIF records claim  
**Example:** Source (VIF) → witnesses → Claim

### **5. cites**
Reference to source  
**Example:** Claim → cites → Source

---

## 🔧 **Implementation**

**Status:** 30% implemented

**Working:**
- ✅ Basic node/edge creation
- ✅ JSONL storage

**Needed:**
- 🔄 Full schema validation
- 🔄 Type enforcement
- 🔄 Graph database (Neo4j)

**Code:** `packages/seg/`

---

**Parent:** [../../README.md](../../README.md)

