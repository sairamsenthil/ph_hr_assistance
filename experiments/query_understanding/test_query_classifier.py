
from src.hr_assistant.query_understanding import QueryClassifier

from experiments.chunking.parent_child.test_retrieval_evaluation import (
    EVALUATION_DATASET,
)


ADDITIONAL_TEST_CASES = [
    {
        "query": "Who investigates a grievance and within how many days must they respond?",
        "expected": ["deadline", "responsibility"],
    },
    {
        "query": "Who is eligible for parental leave?",
        "expected": ["eligibility"],
    },
    {
        "query": "What constitutes workplace harassment?",
        "expected": ["definition"],
    },
    {
        "query": "Who can access confidential complaint records?",
        "expected": ["confidentiality"],
    },
    {
        "query": "How long are complaint records retained?",
        "expected": ["record_retention"],
    },
        {
        "query": "Who is responsible for investigating a grievance, and what is the response deadline?",
        "expected": ["deadline", "responsibility"],
    },
    {
        "query": "How long are complaint records kept?",
        "expected": ["record_retention"],
    },
    {
        "query": "What does harassment mean?",
        "expected": ["definition"],
    },
    {
        "query": "   How can an employee raise a complaint?   ",
        "expected": ["procedure"],
    },
    {
        "query": "Tell me the weather today.",
        "expected": ["general_information"],
    },
    {
        "query": "How many working days does a manager have to respond?",
        "expected": ["deadline"],
    },
    {
        "query": "Can an employee appeal a disciplinary decision?",
        "expected": ["disciplinary"],
    },
    {
    "query": "What is workplace harassment?",
    "expected": ["definition"],
    },
]


def main():

    classifier = QueryClassifier()

    print("=" * 75)
    print("QUERY CLASSIFICATION EVALUATION")
    print("=" * 75)

    test_cases = []

    # Existing retrieval evaluation questions
    for item in EVALUATION_DATASET:

        test_cases.append({
            "query": item["query"],
            "expected": None,
            "source": "existing_retrieval_dataset",
        })

    # Additional manually labelled examples
    for item in ADDITIONAL_TEST_CASES:

        test_cases.append({
            **item,
            "source": "additional_test_cases",
        })

    for index, test_case in enumerate(test_cases, start=1):

        result = classifier.classify(test_case["query"])

        print("\n" + "-" * 75)
        print(f"Test Case: {index}")
        print(f"Query: {result['original_query']}")
        print(f"Detected: {result['intents']}")
        print(f"Primary Intent: {result['primary_intent']}")

        if test_case["expected"] is not None:

            expected = set(test_case["expected"])
            actual = set(result["intents"])

            status = "PASS" if expected == actual else "FAIL"

            print(f"Expected: {sorted(expected)}")
            print(f"Actual:   {sorted(actual)}")
            print(f"Status:   {status}")

        else:
            print("Status: Unlabelled baseline observation")


if __name__ == "__main__":
    main()
