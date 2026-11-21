import pytest

from src.prompt_builder import SYSTEM_PROMPT, build_prompt


def test_prompt_contains_report_and_requested_length():
    prompt = build_prompt("Uses Flask and SQLite", "Detailed")
    assert "Flask and SQLite" in prompt
    assert "3–5 concise sentences" in prompt
    assert "exactly 15" in prompt
    assert "Never invent" in SYSTEM_PROMPT


def test_invalid_answer_length_rejected():
    with pytest.raises(ValueError):
        build_prompt("report", "Long")

