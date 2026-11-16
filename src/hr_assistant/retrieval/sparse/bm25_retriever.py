
import re
from collections import Counter
from math import log


def retrieve_children_bm25(query, children, top_k=5):

    k1 = 1.5
    b = 0.75

    query_terms = set(
        re.findall(r"\b[a-z0-9]+\b", query.lower())
    )

    corpus = [
        re.findall(r"\b[a-z0-9]+\b", child["text"].lower())
        for child in children
    ]

    total_documents = len(corpus)

    if total_documents == 0:
        return []

    document_frequency = Counter()

    for tokens in corpus:
        document_frequency.update(set(tokens))

    average_length = (
        sum(len(tokens) for tokens in corpus) / total_documents
    )

    results = []

    for child, tokens in zip(children, corpus):

        term_frequency = Counter(tokens)
        document_length = len(tokens)
        score = 0

        for term in query_terms:

            frequency = term_frequency[term]

            if frequency == 0:
                continue

            df = document_frequency[term]

            idf = log(
                1 + (
                    total_documents - df + 0.5
                ) / (df + 0.5)
            )

            denominator = (
                frequency
                + k1 * (
                    1 - b
                    + b * document_length / average_length
                )
            )

            score += (
                idf
                * frequency
                * (k1 + 1)
                / denominator
            )

        if score > 0:
            results.append({
                "chunk": child,
                "score": score,
            })

    return sorted(
        results,
        key=lambda item: item["score"],
        reverse=True
    )[:top_k]
