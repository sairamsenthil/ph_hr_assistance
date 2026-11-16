
import re


class QueryClassifier:

    def __init__(self):

        self.intent_patterns = {

            "procedure": [
                r"\bhow can\b",
                r"\bhow do i\b",
                r"\bwhat steps\b",
                r"\bsteps to\b",
                r"\bprocess for\b",
                r"\bprocedure for\b",
                r"\bhow are .* selected\b",
                r"\braise .* complaint\b",
                r"\braise .* grievance\b",
            ],

            "obligation": [
                r"\bwhat should\b",
                r"\bmust .* do\b",
                r"\bshould .* do\b",
                r"\brequired to\b",
                r"\bneed to\b",
            ],

            "eligibility": [
                r"\beligible\b",
                r"\bqualify\b",
                r"\bentitled to\b",
                r"\bwho can apply\b",
                r"\bwho is allowed\b",
            ],

            "deadline": [
                r"\bhow many days\b",
                r"\bhow many working days\b",
                r"\bwithin \d+ days\b",
                r"\bdeadline\b",
                r"\btime limit\b",
                r"\bby when\b",
                r"\bhow long do i have\b",
                r"\bresponse deadline\b",
            ],

            "responsibility": [
                r"\bwho is responsible\b",
                r"\bwho handles\b",
                r"\bwho investigates\b",
                r"\bwho should\b",
                r"\bwhich manager\b",
                r"\bwho approves\b",
            ],

            "definition": [
                r"\bwhat is (?:the )?(?:meaning|definition) of\b",
                r"\bwhat does .* mean\b",
                r"\bwhat constitutes\b",
                r"\bdefine\b",
                r"\bwhat is (?:workplace )?(?:harassment|bullying|misconduct)\b",
            ],

            "confidentiality": [
                r"\bconfidential\b",
                r"\bconfidentiality\b",
                r"\bprivate\b",
                r"\bwho can access\b",
                r"\bdisclose\b",
                r"\bshare .* information\b",
            ],

            "record_retention": [
                r"\bhow long .* retained\b",
                r"\bhow long .* kept\b",
                r"\bretention\b",
                r"\bretain .* records\b",
                r"\bkeep .* records\b",
                r"\bstored .* records\b",
            ],

            "disciplinary": [
                r"\bdisciplinary\b",
                r"\bmisconduct\b",
                r"\bmisbehaviour\b",
                r"\bsanction\b",
                r"\bdismissal\b",
                r"\bwarning\b",
            ],

            "policy_overview": [
                r"\bwhat does .* policy say\b",
                r"\bexplain .* policy\b",
                r"\btell me about\b",
                r"\boverview of\b",
            ],
        }

    def classify(self, query):

        if not isinstance(query, str) or not query.strip():
            raise ValueError("Query must be a non-empty string.")

        normalized_query = re.sub(
            r"\s+",
            " ",
            query.lower()
        ).strip()

        detected_intents = []

        for intent, patterns in self.intent_patterns.items():

            for pattern in patterns:

                if re.search(pattern, normalized_query):

                    detected_intents.append(intent)
                    break

        if not detected_intents:
            detected_intents.append("general_information")

        return {
            "original_query": query,
            "normalized_query": normalized_query,
            "intents": detected_intents,
            "primary_intent": detected_intents[0],
            "classification_method": "rule_based",
        }
