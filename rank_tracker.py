# rank_tracker.py
import asyncio
import json
import csv
from typing import List, Dict, Any, Optional
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from base_client import PlatformResponse, RankResult
from chatgpt_client import ChatGPTClient
from perplexity_client import PerplexityClient
from gemini_client import GeminiClient

class KeywordRankTracker:
    """Orchestrates multi-platform keyword rank tracking"""
    
    def __init__(self):
        self.clients = {
            "chatgpt": ChatGPTClient(),
            "perplexity": PerplexityClient(),
            "gemini": GeminiClient()
        }
        self.results_history = []
    
    def query_all_platforms(self, 
                           keyword: str,
                           platforms: Optional[List[str]] = None,
                           web_search: bool = True,
                           parallel: bool = True) -> Dict[str, PlatformResponse]:
        """Query multiple platforms for keyword rankings"""
        
        if platforms is None:
            platforms = list(self.clients.keys())
        
        results = {}
        
        if parallel:
            # Parallel execution for faster results
            with ThreadPoolExecutor(max_workers=len(platforms)) as executor:
                future_to_platform = {
                    executor.submit(
                        self.clients[platform].query, 
                        keyword, 
                        web_search=web_search
                    ): platform 
                    for platform in platforms if platform in self.clients
                }
                
                for future in as_completed(future_to_platform):
                    platform = future_to_platform[future]
                    try:
                        results[platform] = future.result()
                    except Exception as e:
                        print(f"Error querying {platform}: {e}")
                        results[platform] = PlatformResponse(
                            platform=platform,
                            model="",
                            raw_text="",
                            ranked_items=[],
                            input_tokens=0,
                            output_tokens=0,
                            cost=0.0,
                            error=str(e)
                        )
        else:
            # Sequential execution for debugging
            for platform in platforms:
                if platform in self.clients:
                    try:
                        results[platform] = self.clients[platform].query(keyword, web_search=web_search)
                    except Exception as e:
                        print(f"Error querying {platform}: {e}")
                        results[platform] = PlatformResponse(
                            platform=platform,
                            model="",
                            raw_text="",
                            ranked_items=[],
                            input_tokens=0,
                            output_tokens=0,
                            cost=0.0,
                            error=str(e)
                        )
        
        # Store results with timestamp
        self.results_history.append({
            "timestamp": datetime.now().isoformat(),
            "keyword": keyword,
            "results": results
        })
        
        return results
    
    def normalize_title(self, title: str) -> str:
        """Normalize title for better comparison"""
        # Remove common words and clean up
        title = title.lower().strip()
        # Remove common suffixes/prefixes
        for word in ['coffee', 'canister', 'container', 'jar', 'vault', 'storage']:
            title = title.replace(word, '')
        # Remove extra whitespace
        title = ' '.join(title.split())
        return title
    
    def find_similar_items(self, title: str, items_dict: Dict[str, List]) -> List[str]:
        """Find similar items using fuzzy matching"""
        normalized = self.normalize_title(title)
        similar = []
        
        for other_title in items_dict.keys():
            other_normalized = self.normalize_title(other_title)
            # Check if main words match
            if normalized in other_normalized or other_normalized in normalized:
                similar.append(other_title)
            # Check if they share significant words
            elif len(set(normalized.split()) & set(other_normalized.split())) >= 2:
                similar.append(other_title)
        
        return similar
    
    def calculate_average_rankings(self, results: Dict[str, PlatformResponse]) -> Dict[str, float]:
        """Calculate average ranking for items across platforms"""
        item_rankings = {}
        
        for platform, response in results.items():
            if response.error:
                continue
            
            for item in response.ranked_items:
                title_key = item.title.lower().strip()
                
                # Find if this item or similar exists
                if title_key not in item_rankings:
                    # Check for similar items
                    found_similar = False
                    for existing_key in item_rankings.keys():
                        if self.normalize_title(title_key) == self.normalize_title(existing_key):
                            item_rankings[existing_key]['ranks'].append(item.rank)
                            item_rankings[existing_key]['platforms'].append(platform)
                            found_similar = True
                            break
                    
                    if not found_similar:
                        item_rankings[title_key] = {
                            'title': item.title,
                            'ranks': [item.rank],
                            'platforms': [platform]
                        }
                else:
                    item_rankings[title_key]['ranks'].append(item.rank)
                    item_rankings[title_key]['platforms'].append(platform)
        
        # Calculate averages
        average_rankings = {}
        for key, data in item_rankings.items():
            avg_rank = sum(data['ranks']) / len(data['ranks'])
            average_rankings[data['title']] = {
                'average_rank': round(avg_rank, 2),
                'appearances': len(data['ranks']),
                'platforms': data['platforms'],
                'individual_ranks': data['ranks']
            }
        
        # Sort by average rank
        return dict(sorted(average_rankings.items(), key=lambda x: x[1]['average_rank']))
    
    def compare_rankings(self, results: Dict[str, PlatformResponse]) -> Dict[str, Any]:
        """Compare rankings across platforms with improved matching"""
        comparison = {
            "summary": {},
            "items_by_platform": {},
            "common_items": [],
            "unique_items": {},
            "average_rankings": {}
        }
        
        all_items = {}
        platform_items = {}
        
        for platform, response in results.items():
            if response.error:
                comparison["summary"][platform] = f"Error: {response.error}"
                continue
            
            comparison["summary"][platform] = {
                "items_found": len(response.ranked_items),
                "model": response.model,
                "cost": response.cost,
                "web_search": response.web_search_used
            }
            
            platform_items[platform] = []
            comparison["items_by_platform"][platform] = []
            
            for item in response.ranked_items:
                item_key = item.title.lower().strip()
                platform_items[platform].append(item_key)
                
                comparison["items_by_platform"][platform].append({
                    "rank": item.rank,
                    "title": item.title,
                    "description": item.description
                })
                
                # Check for similar items
                found_similar = False
                for existing_key in all_items.keys():
                    if self.normalize_title(item_key) == self.normalize_title(existing_key):
                        all_items[existing_key].append(platform)
                        found_similar = True
                        break
                
                if not found_similar:
                    if item_key not in all_items:
                        all_items[item_key] = []
                    all_items[item_key].append(platform)
        
        # Find common items across platforms
        for item_key, platforms in all_items.items():
            if len(platforms) > 1:
                comparison["common_items"].append({
                    "item": item_key,
                    "platforms": platforms,
                    "count": len(platforms)
                })
        
        # Find unique items per platform
        for platform, items in platform_items.items():
            unique = []
            for item in items:
                item_platforms = []
                for key, plats in all_items.items():
                    if self.normalize_title(item) == self.normalize_title(key):
                        item_platforms.extend(plats)
                        break
                if len(set(item_platforms)) == 1:
                    unique.append(item)
            
            if unique:
                comparison["unique_items"][platform] = unique
        
        # Add average rankings
        comparison["average_rankings"] = self.calculate_average_rankings(results)
        
        return comparison
    
    def export_to_csv(self, results: Dict[str, PlatformResponse], filename: str):
        """Export results to CSV file"""
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['platform', 'rank', 'title', 'description', 'model', 'cost', 'web_search']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for platform, response in results.items():
                if response.error:
                    writer.writerow({
                        'platform': platform,
                        'rank': 'ERROR',
                        'title': response.error,
                        'description': '',
                        'model': response.model,
                        'cost': 0,
                        'web_search': False
                    })
                else:
                    for item in response.ranked_items:
                        writer.writerow({
                            'platform': platform,
                            'rank': item.rank,
                            'title': item.title,
                            'description': item.description or '',
                            'model': response.model,
                            'cost': response.cost,
                            'web_search': response.web_search_used
                        })
    
    def export_to_json(self, results: Dict[str, PlatformResponse], filename: str):
        """Export results to JSON file"""
        export_data = {
            "timestamp": datetime.now().isoformat(),
            "results": {}
        }
        
        for platform, response in results.items():
            export_data["results"][platform] = {
                "model": response.model,
                "cost": response.cost,
                "input_tokens": response.input_tokens,
                "output_tokens": response.output_tokens,
                "web_search_used": response.web_search_used,
                "error": response.error,
                "ranked_items": [
                    {
                        "rank": item.rank,
                        "title": item.title,
                        "description": item.description
                    }
                    for item in response.ranked_items
                ],
                "raw_text": response.raw_text
            }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
    
    def generate_results_text(self, results: Dict[str, PlatformResponse]) -> str:
        """Generate formatted results text and return as string"""
        output_lines = []
        
        for platform, response in results.items():
            output_lines.append("=" * 60)
            output_lines.append(f"Platform: {platform.upper()}")
            output_lines.append(f"Model: {response.model}")
            output_lines.append(f"Cost: ${response.cost:.4f}")
            output_lines.append(f"Tokens: {response.input_tokens} in / {response.output_tokens} out")
            output_lines.append(f"Web Search: {response.web_search_used}")
            
            if response.error:
                output_lines.append(f"ERROR: {response.error}")
            else:
                output_lines.append("\nTop Rankings:")
                for item in response.ranked_items[:5]:  # Show top 5
                    output_lines.append(f"  {item.rank}. {item.title}")
                    if item.description:
                        output_lines.append(f"     {item.description[:100]}...")
        
        output_lines.append("=" * 60)
        output_lines.append("COMPARISON & ANALYSIS")
        comparison = self.compare_rankings(results)
        
        # Show average rankings
        output_lines.append("\n📊 AVERAGE RANKINGS (sorted by best average):")
        output_lines.append("-" * 50)
        for i, (title, data) in enumerate(list(comparison["average_rankings"].items())[:10], 1):
            output_lines.append(f"{i}. {title}")
            output_lines.append(f"   Average Rank: {data['average_rank']} | Appears on: {data['appearances']} platform(s)")
            output_lines.append(f"   Individual ranks: {data['individual_ranks']} ({', '.join(data['platforms'])})")
        
        output_lines.append("\n🔗 Common items across platforms:")
        for common in comparison["common_items"][:5]:
            output_lines.append(f"  - {common['item']} (found on: {', '.join(common['platforms'])})")
        
        total_cost = sum(r.cost for r in results.values() if not r.error)
        output_lines.append(f"\n💰 Total cost: ${total_cost:.4f}")
        
        return "\n".join(output_lines)
    
    def export_to_txt(self, results: Dict[str, PlatformResponse], keyword: str):
        """Export results to text file named after the keyword"""
        # Clean the keyword to create a valid filename
        clean_keyword = "".join(c for c in keyword if c.isalnum() or c in (' ', '-', '_')).rstrip()
        clean_keyword = clean_keyword.replace(' ', '_')
        filename = f"{clean_keyword}.txt"
        
        # Get formatted results text
        results_text = self.generate_results_text(results)
        
        # Add header with timestamp and keyword
        header = f"Keyword Rank Tracker Results\n"
        header += f"Keyword: {keyword}\n"
        header += f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        header += "=" * 60 + "\n\n"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(header + results_text)
        
        return filename
    
    def print_results(self, results: Dict[str, PlatformResponse]):
        """Print formatted results to console"""
        for platform, response in results.items():
            print(f"\n{'='*60}")
            print(f"Platform: {platform.upper()}")
            print(f"Model: {response.model}")
            print(f"Cost: ${response.cost:.4f}")
            print(f"Tokens: {response.input_tokens} in / {response.output_tokens} out")
            print(f"Web Search: {response.web_search_used}")
            
            if response.error:
                print(f"ERROR: {response.error}")
            else:
                print(f"\nTop Rankings:")
                for item in response.ranked_items[:5]:  # Show top 5
                    print(f"  {item.rank}. {item.title}")
                    if item.description:
                        print(f"     {item.description[:100]}...")
        
        print(f"\n{'='*60}")
        print("COMPARISON & ANALYSIS")
        comparison = self.compare_rankings(results)
        
        # Show average rankings
        print("\n📊 AVERAGE RANKINGS (sorted by best average):")
        print("-" * 50)
        for i, (title, data) in enumerate(list(comparison["average_rankings"].items())[:10], 1):
            print(f"{i}. {title}")
            print(f"   Average Rank: {data['average_rank']} | Appears on: {data['appearances']} platform(s)")
            print(f"   Individual ranks: {data['individual_ranks']} ({', '.join(data['platforms'])})")
        
        print("\n🔗 Common items across platforms:")
        for common in comparison["common_items"][:5]:
            print(f"  - {common['item']} (found on: {', '.join(common['platforms'])})")
        
        total_cost = sum(r.cost for r in results.values() if not r.error)
        print(f"\n💰 Total cost: ${total_cost:.4f}")