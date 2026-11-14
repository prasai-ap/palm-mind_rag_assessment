import asyncio
from unittest.mock import AsyncMock

import pytest
from qdrant_client import models

from app.services import qdrant_service


def test_delete_document_chunks():
    document_uuid = "088df054-6b5a-475d-bd9b-a9a21384655c"

    original_delete = qdrant_service.qdrant_client.delete
    mock_delete = AsyncMock()
    qdrant_service.qdrant_client.delete = mock_delete

    try:
        asyncio.run(
            qdrant_service.delete_document_chunks(document_uuid)
        )

        mock_delete.assert_awaited_once()

        call_kwargs = mock_delete.await_args.kwargs

        assert call_kwargs["collection_name"] == (
            qdrant_service.settings.qdrant_collection_name
        )
        assert call_kwargs["wait"] is True

        selector = call_kwargs["points_selector"]
        assert isinstance(selector, models.FilterSelector)

        condition = selector.filter.must[0]
        assert condition.key == "document_uuid"
        assert condition.match.value == document_uuid

    finally:
        qdrant_service.qdrant_client.delete = original_delete


def test_delete_document_chunks_rejects_empty_uuid():
    with pytest.raises(
        ValueError,
        match="Document UUID cannot be empty",
    ):
        asyncio.run(
            qdrant_service.delete_document_chunks(" ")
        )