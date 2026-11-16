
import json
from pathlib import Path

from src.hr_assistant.retrieval.dense import DenseRetriever

from experiments.chunking.parent_child.evidence_dataset import (
    EVIDENCE_DATASET,
)


PROJECT_ROOT = Path(__file__).resolve().parents[3]

VECTOR_DB_DIR = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "vector_db"
    / "dense"
)

CHUNKS_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "chunks"
    / "parent_child"
    / "parent-child.jsonl"
)

TOP_K = 5


def load_parent_chunks():

    parents = {}

    with open(CHUNKS_FILE, "r", encoding="utf-8") as file:

        for line in file:

            chunk = json.loads(line)

            if chunk["chunking_strategy"] == "parent":
                parents[chunk["chunk_id"]] = chunk

    return parents


def evaluate_evidence(retrieved_children, parents, required_evidence):

    parent_ids = list(dict.fromkeys(
        child["metadata"]["parent_chunk_id"]
        for child in retrieved_children
    ))

    parent_texts = [
        parents[parent_id]["text"]
        for parent_id in parent_ids
        if parent_id in parents
    ]

    combined_context = "\n".join(parent_texts).lower()

    matched_evidence = [
        phrase
        for phrase in required_evidence
        if phrase.lower() in combined_context
    ]

    return {
        "matched": matched_evidence,
        "missing": [
            phrase
            for phrase in required_evidence
            if phrase not in matched_evidence
        ],
        "passed": len(matched_evidence) == len(required_evidence),
    }


def main():

    retriever = DenseRetriever(
        persist_directory=str(VECTOR_DB_DIR)
    )

    parents = load_parent_chunks()

    evidence_hits = {
        1: [],
        3: [],
        5: [],
    }

    print("DENSE RETRIEVAL - EVIDENCE EVALUATION")
    print("=" * 70)

    for test_case in EVIDENCE_DATASET:

        results = retriever.search(
            query=test_case["query"],
            top_k=TOP_K,
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

            print(f"\nEvidence evaluation at Top-{k}")
            print("Matched:", evaluation["matched"])
            print("Missing:", evaluation["missing"])
            print("Evidence complete:", evaluation["passed"])

    print("\n" + "=" * 70)
    print("OVERALL EVIDENCE RETRIEVAL METRICS")
    print("=" * 70)

    for k, values in evidence_hits.items():

        score = sum(values) / len(values)

        print(f"Evidence Hit@{k}: {score:.2f}")


if __name__ == "__main__":
    main()
