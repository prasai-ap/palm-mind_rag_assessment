
import asyncio

import pytest

from app.schemas.retrieval import RetrievedChunk
from app.services import rag_service


@pytest.fixture
def sample_chunks() -> list[RetrievedChunk]:
    return [
        RetrievedChunk(
            filename="healthcare.pdf",
            page_number=1,
            chunk_index=0,
            text="Machine learning helps doctors identify diseases.",
            score=0.89,
        )
    ]


def test_successful_rag_pipeline(
    monkeypatch: pytest.MonkeyPatch,
    sample_chunks: list[RetrievedChunk],
) -> None:
    async def mock_retrieve(
        query: str,
        limit: int,
    ) -> list[RetrievedChunk]:
        return sample_chunks

    def mock_build_prompt(
        question: str,
        retrieved_chunks: list[RetrievedChunk],
        conversation_history: list[dict[str, str]] | None = None,
        ) -> str:
            return "Test prompt"

    async def mock_generate(prompt: str) -> str:
        return "Machine learning helps doctors identify diseases."

    monkeypatch.setattr(
        rag_service,
        "retrieve_relevant_chunks",
        mock_retrieve,
    )
    monkeypatch.setattr(
        rag_service,
        "build_rag_prompt",
        mock_build_prompt,
    )
    monkeypatch.setattr(
        rag_service,
        "generate_response",
        mock_generate,
    )

    answer = asyncio.run(
        rag_service.answer_question(
            question="How does machine learning help doctors?",
            limit=3,
        )
    )

    assert answer == "Machine learning helps doctors identify diseases."


def test_no_relevant_chunks_does_not_call_llm(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def mock_retrieve(
        query: str,
        limit: int,
    ) -> list[RetrievedChunk]:
        return []

    async def mock_generate(prompt: str) -> str:
        pytest.fail("LLM should not be called when no chunks are retrieved.")

    monkeypatch.setattr(
        rag_service,
        "retrieve_relevant_chunks",
        mock_retrieve,
    )
    monkeypatch.setattr(
        rag_service,
        "generate_response",
        mock_generate,
    )

    answer = asyncio.run(
        rag_service.answer_question(
            question="What is quantum computing?"
        )
    )

    assert "couldn't find relevant information" in answer


def test_empty_question_raises_error() -> None:
    with pytest.raises(ValueError, match="Question cannot be empty"):
        asyncio.run(
            rag_service.answer_question(question="   ")
        )


def test_invalid_retrieval_limit_raises_error() -> None:
    with pytest.raises(
        ValueError,
        match="Retrieval limit must be greater than zero",
    ):
        asyncio.run(
            rag_service.answer_question(
                question="Explain machine learning.",
                limit=0,
            )
        )

@pytest.mark.anyio
async def test_answer_question_uses_rewritten_question(monkeypatch):
    retrieved_queries = []

    async def mock_rewrite(question, history):
        return "What are the applications of machine learning?"

    async def mock_retrieve(query, limit):
        retrieved_queries.append(query)
        return [
            RetrievedChunk(
                filename="healthcare.pdf",
                page_number=1,
                chunk_index=0,
                text="Machine learning helps doctors identify diseases.",
                score=0.9,
            )
        ]

    def mock_build_prompt(question, retrieved_chunks, conversation_history):
        assert question == "What about its applications?"
        assert conversation_history is not None
        return "Test prompt"

    async def mock_generate_response(prompt):
        return "It helps doctors identify diseases."

    monkeypatch.setattr(
        rag_service, "rewrite_followup_question", mock_rewrite
    )
    monkeypatch.setattr(
        rag_service, "retrieve_relevant_chunks", mock_retrieve
    )
    monkeypatch.setattr(
        rag_service, "build_rag_prompt", mock_build_prompt
    )
    monkeypatch.setattr(
        rag_service, "generate_response", mock_generate_response
    )

    history = [
        {"role": "user", "content": "What is machine learning?"},
        {
            "role": "assistant",
            "content": "It enables computers to learn from data.",
        },
    ]

    answer = await rag_service.answer_question(
        question="What about its applications?",
        conversation_history=history,
    )

    assert retrieved_queries == [
        "What are the applications of machine learning?"
    ]
    assert answer == "It helps doctors identify diseases."


@pytest.mark.anyio
async def test_answer_question_passes_history_to_prompt(monkeypatch):
    captured_history = None

    async def mock_rewrite(question, history):
        return question

    async def mock_retrieve(query, limit):
        return [
            RetrievedChunk(
                filename="healthcare.pdf",
                page_number=1,
                chunk_index=0,
                text="Machine learning helps doctors identify diseases.",
                score=0.9,
            )
        ]

    def mock_build_prompt(question, retrieved_chunks, conversation_history):
        nonlocal captured_history
        captured_history = conversation_history
        return "Test prompt"

    async def mock_generate_response(prompt):
        return "Test answer"

    monkeypatch.setattr(
        rag_service, "rewrite_followup_question", mock_rewrite
    )
    monkeypatch.setattr(
        rag_service, "retrieve_relevant_chunks", mock_retrieve
    )
    monkeypatch.setattr(
        rag_service, "build_rag_prompt", mock_build_prompt
    )
    monkeypatch.setattr(
        rag_service, "generate_response", mock_generate_response
    )

    history = [
        {"role": "user", "content": "What is machine learning?"}
    ]

    await rag_service.answer_question(
        question="Explain it.",
        conversation_history=history,
    )

    assert captured_history == history
