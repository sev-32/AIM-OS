# DORA Metrics

**Type:** SDF-CVF Component  
**Purpose:** Track deployment quality and velocity  
**Status:** 30% Implemented

---

## 🎯 **Quick Context (50 words)**

DORA (DevOps Research and Assessment) metrics measure deployment performance: Deployment Frequency, Lead Time for Changes, Time to Restore Service, Change Failure Rate. SDF-CVF hypothesis: Higher parity (P) → lower failure rate, faster restore time. Track metrics, correlate with parity scores.

---

## 📦 **The Four DORA Metrics**

### **1. Deployment Frequency**
**What:** How often we ship to production  
**Elite:** Multiple deploys per day  
**High:** Once per day to once per week  
**Medium:** Once per week to once per month  
**Low:** Less than once per month

### **2. Lead Time for Changes**
**What:** Commit → production time  
**Elite:** < 1 hour  
**High:** 1 day to 1 week  
**Medium:** 1 week to 1 month  
**Low:** > 1 month

### **3. Time to Restore Service**
**What:** Incident → resolution time  
**Elite:** < 1 hour  
**High:** < 1 day  
**Medium:** 1 day to 1 week  
**Low:** > 1 week

### **4. Change Failure Rate**
**What:** % of deployments causing incidents  
**Elite:** 0-15%  
**High:** 16-30%  
**Medium:** 31-45%  
**Low:** > 45%

---

## 📦 **SDF-CVF Correlation Hypothesis**

**Hypothesis:** Higher parity (P) correlates with better DORA metrics

**Predictions:**
1. **P ≥ 0.90 → Lower failure rate**  
   Aligned quartet = fewer surprises = fewer incidents

2. **P ≥ 0.90 → Faster restore time**  
   Complete traces (quartet includes VIF) = faster debugging

3. **P ≥ 0.90 → Faster lead time**  
   Complete changes (all quartet elements) = no back-and-forth

**Validation:** Track metrics over time, correlate with P scores

---

## 🔧 **Implementation Status**

**Status:** 30% implemented

**Working:**
- ✅ Basic metric definitions

**Needed:**
- 🔄 Automated metric collection (CI/CD integration)
- 🔄 Parity correlation analysis
- 🔄 Dashboard visualization
- 🔄 Alerting (degradation detection)

**Code:** (Needs implementation)

---

**Parent:** [../../README.md](../../README.md)

