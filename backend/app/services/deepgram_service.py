from __future__ import annotations

import httpx

from backend.app.core.config import Settings
from backend.app.models.schemas import SpeechToTextResponse


class DeepgramService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    async def transcribe(self, audio_bytes: bytes, content_type: str) -> SpeechToTextResponse:
        if not self.settings.deepgram_api_key:
            raise ValueError("DEEPGRAM_API_KEY is not configured.")

        headers = {
            "Authorization": f"Token {self.settings.deepgram_api_key}",
            "Content-Type": content_type or "audio/wav",
        }
        params = {
            "model": "nova-2",
            "smart_format": "true",
            "detect_language": "true",
            "punctuate": "true",
        }

        async with httpx.AsyncClient(timeout=60.0, trust_env=False) as client:
            response = await client.post(
                "https://api.deepgram.com/v1/listen",
                params=params,
                headers=headers,
                content=audio_bytes,
            )
            response.raise_for_status()
            payload = response.json()

        alternative = (
            payload.get("results", {})
            .get("channels", [{}])[0]
            .get("alternatives", [{}])[0]
        )

        return SpeechToTextResponse(
            transcript=alternative.get("transcript", "").strip(),
            duration_seconds=float(payload.get("metadata", {}).get("duration", 0.0)),
            language=alternative.get("languages", ["unknown"])[0],
        )
