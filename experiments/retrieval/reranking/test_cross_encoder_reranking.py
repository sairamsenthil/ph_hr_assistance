
import json
from pathlib import Path

from src.hr_assistant.retrieval.dense import DenseRetriever
from src.hr_assistant.retrieval.hybrid import HybridRetriever
from src.hr_assistant.retrieval.reranking import CrossEncoderReranker

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


def load_chunks():

    chunks = []

    with open(CHUNKS_FILE, "r", encoding="utf-8") as file:
        for line in file:
            if line.strip():
                chunks.append(json.loads(line))

    return chunks


def calculate_metrics(results, expected_policy):

    policies = [
        item["chunk"]["policy_title"]
        for item in results
    ]

    relevant = [
        policy == expected_policy
        for policy in policies
    ]

    hit = int(any(relevant))
    precision = sum(relevant) / len(relevant) if relevant else 0

    reciprocal_rank = 0

    for rank, is_relevant in enumerate(relevant, start=1):
        if is_relevant:
            reciprocal_rank = 1 / rank
            break

    return hit, precision, reciprocal_rank


def main():

    print("Loading Parent-Child chunks...")

    chunks = load_chunks()

    children = [
        chunk for chunk in chunks
        if chunk["chunking_strategy"] == "child"
    ]

    print("Children loaded:", len(children))
    print("Evaluation queries:", len(EVALUATION_DATASET))

    dense_retriever = DenseRetriever(
        persist_directory=str(VECTOR_DB_DIR)
    )

    hybrid_retriever = HybridRetriever(
        dense_retriever=dense_retriever,
        children=children,
    )

    reranker = CrossEncoderReranker()

    methods = {
        "Hybrid": {"hit": [], "precision": [], "mrr": []},
        "Hybrid + Reranking": {
            "hit": [],
            "precision": [],
            "mrr": [],
        },
    }

    for index, test_case in enumerate(EVALUATION_DATASET, start=1):

        query = test_case["query"]
        expected_policy = test_case["expected_policy"]

                # 1. Retrieve Top-10 candidates from Hybrid Retrieval
        hybrid_candidates = hybrid_retriever.search(
            query=query,
            top_k=CANDIDATE_K,
            candidate_k=CANDIDATE_K,
        )

        # 2. Keep original Hybrid Top-5 for baseline comparison
        hybrid_results = hybrid_candidates[:TOP_K]

        # 3. Rerank all 10 candidates and select the best 5
        reranked_results = reranker.rerank(
            query=query,
            candidates=hybrid_candidates,
            top_k=TOP_K,
        )

        hybrid_metrics = calculate_metrics(
            hybrid_results,
            expected_policy,
        )

        reranked_metrics = calculate_metrics(
            reranked_results,
            expected_policy,
        )

        for method, metrics in [
            ("Hybrid", hybrid_metrics),
            ("Hybrid + Reranking", reranked_metrics),
        ]:

            methods[method]["hit"].append(metrics[0])
            methods[method]["precision"].append(metrics[1])
            methods[method]["mrr"].append(metrics[2])

        print("\n" + "=" * 65)
        print(f"Query {index}: {query}")
        print("Expected Policy:", expected_policy)

        print("\nHybrid Top-5:")
        for rank, item in enumerate(hybrid_results, start=1):
            print(
                rank,
                item["chunk"]["policy_title"],
                item["chunk_id"],
            )

        print("\nReranked Top-5:")
        for rank, item in enumerate(reranked_results, start=1):
            print(
                rank,
                item["chunk"]["policy_title"],
                item["chunk_id"],
                "Score:",
                round(item["rerank_score"], 4),
            )

    print("\n" + "=" * 65)
    print("FINAL COMPARISON")

    for method, metrics in methods.items():

        hit = sum(metrics["hit"]) / len(metrics["hit"])
        precision = sum(metrics["precision"]) / len(metrics["precision"])
        mrr = sum(metrics["mrr"]) / len(metrics["mrr"])

        print(f"\n{method}")
        print(f"Hit@5:     {hit:.2f}")
        print(f"Precision@5: {precision:.2f}")
        print(f"MRR:       {mrr:.2f}")


if __name__ == "__main__":
    main()
