from __future__ import annotations

from src.llm import SYSTEM_PROMPT, generate_answer, is_available


def test_system_prompt_forbids_invention():
    lowered = SYSTEM_PROMPT.lower()
    assert "only" in lowered
    assert "invent" in lowered
    assert "not found" in lowered or "does not contain" in lowered


def test_generate_answer_without_key(monkeypatch):
    monkeypatch.setattr("src.llm.is_available", lambda: False)
    monkeypatch.setattr("src.llm.llm_is_configured", lambda: False)
    assert is_available() is False
    try:
        generate_answer("question", "context")
        raised = False
    except Exception as exc:
        raised = True
        assert "API key" in str(exc)
    assert raised
