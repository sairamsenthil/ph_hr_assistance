
import sys
from pathlib import Path

from pypdf import PdfReader

# Add project root to Python's module search path.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.hr_assistant.config import RAW_DATA_DIR


PDF_PATH = RAW_DATA_DIR / "hr_policy_manual.pdf"

PAGES_TO_INSPECT = [
    8, 14, 15, 28, 35, 91, 93
]


def inspect_page(reader, page_number):

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

        font_size = (
            float(font_size)
            if font_size
            else 0.0
        )

        is_large = font_size > 12.5

        is_bold_or_italic = (
            "bold" in font_name.lower()
            or "italic" in font_name.lower()
        )

        fragments.append({
            "text": text,
            "font": font_name,
            "font_size": round(font_size, 2),
            "x": float(tm[4]),
            "y": float(tm[5]),
            "heading_signal": is_large or is_bold_or_italic
        })

    page.extract_text(visitor_text=visitor_text)

    # Group fragments that appear on approximately
    # the same visual line.
    fragments.sort(
        key=lambda item: (-item["y"], item["x"])
    )

    lines = []

    for fragment in fragments:

        matching_line = None

        for line in lines:

            if abs(line["y"] - fragment["y"]) <= 2.0:
                matching_line = line
                break

        if matching_line is None:

            matching_line = {
                "y": fragment["y"],
                "fragments": []
            }

            lines.append(matching_line)

        matching_line["fragments"].append(fragment)

    print("\n" + "=" * 90)
    print(f"PAGE {page_number} - TEXT AND FORMATTING INSPECTION")
    print("=" * 90)

    for line in lines:

        line_fragments = sorted(
            line["fragments"],
            key=lambda item: item["x"]
        )

        combined_text = " ".join(
            item["text"]
            for item in line_fragments
        )

        has_heading_signal = any(
            item["heading_signal"]
            for item in line_fragments
        )

        marker = (
            "POSSIBLE HEADING"
            if has_heading_signal
            else "BODY TEXT"
        )

        print(f"\n[{marker}]")
        print("Text:", combined_text)

        for item in line_fragments:

            print(
                f"  Font={item['font']}, "
                f"Size={item['font_size']}, "
                f"X={item['x']:.2f}, "
                f"Y={item['y']:.2f}"
            )


if __name__ == "__main__":

    if not PDF_PATH.exists():
        raise FileNotFoundError(
            f"PDF not found: {PDF_PATH}"
        )

    reader = PdfReader(str(PDF_PATH))

    for page_number in PAGES_TO_INSPECT:

        inspect_page(reader, page_number)
