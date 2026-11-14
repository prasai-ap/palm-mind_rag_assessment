
from io import BytesIO

import pytest
from pypdf import PdfWriter

from app.services.document_processor import (
    ExtractedPage,
    extract_document,
)

from reportlab.pdfgen import canvas

def create_test_pdf(pages: list[str]) -> bytes:
    """Create a text-based PDF in memory."""

    buffer = BytesIO()
    pdf = canvas.Canvas(buffer)

    for text in pages:
        pdf.drawString(50, 750, text)
        pdf.showPage()

    pdf.save()

    return buffer.getvalue()


def test_extract_txt_success() -> None:
    content = b"Palm Mind AI document processing test."

    result = extract_document(content, "sample.txt")

    assert len(result) == 1
    assert result[0] == ExtractedPage(
        filename="sample.txt",
        page_number=None,
        text="Palm Mind AI document processing test.",
    )


def test_extract_txt_strips_whitespace() -> None:
    content = b"   Hello Palm Mind   \n"

    result = extract_document(content, "sample.txt")

    assert result[0].text == "Hello Palm Mind"


def test_extract_pdf_success() -> None:
    pdf_content = create_test_pdf(
        ["First page content", "Second page content"]
    )

    result = extract_document(pdf_content, "sample.pdf")

    assert len(result) == 2
    assert result[0].filename == "sample.pdf"
    assert result[0].page_number == 1
    assert result[1].page_number == 2


def test_extract_empty_file() -> None:
    with pytest.raises(ValueError, match="uploaded file is empty"):
        extract_document(b"", "empty.txt")


def test_unsupported_file_type() -> None:
    with pytest.raises(ValueError, match="Unsupported file type"):
        extract_document(b"some content", "sample.docx")


def test_extract_txt_invalid_utf8() -> None:
    content = b"\xff\xfe\xfa"

    with pytest.raises(ValueError, match="Unable to decode TXT"):
        extract_document(content, "invalid.txt")


def test_extract_empty_txt() -> None:
    with pytest.raises(ValueError, match="No extractable text"):
        extract_document(b"   \n  ", "empty.txt")


def test_extract_pdf_without_text() -> None:
    pdf_content = create_test_pdf([""])

    with pytest.raises(ValueError, match="No extractable text"):
        extract_document(pdf_content, "image_only.pdf")


def test_pdf_preserves_original_page_numbers() -> None:
    pdf_content = create_test_pdf(
        ["First page", "", "Third page"]
    )

    result = extract_document(pdf_content, "research.pdf")

    assert len(result) == 2
    assert result[0].page_number == 1
    assert result[1].page_number == 3
