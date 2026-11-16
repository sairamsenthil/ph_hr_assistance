
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

TOKEN_THRESHOLD = 100


def main():

    with open(CHUNKS_FILE, "r", encoding="utf-8") as file:
        chunks = [
            json.loads(line)
            for line in file
            if line.strip()
        ]

    small_chunks = [
        chunk
        for chunk in chunks
        if chunk["token_count"] < TOKEN_THRESHOLD
    ]

    print("\n--- SMALL CHUNK INSPECTION ---")
    print(f"Total chunks: {len(chunks)}")
    print(f"Threshold: Below {TOKEN_THRESHOLD} tokens")
    print(f"Small chunks: {len(small_chunks)}")

    for chunk in small_chunks:

        print("\n" + "=" * 70)

        print(f"Chunk ID: {chunk['chunk_id']}")
        print(f"Page: {chunk['page_start']}")
        print(f"Tokens: {chunk['token_count']}")
        print(f"Words: {len(chunk['text'].split())}")

        print(f"Major section: {chunk['major_section']}")
        print(f"Policy: {chunk['policy_title']}")
        print(f"Subsection: {chunk['subsection_title']}")

        print("\nTEXT:")
        print(chunk["text"])


if __name__ == "__main__":
    main()
