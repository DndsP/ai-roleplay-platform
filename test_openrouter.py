from __future__ import annotations

import os
import sys

import httpx
from dotenv import load_dotenv


def main() -> int:
    load_dotenv()

    api_key = os.getenv("OPENROUTER_API_KEY", "").strip()
    model = os.getenv("OPENROUTER_MODEL", "openai/gpt-4o-mini").strip()

    if not api_key:
        print("OPENROUTER_API_KEY is missing in .env")
        return 1

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:8501",
        "X-Title": "AI Roleplay Trainer Key Test",
    }

    payload = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": "Reply with exactly: OpenRouter key works",
            }
        ],
        "temperature": 0,
    }

    try:
        response = httpx.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=30.0,
            trust_env=False,
        )
        print(f"HTTP {response.status_code}")
        print(response.text)
        response.raise_for_status()
    except httpx.HTTPStatusError as exc:
        print("\nOpenRouter request failed.")
        print(f"Status: {exc.response.status_code}")
        return 1
    except Exception as exc:
        print(f"\nUnexpected error: {exc}")
        return 1

    print("\nOpenRouter key and model look valid.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
