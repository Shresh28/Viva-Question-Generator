"""Strict validation for the local model's structured response."""

from collections import Counter
import json
import re
from typing import Any

DIFFICULTIES = ("Easy", "Medium", "Hard")
OUTPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "project_info": {
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "domain": {"type": "string"},
                "objective": {"type": "string"},
                "technologies": {"type": "array", "items": {"type": "string"}},
            },
            "required": ["title", "domain", "objective", "technologies"],
            "additionalProperties": False,
        },
        "questions": {
            "type": "object",
            "properties": {
                level: {
                    "type": "array",
                    "minItems": 5,
                    "maxItems": 5,
                    "items": {
                        "type": "object",
                        "properties": {
                            "question": {"type": "string"},
                            "answer": {"type": "string"},
                        },
                        "required": ["question", "answer"],
                        "additionalProperties": False,
                    },
                }
                for level in DIFFICULTIES
            },
            "required": list(DIFFICULTIES),
            "additionalProperties": False,
        },
    },
    "required": ["project_info", "questions"],
    "additionalProperties": False,
}


class OutputValidationError(ValueError):
    """Raised when generated JSON does not meet the application contract."""


def _strip_fence(raw: str) -> str:
    value = raw.strip()
    if value.startswith("```"):
        value = re.sub(r"^```(?:json)?\s*", "", value, flags=re.IGNORECASE)
        value = re.sub(r"\s*```$", "", value)
    return value.strip()


def parse_response(raw: str, expected_per_level: int = 5) -> dict[str, Any]:
    try:
        data = json.loads(_strip_fence(raw))
    except (json.JSONDecodeError, TypeError) as exc:
        raise OutputValidationError("The AI returned invalid JSON. Please regenerate the questions.") from exc
    if not isinstance(data, dict) or not isinstance(data.get("project_info"), dict):
        raise OutputValidationError("The AI response is missing project_info.")
    info = data["project_info"]
    for field in ("title", "domain", "objective"):
        if not isinstance(info.get(field), str) or not info[field].strip():
            raise OutputValidationError(f"The AI response has a missing or invalid project_info.{field} field.")
    # Smaller local models occasionally return a single technology string
    # instead of the requested array; normalize that harmless shape variation.
    technologies = info.get("technologies")
    if isinstance(technologies, str):
        technologies = [part.strip() for part in re.split(r"[,;]", technologies) if part.strip()]
    if technologies is None:
        technologies = []
    if not isinstance(technologies, list) or not all(isinstance(x, str) for x in technologies):
        raise OutputValidationError("The AI response has an invalid project_info.technologies field.")
    info["technologies"] = technologies
    questions = data.get("questions")
    if isinstance(questions, dict):
        grouped = []
        for level in DIFFICULTIES:
            level_items = questions.get(level)
            if not isinstance(level_items, list):
                raise OutputValidationError(f"The AI response is missing the {level} question group.")
            grouped.extend(
                {**item, "difficulty": level} if isinstance(item, dict) else item
                for item in level_items
            )
        questions = grouped
    expected_total = expected_per_level * len(DIFFICULTIES)
    if not isinstance(questions, list) or len(questions) != expected_total:
        raise OutputValidationError(f"Expected exactly {expected_total} questions; the AI returned an incomplete set.")
    counts: Counter[str] = Counter()
    seen: set[str] = set()
    validated = []
    for index, item in enumerate(questions, 1):
        if not isinstance(item, dict):
            raise OutputValidationError(f"Question {index} is not an object.")
        level, question, answer = item.get("difficulty"), item.get("question"), item.get("answer")
        if level not in DIFFICULTIES:
            raise OutputValidationError(f"Question {index} has an unknown difficulty.")
        if not isinstance(question, str) or not question.strip() or not isinstance(answer, str) or not answer.strip():
            raise OutputValidationError(f"Question {index} is missing its question or answer.")
        key = re.sub(r"[^a-z0-9]+", " ", question.lower()).strip()
        if key in seen:
            raise OutputValidationError("The AI returned duplicate questions. Please regenerate.")
        seen.add(key)
        counts[level] += 1
        validated.append({"difficulty": level, "question": question.strip(), "answer": answer.strip()})
    if any(counts[level] != expected_per_level for level in DIFFICULTIES):
        raise OutputValidationError("Question difficulty counts are incorrect. Please regenerate.")
    return {"project_info": {**info, "technologies": info["technologies"]}, "questions": validated}

