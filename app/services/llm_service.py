
from google import genai

from app.core.config import get_settings


settings = get_settings()

_client: genai.Client | None = None


def _get_client() -> genai.Client:
    """Return a reusable Gemini API client."""

    global _client

    if _client is None:
        if settings.gemini_api_key is None:
            raise RuntimeError("GEMINI_API_KEY is not configured.")

        api_key = settings.gemini_api_key.get_secret_value().strip()

        if not api_key:
            raise RuntimeError("GEMINI_API_KEY is empty.")

        _client = genai.Client(api_key=api_key)

    return _client


async def generate_response(prompt: str) -> str:
    """
    Generate an LLM response using the supplied prompt.
    """

    if not prompt.strip():
        raise ValueError("Prompt cannot be empty.")

    client = _get_client()

    try:
        response = await client.aio.models.generate_content(
            model=settings.llm_model,
            contents=prompt,
        )

    except Exception as exc:
        raise RuntimeError(
            "Failed to generate a response using Gemini."
        ) from exc

    if not response.text:
        raise RuntimeError("Gemini returned an empty response.")

    return response.text.strip()
