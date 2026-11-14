
from datetime import date, time

from pydantic import BaseModel, EmailStr, Field, field_validator


class InterviewBookingExtraction(BaseModel):
    booking_requested: bool = False
    name: str | None = Field(default=None, max_length=150)
    email: EmailStr | None = None
    interview_date: date | None = None
    interview_time: time | None = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str | None) -> str | None:
        if value is not None:
            value = value.strip()

            if not value:
                return None

        return value


class InterviewBookingResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    interview_date: date
    interview_time: time
    status: str
