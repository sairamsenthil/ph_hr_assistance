from src.hr_assistant.query_understanding import QueryRewriter


def main():

    rewriter = QueryRewriter()

    query = (
        "My manager isn't listening to my complaint. "
        "What can I do?"
    )

    print("=" * 70)
    print("LLM QUERY REWRITING EXPERIMENT")
    print("=" * 70)

    result = rewriter.rewrite(query)

    print("\nOriginal Query:")
    print(result["original_query"])

    print("\nRewritten Query:")
    print(result["rewritten_query"])

    print("\nModel:")
    print(result["model"])

    print("\nStatus:")
    print(result["rewrite_status"])

    print("\nFallback Used:")
    print(result["fallback_used"])

    if result.get("error"):
        print("\nError:")
        print(result["error"])


if __name__ == "__main__":
    main()