# API Key Management Strategy

**Date:** 2025-10-21  
**Issue:** API keys in committed files (security risk)  
**Solution:** Proper secret management  

---

## 🎯 **CURRENT PROBLEM**

**API keys found in:**
- `Testing/artifacts/API_KEY_STATUS.md`
- `ACTIVE_SPRINT_STATUS.md`

**Risk:**
- Exposed in git history
- Visible if repo made public
- GitHub security flagged them ✅
- **Need proper management**

---

## ✅ **PROPER SOLUTIONS**

### **Tier 1: Environment Variables (Development)**

**For local development:**

**Create `.env` file:**
```bash
# .env (gitignored)
GEMINI_API_KEY=[YOUR_GEMINI_KEY_HERE]
OPENAI_API_KEY=[YOUR_OPENAI_KEY_HERE]
ANTHROPIC_API_KEY_1=[YOUR_ANTHROPIC_KEY_1_HERE]
ANTHROPIC_API_KEY_2=[YOUR_ANTHROPIC_KEY_2_HERE]
CEREBRAS_API_KEY=[YOUR_CEREBRAS_KEY_HERE]
DEEPINFRA_API_KEY=[YOUR_DEEPINFRA_KEY_HERE]
REPLICATE_API_TOKEN=[YOUR_REPLICATE_TOKEN_HERE]
XAI_API_KEY=[YOUR_XAI_KEY_HERE]
HUGGINGFACE_TOKEN=[YOUR_HUGGINGFACE_TOKEN_HERE]
```

**Update .gitignore:**
```bash
# Already has Python excludes, add:
.env
.env.*
*.key
secrets/
```

**Use in code:**
```python
import os
from dotenv import load_dotenv  # pip install python-dotenv

load_dotenv()

gemini_key = os.getenv("GEMINI_API_KEY")
openai_key = os.getenv("OPENAI_API_KEY")
```

**Benefits:**
- ✅ Never in git
- ✅ Local development easy
- ✅ Industry standard
- ✅ Simple

**Drawbacks:**
- 🟡 Each developer needs own .env
- 🟡 Not shared across team
- 🟡 Manual distribution

---

### **Tier 2: Supabase (Team Sharing) - YOUR SUGGESTION ✅**

**You have Supabase access:**
- URL: `https://kyxzymgdmrgbxlkpcoqf.supabase.co`
- JWT: (you provided earlier)

**Setup:**

**1. Create secrets table in Supabase:**
```sql
-- In Supabase SQL editor
CREATE TABLE api_keys (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    provider TEXT NOT NULL,
    key_name TEXT NOT NULL,
    key_value TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP,
    active BOOLEAN DEFAULT TRUE,
    metadata JSONB
);

-- Row-level security
ALTER TABLE api_keys ENABLE ROW LEVEL SECURITY;

-- Policy: Only authenticated users can read
CREATE POLICY "Authenticated users can read keys"
    ON api_keys FOR SELECT
    TO authenticated
    USING (true);
```

**2. Store keys in Supabase:**
```python
# scripts/store_keys_in_supabase.py
from supabase import create_client

supabase = create_client(
    "https://kyxzymgdmrgbxlkpcoqf.supabase.co",
    "YOUR_ANON_KEY"
)

# Store each key
supabase.table('api_keys').insert({
    'provider': 'gemini',
    'key_name': 'GEMINI_API_KEY',
    'key_value': 'AIzaSyA9S1wx...',
    'metadata': {'purpose': 'Primary LLM', 'budget': '$300 trial'}
}).execute()

# Repeat for each provider
```

**3. Retrieve in code:**
```python
# packages/llm_manager/key_manager.py
class KeyManager:
    def __init__(self):
        self.supabase = create_client(supabase_url, supabase_key)
    
    def get_key(self, provider: str) -> str:
        result = self.supabase.table('api_keys')\
            .select('key_value')\
            .eq('provider', provider)\
            .eq('active', True)\
            .single()\
            .execute()
        
        return result.data['key_value']

# Usage:
key_mgr = KeyManager()
gemini_key = key_mgr.get_key('gemini')
```

**Benefits:**
- ✅ Centralized storage
- ✅ Team can share
- ✅ Remote access (any machine)
- ✅ Can rotate keys easily
- ✅ Audit trail (who accessed when)
- ✅ **Professional grade** 🌟

**Drawbacks:**
- 🟡 Requires network access
- 🟡 Setup time (20-30 min)
- 🟡 Dependency on Supabase

---

### **Tier 3: Vault / AWS Secrets Manager (Production)**

**For future/production:**
- HashiCorp Vault
- AWS Secrets Manager
- Azure Key Vault
- Google Secret Manager

**Benefits:** Enterprise-grade  
**Drawbacks:** Overkill for now  

---

## 🎯 **IMMEDIATE FIX (To Push to GitHub)**

**Two-step approach:**

### **Step 1: Redact from Git History (NOW)**

**Quick fix:**
```bash
# Remove API keys from the problematic files
# Replace with placeholders
```

**Files to fix:**
1. `Testing/artifacts/API_KEY_STATUS.md` (lines 36, 171, 173)
2. `ACTIVE_SPRINT_STATUS.md` (line 1381)

**Replace keys with:**
```
[REDACTED - Stored in environment variables / Supabase]
```

**Then:**
```bash
git add Testing/artifacts/API_KEY_STATUS.md ACTIVE_SPRINT_STATUS.md
git commit -m "security: redact API keys from documentation"
git push -u origin feature/phase-2-hhni
```

---

### **Step 2: Setup Proper Management (Next Session)**

**Use Supabase (your suggestion is good!):**

**Benefits for AIM-OS:**
- ✅ You already have Supabase
- ✅ Fits AIM-OS architecture (remote storage)
- ✅ Can integrate with CMC later
- ✅ Team-friendly
- ✅ Can track key usage

**Implementation:**
```python
# packages/key_manager/
#   __init__.py
#   supabase_store.py  - Supabase integration
#   env_store.py       - Fallback to .env
#   manager.py         - Unified interface

class KeyManager:
    """
    Unified API key management.
    
    Priority:
    1. Supabase (if available)
    2. Environment variables
    3. Raise error
    """
    
    def get_key(self, provider: str) -> str:
        # Try Supabase first
        if self.supabase_available:
            return self.supabase_store.get(provider)
        
        # Fallback to env
        return os.getenv(f"{provider.upper()}_API_KEY")
```

**Then use everywhere:**
```python
# Instead of hardcoded keys
from packages.key_manager import KeyManager

key_mgr = KeyManager()
gemini_key = key_mgr.get_key('gemini')
```

---

## 🚀 **RECOMMENDED APPROACH**

### **Today (Immediate):**
1. I redact keys from 2 files (5 min)
2. Commit redaction
3. Push to GitHub (succeeds)
4. **Backup complete** ✅

### **Tomorrow (Proper Setup - 30 min):**
1. Create .env file with all keys
2. Update .gitignore to exclude .env
3. Optionally: Setup Supabase key storage
4. Build KeyManager class
5. Update code to use KeyManager
6. **Professional secret management** ✅

### **Future (Production):**
1. Supabase as primary key store
2. Environment variables as fallback
3. Key rotation support
4. Usage tracking
5. **Enterprise-grade** 🌟

---

## 🎯 **IMMEDIATE ACTION**

**Should I:**

**Option 1:** Redact keys from files now, push to GitHub (5 min)  
**Option 2:** You use GitHub's bypass URLs (2 min, but keys stay exposed)  
**Option 3:** Different approach?

**My recommendation: Option 1 (redact keys)**

**Then separately (later):**
- Setup proper .env + Supabase management
- Build KeyManager class
- Professional secret handling

---

**Your Supabase idea is EXCELLENT for production!**  
**But for immediate GitHub push, just need to redact.** ✅

**Proceed with redaction?** 🎯

