"""Ollama local-model adapter for viva question generation."""

import os

from dotenv import load_dotenv
import requests

from src.output_parser import OUTPUT_SCHEMA, OutputValidationError, parse_response
from src.prompt_builder import SYSTEM_PROMPT, build_prompt


class AIGenerationError(RuntimeError):
    """A safe, user-presentable local model error."""


def generate_questions(report_text: str, answer_length: str = "Short", *,
                       model: str | None = None) -> dict:
    """Send report text to the local Ollama HTTP service and validate its output."""
    load_dotenv()
    model_name = model or os.getenv("OLLAMA_MODEL", "llama3.2:latest").strip()
    base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434").rstrip("/")
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": build_prompt(report_text, answer_length)},
    ]
    for attempt in range(3):
        try:
            response = requests.post(
                f"{base_url}/api/chat",
                json={
                    "model": model_name,
                    "messages": messages,
                    "format": OUTPUT_SCHEMA,
                    "stream": False,
                    "options": {"temperature": 0.2},
                },
                timeout=180,
            )
        except requests.exceptions.ConnectionError as exc:
            raise AIGenerationError("Ollama is not running. Start the Ollama app, then try again.") from exc
        except requests.exceptions.Timeout as exc:
            raise AIGenerationError("The local model took too long. Try a shorter report or a smaller model.") from exc
        except requests.exceptions.RequestException as exc:
            raise AIGenerationError("Could not reach the local Ollama service. Check that it is running.") from exc

        if response.status_code == 404:
            raise AIGenerationError(f"Ollama model '{model_name}' is not installed. Run: ollama pull {model_name}")
        if not response.ok:
            raise AIGenerationError(f"Ollama could not generate questions (HTTP {response.status_code}). Check its local service and model.")
        try:
            data = response.json()
            response_text = data["message"]["content"]
        except (ValueError, KeyError, TypeError) as exc:
            raise AIGenerationError("Ollama returned an unexpected response. Try again or choose another model.") from exc
        if not isinstance(response_text, str) or not response_text.strip():
            raise AIGenerationError("Ollama returned an empty response. Try again.")
        try:
            return parse_response(response_text)
        except OutputValidationError as exc:
            if attempt == 2:
                raise AIGenerationError(str(exc)) from exc
            messages.extend([
                {"role": "assistant", "content": response_text},
                {"role": "user", "content": (
                    f"Your previous answer failed validation: {exc}. Regenerate the complete JSON. "
                    "There must be exactly five entries under each of Easy, Medium, and Hard, and "
                    "all 15 questions must test different facts or reasoning. Do not repeat a question "
                    "or ask the same thing in different words. Follow the required JSON schema exactly."
                )},
            ])

