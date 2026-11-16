
import json
import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]

CHUNK_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "chunks"
    / "recursive"
    / "recursive_chunks.jsonl"
)

REPORT_FILE = (
    PROJECT_ROOT
    / "experiments"
    / "chunking"
    / "recursive"
    / "recursive_token_report.json"
)


def load_jsonl(path):
    with open(path, "r", encoding="utf-8") as file:
        return [json.loads(line) for line in file if line.strip()]


def load_json(path):
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def main():
    chunks = load_jsonl(CHUNK_FILE)
    report = load_json(REPORT_FILE)

    oversized_ids = {
        item["chunk_id"]
        for item in report["chunks_exceeding_limit"]
    }

    oversized_chunks = [
        chunk for chunk in chunks
        if chunk["chunk_id"] in oversized_ids
    ]

    print("\n--- RECURSIVE OVERSIZED CHUNK INSPECTION ---")
    print(f"Oversized chunks: {len(oversized_chunks)}")

    for chunk in oversized_chunks:
        text = chunk["text"]

        dotted_runs = re.findall(r"\.{3,}", text)
        underscore_runs = re.findall(r"_{3,}", text)

        punctuation_only_parts = re.findall(
            r"(?<!\S)[^\w\s]+(?!\S)",
            text
        )

        print("\n" + "=" * 70)
        print("Chunk:", chunk["chunk_id"])
        print("Pages:", chunk["page_start"], "-", chunk["page_end"])
        print("Words:", len(text.split()))

        token_data = next(
            item for item in report["all_chunks"]
            if item["chunk_id"] == chunk["chunk_id"]
        )

        print("Tokens:", token_data["token_count"])
        print("Dotted runs (3+ dots):", len(dotted_runs))
        print("Underscore runs:", len(underscore_runs))
        print(
            "Standalone punctuation groups:",
            len(punctuation_only_parts)
        )

        print("\n--- TEXT PREVIEW (FIRST 2000 CHARACTERS) ---")
        print(text[:2000])


if __name__ == "__main__":
    main()
