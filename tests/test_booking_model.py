
from app.database.models import InterviewBooking


def test_booking_table_name():
    assert InterviewBooking.__tablename__ == "interview_bookings"


def test_booking_model_columns():
    columns = InterviewBooking.__table__.columns

    expected_columns = {
        "id",
        "session_id",
        "name",
        "email",
        "interview_date",
        "interview_time",
        "status",
        "created_at",
    }

    assert expected_columns.issubset(set(columns.keys()))


def test_booking_primary_key():
    primary_key = InterviewBooking.__table__.primary_key

    assert [column.name for column in primary_key.columns] == ["id"]


def test_booking_required_fields():
    columns = InterviewBooking.__table__.columns

    required_fields = [
        "session_id",
        "name",
        "email",
        "interview_date",
        "interview_time",
        "status",
        "created_at",
    ]

    for field in required_fields:
        assert columns[field].nullable is False
