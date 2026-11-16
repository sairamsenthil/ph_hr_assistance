
from pypdf import PdfReader

from src.hr_assistant.config import RAW_DATA_DIR


PDF_PATH = RAW_DATA_DIR / "hr_policy_manual.pdf"

PAGES_TO_INSPECT = [35, 91]


def inspect_fragments(reader, page_number):

    page = reader.pages[page_number - 1]

    fragments = []

    def visitor_text(text, cm, tm, font_dict, font_size):

        text = text.strip()

        if not text:
            return

        font_name = "Unknown"

        if font_dict:
            font_name = str(
                font_dict.get("/BaseFont", "Unknown")
            )

        fragments.append({
            "text": text,
            "font": font_name,
            "font_size": round(float(font_size), 2),
            "x": round(float(tm[4]), 2),
            "y": round(float(tm[5]), 2)
        })

    page.extract_text(
        visitor_text=visitor_text
    )

    # Sort by vertical position, then horizontal position.
    # PDF coordinates normally increase upwards, so higher
    # Y values appear earlier on the page.
    fragments.sort(
        key=lambda item: (
            -item["y"],
            item["x"]
        )
    )

    print(f"\n{'=' * 80}")
    print(f"PAGE {page_number} - ORDERED TEXT FRAGMENTS")
    print(f"{'=' * 80}")

    for index, fragment in enumerate(
        fragments,
        start=1
    ):

        print(
            f"{index:03} | "
            f"Y={fragment['y']:7.2f} | "
            f"X={fragment['x']:7.2f} | "
            f"SIZE={fragment['font_size']:5.2f} | "
            f"FONT={fragment['font']} | "
            f"TEXT={fragment['text']!r}"
        )


if __name__ == "__main__":

    reader = PdfReader(str(PDF_PATH))

    for page_number in PAGES_TO_INSPECT:

        inspect_fragments(
            reader,
            page_number
        )
