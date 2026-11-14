
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.schemas.conversation import ChatRequest, ChatResponse
from app.services.booking_workflow_service import process_booking_message
from app.services.chat_memory_service import add_message, get_history
from app.services.rag_service import answer_question

router = APIRouter(prefix="/conversation", tags=["Conversation"])


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db),
) -> ChatResponse:
    try:
        history = await get_history(request.session_id)

        booking_response = await process_booking_message(
            db=db,
            session_id=request.session_id,
            message=request.message,
            conversation_history=history,
        )

        if booking_response is not None:
            answer = booking_response
        else:
            answer = await answer_question(
                question=request.message,
                conversation_history=history,
            )

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

        return ChatResponse(
            session_id=request.session_id,
            answer=answer,
        )

    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    except RuntimeError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
