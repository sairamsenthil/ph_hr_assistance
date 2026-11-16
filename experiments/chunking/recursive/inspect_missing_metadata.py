
import json
from pathlib import Path

from src.hr_assistant.metadata.section_identifier import build_page_registry

PROJECT_ROOT = Path(__file__).resolve().parents[3]

CHUNK_FILE = (
    PROJECT_ROOT / "data" / "processed"
    / "chunks" / "recursive" / "recursive_chunks.jsonl"
)

PAGES_FILE = (
    PROJECT_ROOT / "data" / "processed"
    / "hr_policy_pages.jsonl"
)

REGISTRY_FILE = (
    PROJECT_ROOT / "data" / "processed"
    / "hr_toc_registry.json"
)


def load_jsonl(path):
    with open(path, "r", encoding="utf-8") as file:
        return [json.loads(line) for line in file if line.strip()]


def load_json(path):
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def main():
    chunks = load_jsonl(CHUNK_FILE)
    pages = load_jsonl(PAGES_FILE)
    registry = load_json(REGISTRY_FILE)

    page_registry = build_page_registry(
        registry,
        total_pages=len(pages)
    )

    target_ids = {
        "hr_policy_manual:recursive:00005",
        "hr_policy_manual:recursive:00035"
    }

    for chunk in chunks:
        if chunk["chunk_id"] not in target_ids:
            continue

        print("\n" + "=" * 65)
        print("CHUNK:", chunk["chunk_id"])
        print("Pages:", chunk["page_start"], "-", chunk["page_end"])
        print("Stored policy:", chunk.get("policy_number"))
        print("Stored policy title:", chunk.get("policy_title"))
        print("Stored major section:", chunk.get("major_section"))

        print("\n--- PAGE REGISTRY ---")

        for page_number in range(
            chunk["page_start"],
            chunk["page_end"] + 1
        ):
            metadata = page_registry.get(page_number, {})

            print(
                f"Page {page_number} | "
                f"Type: {metadata.get('page_type')} | "
                f"Section: {metadata.get('major_section_number')} "
                f"{metadata.get('major_section')} | "
                f"Policy: {metadata.get('policy_number')} "
                f"{metadata.get('policy_title')}"
            )

        print("\n--- CHUNK TEXT PREVIEW ---")
        print(chunk["text"][:1500])


if __name__ == "__main__":
    main()
