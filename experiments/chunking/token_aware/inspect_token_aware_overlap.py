
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


def main():
    with open(INPUT_FILE, "r", encoding="utf-8") as file:
        chunks = [
            json.loads(line)
            for line in file
            if line.strip()
        ]

    print("\n--- ACTUAL CHUNK OVERLAP INSPECTION ---")

    inspected = 0

    for previous, current in zip(chunks, chunks[1:]):

        if previous["page_start"] != current["page_start"]:
            continue

        previous_words = previous["text"].split()
        current_words = current["text"].split()

        max_size = min(
            len(previous_words),
            len(current_words)
        )

        overlap_words = 0

        for size in range(max_size, 0, -1):
            if (
                previous_words[-size:]
                == current_words[:size]
            ):
                overlap_words = size
                break

        print(f"\nPage: {current['page_start']}")
        print(
            f"Chunks: {previous['chunk_index']} -> "
            f"{current['chunk_index']}"
        )
        print(f"Previous chunk tokens: {previous['token_count']}")
        print(f"Current chunk tokens: {current['token_count']}")
        print(f"Actual shared words: {overlap_words}")
        print("Previous ending:", " ".join(previous_words[-20:]))
        print("Current beginning:", " ".join(current_words[:20]))

        inspected += 1

        if inspected == 5:
            break


if __name__ == "__main__":
    main()
