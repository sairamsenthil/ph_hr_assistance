
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]

SOURCE_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "hr_policy_pages.jsonl"
)

OUTPUT_DIR = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "experiments"
    / "recursive"
)

OUTPUT_FILE = OUTPUT_DIR / "policy_pages.jsonl"

TOC_PAGES = {3, 4, 5, 6}


def main():
    with open(SOURCE_FILE, "r", encoding="utf-8") as file:
        pages = [
            json.loads(line)
            for line in file
            if line.strip()
        ]

    policy_pages = [
        page
        for page in pages
        if page["metadata"]["page"] not in TOC_PAGES
    ]

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
        for page in policy_pages:
            file.write(
                json.dumps(page, ensure_ascii=False) + "\n"
            )

    original_pages = len(pages)
    excluded_pages = original_pages - len(policy_pages)

    print("\n--- POLICY PAGE PREPARATION REPORT ---")
    print(f"Original pages: {original_pages}")
    print(f"Excluded TOC pages: {excluded_pages}")
    print(f"Remaining pages: {len(policy_pages)}")
    print(f"First page: {policy_pages[0]['metadata']['page']}")
    print(f"Last page: {policy_pages[-1]['metadata']['page']}")
    print(f"Output: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
