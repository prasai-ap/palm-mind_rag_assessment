import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.api import conversation as conversation_api

client = TestClient(app)


def test_successful_conversation(monkeypatch):
    saved_messages = []

    async def mock_get_history(session_id):
        assert session_id == "session_123"
        return [
            {"role": "user", "content": "What is machine learning?"},
            {"role": "assistant", "content": "It learns from data."},
        ]

    async def mock_answer_question(question, conversation_history):
        assert question == "How is it used in healthcare?"
        assert len(conversation_history) == 2
        return "It helps doctors identify diseases."

    async def mock_add_message(session_id, role, content):
        saved_messages.append({
            "session_id": session_id,
            "role": role,
            "content": content,
        })

    monkeypatch.setattr(
        conversation_api, "get_history", mock_get_history
    )
    monkeypatch.setattr(
        conversation_api, "answer_question", mock_answer_question
    )
    monkeypatch.setattr(
        conversation_api, "add_message", mock_add_message
    )

    response = client.post(
        "/conversation/chat",
        json={
            "session_id": "session_123",
            "message": "How is it used in healthcare?",
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "session_id": "session_123",
        "answer": "It helps doctors identify diseases.",
    }

    assert len(saved_messages) == 2
    assert saved_messages[0]["role"] == "user"
    assert saved_messages[1]["role"] == "assistant"


def test_rag_failure_does_not_save_messages(monkeypatch):
    saved_messages = []

    async def mock_get_history(session_id):
        return []

    async def mock_answer_question(question, conversation_history):
        raise RuntimeError("Gemini service unavailable.")

    async def mock_add_message(session_id, role, content):
        saved_messages.append(content)

    monkeypatch.setattr(
        conversation_api, "get_history", mock_get_history
    )
    monkeypatch.setattr(
        conversation_api, "answer_question", mock_answer_question
    )
    monkeypatch.setattr(
        conversation_api, "add_message", mock_add_message
    )

    response = client.post(
        "/conversation/chat",
        json={
            "session_id": "session_123",
            "message": "Hello",
        },
    )

    assert response.status_code == 502
    assert response.json()["detail"] == "Gemini service unavailable."
    assert saved_messages == []


def test_invalid_chat_request():
    response = client.post(
        "/conversation/chat",
        json={
            "session_id": "session_123",
            "message": "   ",
        },
    )

    assert response.status_code == 422


def test_empty_session_id():
    response = client.post(
        "/conversation/chat",
        json={
            "session_id": "   ",
            "message": "Hello",
        },
    )

    assert response.status_code == 422
