from typing import Literal

from pydantic import BaseModel


class DocumentChunk(BaseModel):
    filename: str
    page_number: int | None
    chunk_index: int
    text: str


ChunkingStrategy = Literal["fixed", "recursive"]

class DocumentUploadResponse(BaseModel):
    document_uuid: str
    filename: str
    pages_extracted: int
    chunks_created: int
    vectors_stored: int
    chunking_strategy: ChunkingStrategy