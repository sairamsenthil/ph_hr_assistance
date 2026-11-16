
import sys
from pathlib import Path
from collections import Counter

from pypdf import PdfReader

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.hr_assistant.config import RAW_DATA_DIR
from src.hr_assistant.metadata.toc_extractor import extract_toc_entries
from src.hr_assistant.metadata.toc_registry import build_registry
from src.hr_assistant.ingestion.heading_identifier import normalize_for_matching


PDF_PATH = RAW_DATA_DIR / "hr_policy_manual.pdf"


def inspect_heading_formatting(page, title):

    fragments = []

    def visitor_text(text, cm, tm, font_dict, font_size):

        if not text:
            return

        font_name = "Unknown"

        if font_dict:
            font_name = str(
                font_dict.get("/BaseFont", "Unknown")
            )

        normalized_fragment = normalize_for_matching(text)

        for character in normalized_fragment:
            fragments.append({
                "character": character,
                "font": font_name,
                "font_size": (
                    float(font_size)
                    if font_size
                    else 0.0
                )
            })

    page.extract_text(visitor_text=visitor_text)

    normalized_title = normalize_for_matching(title)

    extracted_text = "".join(
        item["character"]
        for item in fragments
    )

    match_position = extracted_text.find(normalized_title)

    if match_position == -1:
        return None

    matched_fragments = fragments[
        match_position:
        match_position + len(normalized_title)
    ]

    font_counts = Counter(
        item["font"]
        for item in matched_fragments
    )

    bold_characters = sum(
        count
        for font, count in font_counts.items()
        if "bold" in font.lower()
    )

    italic_characters = sum(
        count
        for font, count in font_counts.items()
        if "italic" in font.lower()
    )

    total_characters = len(matched_fragments)

    return {
        "font_counts": font_counts,
        "bold_percentage": (
            bold_characters / total_characters * 100
        ),
        "italic_percentage": (
            italic_characters / total_characters * 100
        )
    }


if __name__ == "__main__":

    reader = PdfReader(str(PDF_PATH))

    entries = extract_toc_entries(reader)
    registry = build_registry(entries)

    results = []

    for section in registry["major_sections"]:

        for policy in section["policies"]:

            for subsection in policy["subsections"]:

                page_number = subsection["page_start"]
                page = reader.pages[page_number - 1]

                formatting = inspect_heading_formatting(
                    page,
                    subsection["title"]
                )

                results.append({
                    "policy_number": policy["policy_number"],
                    "subsection_number": subsection["subsection_number"],
                    "title": subsection["title"],
                    "page": page_number,
                    "formatting": formatting
                })

    matched = [
        item for item in results
        if item["formatting"] is not None
    ]

    unmatched = [
        item for item in results
        if item["formatting"] is None
    ]

    bold_majority = [
        item for item in matched
        if item["formatting"]["bold_percentage"] >= 50
    ]

    regular_majority = [
        item for item in matched
        if item["formatting"]["bold_percentage"] < 50
    ]

    print("\n--- SUBSECTION FORMATTING REPORT ---")
    print("Total subsections:", len(results))
    print("Formatting matches:", len(matched))
    print("Formatting not matched:", len(unmatched))
    print("Majority bold:", len(bold_majority))
    print("Majority non-bold:", len(regular_majority))

    print("\n--- NON-BOLD MAJORITY MATCHES ---")

    for item in regular_majority:

        formatting = item["formatting"]

        print(
            f"Policy {item['policy_number']} | "
            f"Subsection {item['subsection_number']} | "
            f"Page {item['page']} | "
            f"{item['title']}"
        )

        print(
            "  Bold:",
            round(formatting["bold_percentage"], 2),
            "% | Italic:",
            round(formatting["italic_percentage"], 2),
            "%"
        )

        print("  Fonts:", dict(formatting["font_counts"]))

    print("\n--- FORMATTING MATCH FAILURES ---")

    for item in unmatched:

        print(
            f"Policy {item['policy_number']} | "
            f"Subsection {item['subsection_number']} | "
            f"Page {item['page']} | "
            f"{item['title']}"
        )

    print("\n--- FONT DISTRIBUTION ---")

    all_fonts = Counter()

    for item in matched:
        all_fonts.update(
            item["formatting"]["font_counts"]
        )

    for font, count in all_fonts.most_common():
        print(f"{font}: {count} characters")
