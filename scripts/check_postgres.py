
import asyncio

from sqlalchemy import text

from app.database.session import engine


async def check_connection() -> None:
    try:
        async with engine.connect() as connection:
            result = await connection.execute(text("SELECT 1"))
            print("PostgreSQL connection successful!")
            print("Query result:", result.scalar_one())

    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(check_connection())
