from datetime import date, time

import pytest

from app.schemas.booking import InterviewBookingExtraction
from app.services.booking_extraction_service import (
    build_booking_extraction_prompt,
    extract_booking_details,
)


def test_prompt_includes_latest_message():
    prompt = build_booking_extraction_prompt(
        message="I want to schedule an interview.",
        conversation_history=[],
    )

    assert "I want to schedule an interview." in prompt
    assert "booking_requested" in prompt
    assert "user_confirmed" in prompt
    assert "Never invent or assume" in prompt


def test_prompt_includes_conversation_history():
    prompt = build_booking_extraction_prompt(
        message="Tomorrow at 2 PM works for me.",
        conversation_history=[
            {
                "role": "user",
                "content": "My name is Aayus and my email is aayus@example.com.",
            }
        ],
    )

    assert "Aayus" in prompt
    assert "aayus@example.com" in prompt
    assert "Tomorrow at 2 PM works for me." in prompt


@pytest.mark.anyio
async def test_extract_booking_details(monkeypatch):
    expected = InterviewBookingExtraction(
        booking_requested=True,
        user_confirmed=True,
        name="Aayus Prasai",
        email="aayus@example.com",
        interview_date=date(2026, 11, 20),
        interview_time=time(14, 30),
    )

    async def mock_generate_structured_response(prompt, response_schema):
        assert "schedule an interview" in prompt
        assert response_schema is InterviewBookingExtraction
        return expected

    monkeypatch.setattr(
        "app.services.booking_extraction_service.generate_structured_response",
        mock_generate_structured_response,
    )

    result = await extract_booking_details(
        message="I want to schedule an interview."
    )

    assert result == expected


@pytest.mark.anyio
async def test_extract_booking_details_rejects_empty_message():
    with pytest.raises(ValueError, match="Message cannot be empty"):
        await extract_booking_details(message="   ")
