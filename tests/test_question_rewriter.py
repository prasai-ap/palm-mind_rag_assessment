
import pytest

from app.services import question_rewriter


@pytest.mark.anyio
async def test_rewrite_without_history_returns_original_question(monkeypatch):
    async def unexpected_llm_call(prompt: str) -> str:
        raise AssertionError("LLM should not be called without history.")

    monkeypatch.setattr(
        question_rewriter,
        "generate_response",
        unexpected_llm_call,
    )

    result = await question_rewriter.rewrite_followup_question(
        question="What is machine learning?",
        history=[],
    )

    assert result == "What is machine learning?"


@pytest.mark.anyio
async def test_rewrite_followup_question(monkeypatch):
    async def mock_generate_response(prompt: str) -> str:
        assert "What is machine learning?" in prompt
        assert "What about its applications?" in prompt

        return "What are the applications of machine learning?"

    monkeypatch.setattr(
        question_rewriter,
        "generate_response",
        mock_generate_response,
    )

    history = [
        {
            "role": "user",
            "content": "What is machine learning?",
        },
        {
            "role": "assistant",
            "content": "Machine learning enables computers to learn from data.",
        },
    ]

    result = await question_rewriter.rewrite_followup_question(
        question="What about its applications?",
        history=history,
    )

    assert result == "What are the applications of machine learning?"


@pytest.mark.anyio
async def test_empty_question_is_rejected():
    with pytest.raises(ValueError, match="Question cannot be empty"):
        await question_rewriter.rewrite_followup_question(
            question="   ",
            history=[],
        )


@pytest.mark.anyio
async def test_empty_llm_response_is_rejected(monkeypatch):
    async def mock_generate_response(prompt: str) -> str:
        return "   "

    monkeypatch.setattr(
        question_rewriter,
        "generate_response",
        mock_generate_response,
    )

    with pytest.raises(RuntimeError, match="empty response"):
        await question_rewriter.rewrite_followup_question(
            question="What about its applications?",
            history=[
                {"role": "user", "content": "What is machine learning?"}
            ],
        )
