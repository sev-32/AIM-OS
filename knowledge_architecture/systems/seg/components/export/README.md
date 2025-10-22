# Export System

**Type:** SEG Component  
**Purpose:** Export graph to standard formats (JSON-LD, RDF, SHACL)  
**Status:** 30% Implemented

---

## 🎯 **Quick Context (50 words)**

Export system converts SEG to W3C-standard formats: JSON-LD (linked data), RDF (triple store), SHACL (shape validation). Enables interoperability with external knowledge graphs, semantic web tools, compliance systems. Export preserves full provenance, temporal data, and graph structure. Foundation for standards-compliant knowledge sharing.

---

## 📦 **Export Formats**

### **1. JSON-LD**
**Standard:** W3C Linked Data  
**Use:** Web-compatible knowledge representation  
**Output:**
```json
{
  "@context": "https://aimos.org/seg/context",
  "@type": "Claim",
  "@id": "claim:c123",
  "content": "OAuth2 uses JWT tokens",
  "created": "2025-10-21T10:00:00Z",
  "validFrom": "2025-10-21T10:00:00Z",
  "witnesses": [{"@id": "vif:w456"}]
}
```

### **2. RDF**
**Standard:** Resource Description Framework  
**Use:** Triple store compatibility (Stardog, GraphDB)  
**Output:**
```turtle
:claim:c123 rdf:type :Claim ;
           :content "OAuth2 uses JWT tokens" ;
           :created "2025-10-21T10:00:00Z"^^xsd:dateTime ;
           :witnesses :vif:w456 .
```

### **3. SHACL**
**Standard:** Shapes Constraint Language  
**Use:** Graph validation (ensure integrity)  
**Output:**
```turtle
:ClaimShape a sh:NodeShape ;
  sh:targetClass :Claim ;
  sh:property [
    sh:path :content ;
    sh:minCount 1 ;
    sh:datatype xsd:string
  ] .
```

---

## 🔧 **Implementation**

**Status:** 30% implemented

**Working:**
- ✅ Basic JSONL export

**Needed:**
- 🔄 JSON-LD with @context
- 🔄 RDF serialization
- 🔄 SHACL validation schemas
- 🔄 Round-trip testing (export → import → verify)

**Code:** `packages/seg/` (partial)

---

**Parent:** [../../README.md](../../README.md)

