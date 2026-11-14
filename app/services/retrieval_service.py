from app.core.config import get_settings
from app.schemas.retrieval import RetrievedChunk
from app.services.embedding_service import embed_texts
from app.services.qdrant_service import qdrant_client


settings = get_settings()


async def retrieve_relevant_chunks(
    query: str,
    limit: int = 5,
    score_threshold: float | None = None,
) -> list[RetrievedChunk]:
    """
    Retrieve the most relevant document chunks for a user query.

    Args:
        query: User's search question.
        limit: Maximum number of chunks to retrieve.
        score_threshold: Optional minimum similarity score.

    Returns:
        Relevant document chunks ordered by similarity.
    """

    if not query.strip():
        raise ValueError("Search query cannot be empty.")

    if limit <= 0:
        raise ValueError("Retrieval limit must be greater than zero.")

    # 1. Convert the user question into an embedding.
    query_vectors = await embed_texts(
        texts=[query],
        task_type="RETRIEVAL_QUERY",
    )

    query_vector = query_vectors[0]

    # 2. Search Qdrant using the query embedding.
    search_result = await qdrant_client.query_points(
        collection_name=settings.qdrant_collection_name,
        query=query_vector,
        limit=limit,
        with_payload=True,
        score_threshold=score_threshold,
    )

    # 3. Convert Qdrant results into application schemas.
    retrieved_chunks: list[RetrievedChunk] = []

    for point in search_result.points:
        payload = point.payload or {}

        retrieved_chunks.append(
            RetrievedChunk(
                filename=payload["filename"],
                page_number=payload["page_number"],
                chunk_index=payload["chunk_index"],
                text=payload["text"],
                score=point.score,
            )
        )

    return retrieved_chunks
