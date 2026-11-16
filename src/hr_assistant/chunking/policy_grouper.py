
def group_pages_by_policy(
    pages: list[dict],
    page_registry: dict
) -> list[dict]:
    """
    Group consecutive pages belonging to the same policy.

    Pages with different policies or document regions
    are kept in separate groups.
    """

    sorted_pages = sorted(
        pages,
        key=lambda item: item["metadata"]["page"]
    )

    groups = []
    current_group = None

    for page in sorted_pages:

        page_number = page["metadata"]["page"]

        registry_metadata = page_registry.get(
            page_number,
            {}
        )

        policy_number = registry_metadata.get("policy_number")
        major_section_number = registry_metadata.get(
            "major_section_number"
        )
        document_region = registry_metadata.get(
            "document_region"
        )

        group_key = (
            document_region,
            major_section_number,
            policy_number
        )

        if (
    current_group is None
    or current_group["group_key"] != group_key
    or page_number != current_group["page_end"] + 1
    ):

            current_group = {
                "group_key": group_key,
                "document_region": document_region,
                "major_section_number": major_section_number,
                "policy_number": policy_number,
                "policy_title": registry_metadata.get("policy_title"),
                "page_start": page_number,
                "page_end": page_number,
                "pages": []
            }

            groups.append(current_group)

        current_group["pages"].append(page)
        current_group["page_end"] = page_number

    return groups


def combine_group_pages(group: dict) -> dict:
    """
    Combine pages belonging to one group while
    preserving each page's character positions.
    """

    text_parts = []
    page_spans = []
    current_position = 0

    for page in group["pages"]:

        page_number = page["metadata"]["page"]
        page_text = page.get("normalized_text", "").strip()

        start_char = current_position
        end_char = start_char + len(page_text)

        page_spans.append({
            "page": page_number,
            "start_char": start_char,
            "end_char": end_char
        })

        text_parts.append(page_text)
        current_position = end_char

        # Add a separator between consecutive pages.
        text_parts.append("\n\n")
        current_position += 2

    combined_text = "".join(text_parts).rstrip()

    return {
        "text": combined_text,
        "page_spans": page_spans,
        "page_start": group["page_start"],
        "page_end": group["page_end"],
        "policy_number": group["policy_number"],
        "policy_title": group["policy_title"]
    }
