
import json
import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]

CHUNK_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "chunks"
    / "fixed_size"
    / "fixed_size_chunks.jsonl"
)

EXPECTED_OVERLAP = 50
MAX_BOUNDARIES_TO_DISPLAY = 15


def load_chunks():
    chunks = []

    with open(CHUNK_FILE, "r", encoding="utf-8") as file:
        for line in file:
            if line.strip():
                chunks.append(json.loads(line))

    return chunks


def get_tokens(text):
    return list(re.finditer(r"\S+", text))


def find_overlap(previous_tokens, current_tokens):
    max_overlap = min(
        len(previous_tokens),
        len(current_tokens),
        EXPECTED_OVERLAP + 10
    )

    for size in range(max_overlap, 0, -1):
        previous_suffix = [
            token.group().lower()
            for token in previous_tokens[-size:]
        ]

        current_prefix = [
            token.group().lower()
            for token in current_tokens[:size]
        ]

        if previous_suffix == current_prefix:
            return size

    return 0



def inspect_boundary(previous_chunk, current_chunk):
    previous_text = previous_chunk["text"]
    current_text = current_chunk["text"]

    previous_tokens = get_tokens(previous_text)
    current_tokens = get_tokens(current_text)

    overlap = find_overlap(previous_tokens, current_tokens)

    if overlap == 0:
        return {
            "overlap": 0,
            "status": "Could not identify overlap",
        }

    if overlap >= len(current_tokens):
        return {
            "overlap": overlap,
            "status": "Insufficient new content",
        }

    # Actual split: after the previous chunk's final token.
    previous_last = previous_tokens[-1]

    # First token in the current chunk that is new,
    # rather than part of the 50-word overlap.
    next_new_token = current_tokens[overlap]

    # Check the gap immediately before the new content.
    gap_start = current_tokens[overlap - 1].end()
    gap_end = next_new_token.start()
    gap = current_text[gap_start:gap_end]

    paragraph_boundary = "\n\n" in gap

    sentence_boundary = bool(
        re.search(r'[.!?]["\')\]]*$', previous_last.group())
    )

    if paragraph_boundary:
        boundary_type = "PARAGRAPH"
    elif sentence_boundary:
        boundary_type = "SENTENCE"
    else:
        boundary_type = "POSSIBLE MID-SENTENCE"

    return {
        "overlap": overlap,
        "boundary_type": boundary_type,
        "previous_ending": previous_text[
            max(0, previous_last.start() - 100):previous_last.end()
        ].replace("\n", " "),
        "next_start": current_text[
            next_new_token.start():next_new_token.start() + 150
        ].replace("\n", " "),
    }



def main():
    chunks = load_chunks()

    print("\n--- FIXED-SIZE BOUNDARY INSPECTION ---")
    print(f"Total chunks: {len(chunks)}")

    results = []

    for index in range(len(chunks) - 1):
        result = inspect_boundary(
            chunks[index],
            chunks[index + 1]
        )

        results.append({
            "previous_chunk": chunks[index]["chunk_id"],
            "next_chunk": chunks[index + 1]["chunk_id"],
            **result
        })

    categories = {
        "PARAGRAPH": 0,
        "SENTENCE": 0,
        "POSSIBLE MID-SENTENCE": 0,
        "Could not identify overlap": 0,
        "Insufficient content before split": 0,
    }

    for result in results:
        category = result.get("boundary_type") or result.get("status")
        categories[category] += 1

    print(f"Boundaries inspected: {len(results)}")
    print("\n--- BOUNDARY SUMMARY ---")

    for category, count in categories.items():
        print(f"{category}: {count}")

    print("\n--- BOUNDARY DETAILS ---")

    for result in results[:MAX_BOUNDARIES_TO_DISPLAY]:
        print("\n" + "=" * 65)
        print(
            f"{result['previous_chunk']} -> "
            f"{result['next_chunk']}"
        )
        print(f"Overlap detected: {result['overlap']} words")

        if "boundary_type" in result:
            print(f"Boundary type: {result['boundary_type']}")
            print(f"Previous ending: {result['previous_ending']}")
            print(f"Next chunk starts: {result['next_start']}")
        else:
            print(f"Status: {result['status']}")

    print("\n--- INSPECTION COMPLETE ---")


if __name__ == "__main__":
    main()
