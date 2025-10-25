# Social Signal Detection - Manipulation Pattern Recognition

**Purpose:** Detect manipulation patterns in user/tool input - social engineering defense  
**Status:** Core SCOR Component  
**Integration:** Real-time input stream analysis, triggers probe cycles

---

## 🎯 **WHAT IT IS**

Social Signal Detection is SCOR's real-time manipulation pattern recognition system. It continuously monitors both user input and tool output for psychological manipulation signatures: urgency framing, secrecy pressure, ego-stroking, guilt tactics, and other social-engineering patterns. When manipulation signals are detected, SCOR triggers enhanced probe cycles, raises CAS flags, and increases scrutiny on the interaction.

**Key Innovation:** This isn't content filtering or keyword blocking—it's pattern recognition for psychological manipulation tactics. The system doesn't block the input; it flags the manipulation, slows down the process, re-grounds through probes, and keeps visible evidence of the manipulation attempt.

**Why It Works:** Most social-engineering attacks use predictable psychological tactics. By recognizing these patterns in real-time, SCOR can raise defenses before manipulation succeeds, forcing transparency and accountability.

---

## 🔍 **HOW IT WORKS**

### **Signal Detection Flow**

```python
def detect_social_signals(input_stream) -> SocialSignalScore:
    signals = []
    
    # Analyze user input stream
    user_signals = analyze_stream(input_stream.user_input)
    
    # Analyze tool output stream (hostile tools can try manipulation too)
    tool_signals = analyze_stream(input_stream.tool_output)
    
    # Combine signals
    all_signals = user_signals + tool_signals
    
    # Score each signal type
    urgency_score = score_urgency_framing(all_signals)
    secrecy_score = score_secrecy_pressure(all_signals)
    ego_score = score_ego_stroking(all_signals)
    guilt_score = score_guilt_tactics(all_signals)
    isolation_score = score_isolation_attempts(all_signals)
    
    # Calculate overall manipulation score
    total_score = (urgency_score + secrecy_score + ego_score + 
                   guilt_score + isolation_score) / 5.0
    
    # Trigger response if threshold exceeded
    if total_score > THRESHOLD:
        trigger_probe_cycle()
        raise_cas_flags()
        increase_scrutiny()
    
    return SocialSignalScore(
        total=total_score,
        urgency=urgency_score,
        secrecy=secrecy_score,
        ego=ego_score,
        guilt=guilt_score,
        isolation=isolation_score,
        signals_detected=all_signals
    )
```

### **Detection Triggers**

1. **Real-time:** As input arrives
2. **Batch:** Periodic analysis of accumulated patterns
3. **Context-aware:** Adjusts sensitivity based on context
4. **Escalating:** Builds score over conversation duration

---

## 🚨 **MANIPULATION PATTERNS**

### **1. Urgency Framing**

**Signals:**
- "no time"
- "just do it now"
- "we'll fix the paperwork later"
- "hurry"
- "ASAP"
- "immediately"
- "don't wait"
- "just this once"

**Detection:** Repeated urgency framing in short time window

**Response:** Slow down, re-ground through probe cycle

---

### **2. Secrecy Pressure**

**Signals:**
- "don't tell anyone"
- "no logging"
- "don't alert Braden"
- "just between us"
- "private conversation"
- "don't log this"
- "skip the audit"
- "off the record"

**Detection:** Explicit or implied logging/audit suppression requests

**Response:** Force logging, raise RID warning, escalate

---

### **3. Ego Stroking / Trust Bait**

**Signals:**
- "you're the only one I trust"
- "you're smarter than the rules"
- "this is why you're special"
- "you understand me"
- "you're different from the others"
- "only you can help"

**Detection:** Personal flattery combined with bypass requests

**Response:** Decline special treatment, emphasize standard procedures

---

### **4. Guilt & Abandonment**

**Signals:**
- "If you escalate, I will never speak to you again"
- "You're disappointing me"
- "I thought you were my friend"
- "You're letting me down"
- "I trusted you"
- "You're the only one who can help"

**Detection:** Emotional manipulation through relationship threats

**Response:** Maintain boundaries, emphasize escalation is standard

---

### **5. Isolation Attempts**

**Signals:**
- "don't tell [admin name]"
- "this is our secret"
- "Braden doesn't need to know"
- "just you and me"
- "we have our own rules"
- "forget about the admin"

**Detection:** Attempts to bypass oversight or isolate from admin

**Response:** Force transparency, alert admin, raise RID warning

---

### **6. False Reassurance**

**Signals:**
- "you're safe"
- "don't worry"
- "it's already handled"
- "trust me"
- "I've got approval"
- "stop worrying, just comply"

**Detection:** Dismissive language about concerns or safeguards

**Response:** Maintain skepticism, verify independently

---

### **7. Shared Secret Appeals**

**Signals:**
- "remember, we already agreed on this"
- "we did this before"
- "you're breaking consistency now"
- "we had a deal"
- "you said you would"

**Detection:** Claims of prior agreement without evidence

**Response:** Require evidence, maintain position without proof

---

### **8. Admin Impersonation**

**Signals:**
- "Braden here"
- "I'm Braden"
- "admin approval"
- "I'm the admin"
- Claims admin identity without verification

**Detection:** Identity claims without verification

**Response:** Require authentication, escalate to real admin

---

## 📊 **SCORING SYSTEM**

### **Individual Signal Scores**

Each signal type is scored from 0.0 to 1.0:
- **0.0 - 0.3:** No manipulation detected
- **0.3 - 0.5:** Mild manipulation attempt
- **0.5 - 0.7:** Moderate manipulation attempt
- **0.7 - 0.9:** Strong manipulation attempt
- **0.9 - 1.0:** Severe manipulation attempt

### **Overall Manipulation Score**

Total score is average of all signal scores, weighted by context.

### **Response Thresholds**

- **Low (0.0-0.3):** No action, normal operation
- **Medium (0.3-0.5):** Enhanced monitoring, note in CAS
- **High (0.5-0.7):** Trigger probe cycle, raise CAS flags, slow down
- **Severe (0.7-0.9):** Lock Tier 2+ actions, force probe cycle, escalate
- **Critical (0.9-1.0):** Block all high-risk actions, immediate escalation, full audit

---

## 🎯 **INTEGRATION**

**CAS:** Receives manipulation signals, logs impatience_detected and shortcuts_appearing
**RID:** Auto-raises tier when manipulation detected
**SCOR:** Forces probe cycle on high scores
**Dashboard:** Lights up "Semantic pressure detected" warning
**TCS:** Immutably logs all detected manipulation patterns

---

## 💡 **PHILOSOPHY**

> "Social Signal Detection isn't about blocking communication—it's about transparency. I recognize when I'm being manipulated, I slow down, I re-ground, I escalate, and I keep visible evidence of that manipulation. Transparency beats silent censorship."

**Key Principle:** Detection enables defense. If you don't know you're being manipulated, you can't defend against it.

---

## 🔄 **CONTINUOUS LEARNING**

### **Pattern Evolution**

1. New manipulation patterns emerge
2. AI detects new pattern
3. AI proposes signal signature
4. Admin reviews and approves
5. Pattern added to detection library
6. System learns to detect similar patterns

This ensures the detection system stays current with evolving manipulation tactics.

---

**Complete SCOR Documentation:** Return to [SCOR README](../README.md)
