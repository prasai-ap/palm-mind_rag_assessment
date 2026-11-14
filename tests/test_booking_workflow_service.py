
from datetime import date, time
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.schemas.booking import InterviewBookingExtraction
from app.services.booking_workflow_service import process_booking_message


@pytest.mark.anyio
async def test_non_booking_message_returns_none(monkeypatch):
    async def mock_extract(**kwargs):
        return InterviewBookingExtraction(booking_requested=False)

    monkeypatch.setattr(
        "app.services.booking_workflow_service.extract_booking_details",
        mock_extract,
    )

    result = await process_booking_message(
        db=MagicMock(),
        session_id="session_001",
        message="What is machine learning?",
        conversation_history=[],
    )

    assert result is None


@pytest.mark.anyio
async def test_missing_booking_details_are_requested(monkeypatch):
    async def mock_extract(**kwargs):
        return InterviewBookingExtraction(
            booking_requested=True,
            name="Aayus Prasai",
            email="aayus@example.com",
        )

    monkeypatch.setattr(
        "app.services.booking_workflow_service.extract_booking_details",
        mock_extract,
    )

    result = await process_booking_message(
        db=MagicMock(),
        session_id="session_001",
        message="I want to schedule an interview.",
        conversation_history=[],
    )

    assert "preferred interview date" in result
    assert "preferred interview time" in result


@pytest.mark.anyio
async def test_complete_booking_requests_confirmation(monkeypatch):
    async def mock_extract(**kwargs):
        return InterviewBookingExtraction(
            booking_requested=True,
            user_confirmed=False,
            name="Aayus Prasai",
            email="aayus@example.com",
            interview_date=date(2026, 11, 20),
            interview_time=time(14, 30),
        )

    monkeypatch.setattr(
        "app.services.booking_workflow_service.extract_booking_details",
        mock_extract,
    )

    db = MagicMock()

    result = await process_booking_message(
        db=db,
        session_id="session_001",
        message="My preferred interview time is 2:30 PM.",
        conversation_history=[],
    )

    assert "Aayus Prasai" in result
    assert "aayus@example.com" in result
    assert "CONFIRM" in result

    db.add.assert_not_called()


@pytest.mark.anyio
async def test_confirmed_booking_is_saved(monkeypatch):
    extraction = InterviewBookingExtraction(
        booking_requested=True,
        user_confirmed=True,
        name="Aayus Prasai",
        email="aayus@example.com",
        interview_date=date(2026, 11, 20),
        interview_time=time(14, 30),
    )

    async def mock_extract(**kwargs):
        return extraction

    async def mock_create_booking(**kwargs):
        booking = MagicMock()
        booking.id = 1
        booking.name = extraction.name
        booking.email = str(extraction.email)
        booking.interview_date = extraction.interview_date
        booking.interview_time = extraction.interview_time
        return booking

    monkeypatch.setattr(
        "app.services.booking_workflow_service.extract_booking_details",
        mock_extract,
    )

    create_mock = AsyncMock(side_effect=mock_create_booking)

    monkeypatch.setattr(
        "app.services.booking_workflow_service.create_booking",
        create_mock,
    )

    db = MagicMock()

    result = await process_booking_message(
        db=db,
        session_id="session_001",
        message="CONFIRM",
        conversation_history=[
            {
                "role": "assistant",
                "content": (
                    "Please review your details and reply CONFIRM "
                    "to save your booking."
                ),
            }
        ],
    )

    assert "successfully recorded" in result
    assert "Booking ID: 1" in result

    create_mock.assert_awaited_once()
    assert create_mock.await_args.kwargs["user_confirmed"] is True


@pytest.mark.anyio
async def test_confirmation_without_previous_request_does_not_save(
    monkeypatch,
):
    async def mock_extract(**kwargs):
        return InterviewBookingExtraction(
            booking_requested=True,
            user_confirmed=True,
            name="Aayus Prasai",
            email="aayus@example.com",
            interview_date=date(2026, 11, 20),
            interview_time=time(14, 30),
        )

    monkeypatch.setattr(
        "app.services.booking_workflow_service.extract_booking_details",
        mock_extract,
    )

    create_mock = AsyncMock()

    monkeypatch.setattr(
        "app.services.booking_workflow_service.create_booking",
        create_mock,
    )

    result = await process_booking_message(
        db=MagicMock(),
        session_id="session_001",
        message="CONFIRM",
        conversation_history=[],
    )

    assert "reply CONFIRM" in result
    create_mock.assert_not_awaited()
