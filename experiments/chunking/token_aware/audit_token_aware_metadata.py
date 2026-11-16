
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

    print("\n--- TOKEN-AWARE METADATA AUDIT ---")

    for chunk in chunks:
        missing = []

        if not chunk.get("major_section"):
            missing.append("major_section")

        if chunk.get("policy_number") is None:
            missing.append("policy_number")

        if missing:
            print("\nChunk:", chunk["chunk_id"])
            print("Page:", chunk["page_start"])
            print("Missing:", ", ".join(missing))
            print("Major section:", chunk.get("major_section"))
            print("Policy number:", chunk.get("policy_number"))
            print("Text preview:", chunk["text"][:250])


if __name__ == "__main__":
    main()
