
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


def main():

    retriever = DenseRetriever(
        persist_directory=str(VECTOR_DB_DIR)
    )

    query = "How can an employee raise a workplace complaint?"

    print("METADATA FILTERING EXPERIMENT")
    print("=" * 70)
    print("Query:", query)

    # Search across all policies
    normal_results = retriever.search(
        query=query,
        top_k=5,
    )

    print("\nWITHOUT METADATA FILTER")
    print("-" * 70)

    for item in normal_results:
        print(
            item["metadata"].get("policy_title"),
            "| Similarity:",
            round(item["similarity"], 4),
        )

    # Search only inside Grievance Procedure
    filtered_results = retriever.search(
        query=query,
        top_k=5,
        where={
            "policy_title": "Grievance Procedure"
        },
    )

    print("\nWITH METADATA FILTER")
    print("-" * 70)

    for item in filtered_results:
        print(
            item["metadata"].get("policy_title"),
            "| Similarity:",
            round(item["similarity"], 4),
        )

    print("\nRESULT COUNTS")
    print("Without filter:", len(normal_results))
    print("With filter:", len(filtered_results))


if __name__ == "__main__":
    main()
