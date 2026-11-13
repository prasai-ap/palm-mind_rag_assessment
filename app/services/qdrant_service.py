
from qdrant_client import AsyncQdrantClient

from app.core.config import get_settings


settings = get_settings()

qdrant_client = AsyncQdrantClient(
    url=settings.qdrant_url,
)


async def close_qdrant() -> None:
    """Close the Qdrant client connection."""
    await qdrant_client.close()
