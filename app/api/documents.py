
from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from app.schemas.document import (
    ChunkingStrategy,
    DocumentUploadResponse,
)
from app.services.document_processor import extract_document
from app.services.chunking import chunk_document
from app.services.embedding_service import embed_texts
from app.services.qdrant_service import store_chunks


router = APIRouter(
    prefix="/documents",
    tags=["Documents"],
)


@router.post(
    "/upload",
    response_model=DocumentUploadResponse,
)
async def upload_document(
    file: UploadFile = File(...),
    strategy: ChunkingStrategy = Form("recursive"),
) -> DocumentUploadResponse:

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="Filename is required.",
        )

    filename = file.filename

    try:
        # 1. Read uploaded file.
        file_content = await file.read()

        # 2. Extract document text.
        pages = extract_document(
            file_content=file_content,
            filename=filename,
        )

        # 3. Split extracted text into chunks.
        chunks = chunk_document(
            pages=pages,
            strategy=strategy,
        )

        if not chunks:
            raise ValueError("No document chunks were generated.")

        # 4. Generate embeddings.
        vectors = await embed_texts(
            texts=[chunk.text for chunk in chunks],
            task_type="RETRIEVAL_DOCUMENT",
        )

        # 5. Store chunks and embeddings in Qdrant.
        await store_chunks(
            chunks=chunks,
            vectors=vectors,
        )

        return DocumentUploadResponse(
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
