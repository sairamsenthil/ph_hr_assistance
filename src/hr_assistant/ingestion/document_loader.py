from pathlib import Path
from pypdf import PdfReader

from ..config import RAW_DATA_DIR


def load_pdf(
    file_path: Path,
    document_type: str = "unknown"
) -> list[dict]:
    """
    Extract text page by page and attach document metadata.
    """

    reader = PdfReader(str(file_path))

    documents = []

    # Stable document identity derived from the filename.
    document_id = file_path.stem.lower().replace(" ", "_")

    for page_number, page in enumerate(reader.pages, start=1):

        text = page.extract_text() or ""

        documents.append({
            "text": text,
            "metadata": {
                "document_id": document_id,
                "source": file_path.name,
                "document_type": document_type,
                "page": page_number
            }
        })

    return documents


if __name__ == "__main__":

    pdf_path = RAW_DATA_DIR / "hr_policy_manual.pdf"

    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    pages = load_pdf(
        pdf_path,
        document_type="hr_policy_manual"
    )

    print("Total pages:", len(pages))
    print("First page metadata:", pages[0]["metadata"])
    print("Last page metadata:", pages[-1]["metadata"])