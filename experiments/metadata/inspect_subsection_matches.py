
import sys
from pathlib import Path

from pypdf import PdfReader

# Add project root to Python's module search path.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.hr_assistant.config import RAW_DATA_DIR, PROCESSED_DATA_DIR
from src.hr_assistant.metadata.toc_extractor import extract_toc_entries
from src.hr_assistant.metadata.toc_registry import build_registry
from src.hr_assistant.ingestion.heading_identifier import identify_subsection_headings


if __name__ == "__main__":

    pdf_path = RAW_DATA_DIR / "hr_policy_manual.pdf"

    reader = PdfReader(str(pdf_path))

    # Rebuild the TOC registry.
    entries = extract_toc_entries(reader)
    registry = build_registry(entries)

    # Identify subsection candidates.
    results = identify_subsection_headings(
        reader,
        registry
    )

    found = [
        item for item in results
        if item["found_on_start_page"]
    ]

    not_found = [
        item for item in results
        if not item["found_on_start_page"]
    ]

    print("\n--- SUBSECTION MATCHING REPORT ---")
    print("Total subsection entries:", len(results))
    print("Found on starting page:", len(found))
    print("Not found on starting page:", len(not_found))

    print("\n--- MATCHING PERCENTAGE ---")

    if results:
        percentage = len(found) / len(results) * 100
        print(f"{percentage:.2f}%")

    print("\n--- SUBSECTIONS NOT FOUND ---")

    for item in not_found:

        print(
            f"Policy {item['policy_number']} - "
            f"{item['policy_title']} | "
            f"Subsection {item['subsection_number']}: "
            f"{item['subsection_title']} | "
            f"Page {item['page_start']} | "
            f"Status: {item['status']}"
        )

    print("\n--- SAMPLE SUCCESSFUL MATCHES ---")

    for item in found[:10]:

        print(
            f"Policy {item['policy_number']} | "
            f"{item['subsection_number']}. "
            f"{item['subsection_title']} | "
            f"Page {item['page_start']}"
        )
