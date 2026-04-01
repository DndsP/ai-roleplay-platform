from typing import Literal

from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str


class SpeechToTextResponse(BaseModel):
    transcript: str
    duration_seconds: float = 0.0
    language: str = "unknown"


class ChatRequest(BaseModel):
    transcript: str = Field(..., min_length=1)
    scenario: str = "Customer success escalation"
    persona_name: str = "Jordan"
    persona_goal: str = "Act like the customer or stakeholder in the scenario."
    conversation_history: list[ChatMessage] = Field(default_factory=list)


class ChatResponse(BaseModel):
    response: str
    persona_name: str
    scenario: str


class EvaluationScores(BaseModel):
    clarity: int = Field(..., ge=1, le=10)
    relevance: int = Field(..., ge=1, le=10)
    confidence: int = Field(..., ge=1, le=10)
    overall: int = Field(..., ge=1, le=10)


class EvaluationResponse(BaseModel):
    scores: EvaluationScores
    strengths: list[str]
    improvements: list[str]
    summary: str


class EvaluateRequest(BaseModel):
    transcript: str = Field(..., min_length=1)
    scenario: str = "Customer success escalation"
    coaching_goal: str = "Be clear, empathetic, and solution-oriented."


class TTSRequest(BaseModel):
    text: str = Field(..., min_length=1)
    voice: str | None = None


class SimliSessionRequest(BaseModel):
    face_id: str | None = None


class SimliSessionResponse(BaseModel):
    session_token: str
    face_id: str


class LiveKitTokenRequest(BaseModel):
    room_name: str | None = None
    participant_name: str = "user"
    scenario: str = "Customer success escalation"
    persona_name: str = "Jordan"
    persona_goal: str = "Act like the customer or stakeholder in the scenario."
    environment: str = "Escalation call"


class LiveKitTokenResponse(BaseModel):
    token: str
    room_name: str
    participant_name: str
    livekit_url: str


class SessionContext(BaseModel):
    room_name: str
    participant_name: str = "user"
    scenario: str = "Customer success escalation"
    persona_name: str = "Jordan"
    persona_goal: str = "Act like the customer or stakeholder in the scenario."
    environment: str = "Escalation call"


class SessionTranscriptSegment(BaseModel):
    segment_id: str
    speaker_identity: str
    speaker_label: str
    text: str = Field(..., min_length=1)
    is_final: bool = True
    first_received_time: float = 0.0


class SessionInitRequest(SessionContext):
    pass


class SessionSegmentRequest(BaseModel):
    room_name: str
    segment: SessionTranscriptSegment


class SessionDataResponse(BaseModel):
    context: SessionContext
    transcript_segments: list[SessionTranscriptSegment]


class SessionEvaluationResponse(BaseModel):
    scores: EvaluationScores
    strengths: list[str]
    improvements: list[str]
    summary: str
