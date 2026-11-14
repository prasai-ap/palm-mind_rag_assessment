from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from fastapi import FastAPI
from sqlalchemy import text

from app.core.config import get_settings
from app.core.redis import redis_client, close_redis
from app.database.session import engine
from app.services.qdrant_service import (
    qdrant_client,
    close_qdrant,
)

from app.api.documents import router as documents_router
from app.api.conversation import router as conversation_router

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Manage application startup and shutdown."""

    # Startup: verify infrastructure connections.
    async with engine.connect() as connection:
        await connection.execute(text("SELECT 1"))

    await redis_client.ping()
    await qdrant_client.get_collections()

    print("PostgreSQL connected.")
    print("Redis connected.")
    print("Qdrant connected.")

    yield

    # Shutdown: close infrastructure connections.
    await engine.dispose()
    await close_redis()
    await close_qdrant()

    print("Infrastructure connections closed.")


app = FastAPI(
    title=settings.app_name,
    description="Document ingestion and conversational RAG API",
    version="1.0.0",
    debug=settings.debug,
    lifespan=lifespan,
)

app.include_router(documents_router)

app.include_router(conversation_router)

@app.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "healthy"}
