
import json
from pathlib import Path
from tokenizers import Tokenizer


PROJECT_ROOT = Path(__file__).resolve().parents[3]

CHUNKS_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "chunks"
    / "token_aware"
    / "token_aware_chunks.jsonl"
)

TARGET_PAGES = {76}


def find_character_overlap(previous_text, current_text):
    max_chars = min(
        len(previous_text),
        len(current_text)
    )

    for size in range(max_chars, 0, -1):
        if previous_text.endswith(current_text[:size]):
            return size

    return 0


def find_word_overlap(previous_text, current_text):
    previous_words = previous_text.split()
    current_words = current_text.split()

    max_words = min(
        len(previous_words),
        len(current_words)
    )

    for size in range(max_words, 0, -1):
        if previous_words[-size:] == current_words[:size]:
            return size

    return 0


def main():

    tokenizer = Tokenizer.from_pretrained(
        "mixedbread-ai/mxbai-embed-large-v1"
    )

    with open(CHUNKS_FILE, "r", encoding="utf-8") as file:
        chunks = [
            json.loads(line)
            for line in file
            if line.strip()
        ]

    for previous, current in zip(chunks, chunks[1:]):

        page = current["page_start"]

        if page not in TARGET_PAGES:
            continue

        if previous["page_start"] != page:
            continue

        previous_text = previous["text"]
        current_text = current["text"]

        print("\n" + "=" * 60)
        print(f"PAGE: {page}")
        print(
            f"CHUNKS: {previous['chunk_index']} -> "
            f"{current['chunk_index']}"
        )

        print("\nPREVIOUS CHUNK END:")
        print(repr(previous_text[-500:]))

        print("\nCURRENT CHUNK START:")
        print(repr(current_text[:500]))

        # 1. Character overlap
        char_overlap = find_character_overlap(
            previous_text,
            current_text
        )

        overlap_text = current_text[:char_overlap]

        print("\n--- CHARACTER OVERLAP ---")
        print(f"Shared characters: {char_overlap}")
        print(f"Shared text: {repr(overlap_text)}")

        # 2. Word overlap
        word_overlap = find_word_overlap(
            previous_text,
            current_text
        )

        print("\n--- WORD OVERLAP ---")
        print(f"Shared words: {word_overlap}")

        # 3. Token overlap
        overlap_tokens = tokenizer.encode(
            overlap_text
        )

        print("\n--- TOKEN OVERLAP ---")
        print(f"Shared tokens: {len(overlap_tokens.ids)}")
        print(
            "Shared token pieces:",
            overlap_tokens.tokens
        )


if __name__ == "__main__":
    main()
