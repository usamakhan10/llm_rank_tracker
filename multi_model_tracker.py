# multi_model_tracker.py
"""Enhanced tracker that can query multiple models per platform"""

from rank_tracker import KeywordRankTracker
from base_client import PlatformResponse
from typing import Dict, List, Optional
import json
from datetime import datetime

class MultiModelTracker(KeywordRankTracker):
    """Extended tracker with multi-model support"""
    
    # Define available models per platform
    PLATFORM_MODELS = {
        "chatgpt": [
            "gpt-4o-mini-2024-07-18",
            "gpt-4o-2024-11-20",
            "gpt-4-turbo-2024-04-09",
            "gpt-3.5-turbo-0125"
        ],
        "perplexity": [
            "sonar",
            "sonar-pro", 
            "sonar-reasoning",
            "sonar-reasoning-pro"
        ],
        "gemini": [
            "gemini-2.5-flash",
            "gemini-2.5-pro",
            "gemini-1.5-flash-001",
            "gemini-1.5-pro-001"
        ]
    }
    
    def query_all_models(self, 
                        keyword: str,
                        platforms: Optional[List[str]] = None,
                        web_search: bool = True) -> Dict[str, Dict[str, PlatformResponse]]:
        """Query all available models for specified platforms"""
        
        if platforms is None:
            platforms = list(self.clients.keys())
        
        all_results = {}
        
        for platform in platforms:
            if platform not in self.clients:
                continue
            
            all_results[platform] = {}
            models = self.PLATFORM_MODELS.get(platform, [])
            
            print(f"\n🔍 Querying {platform.upper()} models...")
            
            for model in models:
                print(f"  - Testing model: {model}")
                try:
                    response = self.clients[platform].query(
                        keyword=keyword,
                        model_name=model,
                        web_search=web_search
                    )
                    all_results[platform][model] = response
                    
                    if response.error:
                        print(f"    ❌ Error: {response.error}")
                    else:
                        print(f"    ✅ Found {len(response.ranked_items)} items (cost: ${response.cost:.4f})")
                        
                except Exception as e:
                    print(f"    ❌ Failed: {str(e)}")
                    all_results[platform][model] = PlatformResponse(
                        platform=platform,
                        model=model,
                        raw_text="",
                        ranked_items=[],
                        input_tokens=0,
                        output_tokens=0,
                        cost=0.0,
                        error=str(e)
                    )
        
        return all_results
    
    def compare_models_within_platform(self, 
                                      platform_results: Dict[str, PlatformResponse]) -> Dict:
        """Compare results from different models within the same platform"""
        
        comparison = {
            "model_performance": {},
            "consensus_items": [],
            "model_specific_items": {}
        }
        
        all_items = {}
        
        for model, response in platform_results.items():
            if response.error:
                comparison["model_performance"][model] = {
                    "status": "error",
                    "error": response.error
                }
                continue
            
            comparison["model_performance"][model] = {
                "items_found": len(response.ranked_items),
                "cost": response.cost,
                "tokens": f"{response.input_tokens}/{response.output_tokens}"
            }
            
            for item in response.ranked_items:
                item_key = self.normalize_title(item.title)
                if item_key not in all_items:
                    all_items[item_key] = {
                        "title": item.title,
                        "models": []
                    }
                all_items[item_key]["models"].append(model)
        
        # Find consensus items (appearing in multiple models)
        for item_key, data in all_items.items():
            if len(data["models"]) > 1:
                comparison["consensus_items"].append({
                    "item": data["title"],
                    "models": data["models"],
                    "agreement_score": len(data["models"]) / len(platform_results)
                })
        
        # Sort consensus items by agreement score
        comparison["consensus_items"].sort(key=lambda x: x["agreement_score"], reverse=True)
        
        return comparison
    
    def export_multi_model_results(self, 
                                  results: Dict[str, Dict[str, PlatformResponse]], 
                                  filename: str):
        """Export multi-model results to JSON"""
        
        export_data = {
            "timestamp": datetime.now().isoformat(),
            "platforms": {}
        }
        
        for platform, model_results in results.items():
            export_data["platforms"][platform] = {
                "models": {},
                "comparison": self.compare_models_within_platform(model_results)
            }
            
            for model, response in model_results.items():
                export_data["platforms"][platform]["models"][model] = {
                    "cost": response.cost,
                    "tokens": {"input": response.input_tokens, "output": response.output_tokens},
                    "web_search": response.web_search_used,
                    "error": response.error,
                    "items_count": len(response.ranked_items),
                    "top_5_items": [
                        {"rank": item.rank, "title": item.title}
                        for item in response.ranked_items[:5]
                    ]
                }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n📄 Multi-model results exported to: {filename}")
    
    def print_multi_model_summary(self, results: Dict[str, Dict[str, PlatformResponse]]):
        """Print summary of multi-model results"""
        
        print("\n" + "="*70)
        print("MULTI-MODEL ANALYSIS SUMMARY")
        print("="*70)
        
        total_cost = 0
        total_queries = 0
        
        for platform, model_results in results.items():
            print(f"\n📱 {platform.upper()}")
            print("-" * 40)
            
            platform_cost = 0
            successful_models = 0
            
            for model, response in model_results.items():
                total_queries += 1
                if not response.error:
                    successful_models += 1
                    platform_cost += response.cost
                    total_cost += response.cost
                    print(f"  ✅ {model}: {len(response.ranked_items)} items (${response.cost:.4f})")
                else:
                    print(f"  ❌ {model}: {response.error}")
            
            print(f"  Platform total: ${platform_cost:.4f} ({successful_models}/{len(model_results)} models)")
            
            # Show consensus items for this platform
            comparison = self.compare_models_within_platform(model_results)
            if comparison["consensus_items"]:
                print(f"\n  🤝 Top consensus items (appearing in multiple models):")
                for item in comparison["consensus_items"][:3]:
                    print(f"     - {item['item']} ({len(item['models'])} models agree)")
        
        print(f"\n💰 TOTAL COST: ${total_cost:.4f} across {total_queries} queries")
        print(f"📊 Average cost per query: ${total_cost/total_queries:.4f}" if total_queries > 0 else "")