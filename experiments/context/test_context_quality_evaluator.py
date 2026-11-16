
from src.hr_assistant.context.context_quality_evaluator import (
    ContextQualityEvaluator,
)


def main():

    # All three required evidence items from the semantic evaluator test.
    required_evidence = [
        "Employees should first try to resolve the complaint informally, if they feel able to do so.",
        "If informal resolution is not possible or unsuccessful, the employee can raise a formal complaint in writing.",
        "The employee may submit the complaint to a more senior manager if they feel unable to approach their line manager.",
    ]

    context = """
    Employees are encouraged to resolve workplace complaints informally
    with their line manager or Human Resources, provided they feel able
    to do so.

    If the employee feels unable to resolve the issue informally, or if
    the informal approach is unsuccessful, they may raise a formal
    complaint with the employer.

    Normally, the employee should submit the formal complaint to their
    line manager. However, if the employee feels unable to approach their
    line manager, they should submit the complaint in writing to a more
    senior manager within their department or directorate.
    """

    context_output = {
        "query": "How can an employee raise a workplace complaint?",
        "context": context,
        "sources": [
            {
                "source_id": "synthetic_hr_policy:parent:00001",
                "policy_title": "Grievance Procedure",
                "page_start": 62,
                "page_end": 63,
            }
        ],
        "context_status": "ready",
        "budget_status": "within_budget",
        "token_count": 180,
        "token_budget": 3000,
        "excluded_count": 0,
    }

    evaluator = ContextQualityEvaluator()

    result = evaluator.evaluate(
        context_output=context_output,
        required_evidence=required_evidence,
    )

    print("\n========== CONTEXT QUALITY EVALUATION ==========")
    print("Query:", result["query"])
    print("Answerable:", result["answerable"])
    print("Final Status:", result["final_status"])

    print("\n========== STRUCTURAL EVALUATION ==========")
    print(result["structural_evaluation"])

    print("\n========== EXACT EVIDENCE EVALUATION ==========")
    print(result["exact_evidence_evaluation"])

    print("\n========== SEMANTIC EVALUATION ==========")
    print(result["semantic_evaluation"])

    assert result["answerable"] is True
    assert result["final_status"] == "sufficient"

    print("\nContext quality evaluation passed.")


if __name__ == "__main__":
    main()
