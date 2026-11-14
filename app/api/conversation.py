from fastapi import APIRouter, HTTPException

from app.schemas.conversation import ChatRequest, ChatResponse
from app.services.chat_memory_service import (
    add_message,
    get_history,
)
from app.services.rag_service import answer_question

router = APIRouter(
    prefix="/conversation",
    tags=["Conversation"],
)


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    try:
        # Step 1: Retrieve previous conversation history.
        history = await get_history(request.session_id)

        # Step 2: Generate an answer using conversational RAG.
        answer = await answer_question(
            question=request.message,
            conversation_history=history,
        )

        # Step 3: Save the successful exchange in Redis.
        await add_message(
            session_id=request.session_id,
            role="user",
            content=request.message,
        )

        await add_message(
            session_id=request.session_id,
            role="assistant",
            content=answer,
        )

        # Step 4: Return the response.
        return ChatResponse(
            session_id=request.session_id,
            answer=answer,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except RuntimeError as exc:
        raise HTTPException(
            status_code=502,
            detail=str(exc),
        ) from exc
