
from datetime import date, time
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.database.models import InterviewBooking
from app.repositories.booking_repository import create_booking
from app.schemas.booking import InterviewBookingExtraction


@pytest.mark.anyio
async def test_create_booking():
    db = MagicMock()
    db.commit = AsyncMock()
    db.refresh = AsyncMock()
    db.rollback = AsyncMock()

    booking = InterviewBookingExtraction(
        booking_requested=True,
        name="Aayus Prasai",
        email="aayus@example.com",
        interview_date=date(2026, 11, 20),
        interview_time=time(14, 30),
    )

    result = await create_booking(
        db=db,
        session_id="test_session_001",
        booking=booking,
        user_confirmed=True,
    )

    assert isinstance(result, InterviewBooking)
    assert result.session_id == "test_session_001"
    assert result.name == "Aayus Prasai"
    assert result.email == "aayus@example.com"
    assert result.interview_date == date(2026, 11, 20)
    assert result.interview_time == time(14, 30)
    assert result.status == "confirmed"

    db.add.assert_called_once_with(result)
    db.commit.assert_awaited_once()
    db.refresh.assert_awaited_once_with(result)


@pytest.mark.anyio
async def test_booking_requires_confirmation():
    db = MagicMock()

    booking = InterviewBookingExtraction(
        booking_requested=True,
        name="Aayus Prasai",
        email="aayus@example.com",
        interview_date="2026-11-20",
        interview_time="14:30",
    )

    with pytest.raises(ValueError, match="confirmation is required"):
        await create_booking(
            db=db,
            session_id="test_session_001",
            booking=booking,
            user_confirmed=False,
        )

    db.add.assert_not_called()


@pytest.mark.anyio
async def test_booking_rejects_incomplete_details():
    db = MagicMock()

    booking = InterviewBookingExtraction(
        booking_requested=True,
        name="Aayus Prasai",
        email="aayus@example.com",
    )

    with pytest.raises(ValueError, match="All interview booking details"):
        await create_booking(
            db=db,
            session_id="test_session_001",
            booking=booking,
            user_confirmed=True,
        )

    db.add.assert_not_called()


@pytest.mark.anyio
async def test_booking_rejects_missing_booking_intent():
    db = MagicMock()

    booking = InterviewBookingExtraction(
        booking_requested=False,
        name="Aayus Prasai",
        email="aayus@example.com",
        interview_date="2026-11-20",
        interview_time="14:30",
    )

    with pytest.raises(ValueError, match="No interview booking was requested"):
        await create_booking(
            db=db,
            session_id="test_session_001",
            booking=booking,
            user_confirmed=True,
        )

    db.add.assert_not_called()
