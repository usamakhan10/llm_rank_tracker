# gemini_client.py
import os
import requests
from typing import Any, Dict, List, Optional
from dotenv import load_dotenv
from base_client import BaseLLMClient, PlatformResponse

load_dotenv()

class GeminiClient(BaseLLMClient):
    """DataForSEO Gemini API client with unified interface"""
    
    def __init__(self, 
                 login: Optional[str] = None,
                 password: Optional[str] = None,
                 timeout_s: int = 120):
        super().__init__(timeout_s)
        self.session = requests.Session()
        self.session.auth = (
            login or os.environ["DATAFORSEO_LOGIN"],
            password or os.environ["DATAFORSEO_PASSWORD"],
        )
        self.session.headers.update({"Content-Type": "application/json"})
        self.base_url = "https://api.dataforseo.com"
    
    def list_models(self) -> List[Dict[str, Any]]:
        """Returns available Gemini models"""
        url = f"{self.base_url}/v3/ai_optimization/gemini/llm_responses/models"
        r = self.session.get(url, timeout=30)
        r.raise_for_status()
        data = r.json()
        self._assert_ok(data)
        return data["tasks"][0]["result"]
    
    def query(self, 
              keyword: str,
              model_name: Optional[str] = None,
              web_search: bool = True,
              max_tokens: int = 800) -> PlatformResponse:
        """Query Gemini with keyword and return structured response"""
        
        if model_name is None:
            model_name = "gemini-2.5-flash"
        
        url = f"{self.base_url}/v3/ai_optimization/gemini/llm_responses/live"
        prompt = self.create_search_prompt(keyword)
        
        task = {
            "user_prompt": prompt,
            "model_name": model_name,
            "system_message": "You are a product ranking assistant. Follow the exact format requested. List only product names, no descriptions or features.",
            "max_output_tokens": max_tokens,
            "temperature": 0.2,
            "top_p": 0.9,
            "web_search": web_search
        }
        
        try:
            r = self.session.post(url, json=[task], timeout=self.timeout_s)
            r.raise_for_status()
            data = r.json()
            self._assert_ok(data)
            
            result = data["tasks"][0]["result"][0]
            
            # Extract text from response
            raw_text = self._extract_text(result)
            
            # Extract rankings
            ranked_items = self.extract_rankings(raw_text)
            
            return PlatformResponse(
                platform="Gemini",
                model=model_name,
                raw_text=raw_text,
                ranked_items=ranked_items,
                input_tokens=result.get("input_tokens", 0),
                output_tokens=result.get("output_tokens", 0),
                cost=result.get("money_spent", 0.0),
                web_search_used=result.get("web_search", False)
            )
            
        except Exception as e:
            return PlatformResponse(
                platform="Gemini",
                model=model_name,
                raw_text="",
                ranked_items=[],
                input_tokens=0,
                output_tokens=0,
                cost=0.0,
                error=str(e)
            )
    
    def _extract_text(self, result: Dict[str, Any]) -> str:
        """Extract plain text from Gemini structured response"""
        text_parts = []
        
        for item in result.get("items", []) or result.get("content", []):
            # Support both "items" (newer) and "content" (older) response shapes
            sections = item.get("sections") or ([item] if item.get("type") else [])
            for sec in sections:
                if sec.get("type") == "text" and "text" in sec:
                    text_parts.append(sec["text"])
                # Fallback: some responses put text directly under "text" on item
                elif sec.get("type") is None and "text" in sec:
                    text_parts.append(sec["text"])
        
        return "\n\n".join(text_parts).strip()
    
    @staticmethod
    def _assert_ok(payload: Dict[str, Any]) -> None:
        if payload.get("status_code") != 20000:
            raise RuntimeError(f"DataForSEO API error: {payload.get('status_message')}")
        task = (payload.get("tasks") or [{}])[0]
        if task.get("status_code") != 20000:
            raise RuntimeError(f"Task error: {task.get('status_message')}")