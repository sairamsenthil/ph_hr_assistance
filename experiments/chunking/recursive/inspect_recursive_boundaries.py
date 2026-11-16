
import json
import re
from pathlib import Path
from collections import Counter

PROJECT_ROOT = Path(__file__).resolve().parents[3]

CHUNK_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "chunks"
    / "recursive"
    / "recursive_chunks.jsonl"
)


def load_chunks():
    with open(CHUNK_FILE, "r", encoding="utf-8") as file:
        return [json.loads(line) for line in file if line.strip()]


def inspect_boundary(previous, current):
    previous_words = previous["text"].split()
    current_text = current["text"]

    current_matches = list(re.finditer(r"\S+", current_text))

    if len(previous_words) < 50 or len(current_matches) <= 50:
        return "INSUFFICIENT_CONTENT"

    # The first 50 words in the current chunk are overlap.
    # The next word is the first new word.
    previous_word = current_matches[49]
    next_word = current_matches[50]

    gap = current_text[previous_word.end():next_word.start()]
    previous_text = previous_word.group()

    if gap.count("\n") >= 2:
        return "PARAGRAPH"

    if "\n" in gap:
        return "LINE"

    if re.search(r"[.!?][\"')\]]*$", previous_text):
        return "SENTENCE"

    return "WORD_FALLBACK"


def main():
    chunks = load_chunks()

    results = []

    for previous, current in zip(chunks, chunks[1:]):
        boundary_type = inspect_boundary(previous, current)

        results.append({
            "previous_chunk": previous["chunk_id"],
            "current_chunk": current["chunk_id"],
            "boundary_type": boundary_type,
            "previous_page_end": previous["page_end"],
            "current_page_start": current["page_start"]
        })

    counts = Counter(
        result["boundary_type"] for result in results
    )

    print("\n--- RECURSIVE BOUNDARY INSPECTION ---")
    print(f"Total chunks: {len(chunks)}")
    print(f"Boundaries inspected: {len(results)}")

    print("\n--- BOUNDARY SUMMARY ---")

    for category in [
        "PARAGRAPH",
        "LINE",
        "SENTENCE",
        "WORD_FALLBACK",
        "INSUFFICIENT_CONTENT"
    ]:
        print(f"{category}: {counts[category]}")

    print("\n--- FIRST 20 BOUNDARIES ---")

    for result in results[:20]:
        print(
            f"{result['previous_chunk']} -> "
            f"{result['current_chunk']} | "
            f"{result['boundary_type']} | "
            f"Pages: {result['previous_page_end']} -> "
            f"{result['current_page_start']}"
        )


if __name__ == "__main__":
    main()
