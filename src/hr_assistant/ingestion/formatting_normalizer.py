
import re


DOT_LEADER_PATTERN = re.compile(r"\.{10,}")
DASH_SEPARATOR_PATTERN = re.compile(r"-{10,}")


def normalize_formatting(text: str) -> dict:
    """
    Remove long visual separators while preserving semantic text.
    """

    normalized_text, dotted_count = DOT_LEADER_PATTERN.subn(
        "[Field]",
        text
    )

    normalized_text, dashed_count = DASH_SEPARATOR_PATTERN.subn(
        "",
        normalized_text
    )

    # Remove unnecessary spaces left around removed separators.
    normalized_text = re.sub(r"[ \t]{2,}", " ", normalized_text)
    normalized_text = re.sub(r" *\n *", "\n", normalized_text)

    return {
        "text": normalized_text.strip(),
        "dotted_runs_removed": dotted_count,
        "dashed_runs_removed": dashed_count
    }
