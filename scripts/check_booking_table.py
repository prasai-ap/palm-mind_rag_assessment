import asyncio

from sqlalchemy import text

from app.database.session import engine


async def main() -> None:
    async with engine.connect() as connection:
        result = await connection.execute(
            text("""
                SELECT column_name
                FROM information_schema.columns
                WHERE table_name = 'interview_bookings'
                ORDER BY ordinal_position
            """)
        )

        for row in result:
            print(row.column_name)

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())