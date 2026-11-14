from app.services.retrieval_service import retrieve_relevant_chunks
from app.services.prompt_service import build_rag_prompt
from app.services.llm_service import generate_response


async def answer_question(
    question: str,
    limit: int = 5,
) -> str:
    """
    Answer a user's question using the custom RAG pipeline.

    Pipeline:
        1. Retrieve relevant document chunks.
        2. Construct a grounded prompt.
        3. Generate an answer using Gemini.

    Args:
        question: The user's question.
        limit: Maximum number of chunks to retrieve.

    Returns:
        The generated answer.
    """

    if not question.strip():
        raise ValueError("Question cannot be empty.")

    if limit <= 0:
        raise ValueError("Retrieval limit must be greater than zero.")

    # 1. Retrieve relevant document chunks.
    retrieved_chunks = await retrieve_relevant_chunks(
        query=question,
        limit=limit,
    )

    # 2. Handle cases where no documents were retrieved.
    if not retrieved_chunks:
        return (
            "I couldn't find relevant information in the "
            "uploaded documents to answer your question."
        )

    # 3. Construct the RAG prompt.
    prompt = build_rag_prompt(
        question=question,
        retrieved_chunks=retrieved_chunks,
    )

    # 4. Generate the final answer.
    answer = await generate_response(prompt)

    return answer
