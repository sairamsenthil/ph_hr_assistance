
import sys
from pathlib import Path

from pypdf import PdfReader

# Add project root to Python's module search path.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from src.hr_assistant.config import RAW_DATA_DIR
from src.hr_assistant.metadata.toc_extractor import extract_toc_entries


if __name__ == "__main__":

    pdf_path = RAW_DATA_DIR / "hr_policy_manual.pdf"

    reader = PdfReader(str(pdf_path))

    entries = extract_toc_entries(reader)

    print("\n--- EXTRACTED TOC ENTRIES ---")
    print("Total entries:", len(entries))

    for entry in entries:
        print(entry)
