
import json
from pathlib import Path

from src.hr_assistant.retrieval.dense import DenseRetriever
from src.hr_assistant.retrieval.pipeline.retrieval_pipeline import (
    HRRetrievalPipeline,
)
from src.hr_assistant.context.context_compressor import (
    ContextCompressor,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]

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


def load_chunks():

    with open(CHUNKS_FILE, "r", encoding="utf-8") as file:

        return [
            json.loads(line)
            for line in file
            if line.strip()
        ]


def main():

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

    # 1. Initialize retrieval pipeline
    dense_retriever = DenseRetriever(
        persist_directory=str(VECTOR_DB_DIR)
    )

    pipeline = HRRetrievalPipeline(
        dense_retriever=dense_retriever,
        children=children,
        parents=parents,
        use_reranking=True,
    )

    query = "How can an employee raise a workplace complaint?"

    # 2. Retrieve parent contexts
    retrieval_output = pipeline.search(
        query=query,
        top_k=5,
        candidate_k=10,
    )

    # 3. Initialize context compressor
    compressor = ContextCompressor()

    total_original_paragraphs = 0
    total_retained_paragraphs = 0

    total_original_groups = 0
    total_retained_groups = 0

    print("\n--- GROUP-LEVEL CONTEXT COMPRESSION ---")
    print("Query:", query)

    # 4. Compress each retrieved source
    for source in retrieval_output["parent_contexts"]:

        compressed_source = compressor.compress_source(
            query=query,
            source=source,
        )

        filtered_output = compressor.filter_groups(
            compressed_source=compressed_source,
            min_relevance=0.2,
        )

        total_original_paragraphs += (
            filtered_output["original_paragraph_count"]
        )

        total_retained_paragraphs += (
            filtered_output["retained_paragraph_count"]
        )

        total_original_groups += (
            filtered_output["original_group_count"]
        )

        total_retained_groups += (
            filtered_output["retained_group_count"]
        )

        print("\n-----------------------------------")

        print("Policy:", filtered_output["policy_title"])

        print(
            "Pages:",
            filtered_output["page_start"],
            "-",
            filtered_output["page_end"],
        )

        print("Source ID:", filtered_output["source_id"])

        print(
            "Original paragraphs:",
            filtered_output["original_paragraph_count"],
        )

        print(
            "Original groups:",
            filtered_output["original_group_count"],
        )

        print(
            "Retained groups:",
            filtered_output["retained_group_count"],
        )

        print(
            "Removed groups:",
            filtered_output["removed_group_count"],
        )

        print("\n--- RETAINED EVIDENCE ---")

        for group in filtered_output["groups"]:

            print(
                f"\nGroup {group['group_index']}"
                f" | Score: {group['relevance_score']:.2f}"
            )

            print(
                "Paragraph indexes:",
                group["paragraph_indexes"],
            )

            print(group["text"])

        # 5. Identify rejected groups
        retained_group_indexes = {
            group["group_index"]
            for group in filtered_output["groups"]
        }

        print("\n--- REJECTED EVIDENCE ---")

        for group in compressed_source["groups"]:

            if group["group_index"] not in retained_group_indexes:

                print(
                    f"\nGroup {group['group_index']}"
                    f" | Score: {group['relevance_score']:.2f}"
                )

                print(group["text"])

    # 6. Overall statistics
    print("\n========== OVERALL STATISTICS ==========")

    print(
        "Original paragraphs:",
        total_original_paragraphs,
    )

    print(
        "Retained paragraphs:",
        total_retained_paragraphs,
    )

    print(
        "Removed paragraphs:",
        total_original_paragraphs - total_retained_paragraphs,
    )

    print(
        "Original groups:",
        total_original_groups,
    )

    print(
        "Retained groups:",
        total_retained_groups,
    )

    print(
        "Removed groups:",
        total_original_groups - total_retained_groups,
    )

    paragraph_reduction = (
        (
            total_original_paragraphs
            - total_retained_paragraphs
        )
        / total_original_paragraphs
        * 100
        if total_original_paragraphs else 0
    )

    group_reduction = (
        (
            total_original_groups
            - total_retained_groups
        )
        / total_original_groups
        * 100
        if total_original_groups else 0
    )

    print(
        f"Paragraph reduction: {paragraph_reduction:.2f}%"
    )

    print(
        f"Group reduction: {group_reduction:.2f}%"
    )


if __name__ == "__main__":
    main()
