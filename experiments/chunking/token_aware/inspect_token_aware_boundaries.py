
import json
from pathlib import Path
from collections import Counter


PROJECT_ROOT = Path(__file__).resolve().parents[3]

CHUNKS_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "chunks"
    / "token_aware"
    / "token_aware_chunks.jsonl"
)

PAGES_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "experiments"
    / "recursive"
    / "normalized_policy_pages.jsonl"
)


def find_character_overlap(previous_text, current_text):
    max_chars = min(
        len(previous_text),
        len(current_text)
    )

    for size in range(max_chars, 0, -1):
        if previous_text.endswith(current_text[:size]):
            return size

    return 0


def classify_boundary(source_text, boundary_position, previous_text):

    remaining_text = source_text[boundary_position:]

    if remaining_text.startswith("\n\n"):
        return "PARAGRAPH"

    if remaining_text.startswith("\n"):
        return "LINE"

    if previous_text.rstrip().endswith((".", "!", "?")):
        return "SENTENCE"

    return "POSSIBLE MID-SENTENCE"


def main():

    with open(CHUNKS_FILE, "r", encoding="utf-8") as file:
        chunks = [
            json.loads(line)
            for line in file
            if line.strip()
        ]

    with open(PAGES_FILE, "r", encoding="utf-8") as file:
        pages = [
            json.loads(line)
            for line in file
            if line.strip()
        ]

    page_texts = {
        page["metadata"]["page"]: page["normalized_text"]
        for page in pages
    }

    results = []

    for previous, current in zip(chunks, chunks[1:]):

        page = current["page_start"]

        if previous["page_start"] != page:
            continue

        source_text = page_texts.get(page)

        if source_text is None:
            continue

        previous_text = previous["text"]
        current_text = current["text"]

        overlap = find_character_overlap(
            previous_text,
            current_text
        )

        if overlap == 0:
            results.append({
                "page": page,
                "previous": previous["chunk_index"],
                "current": current["chunk_index"],
                "boundary": "NO OVERLAP",
                "overlap": 0,
                "context": ""
            })
            continue

        # Locate the complete previous chunk in the original page.
        source_position = source_text.rfind(previous_text)

        if source_position == -1:
            results.append({
                "page": page,
                "previous": previous["chunk_index"],
                "current": current["chunk_index"],
                "boundary": "SOURCE MATCH NOT FOUND",
                "overlap": overlap,
                "context": ""
            })
            continue

        boundary_position = source_position + len(previous_text)

        boundary_type = classify_boundary(
            source_text,
            boundary_position,
            previous_text
        )

        context = source_text[
            max(0, boundary_position - 100):
            boundary_position + 100
        ]

        results.append({
            "page": page,
            "previous": previous["chunk_index"],
            "current": current["chunk_index"],
            "boundary": boundary_type,
            "overlap": overlap,
            "context": context
        })

    counts = Counter(
        item["boundary"] for item in results
    )

    print("\n--- TOKEN-AWARE BOUNDARY INSPECTION ---")
    print(f"Adjacent same-page pairs: {len(results)}")

    print("\n--- BOUNDARY SUMMARY ---")

    for category, count in counts.items():
        print(f"{category}: {count}")

    print("\n--- FIRST 20 BOUNDARIES ---")

    for item in results[:20]:

        print(
            f"\nPage {item['page']} | "
            f"Chunks {item['previous']} -> {item['current']} | "
            f"{item['boundary']} | "
            f"Overlap: {item['overlap']} characters"
        )

        if item["context"]:
            print("Boundary context:")
            print(repr(item["context"]))


if __name__ == "__main__":
    main()
