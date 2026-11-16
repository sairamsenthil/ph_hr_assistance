
import json
import re

from ...config import PROCESSED_DATA_DIR
from ...metadata.section_identifier import build_page_registry
from ..chunk_schema import build_chunk

DEFAULT_CHUNK_SIZE = 350
DEFAULT_OVERLAP = 50


def create_fixed_size_chunks(
    pages: list[dict],
    page_registry: dict,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    overlap: int = DEFAULT_OVERLAP
) -> list[dict]:
    """
    Create fixed-size word-based chunks while preserving
    original page boundaries and structural metadata.

    Structural metadata is taken from the chunk's starting page.
    """

    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than zero.")

    if overlap < 0 or overlap >= chunk_size:
        raise ValueError(
            "overlap must be non-negative and smaller than chunk_size."
        )

    # Sort pages to guarantee document order.
    pages = sorted(
        pages,
        key=lambda item: item["metadata"]["page"]
    )

    page_texts = [
        page.get("cleaned_text", "")
        for page in pages
    ]

    # Combine pages while retaining their original text positions.
    full_text = "\n".join(page_texts)

    # Map each word to its original page.
    word_spans = []
    current_offset = 0

    for page, page_text in zip(pages, page_texts):

        page_number = page["metadata"]["page"]

        for match in re.finditer(r"\S+", page_text):
            word_spans.append({
                "start": current_offset + match.start(),
                "end": current_offset + match.end(),
                "page": page_number
            })

        current_offset += len(page_text) + 1

    chunks = []

    step_size = chunk_size - overlap
    chunk_index = 0

    for start in range(0, len(word_spans), step_size):

        end = min(start + chunk_size, len(word_spans))

        selected_words = word_spans[start:end]

        if not selected_words:
            continue

        first_word = selected_words[0]
        last_word = selected_words[-1]

        chunk_text = full_text[
            first_word["start"]:last_word["end"]
        ]

        page_start = first_word["page"]
        page_end = last_word["page"]

        # Use structural metadata from the starting page.
        metadata = next(
            page["metadata"]
            for page in pages
            if page["metadata"]["page"] == page_start
        )

        structural_metadata = page_registry.get(page_start, {})

        metadata = {
            **metadata,
            **structural_metadata
        }

        chunk = build_chunk(
            text=chunk_text,
            metadata=metadata,
            chunking_strategy="fixed_size",
            chunk_index=chunk_index,
            page_start=page_start,
            page_end=page_end
        )

        chunks.append(chunk)
        chunk_index += 1

        if end == len(word_spans):
            break

    return chunks


def save_chunks(chunks: list[dict]) -> None:
    """Save fixed-size chunks as JSONL."""

    output_dir = PROCESSED_DATA_DIR / "chunks" / "fixed_size"
    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = output_dir / "fixed_size_chunks.jsonl"

    with output_path.open("w", encoding="utf-8") as file:

        for chunk in chunks:
            file.write(
                json.dumps(chunk, ensure_ascii=False) + "\n"
            )

    print(f"Saved chunks: {len(chunks)}")
    print(f"Output: {output_path}")


if __name__ == "__main__":

    # Load cleaned page-level documents.
    pages_path = (
        PROCESSED_DATA_DIR / "hr_policy_pages.jsonl"
    )

    with pages_path.open("r", encoding="utf-8") as file:
        pages = [
            json.loads(line)
            for line in file
            if line.strip()
        ]

    # Load the TOC hierarchy.
    registry_path = (
        PROCESSED_DATA_DIR / "hr_toc_registry.json"
    )

    with registry_path.open("r", encoding="utf-8") as file:
        toc_registry = json.load(file)

    # Build page-level structural metadata.
    page_registry = build_page_registry(
        toc_registry,
        total_pages=len(pages)
    )

    # Generate fixed-size chunks.
    chunks = create_fixed_size_chunks(
        pages=pages,
        page_registry=page_registry
    )

    save_chunks(chunks)

    # Basic report.
    print("\n--- FIXED-SIZE CHUNKING REPORT ---")
    print("Total source pages:", len(pages))
    print("Total chunks:", len(chunks))

    if chunks:
        print("First chunk ID:", chunks[0]["chunk_id"])
        print("First chunk pages:",
              chunks[0]["page_start"],
              "-",
              chunks[0]["page_end"])
        print("First chunk word count:",
              len(chunks[0]["text"].split()))
        print("Last chunk ID:", chunks[-1]["chunk_id"])