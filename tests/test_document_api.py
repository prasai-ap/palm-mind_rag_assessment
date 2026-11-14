
from fastapi.testclient import TestClient

from app.main import app
from app.api import documents as document_api
from app.services.document_processor import ExtractedPage
from app.schemas.document import DocumentChunk


client = TestClient(app)


def test_successful_document_upload(
    monkeypatch,
) -> None:
    # Mock document extraction.
    def mock_extract_document(
        file_content: bytes,
        filename: str,
    ) -> list[ExtractedPage]:
        return [
            ExtractedPage(
                filename=filename,
                page_number=None,
                text="Machine learning helps doctors identify diseases.",
            )
        ]

    # Mock chunking.
    def mock_chunk_document(
        pages: list[ExtractedPage],
        strategy: str,
    ) -> list[DocumentChunk]:
        return [
            DocumentChunk(
                filename="sample.txt",
                page_number=None,
                chunk_index=0,
                text="Machine learning helps doctors identify diseases.",
            )
        ]

    # Mock embedding generation.
    async def mock_embed_texts(
        texts: list[str],
        task_type: str,
    ) -> list[list[float]]:
        return [[0.1] * 768]

    # Mock Qdrant storage.
    async def mock_store_chunks(
        chunks: list[DocumentChunk],
        vectors: list[list[float]],
    ) -> None:
        assert len(chunks) == len(vectors)

    monkeypatch.setattr(
        document_api,
        "extract_document",
        mock_extract_document,
    )
    monkeypatch.setattr(
        document_api,
        "chunk_document",
        mock_chunk_document,
    )
    monkeypatch.setattr(
        document_api,
        "embed_texts",
        mock_embed_texts,
    )
    monkeypatch.setattr(
        document_api,
        "store_chunks",
        mock_store_chunks,
    )

    response = client.post(
        "/documents/upload",
        files={
            "file": (
                "sample.txt",
                b"Machine learning helps doctors identify diseases.",
                "text/plain",
            )
        },
        data={"strategy": "recursive"},
    )

    assert response.status_code == 200

    result = response.json()

    assert result["filename"] == "sample.txt"
    assert result["pages_extracted"] == 1
    assert result["chunks_created"] == 1
    assert result["vectors_stored"] == 1
    assert result["chunking_strategy"] == "recursive"


def test_empty_document_upload() -> None:
    response = client.post(
        "/documents/upload",
        files={
            "file": ("empty.txt", b"", "text/plain")
        },
    )

    assert response.status_code == 400
    assert "empty" in response.json()["detail"].lower()


def test_unsupported_file_type() -> None:
    response = client.post(
        "/documents/upload",
        files={
            "file": ("sample.docx", b"some content", "application/octet-stream")
        },
    )

    assert response.status_code == 400
    assert "Unsupported file type" in response.json()["detail"]


def test_invalid_chunking_strategy() -> None:
    response = client.post(
        "/documents/upload",
        files={
            "file": ("sample.txt", b"Some content", "text/plain")
        },
        data={"strategy": "invalid"},
    )

    assert response.status_code == 422
