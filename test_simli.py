from __future__ import annotations

import os
import sys

import httpx
from dotenv import load_dotenv


def main() -> int:
    load_dotenv()

    api_key = os.getenv("SIMLI_API_KEY", "").strip()
    face_id = os.getenv("SIMLI_FACE_ID", "").strip()
    base_url = os.getenv("SIMLI_BASE_URL", "https://api.simli.ai").strip()

    if not api_key:
        print("SIMLI_API_KEY is missing in .env")
        return 1

    if not face_id:
        print("SIMLI_FACE_ID is missing in .env")
        return 1

    headers = {
        "x-simli-api-key": api_key,
        "Content-Type": "application/json",
    }
    payload = {
        "faceId": face_id,
        "maxSessionLength": 1800,
        "maxIdleTime": 30,
        "handleSilence": False,
    }

    try:
        with httpx.Client(timeout=30.0, trust_env=False) as client:
            response = client.post(f"{base_url}/compose/token", headers=headers, json=payload)
            print(f"HTTP {response.status_code}")
            print(response.text)
            response.raise_for_status()
    except httpx.HTTPStatusError as exc:
        print("\nSimli request failed.")
        print(f"Status: {exc.response.status_code}")
        return 1
    except Exception as exc:
        print(f"\nUnexpected error: {exc}")
        return 1

    print("\nSimli API key and face id look valid.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
