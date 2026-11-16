
import json
from pathlib import Path

from src.hr_assistant.retrieval.dense import DenseRetriever
from src.hr_assistant.retrieval.hybrid import HybridRetriever

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


def load_chunks():

    chunks = []

    with open(CHUNKS_FILE, "r", encoding="utf-8") as file:
        for line in file:
            if line.strip():
                chunks.append(json.loads(line))

    return chunks


def evaluate_evidence(retrieved, parents, required_evidence):

    parent_ids = list(dict.fromkeys(
        result["chunk"]["parent_chunk_id"]
        for result in retrieved
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
        if phrase not in matched
    ]

    return {
        "matched": matched,
        "missing": missing,
        "passed": len(matched) == len(required_evidence),
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

    dense_retriever = DenseRetriever(
        persist_directory=str(VECTOR_DB_DIR)
    )

    hybrid_retriever = HybridRetriever(
        dense_retriever=dense_retriever,
        children=children,
    )

    evidence_hits = {1: [], 3: [], 5: []}

    for test_case in EVIDENCE_DATASET:

        results = hybrid_retriever.search(
            query=test_case["query"],
            top_k=TOP_K,
            candidate_k=10,
        )

        print("\n" + "=" * 70)
        print("Query:", test_case["query"])
        print("Expected Policy:", test_case["expected_policy"])

        for k in [1, 3, 5]:

            evaluation = evaluate_evidence(
                results[:k],
                parents,
                test_case["required_evidence"],
            )

            evidence_hits[k].append(
                int(evaluation["passed"])
            )

            print(f"\nEvidence Evaluation at Top-{k}")
            print("Parent IDs:", evaluation["parent_ids"])
            print("Matched:", evaluation["matched"])
            print("Missing:", evaluation["missing"])
            print("Evidence Complete:", evaluation["passed"])

    print("\n" + "=" * 70)
    print("HYBRID EVIDENCE RETRIEVAL METRICS")

    for k, values in evidence_hits.items():

        score = sum(values) / len(values)

        print(f"Evidence Hit@{k}: {score:.2f}")


if __name__ == "__main__":
    main()
