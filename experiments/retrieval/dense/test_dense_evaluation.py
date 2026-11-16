
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


def evaluate_query(retriever, test_case):

    results = retriever.search(
        test_case["query"],
        top_k=TOP_K,
    )

    expected_policy = test_case["expected_policy"]

    relevant_ranks = [
        rank
        for rank, item in enumerate(results, start=1)
        if item["metadata"].get("policy_title") == expected_policy
    ]

    metrics = {}

    for k in [1, 3, 5]:

        top_k_results = results[:k]

        hits = sum(
            1
            for item in top_k_results
            if item["metadata"].get("policy_title") == expected_policy
        )

        metrics[f"hit@{k}"] = int(hits > 0)
        metrics[f"precision@{k}"] = hits / k

    metrics["reciprocal_rank"] = (
        1 / relevant_ranks[0]
        if relevant_ranks
        else 0
    )

    return results, metrics


def main():

    retriever = DenseRetriever(
        persist_directory=str(VECTOR_DB_DIR)
    )

    print("DENSE RETRIEVAL EVALUATION")
    print("=" * 70)

    overall = {
        "hit@1": [],
        "hit@3": [],
        "hit@5": [],
        "precision@1": [],
        "precision@3": [],
        "precision@5": [],
        "reciprocal_rank": [],
    }

    for test_case in EVALUATION_DATASET:

        results, metrics = evaluate_query(
            retriever,
            test_case,
        )

        print("\n" + "=" * 70)
        print("Query:", test_case["query"])
        print("Expected Policy:", test_case["expected_policy"])

        for rank, item in enumerate(results, start=1):

            print(
                f"{rank}. {item['chunk_id']} | "
                f"{item['metadata'].get('policy_title')} | "
                f"Similarity: {item['similarity']:.4f}"
            )

        print("\nMetrics:")

        for name, value in metrics.items():
            print(f"{name}: {value:.2f}")
            overall[name].append(value)

    print("\n" + "=" * 70)
    print("OVERALL DENSE RETRIEVAL METRICS")
    print("=" * 70)

    for name, values in overall.items():
        print(f"{name}: {sum(values) / len(values):.2f}")


if __name__ == "__main__":
    main()
