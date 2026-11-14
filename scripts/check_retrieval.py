
import asyncio

from app.services.retrieval_service import retrieve_relevant_chunks


async def main() -> None:
    questions = [
        "How does machine learning help doctors?",
        "How is artificial intelligence used in medical image analysis?",
        "How can computers understand medical records?",
    ]

    for question in questions:
        print("\n" + "=" * 70)
        print("QUESTION:", question)
        print("=" * 70)

        results = await retrieve_relevant_chunks(
            query=question,
            limit=3,
        )

        if not results:
            print("No relevant chunks found.")
            continue

        for index, result in enumerate(results, start=1):
            print(f"\nResult {index}")
            print("Similarity score:", round(result.score, 4))
            print("Filename:", result.filename)
            print("Page:", result.page_number)
            print("Chunk index:", result.chunk_index)
            print("Text:", result.text)

    print("\nRetrieval verification completed!")


if __name__ == "__main__":
    asyncio.run(main())
