
from src.hr_assistant.generation.claim_grounding_validator import (
    ClaimGroundingValidator,
)


def main():

    validator = ClaimGroundingValidator()

    test_cases = [
        {
            "name": "Fully supported claims",
            "claims": [
                {"status": "supported"},
                {"status": "supported"},
            ],
            "expected": True,
        },
        {
            "name": "Partially supported claims",
            "claims": [
                {"status": "supported"},
                {"status": "partially_supported"},
            ],
            "expected": False,
        },
        {
            "name": "Unsupported claims",
            "claims": [
                {"status": "supported"},
                {"status": "unsupported"},
            ],
            "expected": False,
        },
        {
            "name": "Contradicted claims",
            "claims": [
                {"status": "supported"},
                {"status": "contradicted"},
            ],
            "expected": False,
        },
        {
            "name": "Empty claims",
            "claims": [],
            "expected": False,
        },
    ]

    for test in test_cases:

        result = validator.validate(test["claims"])

        print(f"\nTest: {test['name']}")
        print(result)

        assert result["grounded"] == test["expected"]

    print("\nAll claim grounding tests passed.")


if __name__ == "__main__":
    main()
