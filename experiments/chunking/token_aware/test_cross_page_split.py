
import json
from pathlib import Path

from tokenizers import Tokenizer

from src.hr_assistant.config import PROCESSED_DATA_DIR
from hr_assistant.chunking.token_aware.token_aware import (
    split_text,
    TOKENIZER_NAME
)

from src.hr_assistant.metadata.section_identifier import build_page_registry

from src.hr_assistant.chunking.policy_grouper import (
    group_pages_by_policy,
    combine_group_pages
)


PROJECT_ROOT = Path(__file__).resolve().parents[4]

PAGES_FILE = (
    PROCESSED_DATA_DIR
    / "experiments"
    / "recursive"
    / "normalized_policy_pages.jsonl"
)

TOC_FILE = (
    PROCESSED_DATA_DIR
    / "hr_toc_registry.json"
)

CHUNK_SIZE = 460
OVERLAP = 50
TARGET_POLICY = 5


def load_jsonl(file_path):

    records = []

    with open(file_path, "r", encoding="utf-8") as file:
        for line in file:
            if line.strip():
                records.append(json.loads(line))

    return records

def calculate_token_overlap(chunks, source_text, tokenizer):

    results = []

    for i in range(len(chunks) - 1):

        current_chunk = chunks[i]
        next_chunk = chunks[i + 1]

        overlap_start = max(
            current_chunk["start_char"],
            next_chunk["start_char"]
        )

        overlap_end = min(
            current_chunk["end_char"],
            next_chunk["end_char"]
        )

        overlap_chars = max(
            0,
            overlap_end - overlap_start
        )

        overlap_text = source_text[
            overlap_start:overlap_end
        ]

        overlap_tokens = len(
            tokenizer.encode(overlap_text).ids
        )

        results.append({
            "boundary": f"{i} -> {i + 1}",
            "overlap_characters": overlap_chars,
            "actual_overlap_tokens": overlap_tokens
        })

    return results

def main():

    print("\nLoading HR policy documents...")

    pages = load_jsonl(PAGES_FILE)

    with open(TOC_FILE, "r", encoding="utf-8") as file:
        registry = json.load(file)

    page_registry = build_page_registry(
        registry,
        98
    )

    print(f"Total pages loaded: {len(pages)}")

    print("\nGrouping pages by policy...")

    policy_groups = group_pages_by_policy(
        pages,
        page_registry
    )

    target_group = next(
        (
            group
            for group in policy_groups
            if group["policy_number"] == TARGET_POLICY
        ),
        None
    )

    if target_group is None:
        raise ValueError(
            f"Policy {TARGET_POLICY} not found."
        )

    combined = combine_group_pages(target_group)

    print("\nSelected Policy:")
    print(f"Policy: {target_group.get('policy_title')}")
    print(f"Pages: {combined['page_start']}-{combined['page_end']}")
    print(f"Characters: {len(combined['text'])}")

    print("\nLoading tokenizer...")

    tokenizer = Tokenizer.from_pretrained(
        TOKENIZER_NAME
    )

    tokenizer.no_truncation()

    print("\nGenerating cross-page chunks...")

    chunks = split_text(
        text=combined["text"],
        page_spans=combined["page_spans"],
        tokenizer=tokenizer,
        chunk_size=CHUNK_SIZE,
        overlap=OVERLAP
    )

    # 1. Main report

    print("\n--- CROSS-PAGE TOKEN SPLITTING REPORT ---")

    print(f"Policy: {target_group.get('policy_title')}")

    print(
        f"Source pages: "
        f"{combined['page_start']}-{combined['page_end']}"
    )

    print(f"Total chunks: {len(chunks)}")

    # 2. Chunk details

    print("\n--- CHUNK DETAILS ---")

    for index, chunk in enumerate(chunks):

        print(
            f"Chunk {index:03d} | "
            f"Tokens: {chunk['token_count']} | "
            f"Pages: {chunk['page_start']}-{chunk['page_end']} | "
            f"Characters: {chunk['start_char']}-{chunk['end_char']}"
        )

    # 3. Token validation

    token_counts = [
        chunk["token_count"]
        for chunk in chunks
    ]

    maximum_tokens = max(token_counts, default=0)

    exceeding_chunks = sum(
        count > CHUNK_SIZE
        for count in token_counts
    )

    multi_page_chunks = sum(
        chunk["page_start"] != chunk["page_end"]
        for chunk in chunks
    )

    print("\n--- VALIDATION ---")

    print(f"Maximum token count: {maximum_tokens}")

    print(
        f"Chunks exceeding {CHUNK_SIZE}: "
        f"{exceeding_chunks}"
    )

    print(
        f"Chunks spanning multiple pages: "
        f"{multi_page_chunks}"
    )

    # 4. Actual token overlap

    print("\n--- TOKEN OVERLAP VALIDATION ---")

    overlaps = calculate_token_overlap(
    chunks,
    combined["text"],
    tokenizer
)

    for item in overlaps:

        print(
             f"{item['boundary']}: "
        f"{item['actual_overlap_tokens']} tokens | "
        f"{item['overlap_characters']} characters"
        )

    # 5. Content preview

    if chunks:

        print("\n--- FIRST CHUNK PREVIEW ---")

        print(chunks[0]["text"][:1500])

    # 6. Final status

    print("\n--- FINAL STATUS ---")

    if exceeding_chunks == 0:
        print("PASS: All chunks satisfy the token limit.")
    else:
        print("FAIL: Some chunks exceed the token limit.")

    if all(
        chunk["source_pages"]
        for chunk in chunks
    ):
        print("PASS: Source-page metadata is available.")
    else:
        print("FAIL: Missing source-page metadata.")


if __name__ == "__main__":
    main()
