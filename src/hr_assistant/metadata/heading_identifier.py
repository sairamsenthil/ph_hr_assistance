
import re


def normalize_for_matching(text: str) -> str:
    """
    Normalize text for comparison.

    Removes spaces, punctuation and line breaks so that
    PDF extraction artifacts such as 'Perfor mance' can
    still match 'Performance'.
    """

    return re.sub(
        r"[^a-z0-9]",
        "",
        text.lower()
    )


def identify_subsection_headings(
    reader,
    registry: dict
) -> list[dict]:
    """
    Check whether each TOC subsection title appears
    on its recorded starting page.

    This is an initial TOC-backed candidate detector.
    It does not yet verify font formatting.
    """

    results = []

    for section in registry["major_sections"]:

        for policy in section["policies"]:

            for subsection in policy["subsections"]:

                page_number = subsection["page_start"]

                if page_number < 1 or page_number > len(reader.pages):
                    results.append({
                        "document_id": registry["document_id"],
                        "major_section_number": section["section_number"],
                        "policy_number": policy["policy_number"],
                        "policy_title": policy["title"],
                        "subsection_number": subsection["subsection_number"],
                        "subsection_title": subsection["title"],
                        "page_start": page_number,
                        "found_on_start_page": False,
                        "status": "INVALID_PAGE"
                    })
                    continue

                page = reader.pages[page_number - 1]

                page_text = page.extract_text() or ""

                normalized_title = normalize_for_matching(
                    subsection["title"]
                )

                normalized_page_text = normalize_for_matching(
                    page_text
                )

                found = (
                    bool(normalized_title)
                    and normalized_title in normalized_page_text
                )

                results.append({
                    "document_id": registry["document_id"],
                    "major_section_number": section["section_number"],
                    "policy_number": policy["policy_number"],
                    "policy_title": policy["title"],
                    "subsection_number": subsection["subsection_number"],
                    "subsection_title": subsection["title"],
                    "page_start": page_number,
                    "found_on_start_page": found,
                    "status": "FOUND" if found else "NOT_FOUND"
                })

    return results
