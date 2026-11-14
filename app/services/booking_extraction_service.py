from app.schemas.booking import InterviewBookingExtraction
from app.services.llm_service import generate_structured_response


def build_booking_extraction_prompt(
    message: str,
    conversation_history: list[dict[str, str]],
) -> str:
    history_text = "\n".join(
        f"{item['role']}: {item['content']}"
        for item in conversation_history
    )

    return f"""
You are an interview booking information extraction assistant.

Your task is to identify whether the user is requesting an interview
booking and extract information they have explicitly provided.

Extract these fields:
- booking_requested: whether the user is requesting to arrange or confirm
  an interview booking
- user_confirmed: whether the user explicitly confirms the proposed
  interview booking in their latest message.
- name: the candidate's name
- email: the candidate's email address
- interview_date: the interview date in YYYY-MM-DD format
- interview_time: the interview time in HH:MM 24-hour format

Rules:
1. Extract only information supported by the conversation.
2. Never invent or assume a name, email, date, or time.
3. Use conversation history to resolve information the user provided earlier.
4. Do not treat information in unrelated assistant responses as user-provided
   booking details.
5. If a field is missing or ambiguous, return null for that field.
6. A question about interview booking availability is a booking request,
   even if the user has not provided all the details.
7. Do not consider a booking confirmed just because all fields are present.
8. Return only the structured data matching the required schema.
9. Set user_confirmed to true only when the latest user message
   clearly confirms the booking.
10. A message such as "yes", "confirm", or "book it" can confirm
   a booking when the conversation history shows that the assistant
   explicitly requested confirmation.
11. Never interpret providing personal details as confirmation.
12. Never interpret the assistant's own message as user confirmation.
13. If confirmation is ambiguous, return false.

CONVERSATION HISTORY:
{history_text or "No previous conversation."}

LATEST USER MESSAGE:
{message}
""".strip()


async def extract_booking_details(
    message: str,
    conversation_history: list[dict[str, str]] | None = None,
) -> InterviewBookingExtraction:
    if not message.strip():
        raise ValueError("Message cannot be empty.")

    history = conversation_history or []

    prompt = build_booking_extraction_prompt(
        message=message,
        conversation_history=history,
    )

    return await generate_structured_response(
        prompt=prompt,
        response_schema=InterviewBookingExtraction,
    )
