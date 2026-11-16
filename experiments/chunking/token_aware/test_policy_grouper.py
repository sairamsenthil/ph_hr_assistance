
import json

from src.hr_assistant.config import PROCESSED_DATA_DIR
from src.hr_assistant.metadata.section_identifier import build_page_registry
from src.hr_assistant.chunking.policy_grouper import (
    group_pages_by_policy
)


PAGES_FILE = (
    PROCESSED_DATA_DIR
    / "experiments"
    / "recursive"
    / "normalized_policy_pages.jsonl"
)

TOC_FILE = PROCESSED_DATA_DIR / "hr_toc_registry.json"


def load_jsonl(path):
    with open(path, "r", encoding="utf-8") as file:
        return [
            json.loads(line)
            for line in file
            if line.strip()
        ]


def main():
    pages = load_jsonl(PAGES_FILE)

    with open(TOC_FILE, "r", encoding="utf-8") as file:
        registry = json.load(file)

    page_registry = build_page_registry(registry, 98)

    groups = group_pages_by_policy(pages, page_registry)

    policy_groups = [
        group for group in groups
        if group["document_region"] == "policy_content"
    ]

    print("\n--- POLICY ISOLATION REPORT ---")
    print(f"Total document pages loaded: {len(pages)}")
    print(f"Total policy groups: {len(policy_groups)}")

    print("\n--- POLICY GROUP DETAILS ---")

    for group in policy_groups:
        print(
            f"Policy {group['policy_number']} | "
            f"{group['policy_title']} | "
            f"Pages: {group['page_start']}-{group['page_end']} | "
            f"Pages grouped: {len(group['pages'])}"
        )

    print("\n--- VALIDATION ---")

    unique_policies = {
        group["policy_number"]
        for group in policy_groups
    }

    print(f"Unique policy numbers: {len(unique_policies)}")

    duplicate_groups = len(policy_groups) != len(unique_policies)
    missing_metadata = any(
        group["policy_number"] is None or not group["policy_title"]
        for group in policy_groups
    )

    print(
        "Duplicate policy groups:",
        "FAIL" if duplicate_groups else "PASS"
    )

    print(
        "Missing policy metadata:",
        "FAIL" if missing_metadata else "PASS"
    )


if __name__ == "__main__":
    main()
