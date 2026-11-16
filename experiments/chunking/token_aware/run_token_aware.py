
import json
from pathlib import Path

from hr_assistant.chunking.token_aware.token_aware import (
    create_token_aware_chunks
)
from src.hr_assistant.metadata.section_identifier import (
    build_page_registry
)

PROJECT_ROOT = Path(__file__).resolve().parents[3]

PAGES_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "experiments"
    / "recursive"
    / "normalized_policy_pages.jsonl"
)

TOC_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "hr_toc_registry.json"
)

OUTPUT_DIR = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "chunks"
    / "token_aware"
)

OUTPUT_FILE = OUTPUT_DIR / "token_aware_chunks.jsonl"


def main():
    with open(PAGES_FILE, "r", encoding="utf-8") as file:
        pages = [
            json.loads(line)
            for line in file
            if line.strip()
        ]

    with open(TOC_FILE, "r", encoding="utf-8") as file:
        toc_registry = json.load(file)

    page_registry = build_page_registry(
        toc_registry,
        total_pages=98
    )

    chunks = create_token_aware_chunks(
        pages=pages,
        page_registry=page_registry,
        chunk_size=460,
        overlap=50
    )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
        for chunk in chunks:
            file.write(
                json.dumps(chunk, ensure_ascii=False) + "\n"
            )

    token_counts = [
        chunk["token_count"] for chunk in chunks
    ]

    print("\n--- TOKEN-AWARE CHUNKING REPORT ---")
    print(f"Source pages: {len(pages)}")
    print(f"Total chunks: {len(chunks)}")
    print(f"Maximum tokens: {max(token_counts, default=0)}")
    print(f"Minimum tokens: {min(token_counts, default=0)}")
    print(
        f"Chunks exceeding 460 tokens: "
        f"{sum(count > 460 for count in token_counts)}"
    )
    print(f"Output: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
