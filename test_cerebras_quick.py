"""Quick test to verify Cerebras API works."""

import sys
sys.path.insert(0, 'packages')

from llm_client import CerebrasClient, LLMError, RateLimitError, AuthenticationError
import os

# Test with direct API key or env var
CEREBRAS_API_KEY = os.getenv("CEREBRAS_API_KEY")

print("=" * 60)
print("Testing Cerebras Cloud API Integration")
print("=" * 60)

if not CEREBRAS_API_KEY:
    print("\n[WARN] CEREBRAS_API_KEY environment variable not set.")
    print("Please set it in your .env file or export it.")
    print("\nTo get an API key:")
    print("1. Visit: https://cloud.cerebras.ai/")
    print("2. Sign up for free tier")
    print("3. Get your API key")
    print("4. Set CEREBRAS_API_KEY in .env")
    sys.exit(0)

try:
    # Create client
    print("\n1. Creating CerebrasClient...")
    client = CerebrasClient(api_key=CEREBRAS_API_KEY)
    print(f"   [OK] Client created: {client.model_name}")
    
    # Get model info
    print("\n2. Getting model info...")
    info = client.get_model_info()
    print(f"   [OK] Model: {info.name}")
    print(f"   [OK] Provider: {info.provider}")
    print(f"   [OK] Context window: {info.context_window:,} tokens")
    print(f"   [OK] Max output: {info.max_output_tokens:,} tokens")
    print(f"   [OK] Speed: {info.capabilities.get('speed')}")
    
    # Test ultra-fast generation
    print("\n3. Testing ULTRA-FAST generation...")
    import time
    start = time.time()
    response = client.generate("Say 'Hello from Cerebras!' and nothing else.")
    elapsed = (time.time() - start) * 1000
    print(f"   [OK] Generated: {response.text}")
    print(f"   [OK] Tokens used: {response.tokens_used}")
    print(f"   [OK] Latency: {response.latency_ms:.2f}ms")
    print(f"   [OK] Total time: {elapsed:.2f}ms")
    print(f"   [OK] Speed: ULTRA-FAST!" if elapsed < 2000 else f"   [WARN] Slower than expected")
    
    # Test longer generation
    print("\n4. Testing longer technical response...")
    start = time.time()
    response2 = client.generate(
        "Explain bitemporal databases in exactly 2 sentences."
    )
    elapsed2 = (time.time() - start) * 1000
    print(f"   [OK] Generated: {response2.text}")
    print(f"   [OK] Tokens used: {response2.tokens_used}")
    print(f"   [OK] Latency: {response2.latency_ms:.2f}ms")
    print(f"   [OK] Total time: {elapsed2:.2f}ms")
    
    # Verify response quality
    print("\n5. Quality checks...")
    assert len(response2.text) > 50, "Response too short"
    assert "time" in response2.text.lower() or "temporal" in response2.text.lower(), "Missing key concept"
    print("   [OK] Response contains expected concepts")
    
    # Speed comparison note
    print("\n6. Speed comparison (vs Gemini)...")
    print(f"   Cerebras latency: {response.latency_ms:.2f}ms")
    print(f"   Gemini typical: ~1500-3000ms")
    speedup = 2000 / response.latency_ms if response.latency_ms > 0 else 0
    print(f"   Speedup: ~{speedup:.1f}x faster!")
    
    print("\n" + "=" * 60)
    print("[SUCCESS] ALL TESTS PASSED - CEREBRAS INTEGRATION WORKS!")
    print("=" * 60)
    print("\nCerebras is ULTRA-FAST and ready for high-volume tasks!")
    print("Use for: summaries, classification, context prep, rapid iteration")
    print("\nNext: Test multi-LLM orchestration (Cerebras + Gemini)\n")
    
except AuthenticationError as e:
    print(f"\n[ERROR] Authentication failed")
    print(f"   Message: {str(e)}")
    print("\nCheck your CEREBRAS_API_KEY and try again.")
    sys.exit(1)
    
except RateLimitError as e:
    print(f"\n[ERROR] Rate limit exceeded")
    print(f"   Message: {str(e)}")
    print("\nCerebras has rate limits. Wait a moment and try again.")
    sys.exit(1)
    
except Exception as e:
    print(f"\n[ERROR] {type(e).__name__}")
    print(f"   Message: {str(e)}")
    print("\n" + "=" * 60)
    import traceback
    traceback.print_exc()
    sys.exit(1)

