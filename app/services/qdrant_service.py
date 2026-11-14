from uuid import uuid4

from qdrant_client import AsyncQdrantClient, models

from app.core.config import get_settings
from app.schemas.document import DocumentChunk


settings = get_settings()

qdrant_client = AsyncQdrantClient(
    url=settings.qdrant_url,
)


async def create_collection() -> None:
    """Create the document collection if it does not already exist."""

    collection_name = settings.qdrant_collection_name

    exists = await qdrant_client.collection_exists(
        collection_name=collection_name
    )

    if exists:
        print(f"Qdrant collection '{collection_name}' already exists.")
        return

    await qdrant_client.create_collection(
        collection_name=collection_name,
        vectors_config=models.VectorParams(
            size=settings.embedding_dimension,
            distance=models.Distance.COSINE,
        ),
    )

    print(f"Qdrant collection '{collection_name}' created.")


async def store_chunks(
    chunks: list[DocumentChunk],
    vectors: list[list[float]],
    document_uuid:str,
) -> None:
    """
    Store document chunks and their corresponding vectors in Qdrant.

    Each vector is stored with its original document metadata.
    """
    if not document_uuid.strip():
        raise ValueError("Document UUID cannot be empty.")
    
    if not chunks:
        raise ValueError("At least one document chunk is required.")

    if len(chunks) != len(vectors):
        raise ValueError(
            "The number of chunks must match the number of vectors."
        )

    for vector in vectors:
        if len(vector) != settings.embedding_dimension:
            raise ValueError(
                f"Expected vector dimension "
                f"{settings.embedding_dimension}, "
                f"received {len(vector)}."
            )

    await create_collection()

    points = []

    for chunk, vector in zip(chunks, vectors):
        points.append(
            models.PointStruct(
                id=str(uuid4()),
                vector=vector,
                payload={
                    "document_uuid": document_uuid,
                    "filename": chunk.filename,
                    "page_number": chunk.page_number,
                    "chunk_index": chunk.chunk_index,
                    "text": chunk.text,
                },
            )
        )

    await qdrant_client.upsert(
        collection_name=settings.qdrant_collection_name,
        points=points,
        wait=True,
    )

    print(f"Successfully stored {len(points)} chunks in Qdrant.")

async def delete_document_chunks(document_uuid: str) -> None:
    if not document_uuid.strip():
        raise ValueError("Document UUID cannot be empty.")

    await qdrant_client.delete(
        collection_name=settings.qdrant_collection_name,
        points_selector=models.FilterSelector(
            filter=models.Filter(
                must=[
                    models.FieldCondition(
                        key="document_uuid",
                        match=models.MatchValue(value=document_uuid),
                    )
                ]
            )
        ),
        wait=True,
    )

    print(f"Deleted Qdrant chunks for document: {document_uuid}")

async def close_qdrant() -> None:
    """Close the Qdrant client connection."""

    await qdrant_client.close()
