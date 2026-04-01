from __future__ import annotations

import html

import httpx

from backend.app.core.config import Settings


class AzureTTSService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    async def synthesize(self, text: str, voice: str | None = None) -> bytes:
        if not self.settings.azure_speech_key or not self.settings.azure_speech_region:
            raise ValueError("Azure Speech credentials are not configured.")

        selected_voice = voice or self.settings.azure_speech_voice
        endpoint = (
            f"https://{self.settings.azure_speech_region}.tts.speech.microsoft.com/"
            "cognitiveservices/v1"
        )
        ssml = (
            "<speak version='1.0' xml:lang='en-US'>"
            f"<voice name='{html.escape(selected_voice)}'>"
            f"{html.escape(text)}"
            "</voice>"
            "</speak>"
        )
        headers = {
            "Ocp-Apim-Subscription-Key": self.settings.azure_speech_key,
            "Content-Type": "application/ssml+xml",
            "X-Microsoft-OutputFormat": "audio-24khz-96kbitrate-mono-mp3",
            "User-Agent": "ai-roleplay-trainer",
        }

        async with httpx.AsyncClient(timeout=90.0, trust_env=False) as client:
            response = await client.post(endpoint, headers=headers, content=ssml.encode("utf-8"))
            response.raise_for_status()
            return response.content
