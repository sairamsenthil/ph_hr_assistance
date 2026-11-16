
import unittest

from src.hr_assistant.security.document_access_control import (
    DocumentAccessControl,
)


class TestDocumentAccessControl(unittest.TestCase):

    def setUp(self):
        self.access_control = DocumentAccessControl()

    def test_employee_can_access_public_documents(self):
        self.assertTrue(
            self.access_control.can_access("employee", "public")
        )

    def test_employee_cannot_access_manager_documents(self):
        self.assertFalse(
            self.access_control.can_access("employee", "manager")
        )

    def test_manager_can_access_manager_documents(self):
        self.assertTrue(
            self.access_control.can_access("manager", "manager")
        )

    def test_manager_cannot_access_hr_documents(self):
        self.assertFalse(
            self.access_control.can_access("manager", "hr")
        )

    def test_hr_can_access_hr_documents(self):
        self.assertTrue(
            self.access_control.can_access("hr", "hr")
        )

    def test_hr_cannot_access_admin_documents(self):
        self.assertFalse(
            self.access_control.can_access("hr", "admin")
        )

    def test_admin_can_access_all_levels(self):
        for level in ("public", "manager", "hr", "admin"):
            with self.subTest(level=level):
                self.assertTrue(
                    self.access_control.can_access("admin", level)
                )

    def test_unknown_role_is_denied(self):
        self.assertFalse(
            self.access_control.can_access("superuser", "public")
        )

    def test_unknown_access_level_is_denied(self):
        self.assertFalse(
            self.access_control.can_access("admin", "confidential")
        )

    def test_malformed_role_is_denied(self):
        self.assertFalse(
            self.access_control.can_access(["admin"], "public")
        )

    def test_malformed_access_level_is_denied(self):
        self.assertFalse(
            self.access_control.can_access("admin", ["public"])
        )

    def test_filter_documents_returns_only_authorized_documents(self):

        documents = [
            {"name": "Public Policy", "access_level": "public"},
            {"name": "Manager Policy", "access_level": "manager"},
            {"name": "HR Policy", "access_level": "hr"},
            {"name": "Admin Policy", "access_level": "admin"},
        ]

        result = self.access_control.filter_documents(
            documents,
            "employee",
        )

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["name"], "Public Policy")

    def test_filter_documents_skips_malformed_records(self):

        documents = [
            {"name": "Public Policy", "access_level": "public"},
            "invalid record",
            {"name": "Invalid Policy"},
            {"name": "HR Policy", "access_level": "hr"},
        ]

        result = self.access_control.filter_documents(
            documents,
            "employee",
        )

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["name"], "Public Policy")

    def test_filter_documents_denies_unknown_role(self):

        documents = [
            {"name": "Public Policy", "access_level": "public"},
        ]

        result = self.access_control.filter_documents(
            documents,
            "unknown",
        )

        self.assertEqual(result, [])

    def test_filter_documents_rejects_non_list_input(self):

        with self.assertRaises(ValueError):
            self.access_control.filter_documents(
                {"name": "Public Policy"},
                "employee",
            )

    def test_filter_documents_denies_malformed_role(self):

        documents = [
            {"name": "Public Policy", "access_level": "public"},
        ]

        result = self.access_control.filter_documents(
            documents,
            ["admin"],
        )

        self.assertEqual(result, [])


if __name__ == "__main__":
    unittest.main()
