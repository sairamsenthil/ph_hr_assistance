
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
from src.hr_assistant.context import (
    ContextSufficiencyEvaluator,
    ContextEvidenceEvaluator,
)

from experiments.chunking.parent_child.evidence_dataset import (
    EVIDENCE_DATASET,
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

TOKEN_BUDGET = 3000


# --------------------------------------------------
# 2. LOAD PARENT-CHILD DATA
# --------------------------------------------------

records = []

with open(CHUNKS_FILE, "r", encoding="utf-8") as file:
    for line in file:
        if line.strip():
            records.append(json.loads(line))

children = [
    record for record in records
    if record.get("chunking_strategy") == "child"
]

parents = {
    record["chunk_id"]: record
    for record in records
    if record.get("chunking_strategy") == "parent"
}

print("--- DATA LOADED ---")
print("Children:", len(children))
print("Parents:", len(parents))
print("Evaluation queries:", len(EVIDENCE_DATASET))


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
# 4. INITIALIZE CONTEXT COMPONENTS
# --------------------------------------------------

tokenizer = Tokenizer.from_pretrained(
    "mixedbread-ai/mxbai-embed-large-v1"
)

context_builder = ContextBuilder(
    tokenizer=tokenizer,
    ordering_strategy="relevance_first",
)

sufficiency_evaluator = ContextSufficiencyEvaluator()
evidence_evaluator = ContextEvidenceEvaluator()


# --------------------------------------------------
# 5. EVALUATION METRICS
# --------------------------------------------------

structural_passes = 0
evidence_complete_count = 0

total_evidence = 0
matched_evidence = 0
missing_evidence = 0


# --------------------------------------------------
# 6. RUN END-TO-END EVALUATION
# --------------------------------------------------

for index, test_case in enumerate(EVIDENCE_DATASET, start=1):

    query = test_case["query"]
    required_evidence = test_case["required_evidence"]

    print("\n" + "=" * 75)
    print(f"QUERY {index}: {query}")
    print("=" * 75)

    # Retrieve relevant contexts
    retrieval_output = retrieval_pipeline.search(
        query=query,
        top_k=5,
        candidate_k=10,
    )

    # Build final context
    context_output = context_builder.build(
        retrieval_output=retrieval_output,
        token_budget=TOKEN_BUDGET,
    )

    # Structural sufficiency
    structural_result = sufficiency_evaluator.evaluate(
        context_output
    )

    # Evidence coverage
    evidence_result = evidence_evaluator.evaluate(
        context=context_output["context"],
        required_evidence=required_evidence,
    )

    if structural_result["answerable"]:
        structural_passes += 1

    if evidence_result["evidence_complete"]:
        evidence_complete_count += 1

    total_evidence += evidence_result["total_evidence"]
    matched_evidence += evidence_result["matched_count"]
    missing_evidence += evidence_result["missing_count"]

    # Display results
    print("\n--- CONTEXT BUILDER ---")
    print("Context status:", context_output["context_status"])
    print("Sources:", context_output["source_count"])
    print("Tokens:", context_output["token_count"])
    print("Budget status:", context_output["budget_status"])

    print("\n--- STRUCTURAL SUFFICIENCY ---")
    print("Answerable:", structural_result["answerable"])
    print("Status:", structural_result["sufficiency_status"])
    print("Issues:", structural_result["issues"])

    print("\n--- EVIDENCE COVERAGE ---")
    print(f"Coverage: {evidence_result['coverage']:.2%}")
    print("Matched:", evidence_result["matched_evidence"])
    print("Missing:", evidence_result["missing_evidence"])
    print("Evidence complete:", evidence_result["evidence_complete"])


# --------------------------------------------------
# 7. FINAL EVALUATION SUMMARY
# --------------------------------------------------

query_count = len(EVIDENCE_DATASET)

overall_coverage = (
    matched_evidence / total_evidence
    if total_evidence
    else 0.0
)

print("\n" + "=" * 75)
print("END-TO-END CONTEXT SUFFICIENCY EVALUATION")
print("=" * 75)

print("Total queries:", query_count)

print(
    f"Structural sufficiency: "
    f"{structural_passes}/{query_count}"
)

print(
    f"Evidence-complete contexts: "
    f"{evidence_complete_count}/{query_count}"
)

print("Total expected evidence:", total_evidence)
print("Matched evidence:", matched_evidence)
print("Missing evidence:", missing_evidence)

print(f"Overall evidence coverage: {overall_coverage:.2%}")
