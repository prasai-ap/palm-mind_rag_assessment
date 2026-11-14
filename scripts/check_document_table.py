import asyncio

from sqlalchemy import text

from app.database.session import engine


async def main() -> None:
    async with engine.connect() as connection:
        result = await connection.execute(
            text("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns
                WHERE table_name = 'documents'
                ORDER BY ordinal_position;
            """)
        )

        for row in result:
            print(row)

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())