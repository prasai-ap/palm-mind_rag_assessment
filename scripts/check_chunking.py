
from app.services.document_processor import ExtractedPage
from app.services.chunking import chunk_document


pages = [
    ExtractedPage(
        filename="research.pdf",
        page_number=1,
        text=(
            "Artificial intelligence is transforming healthcare. "
            "Machine learning helps doctors identify diseases. "
            "Deep learning improves medical image analysis. "
        ) * 10,
    ),
    ExtractedPage(
        filename="research.pdf",
        page_number=2,
        text=(
            "Natural language processing helps analyze medical records. "
            "Retrieval augmented generation provides contextual answers. "
        ) * 10,
    ),
]


for strategy in ["fixed", "recursive"]:
    chunks = chunk_document(
        pages=pages,
        strategy=strategy,
        chunk_size=200,
        chunk_overlap=40,
    )

    print(f"\nStrategy: {strategy}")
    print(f"Total chunks: {len(chunks)}")

    for chunk in chunks:
        print(
            f"Index: {chunk.chunk_index} | "
            f"Page: {chunk.page_number} | "
            f"Length: {len(chunk.text)}"
        )
        print(chunk.text[:100])
