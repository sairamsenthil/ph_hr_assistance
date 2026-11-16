
import json
import re
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
CONTEXT_LIMIT = 512


def load_pages():
    with open(PAGES_FILE, "r", encoding="utf-8") as file:
        return [json.loads(line) for line in file if line.strip()]


def main():
    tokenizer = Tokenizer.from_pretrained(TOKENIZER_NAME)
    tokenizer.no_truncation()

    pages = load_pages()
    oversized_pages = []

    for page in pages:
        text = page.get("cleaned_text", "")
        token_count = len(tokenizer.encode(text).ids)

        if token_count > CONTEXT_LIMIT:
            oversized_pages.append({
                "page": page["metadata"]["page"],
                "text": text,
                "words": len(text.split()),
                "tokens": token_count
            })

    # Pages 3–6 are known TOC pages.
    policy_pages = [
        page for page in oversized_pages
        if page["page"] not in {3, 4, 5, 6}
    ]

    print("\n--- OVERSIZED POLICY PAGE INSPECTION ---")
    print(f"Policy pages to inspect: {len(policy_pages)}")

    for page in policy_pages:
        text = page["text"]

        dotted_runs = re.findall(r"\.{3,}", text)
        underscore_runs = re.findall(r"_{3,}", text)

        print("\n" + "=" * 65)
        print(f"PAGE: {page['page']}")
        print(f"Words: {page['words']}")
        print(f"Tokens: {page['tokens']}")
        print(f"Dotted runs: {len(dotted_runs)}")
        print(f"Underscore runs: {len(underscore_runs)}")

        print("\n--- FULL PAGE TEXT ---")
        print(text)


if __name__ == "__main__":
    main()
