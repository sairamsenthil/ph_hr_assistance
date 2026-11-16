
import json
from pathlib import Path

from src.hr_assistant.retrieval.dense import DenseRetriever
from src.hr_assistant.retrieval.hybrid import HybridRetriever


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


def main():

    print("Loading child chunks...")

    children = load_children()

    print("Children loaded:", len(children))

    dense_retriever = DenseRetriever(
        persist_directory=str(VECTOR_DB_DIR)
    )

    hybrid_retriever = HybridRetriever(
        dense_retriever=dense_retriever,
        children=children,
    )

    query = "How can an employee raise a workplace complaint?"

    results = hybrid_retriever.search(
        query=query,
        top_k=5,
        candidate_k=10,
    )

    print("\nHYBRID RETRIEVAL RESULTS")
    print("=" * 75)
    print("Query:", query)

    for rank, result in enumerate(results, start=1):

        chunk = result["chunk"]

        print(f"\nRank: {rank}")
        print("Chunk ID:", result["chunk_id"])
        print("Policy:", chunk["policy_title"])
        print("RRF Score:", round(result["rrf_score"], 5))
        print("BM25 Rank:", result["bm25_rank"])
        print("Dense Rank:", result["dense_rank"])


if __name__ == "__main__":
    main()
