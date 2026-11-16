
from time import perf_counter

from src.hr_assistant.query_understanding import QueryExpander


def main():

    expander = QueryExpander(max_queries=3)

    test_queries = [
        "How can I complain at work?",
        "How many working days does my manager have to reply to my grievance?",
        "Will everyone know if I report harassment?",
        "Can I appeal if I disagree with a disciplinary decision?",
        "Who investigates a workplace bullying complaint?",
        "What happens if my grievance is not resolved?",
        "Can I directly approach the director if my manager is involved?",
        "How long are complaint records retained?",
    ]

    successful = 0
    failed = 0
    total_time = 0

    for index, query in enumerate(test_queries, start=1):

        print("\n" + "=" * 75)
        print(f"QUERY {index}")
        print("=" * 75)

        print(f"\nOriginal: {query}")

        start = perf_counter()
        result = expander.expand(query)
        duration = perf_counter() - start

        total_time += duration

        print("\nExpanded:")

        for expanded in result["expanded_queries"]:
            print(f"- {expanded}")

        print(f"\nStatus: {result['expansion_status']}")
        print(f"Fallback: {result['fallback_used']}")
        print(f"Latency: {duration:.2f} seconds")

        if result["expansion_status"] == "success":
            successful += 1
        else:
            failed += 1

    print("\n" + "=" * 75)
    print("BATCH SUMMARY")
    print("=" * 75)

    print(f"Total queries: {len(test_queries)}")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")
    print(f"Average latency: {total_time / len(test_queries):.2f} seconds")
    print(f"Total latency: {total_time:.2f} seconds")


if __name__ == "__main__":
    main()
