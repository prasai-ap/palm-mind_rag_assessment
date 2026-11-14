import logging
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.repositories.document_repository import create_document
from app.schemas.document import ChunkingStrategy, DocumentUploadResponse
from app.services.document_processor import extract_document
from app.services.chunking import chunk_document
from app.services.embedding_service import embed_texts
from app.services.qdrant_service import (
    store_chunks,
    delete_document_chunks,
)

logger = logging.getLogger(__name__)

MAX_UPLOAD_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB

router = APIRouter(prefix="/documents", tags=["Documents"])


@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    strategy: ChunkingStrategy = Form("recursive"),
    db: AsyncSession = Depends(get_db),
) -> DocumentUploadResponse:

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="Filename is required.",
        )

    filename = file.filename
    document_uuid = str(uuid4())

    try:
        file_content = await file.read(MAX_UPLOAD_SIZE_BYTES + 1)

        if len(file_content) > MAX_UPLOAD_SIZE_BYTES:
            raise HTTPException(
                status_code=413,
                detail="File size exceeds the maximum allowed limit of 10 MB.",
            )

        pages = extract_document(
            file_content=file_content,
            filename=filename,
        )

        chunks = chunk_document(
            pages=pages,
            strategy=strategy,
        )

        if not chunks:
            raise ValueError("No document chunks were generated.")

        vectors = await embed_texts(
            texts=[chunk.text for chunk in chunks],
            task_type="RETRIEVAL_DOCUMENT",
        )

        await store_chunks(
            chunks=chunks,
            vectors=vectors,
            document_uuid=document_uuid,
        )

        try:
            await create_document(
                db=db,
                document_uuid=document_uuid,
                filename=filename,
                file_type=Path(filename).suffix.lower(),
                pages_extracted=len(pages),
                chunks_created=len(chunks),
                chunking_strategy=strategy,
            )

        except Exception as exc:
            logger.exception(
                "Failed to save document metadata for %s",
                document_uuid,
            )

            try:
                await delete_document_chunks(document_uuid)

            except Exception as cleanup_exc:
                logger.exception(
                    "Failed to clean up Qdrant chunks for %s",
                    document_uuid,
                )

                raise HTTPException(
                    status_code=500,
                    detail=(
                        "Document metadata could not be saved, "
                        "and Qdrant cleanup also failed."
                    ),
                ) from cleanup_exc

            raise HTTPException(
                status_code=500,
                detail=(
                    "Document metadata could not be saved. "
                    "Qdrant chunks were cleaned up."
                ),
            ) from exc

        return DocumentUploadResponse(
            document_uuid=document_uuid,
            filename=filename,
            pages_extracted=len(pages),
            chunks_created=len(chunks),
            vectors_stored=len(vectors),
            chunking_strategy=strategy,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except RuntimeError as exc:
        raise HTTPException(
            status_code=502,
            detail=str(exc),
        ) from exc

    finally:
        await file.close()