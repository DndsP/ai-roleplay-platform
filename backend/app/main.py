from __future__ import annotations

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from backend.app.core.config import get_settings
from backend.app.models.schemas import (
    ChatRequest,
    ChatResponse,
    EvaluateRequest,
    EvaluationResponse,
    LiveKitTokenRequest,
    LiveKitTokenResponse,
    SessionDataResponse,
    SessionEvaluationResponse,
    SessionInitRequest,
    SessionSegmentRequest,
    SimliSessionRequest,
    SimliSessionResponse,
    SpeechToTextResponse,
    TTSRequest,
)
from backend.app.services.azure_tts_service import AzureTTSService
from backend.app.services.deepgram_service import DeepgramService
from backend.app.services.livekit_service import LiveKitService
from backend.app.services.openrouter_service import OpenRouterService
from backend.app.services.session_store import SessionStore
from backend.app.services.simli_service import SimliService

settings = get_settings()
app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

deepgram_service = DeepgramService(settings)
openrouter_service = OpenRouterService(settings)
azure_tts_service = AzureTTSService(settings)
simli_service = SimliService(settings)
livekit_service = LiveKitService(settings)
session_store = SessionStore()


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/speech-to-text", response_model=SpeechToTextResponse)
async def speech_to_text(audio: UploadFile = File(...)) -> SpeechToTextResponse:
    try:
        audio_bytes = await audio.read()
        if not audio_bytes:
            raise HTTPException(status_code=400, detail="Uploaded audio file is empty.")
        return await deepgram_service.transcribe(audio_bytes, audio.content_type or "audio/wav")
    except HTTPException:
        raise
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Speech-to-text failed: {exc}") from exc


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    try:
        return await openrouter_service.generate_roleplay_reply(request)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Chat generation failed: {exc}") from exc


@app.post("/evaluate", response_model=EvaluationResponse)
async def evaluate(request: EvaluateRequest) -> EvaluationResponse:
    try:
        return await openrouter_service.evaluate_response(request)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Evaluation failed: {exc}") from exc


@app.post("/tts")
async def tts(request: TTSRequest) -> StreamingResponse:
    try:
        audio_bytes = await azure_tts_service.synthesize(request.text, request.voice)
        return StreamingResponse(
            iter([audio_bytes]),
            media_type="audio/mpeg",
            headers={"Content-Disposition": "inline; filename=roleplay-response.mp3"},
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Text-to-speech failed: {exc}") from exc


@app.post("/simli/session-token", response_model=SimliSessionResponse)
async def simli_session_token(request: SimliSessionRequest) -> SimliSessionResponse:
    try:
        return await simli_service.create_session_token(face_id=request.face_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Simli session creation failed: {exc}") from exc


@app.post("/livekit/token", response_model=LiveKitTokenResponse)
async def livekit_token(request: LiveKitTokenRequest) -> LiveKitTokenResponse:
    try:
        session_context = SessionInitRequest(
            room_name=request.room_name or settings.livekit_default_room,
            participant_name=request.participant_name,
            scenario=request.scenario,
            persona_name=request.persona_name,
            persona_goal=request.persona_goal,
            environment=request.environment,
        )
        return livekit_service.create_token(
            room_name=request.room_name,
            participant_name=request.participant_name,
            session_context=session_context,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"LiveKit token generation failed: {exc}") from exc


@app.post("/session/init", response_model=SessionDataResponse)
async def session_init(request: SessionInitRequest) -> SessionDataResponse:
    try:
        return session_store.init_session(request)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Session init failed: {exc}") from exc


@app.post("/session/segment", response_model=SessionDataResponse)
async def session_segment(request: SessionSegmentRequest) -> SessionDataResponse:
    try:
        return session_store.append_segment(request)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Session update failed: {exc}") from exc


@app.get("/session/{room_name}", response_model=SessionDataResponse)
async def session_data(room_name: str) -> SessionDataResponse:
    try:
        return session_store.get_session(room_name)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Session retrieval failed: {exc}") from exc


@app.post("/session/{room_name}/evaluate", response_model=SessionEvaluationResponse)
async def session_evaluate(room_name: str) -> SessionEvaluationResponse:
    try:
        session = session_store.get_session(room_name)
        return await openrouter_service.evaluate_session(session)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Session evaluation failed: {exc}") from exc


@app.delete("/session/{room_name}")
async def session_delete(room_name: str) -> dict[str, str]:
    try:
        session_store.clear_session(room_name)
        return {"status": "deleted", "room_name": room_name}
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Session deletion failed: {exc}") from exc
