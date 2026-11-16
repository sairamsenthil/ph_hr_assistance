
from src.hr_assistant.generation.citation_validator import (
    CitationValidator,
)


def main():

    validator = CitationValidator()

    sources = [
        {"source_id": "policy_001"},
        {"source_id": "policy_002"},
        {"source_id": "policy_003"},
    ]

    test_cases = [
        {
            "name": "Valid citations",
            "answer": (
                "Employees can raise complaints formally [SOURCE 1]. "
                "They may also approach HR [SOURCE 2]."
            ),
            "expected_valid": True,
            "expected_status": "valid",
        },
        {
            "name": "Invalid citation",
            "answer": "Employees can raise complaints [SOURCE 5].",
            "expected_valid": False,
            "expected_status": "invalid_citations_found",
        },
        {
            "name": "No citations",
            "answer": "Employees can raise workplace complaints.",
            "expected_valid": False,
            "expected_status": "missing_citations",
        },
        {
            "name": "Mixed valid and invalid",
            "answer": (
                "Employees can raise complaints [SOURCE 1]. "
                "They can also appeal [SOURCE 8]."
            ),
            "expected_valid": False,
            "expected_status": "invalid_citations_found",
        },
    ]

    for test in test_cases:

        result = validator.validate(
            answer=test["answer"],
            sources=sources,
        )

        print(f"\nTest: {test['name']}")
        print(result)

        assert result["valid"] == test["expected_valid"], (
            f"Unexpected validity for {test['name']}"
        )

        assert result["status"] == test["expected_status"], (
            f"Unexpected status for {test['name']}"
        )

    print("\nAll 4 citation existence tests passed.")


if __name__ == "__main__":
    main()
