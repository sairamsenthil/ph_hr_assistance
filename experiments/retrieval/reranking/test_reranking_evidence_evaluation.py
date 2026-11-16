
import json
from pathlib import Path

from src.hr_assistant.retrieval.dense import DenseRetriever
from src.hr_assistant.retrieval.hybrid import HybridRetriever
from src.hr_assistant.retrieval.reranking import CrossEncoderReranker

from experiments.chunking.parent_child.evidence_dataset import (
    EVIDENCE_DATASET,
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


def evaluate_evidence(results, parents, required_evidence):

    parent_ids = list(dict.fromkeys(
        item["chunk"]["parent_chunk_id"]
        for item in results
    ))

    parent_texts = [
        parents[parent_id]["text"]
        for parent_id in parent_ids
        if parent_id in parents
    ]

    combined_context = "\n".join(parent_texts).lower()

    matched = [
        phrase
        for phrase in required_evidence
        if phrase.lower() in combined_context
    ]

    missing = [
        phrase
        for phrase in required_evidence
        if phrase.lower() not in combined_context
    ]

    return {
        "passed": len(matched) == len(required_evidence),
        "matched": matched,
        "missing": missing,
        "parent_ids": parent_ids,
    }


def main():

    print("Loading Parent-Child chunks...")

    chunks = load_chunks()

    children = [
        chunk for chunk in chunks
        if chunk["chunking_strategy"] == "child"
    ]

    parents = {
        chunk["chunk_id"]: chunk
        for chunk in chunks
        if chunk["chunking_strategy"] == "parent"
    }

    print("Children:", len(children))
    print("Parents:", len(parents))
    print("Evaluation queries:", len(EVIDENCE_DATASET))

    dense_retriever = DenseRetriever(
        persist_directory=str(VECTOR_DB_DIR)
    )

    hybrid_retriever = HybridRetriever(
        dense_retriever=dense_retriever,
        children=children,
    )

    reranker = CrossEncoderReranker()

    methods = {
        "Hybrid": {1: [], 3: [], 5: []},
        "Hybrid + Reranking": {1: [], 3: [], 5: []},
    }

    for index, test_case in enumerate(EVIDENCE_DATASET, start=1):

        query = test_case["query"]
        required_evidence = test_case["required_evidence"]

        hybrid_candidates = hybrid_retriever.search(
            query=query,
            top_k=CANDIDATE_K,
            candidate_k=CANDIDATE_K,
        )

        hybrid_results = hybrid_candidates[:TOP_K]

        reranked_results = reranker.rerank(
            query=query,
            candidates=hybrid_candidates,
            top_k=TOP_K,
        )

        print("\n" + "=" * 70)
        print(f"Query {index}: {query}")

        for method_name, results in [
            ("Hybrid", hybrid_results),
            ("Hybrid + Reranking", reranked_results),
        ]:

            print(f"\n--- {method_name} ---")

            for k in [1, 3, 5]:

                evaluation = evaluate_evidence(
                    results[:k],
                    parents,
                    required_evidence,
                )

                methods[method_name][k].append(
                    int(evaluation["passed"])
                )

                print(f"\nEvidence Hit@{k}: {evaluation['passed']}")
                print("Parent IDs:", evaluation["parent_ids"])
                print("Matched:", evaluation["matched"])
                print("Missing:", evaluation["missing"])

    print("\n" + "=" * 70)
    print("FINAL EVIDENCE EVALUATION")

    for method_name, metrics in methods.items():

        print(f"\n{method_name}")

        for k in [1, 3, 5]:

            hit_rate = sum(metrics[k]) / len(metrics[k])

            print(f"Evidence Hit@{k}: {hit_rate:.2f}")


if __name__ == "__main__":
    main()
