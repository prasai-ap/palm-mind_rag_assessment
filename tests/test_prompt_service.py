
import pytest

from app.schemas.retrieval import RetrievedChunk
from app.services.prompt_service import build_rag_prompt


@pytest.fixture
def sample_chunks() -> list[RetrievedChunk]:
    return [
        RetrievedChunk(
            filename="healthcare.pdf",
            page_number=1,
            chunk_index=0,
            text="Machine learning helps doctors identify diseases.",
            score=0.89,
        ),
        RetrievedChunk(
            filename="healthcare.pdf",
            page_number=2,
            chunk_index=1,
            text="Deep learning improves medical image analysis.",
            score=0.85,
        ),
    ]


def test_prompt_contains_user_question(
    sample_chunks: list[RetrievedChunk],
) -> None:
    question = "How does machine learning help doctors?"

    prompt = build_rag_prompt(question, sample_chunks)

    assert question in prompt


def test_prompt_contains_retrieved_context(
    sample_chunks: list[RetrievedChunk],
) -> None:
    prompt = build_rag_prompt(
        "How does AI help healthcare?",
        sample_chunks,
    )

    assert "Machine learning helps doctors identify diseases." in prompt
    assert "Deep learning improves medical image analysis." in prompt


def test_prompt_preserves_source_metadata(
    sample_chunks: list[RetrievedChunk],
) -> None:
    prompt = build_rag_prompt(
        "Explain machine learning.",
        sample_chunks,
    )

    assert "healthcare.pdf" in prompt
    assert "Page: 1" in prompt
    assert "Page: 2" in prompt


def test_prompt_contains_grounding_instructions(
    sample_chunks: list[RetrievedChunk],
) -> None:
    prompt = build_rag_prompt(
        "Explain machine learning.",
        sample_chunks,
    )

    assert "using only the supplied context" in prompt
    assert "cannot answer" in prompt
    assert "untrusted data" in prompt


def test_prompt_handles_no_retrieved_chunks() -> None:
    prompt = build_rag_prompt(
        "What is quantum computing?",
        [],
    )

    assert "No relevant document context was retrieved." in prompt


def test_empty_question_raises_error(
    sample_chunks: list[RetrievedChunk],
) -> None:
    with pytest.raises(ValueError, match="Question cannot be empty"):
        build_rag_prompt("   ", sample_chunks)
