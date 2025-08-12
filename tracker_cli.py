# tracker_cli.py
import argparse
import sys
from rank_tracker import KeywordRankTracker
from datetime import datetime

def main():
    parser = argparse.ArgumentParser(
        description="Multi-platform AI Keyword Rank Tracker",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python tracker_cli.py -k "best coffee jar" 
  python tracker_cli.py -k "top smartphones 2024" -p chatgpt gemini
  python tracker_cli.py -k "best laptops" --export-csv results.csv --export-json results.json
  python tracker_cli.py -k "wireless headphones" --no-web-search --sequential
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
        "--models",
        nargs=3,
        metavar=("CHATGPT", "PERPLEXITY", "GEMINI"),
        help="Specify models for each platform"
    )
    
    parser.add_argument(
        "--no-web-search",
        action="store_true",
        help="Disable web search for all platforms"
    )
    
    parser.add_argument(
        "--sequential",
        action="store_true",
        help="Query platforms sequentially instead of in parallel"
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
    
    parser.add_argument(
        "--txt", "--text",
        action="store_true",
        help="Save all output text to a file named <keyword>.txt"
    )
    
    args = parser.parse_args()
    
    # Initialize tracker
    tracker = KeywordRankTracker()
    
    # Override models if specified
    if args.models:
        model_mapping = {
            "chatgpt": args.models[0],
            "perplexity": args.models[1],
            "gemini": args.models[2]
        }
        
        # Temporarily override query methods to use custom models
        for platform, model in model_mapping.items():
            if platform in tracker.clients:
                original_query = tracker.clients[platform].query
                tracker.clients[platform].query = lambda k, m=model, ws=not args.no_web_search, mt=800, oq=original_query: oq(k, model_name=m, web_search=ws, max_tokens=mt)
    
    if not args.quiet:
        print(f"\n[*] Tracking keyword: '{args.keyword}'")
        print(f"[*] Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        platforms_str = ", ".join(args.platforms) if args.platforms else "all platforms"
        print(f"[*] Querying: {platforms_str}")
        print(f"[*] Web search: {'disabled' if args.no_web_search else 'enabled'}")
        print(f"[*] Mode: {'sequential' if args.sequential else 'parallel'}")
        print("\nQuerying platforms...")
    
    try:
        # Query all platforms
        results = tracker.query_all_platforms(
            keyword=args.keyword,
            platforms=args.platforms,
            web_search=not args.no_web_search,
            parallel=not args.sequential
        )
        
        # Print results to console
        if not args.quiet:
            tracker.print_results(results)
        
        # Export to CSV if requested
        if args.export_csv:
            tracker.export_to_csv(results, args.export_csv)
            if not args.quiet:
                print(f"\n[+] Results exported to CSV: {args.export_csv}")
        
        # Export to JSON if requested
        if args.export_json:
            tracker.export_to_json(results, args.export_json)
            if not args.quiet:
                print(f"[+] Results exported to JSON: {args.export_json}")
        
        # Export to text file if requested
        if args.txt:
            txt_filename = tracker.export_to_txt(results, args.keyword)
            if not args.quiet:
                print(f"[+] Results exported to text file: {txt_filename}")
        
        # Return success
        return 0
        
    except KeyboardInterrupt:
        print("\n\n[!] Operation cancelled by user")
        return 1
    except Exception as e:
        print(f"\n[ERROR] {e}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main())