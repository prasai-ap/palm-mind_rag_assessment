import asyncio

from qdrant_client import models
from sqlalchemy import select

from app.core.config import get_settings
from app.database.models import Document
from app.database.session import AsyncSessionLocal, engine
from app.services.qdrant_service import qdrant_client


DOCUMENT_UUID = "32f34386-b403-465d-af88-0cd0db0c1e53"


async def main() -> None:
    settings = get_settings()

    try:
        # Verify PostgreSQL metadata.
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(Document).where(
                    Document.document_uuid == DOCUMENT_UUID
                )
            )
            document = result.scalar_one_or_none()

        if document is None:
            print("PostgreSQL: Document not found.")
        else:
            print("PostgreSQL: Document found.")
            print(f"Filename: {document.filename}")
            print(f"Pages: {document.pages_extracted}")
            print(f"Chunks: {document.chunks_created}")
            print(f"Strategy: {document.chunking_strategy}")

        # Verify Qdrant vectors belonging to this document.
        points, _ = await qdrant_client.scroll(
            collection_name=settings.qdrant_collection_name,
            scroll_filter=models.Filter(
                must=[
                    models.FieldCondition(
                        key="document_uuid",
                        match=models.MatchValue(value=DOCUMENT_UUID),
                    )
                ]
            ),
            limit=100,
            with_payload=True,
            with_vectors=False,
        )

        print(f"\nQdrant: Found {len(points)} points.")

        for point in points[:3]:
            print(
                f"Chunk index: {point.payload['chunk_index']}, "
                f"Filename: {point.payload['filename']}"
            )

        if document is not None and len(points) == document.chunks_created:
            print("\nSUCCESS: PostgreSQL metadata and Qdrant chunks match.")
        else:
            print("\nVERIFICATION FAILED: Check the results above.")

    finally:
        await engine.dispose()
        await qdrant_client.close()


if __name__ == "__main__":
    asyncio.run(main())
