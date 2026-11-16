
import json
from pathlib import Path

from src.hr_assistant.metadata.section_identifier import (
    build_page_registry
)

from src.hr_assistant.chunking.parent_child import (
    create_parent_child_chunks
)


PROJECT_ROOT = Path(__file__).resolve().parents[3]

PAGES_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "chunks"
    / "recursive"
    / "normalized_policy_pages.jsonl"
)


REGISTRY_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "hr_toc_registry.json"
)


OUTPUT_DIR = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "chunks"
    / "parent_child"
)

OUTPUT_FILE = OUTPUT_DIR / "parent-child.jsonl"


def load_jsonl(path):
    with open(path, "r", encoding="utf-8") as file:
        return [
            json.loads(line)
            for line in file
            if line.strip()
        ]

def save_chunks_jsonl(parents, children, output_file):

    output_file.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    all_chunks = parents + children

    with open(output_file, "w", encoding="utf-8") as file:

        for chunk in all_chunks:
            file.write(
                json.dumps(chunk, ensure_ascii=False) + "\n"
            )

    print("\n--- JSONL EXPORT ---")
    print(f"Total records saved: {len(all_chunks)}")
    print(f"Parent records: {len(parents)}")
    print(f"Child records: {len(children)}")
    print(f"Output file: {output_file}")

   
def main():

    print("\nLoading HR policy documents...")

    pages = load_jsonl(PAGES_FILE)

    with open(REGISTRY_FILE, "r", encoding="utf-8") as file:
        registry = json.load(file)

    total_pages = max(
    page["metadata"]["page"]
    for page in pages
)

    page_registry = build_page_registry(
        registry,
        total_pages=total_pages
    )

    print(f"Total pages loaded: {len(pages)}")

    print("\nGenerating parent-child chunks...")

    result = create_parent_child_chunks(
        pages=pages,
        page_registry=page_registry,
        parent_size=900,
        child_size=250,
        child_overlap=40,
    )

    parents = result["parents"]
    children = result["children"]

    save_chunks_jsonl(
    parents=parents,
    children=children,
    output_file=OUTPUT_FILE
)

    print("\n--- PARENT-CHILD REPORT ---")
    print(f"Total parent chunks: {len(parents)}")
    print(f"Total child chunks: {len(children)}")

    print("\n--- FIRST 10 PARENTS ---")

    for parent in parents[:10]:

        linked_children = [
            child for child in children
            if child["parent_chunk_id"] == parent["chunk_id"]
        ]

        print(
            f"Parent: {parent['chunk_id']} | "
            f"Policy: {parent['policy_title']} | "
            f"Tokens: {parent['token_count']} | "
            f"Pages: {parent['page_start']}-{parent['page_end']} | "
            f"Children: {len(linked_children)}"
        )

    print("\n--- FIRST 10 CHILDREN ---")

    for child in children[:10]:

        print(
            f"Child: {child['chunk_id']} | "
            f"Parent: {child['parent_chunk_id']} | "
            f"Policy: {child['policy_title']} | "
            f"Tokens: {child['token_count']} | "
            f"Pages: {child['page_start']}-{child['page_end']}"
        )

    # Validation

    parent_ids = {
        parent["chunk_id"]
        for parent in parents
    }

    orphan_children = [
        child for child in children
        if child["parent_chunk_id"] not in parent_ids
    ]

    invalid_policy_links = []

    parent_lookup = {
        parent["chunk_id"]: parent
        for parent in parents
    }

    for child in children:

        parent = parent_lookup.get(
            child["parent_chunk_id"]
        )

        if parent and (
            child["policy_number"] != parent["policy_number"]
        ):
            invalid_policy_links.append(child["chunk_id"])

    oversized_parents = sum(
        parent["token_count"] > 900
        for parent in parents
    )

    oversized_children = sum(
        child["token_count"] > 250
        for child in children
    )

    print("\n--- VALIDATION ---")

    print(
        f"Parents exceeding 900 tokens: {oversized_parents}"
    )

    print(
        f"Children exceeding 250 tokens: {oversized_children}"
    )

    print(
        f"Orphan children: {len(orphan_children)}"
    )

    print(
        f"Policy mismatches: {len(invalid_policy_links)}"
    )

    print("\n--- FINAL STATUS ---")

    checks = {
        "Parent token limit": oversized_parents == 0,
        "Child token limit": oversized_children == 0,
        "Parent-child links": len(orphan_children) == 0,
        "Policy isolation": len(invalid_policy_links) == 0,
        "Parents generated": len(parents) > 0,
        "Children generated": len(children) > 0,
    }

    for name, passed in checks.items():
        print(f"{'PASS' if passed else 'FAIL'}: {name}")

    if all(checks.values()):
        print("\nSUCCESS: Parent-child chunking validation passed.")
    else:
        print("\nFAILURE: Review the validation results.")


if __name__ == "__main__":
    main()
