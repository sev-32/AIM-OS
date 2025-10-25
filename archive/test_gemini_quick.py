"""Quick test to verify Gemini API works."""

import sys
sys.path.insert(0, 'packages')

from llm_client import GeminiClient

# Test with direct API key
API_KEY = "AIzaSyA9S1wxLNlvpx5g8A9UVS_TIJJVzngV_xY"

print("=" * 60)
print("Testing Gemini API Integration")
print("=" * 60)

try:
    # Create client
    print("\n1. Creating GeminiClient...")
    client = GeminiClient(api_key=API_KEY)
    print(f"   [OK] Client created: {client.model_name}")
    
    # Get model info
    print("\n2. Getting model info...")
    info = client.get_model_info()
    print(f"   [OK] Model: {info.name}")
    print(f"   [OK] Provider: {info.provider}")
    print(f"   [OK] Context window: {info.context_window:,} tokens")
    print(f"   [OK] Max output: {info.max_output_tokens:,} tokens")
    
    # Test generation
    print("\n3. Testing simple generation...")
    response = client.generate("Say 'Hello from Aether!' and nothing else.")
    print(f"   [OK] Generated: {response.text}")
    print(f"   [OK] Tokens used: {response.tokens_used}")
    print(f"   [OK] Latency: {response.latency_ms:.2f}ms")
    print(f"   [OK] Confidence: {response.confidence}")
    
    # Test longer generation
    print("\n4. Testing technical question...")
    response2 = client.generate(
        "Explain bitemporal databases in exactly 2 sentences."
    )
    print(f"   [OK] Generated: {response2.text}")
    print(f"   [OK] Tokens used: {response2.tokens_used}")
    print(f"   [OK] Latency: {response2.latency_ms:.2f}ms")
    print(f"   [OK] Confidence: {response2.confidence}")
    
    # Verify response quality
    print("\n5. Quality checks...")
    assert len(response2.text) > 50, "Response too short"
    assert "time" in response2.text.lower() or "temporal" in response2.text.lower(), "Missing key concept"
    print("   [OK] Response contains expected concepts")
    
    print("\n" + "=" * 60)
    print("[SUCCESS] ALL TESTS PASSED - GEMINI INTEGRATION WORKS!")
    print("=" * 60)
    print("\nInfrastructure + Real AI = PROVEN!\n")
    
except Exception as e:
    print(f"\n[ERROR] {type(e).__name__}")
    print(f"   Message: {str(e)}")
    print("\n" + "=" * 60)
    import traceback
    traceback.print_exc()

