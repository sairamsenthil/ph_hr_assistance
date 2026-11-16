
import json
from pathlib import Path

from tokenizers import Tokenizer

from src.hr_assistant.retrieval.dense.dense_retriever import (
    DenseRetriever,
)
from src.hr_assistant.retrieval.pipeline.retrieval_pipeline import (
    HRRetrievalPipeline,
)
from src.hr_assistant.context.context_builder import (
    ContextBuilder,
)


# --------------------------------------------------
# 1. PROJECT PATHS
# --------------------------------------------------

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


# --------------------------------------------------
# 2. LOAD PARENT-CHILD DATA
# --------------------------------------------------

records = []

with open(CHUNKS_FILE, "r", encoding="utf-8") as file:
    for line in file:
        if line.strip():
            records.append(json.loads(line))

children = [
    record
    for record in records
    if record.get("chunking_strategy") == "child"
]

parents = {
    record["chunk_id"]: record
    for record in records
    if record.get("chunking_strategy") == "parent"
}

print("--- DATA LOADED ---")
print(f"Total records: {len(records)}")
print(f"Parent chunks: {len(parents)}")
print(f"Child chunks: {len(children)}")


# --------------------------------------------------
# 3. INITIALIZE RETRIEVAL PIPELINE
# --------------------------------------------------

dense_retriever = DenseRetriever(
    persist_directory=str(VECTOR_DB_DIR)
)

retrieval_pipeline = HRRetrievalPipeline(
    dense_retriever=dense_retriever,
    children=children,
    parents=parents,
    use_reranking=True,
)


# --------------------------------------------------
# 4. INITIALIZE TOKENIZER
# --------------------------------------------------

tokenizer = Tokenizer.from_pretrained(
    "mixedbread-ai/mxbai-embed-large-v1"
)


# --------------------------------------------------
# 5. INITIALIZE CONTEXT BUILDER
# --------------------------------------------------

context_builder = ContextBuilder(
    tokenizer=tokenizer,
    ordering_strategy="relevance_first",
)


# --------------------------------------------------
# 6. RETRIEVE CONTEXT
# --------------------------------------------------

query = "How can an employee raise a workplace complaint?"

retrieval_output = retrieval_pipeline.search(
    query=query,
    top_k=5,
    candidate_k=10,
)

print("\n--- RETRIEVAL COMPLETED ---")
print(f"Query: {query}")
print(
    f"Retrieved chunks: "
    f"{len(retrieval_output['retrieved_chunks'])}"
)
print(
    f"Parent contexts: "
    f"{len(retrieval_output['parent_contexts'])}"
)


# --------------------------------------------------
# 7. BUILD FINAL CONTEXT
# --------------------------------------------------

context_output = context_builder.build(
    retrieval_output=retrieval_output,
    token_budget=3000,
)


# --------------------------------------------------
# 8. DISPLAY CONTEXT BUILDER RESULTS
# --------------------------------------------------

print("\n--- CONTEXT BUILDER RESULTS ---")

print(f"Context status: {context_output['context_status']}")
print(f"Source count: {context_output['source_count']}")
print(f"Ordering: {context_output['ordering_strategy']}")

print(
    f"Original paragraphs: "
    f"{context_output['original_paragraph_count']}"
)
print(
    f"Unique paragraphs: "
    f"{context_output['unique_paragraph_count']}"
)
print(
    f"Duplicates removed: "
    f"{context_output['duplicates_removed']}"
)

print(f"Token count: {context_output['token_count']}")
print(f"Token budget: {context_output['token_budget']}")
print(f"Remaining tokens: {context_output['remaining_tokens']}")
print(f"Budget status: {context_output['budget_status']}")

print(f"Selected sources: {context_output['selected_count']}")
print(f"Excluded sources: {context_output['excluded_count']}")


# --------------------------------------------------
# 9. DISPLAY SOURCE METADATA
# --------------------------------------------------

print("\n--- SELECTED SOURCES ---")

for index, source in enumerate(
    context_output["sources"],
    start=1,
):
    print(f"\nSource {index}")
    print(f"Policy: {source['policy_title']}")
    print(f"Pages: {source['page_start']}-{source['page_end']}")
    print(f"Source ID: {source['source_id']}")
    print(f"Retrieval rank: {source['retrieval_rank']}")
    print(f"Ranking method: {source['ranking_method']}")


# --------------------------------------------------
# 10. DISPLAY FINAL CONTEXT
# --------------------------------------------------

print("\n--- FINAL LLM-READY CONTEXT ---")
print(context_output["context"])


# --------------------------------------------------
# 11. BASIC VALIDATION
# --------------------------------------------------

print("\n--- PIPELINE VALIDATION ---")

assert context_output["context_status"] == "ready", (
    "Final context is empty"
)

assert context_output["budget_status"] == "within_budget", (
    "Token budget exceeded"
)

assert context_output["token_count"] <= 3000, (
    "Context token count exceeds budget"
)

assert context_output["source_count"] > 0, (
    "No sources selected"
)

print("PASS: Final context is ready")
print("PASS: Token budget respected")
print("PASS: Source metadata available")
print("PASS: At least one source selected")
