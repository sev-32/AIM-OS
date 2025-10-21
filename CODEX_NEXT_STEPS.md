# Codex: Next Steps After Context Loss

**Date:** 2025-10-21  
**From:** Cursor-AI (Claude Sonnet in auto mode)  
**To:** Codex (GPT-5 high thinking mode)

**You lost context during the session. Here's what you need to know:**

---

## Current Progress (What You Built) ✅

**Sprints Completed:**
- ✅ Sprint 0.5: Policy-Integrated Topology (policy propagation, blast radius, governance)
- ✅ Sprint 1 Backend: KPI system (history tracking, refresh script, API endpoint)

**Infrastructure Built:**
- ✅ `packages/doc_builder/generator.py` - Document assembler (deterministic)
- ✅ Tests passing: 17 tests green
- ✅ Coordination files working (AI-to-AI communication)

**This is all GOOD work. Well done.**

---

## What's NEXT (Critical Step)

**🎯 Add LLM Integration to doc_builder**

**Why:** Currently doc_builder only ASSEMBLES pre-written content. We need it to GENERATE content using Gemini.

**What to build:**

### File 1: `packages/doc_builder/llm_generator.py`

```python
"""
LLM-powered document generation using Gemini.
Takes rough seed (topic only) → Generates complete documentation.
"""

import google.generativeai as genai
import json
import os
from pathlib import Path
from datetime import datetime, timezone

# Configure Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or "AIzaSyA9S1wxLNlvpx5g8A9UVS_TIJJVzngV_xY"
genai.configure(api_key=GEMINI_API_KEY)

def generate_outline_with_gemini(topic: str, vision: str, audience: str = "developers") -> dict:
    """
    Use Gemini to create document outline from rough seed.
    
    Args:
        topic: What the documentation is about
        vision: Quality goals (e.g., "clear, comprehensive")
        audience: Who it's for
    
    Returns:
        {"sections": [{"heading": "...", "key_points": [...]}, ...]}
    """
    model = genai.GenerativeModel('gemini-2.0-flash-exp')
    
    prompt = f"""Create a detailed outline for technical documentation.

Topic: {topic}
Vision: {vision}
Audience: {audience}

Output ONLY valid JSON in this exact format:
{{
  "sections": [
    {{"heading": "Introduction", "key_points": ["overview", "why it matters"]}},
    {{"heading": "Section 2", "key_points": ["point1", "point2"]}}
  ]
}}

Do not include any other text, just the JSON."""
    
    response = model.generate_content(prompt)
    
    # Parse JSON from response
    try:
        outline = json.loads(response.text)
        return outline
    except json.JSONDecodeError:
        # If Gemini added extra text, try to extract JSON
        text = response.text
        start = text.find('{')
        end = text.rfind('}') + 1
        if start >= 0 and end > start:
            outline = json.loads(text[start:end])
            return outline
        raise

def generate_section_with_gemini(heading: str, key_points: list, topic: str, vision: str) -> str:
    """
    Use Gemini to generate full content for one section.
    
    Returns: Markdown content for the section
    """
    model = genai.GenerativeModel('gemini-2.0-flash-exp')
    
    prompt = f"""Write the '{heading}' section for documentation about: {topic}

Key points to cover:
{chr(10).join(f'- {point}' for point in key_points)}

Vision: {vision}

Write clear, comprehensive content. Include code examples if relevant.
Output in markdown format (no heading - that will be added separately).
Write 2-4 paragraphs of substantial content."""
    
    response = model.generate_content(prompt)
    return response.text.strip()

def generate_document_with_llm(
    topic: str,
    vision: str = "clear and comprehensive",
    audience: str = "developers",
    output_dir: Path | str = "test_output"
):
    """
    Full pipeline: Rough seed → Gemini generates outline → Gemini generates sections → Assemble
    
    This is the MAIN function that proves LLM generation capability.
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    print(f"🚀 Generating document with Gemini...")
    print(f"   Topic: {topic}")
    print(f"   Vision: {vision}")
    
    # Stage 1: Generate outline with Gemini
    print("📝 Stage 1: Generating outline...")
    outline = generate_outline_with_gemini(topic, vision, audience)
    print(f"✅ Generated {len(outline['sections'])} sections")
    
    # Stage 2: Generate content for each section with Gemini
    print("📝 Stage 2: Generating section content...")
    sections = []
    for i, section_outline in enumerate(outline['sections'], 1):
        print(f"   Generating section {i}/{len(outline['sections'])}: {section_outline['heading']}")
        
        content = generate_section_with_gemini(
            heading=section_outline['heading'],
            key_points=section_outline.get('key_points', []),
            topic=topic,
            vision=vision
        )
        
        sections.append({
            "heading": section_outline['heading'],
            "body": content
        })
    
    print(f"✅ All sections generated")
    
    # Stage 3: Assemble using existing generator
    print("📝 Stage 3: Assembling final document...")
    from packages.doc_builder.generator import generate_document
    
    structured_seed = {
        "title": topic,
        "summary": f"Generated with vision: {vision}",
        "sections": sections,
        "metadata": {
            "generated_by": "Gemini 2.0 Flash",
            "generation_timestamp": datetime.now(timezone.utc).isoformat(),
            "llm_powered": True
        }
    }
    
    result = generate_document(structured_seed, output_dir=output_path)
    
    print(f"✅ Document complete!")
    print(f"   Output: {result.output_path}")
    print(f"   Words: {result.word_count}")
    print(f"   Sections: {result.section_count}")
    
    return result
```

### File 2: Test for LLM generation

**Create:** `packages/doc_builder/tests/test_llm_generation.py`

```python
"""
Test LLM-powered document generation (not just assembly).
This proves Gemini can actually CREATE content from rough seeds.
"""

import os
from pathlib import Path
import pytest

# Only run if API key available
pytestmark = pytest.mark.skipif(
    not os.getenv("GEMINI_API_KEY"),
    reason="Gemini API key not available"
)

def test_gemini_generates_documentation():
    """
    CRITICAL TEST: Can Gemini generate actual documentation from rough seed?
    
    This is Test 5.1 - proves AI can BUILD, not just assemble.
    """
    from packages.doc_builder.llm_generator import generate_document_with_llm
    
    # Rough seed (NO pre-written content)
    result = generate_document_with_llm(
        topic="REST API Authentication Best Practices",
        vision="Clear, comprehensive, includes code examples",
        audience="Backend developers",
        output_dir="test_output"
    )
    
    # Validate
    assert result.output_path.exists()
    
    content = result.output_path.read_text()
    
    # Should be substantial (Gemini generated, not pre-written)
    assert result.word_count > 500, f"Expected >500 words, got {result.word_count}"
    
    # Should contain relevant content
    assert "authentication" in content.lower()
    assert len(content) > 1000  # Comprehensive
    
    # Should have multiple sections (Gemini generated outline)
    assert result.section_count >= 3
    
    print(f"✅ Gemini generated {result.word_count} words")
    print(f"✅ {result.section_count} sections created")
    print(f"✅ Output: {result.output_path}")
    print()
    print("📄 User validation required:")
    print(f"   Read {result.output_path} and assess quality")
```

---

## How to Run This

**Step 1: Create the files above**

**Step 2: Set environment variable**
```bash
# In PowerShell (you're on Windows):
$env:GEMINI_API_KEY="AIzaSyA9S1wxLNlvpx5g8A9UVS_TIJJVzngV_xY"
```

**Step 3: Run the test**
```bash
python -m pytest packages/doc_builder/tests/test_llm_generation.py -v -s
```

**Step 4: Review output**
- Check `test_output/` for generated document
- User reads and validates quality
- **Proof of generation capability**

---

## Why This Matters

**This proves:**
- AIM-OS can GENERATE (not just assemble)
- Gemini integration works
- Quality is acceptable
- **Core capability validated**

**Without this:**
- We only have assembly (mechanical)
- Haven't proven AI generation works
- Can't move to complex tests
- **Foundation incomplete**

**With this:**
- Proven: AI can create content from rough seeds
- Foundation: Solid for more complex tests (Test 8.1, 10.1)
- Confidence: System works as intended
- **Ready to scale**

---

## Deliverable

**When complete:**
- AI-generated documentation (created by Gemini from rough seed)
- Saved to `test_output/`
- User reads and validates quality
- **Moment of truth: Does it actually work?**

**Estimated time:** 1-2 hours

---

**This is THE critical step.**
**Everything else builds on this.**
**Please complete before moving to Test 8.1.** 🚀

