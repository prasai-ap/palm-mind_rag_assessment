
from datetime import date, datetime, time

from sqlalchemy import Date, DateTime, Integer, String, Time, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class InterviewBooking(Base):
    __tablename__ = "interview_bookings"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    session_id: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
        index=True,
    )

    name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    email: Mapped[str] = mapped_column(
        String(254),
        nullable=False,
    )

    interview_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )

    interview_time: Mapped[time] = mapped_column(
        Time,
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="confirmed",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

class Document(Base):
    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    document_uuid: Mapped[str] = mapped_column(
        String(36),
        unique=True,
        nullable=False,
        index=True,
    )
    filename: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    file_type: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
    )
    pages_extracted: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    chunks_created: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    chunking_strategy: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )