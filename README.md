# Multi-Platform AI Keyword Rank Tracker

A Python tool for tracking keyword rankings across multiple AI platforms (ChatGPT, Perplexity, and Gemini) using DataForSEO APIs.

## Features

- **Multi-Platform Support**: Query ChatGPT, Perplexity, and Gemini simultaneously
- **Unified Interface**: Consistent API across all platforms via abstract base class
- **Rank Extraction**: Automatically parse and extract ranked items from AI responses
- **Parallel Processing**: Query multiple platforms concurrently for faster results
- **Export Options**: Save results to CSV or JSON formats
- **Cost Tracking**: Monitor API usage costs per query
- **Comparison Analysis**: Compare rankings across platforms to find common/unique items

## Installation

1. Clone the repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your DataForSEO credentials
```

## Usage

### Basic Usage
```bash
# Query all platforms for a keyword
python tracker_cli.py -k "best coffee jar"

# Query specific platforms
python tracker_cli.py -k "top smartphones 2024" -p chatgpt gemini

# Export results
python tracker_cli.py -k "best laptops" --export-csv results.csv --export-json results.json

# Disable web search
python tracker_cli.py -k "wireless headphones" --no-web-search
```

### Python API
```python
from rank_tracker import KeywordRankTracker

tracker = KeywordRankTracker()
results = tracker.query_all_platforms("best coffee jar")
tracker.print_results(results)
tracker.export_to_csv(results, "rankings.csv")
```

## Architecture

### Core Components

1. **base_client.py**: Abstract base class defining the interface for all platform clients
   - `BaseLLMClient`: Abstract methods for model listing and querying
   - `RankResult`: Data class for ranked items
   - `PlatformResponse`: Unified response model
   - Rank extraction logic with multiple pattern matching strategies

2. **Platform Clients**:
   - `chatgpt_client.py`: ChatGPT/OpenAI integration
   - `perplexity_client.py`: Perplexity AI integration  
   - `gemini_client.py`: Google Gemini integration (wrapper around existing DataForSEO client)

3. **rank_tracker.py**: Orchestration layer
   - Parallel/sequential platform querying
   - Results comparison and analysis
   - Export functionality (CSV/JSON)
   - Cost tracking and aggregation

4. **tracker_cli.py**: Command-line interface
   - Argument parsing
   - Progress indicators
   - Formatted output display

## API Endpoints Used

All platforms are accessed via DataForSEO's unified API:
- **Base URL**: `https://api.dataforseo.com`
- **ChatGPT**: `/v3/ai_optimization/chat_gpt/llm_responses/live`
- **Perplexity**: `/v3/ai_optimization/perplexity/llm_responses/live`
- **Gemini**: `/v3/ai_optimization/gemini/llm_responses/live`

## Next Steps for Production

### High Priority
1. **Enhanced Rank Extraction**
   - Add support for table parsing
   - Handle more complex response formats
   - Implement confidence scoring for extracted ranks

2. **Error Handling & Resilience**
   - Implement retry logic with exponential backoff
   - Add rate limiting protection
   - Handle API quota exceeded scenarios

3. **Testing Infrastructure**
   - Unit tests for rank extraction logic
   - Integration tests with mock API responses
   - End-to-end testing suite

### Medium Priority
4. **Performance Optimization**
   - Implement caching layer for repeated queries
   - Add request batching for multiple keywords
   - Optimize token usage per platform

5. **Advanced Features**
   - Scheduled tracking with cron/task scheduler
   - Web dashboard for visualization
   - Historical trend analysis
   - Keyword position change alerts

6. **Data Persistence**
   - SQLite/PostgreSQL database integration
   - Time-series data storage
   - Query history and analytics

### Low Priority
7. **Additional Platforms**
   - Add direct API support (bypass DataForSEO)
   - Integrate more AI platforms (Cohere, Anthropic direct, etc.)
   - Support for search engines (Google, Bing)

8. **Configuration Management**
   - YAML/JSON config files for complex setups
   - Per-platform configuration options
   - Model selection strategies

## Current Limitations

1. **API Dependency**: Relies entirely on DataForSEO proxy (no direct platform APIs)
2. **Prompt Length**: Limited to 500 characters per DataForSEO constraints
3. **Rate Limits**: 2000 API calls/minute shared across all platforms
4. **Cost**: Each query incurs DataForSEO + LLM provider costs
5. **Rank Extraction**: Pattern matching may miss some ranking formats

## Cost Considerations

- Each platform query costs vary based on:
  - Model selection (GPT-4 vs GPT-3.5, etc.)
  - Token usage (input + output)
  - Web search enablement
  - DataForSEO markup

Monitor costs via the `money_spent` field in responses and aggregate totals in the CLI output.