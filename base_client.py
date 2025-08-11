# base_client.py
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
import re
from dataclasses import dataclass

@dataclass
class RankResult:
    """Represents a ranked item from AI response"""
    rank: int
    title: str
    description: Optional[str] = None
    source: Optional[str] = None
    
@dataclass
class PlatformResponse:
    """Unified response model for all platforms"""
    platform: str
    model: str
    raw_text: str
    ranked_items: List[RankResult]
    input_tokens: int
    output_tokens: int
    cost: float
    web_search_used: bool = False
    error: Optional[str] = None

class BaseLLMClient(ABC):
    """Abstract base class for all LLM platform clients"""
    
    def __init__(self, timeout_s: int = 120):
        self.timeout_s = timeout_s
        self.platform_name = self.__class__.__name__.replace("Client", "")
    
    @abstractmethod
    def list_models(self) -> List[Dict[str, Any]]:
        """List available models for the platform"""
        pass
    
    @abstractmethod
    def query(self, 
              keyword: str,
              model_name: Optional[str] = None,
              web_search: bool = True,
              max_tokens: int = 800) -> PlatformResponse:
        """Query the platform with a keyword and return structured response"""
        pass
    
    def extract_rankings(self, text: str) -> List[RankResult]:
        """Extract ranked items from AI response text - optimized for strict format"""
        ranked_items = []
        lines = text.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Look for numbered items (1. Item or 1) Item)
            numbered_match = re.match(r'^(\d+)[\.\)]\s*(.+)', line)
            if numbered_match:
                rank = int(numbered_match.group(1))
                item_text = numbered_match.group(2).strip()
                
                # Remove any markdown formatting
                item_text = re.sub(r'\*+', '', item_text)
                item_text = re.sub(r'\[|\]', '', item_text)  # Remove brackets
                item_text = item_text.strip()
                
                # Skip if this looks like a description or feature
                if self._is_likely_product_name(item_text):
                    ranked_items.append(RankResult(
                        rank=rank,
                        title=item_text,
                        description=None  # No descriptions in strict format
                    ))
        
        # If we got very few results, fallback to more lenient extraction
        if len(ranked_items) < 3:
            ranked_items = self._fallback_extraction(text)
        
        # Remove duplicates
        seen_titles = set()
        unique_items = []
        for item in ranked_items:
            title_key = item.title.lower().strip()
            if title_key not in seen_titles:
                seen_titles.add(title_key)
                unique_items.append(item)
        
        # Re-number items sequentially
        for i, item in enumerate(unique_items, 1):
            item.rank = i
        
        return unique_items
    
    def _is_likely_product_name(self, text: str) -> bool:
        """Check if text is likely a product name"""
        if not text or len(text) < 3:
            return False
        
        # Reject obvious features/descriptions
        text_lower = text.lower()
        reject_patterns = [
            'features', 'includes', 'made from', 'equipped with',
            'available in', 'comes with', 'designed', 'key features'
        ]
        
        for pattern in reject_patterns:
            if text_lower.startswith(pattern):
                return False
        
        # Accept if reasonable length
        return 3 <= len(text) <= 100
    
    def _fallback_extraction(self, text: str) -> List[RankResult]:
        """Fallback extraction for non-compliant responses"""
        ranked_items = []
        lines = text.split('\n')
        
        for line in lines:
            line = line.strip()
            
            # Try to find product-like names with bold formatting
            bold_match = re.search(r'\*\*([^\*]+)\*\*', line)
            if bold_match:
                title = bold_match.group(1).strip()
                if self._is_likely_product_name(title):
                    ranked_items.append(RankResult(
                        rank=len(ranked_items) + 1,
                        title=title,
                        description=None
                    ))
        
        return ranked_items
    
    def create_search_prompt(self, keyword: str) -> str:
        """Create a standardized prompt for ranking queries"""
        return (
            f"List the top 10 {keyword}. Use ONLY this exact format:\n\n"
            f"1. [Product Name]\n"
            f"2. [Product Name]\n"
            f"3. [Product Name]\n"
            f"etc.\n\n"
            f"STRICT RULES:\n"
            f"- Write ONLY the product name/brand after each number\n"
            f"- Do NOT add descriptions, features, or any other text\n"
            f"- One product per line\n"
            f"- No bullet points or sub-items\n"
            f"- No additional commentary\n"
            f"Example correct format:\n"
            f"1. Fellow Atmos Vacuum Canister\n"
            f"2. Coffee Gator Stainless Steel Container\n"
            f"3. OXO POP Container"
        )