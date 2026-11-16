
import json
from pathlib import Path
from collections import Counter


# --------------------------------------------------
# 1. CONFIGURATION
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

ARTIFACT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "evaluation"
    / "generation_runs"
    / "complaint_answer.json"
)


# --------------------------------------------------
# 2. LOAD GENERATED ANSWER
# --------------------------------------------------

with open(ARTIFACT_FILE, "r", encoding="utf-8") as file:
    artifact = json.load(file)

answer = artifact["answer"]
context = artifact["context"]


# --------------------------------------------------
# 3. HUMAN-REVIEWED CLAIM ANNOTATIONS
# --------------------------------------------------

claims = [

    {
        "id": "C01",
        "claim": "Employees can initially discuss bullying or harassment with their line manager or HR if able.",
        "status": "supported",
        "policy": "Prevention of Bullying and Harassment at Work",
        "pages": "70",
        "evidence": "encouraged to first discuss matters informally with their line manager or with Human Resources",
        "reason": "Directly supported."
    },

    {
        "id": "C02",
        "claim": "A colleague or trade union representative can speak to the alleged harasser when informal resolution fails.",
        "status": "contradicted",
        "policy": "Prevention of Bullying and Harassment at Work",
        "pages": "71",
        "evidence": "If the complainant feels unable to approach the alleged harasser, a work colleague, or Trade Union representative could be asked to speak to the alleged harasser on the complainant's behalf.",
        "reason": "The answer changes the condition. The actual condition is inability to approach the alleged harasser."
    },

    {
        "id": "C03",
        "claim": "The complainant should document incidents, including times and dates, and notify HR.",
        "status": "supported",
        "policy": "Prevention of Bullying and Harassment at Work",
        "pages": "71",
        "evidence": "times and dates of incidents should be recorded; the matter notified to Human Resources",
        "reason": "Both documentation and HR notification are supported."
    },

    {
        "id": "C04",
        "claim": "The alleged harasser should listen, respect the complainant's perspective and agree to change unacceptable behaviour.",
        "status": "supported",
        "policy": "Prevention of Bullying and Harassment at Work",
        "pages": "71",
        "evidence": "Listen carefully; Respect the other person's point of view; Agree the aspects of behaviour that will change.",
        "reason": "Directly supported."
    },

    {
        "id": "C05",
        "claim": "Formal resolution should be used if informal resolution fails or the allegation is serious.",
        "status": "supported",
        "policy": "Prevention of Bullying and Harassment at Work",
        "pages": "70-71",
        "evidence": "If the alleged harassment continues, the complainant feels unable or unwilling to deal with the matter informally, or the allegation is so serious as to prevent use of the informal procedure.",
        "reason": "Supported, although the answer omits some conditions."
    },

    {
        "id": "C06",
        "claim": "If unable to approach the line manager, the employee should submit a written complaint to a more senior manager or Director.",
        "status": "supported",
        "policy": "Prevention of Bullying and Harassment at Work",
        "pages": "72",
        "evidence": "If the employee feels unable to do this they should submit the complaint in writing to a more senior manager. In exceptional circumstances, allegations may be raised directly with the relevant Director.",
        "reason": "The answer omits the exceptional-circumstances qualification for direct escalation to a Director."
    },

    {
        "id": "C07",
        "claim": "The manager must obtain written details from the complainant and witnesses.",
        "status": "supported",
        "policy": "Prevention of Bullying and Harassment at Work",
        "pages": "72",
        "evidence": "Take full details of the incidents in writing from the complainant; Take full details from any witnesses.",
        "reason": "Directly supported."
    },

    {
        "id": "C08",
        "claim": "The manager must inform the alleged harasser of the allegations and invite them to a meeting.",
        "status": "supported",
        "policy": "Prevention of Bullying and Harassment at Work",
        "pages": "72",
        "evidence": "Inform the alleged harasser of the complaints against him/her ... and invite him/her to a meeting.",
        "reason": "Directly supported."
    },

    {
        "id": "C09",
        "claim": "The manager must keep parties informed of the investigation timeline and outcome.",
        "status": "supported",
        "policy": "Prevention of Bullying and Harassment at Work",
        "pages": "72",
        "evidence": "Keep all parties informed of expected timescales. Inform all parties in writing of the outcome and any action that may be required.",
        "reason": "The answer does not explicitly preserve the requirement to communicate the outcome in writing."
    },

    {
        "id": "C10",
        "claim": "The manager should consider disciplinary action if the complaint is upheld.",
        "status": "supported",
        "policy": "Prevention of Bullying and Harassment at Work",
        "pages": "72-73",
        "evidence": "If there should be a case to answer, an impartial manager will conduct a separate disciplinary investigation; if the complaint is upheld at the disciplinary stage, possible outcomes follow.",
        "reason": "The answer skips the separate disciplinary investigation and procedure."
    },

    {
        "id": "C11",
        "claim": "Possible outcomes include dismissal, warnings and redeployment.",
        "status": "supported",
        "policy": "Prevention of Bullying and Harassment at Work",
        "pages": "73",
        "evidence": "Dismissal; A formal warning; A recommendation of redeployment.",
        "reason": "Directly supported."
    },

    {
        "id": "C12",
        "claim": "Employees should raise grievances immediately with their line manager or supervisor.",
        "status": "supported",
        "policy": "Grievance Procedure",
        "pages": "62",
        "evidence": "An employee who has a grievance, should raise the matter with his line manager / supervisor immediately.",
        "reason": "Directly supported."
    },

    {
        "id": "C13",
        "claim": "The manager must respond to a formal written grievance within two working days.",
        "status": "supported",
        "policy": "Grievance Procedure",
        "pages": "62",
        "evidence": "The manager should then respond within 2 working days.",
        "reason": "Correctly assigns the deadline to the manager."
    },

    {
        "id": "C14",
        "claim": "An employee may appeal to the next manager within ten working days.",
        "status": "supported",
        "policy": "Grievance Procedure",
        "pages": "63",
        "evidence": "The appeal, to the manager next in line, must be made within ten working days of the original response.",
        "reason": "The answer captures the deadline but omits its starting point."
    },

    {
        "id": "C15",
        "claim": "An unresolved grievance proceeds to the Director responsible for the employee's function or the Chief Executive.",
        "status": "supported",
        "policy": "Grievance Procedure",
        "pages": "63",
        "evidence": "Stage 3 appeal to the Director responsible for the employee's function; a grievance raised against a Director will be heard by the Chief Executive.",
        "reason": "The answer makes the Chief Executive sound like a general escalation option. It applies to grievances against a Director."
    },

    {
        "id": "C16",
        "claim": "Appeals must be in writing and include the original grievance form.",
        "status": "supported",
        "policy": "Grievance Procedure",
        "pages": "63",
        "evidence": "Stage 2 appeal must be in writing and contain the original formal Grievance form; Stage 3 appeal must be in writing and enclose a copy of the original Formal Grievance form.",
        "reason": "The requirement applies to specified appeal stages, not necessarily every appeal."
    },

    {
        "id": "C17",
        "claim": "Mediation is voluntary and can help resolve grievances before formal procedures.",
        "status": "supported",
        "policy": "Grievance Procedure",
        "pages": "63",
        "evidence": "An independent third party or mediator can sometimes help resolve grievance issues before it is necessary to invoke the formal procedure. Mediation is a voluntary process.",
        "reason": "Directly supported."
    },

    {
        "id": "C18",
        "claim": "The mediator facilitates discussion and does not decide the outcome.",
        "status": "supported",
        "policy": "Grievance Procedure",
        "pages": "63",
        "evidence": "Any agreement comes from those in dispute, not from the mediator. The mediator is in charge of the process ... but not the outcome.",
        "reason": "Directly supported."
    },

    {
        "id": "C19",
        "claim": "Mediation is not a substitute for formal procedures.",
        "status": "supported",
        "policy": "Grievance Procedure",
        "pages": "63",
        "evidence": "A mediator can sometimes help resolve grievance issues before it is necessary to invoke the formal procedure.",
        "reason": "The answer adds an interpretation not explicitly stated in the source."
    },

    {
        "id": "C20",
        "claim": "All investigations must be thorough and objective.",
        "status": "supported",
        "policy": "Prevention of Bullying and Harassment at Work",
        "pages": "73",
        "evidence": "With any allegation, the need for a thorough and objective investigation is paramount.",
        "reason": "The statement is supported in the context of allegations under this policy, but the answer's broad wording may imply all investigations generally."
    },

    {
        "id": "C21",
        "claim": "A frivolous or malicious complaint may lead to disciplinary proceedings.",
        "status": "supported",
        "policy": "Prevention of Bullying and Harassment at Work",
        "pages": "73",
        "evidence": "If evidence demonstrates that the allegation has been made frivolously, maliciously, or for personal gain, then the individual making the complaint will be subject to Disciplinary proceedings.",
        "reason": "Directly supported."
    },

    {
        "id": "C22",
        "claim": "Records are retained for 12 months if a complaint is substantiated but does not proceed to disciplinary action.",
        "status": "supported",
        "policy": "Prevention of Bullying and Harassment at Work",
        "pages": "73",
        "evidence": "A letter confirming the outcome will be retained on the personal file and supporting documentation retained in a separate file for a period of 12 months.",
        "reason": "The answer omits the distinction between the personal-file letter and supporting documentation in a separate file."
    },

    {
        "id": "C23",
        "claim": "Formal disciplinary records are stored according to the disciplinary procedure.",
        "status": "supported",
        "policy": "Prevention of Bullying and Harassment at Work",
        "pages": "73",
        "evidence": "Where the matter proceeds to a disciplinary hearing then the storage of records should be in accordance with the disciplinary procedure.",
        "reason": "Directly supported."
    },

    {
        "id": "C24",
        "claim": "All investigations must be thorough and objective.",
        "status": "unsupported",
        "policy": "Prevention of Bullying and Harassment at Work",
        "pages": "73",
        "evidence": "With any allegation, the need for a thorough and objective investigation is paramount.",
        "reason": "The source supports thorough and objective investigation, but this is a repeated claim already captured in C20. Do not count this duplicate separately."
    },
]


# --------------------------------------------------
# 4. MANUALLY REVIEWED OMISSIONS
# --------------------------------------------------

omissions = [

    {
        "id": "O01",
        "requirement": "Preserve the confidentiality requirement and explain its scope.",
        "policy": "Prevention of Bullying and Harassment at Work",
        "pages": "70-71",
        "evidence": "All matters relating to the investigation of complaints of harassment or bullying will be treated in strict confidence.",
        "reason": "The generated answer does not explain confidentiality."
    },

    {
        "id": "O02",
        "requirement": "Mention that alleged perpetrators must be informed of the allegations and the names of complainants and witnesses.",
        "policy": "Prevention of Bullying and Harassment at Work",
        "pages": "70-71",
        "evidence": "It will be necessary that any alleged perpetrator is made aware of the allegations ... and the names of witnesses.",
        "reason": "The answer mentions informing the alleged harasser but omits the necessary disclosure qualification."
    },

    {
        "id": "O03",
        "requirement": "Explain that informal complaints resolved at that stage leave no record on personal files.",
        "policy": "Prevention of Bullying and Harassment at Work",
        "pages": "73",
        "evidence": "Where the complaint is informal and resolved at this stage, no record will be kept on personal files.",
        "reason": "Omitted from the answer."
    },

    {
        "id": "O04",
        "requirement": "Explain that no records are retained when a formal investigation does not substantiate the complaint.",
        "policy": "Prevention of Bullying and Harassment at Work",
        "pages": "73",
        "evidence": "Following formal investigation, where the complaint is not substantiated, no records will be retained.",
        "reason": "Omitted from the answer."
    },

    {
        "id": "O05",
        "requirement": "Mention the Stage 2 manager's response deadline of seven days.",
        "policy": "Grievance Procedure",
        "pages": "63",
        "evidence": "A formal response and full explanation will be given in writing ... within 7 days.",
        "reason": "Omitted from the answer."
    },

    {
        "id": "O06",
        "requirement": "Mention the Stage 3 Director's response deadline of twenty working days.",
        "policy": "Grievance Procedure",
        "pages": "63",
        "evidence": "This Director will arrange and hear the appeal ... and respond formally with a full explanation within 20 working days.",
        "reason": "Omitted from the answer."
    },

    {
        "id": "O07",
        "requirement": "Preserve the exceptional-circumstances condition for raising allegations directly with a Director.",
        "policy": "Prevention of Bullying and Harassment at Work",
        "pages": "72",
        "evidence": "In exceptional circumstances, allegations may be raised directly with the relevant Director.",
        "reason": "The answer does not preserve this qualification."
    }
]


# --------------------------------------------------
# 5. HUMAN REVIEW STATUS
# --------------------------------------------------

# Claims are manually annotated against the latest generated answer.
# Do not infer support from keyword matching.

for claim in claims:
    claim["present_in_answer"] = True

# C24 duplicates C20 and is excluded from metric calculations.
evaluated_claims = [
    claim for claim in claims
    if claim["id"] != "C24"
]


# --------------------------------------------------
# 6. CALCULATE METRICS
# --------------------------------------------------

status_counts = Counter(
    claim["status"]
    for claim in evaluated_claims
)

total_claims = len(evaluated_claims)

supported = status_counts["supported"]
partial = status_counts["partially_supported"]
unsupported = status_counts["unsupported"]
contradicted = status_counts["contradicted"]

strict_grounding_score = (
    supported / total_claims
) * 100

weighted_grounding_score = (
    (supported + (0.5 * partial)) / total_claims
) * 100

omission_count = len(omissions)


# --------------------------------------------------
# 7. PRINT CLAIM-LEVEL RESULTS
# --------------------------------------------------

print("\n" + "=" * 75)
print("CLAIM-LEVEL EVIDENCE GROUNDING EVALUATION")
print("=" * 75)

for claim in evaluated_claims:

    print(f"\n{claim['id']} | {claim['status'].upper()}")
    print("Claim:", claim["claim"])
    print("Policy:", claim["policy"])
    print("Pages:", claim["pages"])
    print("Evidence:", claim["evidence"])
    print("Reason:", claim["reason"])


# --------------------------------------------------
# 8. PRINT OMISSIONS
# --------------------------------------------------

print("\n" + "=" * 75)
print("IMPORTANT EVIDENCE OMISSIONS")
print("=" * 75)

for omission in omissions:

    print(f"\n{omission['id']}")
    print("Requirement:", omission["requirement"])
    print("Policy:", omission["policy"])
    print("Pages:", omission["pages"])
    print("Evidence:", omission["evidence"])
    print("Reason:", omission["reason"])


# --------------------------------------------------
# 9. PRINT SUMMARY
# --------------------------------------------------

print("\n" + "=" * 75)
print("EVALUATION SUMMARY")
print("=" * 75)

print("Total evaluated claims:", total_claims)
print("Supported:", supported)
print("Partially supported:", partial)
print("Unsupported:", unsupported)
print("Contradicted:", contradicted)

print(f"Strict grounding score: {strict_grounding_score:.2f}%")
print(f"Weighted grounding score: {weighted_grounding_score:.2f}%")

print("Important omissions:", omission_count)


# --------------------------------------------------
# 10. SAVE RESULTS
# --------------------------------------------------

output = {
    "query": artifact["query"],
    "model": artifact["generation_metadata"]["model"],
    "total_claims": total_claims,
    "status_counts": dict(status_counts),
    "strict_grounding_score": round(strict_grounding_score, 2),
    "weighted_grounding_score": round(weighted_grounding_score, 2),
    "important_omissions_count": omission_count,
    "claims": evaluated_claims,
    "omissions": omissions,
    "evaluation_note": (
        "Human-reviewed claim annotations. "
        "Scores apply only to the selected claims, not every sentence."
    )
}

output_file = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "evaluation"
    / "generation_runs"
    / "evidence_grounding_results_v2.json"
)

with open(output_file, "w", encoding="utf-8") as file:
    json.dump(output, file, indent=4, ensure_ascii=False)

print("\nResults saved to:")
print(output_file)
