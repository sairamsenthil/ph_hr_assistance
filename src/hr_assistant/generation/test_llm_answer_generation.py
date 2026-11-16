
import json
from pathlib import Path
import sys

import requests
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
from src.hr_assistant.context.context_security import (
    ContextSecurity,
)
from src.hr_assistant.generation.citation_validator import (
    CitationValidator,
)
# from src.hr_assistant.context.context_quality_evaluator import (
#     ContextQualityEvaluator,
# )
from src.hr_assistant.context.context_sufficiency_evaluator import (
    ContextSufficiencyEvaluator,
)

from src.hr_assistant.generation.generation_quality_pipeline import (
    GenerationQualityPipeline,
)
from src.hr_assistant.observability.run_observer import RunObserver


# --------------------------------------------------
# 1. CONFIGURATION
# --------------------------------------------------

MODEL_NAME = "qwen3:8b"
OLLAMA_URL = "http://localhost:11434/api/chat"

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

OBSERVABILITY_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "observability"
    / "pipeline_runs.jsonl"
)

observer = RunObserver(log_file=OBSERVABILITY_FILE)

def handle_uncaught_exception(exc_type, exc_value, exc_traceback):
    try:
        failure_record = observer.fail(exc_value)

        if failure_record is not None:
            print(
                "\n--- FAILED RUN RECORDED ---",
                file=sys.stderr,
            )
            print(
                f"Run ID: {failure_record['run_id']}",
                file=sys.stderr,
            )
            print(
                f"Error: {failure_record['error']}",
                file=sys.stderr,
            )

    except Exception as telemetry_error:
        print(
            f"Could not persist failure telemetry: {telemetry_error}",
            file=sys.stderr,
        )

    sys.__excepthook__(exc_type, exc_value, exc_traceback)


sys.excepthook = handle_uncaught_exception

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
# 4. INITIALIZE CONTEXT BUILDER
# --------------------------------------------------

tokenizer = Tokenizer.from_pretrained(
    "mixedbread-ai/mxbai-embed-large-v1"
)

context_builder = ContextBuilder(
    tokenizer=tokenizer,
    ordering_strategy="relevance_first",
)

context_security = ContextSecurity()

# --------------------------------------------------
# 5. USER QUERY
# --------------------------------------------------

query = "How can an employee raise a workplace complaint?"

REQUIRED_EVIDENCE = [
    "Informal complaints about harassment or bullying can be raised with a line manager or Human Resources.",

    "An employee may attempt informal resolution by speaking to the alleged harasser, verbally or in writing, if they feel able to do so.",

    "If informal resolution is unsuitable, unsuccessful, or the allegation is serious, the employee can raise a formal complaint.",

    "A formal harassment complaint is normally submitted to the employee's line manager, or to a more senior manager if the employee cannot approach their line manager.",

    "An employee with a general employment grievance should initially raise it with their line manager or supervisor, verbally or in writing.",

    "If the grievance concerns the employee's immediate manager, it should be raised with that manager's superior.",

    "Employees have representation rights under the grievance procedure through a Trade Union representative or work colleague.",
]

# --------------------------------------------------
# 6. RETRIEVAL
# --------------------------------------------------

observer.start_stage("retrieval")

retrieval_output = retrieval_pipeline.search(
    query=query,
    top_k=5,
    candidate_k=10,
    user_role="employee",
)

observer.end_stage(
    "retrieval",
    status="success",
   metadata={
    "top_k": 5,
    "candidate_k": 10,
    "reranking_enabled": True,
    "user_role": "employee",
},
)

print("\n--- RETRIEVAL COMPLETED ---")
print(f"Retrieved chunks: {len(retrieval_output['retrieved_chunks'])}")
print(f"Parent contexts: {len(retrieval_output['parent_contexts'])}")


# --------------------------------------------------
# 7. CONTEXT ASSEMBLY
# --------------------------------------------------

observer.start_stage("context_building")

context_output = context_builder.build(
    retrieval_output=retrieval_output,
    token_budget=3000,
)

observer.end_stage(
    "context_building",
    status="success",
    metadata={
        "source_count": context_output["source_count"],
        "token_count": context_output["token_count"],
        "token_budget": context_output["token_budget"],
        "remaining_tokens": context_output["remaining_tokens"],
        "excluded_count": context_output["excluded_count"],
        "context_status": context_output["context_status"],
        "budget_status": context_output["budget_status"],
    },
)

if context_output["context_status"] != "ready":
    raise ValueError("Context assembly produced an empty context.")

if context_output["budget_status"] != "within_budget":
    raise ValueError("Context exceeded the configured token budget.")

context = context_output["context"]

print("\n--- CONTEXT ASSEMBLY COMPLETED ---")
print(f"Sources: {context_output['source_count']}")
print(f"Context tokens: {context_output['token_count']}")

# --------------------------------------------------
# 7.1 CONTEXT SECURITY INSPECTION
# --------------------------------------------------

print("\n--- CONTEXT SECURITY INSPECTION ---")

observer.start_stage("context_security")

security_result = context_security.inspect(context)

observer.end_stage(
    "context_security",
    status="success" if security_result["safe"] else "blocked",
    metadata={
        "safe": security_result["safe"],
        "status": security_result["status"],
    },
)

print("Security status:", security_result["status"])
print("Safe:", security_result["safe"])

if not security_result["safe"]:
    raise RuntimeError(
        "Context security check failed. "
        "Generation blocked because the context is invalid "
        "or contains a potentially malicious instruction."
    )

print("Context passed security inspection.")

# --------------------------------------------------
# CONTEXT QUALITY EVALUATION
# --------------------------------------------------

# Structural context evaluation is performed during
# the final quality evaluation stage (Section 11.1).
# Semantic evaluation is intentionally skipped to
# avoid an additional LLM inference call.


# --------------------------------------------------
# 8. PREPARE SOURCE METADATA
# --------------------------------------------------

source_metadata = []
print("\n--- SOURCE METADATA DEBUG ---")

for position, source in enumerate(context_output["sources"], start=1):

    source_index = source.get("source_index", position)

    source_metadata.append(
        f"[SOURCE {source_index}] Policy: {source['policy_title']} | "
        f"Pages: {source['page_start']}-{source['page_end']}"
    )

source_reference_text = "\n".join(source_metadata)


# --------------------------------------------------
# 9. PREPARE LLM PROMPT
# --------------------------------------------------

system_prompt = """
You are an HR Policy Assistant.

Your responsibility is to answer employee questions
using only the supplied HR policy context.

Follow these rules:

1. Use the provided context as your source of truth.
2. Do not invent policies, procedures, deadlines, or facts.
3. If the context does not contain the answer, clearly say
   that the available policy context does not provide it.
4. Explain procedures in clear, simple language.
5. Preserve important conditions, exceptions, and timelines.
6. Cite the policy name and page number for factual claims.
7. If multiple policies provide relevant information,
   distinguish them clearly.
8. Do not claim that an action is mandatory unless
   the supplied policy explicitly says so.

   ADDITIONAL INSTRUCTIONS:
- Keep the answer concise and structured.
- Use short bullet points instead of lengthy explanations.
- Cover all important steps from the retrieved context.
- Avoid repeating information.
- Include policy names and page references.
- Never stop in the middle of a sentence.
- If the context does not contain enough information, clearly state that.

CRITICAL FACTUAL ACCURACY RULES:
1. Preserve the exact conditions stated in the source.
   Do not change when, why, or under what circumstances
   a procedure can be used.

2. Distinguish responsibilities between different people.
   For every deadline, identify:
   - Who must perform the action?
   - What action must they perform?
   - When must they perform it?

3. Never transfer a deadline from one person to another.
   For example, if an employee must raise a grievance immediately
   and the manager must respond within two working days,
   do not state that the employee has two working days to submit it.

4. Preserve the scope of every policy.
   Do not generalize a rule applicable to bullying and harassment
   complaints to all workplace complaints.

5. Do not broaden procedural options.
   If mediation is described as something that may help before
   formal procedures begin, do not describe it as a general
   alternative to formal procedures.

6. Preserve exceptions and qualifications.
   For example, if a more senior manager can receive a complaint
   when the employee cannot approach their line manager,
   retain that condition and any requirement to submit it in writing.

7. Every factual statement must be supported by the supplied context.
   If the context does not establish a detail, omit it or explicitly
   state that the available information does not specify it.

8. Before generating the final answer, internally verify:
   - Names of policies.
   - Employee and manager responsibilities.
   - Deadlines and their starting points.
   - Conditions and exceptions.
   - Confidentiality and protection scope.
   - Source page references.

Do not sacrifice factual accuracy for completeness or fluency.

EVIDENCE COVERAGE REQUIREMENTS

When answering questions about HR procedures:

1. Identify all relevant procedures and their applicable stages.
2. Preserve every important condition and exception stated in the retrieved evidence.
3. Include deadlines with:
   - The responsible person.
   - The required action.
   - The exact time limit.
   - The event from which the deadline starts.
4. Preserve escalation paths accurately. Do not merge different stages or escalation authorities.
5. Include important confidentiality, investigation and record-retention requirements when relevant.
6. Distinguish between:
   - Informal resolution.
   - Formal grievance.
   - Bullying and harassment procedures.
   - Disciplinary proceedings.
7. Do not omit important procedural details merely to make the answer shorter.
8. Do not add information that is absent from the supplied evidence.
9. If multiple policies address the question, explain their procedures separately.
10. Prioritize complete and accurate procedural guidance over brevity.

Before finalizing the answer, internally verify:
- Have all relevant procedural stages been covered?
- Are all deadlines and their starting points correct?
- Are exceptions and conditions preserved?
- Are responsibilities assigned to the correct people?
- Are confidentiality and record-retention details accurately represented?
- Is every factual statement supported by the retrieved context?

CITATION REQUIREMENTS:
1. Every factual statement about HR policies must include at least one citation.
2. Use only the numbered source references supplied in the user context.
3. Use the exact citation format: [SOURCE 1], [SOURCE 2], etc.
4. The source number must correspond to the supplied source metadata.
5. Place citations immediately after the factual statement or bullet they support.
6. If multiple sources support a statement, cite each relevant source.
7. Never invent source numbers, policy names, or page numbers.
8. Do not make factual policy claims without citations.
9. If the supplied context does not support a claim, explicitly say so.

"""

user_prompt = f"""
Answer the following employee question using the
provided HR policy context.

EMPLOYEE QUESTION:
{query}

RETRIEVED HR POLICY CONTEXT:
{context}

SOURCE REFERENCES:
{source_reference_text}

Provide a clear, structured answer with relevant
policy names and page numbers.
"""


# --------------------------------------------------
# 10. SEND REQUEST TO OLLAMA
# --------------------------------------------------

payload = {
    "model": MODEL_NAME,
    "messages": [
        {
            "role": "system",
            "content": system_prompt,
        },
        {
            "role": "user",
            "content": user_prompt,
        },
    ],
    "think": False,
    "stream": True,
    "keep_alive": "10m",
    "options": {
        "temperature": 0.2,
        "num_predict": 750,
        "num_ctx": 4096,
    },
}

print("\n--- GENERATING ANSWER ---")
observer.start_stage("generation")
answer_parts = []
result = {}

response = requests.post(
    OLLAMA_URL,
    json=payload,
    timeout=(10, 900),
    stream=True,
)

response.raise_for_status()

for line in response.iter_lines():
    if not line:
        continue

    if isinstance(line, bytes):
        line = line.decode("utf-8")

    chunk = json.loads(line)

    message = chunk.get("message", {})
    token = message.get("content", "")

    if token:
        print(token, end="", flush=True)
        answer_parts.append(token)

    if chunk.get("done"):
        result = chunk

answer = "".join(answer_parts)
observer.end_stage(
    "generation",
    status="success",
    metadata={
        "model": result.get("model", MODEL_NAME),
        "prompt_tokens": result.get("prompt_eval_count"),
        "generated_tokens": result.get("eval_count"),
    },
)

if not answer.strip():
    raise RuntimeError("Ollama returned an empty answer.")

# Preserve the final response metadata for existing code.
result["message"] = result.get("message", {})
result["message"]["content"] = answer

print("\n\n--- GENERATION COMPLETED ---")

# --------------------------------------------------
# 11. EXTRACT GENERATED ANSWER
# --------------------------------------------------

print("\n--- GENERATED HR ANSWER ---")
print(answer)


# --------------------------------------------------
# 11.1 CITATION VALIDATION
# --------------------------------------------------
observer.start_stage("quality_evaluation")
citation_validator = CitationValidator()

citation_result = citation_validator.validate(
    answer=answer,
    sources=context_output["sources"],
)

# --------------------------------------------------
# FINAL ANSWER QUALITY AND ABSTENTION
# --------------------------------------------------

# Fast structural evaluation only.
# Semantic evaluation is intentionally not repeated here.
structural_evaluator = ContextSufficiencyEvaluator()

structural_result = structural_evaluator.evaluate(context_output)

context_quality = {
    "answerable": structural_result["answerable"],
    "final_status": (
        "sufficient"
        if structural_result["answerable"]
        else "structurally_insufficient"
    ),
    "structural_evaluation": structural_result,
}

generation_quality_pipeline = GenerationQualityPipeline()

generation_quality_result = generation_quality_pipeline.evaluate(
    answer=answer,
    sources=context_output["sources"],
    context_quality=context_quality,
    claim_assessments=[],
)

final_answer = generation_quality_result["final_answer"]
observer.end_stage(
    "quality_evaluation",
    status="success",
    metadata={
        "citation_valid": citation_result["valid"],
        "citation_status": citation_result["status"],
        "claim_grounding_status": generation_quality_result[
            "claim_grounding"
        ]["status"],
        "final_decision": generation_quality_result[
            "decision"
        ]["decision"],
        "abstention_reasons": generation_quality_result[
            "decision"
        ]["reasons"],
    },
)

observer.add_metrics({
    "source_count": context_output["source_count"],
    "context_tokens": context_output["token_count"],
    "context_token_budget": context_output["token_budget"],
    "security_passed": security_result["safe"],
    "prompt_tokens": result.get("prompt_eval_count"),
    "generated_tokens": result.get("eval_count"),
    "generation_duration": result.get("eval_duration"),
    "citation_valid": citation_result["valid"],
    "final_decision": generation_quality_result["decision"]["decision"],
})

print("\n--- FINAL GENERATION DECISION ---")
print(json.dumps(generation_quality_result, indent=2, ensure_ascii=False))

print("\n--- FINAL ANSWER ---")
print(final_answer)

print("\n--- CITATION VALIDATION ---")
print(json.dumps(citation_result, indent=4))

# --------------------------------------------------
# 12. GENERATION METADATA
# --------------------------------------------------

print("\n--- GENERATION METADATA ---")

print(f"Model: {result.get('model', MODEL_NAME)}")
print(f"Prompt tokens: {result.get('prompt_eval_count', 'N/A')}")
print(f"Generated tokens: {result.get('eval_count', 'N/A')}")

print(
    f"Generation duration: "
    f"{result.get('eval_duration', 'N/A')} ns"
)

print("\n--- LLM ANSWER GENERATION COMPLETED ---")


# --------------------------------------------------
# 13. SAVE GENERATION ARTIFACTS FOR EVALUATION
# --------------------------------------------------

evaluation_dir = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "evaluation"
    / "generation_runs"
)

evaluation_dir.mkdir(
    parents=True,
    exist_ok=True,
)

generation_artifact = {
    "query": query,
    "answer": answer,
    "context": context,
    "sources": context_output["sources"],
    "security_evaluation": security_result,
    "citation_validation": citation_result,
    "context_quality_evaluation": context_quality,
    "raw_answer": answer,
    "final_answer": final_answer,
    "final_decision": generation_quality_result["decision"],
    "claim_grounding": generation_quality_result["claim_grounding"],
    "generation_metadata": {
        "model": result.get("model", MODEL_NAME),
        "prompt_tokens": result.get("prompt_eval_count"),
        "generated_tokens": result.get("eval_count"),
        "generation_duration": result.get("eval_duration"),
    },
}

artifact_file = evaluation_dir / "complaint_answer.json"

with open(
    artifact_file,
    "w",
    encoding="utf-8",
) as file:
    json.dump(
        generation_artifact,
        file,
        ensure_ascii=False,
        indent=4,
    )

print("\n--- EVALUATION ARTIFACT SAVED ---")
print(f"File: {artifact_file}")

observability_record = observer.save()

print("\n--- OBSERVABILITY ---")
print(f"Run ID: {observability_record['run_id']}")
print(
    f"Total duration: "
    f"{observability_record['total_duration_seconds']} seconds"
)
print(f"Stages recorded: {list(observability_record['stages'].keys())}")
print(f"Observability file: {OBSERVABILITY_FILE}")