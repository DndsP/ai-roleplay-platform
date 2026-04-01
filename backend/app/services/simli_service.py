from __future__ import annotations

import httpx

from backend.app.core.config import Settings
from backend.app.models.schemas import SimliSessionResponse


class SimliService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    @property
    def _headers(self) -> dict[str, str]:
        if not self.settings.simli_api_key:
            raise ValueError("SIMLI_API_KEY is not configured.")
        return {
            "x-simli-api-key": self.settings.simli_api_key,
            "Content-Type": "application/json",
        }

    async def create_session_token(self, face_id: str | None = None) -> SimliSessionResponse:
        selected_face_id = face_id or self.settings.simli_face_id
        if not selected_face_id:
            raise ValueError("SIMLI_FACE_ID is not configured.")

        payload = {
            "faceId": selected_face_id,
            "maxSessionLength": self.settings.simli_max_session_length,
            "maxIdleTime": self.settings.simli_max_idle_time,
            "handleSilence": False,
        }

        async with httpx.AsyncClient(timeout=30.0, trust_env=False) as client:
            response = await client.post(
                f"{self.settings.simli_base_url}/compose/token",
                headers=self._headers,
                json=payload,
            )
            response.raise_for_status()
            data = response.json()

        token = data.get("sessionToken") or data.get("session_token") or data.get("token")
        if not token:
            raise RuntimeError("Simli response did not contain a session token.")

        return SimliSessionResponse(session_token=token, face_id=selected_face_id)
