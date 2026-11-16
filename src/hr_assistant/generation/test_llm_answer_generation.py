
import json
from pathlib import Path

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


# --------------------------------------------------
# 1. CONFIGURATION
# --------------------------------------------------

MODEL_NAME = "qwen3:8b"
OLLAMA_URL = "http://localhost:11434/api/chat"

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


# --------------------------------------------------
# 6. RETRIEVAL
# --------------------------------------------------

retrieval_output = retrieval_pipeline.search(
    query=query,
    top_k=5,
    candidate_k=10,
)

print("\n--- RETRIEVAL COMPLETED ---")
print(f"Retrieved chunks: {len(retrieval_output['retrieved_chunks'])}")
print(f"Parent contexts: {len(retrieval_output['parent_contexts'])}")


# --------------------------------------------------
# 7. CONTEXT ASSEMBLY
# --------------------------------------------------

context_output = context_builder.build(
    retrieval_output=retrieval_output,
    token_budget=3000,
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

security_result = context_security.inspect(context)

print("\n--- CONTEXT SECURITY INSPECTION ---")
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
# 8. PREPARE SOURCE METADATA
# --------------------------------------------------

source_metadata = []

for index, source in enumerate(context_output["sources"], start=1):
    source_metadata.append(
        f"[SOURCE {index}] "
        f"Policy: {source['policy_title']}; "
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

print("\n--- SENDING REQUEST TO OLLAMA ---")
print(f"Model: {MODEL_NAME}")

payload = {
    "model": "qwen3:8b",
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
    "stream": False,
    "keep_alive": "10m",
    "options": {
        "temperature": 0.2,
        "num_predict": 750,
        "num_ctx": 4096,
    },
}

response = requests.post(
    OLLAMA_URL,
    json=payload,
    timeout=(10, 900),
)

response.raise_for_status()

result = response.json()


# --------------------------------------------------
# 11. EXTRACT GENERATED ANSWER
# --------------------------------------------------

answer = result["message"]["content"]

print("\n--- GENERATED HR ANSWER ---")
print(answer)


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
