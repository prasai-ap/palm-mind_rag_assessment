import asyncio
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.database.models import Document
from app.repositories.document_repository import create_document


def run_async(coroutine):
    return asyncio.run(coroutine)


def create_mock_db():
    db = MagicMock()
    db.commit = AsyncMock()
    db.refresh = AsyncMock()
    db.rollback = AsyncMock()
    return db


def test_create_document_success():
    db = create_mock_db()

    document = run_async(
        create_document(
            db=db,
            document_uuid="123e4567-e89b-12d3-a456-426614174000",
            filename="sample.pdf",
            file_type=".pdf",
            pages_extracted=5,
            chunks_created=12,
            chunking_strategy="recursive",
        )
    )

    assert isinstance(document, Document)
    assert document.filename == "sample.pdf"
    assert document.file_type == ".pdf"
    assert document.pages_extracted == 5
    assert document.chunks_created == 12
    assert document.chunking_strategy == "recursive"

    db.add.assert_called_once_with(document)
    db.commit.assert_awaited_once()
    db.refresh.assert_awaited_once_with(document)
    db.rollback.assert_not_awaited()


def test_create_document_rejects_empty_uuid():
    db = create_mock_db()

    with pytest.raises(ValueError, match="Document UUID cannot be empty"):
        run_async(
            create_document(
                db=db,
                document_uuid=" ",
                filename="sample.pdf",
                file_type=".pdf",
                pages_extracted=5,
                chunks_created=12,
                chunking_strategy="recursive",
            )
        )

    db.add.assert_not_called()
    db.commit.assert_not_awaited()


def test_create_document_rejects_empty_filename():
    db = create_mock_db()

    with pytest.raises(ValueError, match="Filename cannot be empty"):
        run_async(
            create_document(
                db=db,
                document_uuid="123e4567-e89b-12d3-a456-426614174000",
                filename=" ",
                file_type=".pdf",
                pages_extracted=5,
                chunks_created=12,
                chunking_strategy="recursive",
            )
        )

    db.add.assert_not_called()


@pytest.mark.parametrize(
    "pages_extracted,chunks_created",
    [
        (0, 12),
        (-1, 12),
        (5, 0),
        (5, -1),
    ],
)
def test_create_document_rejects_invalid_counts(
    pages_extracted,
    chunks_created,
):
    db = create_mock_db()

    with pytest.raises(ValueError):
        run_async(
            create_document(
                db=db,
                document_uuid="123e4567-e89b-12d3-a456-426614174000",
                filename="sample.pdf",
                file_type=".pdf",
                pages_extracted=pages_extracted,
                chunks_created=chunks_created,
                chunking_strategy="recursive",
            )
        )

    db.add.assert_not_called()


def test_create_document_rolls_back_on_database_error():
    db = create_mock_db()
    db.commit.side_effect = RuntimeError("Database unavailable")

    with pytest.raises(RuntimeError, match="Database unavailable"):
        run_async(
            create_document(
                db=db,
                document_uuid="123e4567-e89b-12d3-a456-426614174000",
                filename="sample.pdf",
                file_type=".pdf",
                pages_extracted=5,
                chunks_created=12,
                chunking_strategy="recursive",
            )
        )

    db.rollback.assert_awaited_once()