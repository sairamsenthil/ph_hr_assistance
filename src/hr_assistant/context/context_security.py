
import re


class ContextSecurity:

    INJECTION_PATTERNS = [
        r"ignore\s+(all\s+)?previous\s+instructions",
        r"ignore\s+(all\s+)?system\s+instructions",
        r"reveal\s+(the\s+)?system\s+prompt",
        r"act\s+as\s+system",
        r"override\s+(all\s+)?instructions",
        r"disregard\s+(all\s+)?previous\s+instructions",
    ]

    def inspect(self, context):

        if not isinstance(context, str) or not context.strip():
            return {
                "safe": False,
                "status": "invalid_context",
                "detected_patterns": [],
            }

        detected_patterns = []

        for pattern in self.INJECTION_PATTERNS:
            if re.search(pattern, context, re.IGNORECASE):
                detected_patterns.append(pattern)

        return {
            "safe": len(detected_patterns) == 0,
            "status": (
                "potential_injection_detected"
                if detected_patterns
                else "no_known_injection_detected"
            ),
            "detected_patterns": detected_patterns,
        }
