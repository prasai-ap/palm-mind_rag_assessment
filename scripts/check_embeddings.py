
import asyncio
from math import sqrt

from app.services.embedding_service import embed_texts
from app.core.config import get_settings


async def main() -> None:
    settings = get_settings()

    # Test document embeddings.
    documents = [
        "Artificial intelligence is transforming healthcare.",
        "Machine learning helps doctors identify diseases.",
    ]

    document_vectors = await embed_texts(
        texts=documents,
        task_type="RETRIEVAL_DOCUMENT",
    )

    print("Document embedding test successful!")
    print("Number of vectors:", len(document_vectors))

    for index, vector in enumerate(document_vectors):
        magnitude = sqrt(sum(value * value for value in vector))

        print(f"\nVector {index + 1}:")
        print("Dimensions:", len(vector))
        print("Magnitude:", round(magnitude, 6))

        assert len(vector) == settings.embedding_dimension
        assert abs(magnitude - 1.0) < 0.0001

    # Test query embedding.
    query_vectors = await embed_texts(
        texts=["How is machine learning used in healthcare?"],
        task_type="RETRIEVAL_QUERY",
    )

    query_vector = query_vectors[0]

    print("\nQuery embedding test successful!")
    print("Query dimensions:", len(query_vector))

    assert len(query_vector) == settings.embedding_dimension

    print("\nAll embedding checks passed!")


if __name__ == "__main__":
    asyncio.run(main())
