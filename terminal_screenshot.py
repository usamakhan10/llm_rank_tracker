"""
Terminal Screenshot Capture for LLM Rank Tracker
Captures beautifully formatted CLI output as images
"""

import os
import io
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from PIL import Image, ImageDraw, ImageFont
import textwrap

class TerminalScreenshot:
    """Captures terminal output and converts to images"""
    
    def __init__(self):
        self.buffer = []
        self.width = 120  # Terminal width in characters
        self.height = 40  # Terminal height in lines
        self.font_size = 14
        self.line_height = 20
        self.padding = 20
        self.bg_color = (30, 30, 30)  # Dark terminal background
        self.text_color = (220, 220, 220)  # Light gray text
        
        # Color scheme for different elements
        self.colors = {
            'header': (100, 200, 255),  # Blue
            'success': (100, 255, 100),  # Green
            'error': (255, 100, 100),    # Red
            'warning': (255, 200, 100),  # Yellow
            'platform': (200, 150, 255), # Purple
            'cost': (100, 255, 200),     # Cyan
            'rank': (255, 255, 100),     # Yellow
            'title': (255, 255, 255),    # White
            'url': (100, 150, 255),      # Link blue
            'dim': (150, 150, 150),      # Gray
        }
    
    def create_text_image(self, text_lines: List[str], filename: str = None) -> Image:
        """Convert text lines to an image"""
        
        # Calculate image dimensions
        img_width = self.width * 8 + self.padding * 2  # Approx 8 pixels per character
        img_height = len(text_lines) * self.line_height + self.padding * 2
        
        # Create image with dark background
        img = Image.new('RGB', (img_width, img_height), self.bg_color)
        draw = ImageDraw.Draw(img)
        
        # Try to use a monospace font
        try:
            # Windows
            font = ImageFont.truetype("consola.ttf", self.font_size)
        except:
            try:
                # Mac/Linux
                font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", self.font_size)
            except:
                # Fallback to default
                font = ImageFont.load_default()
        
        # Draw each line
        y_position = self.padding
        for line in text_lines:
            # Parse line for color codes
            color = self.text_color
            
            # Detect line type and apply colors
            if line.startswith('=') or line.startswith('-'):
                color = self.colors['dim']
            elif 'ERROR' in line or '❌' in line or '[ERROR]' in line:
                color = self.colors['error']
            elif 'SUCCESS' in line or '✅' in line or '[SUCCESS]' in line:
                color = self.colors['success']
            elif 'WARNING' in line or '⚠️' in line or '[WARNING]' in line:
                color = self.colors['warning']
            elif any(platform in line.upper() for platform in ['CHATGPT', 'PERPLEXITY', 'GEMINI']):
                color = self.colors['platform']
            elif '$' in line and ('cost' in line.lower() or 'total' in line.lower()):
                color = self.colors['cost']
            elif line.strip().startswith(tuple(str(i) + '.' for i in range(1, 11))):
                color = self.colors['rank']
            elif 'http' in line.lower() or 'url' in line.lower():
                color = self.colors['url']
            elif line.startswith('LLM RANK TRACKER') or line.startswith('Query #'):
                color = self.colors['header']
            
            draw.text((self.padding, y_position), line, fill=color, font=font)
            y_position += self.line_height
        
        if filename:
            img.save(filename)
            
        return img
    
    def capture_results_output(self, results: Dict[str, Any], keyword: str) -> List[str]:
        """Format results for terminal display"""
        lines = []
        
        # Header
        lines.append("=" * 80)
        lines.append(f"LLM RANK TRACKER - RESULTS FOR: {keyword}")
        lines.append(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"Location: United States (US)")
        lines.append("=" * 80)
        lines.append("")
        
        # Process each platform
        for platform, response in results.items():
            lines.append(f"{'='*60}")
            lines.append(f"PLATFORM: {platform.upper()}")
            lines.append(f"Model: {response.model}")
            lines.append(f"Cost: ${response.cost:.4f}")
            lines.append(f"Tokens: {response.input_tokens} in / {response.output_tokens} out")
            lines.append(f"Web Search: {'Yes' if response.web_search_used else 'No'}")
            lines.append("")
            
            if response.error:
                lines.append(f"[ERROR] {response.error}")
            else:
                lines.append("Top Rankings:")
                for item in response.ranked_items[:10]:
                    lines.append(f"  {item.rank}. {item.title}")
                    if item.description:
                        wrapped = textwrap.wrap(item.description, width=70)
                        if wrapped:
                            lines.append(f"     {wrapped[0]}")
                    if hasattr(item, 'url') and item.url:
                        lines.append(f"     URL: {item.url[:70]}...")
            lines.append("")
        
        # Summary section
        lines.append("=" * 80)
        lines.append("SUMMARY")
        lines.append("-" * 80)
        
        total_cost = sum(r.cost for r in results.values() if not r.error)
        total_items = sum(len(r.ranked_items) for r in results.values() if not r.error)
        urls_found = sum(1 for r in results.values() if not r.error 
                        for item in r.ranked_items if hasattr(item, 'url') and item.url)
        
        lines.append(f"Total Cost: ${total_cost:.4f}")
        lines.append(f"Total Items Ranked: {total_items}")
        lines.append(f"URLs Extracted: {urls_found}")
        lines.append(f"Platforms Queried: {len(results)}")
        lines.append("=" * 80)
        
        return lines


class CLIScreenshotCapture:
    """Main class for capturing CLI output as screenshots"""
    
    def __init__(self):
        self.screenshot_dir = Path("cli_screenshots")
        self.screenshot_dir.mkdir(exist_ok=True)
        self.terminal_screenshot = TerminalScreenshot()
    
    def capture_tracker_output(self, keyword: str, results: Dict[str, Any]) -> str:
        """Capture tracker results as screenshot"""
        
        # Generate formatted output
        lines = self.terminal_screenshot.capture_results_output(results, keyword)
        
        # Create filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_keyword = keyword.replace(" ", "_").replace("/", "_")[:30]
        filename = self.screenshot_dir / f"cli_output_{safe_keyword}_{timestamp}.png"
        
        # Create and save image
        self.terminal_screenshot.create_text_image(lines, str(filename))
        
        return str(filename)
    
    def capture_comparison_output(self, results_list: List[Dict[str, Any]]) -> str:
        """Capture comparison of multiple queries"""
        lines = []
        
        # Header
        lines.append("=" * 80)
        lines.append("LLM RANK TRACKER - MULTI-QUERY COMPARISON")
        lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("=" * 80)
        lines.append("")
        
        for idx, result_data in enumerate(results_list, 1):
            keyword = result_data['keyword']
            results = result_data['results']
            
            lines.append(f"Query #{idx}: {keyword}")
            lines.append("-" * 60)
            
            # Show top 3 from each platform
            for platform, response in results.items():
                if not response.error and response.ranked_items:
                    lines.append(f"  {platform.upper()}:")
                    for item in response.ranked_items[:3]:
                        lines.append(f"    {item.rank}. {item.title}")
            
            # Quick stats
            total_cost = sum(r.cost for r in results.values() if not r.error)
            lines.append(f"  Cost: ${total_cost:.4f}")
            lines.append("")
        
        # Overall summary
        lines.append("=" * 80)
        lines.append("OVERALL STATISTICS")
        lines.append("-" * 80)
        
        total_queries = len(results_list)
        total_cost_all = sum(
            sum(r.cost for r in rd['results'].values() if not r.error)
            for rd in results_list
        )
        
        lines.append(f"Total Queries: {total_queries}")
        lines.append(f"Total Cost: ${total_cost_all:.4f}")
        lines.append(f"Average Cost per Query: ${total_cost_all/total_queries:.4f}")
        lines.append("=" * 80)
        
        # Create filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = self.screenshot_dir / f"cli_comparison_{timestamp}.png"
        
        # Create and save image
        self.terminal_screenshot.create_text_image(lines, str(filename))
        
        return str(filename)
    
    def create_styled_output(self, text: str, style: str = "default") -> List[str]:
        """Create styled terminal output"""
        styles = {
            "success": "[SUCCESS] ",
            "error": "[ERROR] ",
            "warning": "[WARNING] ",
            "info": "[INFO] ",
            "header": "=== ",
            "default": ""
        }
        
        prefix = styles.get(style, "")
        lines = text.split('\n')
        return [prefix + line for line in lines]


def capture_live_output():
    """Capture live terminal output during execution"""
    
    class OutputCapture:
        def __init__(self):
            self.terminal = sys.stdout
            self.capture_buffer = io.StringIO()
        
        def write(self, message):
            self.terminal.write(message)
            self.capture_buffer.write(message)
        
        def flush(self):
            self.terminal.flush()
        
        def get_captured(self):
            return self.capture_buffer.getvalue()
        
        def save_as_screenshot(self, filename: str = None):
            captured_text = self.get_captured()
            lines = captured_text.split('\n')
            
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"cli_capture_{timestamp}.png"
            
            ts = TerminalScreenshot()
            ts.create_text_image(lines, filename)
            return filename
    
    return OutputCapture()


# Integration with tracker_cli.py
def add_screenshot_to_cli(results: Dict[str, Any], keyword: str, save_screenshot: bool = False) -> Optional[str]:
    """Add screenshot capability to existing CLI"""
    
    if not save_screenshot:
        return None
    
    capture = CLIScreenshotCapture()
    screenshot_path = capture.capture_tracker_output(keyword, results)
    print(f"\n📸 Screenshot saved: {screenshot_path}")
    return screenshot_path


if __name__ == "__main__":
    # Demo the screenshot capability
    print("\n" + "="*80)
    print("TERMINAL SCREENSHOT DEMO")
    print("="*80)
    
    # Create sample output
    sample_lines = [
        "=" * 80,
        "LLM RANK TRACKER - CLI OUTPUT SCREENSHOT DEMO",
        f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "Location: United States (US)",
        "=" * 80,
        "",
        "PLATFORM: CHATGPT",
        "Model: gpt-4o-mini",
        "Cost: $0.0125",
        "Tokens: 245 in / 567 out",
        "",
        "Top Rankings:",
        "  1. Fellow Atmos Vacuum Canister",
        "     URL: https://example.com/fellow-atmos",
        "  2. Coffee Gator Stainless Steel Container", 
        "     URL: https://example.com/coffee-gator",
        "  3. OXO POP Container",
        "     URL: https://example.com/oxo-pop",
        "",
        "=" * 80,
        "PLATFORM: PERPLEXITY",
        "Model: sonar",
        "Cost: $0.0089",
        "Tokens: 198 in / 423 out",
        "",
        "Top Rankings:",
        "  1. Airscape Coffee Storage Canister",
        "  2. Fellow Atmos Vacuum Canister",
        "  3. Coffee Gator Container",
        "",
        "=" * 80,
        "[SUCCESS] Query completed successfully!",
        "Total Cost: $0.0214",
        "URLs Found: 3",
        "=" * 80
    ]
    
    # Create screenshot
    ts = TerminalScreenshot()
    img = ts.create_text_image(sample_lines, "demo_cli_screenshot.png")
    
    print("\n✅ Demo screenshot created: demo_cli_screenshot.png")
    print("\nThis screenshot shows what the CLI output looks like as an image.")
    print("\nFeatures:")
    print("  • Dark terminal theme")
    print("  • Color-coded output (platforms, costs, URLs)")
    print("  • Preserves formatting and structure")
    print("  • Professional appearance for documentation")