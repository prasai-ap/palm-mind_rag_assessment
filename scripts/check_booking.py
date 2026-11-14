import asyncio

from sqlalchemy import select

from app.database.models import InterviewBooking
from app.database.session import AsyncSessionLocal, engine


async def main() -> None:
    try:
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(InterviewBooking).where(
                    InterviewBooking.id == 1
                )
            )
            booking = result.scalar_one_or_none()

            if booking is None:
                print("Booking not found.")
                return

            print("Booking found in PostgreSQL!")
            print(f"ID: {booking.id}")
            print(f"Session: {booking.session_id}")
            print(f"Name: {booking.name}")
            print(f"Email: {booking.email}")
            print(f"Date: {booking.interview_date}")
            print(f"Time: {booking.interview_time}")
            print(f"Status: {booking.status}")

    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
