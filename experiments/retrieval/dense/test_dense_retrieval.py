
import json
from pathlib import Path

from src.hr_assistant.retrieval.dense import DenseRetriever


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


def load_chunks(path):

    with path.open("r", encoding="utf-8") as file:
        return [
            json.loads(line)
            for line in file
            if line.strip()
        ]


def main():

    print("DENSE RETRIEVAL EXPERIMENT")
    print("=" * 70)

    chunks = load_chunks(CHUNKS_FILE)

    children = [
        chunk for chunk in chunks
        if chunk["chunking_strategy"] == "child"
    ]

    print("Total child chunks:", len(children))

    retriever = DenseRetriever(
        persist_directory=str(VECTOR_DB_DIR)
    )

    indexing = retriever.index_chunks(chunks)

    print("\nINDEXING RESULTS")
    print("-" * 70)
    print("Children processed:", indexing["total_children"])
    print("Vectors stored:", indexing["stored_vectors"])

    query = "How are internal candidates selected for interview?"

    print("\nQUERY:", query)

    results = retriever.search(query, top_k=5)

    print("\nDENSE RETRIEVAL RESULTS")
    print("-" * 70)

    for rank, item in enumerate(results, start=1):

        metadata = item["metadata"]

        print(f"\nRank: {rank}")
        print("Chunk ID:", item["chunk_id"])
        print("Policy:", metadata.get("policy_title"))
        print("Parent ID:", metadata.get("parent_chunk_id"))
        print("Cosine distance:", round(item["distance"], 4))
        print("Similarity:", round(item["similarity"], 4))
        print("Text:", item["text"][:300].replace("\n", " "))


if __name__ == "__main__":
    main()
