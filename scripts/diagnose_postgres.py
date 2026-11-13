import asyncio

import asyncpg
from sqlalchemy.engine import make_url

from app.core.config import get_settings


async def main() -> None:
    url = make_url(get_settings().database_url)

    connection = await asyncpg.connect(
        host=url.host,
        port=url.port or 5432,
        user=url.username,
        password=url.password,
        database="postgres",
    )

    try:
        server = await connection.fetchrow(
            """
            SELECT
                current_database(),
                inet_server_addr()::text AS server_ip,
                inet_server_port() AS server_port
            """
        )

        databases = await connection.fetch(
            "SELECT datname FROM pg_database ORDER BY datname"
        )

        print("Connected server:", dict(server))
        print("Available databases:", [row["datname"] for row in databases])

    finally:
        await connection.close()


if __name__ == "__main__":
    asyncio.run(main())