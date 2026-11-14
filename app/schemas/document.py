from typing import Literal

from pydantic import BaseModel


class DocumentChunk(BaseModel):
    filename: str
    page_number: int | None
    chunk_index: int
    text: str


ChunkingStrategy = Literal["fixed", "recursive"]