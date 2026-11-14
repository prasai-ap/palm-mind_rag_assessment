
from dataclasses import dataclass
from io import BytesIO
from pathlib import Path

from pypdf import PdfReader


@dataclass
class ExtractedPage:
    """Represents extracted text from a document page."""

    filename: str
    page_number: int | None
    text: str


def extract_document(
    file_content: bytes,
    filename: str,
) -> list[ExtractedPage]:
    """
    Extract text from a PDF or TXT document.

    Args:
        file_content: Raw bytes of the uploaded document.
        filename: Original name of the uploaded document.

    Returns:
        A list of ExtractedPage objects containing extracted text
        and document metadata.

    Raises:
        ValueError: If the file type is unsupported or no text is extracted.
    """

    extension = Path(filename).suffix.lower()

    if not file_content:
        raise ValueError("The uploaded file is empty.")

    if extension == ".pdf":
        extracted_pages = _extract_pdf(file_content, filename)

    elif extension == ".txt":
        extracted_pages = _extract_txt(file_content, filename)

    else:
        raise ValueError(
            f"Unsupported file type: {extension or 'unknown'}. "
            "Only PDF and TXT files are supported."
        )

    if not extracted_pages:
        raise ValueError(
            f"No extractable text found in document: {filename}"
        )

    return extracted_pages


def _extract_pdf(
    file_content: bytes,
    filename: str,
) -> list[ExtractedPage]:
    """Extract text from each page of a PDF document."""

    reader = PdfReader(BytesIO(file_content))

    extracted_pages: list[ExtractedPage] = []

    for page_number, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        text = text.strip()

        if not text:
            continue

        extracted_pages.append(
            ExtractedPage(
                filename=filename,
                page_number=page_number,
                text=text,
            )
        )

    return extracted_pages


def _extract_txt(
    file_content: bytes,
    filename: str,
) -> list[ExtractedPage]:
    """Extract text from a plain text document."""

    try:
        text = file_content.decode("utf-8").strip()
    except UnicodeDecodeError as exc:
        raise ValueError(
            f"Unable to decode TXT document '{filename}' using UTF-8."
        ) from exc

    if not text:
        return []

    return [
        ExtractedPage(
            filename=filename,
            page_number=None,
            text=text,
        )
    ]
