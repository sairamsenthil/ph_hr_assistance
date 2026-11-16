
import json
from pathlib import Path
from tokenizers import Tokenizer

PROJECT_ROOT = Path(__file__).resolve().parents[3]

PAGES_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "hr_policy_pages.jsonl"
)

TOKENIZER_NAME = "mixedbread-ai/mxbai-embed-large-v1"


def load_pages():
    with open(PAGES_FILE, "r", encoding="utf-8") as file:
        return [json.loads(line) for line in file if line.strip()]


def main():
    tokenizer = Tokenizer.from_pretrained(TOKENIZER_NAME)
    tokenizer.no_truncation()

    pages = load_pages()
    results = []

    for page in pages:
        text = page.get("cleaned_text", "")

        results.append({
            "page": page["metadata"]["page"],
            "words": len(text.split()),
            "tokens": len(tokenizer.encode(text).ids),
            "characters": len(text)
        })

    print("\n--- SOURCE PAGE TOKEN AUDIT ---")
    print(f"Total pages: {len(results)}")

    print("\n--- TOP 20 PAGES BY TOKEN COUNT ---")

    for item in sorted(
        results,
        key=lambda x: x["tokens"],
        reverse=True
    )[:20]:
        print(
            f"Page {item['page']:>3} | "
            f"Words: {item['words']:>4} | "
            f"Tokens: {item['tokens']:>5} | "
            f"Characters: {item['characters']:>5}"
        )

    print("\n--- FIRST 8 PAGES ---")

    for item in results[:8]:
        print(
            f"Page {item['page']:>3} | "
            f"Words: {item['words']:>4} | "
            f"Tokens: {item['tokens']:>5}"
        )


if __name__ == "__main__":
    main()
