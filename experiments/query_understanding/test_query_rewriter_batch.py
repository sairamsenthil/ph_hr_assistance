import time

from src.hr_assistant.query_understanding import QueryRewriter


TEST_CASES = [
    {
        "id": "Q01",
        "category": "informal",
        "query": "My manager isn't listening to my complaint. What can I do?",
    },
    {
        "id": "Q02",
        "category": "deadline",
        "query": "How many working days does my manager have to reply to my grievance?",
    },
    {
        "id": "Q03",
        "category": "multiple_intents",
        "query": "Who investigates a complaint and how long do they have to complete it?",
    },
    {
        "id": "Q04",
        "category": "eligibility",
        "query": "Can someone working part time apply for parental leave?",
    },
    {
        "id": "Q05",
        "category": "confidentiality",
        "query": "Will everyone in the office know if I report harassment?",
    },
    {
        "id": "Q06",
        "category": "specific_condition",
        "query": "Can I complain directly to the director if my manager is the person involved?",
    },
    {
        "id": "Q07",
        "category": "already_clear",
        "query": "What is the formal grievance procedure for employees?",
    },
    {
        "id": "Q08",
        "category": "negation",
        "query": "Can I appeal a disciplinary decision if I do not agree with the outcome?",
    },
]


def main():

    rewriter = QueryRewriter()

    total_duration = 0
    successful = 0
    fallback_count = 0

    print("=" * 85)
    print("BATCH QUERY REWRITING EVALUATION")
    print("=" * 85)

    for test_case in TEST_CASES:

        start_time = time.perf_counter()

        result = rewriter.rewrite(test_case["query"])

        duration = time.perf_counter() - start_time
        total_duration += duration

        if result["rewrite_status"] == "success":
            successful += 1
        else:
            fallback_count += 1

        print("\n" + "-" * 85)
        print(f"Test ID: {test_case['id']}")
        print(f"Category: {test_case['category']}")

        print("\nOriginal Query:")
        print(result["original_query"])

        print("\nRewritten Query:")
        print(result["rewritten_query"])

        print(f"\nStatus: {result['rewrite_status']}")
        print(f"Fallback: {result['fallback_used']}")
        print(f"Latency: {duration:.2f} seconds")

        if result.get("error"):
            print(f"Error: {result['error']}")

    print("\n" + "=" * 85)
    print("BATCH EVALUATION SUMMARY")
    print("=" * 85)

    print(f"Total Queries: {len(TEST_CASES)}")
    print(f"Successful Rewrites: {successful}")
    print(f"Fallbacks: {fallback_count}")
    print(f"Total Duration: {total_duration:.2f} seconds")
    print(f"Average Latency: {total_duration / len(TEST_CASES):.2f} seconds")


if __name__ == "__main__":
    main()