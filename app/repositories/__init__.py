
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import InterviewBooking
from app.schemas.booking import InterviewBookingExtraction


async def create_booking(
    db: AsyncSession,
    session_id: str,
    booking: InterviewBookingExtraction,
    user_confirmed: bool,
) -> InterviewBooking:
    """
    Persist an interview booking after validating its details
    and receiving explicit user confirmation.
    """

    if not user_confirmed:
        raise ValueError("User confirmation is required to create a booking.")

    if not booking.booking_requested:
        raise ValueError("No interview booking was requested.")

    if not all(
        [
            booking.name,
            booking.email,
            booking.interview_date,
            booking.interview_time,
        ]
    ):
        raise ValueError("All interview booking details are required.")

    if not session_id.strip():
        raise ValueError("Session ID cannot be empty.")

    new_booking = InterviewBooking(
        session_id=session_id,
        name=booking.name,
        email=str(booking.email),
        interview_date=booking.interview_date,
        interview_time=booking.interview_time,
        status="confirmed",
    )

    try:
        db.add(new_booking)
        await db.commit()
        await db.refresh(new_booking)
    except Exception:
        await db.rollback()
        raise

    return new_booking
