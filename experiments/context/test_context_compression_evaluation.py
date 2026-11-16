
import json
from pathlib import Path

from src.hr_assistant.retrieval.dense.dense_retriever import (
    DenseRetriever,
)
from src.hr_assistant.retrieval.pipeline.retrieval_pipeline import (
    HRRetrievalPipeline,
)
from src.hr_assistant.context.context_compressor import (
    ContextCompressor,
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
# 4. RETRIEVE CONTEXT
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
# 5. INITIALIZE CONTEXT COMPRESSOR
# --------------------------------------------------

compressor = ContextCompressor()


# --------------------------------------------------
# 6. PREPARE ORIGINAL CONTEXT
# --------------------------------------------------

original_context = "\n\n".join(
    source["text"]
    for source in retrieval_output["parent_contexts"]
)


# --------------------------------------------------
# 7. COMPRESS RETRIEVED CONTEXTS
# --------------------------------------------------

compressed_contexts = []

for source in retrieval_output["parent_contexts"]:

    compression_output = compressor.compress_source(
        query=query,
        source=source,
    )

    filtered_output = compressor.filter_groups(
        compressed_source=compression_output,
        min_relevance=0.2,
    )

    compressed_text = "\n\n".join(
        group["text"]
        for group in filtered_output["groups"]
    )

    compressed_contexts.append(compressed_text)


compressed_context = "\n\n".join(compressed_contexts)


# --------------------------------------------------
# 8. DEFINE REQUIRED EVIDENCE
# --------------------------------------------------

evidence_checks = {
    "Raise grievance with line manager":
        "raise the matter with his line manager",

    "Verbal or written grievance":
        "either verbally or in writing",

    "Formal written grievance":
        "formal written grievance form should be submitted",

    "Manager response timeline":
        "respond within 2 working days",

    "Stage 2 appeal":
        "appeal against the decision",

    "Stage 2 appeal timeline":
        "within ten working days",

    "Stage 3 final appeal":
        "final level of appeal to the Director",

    "Stage 3 appeal timeline":
        "within 20 working days",
}


# --------------------------------------------------
# 9. EVIDENCE PRESERVATION EVALUATION
# --------------------------------------------------

print("\n--- EVIDENCE PRESERVATION EVALUATION ---")

original_found = 0
preserved = 0
lost_during_compression = 0
missing_before_compression = 0

for label, phrase in evidence_checks.items():

    original_match = (
        phrase.casefold() in original_context.casefold()
    )

    compressed_match = (
        phrase.casefold() in compressed_context.casefold()
    )

    if original_match:
        original_found += 1

    if original_match and compressed_match:
        preserved += 1
        status = "PRESERVED"

    elif original_match and not compressed_match:
        lost_during_compression += 1
        status = "LOST DURING COMPRESSION"

    else:
        missing_before_compression += 1
        status = "NOT RETRIEVED"

    print(f"\nEvidence: {label}")
    print(
        f"Original: "
        f"{'FOUND' if original_match else 'MISSING'}"
    )
    print(
        f"Compressed: "
        f"{'FOUND' if compressed_match else 'MISSING'}"
    )
    print(f"Status: {status}")


# --------------------------------------------------
# 10. CALCULATE EVALUATION METRICS
# --------------------------------------------------

total_expected = len(evidence_checks)

original_coverage = (
    original_found / total_expected * 100
    if total_expected else 0
)

evidence_retention = (
    preserved / original_found * 100
    if original_found else 0
)

compression_loss_rate = (
    lost_during_compression / original_found * 100
    if original_found else 0
)


# --------------------------------------------------
# 11. FINAL REPORT
# --------------------------------------------------

print("\n--- EVALUATION SUMMARY ---")

print(f"Total expected evidence: {total_expected}")
print(f"Evidence found before compression: {original_found}")
print(f"Evidence preserved: {preserved}")
print(f"Evidence lost during compression: {lost_during_compression}")
print(f"Evidence not retrieved initially: {missing_before_compression}")

print("\n--- METRICS ---")

print(f"Original evidence coverage: {original_coverage:.2f}%")
print(f"Evidence retention rate: {evidence_retention:.2f}%")
print(f"Compression evidence loss rate: {compression_loss_rate:.2f}%")
