
from math import sqrt
from typing import Literal

from google import genai
from google.genai import types

from app.core.config import get_settings


EmbeddingTask = Literal["RETRIEVAL_DOCUMENT", "RETRIEVAL_QUERY"]

settings = get_settings()

_client: genai.Client | None = None


def _get_client() -> genai.Client:
    """Return a reusable Gemini API client."""

    global _client

    if _client is None:
        if settings.gemini_api_key is None:
            raise RuntimeError("GEMINI_API_KEY is not configured.")

        api_key = settings.gemini_api_key.get_secret_value().strip()

        if not api_key:
            raise RuntimeError("GEMINI_API_KEY is empty.")

        _client = genai.Client(api_key=api_key)

    return _client


def _normalize_vector(vector: list[float]) -> list[float]:
    """Normalize an embedding vector to unit length."""

    magnitude = sqrt(sum(value * value for value in vector))

    if magnitude == 0:
        raise ValueError("Cannot normalize a zero-magnitude vector.")

    return [value / magnitude for value in vector]


async def embed_texts(
    texts: list[str],
    task_type: EmbeddingTask,
) -> list[list[float]]:
    """
    Generate normalized embeddings for multiple text inputs.

    Args:
        texts: Texts to convert into embedding vectors.
        task_type: RETRIEVAL_DOCUMENT or RETRIEVAL_QUERY.

    Returns:
        A list of normalized embedding vectors.

    Raises:
        ValueError: If the input is empty or contains blank text.
        RuntimeError: If the Gemini API request fails or returns
            unexpected embedding data.
    """

    if not texts:
        raise ValueError("At least one text is required.")

    if any(not text.strip() for text in texts):
        raise ValueError("Input texts cannot be empty or whitespace only.")

    client = _get_client()

    try:
        response = await client.aio.models.embed_content(
            model=settings.embedding_model,
            contents=texts,
            config=types.EmbedContentConfig(
                task_type=task_type,
                output_dimensionality=settings.embedding_dimension,
            ),
        )

    except Exception as exc:
        raise RuntimeError(
            "Failed to generate embeddings using Gemini."
        ) from exc

    if not response.embeddings:
        raise RuntimeError("Gemini returned no embeddings.")

    if len(response.embeddings) != len(texts):
        raise RuntimeError(
            "The number of returned embeddings does not match "
            "the number of input texts."
        )

    vectors: list[list[float]] = []

    for embedding in response.embeddings:
        if not embedding.values:
            raise RuntimeError("Gemini returned an empty embedding vector.")

        vector = list(embedding.values)

        if len(vector) != settings.embedding_dimension:
            raise RuntimeError(
                f"Expected {settings.embedding_dimension} dimensions, "
                f"but received {len(vector)}."
            )

        vectors.append(_normalize_vector(vector))

    return vectors
