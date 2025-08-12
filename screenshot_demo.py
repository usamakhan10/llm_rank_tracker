"""
Consolidated Demo Script for CLI Screenshot Feature
Combines all demo functionality in one clean script
"""

import os
from datetime import datetime
from pathlib import Path
from terminal_screenshot import TerminalScreenshot, CLIScreenshotCapture

class ScreenshotDemo:
    """Demo class for screenshot functionality"""
    
    def __init__(self):
        self.capture = CLIScreenshotCapture()
        self.ts = TerminalScreenshot()
        
    def create_sample_output(self) -> list:
        """Generate sample CLI output for demonstration"""
        return [
            "=" * 80,
            "LLM RANK TRACKER - US MARKET RESULTS",
            f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "Location: United States (US)",
            "Keyword: best coffee jar",
            "=" * 80,
            "",
            "PLATFORM: CHATGPT",
            "Model: gpt-4o-mini-2024-07-18",
            "Cost: $0.0125",
            "Tokens: 245 in / 567 out",
            "Web Search: Yes",
            "",
            "Top Rankings:",
            "  1. Fellow Atmos Vacuum Canister",
            "     Premium vacuum-sealed coffee storage",
            "     URL: https://fellowproducts.com/products/atmos",
            "",
            "  2. Coffee Gator Stainless Steel Container",
            "     CO2 release valve and date tracker",
            "     URL: https://coffeegator.com/products/canister",
            "",
            "  3. OXO POP Container",
            "     Airtight seal with one-button design",
            "     URL: https://www.oxo.com/pop-containers.html",
            "",
            "=" * 60,
            "PLATFORM: PERPLEXITY",
            "Model: sonar",
            "Cost: $0.0089",
            "Tokens: 198 in / 423 out",
            "",
            "Top Rankings:",
            "  1. Airscape Coffee Storage Canister",
            "  2. Fellow Atmos Vacuum Canister",
            "  3. Coffee Gator Stainless Steel Container",
            "",
            "=" * 60,
            "PLATFORM: GEMINI",
            "Model: gemini-1.5-flash",
            "Cost: $0.0067",
            "Tokens: 156 in / 389 out",
            "",
            "Top Rankings:",
            "  1. OXO POP Container",
            "  2. Fellow Atmos Vacuum Canister",
            "  3. Rubbermaid Brilliance Container",
            "",
            "=" * 80,
            "SUMMARY STATISTICS",
            "-" * 80,
            "Total Cost: $0.0281",
            "Total Items Ranked: 9",
            "URLs Extracted: 3",
            "Platforms Queried: 3",
            "",
            "[SUCCESS] Query completed successfully!",
            "=" * 80
        ]
    
    def create_comparison_view(self) -> list:
        """Generate multi-query comparison output"""
        return [
            "=" * 80,
            "MULTI-QUERY COMPARISON VIEW",
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "=" * 80,
            "",
            "Query #1: best coffee jar",
            "-" * 60,
            "  CHATGPT: Fellow Atmos, Coffee Gator, OXO POP",
            "  PERPLEXITY: Airscape, Fellow Atmos, Coffee Gator",
            "  GEMINI: OXO POP, Fellow Atmos, Rubbermaid",
            "  Cost: $0.0281",
            "",
            "Query #2: top smartphones 2024",
            "-" * 60,
            "  CHATGPT: iPhone 15 Pro, Galaxy S24, Pixel 8 Pro",
            "  PERPLEXITY: Galaxy S24 Ultra, iPhone 15, OnePlus 12",
            "  GEMINI: iPhone 15 Pro Max, Galaxy S24, Pixel 8",
            "  Cost: $0.0295",
            "",
            "Query #3: best laptops for programming",
            "-" * 60,
            "  CHATGPT: MacBook Pro M3, Dell XPS 15, ThinkPad X1",
            "  PERPLEXITY: MacBook Pro 16\", System76 Lemur, Dell XPS",
            "  GEMINI: MacBook Pro, ThinkPad P1, Dell Precision",
            "  Cost: $0.0312",
            "",
            "=" * 80,
            "OVERALL STATISTICS",
            "-" * 80,
            "Total Queries: 3",
            "Total Cost: $0.0888",
            "Average Cost per Query: $0.0296",
            "Total Items Ranked: 27",
            "=" * 80
        ]
    
    def create_feature_showcase(self) -> list:
        """Generate feature demonstration output"""
        return [
            "=" * 80,
            "CLI SCREENSHOT FEATURE - CAPABILITIES",
            "=" * 80,
            "",
            "COMMAND LINE USAGE:",
            "-" * 40,
            "  Basic screenshot:",
            "    python tracker_cli.py -k 'keyword' --screenshot",
            "",
            "  With data export:",
            "    python tracker_cli.py -k 'keyword' --screenshot \\",
            "      --export-json results.json --export-csv data.csv",
            "",
            "  Specific platforms:",
            "    python tracker_cli.py -k 'keyword' -p chatgpt gemini \\",
            "      --screenshot",
            "",
            "FEATURES:",
            "-" * 40,
            "  [OK] Terminal output as PNG images",
            "  [OK] Dark terminal theme (30, 30, 30)",
            "  [OK] Color-coded elements:",
            "       - Blue: Headers and platforms",
            "       - Green: Success messages",
            "       - Red: Errors",
            "       - Yellow: Rankings",
            "       - Cyan: Costs",
            "       - Purple: Platform names",
            "  [OK] URL extraction and display",
            "  [OK] Cost tracking",
            "  [OK] Multi-query comparison",
            "",
            "OUTPUT:",
            "-" * 40,
            "  Location: cli_screenshots/",
            "  Format: cli_output_[keyword]_[timestamp].png",
            "  Resolution: Dynamic based on content",
            "",
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "=" * 80
        ]
    
    def run_demo(self, demo_type: str = "all"):
        """Run the demo and generate screenshots
        
        Args:
            demo_type: "all", "sample", "comparison", or "features"
        """
        # Ensure directory exists
        os.makedirs("cli_screenshots", exist_ok=True)
        
        screenshots = []
        
        if demo_type in ["all", "sample"]:
            print("\nGenerating sample output screenshot...")
            lines = self.create_sample_output()
            filename = "cli_screenshots/demo_sample_output.png"
            self.ts.create_text_image(lines, filename)
            screenshots.append(filename)
            print(f"[OK] Created: {filename}")
        
        if demo_type in ["all", "comparison"]:
            print("\nGenerating comparison view screenshot...")
            lines = self.create_comparison_view()
            filename = "cli_screenshots/demo_comparison.png"
            self.ts.create_text_image(lines, filename)
            screenshots.append(filename)
            print(f"[OK] Created: {filename}")
        
        if demo_type in ["all", "features"]:
            print("\nGenerating feature showcase screenshot...")
            lines = self.create_feature_showcase()
            filename = "cli_screenshots/demo_features.png"
            self.ts.create_text_image(lines, filename)
            screenshots.append(filename)
            print(f"[OK] Created: {filename}")
        
        return screenshots


def main():
    """Main demo function"""
    print("\n" + "="*80)
    print("CLI SCREENSHOT FEATURE DEMO")
    print("="*80)
    print("\nThis demo generates sample screenshots showing the CLI output")
    print("capture functionality.")
    
    # Check if running in interactive mode
    import sys
    if sys.stdin.isatty():
        print("\nDemo options:")
        print("  1. Generate all demo screenshots")
        print("  2. Sample output only")
        print("  3. Comparison view only")
        print("  4. Feature showcase only")
        
        choice = input("\nEnter choice (1-4, default=1): ").strip() or "1"
        
        demo_types = {
            "1": "all",
            "2": "sample",
            "3": "comparison",
            "4": "features"
        }
        
        demo_type = demo_types.get(choice, "all")
    else:
        # Non-interactive mode - generate all
        print("\nRunning in non-interactive mode. Generating all screenshots...")
        demo_type = "all"
    
    # Run demo
    demo = ScreenshotDemo()
    screenshots = demo.run_demo(demo_type)
    
    print("\n" + "="*80)
    print("DEMO COMPLETED")
    print("="*80)
    print(f"\nGenerated {len(screenshots)} screenshot(s):")
    for screenshot in screenshots:
        print(f"  - {screenshot}")
    
    print("\n" + "="*80)
    print("HOW TO USE IN YOUR PROJECT:")
    print("="*80)
    print("\n1. With CLI:")
    print("   python tracker_cli.py -k 'your keyword' --screenshot")
    print("\n2. In Python code:")
    print("   from terminal_screenshot import CLIScreenshotCapture")
    print("   capture = CLIScreenshotCapture()")
    print("   capture.capture_tracker_output(keyword, results)")
    print("\n3. For custom output:")
    print("   from terminal_screenshot import TerminalScreenshot")
    print("   ts = TerminalScreenshot()")
    print("   ts.create_text_image(lines, 'output.png')")
    print("="*80)


if __name__ == "__main__":
    main()