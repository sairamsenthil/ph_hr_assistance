
import json
from pathlib import Path
from time import perf_counter

from src.hr_assistant.retrieval.dense import DenseRetriever
from src.hr_assistant.retrieval.hybrid import HybridRetriever
from src.hr_assistant.retrieval.reranking import CrossEncoderReranker
from src.hr_assistant.query_understanding import QueryExpander

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
RRF_K = 60


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


def fuse_query_results(ranked_lists, top_k):

    scores = {}
    chunk_lookup = {}

    for ranked_list in ranked_lists:

        for rank, item in enumerate(ranked_list, start=1):

            chunk_id = item["chunk_id"]

            chunk_lookup[chunk_id] = item

            scores[chunk_id] = (
                scores.get(chunk_id, 0.0)
                + 1.0 / (RRF_K + rank)
            )

    ranked_ids = sorted(
        scores,
        key=scores.get,
        reverse=True,
    )

    fused_results = []

    for chunk_id in ranked_ids[:top_k]:

        result = chunk_lookup[chunk_id].copy()

        result["multi_query_rrf_score"] = scores[chunk_id]

        fused_results.append(result)

    return fused_results


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

    expander = QueryExpander(max_queries=3)

    method_results = {
        "Hybrid": {1: [], 3: [], 5: []},
        "Hybrid + Reranking": {1: [], 3: [], 5: []},
        "Multi-query + Reranking": {1: [], 3: [], 5: []},
    }

    total_expansion_time = 0
    total_retrieval_time = 0
    total_reranking_time = 0

    for index, test_case in enumerate(EVIDENCE_DATASET, start=1):

        query = test_case["query"]
        required_evidence = test_case["required_evidence"]

        print("\n" + "=" * 75)
        print(f"QUERY {index}: {query}")
        print("=" * 75)

        # --------------------------------------------------
        # 1. Baseline hybrid retrieval
        # --------------------------------------------------

        retrieval_start = perf_counter()

        hybrid_candidates = hybrid_retriever.search(
            query=query,
            top_k=CANDIDATE_K,
            candidate_k=CANDIDATE_K,
        )

        total_retrieval_time += perf_counter() - retrieval_start

        hybrid_results = hybrid_candidates[:TOP_K]

        # --------------------------------------------------
        # 2. Baseline reranking
        # --------------------------------------------------

        reranking_start = perf_counter()

        baseline_reranked = reranker.rerank(
            query=query,
            candidates=hybrid_candidates,
            top_k=TOP_K,
        )

        total_reranking_time += perf_counter() - reranking_start

        # --------------------------------------------------
        # 3. Query expansion
        # --------------------------------------------------

        expansion_start = perf_counter()

        expansion_result = expander.expand(query)

        total_expansion_time += perf_counter() - expansion_start

        search_queries = expansion_result["search_queries"]

        print("\nExpanded search queries:")

        for search_query in search_queries:
            print("-", search_query)

        print("Expansion status:", expansion_result["expansion_status"])

        # --------------------------------------------------
        # 4. Retrieve candidates for each query
        # --------------------------------------------------

        query_ranked_lists = []

        multi_retrieval_start = perf_counter()

        for search_query in search_queries:

            query_results = hybrid_retriever.search(
                query=search_query,
                top_k=CANDIDATE_K,
                candidate_k=CANDIDATE_K,
            )

            query_ranked_lists.append(query_results)

        total_retrieval_time += perf_counter() - multi_retrieval_start

        # --------------------------------------------------
        # 5. Fuse and deduplicate query results
        # --------------------------------------------------

        fused_candidates = fuse_query_results(
            ranked_lists=query_ranked_lists,
            top_k=CANDIDATE_K * len(search_queries),
        )

        print("\nMulti-query candidates:", len(fused_candidates))

        # --------------------------------------------------
        # 6. Rerank using the ORIGINAL query
        # --------------------------------------------------

        multi_reranking_start = perf_counter()

        multi_query_reranked = reranker.rerank(
            query=query,
            candidates=fused_candidates,
            top_k=TOP_K,
        )

        total_reranking_time += (
            perf_counter() - multi_reranking_start
        )

        # --------------------------------------------------
        # 7. Evaluate all methods
        # --------------------------------------------------

        comparisons = [
            ("Hybrid", hybrid_results),
            ("Hybrid + Reranking", baseline_reranked),
            ("Multi-query + Reranking", multi_query_reranked),
        ]

        for method_name, results in comparisons:

            print(f"\n--- {method_name} ---")

            for k in [1, 3, 5]:

                evaluation = evaluate_evidence(
                    results[:k],
                    parents,
                    required_evidence,
                )

                method_results[method_name][k].append(
                    int(evaluation["passed"])
                )

                print(f"\nEvidence Hit@{k}: {evaluation['passed']}")
                print("Parent IDs:", evaluation["parent_ids"])
                print("Matched:", evaluation["matched"])
                print("Missing:", evaluation["missing"])

    # ------------------------------------------------------
    # 8. Final evaluation summary
    # ------------------------------------------------------

    print("\n" + "=" * 75)
    print("FINAL MULTI-QUERY EVIDENCE EVALUATION")
    print("=" * 75)

    for method_name, metrics in method_results.items():

        print(f"\n{method_name}")

        for k in [1, 3, 5]:

            hit_rate = sum(metrics[k]) / len(metrics[k])

            print(f"Evidence Hit@{k}: {hit_rate:.2f}")

    query_count = len(EVIDENCE_DATASET)

    print("\n" + "=" * 75)
    print("LATENCY SUMMARY")
    print("=" * 75)

    print(f"Queries: {query_count}")
    print(
        f"Average expansion latency: "
        f"{total_expansion_time / query_count:.2f} seconds"
    )
    print(
        f"Average retrieval latency: "
        f"{total_retrieval_time / query_count:.2f} seconds"
    )
    print(
        f"Average reranking latency: "
        f"{total_reranking_time / (query_count * 2):.2f} seconds"
    )


if __name__ == "__main__":
    main()
