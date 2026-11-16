
from src.hr_assistant.context import ContextEvidenceEvaluator

from experiments.chunking.parent_child.evidence_dataset import (
    EVIDENCE_DATASET,
)


def main():

    evaluator = ContextEvidenceEvaluator()

    test_cases = [
        {
            "name": "Complete evidence",
            "context": (
                "Employees should raise a grievance with their "
                "line manager. They may raise it verbally or in writing."
            ),
            "required_evidence": [
                "line manager",
                "verbally or in writing",
            ],
        },
        {
            "name": "Partial evidence",
            "context": (
                "Employees should raise a grievance with their "
                "line manager."
            ),
            "required_evidence": [
                "line manager",
                "verbally or in writing",
            ],
        },
        {
            "name": "No matching evidence",
            "context": "Employees should follow company procedures.",
            "required_evidence": [
                "line manager",
                "verbally or in writing",
            ],
        },
    ]

    print("=" * 75)
    print("CONTEXT EVIDENCE EVALUATION")
    print("=" * 75)

    for test_case in test_cases:

        result = evaluator.evaluate(
            context=test_case["context"],
            required_evidence=test_case["required_evidence"],
        )

        print("\n" + "-" * 65)
        print(test_case["name"])
        print("-" * 65)

        print("Coverage:", f"{result['coverage']:.2%}")
        print("Matched:", result["matched_evidence"])
        print("Missing:", result["missing_evidence"])
        print("Complete:", result["evidence_complete"])


if __name__ == "__main__":
    main()
