
import json
import re
from pathlib import Path

from src.hr_assistant.config import PROCESSED_DATA_DIR
from src.hr_assistant.metadata.section_identifier import build_page_registry
from src.hr_assistant.chunking.chunk_schema import build_chunk


DEFAULT_CHUNK_SIZE = 350
DEFAULT_OVERLAP = 50


def find_preferred_split(
    text,
    word_spans,
    start,
    limit,
    minimum_words
):
    """
    Prefer paragraph, line, and sentence boundaries,
    in that order, within the allowed chunk window.
    """

    separators = ["paragraph", "line", "sentence"]

    for separator in separators:
        candidates = []

        for boundary in range(start + minimum_words, limit + 1):
            previous_end = word_spans[boundary - 1][1]
            next_start = word_spans[boundary][0] if boundary < len(word_spans) else len(text)

            gap = text[previous_end:next_start]

            if separator == "paragraph" and gap.count("\n") >= 2:
                candidates.append(boundary)

            elif separator == "line" and "\n" in gap:
                candidates.append(boundary)

            elif separator == "sentence":
                previous_word = word_spans[boundary - 1]
                previous_text = text[previous_word[0]:previous_word[1]]

                if re.search(r"[.!?][\"')\]]*$", previous_text):
                    candidates.append(boundary)

        if candidates:
            return candidates[-1]

    return limit


def create_recursive_chunks(
    pages,
    page_registry,
    chunk_size=DEFAULT_CHUNK_SIZE,
    overlap=DEFAULT_OVERLAP
):
    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")

    if overlap < 0 or overlap >= chunk_size:
        raise ValueError("overlap must be between 0 and chunk_size")

    pages = sorted(
        pages,
        key=lambda item: item["metadata"]["page"]
    )

    combined_text = ""
    word_spans = []
    page_metadata = {}

    for page in pages:
        page_number = page["metadata"]["page"]
        page_text = page["cleaned_text"]

        page_metadata[page_number] = page["metadata"]

        if combined_text:
            combined_text += "\n"

        page_offset = len(combined_text)
        combined_text += page_text

        for match in re.finditer(r"\S+", page_text):
            word_spans.append((
                page_offset + match.start(),
                page_offset + match.end(),
                page_number
            ))

    chunks = []
    start = 0
    chunk_index = 0
    minimum_words = max(1, chunk_size // 2)

    while start < len(word_spans):

        limit = min(start + chunk_size, len(word_spans))

        if limit == len(word_spans):
            end = limit
        else:
            end = find_preferred_split(
                combined_text,
                word_spans,
                start,
                limit,
                minimum_words
            )

        first_word = word_spans[start]
        last_word = word_spans[end - 1]

        chunk_text = combined_text[
            first_word[0]:last_word[1]
        ]

        page_start = first_word[2]
        page_end = last_word[2]

        metadata = {
            **page_metadata[page_start],
            **page_registry[page_start]
        }

        chunk = build_chunk(
            text=chunk_text,
            metadata=metadata,
            chunking_strategy="recursive",
            chunk_index=chunk_index,
            page_start=page_start,
            page_end=page_end
        )

        chunks.append(chunk)

        if end == len(word_spans):
            break

        start = end - overlap
        chunk_index += 1

    return chunks


def save_chunks(chunks):
    output_dir = (
        PROCESSED_DATA_DIR / "chunks" / "recursive"
    )

    output_dir.mkdir(parents=True, exist_ok=True)

    output_file = output_dir / "recursive_chunks.jsonl"

    with open(output_file, "w", encoding="utf-8") as file:
        for chunk in chunks:
            file.write(
                json.dumps(chunk, ensure_ascii=False) + "\n"
            )

    return output_file


def main():
    pages_file = PROCESSED_DATA_DIR / "hr_policy_pages.jsonl"
    registry_file = PROCESSED_DATA_DIR / "hr_toc_registry.json"

    with open(pages_file, "r", encoding="utf-8") as file:
        pages = [
            json.loads(line)
            for line in file
            if line.strip()
        ]

    with open(registry_file, "r", encoding="utf-8") as file:
        registry = json.load(file)

    page_registry = build_page_registry(
        registry,
        total_pages=len(pages)
    )

    chunks = create_recursive_chunks(
        pages=pages,
        page_registry=page_registry
    )

    output_file = save_chunks(chunks)

    print("\n--- RECURSIVE CHUNKING REPORT ---")
    print(f"Total source pages: {len(pages)}")
    print(f"Total chunks: {len(chunks)}")
    print(f"First chunk ID: {chunks[0]['chunk_id']}")
    print(
        f"First chunk pages: "
        f"{chunks[0]['page_start']} - {chunks[0]['page_end']}"
    )
    print(f"First chunk word count: {len(chunks[0]['text'].split())}")
    print(f"Output file: {output_file}")


if __name__ == "__main__":
    main()
