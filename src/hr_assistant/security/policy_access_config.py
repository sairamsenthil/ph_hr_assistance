
POLICY_ACCESS_LEVELS = {
    "Recruitment and Selection": "public",
    "Induction Policy and Checklist": "public",
    "Equality Policy": "public",
    "Health and Safety Policy": "public",
    "Standards of Business Conduct": "public",
    "Internet and Email Usage Policy and Guidelines": "public",
    "Controlling Absence Policy": "public",
    "Performance Appraisal Policy": "manager",
    "Grievance Procedure": "public",
    "Prevention of Bullying and Harassment at Work": "public",
    '"Whistleblowing" Policy': "public",
    "Disciplinary Procedure": "manager",
    "Capability Procedure": "manager",
    "Drug and Alcohol Abuse Policy": "hr",
}

VALID_ACCESS_LEVELS = {"public", "manager", "hr", "admin"}


def get_policy_access_level(policy_title: str) -> str:
    if policy_title not in POLICY_ACCESS_LEVELS:
        raise ValueError(
            f"No access level configured for policy: {policy_title}"
        )

    access_level = POLICY_ACCESS_LEVELS[policy_title]

    if access_level not in VALID_ACCESS_LEVELS:
        raise ValueError(
            f"Invalid access level '{access_level}' "
            f"for policy '{policy_title}'"
        )

    return access_level
