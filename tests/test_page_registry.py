from pypdf import PdfReader
import sys
from pathlib import Path

# Add the project root to Python's module search path.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))
from src.hr_assistant.config import RAW_DATA_DIR
from src.hr_assistant.metadata.section_identifier import build_page_registry

from src.hr_assistant.metadata.toc_extractor import extract_toc_entries
from src.hr_assistant.metadata.toc_registry import build_registry


def main():

    pdf_path = RAW_DATA_DIR / "hr_policy_manual.pdf"

    reader = PdfReader(str(pdf_path))
    total_pages = len(reader.pages)

    # Rebuild the TOC hierarchy from the original PDF.
    entries = extract_toc_entries(reader)
    toc_registry = build_registry(entries)

    # Map PDF pages to their applicable hierarchy.
    page_registry = build_page_registry(
        toc_registry,
        total_pages
    )

        # Identify pages without policy mappings.
    unmapped_pages = sorted(
        set(range(1, total_pages + 1))
        - set(page_registry.keys())
    )

    print("\n--- UNMAPPED PAGE REPORT ---")
    print("Unmapped pages:", unmapped_pages)

    # Inspect TOC entries sharing the same starting page.
    print("\n--- SAME-PAGE TOC ENTRIES ---")

    for page_number in [8, 14, 35, 40, 91, 93]:

        print(f"\nPage {page_number}:")

        for entry in entries:

            if entry["page"] == page_number:
                print(" ", entry["title"])

    print("\n--- PAGE REGISTRY VALIDATION ---")
    print("Total PDF pages:", total_pages)
    print("Pages mapped:", len(page_registry))
    print("Pages not mapped:", total_pages - len(page_registry))

    pages_to_check = [8, 14, 35, 40, 89, 90, 91, 93, 98]

    for page_number in pages_to_check:

        print(f"\n--- PAGE {page_number} ---")

        page_info = page_registry.get(page_number)

        if page_info is None:
            print("No hierarchy assigned.")
            continue

        for field, value in page_info.items():
            print(f"{field}: {value}")

    print("\n--- MAJOR SECTION INTRODUCTION PAGES ---")

    for page_number in [7, 34, 61, 79]:

        page = reader.pages[page_number - 1]

        text = page.extract_text() or ""

        print(f"\nPAGE {page_number}")
        print("-" * 60)
        print(text[:1000])

        print("\n--- FINAL PAGE CLASSIFICATION ---")

    print("Total PDF pages:", total_pages)
    print("Total classified pages:", len(page_registry))

    region_counts = {}

    for page_info in page_registry.values():

        region = page_info["document_region"]

        region_counts[region] = (
            region_counts.get(region, 0) + 1
        )

    for region, count in region_counts.items():
        print(f"{region}: {count}")

    print("\n--- SAMPLE PAGE VALIDATION ---")

    for page_number in [1, 7, 8, 34, 35, 40, 61, 62, 79, 80, 91, 98]:

        print(
            f"Page {page_number}:",
            page_registry[page_number]
        )


if __name__ == "__main__":
    main()