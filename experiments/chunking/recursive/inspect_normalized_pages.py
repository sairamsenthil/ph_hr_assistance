
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]

INPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "experiments"
    / "recursive"
    / "normalized_policy_pages.jsonl"
)

PAGES_TO_INSPECT = {19, 22, 23, 89}


def main():
    with open(INPUT_FILE, "r", encoding="utf-8") as file:
        pages = [
            json.loads(line)
            for line in file
            if line.strip()
        ]

    for page in pages:
        page_number = page["metadata"]["page"]

        if page_number not in PAGES_TO_INSPECT:
            continue

        print("\n" + "=" * 70)
        print(f"PAGE {page_number}")
        print("=" * 70)

        print("\n--- ORIGINAL CLEANED TEXT ---")
        print(page["cleaned_text"])

        print("\n--- NORMALIZED TEXT ---")
        print(page["normalized_text"])

        print("\n--- PRESERVATION CHECK ---")
        print(
            "Original preserved:",
            isinstance(page["cleaned_text"], str)
        )


if __name__ == "__main__":
    main()
