
import json
from pathlib import Path

from src.hr_assistant.retrieval.dense import DenseRetriever
from src.hr_assistant.retrieval.sparse import retrieve_children_bm25
from src.hr_assistant.retrieval.hybrid import HybridRetriever

from experiments.chunking.parent_child.test_retrieval_evaluation import (
    EVALUATION_DATASET,
)


PROJECT_ROOT = Path(__file__).resolve().parents[3]

CHUNKS_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "chunks"
    / "parent_child"
    / "parent-child.jsonl"
)

VECTOR_DB_DIR = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "vector_db"
    / "dense"
)

TOP_K = 5
CANDIDATE_K = 10


def load_children():

    with open(CHUNKS_FILE, "r", encoding="utf-8") as file:
        chunks = [
            json.loads(line)
            for line in file
            if line.strip()
        ]

    return [
        chunk for chunk in chunks
        if chunk["chunking_strategy"] == "child"
    ]


def calculate_metrics(retrieved, expected_policy, method):

    relevant_ranks = []

    for rank, item in enumerate(retrieved, start=1):

        if method == "dense":
            policy_title = item["metadata"].get("policy_title")

        elif method == "hybrid":
            policy_title = item["chunk"]["policy_title"]

        else:
            policy_title = item["chunk"]["policy_title"]

        if policy_title == expected_policy:
            relevant_ranks.append(rank)

    hit = int(bool(relevant_ranks))
    precision = len(relevant_ranks) / TOP_K

    reciprocal_rank = (
        1 / relevant_ranks[0]
        if relevant_ranks
        else 0
    )

    return {
        "hit": hit,
        "precision": precision,
        "mrr": reciprocal_rank,
    }


def main():

    print("Loading Parent-Child chunks...")

    children = load_children()

    print("Children loaded:", len(children))
    print("Evaluation queries:", len(EVALUATION_DATASET))

    dense_retriever = DenseRetriever(
        persist_directory=str(VECTOR_DB_DIR)
    )

    hybrid_retriever = HybridRetriever(
        dense_retriever=dense_retriever,
        children=children,
    )

    methods = {
        "BM25": [],
        "Dense": [],
        "Hybrid": [],
    }

    for test_case in EVALUATION_DATASET:

        query = test_case["query"]
        expected_policy = test_case["expected_policy"]

        # BM25 retrieval
        bm25_results = retrieve_children_bm25(
            query,
            children,
            top_k=TOP_K,
        )

        # Dense retrieval
        dense_results = dense_retriever.search(
            query=query,
            top_k=TOP_K,
        )

        # Hybrid retrieval
        hybrid_results = hybrid_retriever.search(
            query=query,
            top_k=TOP_K,
            candidate_k=CANDIDATE_K,
        )

        result_sets = {
            "BM25": bm25_results,
            "Dense": dense_results,
            "Hybrid": hybrid_results,
        }

        print("\n" + "=" * 75)
        print("Query:", query)
        print("Expected Policy:", expected_policy)

        for method, retrieved in result_sets.items():

            metrics = calculate_metrics(
                retrieved,
                expected_policy,
                method.lower(),
            )

            methods[method].append(metrics)

            print(
                f"\n{method}: "
                f"Hit@5={metrics['hit']} | "
                f"Precision@5={metrics['precision']:.2f} | "
                f"MRR={metrics['mrr']:.2f}"
            )

    print("\n" + "=" * 75)
    print("FINAL COMPARATIVE EVALUATION")
    print("=" * 75)

    for method, results in methods.items():

        total = len(results)

        hit = sum(r["hit"] for r in results) / total
        precision = sum(r["precision"] for r in results) / total
        mrr = sum(r["mrr"] for r in results) / total

        print(f"\n{method}")
        print(f"Hit@5:       {hit:.2f}")
        print(f"Precision@5: {precision:.2f}")
        print(f"MRR:         {mrr:.2f}")


if __name__ == "__main__":
    main()
