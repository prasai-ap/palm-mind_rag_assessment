import asyncio

from app.services.booking_extraction_service import extract_booking_details


async def main() -> None:
    result = await extract_booking_details(
        message=(
            "I would like to schedule an interview. "
            "My name is Aayus Prasai and my email is "
            "aayus@example.com. I am available on November 20, 2026 "
            "at 2:30 PM."
        )
    )

    print("Extracted booking details:")
    print(result.model_dump_json(indent=2))


if __name__ == "__main__":
    asyncio.run(main())
