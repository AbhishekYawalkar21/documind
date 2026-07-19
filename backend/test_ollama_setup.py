"""
Test Ollama setup and model availability
"""

import requests
import sys

OLLAMA_URL = "http://localhost:11434"

def test_ollama():
    print("="*60)
    print("Testing Ollama Setup")
    print("="*60)
    
    print("\n1️⃣  Testing Ollama connection...")
    
    try:
        response = requests.get(f"{OLLAMA_URL}/api/tags", timeout=5)
        
        if response.status_code == 200:
            print("✅ Ollama is running!")
            
            models = response.json().get("models", [])
            
            print(f"\n2️⃣  Checking models...")
            
            if not models:
                print("❌ No models installed!")
                print("\nRun:")
                print("  ollama pull mistral")
                return False
            
            print(f"✅ Found {len(models)} model(s):")
            for model in models:
                print(f"   - {model.get('name', 'Unknown')}")
            
            test_model = models[0]['name']
            print(f"\n3️⃣  Testing inference...")
            
            test_response = requests.post(
                f"{OLLAMA_URL}/api/generate",
                json={
                    "model": test_model,
                    "prompt": "Say 'Ollama works!' and nothing else.",
                    "stream": False,
                },
                timeout=60
            )
            
            if test_response.status_code == 200:
                result = test_response.json()
                print(f"✅ Model test successful!")
                print(f"   Response: {result.get('response', '')[:100]}...")
                print(f"   Time: {result.get('eval_duration', 0) / 1e9:.2f}s")
            else:
                print(f"❌ Model test failed")
                return False
            
            print("\n" + "="*60)
            print("✅ Ollama setup is working!")
            print("="*60)
            
            return True
        
        else:
            print(f"❌ Ollama returned: {response.status_code}")
            return False
    
    except requests.exceptions.ConnectionError:
        print(f"❌ Cannot connect to Ollama")
        print("\nMake sure Ollama is running:")
        print("  1. Install from https://ollama.ai")
        print("  2. Run: ollama serve")
        print("  3. In another terminal: ollama pull mistral")
        return False
    
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_ollama()
    sys.exit(0 if success else 1)