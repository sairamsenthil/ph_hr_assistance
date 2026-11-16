import unittest

from src.hr_assistant.metadata.metadata_validator import validate_documents


def create_document(page=1, document_id="hr_policy_manual",
                    source="hr_policy_manual.pdf",
                    document_type="hr_policy_manual"):

    return {
        "text": "Sample HR policy text",
        "cleaned_text": "Sample HR policy text",
        "metadata": {
            "document_id": document_id,
            "source": source,
            "document_type": document_type,
            "page": page
        }
    }


class TestMetadataValidator(unittest.TestCase):

    def test_valid_metadata(self):
        documents = [
            create_document(1),
            create_document(2),
            create_document(3)
        ]
        self.assertEqual(validate_documents(documents), [])

    def test_detects_missing_source(self):
        document = create_document()
        del document["metadata"]["source"]

        errors = validate_documents([document])
        self.assertTrue(any("source" in error for error in errors))

    def test_detects_invalid_page_number(self):
        document = create_document(page=-1)

        errors = validate_documents([document])
        self.assertTrue(any("positive integer" in error for error in errors))

    def test_detects_duplicate_page(self):
        documents = [
            create_document(page=1),
            create_document(page=1)
        ]

        errors = validate_documents(documents)
        self.assertTrue(any("duplicate page" in error for error in errors))

    def test_detects_inconsistent_document_identity(self):
        documents = [
            create_document(page=1),
            create_document(page=2, source="another_file.pdf")
        ]

        errors = validate_documents(documents)
        self.assertTrue(any("inconsistent source" in error for error in errors))

    def test_detects_empty_document_list(self):
        errors = validate_documents([])
        self.assertTrue(len(errors) > 0)


if __name__ == "__main__":
    unittest.main()