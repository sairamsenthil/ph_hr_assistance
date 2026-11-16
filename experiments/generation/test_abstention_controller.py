
from src.hr_assistant.generation.abstention_controller import (
    AbstentionController,
)


def main():

    controller = AbstentionController()

    sufficient_context = {
        "answerable": True,
        "final_status": "sufficient",
    }

    insufficient_context = {
        "answerable": False,
        "final_status": "evidence_insufficient",
    }

    grounded_claims = {
        "grounded": True,
    }

    ungrounded_claims = {
        "grounded": False,
    }

    valid_citations = {
        "valid": True,
    }

    invalid_citations = {
        "valid": False,
    }

    test_cases = [
        {
            "name": "All checks pass",
            "context": sufficient_context,
            "claims": grounded_claims,
            "citations": valid_citations,
            "expected": "answer",
        },
        {
            "name": "Insufficient context",
            "context": insufficient_context,
            "claims": grounded_claims,
            "citations": valid_citations,
            "expected": "abstain",
        },
        {
            "name": "Grounding failure",
            "context": sufficient_context,
            "claims": ungrounded_claims,
            "citations": valid_citations,
            "expected": "abstain",
        },
        {
            "name": "Citation failure",
            "context": sufficient_context,
            "claims": grounded_claims,
            "citations": invalid_citations,
            "expected": "abstain",
        },
    ]

    for test in test_cases:

        result = controller.decide(
            context_quality=test["context"],
            claim_grounding=test["claims"],
            citation_validation=test["citations"],
        )

        print(f"\nTest: {test['name']}")
        print(result)

        assert result["decision"] == test["expected"]

    print("\nAll abstention controller tests passed.")


if __name__ == "__main__":
    main()
