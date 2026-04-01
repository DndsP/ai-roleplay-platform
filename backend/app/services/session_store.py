from __future__ import annotations

import json
from pathlib import Path

from backend.app.models.schemas import (
    SessionContext,
    SessionDataResponse,
    SessionEvaluationResponse,
    SessionInitRequest,
    SessionSegmentRequest,
    SessionTranscriptSegment,
)


class SessionStore:
    def __init__(self, base_dir: str = "session_data") -> None:
        self.base_path = Path(base_dir)
        self.base_path.mkdir(parents=True, exist_ok=True)

    def _safe_room_name(self, room_name: str) -> str:
        cleaned = "".join(ch if ch.isalnum() or ch in {"-", "_"} else "_" for ch in room_name)
        return cleaned or "roleplay-room"

    def _path_for_room(self, room_name: str) -> Path:
        return self.base_path / f"{self._safe_room_name(room_name)}.json"

    def init_session(self, request: SessionInitRequest) -> SessionDataResponse:
        payload = {
            "context": request.model_dump(),
            "transcript_segments": [],
        }
        self._path_for_room(request.room_name).write_text(
            json.dumps(payload, indent=2),
            encoding="utf-8",
        )
        return SessionDataResponse(**payload)

    def append_segment(self, request: SessionSegmentRequest) -> SessionDataResponse:
        session = self.get_session(request.room_name)
        existing_ids = {segment.segment_id for segment in session.transcript_segments}
        if request.segment.segment_id not in existing_ids:
            session.transcript_segments.append(request.segment)
            self._write_session(session)
        return session

    def get_session(self, room_name: str) -> SessionDataResponse:
        path = self._path_for_room(room_name)
        if not path.exists():
            raise ValueError(f"No session found for room '{room_name}'.")
        return SessionDataResponse.model_validate_json(path.read_text(encoding="utf-8"))

    def _write_session(self, session: SessionDataResponse) -> None:
        self._path_for_room(session.context.room_name).write_text(
            session.model_dump_json(indent=2),
            encoding="utf-8",
        )

    def clear_session(self, room_name: str) -> None:
        path = self._path_for_room(room_name)
        if path.exists():
            path.unlink()
