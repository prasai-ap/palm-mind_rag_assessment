
from app.services.retrieval_service import retrieve_relevant_chunks
from app.services.prompt_service import build_rag_prompt
from app.services.llm_service import generate_response
from app.services.question_rewriter import rewrite_followup_question


async def answer_question(
    question: str,
    limit: int = 5,
    conversation_history: list[dict[str, str]] | None = None,
) -> str:
    if not question.strip():
        raise ValueError("Question cannot be empty.")

    if limit <= 0:
        raise ValueError("Retrieval limit must be greater than zero.")

    history = conversation_history or []

    # Step 1: Convert the user's question into a standalone query.
    standalone_question = await rewrite_followup_question(
        question=question,
        history=history,
    )

    # Step 2: Retrieve relevant document chunks.
    retrieved_chunks = await retrieve_relevant_chunks(
        query=standalone_question,
        limit=limit,
    )

    # Step 3: Handle cases where no relevant documents exist.
    if not retrieved_chunks:
        return (
            "I couldn't find relevant information in the "
            "uploaded documents to answer your question."
        )

    # Step 4: Build a prompt using document evidence and history.
    prompt = build_rag_prompt(
        question=question,
        retrieved_chunks=retrieved_chunks,
        conversation_history=history,
    )

    # Step 5: Generate the grounded answer.
    answer = await generate_response(prompt)

    return answer
