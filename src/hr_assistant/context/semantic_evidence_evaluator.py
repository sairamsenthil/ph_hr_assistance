
import json
import re
import requests


class SemanticEvidenceEvaluator:

    def __init__(
        self,
        model="qwen3:8b",
        ollama_url="http://localhost:11434/api/chat",
    ):
        self.model = model
        self.ollama_url = ollama_url

    def _extract_json(self, content):

        content = content.strip()

        # Remove optional Markdown code fences
        content = re.sub(
            r"^```(?:json)?\s*|\s*```$",
            "",
            content,
            flags=re.IGNORECASE,
        ).strip()

        return json.loads(content)

    def evaluate(
        self,
        query,
        context,
        required_evidence,
    ):

        if not isinstance(query, str) or not query.strip():
            raise ValueError("Query must be a non-empty string.")

        if not isinstance(context, str) or not context.strip():
            raise ValueError("Context must be a non-empty string.")

        if not isinstance(required_evidence, list) or not required_evidence:
            raise ValueError("Required evidence must be a non-empty list.")

        prompt = f"""
You are evaluating evidence sufficiency for an HR policy RAG system.

Your task is to evaluate whether the supplied context contains enough
reliable evidence to answer the user's question.

USER QUESTION:
{query}

REQUIRED EVIDENCE:
{json.dumps(required_evidence, ensure_ascii=False)}

RETRIEVED CONTEXT:
{context}

INSTRUCTIONS:

1. Evaluate every required evidence item separately.
2. Recognize semantically equivalent paraphrases.
3. Do not treat keyword overlap alone as evidence.
4. Identify missing conditions, exceptions, roles and deadlines.
5. Identify contradictions within the supplied context.
6. Do not use outside knowledge or assumptions.
7. Do not invent policy requirements.
8. If evidence is incomplete or ambiguous, do not mark it as fully supported.
9. Decide whether the context is sufficient to answer the question safely.

Return ONLY valid JSON using this exact structure:

{{
    "answerable": true,
    "overall_status": "sufficient",
    "evidence_assessments": [
        {{
            "requirement": "required evidence item",
            "status": "supported",
            "reason": "explanation based on context"
        }}
    ],
    "missing_conditions": [],
    "contradictions": [],
    "reason": "overall assessment"
}}

Allowed evidence statuses:
- supported
- partially_supported
- missing
- contradicted

Allowed overall_status values:
- sufficient
- partially_sufficient
- insufficient

Set answerable to true only when the context supports a safe,
complete answer to the question.
"""

        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            "stream": False,
            "think": False,
            "format": "json",
            "options": {
                "temperature": 0.0,
                "num_predict": 700,
            },
            "keep_alive": "10m",
        }

        try:

            response = requests.post(
                self.ollama_url,
                json=payload,
                timeout=(10, 300),
            )

            response.raise_for_status()

            response_data = response.json()

            content = response_data["message"]["content"]

            result = self._extract_json(content)

            # Validate model output
            if not isinstance(result, dict):
                raise ValueError("Model output must be a JSON object.")

            required_keys = {
                "answerable",
                "overall_status",
                "evidence_assessments",
                "missing_conditions",
                "contradictions",
                "reason",
            }

            if not required_keys.issubset(result):
                raise ValueError("Model output is missing required fields.")

            if not isinstance(result["answerable"], bool):
                raise ValueError("Invalid answerable value.")

            allowed_statuses = {
                "sufficient",
                "partially_sufficient",
                "insufficient",
            }

            if result["overall_status"] not in allowed_statuses:
                raise ValueError("Invalid overall status.")

            if not isinstance(result["evidence_assessments"], list):
                raise ValueError("Invalid evidence assessments.")
            
            # Verify that every required evidence item was assessed
            assessments = result["evidence_assessments"]

            assessed_requirements = {
                item.get("requirement")
                for item in assessments
            }

            expected_requirements = set(required_evidence)

            if assessed_requirements != expected_requirements:
                raise ValueError(
                    "Evidence assessments do not cover all requirements."
                )

            evidence_statuses = [
                item["status"]
                for item in assessments
            ]

            # Python controls the final answerability decision
            has_contradictions = (
                "contradicted" in evidence_statuses
            )

            has_missing = (
                "missing" in evidence_statuses
            )

            has_partial = (
                "partially_supported" in evidence_statuses
            )

            if has_contradictions or has_missing:
                result["answerable"] = False
                result["overall_status"] = "insufficient"

            elif has_partial:
                result["answerable"] = False
                result["overall_status"] = "partially_sufficient"

            else:
                result["answerable"] = True
                result["overall_status"] = "sufficient"


            allowed_evidence_statuses = {
                "supported",
                "partially_supported",
                "missing",
                "contradicted",
            }

            for item in result["evidence_assessments"]:

                if not isinstance(item, dict):
                    raise ValueError("Invalid evidence assessment item.")

                if item.get("status") not in allowed_evidence_statuses:
                    raise ValueError("Invalid evidence assessment status.")

            if (
                not isinstance(result["missing_conditions"], list)
                or not isinstance(result["contradictions"], list)
                or not isinstance(result["reason"], str)
            ):
                raise ValueError("Invalid semantic evaluation structure.")

            return {
                **result,
                "evaluation_status": "success",
                "model": self.model,
                "fallback_used": False,
            }

        except Exception as error:

            return {
                "answerable": False,
                "overall_status": "insufficient",
                "evidence_assessments": [],
                "missing_conditions": [],
                "contradictions": [],
                "reason": "Semantic evaluation could not be completed.",
                "evaluation_status": "failed",
                "model": self.model,
                "fallback_used": True,
                "error": str(error),
            }
