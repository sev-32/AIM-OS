# Deterministic Replay

**Type:** VIF Component  
**Purpose:** Reproduce exact outputs for debugging/auditing  
**Status:** 25% Implemented

---

## 🎯 **Quick Context (50 words)**

Deterministic replay enables bit-identical reproduction of AI outputs. Store replay seed, exact context snapshot (CMC), prompt hash, model version in VIF witness. To replay: Use same seed + context + prompt → identical output! Enables debugging ("why did it do that?"), auditing (verify claims), regression testing (outputs stable?).

---

## 📊 **Context Budget**

**2k:** This README  
**4k:** L1_overview.md  
**16k:** L2_architecture.md

---

## 📦 **How Replay Works**

**Recording Phase:**
```python
def generate_with_replay(prompt: str, context: List[str]) -> Tuple[str, VIF]:
    """Generate output with replay capability"""
    
    # Set deterministic seed
    replay_seed = random.randint(0, 2**32)
    set_seed(replay_seed)
    
    # Create context snapshot (CMC)
    snapshot = create_snapshot(context)
    
    # Generate output (deterministic!)
    output = model.generate(
        prompt=prompt,
        temperature=0.0,  # Deterministic
        seed=replay_seed
    )
    
    # Create witness
    vif = VIF(
        model_id=model.id,
        context_snapshot_id=snapshot.id,
        prompt_hash=sha256(prompt),
        replay_seed=replay_seed,
        temperature=0.0,
        created_at=datetime.utcnow()
    )
    
    return output, vif
```

**Replay Phase:**
```python
def replay_from_vif(vif: VIF) -> str:
    """Reproduce exact output from witness"""
    
    # Load exact context
    snapshot = load_snapshot(vif.context_snapshot_id)
    context = snapshot.get_atoms()
    
    # Load exact prompt (verify hash)
    prompt = load_prompt(vif.prompt_hash)
    
    # Set same seed
    set_seed(vif.replay_seed)
    
    # Generate (should be identical!)
    output = model.generate(
        prompt=prompt,
        temperature=vif.temperature,
        seed=vif.replay_seed
    )
    
    return output  # Bit-identical to original!
```

---

## 🔧 **Implementation**

**Status:** 25% implemented

**Working:**
- ✅ Basic seed tracking

**Needed:**
- 🔄 Context snapshot integration (CMC)
- 🔄 Prompt hash verification
- 🔄 Model version pinning
- 🔄 Replay validation tests

**Code:** (Partial in `packages/seg/witness.py`)

---

**Parent:** [../../README.md](../../README.md)  
**Status:** Week 4 target

