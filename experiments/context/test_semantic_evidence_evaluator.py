
from src.hr_assistant.context import SemanticEvidenceEvaluator


def main():

    evaluator = SemanticEvidenceEvaluator()

    query = "How can an employee raise a workplace complaint?"

    required_evidence = [
        "The employee should raise the grievance with their line manager.",
        "The grievance can initially be raised verbally or in writing.",
        "If the manager cannot resolve it, a formal written grievance should be submitted.",
    ]

    test_cases = [

        {
            "name": "Complete evidence",
            "context": """
            An employee should raise the matter with their line manager.
            The grievance can be raised verbally or in writing.
            If the manager cannot resolve the matter, a formal written
            grievance form should be submitted.
            """,
        },

        {
            "name": "Missing evidence",
            "context": """
            An employee should raise the matter with their line manager.
            The grievance can be raised verbally or in writing.
            """,
        },

        {
            "name": "Contradictory evidence",
            "context": """
            An employee should raise the matter with their line manager.
            The grievance can be raised verbally or in writing.
            If the manager cannot resolve the matter, no formal written
            grievance is required.
            """,
        },
    ]

    for test_case in test_cases:

        print("\n" + "=" * 70)
        print(test_case["name"])
        print("=" * 70)

        result = evaluator.evaluate(
            query=query,
            context=test_case["context"],
            required_evidence=required_evidence,
        )

        print("Evaluation:", result["evaluation_status"])
        print("Answerable:", result["answerable"])
        print("Status:", result["overall_status"])
        print("Assessments:", result["evidence_assessments"])
        print("Missing conditions:", result["missing_conditions"])
        print("Contradictions:", result["contradictions"])
        print("Reason:", result["reason"])

        if result["evaluation_status"] == "failed":
            print("Error:", result["error"])


if __name__ == "__main__":
    main()
