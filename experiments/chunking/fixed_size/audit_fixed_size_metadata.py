
import json
from pathlib import Path

from src.hr_assistant.metadata.section_identifier import build_page_registry

PROJECT_ROOT = Path(__file__).resolve().parents[3]

CHUNK_FILE = (
    PROJECT_ROOT / "data" / "processed" / "chunks"
    / "fixed_size" / "fixed_size_chunks.jsonl"
)

PAGE_FILE = PROJECT_ROOT / "data" / "processed" / "hr_policy_pages.jsonl"

TOC_FILE = PROJECT_ROOT / "data" / "processed" / "hr_toc_registry.json"


def load_jsonl(path):
    records = []

    with open(path, "r", encoding="utf-8") as file:
        for line in file:
            if line.strip():
                records.append(json.loads(line))

    return records


def load_json(path):
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def main():
    chunks = load_jsonl(CHUNK_FILE)
    pages = load_jsonl(PAGE_FILE)
    toc_registry = load_json(TOC_FILE)

    page_registry = build_page_registry(
        toc_registry,
        total_pages=len(pages)
    )

    multiple_policies = []
    multiple_sections = []
    missing_policy_metadata = []
    metadata_mismatches = []

    for chunk in chunks:
        start = chunk["page_start"]
        end = chunk["page_end"]

        covered_metadata = [
            page_registry.get(page, {})
            for page in range(start, end + 1)
        ]

        policies = {
            (
                metadata.get("policy_number"),
                metadata.get("policy_title")
            )
            for metadata in covered_metadata
            if metadata.get("policy_number") is not None
        }

        sections = {
            (
                metadata.get("major_section_number"),
                metadata.get("major_section")
            )
            for metadata in covered_metadata
            if metadata.get("major_section_number") is not None
        }

        if len(policies) > 1:
            multiple_policies.append((chunk, policies))

        if len(sections) > 1:
            multiple_sections.append((chunk, sections))

        if policies and chunk.get("policy_number") is None:
            missing_policy_metadata.append((chunk, policies))

        starting_metadata = page_registry.get(start, {})

        expected_policy = starting_metadata.get("policy_number")
        stored_policy = chunk.get("policy_number")

        if expected_policy != stored_policy:
            metadata_mismatches.append(
                (chunk, expected_policy, stored_policy)
            )

    print("\n--- FIXED-SIZE METADATA AUDIT ---")
    print(f"Total chunks: {len(chunks)}")
    print(f"Chunks spanning multiple policies: {len(multiple_policies)}")
    print(f"Chunks spanning multiple major sections: {len(multiple_sections)}")
    print(f"Chunks with policy content but missing policy metadata: {len(missing_policy_metadata)}")
    print(f"Starting-page metadata mismatches: {len(metadata_mismatches)}")

    print("\n--- MULTIPLE POLICY CHUNKS ---")

    for chunk, policies in multiple_policies:
        print(f"\n{chunk['chunk_id']}")
        print(f"Pages: {chunk['page_start']} - {chunk['page_end']}")
        print(f"Stored policy: {chunk.get('policy_number')} - {chunk.get('policy_title')}")
        print(f"Policies actually covered: {sorted(policies, key=lambda x: str(x[0]))}")

    print("\n--- MISSING POLICY METADATA ---")

    for chunk, policies in missing_policy_metadata:
        print(f"\n{chunk['chunk_id']}")
        print(f"Pages: {chunk['page_start']} - {chunk['page_end']}")
        print(f"Policies actually covered: {sorted(policies, key=lambda x: str(x[0]))}")

    print("\n--- STARTING-PAGE METADATA MISMATCHES ---")

    for chunk, expected, stored in metadata_mismatches:
        print(
            f"{chunk['chunk_id']} | "
            f"Expected: {expected} | Stored: {stored}"
        )

    print("\n--- AUDIT COMPLETE ---")


if __name__ == "__main__":
    main()
