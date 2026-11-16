
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

ARTIFACT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "evaluation"
    / "generation_runs"
    / "complaint_answer.json"
)

with open(ARTIFACT_FILE, "r", encoding="utf-8") as file:
    artifact = json.load(file)

print("=" * 70)
print("GENERATED ANSWER")
print("=" * 70)

print(artifact["answer"])

print("\n" + "=" * 70)
print("RETRIEVED EVIDENCE CONTEXT")
print("=" * 70)

print(artifact["context"])

print("\n" + "=" * 70)
print("SOURCE METADATA")
print("=" * 70)

for source in artifact["sources"]:
    print({
        "policy": source["policy_title"],
        "pages": (
            f'{source["page_start"]}-{source["page_end"]}'
        ),
        "source_id": source["source_id"],
    })
