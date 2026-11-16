
from pypdf import PdfReader

from src.hr_assistant.config import RAW_DATA_DIR


PDF_PATH = RAW_DATA_DIR / "hr_policy_manual.pdf"

PAGES_TO_INSPECT = [35, 91]

Y_TOLERANCE = 1.5
MAX_HORIZONTAL_GAP = 60


def extract_fragments(page):

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
            "x": float(tm[4]),
            "y": float(tm[5])
        })

    page.extract_text(
        visitor_text=visitor_text
    )

    return fragments


def estimate_text_width(fragment):

    # Approximate width for grouping only.
    # This is not an exact PDF text measurement.

    return (
        len(fragment["text"])
        * fragment["font_size"]
        * 0.5
    )


def reconstruct_text(group):

    reconstructed = ""

    for index, fragment in enumerate(group):

        if index == 0:
            reconstructed = fragment["text"]
            continue

        previous = group[index - 1]

        estimated_end = (
            previous["x"]
            + estimate_text_width(previous)
        )

        horizontal_gap = (
            fragment["x"] - estimated_end
        )

        if horizontal_gap > 1.5:
            reconstructed += " "

        reconstructed += fragment["text"]

    return reconstructed



def group_fragments_into_lines(fragments):

    # Sort from top to bottom, then left to right.
    fragments.sort(
        key=lambda item: (
            -item["y"],
            item["x"]
        )
    )

    lines = []

    for fragment in fragments:

        matching_line = None

        # Find an existing line with a similar Y coordinate
        # and matching font.
        for line in reversed(lines):

            same_baseline = (
                abs(line["y"] - fragment["y"])
                <= Y_TOLERANCE
            )

            same_font = (
                line["font"] == fragment["font"]
                and line["font_size"] == fragment["font_size"]
            )

            if same_baseline and same_font:

                matching_line = line
                break

        if matching_line is None:

            lines.append({
                "y": fragment["y"],
                "font": fragment["font"],
                "font_size": fragment["font_size"],
                "fragments": [fragment]
            })

        else:

            matching_line["fragments"].append(
                fragment
            )

    reconstructed_lines = []

    for line in lines:

        line_fragments = sorted(
            line["fragments"],
            key=lambda item: item["x"]
        )

        # Split distant fragments into separate visual lines.
        groups = []
        current_group = []

        for fragment in line_fragments:

            if not current_group:

                current_group.append(fragment)
                continue

            previous = current_group[-1]

            estimated_end = (
                previous["x"]
                + estimate_text_width(previous)
            )

            horizontal_gap = (
                fragment["x"] - estimated_end
            )

            if horizontal_gap > MAX_HORIZONTAL_GAP:

                groups.append(current_group)
                current_group = [fragment]

            else:

                current_group.append(fragment)

        if current_group:
            groups.append(current_group)

        for group in groups:

            reconstructed_lines.append({
                "y": line["y"],
                "font": line["font"],
                "font_size": line["font_size"],
                "x": group[0]["x"],
                 "text": reconstruct_text(group)
            })

    # Restore top-to-bottom, left-to-right order.
    reconstructed_lines.sort(
        key=lambda item: (
            -item["y"],
            item["x"]
        )
    )

    return reconstructed_lines


def inspect_page(reader, page_number):

    page = reader.pages[page_number - 1]

    fragments = extract_fragments(page)

    lines = group_fragments_into_lines(
        fragments
    )

    print(f"\n{'=' * 80}")
    print(f"PAGE {page_number} - RECONSTRUCTED LINES")
    print(f"{'=' * 80}")

    for index, line in enumerate(lines, start=1):

        print(
            f"{index:03} | "
            f"Y={line['y']:7.2f} | "
            f"X={line['x']:7.2f} | "
            f"SIZE={line['font_size']:5.2f} | "
            f"FONT={line['font']} | "
            f"TEXT={line['text']!r}"
        )


if __name__ == "__main__":

    reader = PdfReader(str(PDF_PATH))

    for page_number in PAGES_TO_INSPECT:

        inspect_page(
            reader,
            page_number
        )
