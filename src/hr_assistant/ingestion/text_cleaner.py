import re
import unicodedata


def clean_text(text: str) -> str:
    """
    Normalize extracted PDF text while preserving
    meaningful paragraph and line structure.
    """

    # 1. Normalize Unicode characters
    text = unicodedata.normalize("NFKC", text)

    # 2. Remove soft hyphen characters
    text = text.replace("\u00ad", "")

    # 3. Standardize line endings
    text = text.replace("\r\n", "\n")
    text = text.replace("\r", "\n")

    # 4. Join words split by a hyphen at a line ending
    text = re.sub(
        r"(?<=\w)-[ \t]*\n[ \t]*(?=\w)",
        "",
        text
    )

    # 5. Normalize spaces and tabs on each line
    lines = []

    for line in text.split("\n"):
        line = re.sub(r"[ \t]+", " ", line)
        lines.append(line.strip())

    text = "\n".join(lines)

    # 6. Remove excessive blank lines
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()

def clean_documents(documents: list[dict]) -> list[dict]:
    """
    Clean extracted documents while preserving original text
    and metadata.
    """
    cleaned_documents = []

    for document in documents:
        cleaned_document = {
            **document,
            "cleaned_text": clean_text(document["text"])
        }

        cleaned_documents.append(cleaned_document)

    return cleaned_documents

if __name__ == "__main__":
    from .document_loader import load_pdf
    from .config import RAW_DATA_DIR

    pdf_path = RAW_DATA_DIR / "hr_policy_manual.pdf"

    pages = load_pdf(pdf_path)
    cleaned_pages = clean_documents(pages)

    original_chars = sum(len(page["text"]) for page in pages)
    cleaned_chars = sum(len(page["cleaned_text"]) for page in cleaned_pages)

    empty_pages = [
        page["metadata"]["page"]
        for page in cleaned_pages
        if not page["cleaned_text"]
    ]

    short_pages = [
        page["metadata"]["page"]
        for page in cleaned_pages
        if 0 < len(page["cleaned_text"]) < 50
    ]

    print("\n--- DOCUMENT CLEANING REPORT ---")
    print("Total pages:", len(cleaned_pages))
    print("Pages with empty cleaned text:", empty_pages)
    print("Pages with fewer than 50 characters:", short_pages)
    print("Original total characters:", original_chars)
    print("Cleaned total characters:", cleaned_chars)
    print("Characters removed:", original_chars - cleaned_chars)

    print("\n--- PAGE 2 CLEANED PREVIEW ---")
    print(cleaned_pages[1]["cleaned_text"][:1000])

    print("\n--- PAGE 40 VALIDATION ---")
    print(repr(cleaned_pages[39]["cleaned_text"]))

    print("\n--- RAW TEXT PRESERVATION ---")
    print("Original text preserved:",
          cleaned_pages[1]["text"] == pages[1]["text"])