
import asyncio

from app.services.rag_service import answer_question


async def main() -> None:
    questions = [
        "How does machine learning help doctors?",
        "How is deep learning used in medical imaging?",
        "How does natural language processing help with medical records?",
    ]

    for question in questions:
        print("\n" + "=" * 70)
        print("QUESTION:", question)
        print("=" * 70)

        answer = await answer_question(
            question=question,
            limit=3,
        )

        print("\nRAG ANSWER:")
        print("-" * 70)
        print(answer)
        print("-" * 70)


if __name__ == "__main__":
    asyncio.run(main())
