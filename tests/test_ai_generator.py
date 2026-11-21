import json

import pytest
import requests

import src.ai_generator as generator
from src.ai_generator import AIGenerationError, generate_questions
from tests.test_output_parser import valid_data


class LocalResponse:
    status_code = 200
    ok = True

    @staticmethod
    def json():
        return {"message": {"content": json.dumps(valid_data())}}


def test_ollama_provider_uses_local_api_and_validates_response(monkeypatch):
    calls = {}

    def fake_post(url, **kwargs):
        calls["url"] = url
        calls["body"] = kwargs["json"]
        return LocalResponse()

    monkeypatch.setattr(generator.requests, "post", fake_post)
    result = generate_questions("report", model="test-model")
    assert len(result["questions"]) == 15
    assert calls["url"] == "http://localhost:11434/api/chat"
    assert calls["body"]["stream"] is False
    assert calls["body"]["model"] == "test-model"
    assert calls["body"]["format"]["type"] == "object"


def test_ollama_missing_service_is_friendly(monkeypatch):
    def offline(*args, **kwargs):
        raise requests.exceptions.ConnectionError("localhost unavailable")

    monkeypatch.setattr(generator.requests, "post", offline)
    with pytest.raises(AIGenerationError, match="Ollama is not running"):
        generate_questions("report")


def test_missing_ollama_model_is_actionable(monkeypatch):
    class MissingModelResponse:
        status_code = 404
        ok = False

    monkeypatch.setattr(generator.requests, "post", lambda *args, **kwargs: MissingModelResponse())
    with pytest.raises(AIGenerationError, match="ollama pull missing-model"):
        generate_questions("report", model="missing-model")


def test_local_timeout_is_friendly(monkeypatch):
    def timeout(*args, **kwargs):
        raise requests.exceptions.Timeout("slow local response")

    monkeypatch.setattr(generator.requests, "post", timeout)
    with pytest.raises(AIGenerationError, match="local model took too long"):
        generate_questions("report")


def test_ollama_retries_invalid_duplicate_questions(monkeypatch):
    class DuplicateResponse:
        status_code = 200
        ok = True

        @staticmethod
        def json():
            data = valid_data()
            data["questions"][1]["question"] = data["questions"][0]["question"]
            return {"message": {"content": json.dumps(data)}}

    class ValidResponse(LocalResponse):
        pass

    responses = [DuplicateResponse(), ValidResponse()]
    request_bodies = []

    def fake_post(url, **kwargs):
        request_bodies.append(kwargs["json"])
        return responses.pop(0)

    monkeypatch.setattr(generator.requests, "post", fake_post)
    result = generate_questions("report")
    assert len(result["questions"]) == 15
    assert len(request_bodies) == 2
    assert "failed validation" in request_bodies[1]["messages"][-1]["content"]

