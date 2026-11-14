
import pytest
import fakeredis.aioredis

from app.services import chat_memory_service


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture
async def fake_redis(monkeypatch):
    client = fakeredis.aioredis.FakeRedis(decode_responses=True)

    monkeypatch.setattr(chat_memory_service, "redis_client", client)

    yield client

    await client.aclose()


@pytest.mark.anyio
async def test_get_history_returns_empty_list(fake_redis):
    history = await chat_memory_service.get_history("session_1")

    assert history == []


@pytest.mark.anyio
async def test_add_and_retrieve_messages(fake_redis):
    await chat_memory_service.add_message(
        "session_1", "user", "What is machine learning?"
    )
    await chat_memory_service.add_message(
        "session_1", "assistant", "It is a branch of AI."
    )

    history = await chat_memory_service.get_history("session_1")

    assert len(history) == 2
    assert history[0] == {
        "role": "user",
        "content": "What is machine learning?",
    }
    assert history[1] == {
        "role": "assistant",
        "content": "It is a branch of AI.",
    }


@pytest.mark.anyio
async def test_history_keeps_only_latest_messages(fake_redis, monkeypatch):
    monkeypatch.setattr(
        chat_memory_service, "MAX_HISTORY_MESSAGES", 3
    )

    for number in range(5):
        await chat_memory_service.add_message(
            "session_1", "user", f"Message {number}"
        )

    history = await chat_memory_service.get_history("session_1")

    assert len(history) == 3
    assert [message["content"] for message in history] == [
        "Message 2",
        "Message 3",
        "Message 4",
    ]


@pytest.mark.anyio
async def test_clear_history_deletes_session(fake_redis):
    await chat_memory_service.add_message(
        "session_1", "user", "Hello"
    )

    await chat_memory_service.clear_history("session_1")

    history = await chat_memory_service.get_history("session_1")

    assert history == []


@pytest.mark.anyio
async def test_message_sets_expiration(fake_redis):
    await chat_memory_service.add_message(
        "session_1", "user", "Hello"
    )

    ttl = await fake_redis.ttl("chat:session_1")

    assert 0 < ttl <= chat_memory_service.CHAT_HISTORY_TTL_SECONDS


@pytest.mark.anyio
async def test_empty_message_is_rejected(fake_redis):
    with pytest.raises(ValueError, match="Message content cannot be empty"):
        await chat_memory_service.add_message(
            "session_1", "user", "   "
        )


@pytest.mark.anyio
async def test_empty_session_id_is_rejected(fake_redis):
    with pytest.raises(ValueError, match="Session ID cannot be empty"):
        await chat_memory_service.get_history("   ")
