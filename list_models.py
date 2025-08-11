# list_models.py
"""List all available models for each platform"""

from chatgpt_client import ChatGPTClient
from perplexity_client import PerplexityClient
from gemini_client import GeminiClient

def main():
    print("Fetching available models for each platform...\n")
    
    # ChatGPT models
    print("=" * 60)
    print("CHATGPT MODELS:")
    print("-" * 60)
    try:
        chatgpt = ChatGPTClient()
        models = chatgpt.list_models()
        for model in models:
            print(f"  • {model.get('model_name')}")
            if model.get('web_search_supported'):
                print(f"    └─ Web search: ✓")
    except Exception as e:
        print(f"  Error: {e}")
    
    # Perplexity models
    print("\n" + "=" * 60)
    print("PERPLEXITY MODELS:")
    print("-" * 60)
    try:
        perplexity = PerplexityClient()
        models = perplexity.list_models()
        for model in models:
            print(f"  • {model.get('model_name')}")
            if model.get('web_search_supported'):
                print(f"    └─ Web search: ✓")
    except Exception as e:
        print(f"  Error: {e}")
    
    # Gemini models
    print("\n" + "=" * 60)
    print("GEMINI MODELS:")
    print("-" * 60)
    try:
        gemini = GeminiClient()
        models = gemini.list_models()
        for model in models:
            print(f"  • {model.get('model_name')}")
            if model.get('web_search_supported'):
                print(f"    └─ Web search: ✓")
    except Exception as e:
        print(f"  Error: {e}")

if __name__ == "__main__":
    main()