
import json
from pathlib import Path

from src.hr_assistant.ingestion.formatting_normalizer import (
    normalize_formatting
)

PROJECT_ROOT = Path(__file__).resolve().parents[3]

INPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "experiments"
    / "recursive"
    / "policy_pages.jsonl"
)

OUTPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "experiments"
    / "recursive"
    / "normalized_policy_pages.jsonl"
)


def main():
    with open(INPUT_FILE, "r", encoding="utf-8") as file:
        pages = [
            json.loads(line)
            for line in file
            if line.strip()
        ]

    total_dotted = 0
    total_dashed = 0
    affected_pages = []

    normalized_pages = []

    for page in pages:
        result = normalize_formatting(page["cleaned_text"])

        normalized_page = {
            **page,
            "normalized_text": result["text"]
        }

        normalized_pages.append(normalized_page)

        total_dotted += result["dotted_runs_removed"]
        total_dashed += result["dashed_runs_removed"]

        if result["dotted_runs_removed"] or result["dashed_runs_removed"]:
            affected_pages.append({
                "page": page["metadata"]["page"],
                "dotted": result["dotted_runs_removed"],
                "dashed": result["dashed_runs_removed"]
            })

    with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
        for page in normalized_pages:
            file.write(
                json.dumps(page, ensure_ascii=False) + "\n"
            )

    print("\n--- FORMATTING NORMALIZATION REPORT ---")
    print(f"Pages processed: {len(pages)}")
    print(f"Pages affected: {len(affected_pages)}")
    print(f"Dotted runs replaced: {total_dotted}")
    print(f"Dashed runs removed: {total_dashed}")

    print("\n--- AFFECTED PAGES ---")
    for page in affected_pages:
        print(
            f"Page {page['page']} | "
            f"Dots: {page['dotted']} | "
            f"Dashes: {page['dashed']}"
        )

    print(f"\nOutput: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
