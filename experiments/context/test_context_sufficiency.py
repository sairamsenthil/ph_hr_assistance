
from src.hr_assistant.context import ContextSufficiencyEvaluator


def main():

    evaluator = ContextSufficiencyEvaluator()

    test_cases = [

        {
            "name": "Valid context",
            "context_output": {
                "query": "How can I raise a grievance?",
                "context": "[SOURCE 1]\nGrievance procedure...",
                "sources": [{"source_id": "parent_001"}],
                "context_status": "ready",
                "budget_status": "within_budget",
                "token_count": 1200,
                "token_budget": 3000,
                "excluded_count": 0,
            },
        },

        {
            "name": "Empty context",
            "context_output": {
                "query": "How can I raise a grievance?",
                "context": "",
                "sources": [],
                "context_status": "empty",
                "budget_status": "within_budget",
                "token_count": 0,
                "token_budget": 3000,
                "excluded_count": 0,
            },
        },

        {
            "name": "Sources excluded",
            "context_output": {
                "query": "How can I raise a grievance?",
                "context": "[SOURCE 1]\nGrievance procedure...",
                "sources": [{"source_id": "parent_001"}],
                "context_status": "ready",
                "budget_status": "within_budget",
                "token_count": 2500,
                "token_budget": 3000,
                "excluded_count": 2,
            },
        },

        {
            "name": "Token budget exceeded",
            "context_output": {
                "query": "How can I raise a grievance?",
                "context": "[SOURCE 1]\nGrievance procedure...",
                "sources": [{"source_id": "parent_001"}],
                "context_status": "ready",
                "budget_status": "exceeded",
                "token_count": 3500,
                "token_budget": 3000,
                "excluded_count": 0,
            },
        },
    ]

    for test_case in test_cases:

        result = evaluator.evaluate(
            test_case["context_output"]
        )

        print("\n" + "=" * 65)
        print(test_case["name"])
        print("=" * 65)

        print("Answerable:", result["answerable"])
        print("Status:", result["sufficiency_status"])
        print("Issues:", result["issues"])


if __name__ == "__main__":
    main()
