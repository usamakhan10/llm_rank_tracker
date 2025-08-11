# main.py
import argparse
from dataforseo_gemini import DataForSEOGemini

def main():
    parser = argparse.ArgumentParser(description="Simple DataForSEO → Gemini demo")
    parser.add_argument("--prompt", "-p", required=True, help="User prompt / keyword")
    parser.add_argument("--model", "-m", default="gemini-2.5-flash", help="Gemini model name")
    parser.add_argument("--web-search", action="store_true", help="Enable web_search if supported")
    args = parser.parse_args()

    cli = DataForSEOGemini(timeout_s=130)  # allow longer Live calls
    print("Listing first models (for info)...")
    models = cli.list_models()
    print([m.get("model_name") for m in models[:5]])

    print("\nRunning Live prompt...")
    result = cli.live(
        user_prompt=args.prompt,
        model_name=args.model,
        system_message="Be concise and list top results if asked.",
        web_search=args.web_search,
        temperature=0.2,
        max_output_tokens=400
    )

    print("\n--- Metrics ---")
    print("Input tokens:", result.get("input_tokens"))
    print("Output tokens:", result.get("output_tokens"))
    print("Money spent (LLM):", result.get("money_spent"))

    print("\n--- Text output ---")
    print(cli.extract_text(result))

if __name__ == "__main__":
    main()
