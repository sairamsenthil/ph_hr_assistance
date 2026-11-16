
import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]

CHUNKS_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "chunks"
    / "token_aware"
    / "token_aware_chunks.jsonl"
)

TARGET_CHUNKS = {9, 38, 90, 100}


def main():

    with open(CHUNKS_FILE, "r", encoding="utf-8") as file:
        chunks = [
            json.loads(line)
            for line in file
            if line.strip()
        ]

    for index, chunk in enumerate(chunks):

        if chunk["chunk_index"] not in TARGET_CHUNKS:
            continue

        print("\n" + "=" * 75)
        print(
            f"TARGET CHUNK: {chunk['chunk_id']} | "
            f"Page: {chunk['page_start']} | "
            f"Tokens: {chunk['token_count']}"
        )

        print("\n--- PREVIOUS CHUNK ---")

        if index > 0:
            previous = chunks[index - 1]
            print(f"ID: {previous['chunk_id']}")
            print(f"Page: {previous['page_start']}")
            print(previous["text"][-500:])
        else:
            print("No previous chunk.")

        print("\n--- TARGET CHUNK ---")
        print(chunk["text"])

        print("\n--- NEXT CHUNK ---")

        if index + 1 < len(chunks):
            following = chunks[index + 1]
            print(f"ID: {following['chunk_id']}")
            print(f"Page: {following['page_start']}")
            print(following["text"][:500])
        else:
            print("No next chunk.")


if __name__ == "__main__":
    main()
