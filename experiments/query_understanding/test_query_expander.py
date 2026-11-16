from src.hr_assistant.query_understanding import QueryExpander


def main():

    expander = QueryExpander(max_queries=3)

    query = "How can I complain at work?"

    print("=" * 75)
    print("LLM QUERY EXPANSION EXPERIMENT")
    print("=" * 75)

    result = expander.expand(query)

    print("\nOriginal Query:")
    print(result["original_query"])

    print("\nExpanded Queries:")

    for index, expanded_query in enumerate(
        result["expanded_queries"],
        start=1,
    ):
        print(f"{index}. {expanded_query}")

    print("\nComplete Search Query Set:")

    for index, search_query in enumerate(
        result["search_queries"],
        start=1,
    ):
        print(f"{index}. {search_query}")

    print("\nModel:")
    print(result["model"])

    print("\nStatus:")
    print(result["expansion_status"])

    print("\nFallback Used:")
    print(result["fallback_used"])

    if result.get("error"):
        print("\nError:")
        print(result["error"])


if __name__ == "__main__":
    main()