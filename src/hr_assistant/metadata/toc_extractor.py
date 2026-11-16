
import re

from pypdf import PdfReader


def extract_toc_entries(reader: PdfReader) -> list[dict]:
    """
    Extract structured Table of Contents entries
    from PDF pages 3 to 6.
    """

    entries = []
    pending_lines = []

    for page_number in range(3, 7):

        page = reader.pages[page_number - 1]
        text = page.extract_text() or ""

        for line in text.splitlines():

            line = line.strip()

            if not line:
                continue

            # Ignore standalone printed page numbers.
            if re.fullmatch(r"\d{1,3}", line):
                continue

            pending_lines.append(line)

            # An entry is complete when its accumulated
            # text ends with a page number.
            combined = " ".join(pending_lines)

            page_match = re.search(r"\s+(\d{1,3})\s*$", combined)

            if not page_match:
                continue

            page_reference = int(page_match.group(1))
            title_part = combined[:page_match.start()].strip()

            # Ignore front matter.
            if page_reference < 7:
                pending_lines = []
                continue

            # Remove dotted leaders.
            title = re.sub(
                r"(?:\s*\.\s*){3,}.*$",
                "",
                title_part
            ).strip()

            # Accept actual TOC entries.
            if title and re.search(r"\.{3,}", title_part):
                entries.append({
                    "title": title,
                    "page": page_reference
                })

            pending_lines = []

    return entries
