
from src.hr_assistant.generation.citation_grounding_evaluator import (
    CitationGroundingEvaluator,
)


def main():

    evaluator = CitationGroundingEvaluator()

    claims = [
        {
            "claim": "Employees can raise harassment complaints with Human Resources.",
            "source_id": "policy_001",
            "source_text": (
                "Any employee who wishes to make a complaint of harassment "
                "or bullying is encouraged to first discuss matters informally "
                "with their line manager or with Human Resources."
            ),
        },
        {
            "claim": "Employees must submit harassment complaints within 2 days.",
            "source_id": "policy_001",
            "source_text": (
                "Any employee who wishes to make a complaint of harassment "
                "or bullying is encouraged to first discuss matters informally "
                "with their line manager or with Human Resources."
            ),
        },
    ]

    print("\n========== CITATION GROUNDING EVALUATION ==========")

    result = evaluator.evaluate(claims)

    print("Evaluation success:", result["success"])
    print("Model:", result["model"])
    print("Fallback used:", result["fallback_used"])

    for assessment in result["assessments"]:

        print("\nClaim:", assessment["claim"])
        print("Source:", assessment["source_id"])
        print("Status:", assessment["status"])
        print("Reason:", assessment["reason"])

    if not result["success"]:
        print("\nEvaluation failed:", result.get("error"))
        return

    assert len(result["assessments"]) == len(claims)

    for assessment in result["assessments"]:
        assert assessment["status"] in evaluator.ALLOWED_STATUSES

    print("\nCitation grounding evaluator test passed.")


if __name__ == "__main__":
    main()
