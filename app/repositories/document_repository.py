from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import Document
from app.schemas.document import ChunkingStrategy


async def create_document(
    db: AsyncSession,
    document_uuid: str,
    filename: str,
    file_type: str,
    pages_extracted: int,
    chunks_created: int,
    chunking_strategy: ChunkingStrategy,
) -> Document:
    if not document_uuid.strip():
        raise ValueError("Document UUID cannot be empty.")

    if not filename.strip():
        raise ValueError("Filename cannot be empty.")

    if pages_extracted <= 0:
        raise ValueError("Pages extracted must be greater than zero.")

    if chunks_created <= 0:
        raise ValueError("Chunks created must be greater than zero.")

    new_document = Document(
        document_uuid=document_uuid,
        filename=filename,
        file_type=file_type,
        pages_extracted=pages_extracted,
        chunks_created=chunks_created,
        chunking_strategy=chunking_strategy,
    )

    try:
        db.add(new_document)
        await db.commit()
        await db.refresh(new_document)
    except Exception:
        await db.rollback()
        raise

    return new_document