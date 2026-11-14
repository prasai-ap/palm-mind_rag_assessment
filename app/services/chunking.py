from langchain_text_splitters import (
    CharacterTextSplitter,
    RecursiveCharacterTextSplitter,
)

from app.schemas.document import DocumentChunk, ChunkingStrategy
from app.services.document_processor import ExtractedPage


def chunk_document(
    pages: list[ExtractedPage],
    strategy: ChunkingStrategy,
    chunk_size: int = 500,
    chunk_overlap: int = 100,
) -> list[DocumentChunk]:
    """
    Split extracted document pages into smaller text chunks.

    Each chunk retains its original filename and page number.
    """

    if chunk_size <= 0:
        raise ValueError("Chunk size must be greater than zero.")

    if chunk_overlap < 0:
        raise ValueError("Chunk overlap cannot be negative.")

    if chunk_overlap >= chunk_size:
        raise ValueError("Chunk overlap must be smaller than chunk size.")

    if strategy == "fixed":
        splitter = CharacterTextSplitter(
            separator="",
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            strip_whitespace=True,
        )

    elif strategy == "recursive":
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", ". ", " ", ""],
            strip_whitespace=True,
        )

    else:
        raise ValueError(
            f"Unsupported chunking strategy: {strategy}"
        )

    chunks: list[DocumentChunk] = []

    for page in pages:
        page_chunks = splitter.split_text(page.text)

        for chunk_text in page_chunks:
            if not chunk_text.strip():
                continue

            chunks.append(
                DocumentChunk(
                    filename=page.filename,
                    page_number=page.page_number,
                    chunk_index=len(chunks),
                    text=chunk_text,
                )
            )

    return chunks
