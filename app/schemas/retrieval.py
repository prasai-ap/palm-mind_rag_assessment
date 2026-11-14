from pydantic import BaseModel


class RetrievedChunk(BaseModel):
    filename: str
    page_number: int | None
    chunk_index: int
    text: str
    score: float