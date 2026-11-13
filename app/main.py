
from fastapi import FastAPI

from app.core.config import get_settings

settings = get_settings()

app = FastAPI(
    title="Palm Mind RAG API",
    description="Document ingestion and conversational RAG backend",
    version="0.1.0",
)


@app.get("/health")
async def health_check() -> dict[str, str]:
    return {
        "status": "healthy",
        "application": "Palm Mind RAG API",
    }
