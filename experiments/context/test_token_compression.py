
import json
from pathlib import Path

from tokenizers import Tokenizer

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

TOKENIZER_NAME = "mixedbread-ai/mxbai-embed-large-v1"


def load_chunks():

    with open(CHUNKS_FILE, "r", encoding="utf-8") as file:

        return [
            json.loads(line)
            for line in file
            if line.strip()
        ]


def count_tokens(tokenizer, text):

    return len(
        tokenizer.encode(
            text,
            add_special_tokens=False,
        ).ids
    )


def main():

    # 1. Load tokenizer
    tokenizer = Tokenizer.from_pretrained(
        TOKENIZER_NAME
    )

    # 2. Load document chunks
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

    # 3. Initialize retrieval pipeline
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

    retrieval_output = pipeline.search(
        query=query,
        top_k=5,
        candidate_k=10,
    )

    # 4. Initialize compressor
    compressor = ContextCompressor()

    total_original_tokens = 0
    total_compressed_tokens = 0

    print("\n--- TOKEN COMPRESSION EXPERIMENT ---")
    print("Query:", query)

    # 5. Compress each retrieved source
    for source in retrieval_output["parent_contexts"]:

        original_text = source["text"]

        original_tokens = count_tokens(
            tokenizer,
            original_text,
        )

        compressed_source = compressor.compress_source(
            query=query,
            source=source,
        )

        filtered_output = compressor.filter_groups(
            compressed_source=compressed_source,
            min_relevance=0.2,
        )

        compressed_text = "\n\n".join(
            group["text"]
            for group in filtered_output["groups"]
        )

        compressed_tokens = count_tokens(
            tokenizer,
            compressed_text,
        )

        tokens_saved = original_tokens - compressed_tokens

        reduction_percentage = (
            tokens_saved / original_tokens * 100
            if original_tokens else 0
        )

        total_original_tokens += original_tokens
        total_compressed_tokens += compressed_tokens

        print("\n-----------------------------------")
        print("Policy:", source["policy_title"])
        print("Source ID:", source["chunk_id"])

        print("Original tokens:", original_tokens)
        print("Compressed tokens:", compressed_tokens)
        print("Tokens saved:", tokens_saved)

        print(
            f"Token reduction: {reduction_percentage:.2f}%"
        )

    # 6. Overall token compression statistics
    total_tokens_saved = (
        total_original_tokens - total_compressed_tokens
    )

    overall_reduction = (
        total_tokens_saved / total_original_tokens * 100
        if total_original_tokens else 0
    )

    print("\n========== OVERALL TOKEN STATISTICS ==========")

    print("Original tokens:", total_original_tokens)
    print("Compressed tokens:", total_compressed_tokens)
    print("Tokens saved:", total_tokens_saved)

    print(
        f"Overall token reduction: {overall_reduction:.2f}%"
    )


if __name__ == "__main__":
    main()
