import unittest

from src.hr_assistant.ingestion.text_cleaner import clean_text, clean_documents


class TestTextCleaner(unittest.TestCase):

    def test_removes_extra_spaces(self):
        self.assertEqual(clean_text("HR Policy   Manual"), "HR Policy Manual")

    def test_reduces_multiple_blank_lines(self):
        self.assertEqual(
            clean_text("Introduction\n\n\n\nPolicy"),
            "Introduction\n\nPolicy"
        )

    def test_joins_hyphenated_words_across_lines(self):
        self.assertEqual(clean_text("employ-\nment"), "employment")

    def test_preserves_normal_hyphenated_words(self):
        self.assertEqual(clean_text("part-time employee"), "part-time employee")

    def test_removes_soft_hyphen(self):
        self.assertEqual(clean_text("employ\u00adment"), "employment")

    def test_removes_leading_and_trailing_spaces(self):
        self.assertEqual(clean_text("  HR Policy Manual  "), "HR Policy Manual")

    def test_clean_documents_preserves_original_text(self):
        documents = [{
            "text": "  HR   Policy  ",
            "metadata": {"source": "test.pdf", "page": 1}
        }]

        result = clean_documents(documents)

        self.assertEqual(result[0]["text"], "  HR   Policy  ")
        self.assertEqual(result[0]["cleaned_text"], "HR Policy")

    def test_clean_documents_preserves_metadata(self):
        documents = [{
            "text": "HR Policy",
            "metadata": {"source": "test.pdf", "page": 1}
        }]

        result = clean_documents(documents)

        self.assertEqual(
            result[0]["metadata"],
            {"source": "test.pdf", "page": 1}
        )


if __name__ == "__main__":
    unittest.main()