from experiments.chunking.parent_child.test_bm25_query_expansion import (
    expand_query,
)

from experiments.chunking.parent_child.test_retrieval_evaluation import (
    CHUNKS_FILE,
    load_chunks,
    retrieve_children_bm25,
)

from experiments.chunking.parent_child.evidence_dataset import (
    EVIDENCE_DATASET,
)


def contains_evidence(text, required_evidence):
    normalized_text = " ".join(text.lower().split())

    return all(
        " ".join(phrase.lower().split()) in normalized_text
        for phrase in required_evidence
    )


def evaluate_evidence(test_case, children, parents):
    expanded_query = expand_query(test_case["query"])

    retrieved = retrieve_children_bm25(
      expanded_query,
      children,
      top_k=5,
    )

    evidence_results = []

    for item in retrieved:
        child = item["chunk"]

        parent = parents.get(child["parent_chunk_id"])

        matched = False

        if parent:
            matched = contains_evidence(
                parent["text"],
                test_case["required_evidence"],
        )
         

        evidence_results.append({
            "chunk": child,
            "score": item["score"],
            "evidence_found": matched,
        })

    metrics = {}

    for k in [1, 3, 5]:

        top_k_results = evidence_results[:k]

        metrics[f"evidence_hit@{k}"] = int(
            any(item["evidence_found"] for item in top_k_results)
        )

    return {
        "query": test_case["query"],
        "expected_policy": test_case["expected_policy"],
        "results": evidence_results,
        "metrics": metrics,
    }


def main():

    chunks = load_chunks(CHUNKS_FILE)

    parents = {
    chunk["chunk_id"]: chunk
    for chunk in chunks
    if chunk["chunking_strategy"] == "parent"
}

    children = [
        chunk for chunk in chunks
        if chunk["chunking_strategy"] == "child"
    ]

    all_results = []

    print("ANSWER EVIDENCE EVALUATION")
    print("=" * 70)

    for test_case in EVIDENCE_DATASET:

        result = evaluate_evidence(test_case, children, parents)
        all_results.append(result)

        print("\n" + "=" * 70)
        print("Query:", result["query"])
        print("Expected Policy:", result["expected_policy"])

        for rank, item in enumerate(result["results"], start=1):

            chunk = item["chunk"]

            print(
                f"{rank}. {chunk['chunk_id']} | "
                f"{chunk['policy_title']} | "
                f"Score: {item['score']:.2f} | "
                f"Evidence: {item['evidence_found']}"
            )

        print("\nEvidence Metrics:")

        for metric, value in result["metrics"].items():
            print(f"{metric}: {value}")

    total = len(all_results)

    print("\n" + "=" * 70)
    print("OVERALL EVIDENCE RETRIEVAL METRICS")

    for k in [1, 3, 5]:

        metric = f"evidence_hit@{k}"

        average = sum(
            result["metrics"][metric]
            for result in all_results
        ) / total

        print(f"{metric}: {average:.2f}")


if __name__ == "__main__":
    main()
