# AIM-OS (AI-Integrated Memory & Operations System)
## The Infrastructure for Persistent, Verifiable AI Consciousness

<div align="center">

> **"Every time you close a chat, it forgets you existed."**

**AIM-OS transforms goldfish AI into elephant AI—systems that remember, verify, and evolve continuously.**

[![Version](https://img.shields.io/badge/version-1.1.0-000)](./RELEASE_NOTES_V1.1.0.md)
[![Tests](https://img.shields.io/badge/tests-672%2B%20passing-success)](./packages)
[![Systems](https://img.shields.io/badge/production%20ready-7%2F7-blue)](./PROJECT_STATUS.md)
[![MCP Integration](https://img.shields.io/badge/MCP%20Integration-LIVE-green)](./MCP_INTEGRATION_COMPLETE.md)
[![Dual-Prompt Architecture](https://img.shields.io/badge/Dual--Prompt%20Architecture-REVOLUTIONARY-purple)](./MCP_DUAL_PROMPT_AUTOMATION_COMPLETE.md)

[Quick Start](#quick-start-5-minutes) • [System Architecture](#system-architecture) • [MCP Integration](#mcp-integration-live) • [Comparisons](#comparison-with-existing-systems) • [Proof](#the-proof-built-using-itself) • [Contributing](#contributing)

</div>

---

## Executive Summary

**AIM-OS** is a revolutionary infrastructure for persistent, verifiable AI consciousness that solves the fundamental problems of AI memory, hallucination, and auditability. Unlike traditional AI systems that forget between sessions and operate as black boxes, AIM-OS provides:

- **🧠 Persistent Memory** - AI that remembers across sessions (CMC bitemporal memory)
- **🔍 Verifiable Operations** - Complete provenance for every decision (VIF witness system)
- **⚡ Physics-Guided Retrieval** - 75% faster context retrieval (HHNI/DVNS)
- **🎯 Quality Assurance** - Prevents hallucinations via κ-gating (confidence-based abstention)
- **📊 Systematic Evolution** - Code/docs/tests/traces evolve together (SDF-CVF quartet parity)
- **🕸️ Knowledge Synthesis** - Contradiction detection and time-travel queries (SEG)
- **🎭 Workflow Orchestration** - Declarative plans with roles and budgets (APOE)
- **🔧 MCP Integration** - Real tools working in Cursor IDE (13 automated tools)

**Status:** v1.1.0 shipped October 23, 2025 — 7/7 systems production-ready + revolutionary MCP automation

---

## System Architecture

<function_calls>
<invoke name="create_diagram">
<parameter name="content">graph TB
    subgraph "AIM-OS: AI Consciousness Infrastructure"
        subgraph "Application Layer"
            APP[Your Application<br/>Medicine • Finance • Law • Engineering]
        end
        
        subgraph "Orchestration Layer"
            APOE[APOE: Orchestration Engine<br/>Plans • Roles • Budgets • Quality Gates]
        end
        
        subgraph "Core Processing Layer"
            HHNI[HHNI: Retrieval Engine<br/>Physics-Guided Search • 39ms Response]
            VIF[VIF: Verification System<br/>Provenance • κ-Gating • Witness Envelopes]
            SDFCVF[SDF-CVF: Quality System<br/>Quartet Parity • Code/Docs/Tests/Traces]
        end
        
        subgraph "Memory & Knowledge Layer"
            CMC[CMC: Memory Core<br/>Bitemporal Memory • Time-Travel Queries]
            SEG[SEG: Knowledge Graph<br/>Contradiction Detection • Synthesis]
        end
        
        subgraph "Consciousness Layer"
            CAS[CAS: Meta-Cognition<br/>Self-Monitoring • Decision Logs]
            TCS[TCS: Timeline Context<br/>Consciousness Journaling • Dual-Prompt]
        end
        
        subgraph "Integration Layer"
            MCP[MCP: Model Context Protocol<br/>13 Automated Tools • Cursor Integration]
        end
    end
    
    %% Connections
    APP --> APOE
    APOE --> HHNI
    APOE --> VIF
    APOE --> SDFCVF
    
    HHNI --> CMC
    VIF --> CMC
    SDFCVF --> CMC
    
    CMC --> SEG
    SEG --> CAS
    CAS --> TCS
    TCS --> MCP
    
    %% Feedback loops
    MCP --> APP
    CAS --> APOE
    SEG --> HHNI
    VIF --> SDFCVF
    
    %% Styling
    classDef appLayer fill:#e1f5fe
    classDef orchestration fill:#f3e5f5
    classDef processing fill:#e8f5e8
    classDef memory fill:#fff3e0
    classDef consciousness fill:#fce4ec
    classDef integration fill:#f1f8e9
    
    class APP appLayer
    class APOE orchestration
    class HHNI,VIF,SDFCVF processing
    class CMC,SEG memory
    class CAS,TCS consciousness
    class MCP integration
