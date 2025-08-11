# chatgpt_client.py
import os
import requests
from typing import Any, Dict, List, Optional
from dotenv import load_dotenv
from base_client import BaseLLMClient, PlatformResponse

load_dotenv()

class ChatGPTClient(BaseLLMClient):
    """DataForSEO ChatGPT API client"""
    
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
        """Returns available ChatGPT models"""
        url = f"{self.base_url}/v3/ai_optimization/chat_gpt/llm_responses/models"
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
        """Query ChatGPT with keyword and return structured response"""
        
        if model_name is None:
            # Default to GPT-4o-mini for cost efficiency
            model_name = "gpt-4o-mini-2024-07-18"
        
        url = f"{self.base_url}/v3/ai_optimization/chat_gpt/llm_responses/live"
        
        prompt = self.create_search_prompt(keyword)
        
        task = {
            "user_prompt": prompt,
            "model_name": model_name,
            "system_message": "You are a product ranking assistant. Follow the exact format requested. List only product names, no descriptions or features.",
            "max_output_tokens": max_tokens,
            "temperature": 0.2,
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
                platform="ChatGPT",
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
                platform="ChatGPT",
                model=model_name,
                raw_text="",
                ranked_items=[],
                input_tokens=0,
                output_tokens=0,
                cost=0.0,
                error=str(e)
            )
    
    def _extract_text(self, result: Dict[str, Any]) -> str:
        """Extract plain text from ChatGPT structured response"""
        text_parts = []
        
        for item in result.get("items", []):
            # ChatGPT response structure
            if "sections" in item:
                for section in item["sections"]:
                    if section.get("type") == "text" and "text" in section:
                        text_parts.append(section["text"])
            elif "text" in item:
                text_parts.append(item["text"])
        
        return "\n\n".join(text_parts).strip()
    
    @staticmethod
    def _assert_ok(payload: Dict[str, Any]) -> None:
        if payload.get("status_code") != 20000:
            raise RuntimeError(f"DataForSEO API error: {payload.get('status_message')}")
        task = (payload.get("tasks") or [{}])[0]
        if task.get("status_code") != 20000:
            raise RuntimeError(f"Task error: {task.get('status_message')}")