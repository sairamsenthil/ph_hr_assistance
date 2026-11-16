
import json

from pypdf import PdfReader

from src.hr_assistant.config import RAW_DATA_DIR, PROCESSED_DATA_DIR
from src.hr_assistant.metadata.toc_extractor import extract_toc_entries
from src.hr_assistant.metadata.toc_registry import (
    build_registry,
    find_numbering_gaps,
    calculate_statistics,
    find_unclassified_entries
)


if __name__ == "__main__":

    # Read the original PDF.
    pdf_path = RAW_DATA_DIR / "hr_policy_manual.pdf"

    reader = PdfReader(str(pdf_path))

    # Extract TOC entries.
    entries = extract_toc_entries(reader)

    print("\n--- TOC EXTRACTION REPORT ---")
    print("Total extracted entries:", len(entries))

    # Build structured registry.
    registry = build_registry(entries)

    # Validate subsection numbering.
    gaps = find_numbering_gaps(registry)

    print("\n--- SUBSECTION NUMBERING VALIDATION ---")

    if gaps:

        for gap in gaps:
            print(
                f"Policy {gap['policy_number']} - "
                f"{gap['policy_title']}: "
                f"Missing {gap['missing_subsections']}"
            )

    else:
        print("No numbering gaps found.")

    # Identify genuinely unclassified entries.
    unclassified = find_unclassified_entries(
        entries,
        registry
    )

    print("\n--- UNCLASSIFIED TOC ENTRIES ---")

    if unclassified:

        for entry in unclassified:
            print(
                f"Page {entry['page']}: "
                f"{entry['title']}"
            )

    else:
        print("No unclassified entries found.")

    print(
        "Total unclassified entries:",
        len(unclassified)
    )

    # Calculate statistics.
    statistics = calculate_statistics(registry)

    print("\n--- STRUCTURED TOC REPORT ---")
    print("Major sections:", statistics["major_sections"])
    print("Main policies:", statistics["main_policies"])
    print("Subsections:", statistics["subsections"])

    # Display hierarchy.
    for section in registry["major_sections"]:

        print(
            f"\nSECTION {section['section_number']}: "
            f"{section['title']}"
        )

        for policy in section["policies"]:

            print(
                f"  POLICY {policy['policy_number']}: "
                f"{policy['title']}"
            )

            for subsection in policy["subsections"]:

                print(
                    f"      {subsection['subsection_number']}. "
                    f"{subsection['title']} "
                    f"(Page {subsection['page_start']})"
                )

    # Save registry.
    PROCESSED_DATA_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    output_path = PROCESSED_DATA_DIR / "hr_toc_registry.json"

    with output_path.open("w", encoding="utf-8") as file:

        json.dump(
            registry,
            file,
            indent=4,
            ensure_ascii=False
        )

    print("\nRegistry saved to:", output_path)
