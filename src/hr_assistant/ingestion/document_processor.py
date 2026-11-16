import json

from ..config import RAW_DATA_DIR, PROCESSED_DATA_DIR
from .document_loader import load_pdf
from .text_cleaner import clean_documents

def process_pdf(file_name: str) -> list[dict]:
    """Extract and clean a PDF while preserving raw text."""

    pdf_path = RAW_DATA_DIR / file_name

    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    raw_documents = load_pdf(
    pdf_path,
    document_type="hr_policy_manual"
)
    cleaned_documents = clean_documents(raw_documents)

    return cleaned_documents


def save_documents(documents: list[dict], output_file: str) -> None:
    """Save processed documents as JSONL."""

    PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)

    output_path = PROCESSED_DATA_DIR / output_file

    with output_path.open("w", encoding="utf-8") as file:
        for document in documents:
            file.write(
                json.dumps(document, ensure_ascii=False) + "\n"
            )

    print(f"Saved {len(documents)} documents to: {output_path}")


if __name__ == "__main__":
    documents = process_pdf("hr_policy_manual.pdf")

    save_documents(
        documents,
        "hr_policy_pages.jsonl"
    )