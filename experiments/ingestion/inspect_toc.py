from pypdf import PdfReader

from src.hr_assistant.config import RAW_DATA_DIR


pdf_path = RAW_DATA_DIR / "hr_policy_manual.pdf"

reader = PdfReader(str(pdf_path))

# PDF pages 3, 4, 5 and 6
toc_pages = [3, 4, 5, 6]

for page_number in toc_pages:

    page = reader.pages[page_number - 1]

    print(f"\n{'=' * 25} PAGE {page_number} {'=' * 25}")

    text = page.extract_text() or ""

    print(text)