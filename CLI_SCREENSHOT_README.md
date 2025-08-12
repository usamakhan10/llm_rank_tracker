# CLI Screenshot Feature Documentation

## Overview
The LLM Rank Tracker now includes a powerful CLI screenshot feature that captures terminal output as professional PNG images. This is perfect for documentation, reports, and sharing results visually.

## Features

### 🎨 Visual Enhancements
- **Dark Terminal Theme**: Professional dark background (RGB: 30, 30, 30)
- **Color-Coded Output**: Different colors for different elements
  - Blue: Headers and platforms
  - Green: Success messages
  - Red: Error messages
  - Yellow: Warnings and rankings
  - Cyan: Cost information
  - Purple: Platform names
  - Light Blue: URLs and links
  - White: Product titles
  - Gray: Separators and dim text

### 📸 Screenshot Capabilities
- Captures full CLI output as PNG images
- Preserves formatting and structure
- Includes timestamps and location information
- Shows rankings, costs, and URLs
- Supports single and multiple query comparisons

## Installation

```bash
pip install Pillow
```

Or install all requirements:
```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage
Add the `--screenshot` flag to any tracker command:

```bash
python tracker_cli.py -k "best coffee jar" --screenshot
```

### With Multiple Options
Combine screenshot with other export options:

```bash
python tracker_cli.py -k "top smartphones 2024" \
  --screenshot \
  --export-json results.json \
  --export-csv results.csv
```

### Specific Platforms
Query specific platforms with screenshot:

```bash
python tracker_cli.py -k "best laptops" \
  -p chatgpt gemini \
  --screenshot
```

### US Market with Web Search
Capture US-focused results:

```bash
python tracker_cli.py -k "wireless headphones" \
  --screenshot \
  --no-web-search  # or leave enabled for URL extraction
```

## Output Location

Screenshots are saved to: `cli_screenshots/`

Filename format: `cli_output_[keyword]_[timestamp].png`

Example: `cli_output_best_coffee_jar_20240115_143022.png`

## Screenshot Examples

### 1. Main Query Output
Shows complete results from all platforms including:
- Platform names and models
- Rankings (top 10 items)
- Costs and token usage
- URLs when available
- Success/error messages

### 2. Comparison View
Multiple queries displayed side-by-side:
- Top 3 results from each platform
- Cost per query
- Overall statistics

### 3. Feature Showcase
Demonstrates all capabilities:
- Color coding examples
- Usage instructions
- Supported features

## API Integration

### In Python Scripts

```python
from terminal_screenshot import CLIScreenshotCapture
from rank_tracker import KeywordRankTracker

# Initialize
tracker = KeywordRankTracker()
capture = CLIScreenshotCapture()

# Run query
results = tracker.query_all_platforms(
    keyword="best coffee jar",
    platforms=["chatgpt", "perplexity", "gemini"]
)

# Capture screenshot
screenshot_path = capture.capture_tracker_output("best coffee jar", results)
print(f"Screenshot saved: {screenshot_path}")
```

### Custom Screenshots

```python
from terminal_screenshot import TerminalScreenshot

# Create custom output
lines = [
    "=" * 80,
    "CUSTOM HEADER",
    "Custom content here...",
    "=" * 80
]

# Generate image
ts = TerminalScreenshot()
ts.create_text_image(lines, "custom_output.png")
```

## Demo Scripts

### Run Basic Demo
```bash
python run_screenshot_demo.py
```
Creates sample screenshots showing the feature capabilities.

### Run Full Demo
```bash
python demo_cli_screenshots.py
```
Interactive demo with live API queries (requires credentials).

## Use Cases

### 1. Documentation
- Include terminal output in technical documentation
- Show exact command results
- Preserve formatting and colors

### 2. Reports
- Generate visual reports for clients
- Create before/after comparisons
- Document API responses

### 3. Debugging
- Capture exact error messages
- Save output for analysis
- Track changes over time

### 4. Sharing
- Share results on social media
- Include in presentations
- Email visual results

### 5. Archiving
- Keep visual record of queries
- Track ranking changes
- Document costs over time

## Technical Details

### Image Generation
- Uses PIL (Python Imaging Library)
- Monospace font rendering
- Automatic line wrapping
- Dynamic image sizing

### Color Parsing
- Automatic detection of content types
- Keyword-based coloring
- Platform-specific highlighting
- Error/success state colors

### File Management
- Automatic directory creation
- Timestamp-based naming
- Safe filename generation
- UTF-8 encoding support

## Troubleshooting

### Unicode Errors
On Windows, some Unicode characters may cause issues. The system automatically falls back to ASCII representations.

### Font Issues
The system tries to use system monospace fonts:
- Windows: Consolas
- Mac/Linux: DejaVu Sans Mono
- Fallback: Default PIL font

### Large Outputs
Very large outputs may create tall images. Consider using comparison view for multiple queries.

## Configuration

### Customizing Colors
Edit `terminal_screenshot.py`:

```python
self.colors = {
    'header': (100, 200, 255),  # RGB values
    'success': (100, 255, 100),
    # ... customize as needed
}
```

### Adjusting Dimensions
```python
self.width = 120  # Terminal width in characters
self.font_size = 14  # Font size in pixels
self.line_height = 20  # Line spacing
```

## Best Practices

1. **Use for Documentation**: Include screenshots in README files and docs
2. **Archive Results**: Keep visual record of important queries
3. **Compare Changes**: Use before/after screenshots for updates
4. **Client Reports**: Generate professional visuals for presentations
5. **Error Tracking**: Capture error messages for debugging

## Future Enhancements

- [ ] Rich text formatting support
- [ ] Animated GIF generation for multiple queries
- [ ] Custom themes and color schemes
- [ ] Watermark support
- [ ] PDF export option
- [ ] Web interface for viewing screenshots

## Contributing

Feel free to suggest improvements or report issues with the screenshot feature.

## License

Part of the LLM Rank Tracker project.