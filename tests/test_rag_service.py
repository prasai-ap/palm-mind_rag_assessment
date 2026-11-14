
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
