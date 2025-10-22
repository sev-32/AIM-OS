# ContentRef Field - Payload Storage Abstraction

**Field of:** Atom  
**Type:** Pydantic Model  
**Purpose:** Store content inline or reference external storage  
**Status:** ✅ Fully Implemented

---

## 🎯 **Quick Context (50 words)**

ContentRef handles atom payload storage: inline (<1KB) or external (URI). Includes media type, size, and SHA-256 hash. Enables lazy loading, deduplication, and scalability. Validation ensures exactly one of inline/uri is set. Immutable once created. Critical for efficient storage and content addressing.

---

## 📦 **Fields**

| Field | Type | Purpose |
|-------|------|---------|
| `inline` | Optional[str] | Small content embedded directly |
| `uri` | Optional[str] | External reference (s3://, file://) |
| `media_type` | str | MIME type (text/plain, application/json) |
| `size_bytes` | Optional[int] | Content size in bytes |
| `hash_sha256` | Optional[str] | Content integrity hash |

**Constraint:** Exactly one of `inline` or `uri` must be set (XOR)

---

## 🔧 **Implementation**

```python
class ContentRef(BaseModel):
    inline: Optional[str] = None
    uri: Optional[str] = None
    media_type: str = "text/plain"
    size_bytes: Optional[int] = None
    hash_sha256: Optional[str] = None
    
    @validator('inline', 'uri')
    def exactly_one_set(cls, v, values):
        if values.get('inline') and v:
            raise ValueError("Cannot set both")
        if not values.get('inline') and not v:
            raise ValueError("Must set one")
        return v
    
    def get_content(self, object_store) -> str:
        if self.inline:
            return self.inline
        return object_store.get(self.uri)
```

---

## 📊 **Storage Strategy**

**Decision Tree:**
```
Content size < 1KB → Inline
Content size ≥ 1KB → External (object store)
```

**Benefits:**
- Inline: Fast access, no external dependency
- External: Scalability, deduplication via hash

---

**Parent:** [../../README.md](../../README.md)  
**Detail Levels:** L1-L4 (to be created)

