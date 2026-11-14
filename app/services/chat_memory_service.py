import json
from typing import Literal

from app.core.redis import redis_client

ChatRole = Literal["user", "assistant"]

MAX_HISTORY_MESSAGES = 20
CHAT_HISTORY_TTL_SECONDS = 86400


def _get_session_key(session_id: str) -> str:
    if not session_id.strip():
        raise ValueError("Session ID cannot be empty.")

    return f"chat:{session_id}"


async def get_history(session_id: str) -> list[dict[str, str]]:
    key = _get_session_key(session_id)

    messages = await redis_client.lrange(key, 0, -1)

    return [json.loads(message) for message in messages]


async def add_message(
    session_id: str,
    role: ChatRole,
    content: str,
) -> None:
    if not content.strip():
        raise ValueError("Message content cannot be empty.")

    key = _get_session_key(session_id)

    message = json.dumps({
        "role": role,
        "content": content,
    })

    async with redis_client.pipeline(transaction=True) as pipeline:
        pipeline.rpush(key, message)
        pipeline.ltrim(key, -MAX_HISTORY_MESSAGES, -1)
        pipeline.expire(key, CHAT_HISTORY_TTL_SECONDS)

        await pipeline.execute()


async def clear_history(session_id: str) -> None:
    key = _get_session_key(session_id)
    await redis_client.delete(key)
