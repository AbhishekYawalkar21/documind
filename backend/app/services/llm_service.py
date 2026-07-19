import requests
from typing import Optional
import os
from dotenv import load_dotenv
import time

load_dotenv()

class LLMService:
    """Service to interact with Local LLM via Ollama (completely free)"""
    
    def __init__(
        self,
        ollama_url: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.3
    ):
        self.ollama_url = ollama_url or os.getenv("OLLAMA_URL", "http://localhost:11434")
        self.model = model or os.getenv("OLLAMA_MODEL", "mistral")
        self.temperature = temperature
        
        print(f"[LLM] Initialized with model: {self.model}")
        print(f"[LLM] Ollama URL: {self.ollama_url}")
        
        self._test_connection()
    
    def _test_connection(self):
        """Test if Ollama is running"""
        try:
            response = requests.get(
                f"{self.ollama_url}/api/tags",
                timeout=5
            )
            if response.status_code == 200:
                print(f"[LLM] ✅ Connected to Ollama")
            else:
                print(f"[LLM] ⚠️  Ollama status: {response.status_code}")
        except requests.exceptions.ConnectionError:
            print(f"[LLM] ❌ Cannot connect to Ollama at {self.ollama_url}")
            raise Exception(
                f"Ollama not running at {self.ollama_url}. "
                "Run: ollama serve"
            )
        except Exception as e:
            print(f"[LLM] ⚠️  Connection test: {str(e)}")
    
    def call_llm(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """
        Call local LLM via Ollama
        
        Args:
            prompt: User prompt
            system_prompt: System instruction (optional)
        
        Returns:
            LLM response text
        """
        
        full_prompt = prompt
        if system_prompt:
            full_prompt = f"{system_prompt}\n\n{prompt}"
        
        try:
            print(f"[LLM] Calling {self.model}...")
            start_time = time.time()
            
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": full_prompt,
                    "stream": False,
                    "temperature": self.temperature,
                },
                timeout=300
            )
            
            elapsed = time.time() - start_time
            print(f"[LLM] Response in {elapsed:.2f}s")
            
            if response.status_code != 200:
                raise Exception(f"Ollama error: {response.text}")
            
            result = response.json()
            response_text = result.get("response", "").strip()
            
            if not response_text:
                raise Exception("Empty response from Ollama")
            
            return response_text
        
        except requests.exceptions.ConnectionError:
            raise Exception(
                f"Cannot connect to Ollama at {self.ollama_url}. "
                "Run: ollama serve"
            )
        except requests.exceptions.Timeout:
            raise Exception(
                "Ollama request timeout. Try smaller model: ollama pull neural-chat"
            )
        except Exception as e:
            raise Exception(f"Error calling Ollama: {str(e)}")
    
    def call_llm_json(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Call LLM and request JSON response"""
        
        json_system = (system_prompt or "") + "\n\nRespond with ONLY valid JSON, no markdown, no extra text, no code blocks."
        
        response = self.llm(prompt, json_system)
        
        # Clean up response if it has markdown
        if response.startswith("```"):
            response = response.split("```")[1]
            if response.startswith("json"):
                response = response[4:]
        
        return response.strip()