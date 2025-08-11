# dataforseo_gemini.py
import os
import requests
from typing import Any, Dict, List, Optional
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "https://api.dataforseo.com"

class DataForSEOGemini:
    def __init__(self,
                 login: Optional[str] = None,
                 password: Optional[str] = None,
                 timeout_s: int = 120):
        self.session = requests.Session()
        self.session.auth = (
            login or os.environ["DATAFORSEO_LOGIN"],
            password or os.environ["DATAFORSEO_PASSWORD"],
        )
        self.session.headers.update({"Content-Type": "application/json"})
        self.base = BASE_URL.rstrip("/")
        self.timeout_s = timeout_s  # Live endpoints can take tens of seconds

    def list_models(self) -> List[Dict[str, Any]]:
        """Returns [{'model_name': 'gemini-2.5-flash', 'web_search_supported': True, ...}, ...]"""
        url = f"{self.base}/v3/ai_optimization/gemini/llm_responses/models"
        r = self.session.get(url, timeout=30)
        r.raise_for_status()
        data = r.json()
        self._assert_ok(data)
        return data["tasks"][0]["result"]

    def live(self,
             user_prompt: str,
             model_name: str = "gemini-2.5-flash",
             system_message: Optional[str] = None,
             message_chain: Optional[List[Dict[str, str]]] = None,
             web_search: Optional[bool] = None,
             temperature: float = 0.3,
             top_p: float = 0.9,
             max_output_tokens: int = 512,
             web_search_country_iso_code: Optional[str] = None,
             web_search_city: Optional[str] = None) -> Dict[str, Any]:
        """Runs a single Live task and returns the first result object."""
        url = f"{self.base}/v3/ai_optimization/gemini/llm_responses/live"

        task = {
            "user_prompt": user_prompt,          # <= keep under ~500 chars
            "model_name": model_name,
            "max_output_tokens": max_output_tokens,
            "temperature": temperature,
            "top_p": top_p,
        }
        if system_message: task["system_message"] = system_message  # <= ~500 chars
        if message_chain:  task["message_chain"]  = message_chain   # <= up to 10 turns
        if web_search is not None: task["web_search"] = bool(web_search)
        if web_search_country_iso_code: task["web_search_country_iso_code"] = web_search_country_iso_code
        if web_search_city: task["web_search_city"] = web_search_city  # (city targeting isn’t supported by every LLM)

        r = self.session.post(url, json=[task], timeout=self.timeout_s)
        r.raise_for_status()
        data = r.json()
        self._assert_ok(data)
        # Return the first result object (structured)
        return data["tasks"][0]["result"][0]

    @staticmethod
    def extract_text(result: Dict[str, Any]) -> str:
        """Pulls plain text from the structured items/sections."""
        out = []
        for item in result.get("items", []) or result.get("content", []):
            # support both "items" (newer) and "content" (older/sample) shapes
            sections = item.get("sections") or ([item] if item.get("type") else [])
            for sec in sections:
                if sec.get("type") == "text" and "text" in sec:
                    out.append(sec["text"])
                # fallback: some responses put text directly under "text" on item
                if sec.get("type") is None and "text" in sec:
                    out.append(sec["text"])
        return "\n\n".join(out).strip()

    @staticmethod
    def _assert_ok(payload: Dict[str, Any]) -> None:
        if payload.get("status_code") != 20000:
            raise RuntimeError(f"DataForSEO API error: {payload.get('status_message')}")
        task = (payload.get("tasks") or [{}])[0]
        if task.get("status_code") != 20000:
            raise RuntimeError(f"Task error: {task.get('status_message')}")
