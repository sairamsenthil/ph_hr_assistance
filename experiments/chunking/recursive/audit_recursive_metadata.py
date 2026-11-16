
import json
from pathlib import Path
from collections import Counter, defaultdict

PROJECT_ROOT = Path(__file__).resolve().parents[3]

CHUNK_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "chunks"
    / "recursive"
    / "recursive_chunks.jsonl"
)

REGISTRY_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "hr_toc_registry.json"
)

PAGES_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "hr_policy_pages.jsonl"
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

    # Build a page-to-policy mapping using the same
    # authoritative registry used during chunk creation.
    from src.hr_assistant.metadata.section_identifier import build_page_registry

    page_registry = build_page_registry(
        registry,
        total_pages=len(pages)
    )

    cross_policy = []
    cross_section = []
    missing_policy = []
    starting_page_mismatches = []

    for chunk in chunks:
        start = chunk["page_start"]
        end = chunk["page_end"]

        policies = set()
        sections = set()

        for page_number in range(start, end + 1):
            metadata = page_registry.get(page_number, {})

            policy = metadata.get("policy_number")
            section = metadata.get("major_section_number")

            if policy is not None:
                policies.add(policy)

            if section is not None:
                sections.add(section)

        if len(policies) > 1:
            cross_policy.append((chunk, sorted(policies)))

        if len(sections) > 1:
            cross_section.append((chunk, sorted(sections)))

        if policies and chunk.get("policy_number") is None:
            missing_policy.append(chunk)

        expected = page_registry.get(start, {})

        if (
            chunk.get("policy_number") != expected.get("policy_number")
            or chunk.get("major_section_number")
            != expected.get("major_section_number")
        ):
            starting_page_mismatches.append(chunk)

    print("\n--- RECURSIVE METADATA AUDIT ---")
    print(f"Total chunks: {len(chunks)}")
    print(f"Chunks spanning multiple policies: {len(cross_policy)}")
    print(f"Chunks spanning multiple major sections: {len(cross_section)}")
    print(f"Policy content with missing policy metadata: {len(missing_policy)}")
    print(f"Starting-page metadata mismatches: {len(starting_page_mismatches)}")

    print("\n--- CROSS-POLICY CHUNKS ---")

    for chunk, policies in cross_policy:
        print(
            f"{chunk['chunk_id']} | "
            f"Pages: {chunk['page_start']}-{chunk['page_end']} | "
            f"Stored policy: {chunk.get('policy_number')} | "
            f"Actual policies: {policies}"
        )

    print("\n--- POLICY CONTENT WITH MISSING METADATA ---")

    for chunk in missing_policy:
        print(
            f"{chunk['chunk_id']} | "
            f"Pages: {chunk['page_start']}-{chunk['page_end']}"
        )

    print("\n--- STARTING-PAGE MISMATCHES ---")

    for chunk in starting_page_mismatches:
        print(
            f"{chunk['chunk_id']} | "
            f"Pages: {chunk['page_start']}-{chunk['page_end']}"
        )


if __name__ == "__main__":
    main()
