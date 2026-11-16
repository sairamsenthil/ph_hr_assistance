
import json
from pathlib import Path

from src.hr_assistant.metadata.section_identifier import (
    build_page_registry
)

from src.hr_assistant.chunking.policy_grouper import (
    group_pages_by_policy,
    combine_group_pages
)

PROJECT_ROOT = Path(__file__).resolve().parents[3]

PAGES_FILE = (
    PROJECT_ROOT / "data" / "processed"
    / "experiments" / "recursive"
    / "normalized_policy_pages.jsonl"
)

TOC_FILE = (
    PROJECT_ROOT / "data" / "processed"
    / "hr_toc_registry.json"
)


def load_jsonl(path):
    with open(path, "r", encoding="utf-8") as file:
        return [json.loads(line) for line in file if line.strip()]


def main():

    pages = load_jsonl(PAGES_FILE)

    with open(TOC_FILE, "r", encoding="utf-8") as file:
        registry = json.load(file)

    page_registry = build_page_registry(registry, 98)

    groups = group_pages_by_policy(pages, page_registry)

    # Inspect Policy 5: Performance Appraisal Policy.
    policy_group = next(
        group for group in groups
        if group["policy_number"] == 5
    )

    combined = combine_group_pages(policy_group)

    print("\n--- CROSS-PAGE TEXT COMBINATION ---")
    print(f"Policy: {combined['policy_title']}")
    print(f"Pages: {combined['page_start']}-{combined['page_end']}")
    print(f"Combined characters: {len(combined['text'])}")
    print(f"Pages tracked: {len(combined['page_spans'])}")

    print("\n--- PAGE POSITION TRACKING ---")

    for span in combined["page_spans"]:
        print(
            f"Page {span['page']} | "
            f"Characters: {span['start_char']}-{span['end_char']}"
        )

    print("\n--- COMBINED TEXT PREVIEW ---")
    print(combined["text"][:1500])

    print("\n--- VALIDATION ---")

    all_pages_tracked = (
        len(combined["page_spans"]) == len(policy_group["pages"])
    )

    page_order_correct = all(
        combined["page_spans"][i]["page"]
        < combined["page_spans"][i + 1]["page"]
        for i in range(len(combined["page_spans"]) - 1)
    )

    print(f"All pages tracked: {all_pages_tracked}")
    print(f"Page order correct: {page_order_correct}")
    print(f"Text is not empty: {bool(combined['text'])}")


if __name__ == "__main__":
    main()
