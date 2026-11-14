
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.booking_repository import create_booking
from app.schemas.booking import InterviewBookingExtraction
from app.services.booking_extraction_service import extract_booking_details


def _previous_message_requested_confirmation(
    history: list[dict[str, str]],
) -> bool:
    if not history:
        return False

    last_message = history[-1]

    return (
        last_message["role"] == "assistant"
        and "reply CONFIRM" in last_message["content"]
    )


def _is_explicit_confirmation(message: str) -> bool:
    return message.strip().casefold() == "confirm"


async def process_booking_message(
    db: AsyncSession,
    session_id: str,
    message: str,
    conversation_history: list[dict[str, str]],
) -> str | None:
    extraction: InterviewBookingExtraction = await extract_booking_details(
        message=message,
        conversation_history=conversation_history,
    )

    if not extraction.booking_requested:
        return None

    missing_fields = []

    if not extraction.name:
        missing_fields.append("your full name")

    if not extraction.email:
        missing_fields.append("your email address")

    if not extraction.interview_date:
        missing_fields.append("your preferred interview date")

    if not extraction.interview_time:
        missing_fields.append("your preferred interview time")

    if missing_fields:
        missing_text = ", ".join(missing_fields)

        return (
            "I'd be happy to help arrange your interview. "
            f"Could you please provide {missing_text}?"
        )

    confirmation_was_requested = (
        _previous_message_requested_confirmation(conversation_history)
    )

    explicitly_confirmed = (
        _is_explicit_confirmation(message)
        and confirmation_was_requested
        and extraction.user_confirmed
    )

    if not explicitly_confirmed:
        return (
            "Here are your interview booking details:\n\n"
            f"Name: {extraction.name}\n"
            f"Email: {extraction.email}\n"
            f"Date: {extraction.interview_date.isoformat()}\n"
            f"Time: {extraction.interview_time.strftime('%I:%M %p')}\n\n"
            "Please review these details. If everything is correct, "
            "reply CONFIRM to save your booking."
        )

    booking = await create_booking(
        db=db,
        session_id=session_id,
        booking=extraction,
        user_confirmed=True,
    )

    return (
        "Your interview booking has been successfully recorded!\n\n"
        f"Booking ID: {booking.id}\n"
        f"Name: {booking.name}\n"
        f"Email: {booking.email}\n"
        f"Date: {booking.interview_date.isoformat()}\n"
        f"Time: {booking.interview_time.strftime('%I:%M %p')}"
    )
