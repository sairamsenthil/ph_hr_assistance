from pypdf import PdfReader

from src.hr_assistant.config import RAW_DATA_DIR


pdf_path = RAW_DATA_DIR / "hr_policy_manual.pdf"

reader = PdfReader(str(pdf_path))

target_pages = {
    8: [
        "Recruitment and Selection",
        "Introduction",
        "Advertisements",
        "Application Form"
    ],
    14: [
        "Induction Policy and Checklist",
        "General Policy Statement",
        "Aim",
        "The Company's Commitment"
    ],
    35: [
        "Performance Appraisal Policy",
        "Appraisal Policy",
        "Core Principles"
    ],
    91: [
        "Health and Safety Policy",
        "Statement of General Policy"
    ]
}


for page_number, keywords in target_pages.items():

    page = reader.pages[page_number - 1]

    print(f"\n{'=' * 20} PAGE {page_number} {'=' * 20}")

    spans = []

    def collect_text(text, cm, tm, font_dict, font_size):

        if text.strip():
            spans.append({
                "text": text.strip(),
                "font_size": round(font_size, 2),
                "font": (
                    font_dict.get("/BaseFont", "Unknown")
                    if font_dict else "Unknown"
                )
            })

    page.extract_text(visitor_text=collect_text)

    for span in spans:

        if any(
            keyword.lower() in span["text"].lower()
            for keyword in keywords
        ):

            print(
                f"Text: {span['text']}\n"
                f"Font size: {span['font_size']}\n"
                f"Font: {span['font']}\n"
                f"{'-' * 45}"
            )