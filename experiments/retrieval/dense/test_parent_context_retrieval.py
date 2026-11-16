
import json
from pathlib import Path

from src.hr_assistant.retrieval.dense import DenseRetriever


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


def load_parent_chunks():

    parents = {}

    with open(CHUNKS_FILE, "r", encoding="utf-8") as file:

        for line in file:

            chunk = json.loads(line)

            if chunk["chunking_strategy"] == "parent":
                parents[chunk["chunk_id"]] = chunk

    return parents


def main():

    retriever = DenseRetriever(
        persist_directory=str(VECTOR_DB_DIR)
    )

    parents = load_parent_chunks()

    query = "How can an employee raise a workplace complaint?"

    child_results = retriever.search(
        query=query,
        top_k=5,
    )

    print("PARENT-CONTEXT RETRIEVAL")
    print("=" * 70)
    print("Query:", query)

    retrieved_parent_ids = set()

    for rank, child in enumerate(child_results, start=1):

        parent_id = child["metadata"]["parent_chunk_id"]

        print("\n" + "-" * 70)
        print(f"CHILD RESULT {rank}")
        print("Child ID:", child["chunk_id"])
        print("Policy:", child["metadata"].get("policy_title"))
        print("Similarity:", round(child["similarity"], 4))
        print("Parent ID:", parent_id)

        retrieved_parent_ids.add(parent_id)

    print("\n" + "=" * 70)
    print("RETRIEVED PARENT CONTEXTS")
    print("=" * 70)

    for parent_id in retrieved_parent_ids:

        parent = parents.get(parent_id)

        if parent is None:
            print("Parent not found:", parent_id)
            continue

        print("\nParent ID:", parent_id)
        print("Policy:", parent["policy_title"])
        print("Pages:", parent["page_start"], "-", parent["page_end"])
        print("Token count:", parent["token_count"])
        print("\nParent Text:\n")
        print(parent["text"])


if __name__ == "__main__":
    main()
