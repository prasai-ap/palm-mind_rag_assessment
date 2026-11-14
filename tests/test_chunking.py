
import pytest

from app.schemas.document import DocumentChunk
from app.services.chunking import chunk_document
from app.services.document_processor import ExtractedPage


@pytest.fixture
def sample_pages() -> list[ExtractedPage]:
    return [
        ExtractedPage(
            filename="research.pdf",
            page_number=1,
            text=(
                "Artificial intelligence is transforming healthcare. "
                "Machine learning helps doctors identify diseases. "
                "Deep learning improves medical image analysis. "
            ) * 10,
        ),
        ExtractedPage(
            filename="research.pdf",
            page_number=2,
            text=(
                "Natural language processing helps analyze medical records. "
                "Retrieval augmented generation provides contextual answers. "
            ) * 10,
        ),
    ]


def test_fixed_chunking_returns_chunks(
    sample_pages: list[ExtractedPage],
) -> None:
    chunks = chunk_document(
        pages=sample_pages,
        strategy="fixed",
        chunk_size=200,
        chunk_overlap=40,
    )

    assert len(chunks) > 0
    assert all(isinstance(chunk, DocumentChunk) for chunk in chunks)


def test_recursive_chunking_returns_chunks(
    sample_pages: list[ExtractedPage],
) -> None:
    chunks = chunk_document(
        pages=sample_pages,
        strategy="recursive",
        chunk_size=200,
        chunk_overlap=40,
    )

    assert len(chunks) > 0
    assert all(isinstance(chunk, DocumentChunk) for chunk in chunks)


def test_fixed_chunk_size_is_respected(
    sample_pages: list[ExtractedPage],
) -> None:
    chunks = chunk_document(
        pages=sample_pages,
        strategy="fixed",
        chunk_size=200,
        chunk_overlap=40,
    )

    assert all(len(chunk.text) <= 200 for chunk in chunks)


def test_recursive_chunk_size_is_respected(
    sample_pages: list[ExtractedPage],
) -> None:
    chunks = chunk_document(
        pages=sample_pages,
        strategy="recursive",
        chunk_size=200,
        chunk_overlap=40,
    )

    assert all(len(chunk.text) <= 200 for chunk in chunks)


def test_fixed_chunk_overlap(
    sample_pages: list[ExtractedPage],
) -> None:
    chunks = chunk_document(
        pages=[sample_pages[0]],
        strategy="fixed",
        chunk_size=200,
        chunk_overlap=40,
    )

    assert len(chunks) > 1

    assert chunks[0].text[-40:] == chunks[1].text[:40]


def test_chunk_metadata_is_preserved(
    sample_pages: list[ExtractedPage],
) -> None:
    chunks = chunk_document(
        pages=sample_pages,
        strategy="recursive",
        chunk_size=200,
        chunk_overlap=40,
    )

    assert all(chunk.filename == "research.pdf" for chunk in chunks)

    assert any(chunk.page_number == 1 for chunk in chunks)
    assert any(chunk.page_number == 2 for chunk in chunks)


def test_chunk_indexes_are_sequential(
    sample_pages: list[ExtractedPage],
) -> None:
    chunks = chunk_document(
        pages=sample_pages,
        strategy="recursive",
        chunk_size=200,
        chunk_overlap=40,
    )

    indexes = [chunk.chunk_index for chunk in chunks]

    assert indexes == list(range(len(chunks)))


def test_chunks_do_not_cross_page_boundaries(
    sample_pages: list[ExtractedPage],
) -> None:
    chunks = chunk_document(
        pages=sample_pages,
        strategy="recursive",
        chunk_size=200,
        chunk_overlap=40,
    )

    assert all(
        chunk.page_number in [1, 2]
        for chunk in chunks
    )


def test_empty_pages_return_empty_list() -> None:
    result = chunk_document(
        pages=[],
        strategy="fixed",
    )

    assert result == []


def test_invalid_chunk_size(
    sample_pages: list[ExtractedPage],
) -> None:
    with pytest.raises(ValueError, match="Chunk size"):
        chunk_document(
            pages=sample_pages,
            strategy="fixed",
            chunk_size=0,
        )


def test_negative_chunk_overlap(
    sample_pages: list[ExtractedPage],
) -> None:
    with pytest.raises(ValueError, match="Chunk overlap"):
        chunk_document(
            pages=sample_pages,
            strategy="fixed",
            chunk_size=200,
            chunk_overlap=-1,
        )


def test_overlap_greater_than_chunk_size(
    sample_pages: list[ExtractedPage],
) -> None:
    with pytest.raises(ValueError, match="smaller than chunk size"):
        chunk_document(
            pages=sample_pages,
            strategy="fixed",
            chunk_size=100,
            chunk_overlap=100,
        )


def test_unsupported_chunking_strategy(
    sample_pages: list[ExtractedPage],
) -> None:
    with pytest.raises(ValueError, match="Unsupported chunking strategy"):
        chunk_document(
            pages=sample_pages,
            strategy="invalid",  # type: ignore[arg-type]
        )
