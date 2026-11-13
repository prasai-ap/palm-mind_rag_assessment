
import asyncio

from app.core.redis import redis_client, close_redis


async def check_connection() -> None:
    try:
        response = await redis_client.ping()

        print("Redis connection successful!")
        print("Ping response:", response)

    finally:
        await close_redis()


if __name__ == "__main__":
    asyncio.run(check_connection())
