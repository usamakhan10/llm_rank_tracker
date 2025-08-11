# test_tracker.py
"""Test script to verify the tracker functionality"""

from rank_tracker import KeywordRankTracker
from multi_model_tracker import MultiModelTracker
import json

def test_single_model():
    """Test single model per platform"""
    print("="*60)
    print("TEST 1: Single Model Per Platform")
    print("="*60)
    
    tracker = KeywordRankTracker()
    
    # Test with corrected Perplexity model
    results = tracker.query_all_platforms(
        keyword="best coffee jar",
        platforms=["chatgpt", "perplexity", "gemini"],
        web_search=True,
        parallel=False  # Sequential for debugging
    )
    
    # Print results
    tracker.print_results(results)
    
    # Test export
    tracker.export_to_json(results, "test_single_model.json")
    print("\n[OK] Single model test complete. Results saved to test_single_model.json")
    
    return results

def test_specific_models():
    """Test with specific models"""
    print("\n" + "="*60)
    print("TEST 2: Specific Models")
    print("="*60)
    
    tracker = KeywordRankTracker()
    
    # Test each platform with specific models
    test_configs = [
        ("perplexity", "sonar-pro"),
        ("perplexity", "sonar-reasoning"),
        ("chatgpt", "gpt-4o-mini-2024-07-18"),
        ("gemini", "gemini-2.5-flash")
    ]
    
    for platform, model in test_configs:
        print(f"\nTesting {platform} with model: {model}")
        try:
            response = tracker.clients[platform].query(
                keyword="best coffee jar",
                model_name=model,
                web_search=True
            )
            
            if response.error:
                print(f"  [ERROR] {response.error}")
            else:
                print(f"  [OK] Success: Found {len(response.ranked_items)} items")
                print(f"     Cost: ${response.cost:.4f}")
                if response.ranked_items:
                    print(f"     Top item: {response.ranked_items[0].title}")
        except Exception as e:
            print(f"  [ERROR] Exception: {e}")
    
    print("\n[OK] Specific models test complete")

def test_rank_extraction():
    """Test the improved rank extraction"""
    print("\n" + "="*60)
    print("TEST 3: Rank Extraction")
    print("="*60)
    
    from chatgpt_client import ChatGPTClient
    
    # Test various formats
    test_texts = [
        # Format 1: Standard numbered list
        """1. **Airscape Coffee Canister** - Vacuum sealed
2. **Coffee Gator** - Stainless steel with date tracker
3. **OXO POP Container** - Airtight seal""",
        
        # Format 2: Mixed formatting
        """Here are the best coffee jars:
1. **Fellow Atmos** 
   Available in multiple sizes
2. **Planetary Design Airscape**
   Removes air to preserve freshness
**Coffee Vault** - Premium option""",
        
        # Format 3: Bullet points
        """• **Mason Jar with Lid** - Classic choice
• **Bodum Coffee Vault** - Danish design
• **Friis Vault** - CO2 venting technology"""
    ]
    
    # Use a concrete implementation to test the base class method
    client = ChatGPTClient()
    
    for i, text in enumerate(test_texts, 1):
        print(f"\nTest case {i}:")
        print("-" * 30)
        items = client.extract_rankings(text)
        for item in items:
            print(f"  {item.rank}. {item.title}")
            if item.description:
                print(f"     -> {item.description}")
    
    print("\n[OK] Rank extraction test complete")

def test_average_rankings():
    """Test average ranking calculation"""
    print("\n" + "="*60)
    print("TEST 4: Average Rankings")
    print("="*60)
    
    # Create mock responses with overlapping items
    from base_client import PlatformResponse, RankResult
    
    mock_results = {
        "chatgpt": PlatformResponse(
            platform="ChatGPT",
            model="gpt-4",
            raw_text="",
            ranked_items=[
                RankResult(1, "Airscape Coffee Canister"),
                RankResult(2, "Coffee Gator"),
                RankResult(3, "OXO Container")
            ],
            input_tokens=100,
            output_tokens=200,
            cost=0.01
        ),
        "gemini": PlatformResponse(
            platform="Gemini",
            model="gemini-pro",
            raw_text="",
            ranked_items=[
                RankResult(1, "Coffee Gator Canister"),  # Similar to Coffee Gator
                RankResult(2, "Airscape"),  # Similar to Airscape
                RankResult(3, "Fellow Atmos")
            ],
            input_tokens=100,
            output_tokens=200,
            cost=0.01
        )
    }
    
    tracker = KeywordRankTracker()
    avg_rankings = tracker.calculate_average_rankings(mock_results)
    
    print("\nAverage Rankings:")
    for title, data in avg_rankings.items():
        print(f"  - {title}")
        print(f"    Average Rank: {data['average_rank']}")
        print(f"    Platforms: {', '.join(data['platforms'])}")
        print(f"    Individual Ranks: {data['individual_ranks']}")
    
    print("\n[OK] Average rankings test complete")

if __name__ == "__main__":
    print("\n=== Running Keyword Rank Tracker Tests ===\n")
    
    # Run tests
    test_rank_extraction()
    test_average_rankings()
    test_specific_models()
    
    # Run full test (costs money)
    print("\n" + "="*60)
    print("[WARNING] The next test will make real API calls and incur costs.")
    response = input("Do you want to run the full API test? (y/n): ")
    
    if response.lower() == 'y':
        test_single_model()
        print("\n[OK] All tests complete!")
    else:
        print("\n[SKIPPED] API test")
    
    print("\n=== Test suite finished ===")