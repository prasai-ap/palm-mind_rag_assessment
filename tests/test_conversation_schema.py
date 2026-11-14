
import pytest
from pydantic import ValidationError

from app.schemas.conversation import ChatRequest, ChatResponse


def test_valid_chat_request():
    request = ChatRequest(
        session_id="session_123",
        message="What is machine learning?",
    )

    assert request.session_id == "session_123"
    assert request.message == "What is machine learning?"


def test_chat_request_strips_whitespace():
    request = ChatRequest(
        session_id=" session_123 ",
        message="  Hello  ",
    )

    assert request.session_id == "session_123"
    assert request.message == "Hello"


@pytest.mark.parametrize(
    "field, value",
    [
        ("session_id", "   "),
        ("message", "   "),
    ],
)
def test_chat_request_rejects_blank_fields(field, value):
    with pytest.raises(ValidationError):
        ChatRequest(
            session_id="session_123" if field != "session_id" else value,
            message="Hello" if field != "message" else value,
        )


def test_chat_request_rejects_long_session_id():
    with pytest.raises(ValidationError):
        ChatRequest(
            session_id="s" * 129,
            message="Hello",
        )


def test_chat_response():
    response = ChatResponse(
        session_id="session_123",
        answer="Machine learning is a branch of AI.",
    )

    assert response.session_id == "session_123"
    assert response.answer == "Machine learning is a branch of AI."
