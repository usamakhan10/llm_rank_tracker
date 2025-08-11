# enhanced_cli.py
"""Enhanced CLI with multi-model support and better error handling"""

import argparse
import sys
from rank_tracker import KeywordRankTracker
from multi_model_tracker import MultiModelTracker
from datetime import datetime

def main():
    parser = argparse.ArgumentParser(
        description="Enhanced Multi-Platform AI Keyword Rank Tracker",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Single model per platform (default)
  python enhanced_cli.py -k "best coffee jar"
  
  # Query all available models
  python enhanced_cli.py -k "best coffee jar" --all-models
  
  # Specific platforms with all models
  python enhanced_cli.py -k "top smartphones" --all-models -p chatgpt perplexity
  
  # Export multi-model results
  python enhanced_cli.py -k "best laptops" --all-models --export-json results.json
  
  # Use specific models
  python enhanced_cli.py -k "wireless headphones" --chatgpt-model gpt-4o-2024-11-20 --perplexity-model sonar-pro --gemini-model gemini-2.5-pro
        """
    )
    
    parser.add_argument(
        "-k", "--keyword", 
        required=True, 
        help="Keyword/query to track rankings for"
    )
    
    parser.add_argument(
        "-p", "--platforms", 
        nargs="+", 
        choices=["chatgpt", "perplexity", "gemini"],
        default=None,
        help="Platforms to query (default: all)"
    )
    
    parser.add_argument(
        "--all-models",
        action="store_true",
        help="Query all available models for each platform"
    )
    
    parser.add_argument(
        "--chatgpt-model",
        default=None,
        help="Specific ChatGPT model to use"
    )
    
    parser.add_argument(
        "--perplexity-model",
        default=None,
        help="Specific Perplexity model to use (sonar, sonar-pro, sonar-reasoning, sonar-reasoning-pro)"
    )
    
    parser.add_argument(
        "--gemini-model",
        default=None,
        help="Specific Gemini model to use"
    )
    
    parser.add_argument(
        "--no-web-search",
        action="store_true",
        help="Disable web search for all platforms"
    )
    
    parser.add_argument(
        "--export-csv",
        metavar="FILE",
        help="Export results to CSV file"
    )
    
    parser.add_argument(
        "--export-json",
        metavar="FILE",
        help="Export results to JSON file"
    )
    
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress console output"
    )
    
    args = parser.parse_args()
    
    if not args.quiet:
        print(f"\n🔍 Enhanced Keyword Rank Tracker")
        print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🎯 Keyword: '{args.keyword}'")
        platforms_str = ", ".join(args.platforms) if args.platforms else "all platforms"
        print(f"🌐 Platforms: {platforms_str}")
        print(f"🔎 Web search: {'disabled' if args.no_web_search else 'enabled'}")
    
    try:
        if args.all_models:
            # Multi-model mode
            if not args.quiet:
                print(f"🚀 Mode: Multi-model analysis")
                print("\nQuerying all available models...")
            
            tracker = MultiModelTracker()
            results = tracker.query_all_models(
                keyword=args.keyword,
                platforms=args.platforms,
                web_search=not args.no_web_search
            )
            
            if not args.quiet:
                tracker.print_multi_model_summary(results)
            
            if args.export_json:
                tracker.export_multi_model_results(results, args.export_json)
                if not args.quiet:
                    print(f"✅ Multi-model results exported to: {args.export_json}")
        
        else:
            # Single model mode
            if not args.quiet:
                print(f"⚡ Mode: Single model per platform")
                print("\nQuerying platforms...")
            
            tracker = KeywordRankTracker()
            
            # Override specific models if provided
            model_overrides = {}
            if args.chatgpt_model:
                model_overrides['chatgpt'] = args.chatgpt_model
            if args.perplexity_model:
                model_overrides['perplexity'] = args.perplexity_model
            if args.gemini_model:
                model_overrides['gemini'] = args.gemini_model
            
            # Query with specific models
            results = {}
            platforms = args.platforms or list(tracker.clients.keys())
            
            for platform in platforms:
                if platform in tracker.clients:
                    model = model_overrides.get(platform)
                    try:
                        results[platform] = tracker.clients[platform].query(
                            keyword=args.keyword,
                            model_name=model,
                            web_search=not args.no_web_search
                        )
                    except Exception as e:
                        if not args.quiet:
                            print(f"❌ Error querying {platform}: {e}")
            
            if not args.quiet:
                tracker.print_results(results)
            
            if args.export_csv:
                tracker.export_to_csv(results, args.export_csv)
                if not args.quiet:
                    print(f"✅ Results exported to CSV: {args.export_csv}")
            
            if args.export_json:
                tracker.export_to_json(results, args.export_json)
                if not args.quiet:
                    print(f"✅ Results exported to JSON: {args.export_json}")
        
        return 0
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Operation cancelled by user")
        return 1
    except Exception as e:
        print(f"\n❌ Error: {e}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main())