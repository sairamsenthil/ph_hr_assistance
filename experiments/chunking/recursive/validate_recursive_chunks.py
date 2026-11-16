
import json
from pathlib import Path
from statistics import mean

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


def main():
    chunks = load_chunks()

    if not chunks:
        print("No chunks found.")
        return

    ids = [chunk["chunk_id"] for chunk in chunks]
    indexes = [chunk["chunk_index"] for chunk in chunks]
    word_counts = [len(chunk["text"].split()) for chunk in chunks]

    empty_chunks = [
        chunk for chunk in chunks
        if not chunk["text"].strip()
    ]

    invalid_ranges = [
        chunk for chunk in chunks
        if chunk["page_start"] > chunk["page_end"]
        or chunk["page_start"] < 1
        or chunk["page_end"] > 98
    ]

    missing_metadata = [
        chunk for chunk in chunks
        if not chunk.get("document_id")
        or not chunk.get("source")
        or not chunk.get("major_section")
        or not chunk.get("policy_title")
    ]

    incorrect_strategy = [
        chunk for chunk in chunks
        if chunk["chunking_strategy"] != "recursive"
    ]

    overlap_checks = []

    for previous, current in zip(chunks, chunks[1:]):
        previous_words = previous["text"].split()
        current_words = current["text"].split()

        overlap_checks.append(
            previous_words[-50:] == current_words[:50]
        )

    print("\n--- RECURSIVE CHUNK VALIDATION ---")
    print(f"Total chunks: {len(chunks)}")
    print(f"Unique chunk IDs: {len(ids) == len(set(ids))}")
    print(f"Sequential indexes: {indexes == list(range(len(chunks)))}")
    print(f"Empty chunks: {len(empty_chunks)}")
    print(f"Minimum words: {min(word_counts)}")
    print(f"Maximum words: {max(word_counts)}")
    print(f"Average words: {mean(word_counts):.2f}")
    print(f"Chunks exceeding 350 words: {sum(n > 350 for n in word_counts)}")
    print(f"Invalid page ranges: {len(invalid_ranges)}")
    print(f"Missing metadata: {len(missing_metadata)}")
    print(f"Incorrect strategy labels: {len(incorrect_strategy)}")

    print(
        f"Exact 50-word overlap: "
        f"{sum(overlap_checks)}/{len(overlap_checks)}"
    )

    if missing_metadata:
        print("\n--- MISSING METADATA ---")
        for chunk in missing_metadata:
            print(
                chunk["chunk_id"],
                chunk["page_start"],
                chunk["page_end"]
            )


if __name__ == "__main__":
    main()
