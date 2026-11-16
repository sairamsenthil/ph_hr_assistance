
def build_page_registry(registry, total_pages):

    page_registry = {}

    # First classify every page as front matter.
    for page in range(1, total_pages + 1):
        page_registry[page] = {
            "document_region": "front_matter",
            "major_section_number": None,
            "major_section": None,
            "policy_number": None,
            "policy_title": None
        }

    sections = registry["major_sections"]

    for section_index, section in enumerate(sections):

        section_start = section["page_start"]

        if section_index + 1 < len(sections):
            section_end = (
                sections[section_index + 1]["page_start"] - 1
            )
        else:
            section_end = total_pages

        # Assign major-section metadata to every page
        # within the section's page range.
        for page in range(section_start, section_end + 1):

            page_registry[page] = {
                "document_region": "major_section_intro",
                "major_section_number": section["section_number"],
                "major_section": section["title"],
                "policy_number": None,
                "policy_title": None
            }

        policies = section["policies"]

        for policy_index, policy in enumerate(policies):

            policy_start = policy["page_start"]

            if policy_index + 1 < len(policies):
                policy_end = (
                    policies[policy_index + 1]["page_start"] - 1
                )
            else:
                policy_end = section_end

            for page in range(policy_start, policy_end + 1):

                page_registry[page].update({
                    "document_region": "policy_content",
                    "policy_number": policy["policy_number"],
                    "policy_title": policy["title"]
                })

    return page_registry
