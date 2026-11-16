
import json
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


def find_character_overlap(previous_text, current_text):
    max_size = min(
        len(previous_text),
        len(current_text)
    )

    for size in range(max_size, 0, -1):
        if previous_text.endswith(current_text[:size]):
            return size

    return 0


def main():
    with open(INPUT_FILE, "r", encoding="utf-8") as file:
        chunks = [
            json.loads(line)
            for line in file
            if line.strip()
        ]

    results = []

    for previous, current in zip(chunks, chunks[1:]):

        if previous["page_start"] != current["page_start"]:
            continue

        char_overlap = find_character_overlap(
            previous["text"],
            current["text"]
        )

        overlap_text = current["text"][:char_overlap]

        results.append({
            "page": current["page_start"],
            "previous_chunk": previous["chunk_index"],
            "current_chunk": current["chunk_index"],
            "characters": char_overlap,
            "words": len(overlap_text.split())
        })

    print("\n--- TOKEN-AWARE CHARACTER OVERLAP AUDIT ---")
    print(f"Adjacent same-page pairs: {len(results)}")

    if not results:
        return

    print(
        "Pairs with zero overlap:",
        sum(item["characters"] == 0 for item in results)
    )

    print(
        "Average shared characters:",
        round(
            sum(item["characters"] for item in results)
            / len(results),
            2
        )
    )

    print(
        "Average shared words:",
        round(
            sum(item["words"] for item in results)
            / len(results),
            2
        )
    )

    print("\n--- ALL PAIRS ---")

    for item in results:
        print(
            f"Page {item['page']} | "
            f"Chunks {item['previous_chunk']} -> "
            f"{item['current_chunk']} | "
            f"{item['characters']} characters | "
            f"{item['words']} words"
        )


if __name__ == "__main__":
    main()
