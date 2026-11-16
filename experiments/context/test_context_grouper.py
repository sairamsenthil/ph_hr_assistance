
import json
from pathlib import Path

from src.hr_assistant.context.context_grouper import (
    ContextGrouper,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]

CHUNKS_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "chunks"
    / "parent_child"
    / "parent-child.jsonl"
)


def load_source():

    with open(CHUNKS_FILE, "r", encoding="utf-8") as file:

        for line in file:

            item = json.loads(line)

            if (
                item["chunk_id"] == "hr_policy_manual:parent:00022"
            ):
                return item

    raise ValueError("Test source not found")


def main():

    source = load_source()

    raw_paragraphs = source["text"].split("\n\n")

    paragraphs = [
        {
            "paragraph_index": index,
            "text": paragraph.strip(),
        }
        for index, paragraph in enumerate(raw_paragraphs)
        if paragraph.strip()
    ]

    grouper = ContextGrouper()

    # 1. Debug bullet detection
    print("\n--- BULLET DETECTION DEBUG ---")

    debug_indexes = list(range(len(paragraphs)))

    for paragraph_index in debug_indexes:

        paragraph = paragraphs[paragraph_index]["text"]

        result = grouper.is_bullet(paragraph)

        print(
            f"Index: {paragraph_index} | "
            f"Text: {paragraph[:60]!r} | "
            f"Is bullet: {result}"
        )

    # 2. Group paragraphs
    groups = grouper.group_paragraphs(paragraphs)

    # 3. Display grouping results
    print("\n--- CONTEXT GROUPING TEST ---")

    print("Policy:", source["policy_title"])
    print("Original paragraphs:", len(paragraphs))
    print("Generated groups:", len(groups))

    for group_index, group in enumerate(groups):

        print(
            f"\n========== GROUP {group_index} =========="
        )

        print(
            "Original paragraph indexes:",
            group["paragraph_indexes"],
        )

        print(group["text"])


if __name__ == "__main__":
    main()
