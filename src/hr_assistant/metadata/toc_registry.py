
import re


# Verified main policy titles from the PDF Table of Contents.
MAIN_POLICIES = {
    1: "Recruitment and Selection",
    2: "Induction Policy and Checklist",
    3: "Standards of Business Conduct",
    4: "Internet and Email Usage Policy and Guidelines",
    5: "Performance Appraisal Policy",
    6: "Controlling Absence Policy",
    7: "Disciplinary Procedure",
    8: "Capability Procedure",
    9: "Grievance Procedure",
    10: "Prevention of Bullying and Harassment at Work",
    11: '"Whistleblowing" Policy',
    12: "Equality Policy",
    13: "Drug and Alcohol Abuse Policy",
    14: "Health and Safety Policy",
}


def normalize_title(title: str) -> str:
    """Normalize titles for reliable comparison."""

    return re.sub(r"\s+", " ", title).strip().lower()


POLICY_LOOKUP = {
    normalize_title(title): number
    for number, title in MAIN_POLICIES.items()
}


# Recognizes:
# 1. Introduction
# 3 Legislation
NUMBERED_PATTERN = re.compile(
    r"^(\d+)\s*\.?\s+(.+)$"
)

# Recognizes:
# SECTION 1 – EMPLOYING STAFF
# SECTION 2 - MANAGING EMPLOYEE PERFORMANCE
SECTION_PATTERN = re.compile(
    r"^SECTION\s+(\d+)\s*[-–:]\s*(.+)$",
    re.IGNORECASE
)


def build_registry(entries: list[dict]) -> dict:
    """
    Convert flat TOC entries into a hierarchy:

    Major section
        Main policy
            Subsection
    """

    registry = {
        "document_id": "hr_policy_manual",
        "major_sections": []
    }

    current_major_section = None
    current_policy = None

    for entry in entries:

        title = entry["title"].strip()
        page = entry["page"]

        # Identify major sections.
        section_match = SECTION_PATTERN.match(title)

        if section_match:

            section_number = int(section_match.group(1))
            section_title = section_match.group(2).strip()

            current_major_section = {
                "section_number": section_number,
                "title": section_title,
                "page_start": page,
                "policies": []
            }

            registry["major_sections"].append(
                current_major_section
            )

            current_policy = None
            continue

        # Identify numbered entries.
        numbered_match = NUMBERED_PATTERN.match(title)

        if not numbered_match:
            continue

        number = int(numbered_match.group(1))
        title_without_number = numbered_match.group(2).strip()

        normalized_title = normalize_title(
            title_without_number
        )

        # Check whether this is a main policy.
        if normalized_title in POLICY_LOOKUP:

            expected_number = POLICY_LOOKUP[normalized_title]

            if number != expected_number:
                raise ValueError(
                    f"Policy number mismatch: {title}"
                )

            if current_major_section is None:
                raise ValueError(
                    f"Policy found before a major section: {title}"
                )

            current_policy = {
                "policy_number": number,
                "title": title_without_number,
                "page_start": page,
                "subsections": []
            }

            current_major_section["policies"].append(
                current_policy
            )

            continue

        # Otherwise, classify it as a subsection.
        if current_policy is None:
            raise ValueError(
                f"Subsection found without a parent policy: {title}"
            )

        current_policy["subsections"].append({
            "subsection_number": number,
            "title": title_without_number,
            "page_start": page
        })

    return registry


def find_numbering_gaps(registry: dict) -> list[dict]:
    """Find missing subsection numbers within each policy."""

    gaps = []

    for section in registry["major_sections"]:

        for policy in section["policies"]:

            numbers = sorted({
                subsection["subsection_number"]
                for subsection in policy["subsections"]
            })

            if not numbers:
                continue

            expected_numbers = set(
                range(1, max(numbers) + 1)
            )

            missing_numbers = sorted(
                expected_numbers - set(numbers)
            )

            if missing_numbers:

                gaps.append({
                    "policy_number": policy["policy_number"],
                    "policy_title": policy["title"],
                    "missing_subsections": missing_numbers
                })

    return gaps


def calculate_statistics(registry: dict) -> dict:
    """Calculate hierarchy counts."""

    total_sections = len(registry["major_sections"])

    total_policies = sum(
        len(section["policies"])
        for section in registry["major_sections"]
    )

    total_subsections = sum(
        len(policy["subsections"])
        for section in registry["major_sections"]
        for policy in section["policies"]
    )

    return {
        "major_sections": total_sections,
        "main_policies": total_policies,
        "subsections": total_subsections
    }


def find_unclassified_entries(
    entries: list[dict],
    registry: dict
) -> list[dict]:
    """
    Compare original TOC entries against the actual
    entries present in the generated hierarchy.
    """

    classified_entries = set()

    for section in registry["major_sections"]:

        classified_entries.add((
            normalize_title(section["title"]),
            section["page_start"]
        ))

        for policy in section["policies"]:

            classified_entries.add((
                normalize_title(policy["title"]),
                policy["page_start"]
            ))

            for subsection in policy["subsections"]:

                classified_entries.add((
                    normalize_title(subsection["title"]),
                    subsection["page_start"]
                ))

    unclassified = []

    for entry in entries:

        title = entry["title"].strip()
        page = entry["page"]

        # Remove the major-section prefix, if present.
        section_match = SECTION_PATTERN.match(title)

        if section_match:
            comparable_title = section_match.group(2).strip()

        else:
            # Remove a numbered-entry prefix, if present.
            numbered_match = NUMBERED_PATTERN.match(title)

            if not numbered_match:
                unclassified.append(entry)
                continue

            comparable_title = numbered_match.group(2).strip()

        identity = (
            normalize_title(comparable_title),
            page
        )

        if identity not in classified_entries:
            unclassified.append(entry)

    return unclassified
