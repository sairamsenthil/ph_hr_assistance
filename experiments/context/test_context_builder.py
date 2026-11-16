
import json
from pathlib import Path

from src.hr_assistant.retrieval.dense import DenseRetriever
from src.hr_assistant.retrieval.pipeline.retrieval_pipeline import (
    HRRetrievalPipeline,
)
from src.hr_assistant.context.context_builder import ContextBuilder
from tokenizers import Tokenizer

TOKENIZER_NAME = "mixedbread-ai/mxbai-embed-large-v1"

tokenizer = Tokenizer.from_pretrained(TOKENIZER_NAME)

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

    # Run retrieval only once
    retrieval_output = pipeline.search(
        query=query,
        top_k=5,
        candidate_k=10,
    )

    # Compare three context ordering strategies
    strategies = [
        "relevance_first",
        "relevance_last",
        "lost_middle",
    ]

    for strategy in strategies:

        context_builder = ContextBuilder(
            tokenizer=tokenizer,
            ordering_strategy=strategy,
        )

        context_output = context_builder.build(
            retrieval_output=retrieval_output,
            token_budget=3000,
        )

        print(f"\n========== {strategy.upper()} ==========")

        print("\nQuery:", context_output["query"])
        print("Context status:", context_output["context_status"])

        print("\nSource ordering:")

        for source in context_output["sources"]:
            print(
                "Rank:", source["retrieval_rank"],
                "| Policy:", source["policy_title"],
                "| Pages:", source["page_start"], "-", source["page_end"],
            )

        print("\nParagraph statistics:")
        print("Original:", context_output["original_paragraph_count"])
        print("Unique:", context_output["unique_paragraph_count"])
        print("Duplicates removed:", context_output["duplicates_removed"])

        print("\nToken budget:")
        print("Token count:", context_output["token_count"])
        print("Token budget:", context_output["token_budget"])
        print("Remaining:", context_output["remaining_tokens"])
        print("Selected:", context_output["selected_count"])
        print("Excluded:", context_output["excluded_count"])
        print("Status:", context_output["budget_status"])

        print("\nCombined context:")
        print(context_output["context"])


if __name__ == "__main__":
    main()
