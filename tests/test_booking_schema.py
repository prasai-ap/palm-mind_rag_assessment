
from datetime import date, time

import pytest
from pydantic import ValidationError

from app.schemas.booking import InterviewBookingExtraction


def test_complete_booking_extraction():
    booking = InterviewBookingExtraction(
        booking_requested=True,
        name="Aayus Prasai",
        email="aayus@example.com",
        interview_date="2026-11-20",
        interview_time="14:30",
    )

    assert booking.booking_requested is True
    assert booking.name == "Aayus Prasai"
    assert booking.email == "aayus@example.com"
    assert booking.interview_date == date(2026, 11, 20)
    assert booking.interview_time == time(14, 30)


def test_incomplete_booking_is_allowed():
    booking = InterviewBookingExtraction(
        booking_requested=True,
        name="Aayus Prasai",
        email="aayus@example.com",
    )

    assert booking.name == "Aayus Prasai"
    assert booking.interview_date is None
    assert booking.interview_time is None


def test_no_booking_requested():
    booking = InterviewBookingExtraction()

    assert booking.booking_requested is False
    assert booking.name is None
    assert booking.email is None


def test_invalid_email_is_rejected():
    with pytest.raises(ValidationError):
        InterviewBookingExtraction(
            booking_requested=True,
            email="not-an-email",
        )


def test_invalid_date_is_rejected():
    with pytest.raises(ValidationError):
        InterviewBookingExtraction(
            interview_date="not-a-date",
        )


def test_invalid_time_is_rejected():
    with pytest.raises(ValidationError):
        InterviewBookingExtraction(
            interview_time="not-a-time",
        )


def test_blank_name_becomes_none():
    booking = InterviewBookingExtraction(
        booking_requested=True,
        name="   ",
    )

    assert booking.name is None

def test_booking_confirmation_defaults_to_false():
    booking = InterviewBookingExtraction(
        booking_requested=True,
        name="Aayus Prasai",
    )

    assert booking.user_confirmed is False