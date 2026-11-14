
import asyncio

from app.services.document_processor import ExtractedPage
from app.services.chunking import chunk_document
from app.services.embedding_service import embed_texts
from app.services.qdrant_service import (
    qdrant_client,
    store_chunks,
    close_qdrant,
)
from app.core.config import get_settings

from qdrant_client import models

from uuid import uuid4

document_uuid = str(uuid4())

async def main() -> None:
    settings = get_settings()

    try:
        # 1. Prepare sample document content.
        pages = [
            ExtractedPage(
                filename="sample_healthcare.txt",
                page_number=1,
                text=(
                    "Artificial intelligence is transforming healthcare. "
                    "Machine learning helps doctors identify diseases. "
                    "Deep learning improves medical image analysis. "
                    "Natural language processing helps analyze medical records."
                ),
            )
        ]

        # 2. Split the document into chunks.
        chunks = chunk_document(
            pages=pages,
            strategy="recursive",
            chunk_size=100,
            chunk_overlap=20,
        )

        print("Chunks generated:", len(chunks))

        # 3. Generate embeddings.
        vectors = await embed_texts(
            texts=[chunk.text for chunk in chunks],
            task_type="RETRIEVAL_DOCUMENT",
        )

        print("Embeddings generated:", len(vectors))

        # 4. Store chunks and vectors in Qdrant.
        await store_chunks(
            chunks=chunks,
            vectors=vectors,
            document_uuid=document_uuid,
        )

        # 5. Verify stored points.
        result = await qdrant_client.scroll(
            collection_name=settings.qdrant_collection_name,
            scroll_filter=models.Filter(
                must=[
                    models.FieldCondition(
                        key="document_uuid",
                        match=models.MatchValue(value=document_uuid),
                    )
                ]
            ),
            limit=len(chunks),
            with_payload=True,
            with_vectors=False,
        )

        stored_points = result[0]

        print("\nStored points retrieved:", len(stored_points))

        for point in stored_points:
            print("\nPoint ID:", point.id)
            print("Document UUID:", point.payload.get("document_uuid"))
            print("Filename:", point.payload["filename"])
            print("Page:", point.payload["page_number"])
            print("Chunk index:", point.payload["chunk_index"])
            print("Text:", point.payload["text"])
            assert point.payload.get("document_uuid") == document_uuid
        
        assert len(stored_points) >= len(chunks)

        print("\nQdrant storage verification successful!")

    finally:
        await close_qdrant()


if __name__ == "__main__":
    asyncio.run(main())
