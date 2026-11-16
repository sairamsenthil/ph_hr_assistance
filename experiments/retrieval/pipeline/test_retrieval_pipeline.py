
import json
from pathlib import Path

from src.hr_assistant.retrieval.dense import DenseRetriever
from src.hr_assistant.retrieval.pipeline.retrieval_pipeline import (
    HRRetrievalPipeline,
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


def load_chunks():

    chunks = []

    with open(CHUNKS_FILE, "r", encoding="utf-8") as file:
        for line in file:
            if line.strip():
                chunks.append(json.loads(line))

    return chunks


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

    dense_retriever = DenseRetriever(
        persist_directory=str(VECTOR_DB_DIR)
    )

    query = "How can an employee raise a workplace complaint?"

    # Mode 1: Hybrid only
    hybrid_pipeline = HRRetrievalPipeline(
        dense_retriever=dense_retriever,
        children=children,
        parents=parents,
        use_reranking=False,
    )

    # Mode 2: Hybrid + Reranking
    reranked_pipeline = HRRetrievalPipeline(
        dense_retriever=dense_retriever,
        children=children,
        parents=parents,
        use_reranking=True,
    )

    for name, pipeline in [
        ("HYBRID ONLY", hybrid_pipeline),
        ("HYBRID + RERANKING", reranked_pipeline),
    ]:

        output = pipeline.search(
            query=query,
            top_k=5,
            candidate_k=10,
        )

        print("\n" + "=" * 70)
        print(name)

        print("\nQuery:", output["query"])
        print("Reranking:", output["reranking_enabled"])
        print("Retrieved chunks:", output["retrieval_count"])
        print("Unique parent contexts:", output["parent_context_count"])

        print("\nRETRIEVED CHILD CHUNKS")

        for rank, item in enumerate(
            output["retrieved_chunks"],
            start=1,
        ):

            chunk = item["chunk"]

            print(
                rank,
                chunk["policy_title"],
                chunk["chunk_id"],
                "Parent:",
                chunk["parent_chunk_id"],
            )

            if "rerank_score" in item:
                print("Rerank score:", round(item["rerank_score"], 4))

                print("\nPARENT CONTEXTS")

        for parent in output["parent_contexts"]:

            print(
                parent["chunk_id"],
                "|",
                parent["policy_title"],
                "| Pages:",
                parent["page_start"],
                "-",
                parent["page_end"],
            )

        print("\n========== PARENT RANKING ==========")

        for parent in output["parent_contexts"]:

            print({
                "chunk_id": parent["chunk_id"],
                "policy_title": parent["policy_title"],
                "retrieval_rank": parent["retrieval_rank"],
                "rerank_score": parent["rerank_score"],
                "rrf_score": parent["rrf_score"],
                "ranking_method": parent["ranking_method"],
            })
             


if __name__ == "__main__":
    main()
