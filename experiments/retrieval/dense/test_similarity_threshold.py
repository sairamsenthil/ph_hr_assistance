
from pathlib import Path

from src.hr_assistant.retrieval.dense import DenseRetriever

from experiments.chunking.parent_child.test_retrieval_evaluation import (
    EVALUATION_DATASET,
)


PROJECT_ROOT = Path(__file__).resolve().parents[3]

VECTOR_DB_DIR = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "vector_db"
    / "dense"
)

TOP_K = 5

THRESHOLDS = [
    None,
    0.65,
    0.70,
    0.75,
    0.80,
]


def evaluate_threshold(retriever, threshold):

    total_results = 0
    total_relevant = 0
    total_queries_with_results = 0
    total_queries_with_relevant = 0
    reciprocal_ranks = []

    print("\n" + "=" * 70)
    print(
        "THRESHOLD:",
        "No threshold" if threshold is None else threshold,
    )
    print("=" * 70)

    for test_case in EVALUATION_DATASET:

        results = retriever.search(
            query=test_case["query"],
            top_k=TOP_K,
            min_similarity=threshold,
        )

        expected_policy = test_case["expected_policy"]

        relevant_ranks = [
            rank
            for rank, item in enumerate(results, start=1)
            if item["metadata"].get("policy_title") == expected_policy
        ]

        relevant_count = len(relevant_ranks)

        total_results += len(results)
        total_relevant += relevant_count

        if results:
            total_queries_with_results += 1

        if relevant_count:
            total_queries_with_relevant += 1
            reciprocal_ranks.append(1 / relevant_ranks[0])
        else:
            reciprocal_ranks.append(0)

        print("\nQuery:", test_case["query"])
        print("Expected:", expected_policy)
        print("Results returned:", len(results))
        print("Relevant results:", relevant_count)

        for rank, item in enumerate(results, start=1):
            print(
                f"  {rank}. {item['metadata'].get('policy_title')} "
                f"| Similarity: {item['similarity']:.4f}"
            )

    query_count = len(EVALUATION_DATASET)

    print("\nTHRESHOLD SUMMARY")
    print("-" * 70)

    print(
        "Average results per query:",
        f"{total_results / query_count:.2f}",
    )

    print(
        "Precision among returned results:",
        f"{total_relevant / total_results:.2f}"
        if total_results else "0.00",
    )

    print(
        "Query coverage:",
        f"{total_queries_with_results / query_count:.2f}",
    )

    print(
        "Policy hit rate:",
        f"{total_queries_with_relevant / query_count:.2f}",
    )

    print(
        "MRR:",
        f"{sum(reciprocal_ranks) / query_count:.2f}",
    )


def main():

    retriever = DenseRetriever(
        persist_directory=str(VECTOR_DB_DIR)
    )

    for threshold in THRESHOLDS:
        evaluate_threshold(retriever, threshold)


if __name__ == "__main__":
    main()
