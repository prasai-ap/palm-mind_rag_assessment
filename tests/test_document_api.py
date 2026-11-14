
from unittest.mock import AsyncMock, Mock

from fastapi.testclient import TestClient

from app.main import app
from app.database.session import get_db


client = TestClient(app)


async def override_get_db():
    yield None


app.dependency_overrides[get_db] = override_get_db


def mock_document_pipeline(monkeypatch):
    async def mock_embed_texts(**kwargs):
        return [[0.1] * 768]

    async def mock_store_chunks(**kwargs):
        return None

    async def mock_create_document(**kwargs):
        return None

    async def mock_delete_document_chunks(**kwargs):
        return None

    monkeypatch.setattr(
        "app.api.documents.extract_document",
        lambda **kwargs: [
            type(
                "Page",
                (),
                {
                    "filename": "sample.txt",
                    "page_number": 1,
                    "text": "Sample document content.",
                },
            )()
        ],
    )

    monkeypatch.setattr(
        "app.api.documents.chunk_document",
        lambda **kwargs: [
            type(
                "Chunk",
                (),
                {
                    "filename": "sample.txt",
                    "page_number": 1,
                    "chunk_index": 0,
                    "text": "Sample document content.",
                },
            )()
        ],
    )

    monkeypatch.setattr(
        "app.api.documents.embed_texts",
        mock_embed_texts,
    )
    monkeypatch.setattr(
        "app.api.documents.store_chunks",
        mock_store_chunks,
    )
    monkeypatch.setattr(
        "app.api.documents.create_document",
        mock_create_document,
    )
    monkeypatch.setattr(
        "app.api.documents.delete_document_chunks",
        mock_delete_document_chunks,
    )


def test_upload_document_success(monkeypatch):
    mock_document_pipeline(monkeypatch)

    response = client.post(
        "/documents/upload",
        files={
            "file": (
                "sample.txt",
                b"Sample document content.",
                "text/plain",
            )
        },
        data={"strategy": "recursive"},
    )

    assert response.status_code == 200

    data = response.json()

    assert data["filename"] == "sample.txt"
    assert data["pages_extracted"] == 1
    assert data["chunks_created"] == 1
    assert data["vectors_stored"] == 1
    assert data["chunking_strategy"] == "recursive"
    assert data["document_uuid"]


def test_upload_document_rejects_unsupported_file(monkeypatch):
    mock_document_pipeline(monkeypatch)

    def mock_extract_document(**kwargs):
        raise ValueError("Unsupported file type: .docx")

    monkeypatch.setattr(
        "app.api.documents.extract_document",
        mock_extract_document,
    )

    response = client.post(
        "/documents/upload",
        files={
            "file": (
                "sample.docx",
                b"Unsupported content",
                "application/octet-stream",
            )
        },
        data={"strategy": "recursive"},
    )

    assert response.status_code == 400
    assert "Unsupported file type" in response.json()["detail"]


def test_upload_document_embedding_failure(monkeypatch):
    mock_document_pipeline(monkeypatch)

    async def mock_embed_failure(**kwargs):
        raise RuntimeError("Gemini embedding service unavailable.")

    monkeypatch.setattr(
        "app.api.documents.embed_texts",
        mock_embed_failure,
    )

    response = client.post(
        "/documents/upload",
        files={
            "file": (
                "sample.txt",
                b"Sample document content.",
                "text/plain",
            )
        },
        data={"strategy": "recursive"},
    )

    assert response.status_code == 502
    assert "Gemini embedding service unavailable" in response.json()["detail"]


def test_upload_document_metadata_failure_cleans_qdrant(monkeypatch):
    mock_document_pipeline(monkeypatch)

    mock_cleanup = AsyncMock()

    async def mock_create_document_failure(**kwargs):
        raise RuntimeError("PostgreSQL unavailable.")

    monkeypatch.setattr(
        "app.api.documents.create_document",
        mock_create_document_failure,
    )

    monkeypatch.setattr(
        "app.api.documents.delete_document_chunks",
        mock_cleanup,
    )

    response = client.post(
        "/documents/upload",
        files={
            "file": (
                "sample.txt",
                b"Sample document content.",
                "text/plain",
            )
        },
        data={"strategy": "recursive"},
    )

    assert response.status_code == 500
    assert "Qdrant chunks were cleaned up" in response.json()["detail"]

    mock_cleanup.assert_awaited_once()

    cleanup_uuid = mock_cleanup.await_args.args[0]
    assert cleanup_uuid


def test_upload_document_cleanup_failure(monkeypatch):
    mock_document_pipeline(monkeypatch)

    async def mock_create_document_failure(**kwargs):
        raise RuntimeError("PostgreSQL unavailable.")

    async def mock_cleanup_failure(**kwargs):
        raise RuntimeError("Qdrant unavailable.")

    monkeypatch.setattr(
        "app.api.documents.create_document",
        mock_create_document_failure,
    )

    monkeypatch.setattr(
        "app.api.documents.delete_document_chunks",
        mock_cleanup_failure,
    )

    response = client.post(
        "/documents/upload",
        files={
            "file": (
                "sample.txt",
                b"Sample document content.",
                "text/plain",
            )
        },
        data={"strategy": "recursive"},
    )

    assert response.status_code == 500
    assert "Qdrant cleanup also failed" in response.json()["detail"]


def test_upload_document_rejects_oversized_file(monkeypatch):
    mock_document_pipeline(monkeypatch)

    mock_extract = Mock()
    mock_embed = AsyncMock()
    mock_store = AsyncMock()

    monkeypatch.setattr(
        "app.api.documents.extract_document",
        mock_extract,
    )
    monkeypatch.setattr(
        "app.api.documents.embed_texts",
        mock_embed,
    )
    monkeypatch.setattr(
        "app.api.documents.store_chunks",
        mock_store,
    )

    oversized_content = b"a" * (10 * 1024 * 1024 + 1)

    response = client.post(
        "/documents/upload",
        files={
            "file": (
                "large.txt",
                oversized_content,
                "text/plain",
            )
        },
        data={"strategy": "recursive"},
    )

    assert response.status_code == 413
    assert "10 MB" in response.json()["detail"]

    mock_extract.assert_not_called()
    mock_embed.assert_not_awaited()
    mock_store.assert_not_awaited()
