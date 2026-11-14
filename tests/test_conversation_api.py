from fastapi.testclient import TestClient

from app.main import app

from app.database.session import get_db

client = TestClient(app)

async def override_get_db():
    yield None


app.dependency_overrides[get_db] = override_get_db

def mock_booking_workflow(monkeypatch, result=None):
    async def mock_process_booking_message(**kwargs):
        return result

    monkeypatch.setattr(
        "app.api.conversation.process_booking_message",
        mock_process_booking_message,
    )


def test_chat_success(monkeypatch):
    history = [
        {
            "role": "user",
            "content": "What is machine learning?",
        }
    ]

    saved_messages = []

    async def mock_get_history(session_id):
        return history

    async def mock_answer_question(question, conversation_history=None):
        assert question == "How does it help doctors?"
        assert conversation_history == history
        return "Machine learning helps doctors identify diseases."

    async def mock_add_message(session_id, role, content):
        saved_messages.append(
            {
                "session_id": session_id,
                "role": role,
                "content": content,
            }
        )

    mock_booking_workflow(monkeypatch)

    monkeypatch.setattr(
        "app.api.conversation.get_history",
        mock_get_history,
    )

    monkeypatch.setattr(
        "app.api.conversation.answer_question",
        mock_answer_question,
    )

    monkeypatch.setattr(
        "app.api.conversation.add_message",
        mock_add_message,
    )

    response = client.post(
        "/conversation/chat",
        json={
            "session_id": "test_session_001",
            "message": "How does it help doctors?",
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "session_id": "test_session_001",
        "answer": "Machine learning helps doctors identify diseases.",
    }

    assert len(saved_messages) == 2
    assert saved_messages[0]["role"] == "user"
    assert saved_messages[0]["content"] == "How does it help doctors?"
    assert saved_messages[1]["role"] == "assistant"
    assert (
        saved_messages[1]["content"]
        == "Machine learning helps doctors identify diseases."
    )


def test_chat_rag_failure_does_not_save_messages(monkeypatch):
    saved_messages = []

    async def mock_get_history(session_id):
        return []

    async def mock_answer_question(question, conversation_history=None):
        raise RuntimeError("Gemini service unavailable.")

    async def mock_add_message(session_id, role, content):
        saved_messages.append(content)

    mock_booking_workflow(monkeypatch)

    monkeypatch.setattr(
        "app.api.conversation.get_history",
        mock_get_history,
    )

    monkeypatch.setattr(
        "app.api.conversation.answer_question",
        mock_answer_question,
    )

    monkeypatch.setattr(
        "app.api.conversation.add_message",
        mock_add_message,
    )

    response = client.post(
        "/conversation/chat",
        json={
            "session_id": "test_session_001",
            "message": "What is machine learning?",
        },
    )

    assert response.status_code == 502
    assert response.json()["detail"] == "Gemini service unavailable."
    assert saved_messages == []


def test_chat_rejects_blank_message():
    response = client.post(
        "/conversation/chat",
        json={
            "session_id": "test_session_001",
            "message": "   ",
        },
    )

    assert response.status_code == 422


def test_chat_rejects_blank_session_id():
    response = client.post(
        "/conversation/chat",
        json={
            "session_id": "   ",
            "message": "Hello",
        },
    )

    assert response.status_code == 422

def test_booking_response_skips_rag(monkeypatch):
    saved_messages = []

    async def mock_get_history(session_id):
        return []

    async def mock_booking_workflow(**kwargs):
        assert kwargs["session_id"] == "booking_session_001"
        assert kwargs["message"] == "I want to book an interview."

        return "Your interview booking is ready for confirmation."

    async def mock_answer_question(**kwargs):
        raise AssertionError(
            "RAG should not be called when the booking workflow returns a response."
        )

    async def mock_add_message(session_id, role, content):
        saved_messages.append(
            {
                "role": role,
                "content": content,
            }
        )

    monkeypatch.setattr(
        "app.api.conversation.get_history",
        mock_get_history,
    )

    monkeypatch.setattr(
        "app.api.conversation.process_booking_message",
        mock_booking_workflow,
    )

    monkeypatch.setattr(
        "app.api.conversation.answer_question",
        mock_answer_question,
    )

    monkeypatch.setattr(
        "app.api.conversation.add_message",
        mock_add_message,
    )

    response = client.post(
        "/conversation/chat",
        json={
            "session_id": "booking_session_001",
            "message": "I want to book an interview.",
        },
    )

    assert response.status_code == 200
    assert response.json()["answer"] == (
        "Your interview booking is ready for confirmation."
    )

    assert len(saved_messages) == 2
    assert saved_messages[0]["role"] == "user"
    assert saved_messages[1]["role"] == "assistant"