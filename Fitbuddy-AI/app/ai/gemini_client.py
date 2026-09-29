from functools import lru_cache
import time

from google import genai

from ..config import settings


@lru_cache
def get_gemini_client():
    if not settings.GEMINI_API_KEY:
        raise RuntimeError(
            "GEMINI_API_KEY is missing. "
            "Please add your Gemini API key to the .env file."
        )

    return genai.Client(api_key=settings.GEMINI_API_KEY)


def generate_content(prompt: str) -> str:
    client = get_gemini_client()

    # Primary model + fallback models
    models = [
        settings.GEMINI_MODEL,
        "gemini-3.5-flash",
        "gemini-3.1-flash-lite",
    ]

    # Remove duplicates while keeping the order
    models = list(dict.fromkeys(models))

    last_error = None

    for model in models:
        for attempt in range(3):
            try:
                print(
                    f"Trying Gemini model: {model} "
                    f"(attempt {attempt + 1}/3)"
                )

                response = client.models.generate_content(
                    model=model,
                    contents=prompt,
                )

                text = getattr(response, "text", None)

                if text and text.strip():
                    print(f"Gemini success: {model}")
                    return text.strip()

                raise RuntimeError(
                    f"Gemini returned an empty response from {model}."
                )

            except Exception as error:
                last_error = error
                error_text = str(error)

                print(
                    f"Gemini error from {model}, "
                    f"attempt {attempt + 1}: {error_text}"
                )

                # Retry temporary server/rate-limit errors
                if (
                    "503" in error_text
                    or "UNAVAILABLE" in error_text
                    or "429" in error_text
                    or "RESOURCE_EXHAUSTED" in error_text
                    or "500" in error_text
                    or "INTERNAL" in error_text
                ):
                    wait_time = 2 ** attempt
                    print(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                    continue

                # For non-temporary errors, move to the next model
                break

        print(f"Trying fallback model after failure: {model}")

    raise RuntimeError(
        f"Gemini API error after trying all available models: {last_error}"
    ) from last_error