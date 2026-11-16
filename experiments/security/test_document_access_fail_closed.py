
from src.hr_assistant.security.document_access_control import (
    DocumentAccessControl,
)


def main():

    access_control = DocumentAccessControl()

    documents = [
        {"id": 1, "access_level": "public"},
        {"id": 2, "access_level": "manager"},
        {"id": 3, "access_level": "hr"},
        {"id": 4, "access_level": "admin"},
        {"id": 5},  # Missing access metadata
        {"id": 6, "access_level": "unknown"},
    ]

    test_cases = [
        ("employee", 1),
        ("manager", 2),
        ("hr", 3),
        ("admin", 4),
        ("unknown", 0),
    ]

    print("\n========== FAIL-CLOSED ACCESS CONTROL ==========")

    for role, expected_minimum in test_cases:

        authorized = access_control.filter_documents(
            documents=documents,
            user_role=role,
        )

        print(f"\nRole: {role}")
        print("Authorized document IDs:", [
            doc["id"] for doc in authorized
        ])

        assert len(authorized) == expected_minimum

        # Missing metadata must never be authorized
        assert all(doc["id"] != 5 for doc in authorized)

        # Unknown access levels must never be authorized
        assert all(doc["id"] != 6 for doc in authorized)

    # Direct authorization checks
    assert access_control.can_access("employee", "admin") is False
    assert access_control.can_access("hr", "admin") is False
    assert access_control.can_access("admin", "admin") is True
    assert access_control.can_access("employee", None) is False

    print("\nAll fail-closed authorization tests passed.")


if __name__ == "__main__":
    main()
