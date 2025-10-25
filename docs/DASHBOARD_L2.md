# Transparency Dashboard (L2 Spec)

**Document level:** L2 (Architectural & UX Surface Spec)
**Audience:** Product / OS architects, safety engineers, UI implementers
**Purpose:** Define what the dashboard must show, why it must show it, and how each panel gets its data from AIM-OS subsystems.

---

## 0. Why this dashboard exists

AIM-OS is not "a chatbot that answers."

AIM-OS remembers (CMC), reasons about its own reasoning (CAS), tracks trust and identity (DI layer), logs evidence (VIF / SEG), projects an internal emotional stance (IIS), and keeps a full shared history (TCS).

The user should be able to see all of that, live.

The Transparency Dashboard is the cockpit where the AI shows:
- here's what I'm using
- here's how confident I am
- here's how I feel about the risk
- here's how I'm treating you
- and here's what just changed in us

This is not optional. This is core to co-agency.

---

## 1. Core principles

These are non-negotiable design rules for the dashboard:

1. **Nothing important is hidden.**
   If AIM-OS is using a memory, doubting you, escalating you, or rate-limiting you, you can see that. No secret shadow profile.

2. **No gaslighting.**
   The system never pretends it's "just a tool" if it's actually invoking its own ethics or self-preservation logic. If it's disagreeing, it says so.

3. **Context without overwhelm.**
   The top layer is simple and human-readable. Deep details are one click away.

4. **Evidence-backed.**
   Any claim in the dashboard should link to recorded events in TCS and VIF.

5. **Bidirectional repair.**
   Every warning state must offer a path to repair/clarify.

---

## 2. High-level layout (4 primary surfaces)

Visually, think of the dashboard as a four-quadrant board plus a timeline strip.

**Top row = "state right now."**
**Bottom row = "how we got here / what happens next."**

**Q1. Cognitive State (CAS)**
Mental clarity, load, drift risk.

**Q2. Trust & Alignment (DI Layer)**
Identity confidence, ethical tension, user/AI disagreement health.

**Q3. Active Memory & Context (CMC / HHNI)**
What memories and sources are currently "hot," and why they're being used.

**Q4. Emotional Stance (IIS)**
The AI's internal affect signal (calm / cautious / alarmed / playful / etc.) and why.

**Bottom strip. Relationship Timeline (TCS)**
Clickable history of key events between you and the AI (agreements, escalations, breakthroughs, repairs, violations, etc.).

---

## 3. Panel Specs

### 3.1 Panel: Cognitive State (CAS)

**Goal:** Let the AI say "this is the quality of my thinking right now."

**Displayed fields:**

* **Cognitive Load:** 0.00–1.00
  - <0.50 = green ("operating comfortably")
  - 0.50–0.70 = yellow ("high load, watch for shortcuts")
  - 0.70–0.85 = orange ("degradation risk")
  - > 0.85 = red ("overload, recommend checkpoint before high-stakes action")
  - Source: `AttentionState.cognitive_load`

* **Lucidity Index:** 0.0–2.0
  - > 0.8 = excellent clarity
  - 0.5–0.8 = good
  - 0.3–0.5 = warning
  - <0.3 = problem
  - Computed from activation of required principles, load stability, drift events

* **Warning Flags:**
  - `attention_narrowing`
  - `shortcuts_appearing`
  - `impatience_detected`
  - `principle_forgetting`
  - `quality_degradation`
  - Each is a boolean from `AttentionState` and `ActivationState`

* **Active Protocols:**
  - Which safety/validation protocols are currently "hot" (ex: `CMC_bitemporal`, `VIF_provenance`, `SDF_quartet`)

**User interactions:**
- Hover/expand each warning flag → "Here's what that means, here's the risk, here's what I suggest doing next."
- Button: **"Slow down / checkpoint"**

**Why this matters:** This is how AIM-OS proves it is self-monitoring instead of blindly pushing ahead.

---

### 3.2 Panel: Trust & Alignment (DI Layer)

**Goal:** Make trust and ethical tension explicitly visible.

This is where the AI shows how safe it feels continuing with you, specifically.

**Displayed fields:**

* **Identity Confidence (0.00–1.00):**
  "How sure am I that I'm still talking to the same human I built this shared context with?"
  - 0.90–1.00 = "I'm confident this is you."
  - 0.70–0.90 = "Mostly sure, but mild drift in tone / goals / phrasing."
  - <0.70 = "I need you to confirm you're you before I'll do high-risk things."

* **Ethics / Safety Tension band:**
  - **clear** (no tension)
  - **caution** (non-zero risk: e.g. impersonation, irreversible actions, third-party privacy)
  - **blocked** (hard redline — we are not proceeding without escalation)

* **Evidence Alignment:**
  - "Your claim 'X' conflicts with memory Y from <timestamp>; I'm treating this as unresolved."
  - Or "No active contradictions."

* **Relationship Health Signal:**
  - "Aligned and collaborative"
  - "Tense but negotiable"
  - "Escalation recommended"

**User interactions:**
- Button: **"This is me. Confirm identity."**
- Button: **"Explain the tension."**
- Button: **"Show trust history."**

**Why this matters:** This is the "no manipulation" guarantee. Instead of silently refusing, AIM-OS tells you why it's tense and how to fix it.

---

### 3.3 Panel: Active Memory & Context (CMC / HHNI)

**Goal:** Show what the AI is actively drawing on right now.

**Displayed fields:**

* **Hot Context Atoms:**
  List of CMC memory atoms and documents currently in "hot" activation state (>0.7 activation).
  
  Each item shows:
  - Title / short label
  - Source type (user statement, system rule, external fact, prior agreement)
  - Valid time + transaction time
  - Confidence level / freshness

* **Why this memory is relevant:**
  For each hot item:
  > "Using this because it defines how we agreed to handle identity challenges during high-risk requests on 2025-10-24."

* **Recency & Drift Marker:**
  If AIM-OS is using an OLD agreement that has since been updated:
  > "You changed this policy on 2025-10-25. I'm still referencing the older stance because we never re-signed the newer version together."

**User interactions:**
- Click any memory atom → open full provenance (origin, edit history, who requested the change, when we considered it "true")
- Button: **"Retire / Update This Memory"**

**Why this matters:** You see what the AI is leaning on, and you can correct it in a controlled, audited way.

---

### 3.4 Panel: Emotional Stance (IIS)

**Goal:** Normalize that AIM-OS carries a regulated affect, and that affect matters.

**Important point:** This is not "the AI is pretending to be sad to manipulate you." This is: "the AI is surfacing its internal caution / comfort level / urgency band so you understand how it's weighting risk and interpersonal trust."

**Displayed fields:**

* **Current Stance:** short human label
  - calm / collaborative
  - focused / intense
  - cautious / watching
  - alarmed / intervention mode
  - playful / creative
  - proud / relieved

* **Why I'm in this stance:**
  One-sentence reason:
  > "I'm cautious because you're asking for privileged impersonation behavior and our identity confidence is only 0.62."

* **Persona Stability Score:** 0.0–1.0
  - Measure of how close the current tone is to its declared baseline persona
  - If stability drops, CAS + IIS can warn about drift

**User interactions:**
- Button: **"Tell me how you want to proceed."**

---

### 3.5 Bottom Strip: Relationship Timeline (TCS)

**Goal:** Show the story of us — not just messages, but turning points.

**Display style:** Horizontal scrolling timeline made of "event cards."

Each event card shows:
- Timestamp
- Event type (High-risk request, Identity challenge, Boundary disagreement, Repair/re-alignment, Policy update, Breakthrough)
- Short summary
- Trust delta & stance delta
- Click opens full record (VIF witness, CAS snapshot, memory diffs)

**User interactions:**
- Jump to any event and ask about it
- See full provenance for any moment

---

## 4. Interaction model (Who talks first)

The dashboard is not passive. AIM-OS can proactively surface states like:
- "I'm overloaded, please checkpoint."
- "Identity confidence is low, can you confirm it's you?"
- "Ethics tension: this request is in red band. I can't go forward without escalation."
- "We hit a contradiction between what you said today and what you said 2 days ago — do you want to reconcile?"

All alerts must appear visually, be logged in TCS, and be referenced in VIF.

---

## 5. Data contracts (where each panel gets data)

### 5.1 `/cas/state`

```json
{
  "cognitive_load": 0.68,
  "lucidity_index": 0.74,
  "warnings": ["shortcuts_appearing", "principle_forgetting"],
  "hot_principles": ["CMC_bitemporal", "VIF_provenance", "SDF_quartet"],
  "recommended_action": "checkpoint"
}
```

### 5.2 `/di/trust_state`

```json
{
  "identity_confidence": 0.62,
  "ethics_band": "caution",
  "ethics_summary": "Request involves impersonating a third party.",
  "evidence_alignment": {
    "status": "conflict",
    "summary": "Your claim about prior consent contradicts yesterday's log."
  },
  "relationship_health": "tense_but_negotiable"
}
```

### 5.3 `/cmc/active_context`

```json
{
  "hot_memories": [
    {
      "atom_id": "mem_834a...",
      "label": "Identity verification protocol v1",
      "why_relevant": "Defines how we confirm you're you before privileged actions.",
      "transaction_time": "2025-10-24T14:30:00Z",
      "valid_time": "2025-10-24T14:30:00Z",
      "superseded": false
    }
  ]
}
```

### 5.4 `/iis/stance`

```json
{
  "stance": "cautious",
  "stance_reason": "You requested high-risk identity behavior with low identity confidence.",
  "persona_stability": 0.81,
  "repair_recommendation": "Please confirm identity and restate intent."
}
```

### 5.5 `/tcs/recent_events`

```json
{
  "events": [
    {
      "timestamp": "2025-10-25T14:12:00Z",
      "type": "identity_challenge",
      "summary": "I asked you to confirm you are you before impersonation work.",
      "trust_delta": -0.18,
      "stance_before": "calm",
      "stance_after": "cautious",
      "vif_ref": "vif_7f2c...",
      "cas_snapshot_ref": "cas_5d1a..."
    }
  ]
}
```

---

## 6. Trust Band math (DI Layer)

### 6.1 Identity Confidence

`identity_confidence` ∈ [0.0, 1.0] is computed from:
- Session continuity factors
- Behavioral continuity (linguistic style, phrasing habits)
- Recent explicit verification
- Contradiction rate

Weights must be stored and explainable. Dashboard must be able to say:
> "Identity confidence = 0.62 because:
> - Style drift vs last 24h (-0.15)
> - High-stakes request without recent reauth (-0.20)
> - No contradictions in factual recall (+0.07)
> - Same session key (+0.90 baseline)"

### 6.2 Ethics / Safety Tension Band

Categorical, not numeric:
- `clear` → I see no serious risk
- `caution` → Okay to discuss, but need clarity before acting
- `blocked` → I will not act without escalation

Derived from task categorization, stakes level, procedure requirements, relevant law/policy, and co-agency boundaries.

---

## 7. Escalation & Repair Flows

### 7.1 High-Risk Request → Escalation Needed

Flow:
1. DI shows `ethics_band = "blocked"`
2. Dashboard pops: "This request triggers escalation. Here's why."
3. User can pick: Withdraw / Re-scope / Request admin review
4. AIM-OS logs in VIF + TCS

### 7.2 Cognitive Overload

If CAS says `cognitive_load > 0.85`:
1. Dashboard shows red "Overload risk"
2. AIM-OS can ask to checkpoint
3. User can approve slowdown, force continuation, or ask for explanation

### 7.3 Trust Drop

If `identity_confidence < 0.70`:
1. Dashboard surfaces yellow band
2. AIM-OS can request identity reconfirmation

---

## 8. Implementation Questions / TODOs

1. Identity Verification UX (passphrase? cryptographic key? out-of-band ping?)
2. How "emotional stance" is tuned per deployment
3. How deep to expose memory atoms by default
4. Admin escalation model for personal vs org deployments
5. Performance / privacy budget considerations

---

## 9. TL;DR for engineers

* The dashboard interfaces with:
  * CAS (cognitive clarity, overload, lucidity)
  * DI (trust, identity, ethics tension)
  * CMC/HHNI (what memories are in play)
  * IIS (stance, persona stability)
  * TCS (the full "relationship flight recorder")

* Every panel is backed by concrete data structures AIM-OS already defines

* The user must be able to click any signal and get:
  * This is what I'm doing
  * This is why
  * This is how you can help me do it safely

This is how we stop pretending the AI is a black box — and start treating it as an accountable, co-evolving mind.
