
import json
import re
from pathlib import Path
from collections import Counter
from math import log
from src.hr_assistant.retrieval.sparse import (
    retrieve_children_bm25,
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

TOP_K = 5
MIN_SCORE = 0.0

EVALUATION_DATASET = [
    {
        "query": "How are internal candidates selected for interview?",
        "expected_policy": "Recruitment and Selection",
    },
    {
        "query": "What should employees do when they cannot attend work?",
        "expected_policy": "Controlling Absence Policy",
    },
    {
        "query": "What steps are followed when disciplinary action is considered?",
        "expected_policy": "Disciplinary Procedure",
    },
    {
        "query": "How can an employee raise a workplace complaint?",
        "expected_policy": "Grievance Procedure",
    },
    {
        "query": "What does the policy say about workplace bullying and harassment?",
        "expected_policy": "Prevention of Bullying and Harassment at Work",
    },
]


def load_chunks(path):
    with open(path, "r", encoding="utf-8") as file:
        return [
            json.loads(line)
            for line in file
            if line.strip()
        ]


def tokenize(text):
    return set(re.findall(r"\b[a-z0-9]+\b", text.lower()))


def calculate_score(query, text):
    query_tokens = tokenize(query)
    text_tokens = tokenize(text)

    if not query_tokens:
        return 0

    matched_tokens = query_tokens.intersection(text_tokens)
    return len(matched_tokens) / len(query_tokens)


def retrieve_children(query, children):
    results = []

    for child in children:
        score = calculate_score(query, child["text"])

        if score >= MIN_SCORE:
            results.append({
                "chunk": child,
                "score": score,
            })

    return sorted(
        results,
        key=lambda item: item["score"],
        reverse=True,
    )[:TOP_K]


# def retrieve_children_bm25(query, children, top_k=5):

#     k1 = 1.5
#     b = 0.75

#     query_terms = set(
#         re.findall(r"\b[a-z0-9]+\b", query.lower())
#     )

#     corpus = [
#         re.findall(r"\b[a-z0-9]+\b", child["text"].lower())
#         for child in children
#     ]

#     total_documents = len(corpus)

#     document_frequency = Counter()

#     for tokens in corpus:
#         document_frequency.update(set(tokens))

#     average_length = (
#         sum(len(tokens) for tokens in corpus) / total_documents
#         if total_documents else 0
#     )

#     results = []

#     for child, tokens in zip(children, corpus):

#         term_frequency = Counter(tokens)
#         document_length = len(tokens)
#         score = 0

#         for term in query_terms:

#             frequency = term_frequency[term]

#             if frequency == 0:
#                 continue

#             df = document_frequency[term]

#             idf = log(
#                 1 + (
#                     total_documents - df + 0.5
#                 ) / (df + 0.5)
#             )

#             denominator = (
#                 frequency
#                 + k1 * (
#                     1 - b
#                     + b * document_length / average_length
#                 )
#             )

#             score += (
#                 idf
#                 * frequency
#                 * (k1 + 1)
#                 / denominator
#             )

#         if score > 0:
#             results.append({
#                 "chunk": child,
#                 "score": score,
#             })

#     return sorted(
#         results,
#         key=lambda item: item["score"],
#         reverse=True
#     )[:top_k]


def evaluate_query(test_case, children):
    retrieved = retrieve_children_bm25(
    test_case["query"],
    children,
    top_k=TOP_K
)
    expected_policy = test_case["expected_policy"]

    relevant_ranks = [
        rank
        for rank, result in enumerate(retrieved, start=1)
        if result["chunk"]["policy_title"] == expected_policy
    ]

    hit_at_k = int(bool(relevant_ranks))
    precision_at_k = len(relevant_ranks) / TOP_K
    reciprocal_rank = (
        1 / relevant_ranks[0]
        if relevant_ranks
        else 0
    )

    return {
        "query": test_case["query"],
        "expected_policy": expected_policy,
        "retrieved": retrieved,
        "hit_at_k": hit_at_k,
        "precision_at_k": precision_at_k,
        "reciprocal_rank": reciprocal_rank,
    }


def main():
    print("Loading Parent-Child chunks...")

    chunks = load_chunks(CHUNKS_FILE)

    children = [
        chunk
        for chunk in chunks
        if chunk["chunking_strategy"] == "child"
    ]

    print(f"Children loaded: {len(children)}")
    print(f"Evaluation queries: {len(EVALUATION_DATASET)}")

    results = []

    for test_case in EVALUATION_DATASET:
        result = evaluate_query(test_case, children)
        results.append(result)

        print("\n" + "=" * 65)
        print(f"Query: {result['query']}")
        print(f"Expected Policy: {result['expected_policy']}")

        print("\nRetrieved Results:")

        if not result["retrieved"]:
            print("No chunks passed the relevance threshold.")

        for rank, item in enumerate(result["retrieved"], start=1):
            chunk = item["chunk"]

            print(
                f"{rank}. {chunk['chunk_id']} | "
                f"Score: {item['score']:.2f} | "
                f"Policy: {chunk['policy_title']}"
            )

        print("\nMetrics:")
        print(f"Hit@{TOP_K}: {result['hit_at_k']}")
        print(f"Precision@{TOP_K}: {result['precision_at_k']:.2f}")
        print(f"Reciprocal Rank: {result['reciprocal_rank']:.2f}")

    total = len(results)

    print("\n" + "=" * 65)
    print("OVERALL RETRIEVAL EVALUATION")

    print(
        f"Hit@{TOP_K}: "
        f"{sum(r['hit_at_k'] for r in results) / total:.2f}"
    )

    print(
        f"Precision@{TOP_K}: "
        f"{sum(r['precision_at_k'] for r in results) / total:.2f}"
    )

    print(
        f"MRR: "
        f"{sum(r['reciprocal_rank'] for r in results) / total:.2f}"
    )


if __name__ == "__main__":
    main()
