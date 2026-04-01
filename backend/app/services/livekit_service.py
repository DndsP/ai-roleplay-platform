from __future__ import annotations

import json

from livekit.api import AccessToken, RoomAgentDispatch, RoomConfiguration, VideoGrants

from backend.app.core.config import Settings
from backend.app.models.schemas import LiveKitTokenResponse, SessionContext


class LiveKitService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def create_token(
        self,
        room_name: str | None,
        participant_name: str,
        session_context: SessionContext,
    ) -> LiveKitTokenResponse:
        if not self.settings.livekit_url:
            raise ValueError("LIVEKIT_URL is not configured.")
        if not self.settings.livekit_api_key or not self.settings.livekit_api_secret:
            raise ValueError("LiveKit API credentials are not configured.")

        selected_room = room_name or self.settings.livekit_default_room
        identity = participant_name.strip().replace(" ", "-") or "user"

        token = (
            AccessToken(self.settings.livekit_api_key, self.settings.livekit_api_secret)
            .with_identity(identity)
            .with_name(participant_name)
            .with_attributes(
                {
                    "scenario": session_context.scenario,
                    "persona_name": session_context.persona_name,
                    "persona_goal": session_context.persona_goal,
                    "environment": session_context.environment,
                }
            )
            .with_metadata(json.dumps(session_context.model_dump()))
            .with_room_config(
                RoomConfiguration(
                    agents=[
                        RoomAgentDispatch(
                            agent_name=self.settings.livekit_agent_name,
                            metadata=json.dumps(session_context.model_dump()),
                        )
                    ]
                )
            )
            .with_grants(
                VideoGrants(
                    room_join=True,
                    room=selected_room,
                    can_publish=True,
                    can_subscribe=True,
                    can_publish_data=True,
                )
            )
            .to_jwt()
        )

        return LiveKitTokenResponse(
            token=token,
            room_name=selected_room,
            participant_name=participant_name,
            livekit_url=self.settings.livekit_url,
        )
