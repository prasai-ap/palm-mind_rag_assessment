
import asyncio

from app.services.qdrant_service import (
    qdrant_client,
    close_qdrant,
)


async def check_connection() -> None:
    try:
        collections = await qdrant_client.get_collections()

        print("Qdrant connection successful!")
        print("Available collections:", collections.collections)

    finally:
        await close_qdrant()


if __name__ == "__main__":
    asyncio.run(check_connection())
