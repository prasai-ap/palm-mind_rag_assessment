
import asyncio

from app.services.llm_service import generate_response


async def main() -> None:
    prompt = """
You are a helpful AI assistant.

Answer the following question in 3-4 sentences:

What is Retrieval-Augmented Generation (RAG)?
Explain how retrieval and language generation work together.
"""

    print("Sending prompt to Gemini...\n")

    response = await generate_response(prompt)

    print("Gemini response:")
    print("-" * 60)
    print(response)
    print("-" * 60)

    assert isinstance(response, str)
    assert len(response.strip()) > 0

    print("\nLLM generation test successful!")


if __name__ == "__main__":
    asyncio.run(main())
