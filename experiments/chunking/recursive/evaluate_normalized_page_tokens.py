
import json
from pathlib import Path
from tokenizers import Tokenizer

PROJECT_ROOT = Path(__file__).resolve().parents[3]

INPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "experiments"
    / "recursive"
    / "normalized_policy_pages.jsonl"
)

TOKENIZER_NAME = "mixedbread-ai/mxbai-embed-large-v1"
CONTEXT_LIMIT = 512
SAFETY_LIMIT = 460


def main():
    tokenizer = Tokenizer.from_pretrained(TOKENIZER_NAME)
    tokenizer.no_truncation()

    with open(INPUT_FILE, "r", encoding="utf-8") as file:
        pages = [
            json.loads(line)
            for line in file
            if line.strip()
        ]

    results = []

    for page in pages:
        text = page["normalized_text"]
        token_count = len(tokenizer.encode(text).ids)

        results.append({
            "page": page["metadata"]["page"],
            "tokens": token_count,
            "words": len(text.split())
        })

    oversized = [
        item for item in results
        if item["tokens"] > CONTEXT_LIMIT
    ]

    approaching = [
        item for item in results
        if SAFETY_LIMIT <= item["tokens"] <= CONTEXT_LIMIT
    ]

    print("\n--- NORMALIZED PAGE TOKEN ANALYSIS ---")
    print(f"Total pages: {len(results)}")
    print(f"Context limit: {CONTEXT_LIMIT}")
    print(f"Safety limit: {SAFETY_LIMIT}")

    print("\n--- TOKEN STATISTICS ---")
    counts = [item["tokens"] for item in results]

    print(f"Minimum tokens: {min(counts)}")
    print(f"Maximum tokens: {max(counts)}")
    print(f"Average tokens: {sum(counts) / len(counts):.2f}")

    print("\n--- CONTEXT LIMIT ANALYSIS ---")
    print(f"Pages exceeding 512 tokens: {len(oversized)}")
    print(f"Pages approaching limit: {len(approaching)}")

    print("\n--- OVERSIZED PAGES ---")
    for item in sorted(
        oversized,
        key=lambda x: x["tokens"],
        reverse=True
    ):
        print(
            f"Page {item['page']} | "
            f"Words: {item['words']} | "
            f"Tokens: {item['tokens']}"
        )

    print("\n--- APPROACHING LIMIT ---")
    for item in approaching:
        print(
            f"Page {item['page']} | "
            f"Tokens: {item['tokens']}"
        )


if __name__ == "__main__":
    main()
