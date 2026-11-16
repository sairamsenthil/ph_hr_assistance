
import json
from collections import Counter
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]

INPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "chunks"
    / "token_aware"
    / "token_aware_chunks.jsonl"
)

MAX_TOKENS = 460


def main():
    with open(INPUT_FILE, "r", encoding="utf-8") as file:
        chunks = [
            json.loads(line)
            for line in file
            if line.strip()
        ]

    ids = [chunk["chunk_id"] for chunk in chunks]
    token_counts = [chunk["token_count"] for chunk in chunks]

    empty_chunks = [
        chunk for chunk in chunks
        if not chunk["text"].strip()
    ]

    oversized = [
        chunk for chunk in chunks
        if chunk["token_count"] > MAX_TOKENS
    ]

    small_chunks = [
        chunk for chunk in chunks
        if chunk["token_count"] < 100
    ]

    missing_metadata = [
        chunk for chunk in chunks
        if not chunk.get("major_section")
        or not chunk.get("policy_number")
    ]

    invalid_page_ranges = [
        chunk for chunk in chunks
        if chunk["page_start"] > chunk["page_end"]
    ]

    page_counts = Counter(
        chunk["page_start"] for chunk in chunks
    )

    print("\n--- TOKEN-AWARE CHUNK VALIDATION ---")
    print(f"Total chunks: {len(chunks)}")
    print(f"Unique IDs: {len(ids) == len(set(ids))}")
    print(
        f"Sequential indexes: "
        f"{[c['chunk_index'] for c in chunks] == list(range(len(chunks)))}"
    )
    print(f"Empty chunks: {len(empty_chunks)}")
    print(f"Maximum tokens: {max(token_counts, default=0)}")
    print(f"Minimum tokens: {min(token_counts, default=0)}")
    print(f"Chunks exceeding {MAX_TOKENS}: {len(oversized)}")
    print(f"Chunks below 100 tokens: {len(small_chunks)}")
    print(f"Missing section/policy metadata: {len(missing_metadata)}")
    print(f"Invalid page ranges: {len(invalid_page_ranges)}")

    print("\n--- CHUNK SIZE DISTRIBUTION ---")

    ranges = [
        (0, 99),
        (100, 199),
        (200, 299),
        (300, 399),
        (400, 460)
    ]

    for lower, upper in ranges:
        count = sum(
            lower <= value <= upper
            for value in token_counts
        )
        print(f"{lower}-{upper} tokens: {count}")

    print("\n--- SMALL CHUNKS ---")

    for chunk in small_chunks:
        print(
            f"Page {chunk['page_start']} | "
            f"Tokens: {chunk['token_count']} | "
            f"Text: {chunk['text'][:100]!r}"
        )

    print("\n--- CHUNKS PER PAGE ---")

    for page, count in sorted(page_counts.items()):
        if count > 1:
            print(f"Page {page}: {count} chunks")


if __name__ == "__main__":
    main()
