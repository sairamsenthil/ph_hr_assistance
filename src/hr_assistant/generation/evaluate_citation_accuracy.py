
import json
from pathlib import Path


ARTIFACT_PATH = Path(
    "data/processed/evaluation/generation_runs/complaint_answer.json"
)

OUTPUT_PATH = Path(
    "data/processed/evaluation/generation_runs/citation_accuracy_results.json"
)


def normalize(value):
    return " ".join(value.lower().split())


def evaluate_citations():
    with open(ARTIFACT_PATH, "r", encoding="utf-8") as file:
        artifact = json.load(file)

    print("\n" + "=" * 75)
    print("CITATION ACCURACY EVALUATION")
    print("=" * 75)

    print("\nGENERATED ANSWER")
    print("-" * 75)
    print(artifact["answer"])

    print("\nAVAILABLE RETRIEVED SOURCES")
    print("-" * 75)

    sources = artifact.get("sources", [])

    for index, source in enumerate(sources, start=1):
        print(f"\nSource {index}")
        print(f"Policy: {source.get('policy_title')}")
        print(f"Pages: {source.get('pages')}")

    # Manually review the generated answer and fill actual_policy
    # and actual_pages for each claim based on its citations.
    claims = [
        {
            "id": "C01",
            "claim": "Initial informal discussion with line manager or HR",
            "expected_policy": "Prevention of Bullying and Harassment at Work",
            "expected_pages": [70],
            "actual_policy": "Prevention of Bullying and Harassment at Work",
            "actual_pages": [70, 71],
        },
        {
            "id": "C02",
            "claim": "Colleague or Trade Union representative can intervene",
            "expected_policy": "Prevention of Bullying and Harassment at Work",
            "expected_pages": [71],
            "actual_policy": "Prevention of Bullying and Harassment at Work",
            "actual_pages": [70, 71], 
        },
        {
            "id": "C03",
            "claim": "Document incidents and record dates and times",
            "expected_policy": "Prevention of Bullying and Harassment at Work",
            "expected_pages": [71],
            "actual_policy": None,
            "actual_pages": [],
        },
        {
            "id": "C04",
            "claim": "Harassment and bullying complaints must be notified to HR",
            "expected_policy": "Prevention of Bullying and Harassment at Work",
            "expected_pages": [71],
            "actual_policy": None,
            "actual_pages": [],
        },
        {
            "id": "C05",
            "claim": "Formal resolution when informal resolution fails or is unsuitable",
            "expected_policy": "Prevention of Bullying and Harassment at Work",
            "expected_pages": [71],
            "actual_policy": None,
            "actual_pages": [],
        },
        {
            "id": "C06",
            "claim": "Formal complaint to line manager or more senior manager",
            "expected_policy": "Prevention of Bullying and Harassment at Work",
            "expected_pages": [72],
            "actual_policy": None,
            "actual_pages": [],
        },
        {
            "id": "C07",
            "claim": "Manager obtains written details from complainant and witnesses",
            "expected_policy": "Prevention of Bullying and Harassment at Work",
            "expected_pages": [72],
            "actual_policy": None,
            "actual_pages": [],
        },
        {
            "id": "C08",
            "claim": "Manager communicates investigation timescales and outcome",
            "expected_policy": "Prevention of Bullying and Harassment at Work",
            "expected_pages": [72],
            "actual_policy": None,
            "actual_pages": [],
        },
        {
            "id": "C09",
            "claim": "Possible outcomes include formal warnings and redeployment",
            "expected_policy": "Prevention of Bullying and Harassment at Work",
            "expected_pages": [73],
            "actual_policy": None,
            "actual_pages": [],
        },
        {
            "id": "C10",
            "claim": "Employee must raise Stage 1 grievance within two working days",
            "expected_policy": "Grievance Procedure",
            "expected_pages": [62],
            "actual_policy": "Grievance Procedure",
            "actual_pages": [62, 63],
        },
        {
            "id": "C11",
            "claim": "Stage 2 appeal within ten working days of original response",
            "expected_policy": "Grievance Procedure",
            "expected_pages": [63],
            "actual_policy": None,
            "actual_pages": [],
        },
        {
            "id": "C12",
            "claim": "Stage 3 appeal within ten working days of Stage 2 response",
            "expected_policy": "Grievance Procedure",
            "expected_pages": [63],
            "actual_policy": None,
            "actual_pages": [],
        },
        {
            "id": "C13",
            "claim": "Grievance against Director is heard by CEO",
            "expected_policy": "Grievance Procedure",
            "expected_pages": [63],
            "actual_policy": None,
            "actual_pages": [],
        },
        {
            "id": "C14",
            "claim": "Mediation can be used before formal grievance procedure",
            "expected_policy": "Grievance Procedure",
            "expected_pages": [63],
            "actual_policy": None,
            "actual_pages": [],
        },
        {
            "id": "C15",
            "claim": "Complaints are treated in strict confidence",
            "expected_policy": "Prevention of Bullying and Harassment at Work",
            "expected_pages": [70, 71],
            "actual_policy": None,
            "actual_pages": [],
        },
        {
            "id": "C16",
            "claim": "Employees are protected from victimization or detriment",
            "expected_policy": "Prevention of Bullying and Harassment at Work",
            "expected_pages": [71],
            "actual_policy": None,
            "actual_pages": [],
        },
    ]

    # Section-level citation annotations from the generated answer

    citation_annotations = {
        "C01": (
            "Prevention of Bullying and Harassment at Work",
            [70, 71],
        ),
        "C02": (
            "Prevention of Bullying and Harassment at Work",
            [70, 71],
        ),
        "C03": (
            "Prevention of Bullying and Harassment at Work",
            [70, 71],
        ),
        "C04": (
            "Prevention of Bullying and Harassment at Work",
            [70, 71],
        ),
        "C05": (
            "Prevention of Bullying and Harassment at Work",
            [71, 72, 73],
        ),
        "C06": (
            "Prevention of Bullying and Harassment at Work",
            [71, 72, 73],
        ),
        "C07": (
            "Prevention of Bullying and Harassment at Work",
            [71, 72, 73],
        ),
        "C08": (
            "Prevention of Bullying and Harassment at Work",
            [71, 72, 73],
        ),
        "C09": (
            "Prevention of Bullying and Harassment at Work",
            [71, 72, 73],
        ),
        "C10": ("Grievance Procedure", [62, 63]),
        "C11": ("Grievance Procedure", [62, 63]),
        "C12": ("Grievance Procedure", [62, 63]),
        "C13": ("Grievance Procedure", [62, 63]),
        "C14": ("Grievance Procedure", [62, 63]),
        "C15": (
            "Prevention of Bullying and Harassment at Work",
            [71],
        ),
        "C16": (None, []),
    }

    for claim in claims:
        policy, pages = citation_annotations[claim["id"]]
        claim["actual_policy"] = policy
        claim["actual_pages"] = pages

    print("\nCITATION REVIEW TEMPLATE")
    print("-" * 75)

    results = []

    for claim in claims:
        actual_policy = claim["actual_policy"]
        actual_pages = claim["actual_pages"]

        if actual_policy is None and not actual_pages:
          status = "MISSING_CITATION"
        elif actual_policy is None or not actual_pages:
            status = "INCOMPLETE_CITATION"
        elif normalize(actual_policy) != normalize(
            claim["expected_policy"]
        ):
            status = "WRONG_POLICY"
        elif not set(actual_pages).intersection(
            claim["expected_pages"]
        ):
            status = "WRONG_PAGE"
        else:
            status = "CORRECT"

        result = {
            **claim,
            "citation_status": status,
        }

        results.append(result)

        print(
            f'{claim["id"]} | {status} | '
            f'{claim["claim"]}'
        )

    reviewed = [
    item for item in results
    if item["citation_status"] not in [
        "NOT_REVIEWED",
        "MISSING_CITATION",
        "INCOMPLETE_CITATION",
    ]
]

    correct = sum(
        item["citation_status"] == "CORRECT"
        for item in reviewed
    )

    print("\n" + "=" * 75)
    print("CITATION EVALUATION SUMMARY")
    print("=" * 75)

    print(f"Total claims: {len(results)}")
    print(f"Reviewed claims: {len(reviewed)}")
    print(f"Correct citations: {correct}")
    print(f"Not reviewed: {len(results) - len(reviewed)}")

    if reviewed:
        accuracy = correct / len(reviewed) * 100
        print(f"Citation accuracy: {accuracy:.2f}%")
    else:
        accuracy = None
        print("Citation accuracy: Not available")

    output = {
        "total_claims": len(results),
        "reviewed_claims": len(reviewed),
        "correct_citations": correct,
        "citation_accuracy": accuracy,
        "results": results,
    }

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    with open(OUTPUT_PATH, "w", encoding="utf-8") as file:
        json.dump(output, file, indent=4, ensure_ascii=False)

    print(f"\nResults saved to: {OUTPUT_PATH}")


if __name__ == "__main__":
    evaluate_citations()
